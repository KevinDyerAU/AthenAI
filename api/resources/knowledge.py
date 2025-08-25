from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.neo4j_client import get_client
from ..utils.audit import audit_event
from ..utils.embeddings import get_query_embedding, vector_search_enabled
from ..utils.kg_schema import validate_facts

ns = Namespace("knowledge", description="Knowledge graph access via Neo4j with context preservation")

query_model = ns.model("KnowledgeQuery", {
    "cypher": fields.String(required=True, description="Read-only Cypher query"),
    "params": fields.Raw(description="Query parameters"),
})

insert_model = ns.model("KnowledgeInsert", {
    "facts": fields.List(fields.Raw, required=True, description="List of fact objects to MERGE"),
    "conflict_policy": fields.String(description="Policy: prefer_latest|prefer_high_confidence", default="prefer_latest"),
})

search_model = ns.model("KnowledgeSearch", {
    "query": fields.String(required=True),
    "limit": fields.Integer(default=10)
})

relation_key_model = ns.model("RelationKey", {
    "subject_id": fields.String(required=True, description="Subject entity id"),
    "predicate": fields.String(required=True, description="Relation type/predicate"),
    "object_id": fields.String(required=True, description="Object entity id"),
})

relation_update_model = ns.inherit("RelationUpdate", relation_key_model, {
    "attributes": fields.Raw(required=True, description="Properties to set on relation"),
    "source": fields.String(description="Provenance source", default="api"),
})

relation_delete_model = ns.inherit("RelationDelete", relation_key_model, {
    "reason": fields.String(description="Reason for deactivation"),
    "source": fields.String(description="Provenance source", default="api"),
})


@ns.route("/query")
class KnowledgeQuery(Resource):
    @jwt_required()
    @ns.expect(query_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        cypher = payload.get("cypher", "").strip()
        params = payload.get("params") or {}
        # Basic guardrail: allow only read operations
        lowered = cypher.lower()
        if any(x in lowered for x in [" create ", " merge ", " delete ", " set ", " remove ", " load csv", " apoc."]):
            ns.abort(400, "Only read-only Cypher is allowed in /knowledge/query")
        user = get_jwt_identity()
        params["_user_id"] = user["id"] if isinstance(user, dict) else user
        client = get_client()
        try:
            records = client.run_query(cypher, params)
            rows = [r.data() for r in records]
            audit_event("knowledge.query", {"rows": len(rows)}, user)
            return {"results": rows, "count": len(rows)}
        except Exception as e:
            audit_event("knowledge.query.error", {"error": str(e)}, user)
            ns.abort(400, f"Query failed: {e}")


@ns.route("/insert")
class KnowledgeInsert(Resource):
    @jwt_required()
    @ns.expect(insert_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        facts = payload.get("facts", [])
        policy = payload.get("conflict_policy", "prefer_latest")
        if not isinstance(facts, list) or not facts:
            ns.abort(400, "facts must be a non-empty list")
        # Schema validation before any write
        ok, errors = validate_facts(facts)
        if not ok:
            audit_event("knowledge.insert.validation_failed", {"errors": errors[:10]}, None)
            ns.abort(400, {"message": "Schema validation failed", "errors": errors})
        # Optional: enrich entities with embeddings for vector search
        if vector_search_enabled():
            for f in facts:
                subj = f.get("subject", {})
                obj = f.get("object", {})
                for node in (subj, obj):
                    if not isinstance(node, dict):
                        continue
                    props = node.get("props") or {}
                    # Build text from props or fallback to id
                    text = props.get("name") or props.get("description") or node.get("id")
                    if text and isinstance(text, str):
                        try:
                            props["embedding"] = get_query_embedding(text)
                            node["props"] = props
                        except Exception as _:
                            # Do not block insert on embedding failure
                            pass
        user = get_jwt_identity()
        user_id = user["id"] if isinstance(user, dict) else user
        # Conflict resolution & provenance tracking
        # - maintain r.version (monotonic)
        # - update r.confidence depending on policy
        # - append provenance record {by, at, source}
        cypher = (
            "UNWIND $facts AS f "
            "MERGE (s:Entity {id: f.subject.id}) SET s += coalesce(f.subject.props, {}) "
            "MERGE (o:Entity {id: f.object.id}) SET o += coalesce(f.object.props, {}) "
            "MERGE (s)-[r:RELATED {type: f.predicate}]->(o) "
            "WITH r, f, $userId AS userId, $policy AS policy, timestamp() AS now "
            "SET r.state = coalesce(r.state, 'active'), r.lastUpdated = now, r.updatedBy = userId, r.version = coalesce(r.version, 0) + 1 "
            "WITH r, f, userId, policy, now "
            "SET r.provenance = coalesce(r.provenance, []) + [{by: userId, at: now, source: coalesce(f.source,'api')}] "
            "WITH r, f, policy "
            "FOREACH (_ IN CASE WHEN policy='prefer_high_confidence' AND exists(f.confidence) THEN [1] ELSE [] END | "+
            "  SET r.confidence = CASE WHEN r.confidence IS NULL THEN f.confidence ELSE greatest(r.confidence, f.confidence) END ) "
            "FOREACH (_ IN CASE WHEN policy='prefer_latest' AND exists(f.confidence) THEN [1] ELSE [] END | SET r.confidence = f.confidence) "
            "RETURN count(r) AS relationships"
        )
        client = get_client()
        try:
            rows = client.run_query(cypher, {"facts": facts, "userId": user_id, "policy": policy})
            count = rows[0].data().get("relationships", 0) if rows else 0
            audit_event("knowledge.insert", {"inserted": count, "policy": policy}, user)
            return {"inserted": count}, 201
        except Exception as e:
            audit_event("knowledge.insert.error", {"error": str(e)}, user)
            ns.abort(400, f"Insert failed: {e}")


@ns.route("/search")
class KnowledgeSearch(Resource):
    @jwt_required()
    @ns.expect(search_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        query = payload.get("query", "").strip()
        limit = int(payload.get("limit", 10))
        if not query:
            ns.abort(400, "query is required")
        client = get_client()
        user = get_jwt_identity()
        try:
            if vector_search_enabled():
                # Compute query embedding and use Neo4j vector index (if configured on :Entity(embedding))
                embedding = get_query_embedding(query)
                rows = client.run_query(
                    "CALL db.index.vector.queryNodes('entityEmbedding', $k, $q) YIELD node, score "
                    "RETURN node{.*, labels: labels(node)} AS entity, score ORDER BY score DESC LIMIT $limit",
                    {"k": limit, "q": embedding, "limit": limit},
                )
                results = [r.data() for r in rows]
                audit_event("knowledge.search.vector", {"query_len": len(query), "count": len(results)}, user)
                return {"results": results, "count": len(results), "mode": "vector"}
            else:
                # Fulltext fallback; assumes existence of a fulltext index named 'entityIndex'
                cypher = (
                    "CALL db.index.fulltext.queryNodes('entityIndex', $q) YIELD node, score "
                    "RETURN node{.*, labels: labels(node)} AS entity, score ORDER BY score DESC LIMIT $limit"
                )
                rows = client.run_query(cypher, {"q": query, "limit": limit})
                results = [r.data() for r in rows]
                audit_event("knowledge.search.fulltext", {"query_len": len(query), "count": len(results)}, user)
                return {"results": results, "count": len(results), "mode": "fulltext"}
        except Exception as e:
            audit_event("knowledge.search.error", {"error": str(e)}, user)
            ns.abort(400, f"Search failed: {e}")


@ns.route("/relations/update")
class KnowledgeRelationUpdate(Resource):
    @jwt_required()
    @ns.expect(relation_update_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        subj = payload.get("subject_id")
        pred = payload.get("predicate")
        obj = payload.get("object_id")
        attrs = payload.get("attributes") or {}
        source = payload.get("source") or "api"
        if not isinstance(attrs, dict) or not attrs:
            ns.abort(400, "attributes must be a non-empty object")
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MERGE (s:Entity {id: $sid}) "
            "MERGE (o:Entity {id: $oid}) "
            "MERGE (s)-[r:RELATED {type: $pred}]->(o) "
            "WITH r, $attrs AS attrs, $uid AS uid, timestamp() AS now, $source AS source "
            "SET r += attrs, r.lastUpdated = now, r.updatedBy = uid, r.version = coalesce(r.version,0)+1, r.state = coalesce(r.state,'active') "
            "SET r.provenance = coalesce(r.provenance, []) + [{by: uid, at: now, source: source, action: 'update'}] "
            "RETURN r"
        )
        try:
            rows = get_client().run_query(cypher, {"sid": subj, "oid": obj, "pred": pred, "attrs": attrs, "uid": str(uid), "source": source})
            r = rows[0][0] if rows else {}
            audit_event("knowledge.relation.update", {"subject": subj, "predicate": pred, "object": obj}, user)
            return {"relation": r}, 200
        except Exception as e:
            audit_event("knowledge.relation.update.error", {"error": str(e)}, user)
            ns.abort(400, f"Relation update failed: {e}")


@ns.route("/relations/delete")
class KnowledgeRelationDelete(Resource):
    @jwt_required()
    @ns.expect(relation_delete_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        subj = payload.get("subject_id")
        pred = payload.get("predicate")
        obj = payload.get("object_id")
        reason = payload.get("reason")
        source = payload.get("source") or "api"
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        cypher = (
            "MATCH (s:Entity {id: $sid})-[r:RELATED {type: $pred}]->(o:Entity {id: $oid}) "
            "WITH r, $uid AS uid, timestamp() AS now, $source AS source, $reason AS reason "
            "SET r.state = 'inactive', r.lastUpdated = now, r.updatedBy = uid, r.version = coalesce(r.version,0)+1 "
            "SET r.provenance = coalesce(r.provenance, []) + [{by: uid, at: now, source: source, action: 'deactivate', reason: reason}] "
            "RETURN r"
        )
        try:
            rows = get_client().run_query(cypher, {"sid": subj, "oid": obj, "pred": pred, "uid": str(uid), "source": source, "reason": reason})
            if not rows:
                ns.abort(404, "Relation not found")
            r = rows[0][0]
            audit_event("knowledge.relation.delete", {"subject": subj, "predicate": pred, "object": obj}, user)
            return {"relation": r}, 200
        except Exception as e:
            audit_event("knowledge.relation.delete.error", {"error": str(e)}, user)
            ns.abort(400, f"Relation delete failed: {e}")


@ns.route("/provenance")
class KnowledgeProvenance(Resource):
    @jwt_required()
    def get(self):
        entity_id = (request.args.get("entityId") or "").strip()
        predicate = (request.args.get("predicate") or "").strip()
        direction = (request.args.get("direction") or "both").strip()  # out|in|both
        limit = int(request.args.get("limit", 100))
        if not entity_id:
            ns.abort(400, "entityId is required")
        # Build directional match
        if direction == "out":
            rel_match = "(e:Entity {id: $eid})-[r:RELATED]->(x)"
        elif direction == "in":
            rel_match = "(x)-[r:RELATED]->(e:Entity {id: $eid})"
        else:
            rel_match = "(e:Entity {id: $eid})-[r:RELATED]-(x)"
        where_pred = " WHERE r.type = $pred " if predicate else " "
        cypher = (
            f"MATCH {rel_match} "
            f"{where_pred} "
            "RETURN r ORDER BY r.lastUpdated DESC LIMIT $limit"
        )
        user = get_jwt_identity()
        try:
            rows = get_client().run_query(cypher, {"eid": entity_id, "pred": predicate, "limit": limit})
            rels = [r[0] for r in rows]
            audit_event("knowledge.provenance.get", {"entity": entity_id, "count": len(rels)}, user)
            return {"relations": rels, "count": len(rels)}
        except Exception as e:
            audit_event("knowledge.provenance.error", {"error": str(e)}, user)
            ns.abort(400, f"Provenance fetch failed: {e}")
