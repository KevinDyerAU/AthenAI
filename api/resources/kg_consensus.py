from __future__ import annotations
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.neo4j_client import get_client
from ..utils.audit import audit_event
from ..utils.kg_schema import monitor_consistency

ns = Namespace("kg_consensus", description="Knowledge Graph conflict detection, voting and resolution")

vote_model = ns.model("KGVote", {
    "subject_id": fields.String(required=True),
    "predicate": fields.String(required=True),
    "object_id": fields.String(required=True),
    "value": fields.Integer(required=True, description="1 for approve, -1 for reject", enum=[-1, 1]),
})

resolve_model = ns.model("KGResolve", {
    "subject_id": fields.String(required=True),
    "predicate": fields.String(required=True),
    "strategy": fields.String(default="votes", description="votes|confidence"),
    "quorum": fields.Integer(default=1),
})

rollback_model = ns.model("KGRollback", {
    "subject_id": fields.String(required=True),
    "predicate": fields.String(required=True),
    "object_id": fields.String(required=True, description="Set this object as active and demote others"),
})


@ns.route("/conflicts/open")
class KGOpenConflicts(Resource):
    @jwt_required()
    def get(self):
        """List potential contradictions (subject+predicate with multiple objects)."""
        data = monitor_consistency(limit=200)
        return {"contradictions": data.get("contradictions", [])}


@ns.route("/conflicts/vote")
class KGVote(Resource):
    @jwt_required()
    @ns.expect(vote_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        sid = payload["subject_id"].strip()
        pred = payload["predicate"].strip()
        oid = payload["object_id"].strip()
        val = int(payload["value"])
        if val not in (-1, 1):
            ns.abort(400, "value must be -1 or 1")
        user = get_jwt_identity()
        voter_id = user["id"] if isinstance(user, dict) else user
        client = get_client()
        cypher = (
            "MERGE (c:Conflict {sid: $sid, pred: $pred}) "
            "MERGE (o:Option {sid: $sid, pred: $pred, oid: $oid}) "
            "MERGE (c)-[:OPTION]->(o) "
            "MERGE (v:Voter {id: $voter}) "
            "MERGE (v)-[r:VOTED {sid: $sid, pred: $pred, oid: $oid}]->(c) "
            "SET r.value = $val, r.at = timestamp() "
            "RETURN c, o"
        )
        try:
            client.run_query(cypher, {"sid": sid, "pred": pred, "oid": oid, "voter": str(voter_id), "val": val})
            audit_event("kg.vote", {"sid": sid, "pred": pred, "oid": oid, "value": val}, user)
            return {"ok": True}
        except Exception as e:
            audit_event("kg.vote.error", {"error": str(e)}, user)
            ns.abort(400, f"Vote failed: {e}")


@ns.route("/conflicts/resolve")
class KGResolve(Resource):
    @jwt_required()
    @ns.expect(resolve_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        sid = payload["subject_id"].strip()
        pred = payload["predicate"].strip()
        strategy = payload.get("strategy", "votes")
        quorum = int(payload.get("quorum", 1))
        user = get_jwt_identity()
        client = get_client()

        if strategy == "votes":
            # Aggregate votes per option
            agg = client.run_query(
                "MATCH (c:Conflict {sid: $sid, pred: $pred})<- [r:VOTED]-(:Voter) "
                "RETURN r.oid AS oid, sum(r.value) AS score",
                {"sid": sid, "pred": pred},
            )
        else:  # confidence
            agg = client.run_query(
                "MATCH (s:Entity {id: $sid})-[rel:RELATED {type: $pred}]->(o:Entity) "
                "RETURN o.id AS oid, coalesce(rel.confidence, 0.0) AS score",
                {"sid": sid, "pred": pred},
            )
        scores = [(r["oid"], r["score"]) for r in agg]
        if not scores:
            ns.abort(400, "No options to resolve")
        scores.sort(key=lambda x: x[1], reverse=True)
        winner, win_score = scores[0]
        if quorum and win_score < quorum and strategy == "votes":
            return {"resolved": False, "reason": "quorum_not_met", "top": {"object_id": winner, "score": win_score}}

        # Promote winner to active, demote others to rejected
        cypher = (
            "MATCH (s:Entity {id: $sid})-[r:RELATED {type: $pred}]->(o:Entity) "
            "WITH r, o, $winner AS winner, timestamp() AS now "
            "SET r.state = CASE WHEN o.id = winner THEN 'active' ELSE 'rejected' END, "
            "    r.lastUpdated = now, r.version = coalesce(r.version,0)+1 "
        )
        try:
            client.run_query(cypher, {"sid": sid, "pred": pred, "winner": winner})
            audit_event("kg.resolve", {"sid": sid, "pred": pred, "winner": winner, "strategy": strategy, "score": win_score}, user)
            return {"resolved": True, "winner": winner}
        except Exception as e:
            audit_event("kg.resolve.error", {"error": str(e)}, user)
            ns.abort(400, f"Resolve failed: {e}")


@ns.route("/relations/rollback")
class KGRollback(Resource):
    @jwt_required()
    @ns.expect(rollback_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        sid = payload["subject_id"].strip()
        pred = payload["predicate"].strip()
        target = payload["object_id"].strip()
        user = get_jwt_identity()
        client = get_client()
        cypher = (
            "MATCH (s:Entity {id: $sid})-[r:RELATED {type: $pred}]->(o:Entity) "
            "WITH r, o, $target AS target, timestamp() AS now "
            "SET r.state = CASE WHEN o.id = target THEN 'active' ELSE 'rejected' END, "
            "    r.lastUpdated = now, r.version = coalesce(r.version,0)+1, r.updatedBy = $userId "
        )
        try:
            user_id = user["id"] if isinstance(user, dict) else user
            client.run_query(cypher, {"sid": sid, "pred": pred, "target": target, "userId": user_id})
            audit_event("kg.rollback", {"sid": sid, "pred": pred, "target": target}, user)
            return {"ok": True}
        except Exception as e:
            audit_event("kg.rollback.error", {"error": str(e)}, user)
            ns.abort(400, f"Rollback failed: {e}")
