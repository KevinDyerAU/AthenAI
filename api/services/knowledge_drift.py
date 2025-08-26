from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import time

from ..utils.neo4j_client import get_client
from ..utils.embeddings import get_query_embedding, vector_search_enabled
from ..utils.kg_schema import monitor_consistency


@dataclass
class DriftSignal:
    kind: str
    severity: str
    details: Dict[str, Any]


def _now_ms() -> int:
    return int(time.time() * 1000)


def recent_entity_texts(limit: int = 200) -> List[Tuple[str, str]]:
    """Return list of (id, text) for recently updated entities."""
    client = get_client()
    rows = client.run_query(
        """
        MATCH (e:Entity)
        WITH e, coalesce(e.updatedAt, e.lastUpdated, 0) AS ts
        RETURN e.id AS id, coalesce(e.name, e.description, e.id) AS text
        ORDER BY ts DESC LIMIT $limit
        """,
        {"limit": limit},
    )
    return [(r["id"], r["text"]) for r in rows if (r.get("text") or "").strip()]


def detect_semantic_drift(sample_limit: int = 100, similarity_threshold: float = 0.80) -> List[DriftSignal]:
    """Detect potential semantic drift by comparing stored embeddings vs fresh embeddings.
    If vector search is disabled or embeddings unavailable, returns empty list.
    """
    signals: List[DriftSignal] = []
    if not vector_search_enabled():
        return signals

    client = get_client()
    # Pull entities that have an existing embedding
    rows = client.run_query(
        """
        MATCH (e:Entity)
        WHERE e.embedding IS NOT NULL
        WITH e, coalesce(e.updatedAt, e.lastUpdated, 0) AS ts
        RETURN e.id AS id, e.embedding AS emb, coalesce(e.name, e.description, e.id) AS text
        ORDER BY ts DESC LIMIT $limit
        """,
        {"limit": sample_limit},
    )
    for r in rows:
        try:
            eid = r["id"]
            stored = r["emb"]
            text = r.get("text") or eid
            fresh = get_query_embedding(text)
            # cosine similarity
            dot = sum((a * b) for a, b in zip(stored, fresh))
            na = sum((a * a) for a in stored) ** 0.5
            nb = sum((b * b) for b in fresh) ** 0.5
            sim = dot / (na * nb + 1e-9)
            if sim < similarity_threshold:
                signals.append(
                    DriftSignal(
                        kind="embedding_shift",
                        severity="medium" if sim > 0.6 else "high",
                        details={"entity_id": eid, "similarity": sim, "threshold": similarity_threshold},
                    )
                )
        except Exception:
            # Skip entities with malformed embeddings
            continue
    return signals


def detect_conflicts(limit: int = 200) -> List[DriftSignal]:
    """Use `monitor_consistency()` contradictions as conflict signals."""
    cons = monitor_consistency(limit=limit)
    signals: List[DriftSignal] = []
    for c in cons.get("contradictions", []) or []:
        objs = c.get("objs", [])
        sev = "medium" if len(objs) == 2 else "high"
        signals.append(
            DriftSignal(kind="contradiction", severity=sev, details=c)
        )
    return signals


def assess_quality(limit: int = 500) -> Dict[str, Any]:
    """Compute simple quality metrics and a composite score [0..1]."""
    client = get_client()
    # Totals
    ent_total = client.run_query("MATCH (e:Entity) RETURN count(e) AS c")[0]["c"]
    rel_total = client.run_query("MATCH ()-[r:RELATED]->() RETURN count(r) AS c")[0]["c"]

    # Orphans, contradictions, missing props
    cons = monitor_consistency(limit=limit)
    orphan_count = len(cons.get("orphans", []))
    contradictions = cons.get("contradictions", []) or []
    missing_props = cons.get("missing_props", []) or []

    # Average confidence and freshness
    avg_conf_rows = client.run_query("MATCH ()-[r:RELATED]->() RETURN avg(coalesce(r.confidence,0.0)) AS avgc")
    avg_conf = float(avg_conf_rows[0]["avgc"] or 0.0)
    # Last update recency (ms)
    last_upd_rows = client.run_query("MATCH ()-[r:RELATED]->() RETURN max(coalesce(r.lastUpdated,0)) AS mx")
    last_upd = int(last_upd_rows[0]["mx"] or 0)
    age_ms = max(0, _now_ms() - last_upd)

    # Composite score: start from 1.0, subtract normalized penalties
    score = 1.0
    if ent_total:
        score -= min(0.3, 0.3 * (orphan_count / max(1, ent_total)))
    if rel_total:
        score -= min(0.4, 0.4 * (len(contradictions) / max(1, rel_total / 10)))
    score -= min(0.2, 0.2 * (1.0 - min(1.0, avg_conf)))
    # Freshness penalty: if older than 24h, degrade up to 0.1
    day_ms = 24 * 3600 * 1000
    if age_ms > day_ms:
        score -= min(0.1, 0.1 * (age_ms / (7 * day_ms)))

    return {
        "entities": ent_total,
        "relations": rel_total,
        "orphans": orphan_count,
        "contradictions": contradictions,
        "missing_props": missing_props,
        "avg_confidence": round(avg_conf, 4),
        "last_update_ms": last_upd,
        "age_ms": age_ms,
        "quality_score": round(max(0.0, min(1.0, score)), 4),
    }


def _score_options(subject_id: str, predicate: str, strategy: str) -> List[Tuple[str, float]]:
    client = get_client()
    if strategy == "confidence":
        rows = client.run_query(
            """
            MATCH (s:Entity {id: $sid})-[r:RELATED {type: $pred}]->(o:Entity)
            RETURN o.id AS oid, coalesce(r.confidence, 0.0) AS score
            """,
            {"sid": subject_id, "pred": predicate},
        )
    else:
        rows = client.run_query(
            """
            MATCH (s:Entity {id: $sid})-[r:RELATED {type: $pred}]->(o:Entity)
            RETURN o.id AS oid, coalesce(r.lastUpdated,0) AS score
            """,
            {"sid": subject_id, "pred": predicate},
        )
    return [(r["oid"], float(r["score"])) for r in rows]


def remediate_conflict(
    subject_id: str,
    predicate: str,
    strategy: str = "confidence",
    dry_run: bool = False,
    escalate: bool = False,
    user_id: str | None = None,
) -> Dict[str, Any]:
    """Remediate contradiction by selecting a winner.
    - dry_run: return plan only
    - escalate: create a ResolutionRequest node and do not modify relations
    - provenance: append to r.provenance and set r.updatedBy
    """
    opts = _score_options(subject_id, predicate, strategy)
    if not opts:
        return {"updated": 0, "reason": "no_options", "plan": None}
    opts.sort(key=lambda x: x[1], reverse=True)
    winner = opts[0][0]
    plan = {
        "subject_id": subject_id,
        "predicate": predicate,
        "winner": winner,
        "losers": [oid for oid, _ in opts if oid != winner],
        "strategy": strategy,
        "count": len(opts),
    }
    if dry_run:
        return {"updated": 0, "plan": plan, "dry_run": True}

    client = get_client()
    now = _now_ms()
    if escalate:
        # Record a resolution request and return without changing edges
        client.run_query(
            """
            MERGE (rr:ResolutionRequest {sid: $sid, pred: $pred})
            SET rr.at = $now, rr.strategy = $strategy, rr.options = $options, rr.requestedBy = $userId
            """,
            {
                "sid": subject_id,
                "pred": predicate,
                "now": now,
                "strategy": strategy,
                "options": [dict(oid=oid, score=score) for oid, score in opts],
                "userId": str(user_id) if user_id is not None else None,
            },
        )
        return {"updated": 0, "plan": plan, "escalated": True}

    # Apply winner and set provenance/updatedBy
    client.run_query(
        """
        MATCH (s:Entity {id: $sid})-[r:RELATED {type: $pred}]->(o:Entity)
        WITH r, o, $winner AS winner, $now AS now, $userId AS uid
        SET r.state = CASE WHEN o.id = winner THEN 'active' ELSE 'rejected' END,
            r.lastUpdated = now, r.version = coalesce(r.version,0)+1,
            r.updatedBy = uid,
            r.provenance = coalesce(r.provenance, []) + [{by: uid, at: now, action: 'remediate', strategy: $strategy}]
        """,
        {
            "sid": subject_id,
            "pred": predicate,
            "winner": winner,
            "now": now,
            "userId": str(user_id) if user_id is not None else None,
            "strategy": strategy,
        },
    )
    return {"updated": len(opts), "winner": winner, "plan": plan}


# ------------- Batch curation utilities -------------

def find_dedup_candidates(limit: int = 100) -> List[Dict[str, Any]]:
    """Return groups of entities with same normalized name as dedup candidates."""
    client = get_client()
    rows = client.run_query(
        """
        MATCH (e:Entity)
        WITH toLower(coalesce(e.name, '')) AS norm, collect(e.id) AS ids
        WHERE norm <> '' AND size(ids) > 1
        RETURN norm AS key, ids LIMIT $limit
        """,
        {"limit": limit},
    )
    return [dict(key=r["key"], ids=r["ids"]) for r in rows]


def merge_entities(target_id: str, duplicate_ids: List[str], dry_run: bool = True, user_id: str | None = None) -> Dict[str, Any]:
    """Merge duplicates into target by rewiring relationships and marking duplicates as merged.
    When dry_run, return a plan only.
    """
    plan = {
        "target": target_id,
        "duplicates": duplicate_ids,
        "actions": [
            "Rewire incoming and outgoing RELATED edges from duplicates to target",
            "Mark duplicates with mergedInto",
        ],
    }
    if dry_run:
        return {"merged": 0, "plan": plan, "dry_run": True}
    client = get_client()
    now = _now_ms()
    uid = str(user_id) if user_id is not None else None
    # Rewire OUTGOING
    client.run_query(
        """
        UNWIND $dups AS dup
        MATCH (d:Entity {id: dup})-[r:RELATED]->(o:Entity)
        WITH r, o
        MATCH (t:Entity {id: $target})
        MERGE (t)-[nr:RELATED {type: r.type}]->(o)
        SET nr += properties(r)
        SET nr.version = coalesce(nr.version,0)+1,
            nr.lastUpdated = $now,
            nr.updatedBy = $uid,
            nr.provenance = coalesce(nr.provenance, []) + [{by: $uid, at: $now, action: 'merge_rewire_out'}]
        DELETE r
        """,
        {"dups": duplicate_ids, "target": target_id, "now": now, "uid": uid},
    )
    # Rewire INCOMING
    client.run_query(
        """
        UNWIND $dups AS dup
        MATCH (s:Entity)-[r:RELATED]->(d:Entity {id: dup})
        WITH r, s
        MATCH (t:Entity {id: $target})
        MERGE (s)-[nr:RELATED {type: r.type}]->(t)
        SET nr += properties(r)
        SET nr.version = coalesce(nr.version,0)+1,
            nr.lastUpdated = $now,
            nr.updatedBy = $uid,
            nr.provenance = coalesce(nr.provenance, []) + [{by: $uid, at: $now, action: 'merge_rewire_in'}]
        DELETE r
        """,
        {"dups": duplicate_ids, "target": target_id, "now": now, "uid": uid},
    )
    # Mark duplicates
    client.run_query(
        """
        UNWIND $dups AS dup
        MATCH (d:Entity {id: dup})
        SET d.mergedInto = $target,
            d.mergedAt = $now,
            d.mergedBy = $uid
        """,
        {"dups": duplicate_ids, "target": target_id, "now": now, "uid": uid},
    )
    return {"merged": len(duplicate_ids), "plan": plan}


def record_quality_snapshot(metrics: Dict[str, Any], user_id: str | None = None) -> None:
    """Persist a QualitySnapshot node for trend analysis."""
    client = get_client()
    client.run_query(
        """
        CREATE (q:QualitySnapshot {
            at: timestamp(),
            entities: $entities,
            relations: $relations,
            orphans: $orphans,
            contradictions: size($contradictions),
            avg_confidence: $avg_confidence,
            quality_score: $quality_score,
            recordedBy: $userId
        })
        """,
        {
            "entities": metrics.get("entities"),
            "relations": metrics.get("relations"),
            "orphans": metrics.get("orphans"),
            "contradictions": metrics.get("contradictions", []),
            "avg_confidence": metrics.get("avg_confidence"),
            "quality_score": metrics.get("quality_score"),
            "userId": str(user_id) if user_id is not None else None,
        },
    )


def get_quality_trend(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent quality snapshots."""
    client = get_client()
    rows = client.run_query(
        "MATCH (q:QualitySnapshot) RETURN q ORDER BY q.at DESC LIMIT $limit",
        {"limit": limit},
    )
    return [r[0] for r in rows]


def enrich_embeddings(limit: int = 200) -> Dict[str, Any]:
    """Compute embeddings for entities missing them (no-op if embeddings disabled)."""
    if not vector_search_enabled():
        return {"updated": 0, "reason": "embeddings_disabled"}
    client = get_client()
    rows = client.run_query(
        """
        MATCH (e:Entity) WHERE e.embedding IS NULL
        WITH e, coalesce(e.name, e.description, e.id) AS text
        WHERE text IS NOT NULL AND text <> ''
        RETURN e.id AS id, text LIMIT $limit
        """,
        {"limit": limit},
    )
    updated = 0
    for r in rows:
        try:
            emb = get_query_embedding(r["text"])
            client.run_query(
                """
                MATCH (e:Entity {id: $id})
                SET e.embedding = $emb, e.updatedAt = timestamp()
                """,
                {"id": r["id"], "emb": emb},
            )
            updated += 1
        except Exception:
            continue
    return {"updated": updated}
