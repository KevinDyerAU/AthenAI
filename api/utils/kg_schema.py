from __future__ import annotations
from typing import Any, Dict, List, Tuple
from .neo4j_client import get_client

# Basic schema catalog for KG governance
NODE_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "Entity": {
        "required": ["id"],
        "optional": ["name", "description", "embedding"],
        "index_suggestions": [
            {"type": "unique", "property": "id"},
        ],
    },
    "Agent": {"required": ["id"], "optional": ["name", "type"]},
    "Task": {"required": ["id"], "optional": ["status", "owner"]},
    "User": {"required": ["id"], "optional": ["email"]},
    "Event": {"required": ["id"], "optional": ["ts", "kind"]},
}

REL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "RELATED": {
        "required": ["type"],
        "optional": ["confidence", "version", "provenance", "lastUpdated", "updatedBy"],
    }
}


def validate_fact(fact: Dict[str, Any]) -> Tuple[bool, str | None]:
    try:
        subj = fact.get("subject") or {}
        obj = fact.get("object") or {}
        pred = fact.get("predicate")
        if not isinstance(subj, dict) or not isinstance(obj, dict) or not pred:
            return False, "Invalid fact shape: missing subject/object/predicate"
        s_id = (subj.get("id") if isinstance(subj.get("id"), str) else subj.get("id", {}).get("id")) or subj.get("id")
        o_id = (obj.get("id") if isinstance(obj.get("id"), str) else obj.get("id", {}).get("id")) or obj.get("id")
        if not s_id or not o_id:
            return False, "subject.id and object.id are required"
        # Optionally enforce known labels (Entity default)
        # Additional type checks can go here
        return True, None
    except Exception as e:
        return False, f"Validation error: {e}"


def validate_facts(facts: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    for i, f in enumerate(facts):
        ok, err = validate_fact(f)
        if not ok:
            errors.append(f"facts[{i}]: {err}")
    return (len(errors) == 0), errors


def monitor_consistency(limit: int = 50) -> Dict[str, Any]:
    """Run lightweight checks: orphan Entities (no rels), contradictory RELATED edges by predicate, dangling properties."""
    client = get_client()
    res: Dict[str, Any] = {}

    # Orphan entities
    orphan = client.run_query(
        "MATCH (e:Entity) WHERE NOT (e)--() RETURN e.id AS id LIMIT $limit", {"limit": limit}
    )
    res["orphans"] = [r["id"] for r in orphan]

    # Contradictory relations: same subject+predicate => multiple objects
    contra = client.run_query(
        "MATCH (s:Entity)-[r:RELATED]->(o:Entity) "
        "WITH s.id AS sid, r.type AS pred, collect(distinct o.id) AS objs "
        "WHERE size(objs) > 1 RETURN sid, pred, objs LIMIT $limit",
        {"limit": limit},
    )
    res["contradictions"] = [r.data() for r in contra]

    # Missing required properties per schema (sampled)
    missing: List[Dict[str, Any]] = []
    for label, spec in NODE_SCHEMAS.items():
        for prop in spec.get("required", []):
            rows = client.run_query(
                f"MATCH (n:{label}) WHERE n.{prop} IS NULL RETURN n LIMIT $limit",
                {"limit": limit},
            )
            if rows:
                missing.append({"label": label, "property": prop, "count": len(rows)})
    res["missing_props"] = missing

    return res


def apply_constraints_and_indexes() -> Dict[str, Any]:
    """Advise to run scripts/neo4j/constraints.cypher and create_indexes.cypher.
    For convenience, we attempt existence checks for critical constraints.
    """
    # Minimal no-op here; docs steer to scripts. Extendable to auto-apply via procedure calls.
    return {
        "message": "Apply constraints via scripts/neo4j/constraints.cypher and indexes via scripts/neo4j/create_indexes.cypher",
        "critical": [
            "Entity.id UNIQUE",
            "Fulltext entityIndex",
            "Vector entityEmbedding (if vector search enabled)",
        ],
    }


def validate_schema() -> Dict[str, Any]:
    """Check existence of critical constraints and indexes."""
    client = get_client()
    constraints = client.run_query("SHOW CONSTRAINTS")
    cons = [r.data() for r in constraints]
    indexes = client.run_query("CALL db.indexes()")
    idxs = [r.data() for r in indexes]

    def has_entity_id_unique() -> bool:
        for c in cons:
            # Neo4j 5: name, type, entityType, labelsOrTypes, properties
            if (
                c.get("type") in ("UNIQUENESS", "NODE_KEY")
                and "Entity" in (c.get("labelsOrTypes") or [])
                and (c.get("properties") or []) == ["id"]
            ):
                return True
        return False

    def has_fulltext_entity_index() -> bool:
        for i in idxs:
            # fulltext indexes appear with type 'FULLTEXT'
            if i.get("type") == "FULLTEXT" and i.get("name") == "entityIndex":
                return True
        return False

    def has_vector_entity_embedding() -> bool:
        for i in idxs:
            # Vector indexes show as type 'VECTOR'
            if i.get("type") == "VECTOR" and i.get("name") == "entityEmbedding":
                return True
        return False

    return {
        "entity_id_unique": has_entity_id_unique(),
        "fulltext_entityIndex": has_fulltext_entity_index(),
        "vector_entityEmbedding": has_vector_entity_embedding(),
        "constraints": cons,
        "indexes": idxs,
    }
