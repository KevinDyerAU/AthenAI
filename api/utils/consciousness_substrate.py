from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase, Driver, Transaction


@dataclass
class ConflictRecord:
    field: str
    conflicting_agent: str
    timestamp: str
    our_value: Any
    their_value: Any


class ConflictError(Exception):
    """Exception raised when knowledge conflicts cannot be resolved"""


class EnhancedConsciousnessSubstrate:
    """
    High-level utility for advanced knowledge operations on the Neo4j consciousness substrate.
    Requires Neo4j 5.x (vector index optional but recommended).
    """

    def __init__(self, uri: str, user: str, password: str) -> None:
        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        if self.driver:
            self.driver.close()

    # -----------------------------
    # Knowledge CRUD with provenance
    # -----------------------------
    def create_knowledge_entity(
        self,
        content: str,
        entity_type: str,
        created_by: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create new knowledge entity with provenance tracking."""
        entity_id = str(uuid.uuid4())
        prov_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        def _tx(tx: Transaction) -> str:
            result = tx.run(
                """
                MERGE (k:KnowledgeEntity { id: $id })
                ON CREATE SET k.content = $content,
                              k.entity_type = $entity_type,
                              k.created_at = datetime($timestamp),
                              k.updated_at = datetime($timestamp),
                              k.version = 1,
                              k.embedding = $embedding,
                              k.metadata = $metadata
                WITH k
                MERGE (p:Provenance { id: $prov_id })
                ON CREATE SET p.source = 'api',
                              p.evidence = 'create',
                              p.actor_id = $created_by,
                              p.created_at = datetime($timestamp),
                              p.metadata = $prov_details
                MERGE (k)-[:HAS_PROVENANCE]->(p)
                RETURN k.id AS entity_id
                """,
                {
                    "id": entity_id,
                    "content": content,
                    "entity_type": entity_type,
                    "timestamp": now_iso,
                    "embedding": embedding,
                    "metadata": metadata or {},
                    "prov_id": prov_id,
                    "created_by": str(created_by),
                    "prov_details": {
                        "action": "create",
                        "content_length": len(content or ""),
                        "entity_type": entity_type,
                    },
                },
            )
            rec = result.single()
            return rec["entity_id"] if rec else entity_id

        with self.driver.session() as session:
            return session.execute_write(_tx)

    def update_knowledge_entity(
        self,
        entity_id: str,
        updates: Dict[str, Any],
        updated_by: str,
        conflict_resolution: str = "merge",
    ) -> int:
        """Update knowledge entity with conflict detection and resolution. Returns new version."""
        now_iso = datetime.now(timezone.utc).isoformat()

        def _read_version(tx: Transaction):
            rec = tx.run(
                """
                MATCH (k:KnowledgeEntity {id: $id})
                RETURN k.version AS version, k.updated_at AS last_update
                """,
                {"id": entity_id},
            ).single()
            return rec

        def _detect_conflicts(tx: Transaction) -> List[ConflictRecord]:
            recent = tx.run(
                """
                MATCH (k:KnowledgeEntity {id: $id})-[:HAS_PROVENANCE]->(p:Provenance)
                WHERE p.created_at > datetime() - duration('PT5M') AND coalesce(p.metadata.action,'') = 'update'
                RETURN p.actor_id AS agent, p.metadata AS details, p.created_at AS ts
                ORDER BY p.created_at DESC
                LIMIT 20
                """,
                {"id": entity_id},
            ).data()
            conflicts: List[ConflictRecord] = []
            for upd in recent:
                details = upd.get("details") or {}
                orig = details.get("original_updates", {})
                for field in updates.keys():
                    if field in orig:
                        conflicts.append(
                            ConflictRecord(
                                field=field,
                                conflicting_agent=str(upd.get("agent")),
                                timestamp=str(upd.get("ts")),
                                our_value=updates[field],
                                their_value=orig[field],
                            )
                        )
            return conflicts

        def _resolve_conflicts(conflicts: List[ConflictRecord]) -> Dict[str, Any]:
            resolved = dict(updates)
            if conflict_resolution == "merge":
                for c in conflicts:
                    if c.field == "content":
                        resolved[c.field] = self.merge_content(str(c.our_value), str(c.their_value))
            elif conflict_resolution == "latest_wins":
                # keep our updates
                pass
            elif conflict_resolution == "first_wins":
                for c in conflicts:
                    if c.field in resolved:
                        del resolved[c.field]
            else:
                # default: latest_wins
                pass
            return resolved

        def _write_update(tx: Transaction, new_updates: Dict[str, Any], conflicts_list: List[ConflictRecord]) -> int:
            # bump version atomically and write provenance + optional snapshot
            conflicts_payload = [c.__dict__ for c in conflicts_list]
            prov_id = str(uuid.uuid4())
            snap_id = str(uuid.uuid4())
            result = tx.run(
                """
                MATCH (k:KnowledgeEntity {id: $id})
                WITH k
                SET k += $updates,
                    k.updated_at = datetime($timestamp),
                    k.version = coalesce(k.version, 0) + 1
                WITH k
                MERGE (p:Provenance { id: $prov_id })
                ON CREATE SET p.source = 'api',
                              p.evidence = 'update',
                              p.actor_id = $updated_by,
                              p.created_at = datetime($timestamp),
                              p.metadata = $prov_details
                MERGE (k)-[:HAS_PROVENANCE]->(p)
                WITH k
                MERGE (s:KnowledgeSnapshot { id: $snap_id })
                ON CREATE SET s.entity_id = k.id,
                              s.version = k.version,
                              s.content = k.content,
                              s.created_at = datetime($timestamp),
                              s.metadata = k.metadata
                MERGE (k)-[:HAS_SNAPSHOT]->(s)
                RETURN k.version AS version
                """,
                {
                    "id": entity_id,
                    "updates": new_updates,
                    "timestamp": now_iso,
                    "prov_id": prov_id,
                    "updated_by": str(updated_by),
                    "prov_details": {
                        "action": "update",
                        "original_updates": updates,
                        "resolved_updates": new_updates,
                        "conflicts": conflicts_payload,
                        "resolution_strategy": conflict_resolution,
                    },
                    "snap_id": snap_id,
                },
            ).single()
            return int(result["version"]) if result else 0

        with self.driver.session() as session:
            # check entity exists and get version
            cur = session.execute_read(_read_version)
            if not cur:
                raise ValueError(f"Knowledge entity {entity_id} not found")

            conflicts = session.execute_read(_detect_conflicts)
            if conflicts and conflict_resolution == "strict":
                raise ConflictError(f"Conflicts detected: {[c.__dict__ for c in conflicts]}")

            resolved_updates = _resolve_conflicts(conflicts)
            return session.execute_write(_write_update, resolved_updates, conflicts)

    # -----------------------------
    # Vector semantic search
    # -----------------------------
    def semantic_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        with self.driver.session() as session:
            result = session.run(
                """
                CALL db.index.vector.queryNodes('knowledge_embeddings', $limit, $query_embedding)
                YIELD node, score
                WHERE score > $threshold
                RETURN node.id AS id, node.content AS content, node.entity_type AS entity_type, score
                ORDER BY score DESC
                """,
                {
                    "query_embedding": query_embedding,
                    "limit": limit,
                    "threshold": threshold,
                },
            )
            return [
                {
                    "id": r["id"],
                    "content": r["content"],
                    "entity_type": r["entity_type"],
                    "similarity": r["score"],
                }
                for r in result
            ]

    # -----------------------------
    # Provenance
    # -----------------------------
    def get_knowledge_provenance(self, entity_id: str) -> List[Dict[str, Any]]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (k:KnowledgeEntity {id: $id})-[:HAS_PROVENANCE]->(p:Provenance)
                RETURN p
                ORDER BY p.created_at ASC
                """,
                {"id": entity_id},
            )
            out: List[Dict[str, Any]] = []
            for rec in result:
                p = rec["p"]
                out.append(
                    {
                        "action": (p.get("metadata", {}) or {}).get("action"),
                        "timestamp": p.get("created_at"),
                        "agent": p.get("actor_id"),
                        "details": p.get("metadata", {}),
                    }
                )
            return out

    # -----------------------------
    # Merge helpers (placeholder for AI-assisted merge)
    # -----------------------------
    def merge_content(self, ours: str, theirs: str) -> str:
        """
        Simple merge heuristic. Replace with AI-assisted merge if available.
        Currently concatenates with separators if texts differ.
        """
        if not ours:
            return theirs
        if not theirs:
            return ours
        if ours.strip() == theirs.strip():
            return ours
        return f"<<ours>>\n{ours}\n\n<<theirs>>\n{theirs}"

    # -----------------------------
    # Advanced graph-based reasoning
    # -----------------------------
    def traverse_related(
        self,
        start_id: str,
        max_depth: int = 2,
        rel_types: Optional[List[str]] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Breadth traversal from an entity with optional relationship filter."""
        rel = "|".join(rel_types) if rel_types else "SIMILAR_TO|HAS_PROVENANCE|HAS_CONFLICT|HAS_SNAPSHOT"
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH path = (k:KnowledgeEntity {{id: $id}})-[:{rel}*1..{max_depth}]-(n)
                WITH nodes(path) AS ns, relationships(path) AS rs
                UNWIND ns AS node
                WITH DISTINCT node LIMIT $limit
                RETURN node.id AS id, labels(node) AS labels, node AS props
                """,
                {"id": start_id, "limit": limit},
            )
            return [
                {"id": r["id"], "labels": r["labels"], "props": dict(r["props"]) }
                for r in result
            ]

    def community_detection_louvain(
        self,
        sample: int = 1000,
        write_property: str = "communityId",
    ) -> Dict[str, Any]:
        """Run Louvain via GDS if available. Returns summary. Does not fail hard if GDS absent."""
        with self.driver.session() as session:
            # Try anonymous graph creation
            try:
                gname = f"kg_tmp_{uuid.uuid4().hex[:8]}"
                session.run(
                    """
                    CALL gds.graph.project($gname, 'KnowledgeEntity', {
                      SIMILAR_TO: {orientation: 'UNDIRECTED'}
                    })
                    """,
                    {"gname": gname},
                ).consume()
                res = session.run(
                    """
                    CALL gds.louvain.write($gname, {writeProperty: $prop, sampleRate: 1.0})
                    YIELD communityCount, nodePropertiesWritten
                    RETURN communityCount AS communities, nodePropertiesWritten AS written
                    """,
                    {"gname": gname, "prop": write_property},
                ).single()
                # drop
                session.run("CALL gds.graph.drop($gname)", {"gname": gname}).consume()
                return {"communities": res["communities"], "written": res["written"]} if res else {"communities": 0, "written": 0}
            except Exception:
                # Fallback no-op
                return {"communities": 0, "written": 0, "note": "GDS not available"}

    def centrality_pagerank(
        self,
        top_n: int = 20,
        relationship: str = "SIMILAR_TO",
    ) -> List[Dict[str, Any]]:
        """Compute approximate PageRank centrality over KnowledgeEntity graph using GDS or Cypher fallback."""
        with self.driver.session() as session:
            try:
                gname = f"kg_pr_{uuid.uuid4().hex[:8]}"
                session.run(
                    "CALL gds.graph.project($gname, 'KnowledgeEntity', $rel)",
                    {"gname": gname, "rel": {relationship: {"orientation": "UNDIRECTED"}}},
                ).consume()
                res = session.run(
                    """
                    CALL gds.pageRank.stream($gname)
                    YIELD nodeId, score
                    RETURN gds.util.asNode(nodeId).id AS id, score
                    ORDER BY score DESC LIMIT $top
                    """,
                    {"gname": gname, "top": top_n},
                )
                out = [{"id": r["id"], "score": r["score"]} for r in res]
                session.run("CALL gds.graph.drop($gname)", {"gname": gname}).consume()
                return out
            except Exception:
                # fallback: degree centrality
                res = session.run(
                    f"""
                    MATCH (k:KnowledgeEntity)-[:{relationship}]-(n)
                    RETURN k.id AS id, count(n) AS degree
                    ORDER BY degree DESC LIMIT $top
                    """,
                    {"top": top_n},
                )
                return [{"id": r["id"], "score": float(r["degree"]) } for r in res]

    def temporal_evolution(
        self,
        entity_id: str,
        since_iso: Optional[str] = None,
        until_iso: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return temporal snapshots and provenance events for an entity between bounds."""
        with self.driver.session() as session:
            params = {"id": entity_id}
            where = []
            if since_iso:
                params["since"] = since_iso
                where.append("p.created_at >= datetime($since)")
            if until_iso:
                params["until"] = until_iso
                where.append("p.created_at <= datetime($until)")
            where_clause = ("WHERE " + " AND ".join(where)) if where else ""

            prov = session.run(
                f"""
                MATCH (k:KnowledgeEntity {{id: $id}})-[:HAS_PROVENANCE]->(p:Provenance)
                {where}
                RETURN p ORDER BY p.created_at ASC
                """.replace("{where}", where_clause),
                params,
            )
            prov_out = []
            for rec in prov:
                p = rec["p"]
                prov_out.append(
                    {
                        "timestamp": p.get("created_at"),
                        "actor": p.get("actor_id"),
                        "metadata": p.get("metadata", {}),
                    }
                )

            snaps = session.run(
                """
                MATCH (k:KnowledgeEntity {id: $id})-[:HAS_SNAPSHOT]->(s:KnowledgeSnapshot)
                RETURN s ORDER BY s.created_at ASC
                """,
                {"id": entity_id},
            )
            snaps_out = []
            for rec in snaps:
                s = rec["s"]
                snaps_out.append(
                    {
                        "version": s.get("version"),
                        "timestamp": s.get("created_at"),
                        "content": s.get("content"),
                        "metadata": s.get("metadata", {}),
                    }
                )

            return [
                {"type": "provenance", "events": prov_out},
                {"type": "snapshots", "events": snaps_out},
            ]
