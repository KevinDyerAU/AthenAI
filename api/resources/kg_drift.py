from __future__ import annotations
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.knowledge_drift import (
    detect_semantic_drift,
    detect_conflicts,
    assess_quality,
    remediate_conflict,
    find_dedup_candidates,
    merge_entities,
    enrich_embeddings,
    record_quality_snapshot,
    get_quality_trend,
)
from ..utils.audit import audit_event
from ..extensions import socketio
from ..utils.rabbitmq import publish_exchange


ns = Namespace("kg_drift", description="Knowledge Drift detection, assessment, and remediation")


detect_model = ns.model("KGDriftDetect", {
    "sample_limit": fields.Integer(default=100, description="Entities to sample for semantic drift"),
    "similarity_threshold": fields.Float(default=0.80, description="Cosine similarity threshold for drift"),
    "conflict_limit": fields.Integer(default=200, description="Max contradictions to surface"),
})

remediate_model = ns.model("KGDriftRemediate", {
    "subject_id": fields.String(required=True),
    "predicate": fields.String(required=True),
    "strategy": fields.String(default="confidence", description="confidence|recency"),
    "dry_run": fields.Boolean(default=False),
    "escalate": fields.Boolean(default=False),
})

dedup_model = ns.model("KGCurationDedup", {
    "limit": fields.Integer(default=100)
})

merge_model = ns.model("KGCurationMerge", {
    "target_id": fields.String(required=True),
    "duplicate_ids": fields.List(fields.String, required=True),
    "dry_run": fields.Boolean(default=True),
})

enrich_model = ns.model("KGCurationEnrichEmbeddings", {
    "limit": fields.Integer(default=200)
})

approve_model = ns.model("KGResolutionApprove", {
    "request_id": fields.String(required=True),
    "subject_id": fields.String(required=True),
    "predicate": fields.String(required=True),
    "strategy": fields.String(default="confidence"),
})

reject_model = ns.model("KGResolutionReject", {
    "request_id": fields.String(required=True),
    "reason": fields.String(required=False),
})


@ns.route("/detect")
class KGDriftDetect(Resource):
    @jwt_required()
    @ns.expect(detect_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        sample_limit = int(payload.get("sample_limit", 100))
        similarity_threshold = float(payload.get("similarity_threshold", 0.80))
        conflict_limit = int(payload.get("conflict_limit", 200))
        user = get_jwt_identity()
        semantic = detect_semantic_drift(sample_limit=sample_limit, similarity_threshold=similarity_threshold)
        conflicts = detect_conflicts(limit=conflict_limit)
        audit_event("kg_drift.detect", {
            "semantic": len(semantic),
            "conflicts": len(conflicts),
        }, user)
        # Publish events for each signal (lightweight fan-out)
        for s in semantic:
            try:
                publish_exchange("kg.drift", f"drift.{s.kind}", {"signal": s.kind, "severity": s.severity, "details": s.details})
                socketio.emit("kg_drift:drift", {"signal": s.kind, "severity": s.severity, "details": s.details})
            except Exception:
                pass
        for c in conflicts:
            try:
                publish_exchange("kg.drift", f"drift.{c.kind}", {"signal": c.kind, "severity": c.severity, "details": c.details})
                socketio.emit("kg_drift:drift", {"signal": c.kind, "severity": c.severity, "details": c.details})
            except Exception:
                pass
        return {
            "semantic": [s.__dict__ for s in semantic],
            "conflicts": [c.__dict__ for c in conflicts],
        }


@ns.route("/quality")
class KGDriftQuality(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        metrics = assess_quality()
        audit_event("kg_drift.quality", metrics, user)
        return metrics


@ns.route("/quality/trend")
class KGDriftQualityTrend(Resource):
    @jwt_required()
    def get(self):
        limit = int(request.args.get("limit", 50))
        trend = get_quality_trend(limit=limit)
        return {"trend": trend}


@ns.route("/quality/snapshot")
class KGDriftQualitySnapshot(Resource):
    @jwt_required()
    def post(self):
        user = get_jwt_identity()
        uid = user.get("id") if isinstance(user, dict) else user
        metrics = assess_quality()
        record_quality_snapshot(metrics, user_id=str(uid) if uid else None)
        audit_event("kg_drift.quality.snapshot", metrics, user)
        try:
            socketio.emit("kg_drift:quality.snapshot", metrics)
        except Exception:
            pass
        return {"recorded": True, "metrics": metrics}


@ns.route("/remediate")
class KGDriftRemediate(Resource):
    @jwt_required()
    @ns.expect(remediate_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        sid = payload.get("subject_id", "").strip()
        pred = payload.get("predicate", "").strip()
        strategy = payload.get("strategy", "confidence").strip()
        dry_run = bool(payload.get("dry_run", False))
        escalate = bool(payload.get("escalate", False))
        if not sid or not pred:
            ns.abort(400, "subject_id and predicate are required")
        user = get_jwt_identity()
        uid = user["id"] if isinstance(user, dict) else user
        result = remediate_conflict(sid, pred, strategy=strategy, dry_run=dry_run, escalate=escalate, user_id=str(uid) if uid else None)
        audit_event("kg_drift.remediate", {"subject_id": sid, "predicate": pred, "strategy": strategy}, user)
        # Emit UI signals
        try:
            if result.get("escalated"):
                socketio.emit("kg_drift:resolution.escalated", {"subject": sid, "predicate": pred})
            elif result.get("dry_run"):
                socketio.emit("kg_drift:remediate.plan", {"subject": sid, "predicate": pred, "plan": result.get("plan")})
            else:
                socketio.emit("kg_drift:remediate.applied", {"subject": sid, "predicate": pred})
        except Exception:
            pass
        return result


@ns.route("/resolution/requests")
class KGResolutionRequests(Resource):
    @jwt_required()
    def get(self):
        from ..utils.neo4j_client import get_client
        client = get_client()
        rows = client.run_query(
            "MATCH (rr:ResolutionRequest) WHERE coalesce(rr.status,'pending')='pending' RETURN rr ORDER BY rr.createdAt DESC LIMIT 200"
        )
        return {"requests": [r[0] for r in rows]}


@ns.route("/resolution/approve")
class KGResolutionApprove(Resource):
    @jwt_required()
    @ns.expect(approve_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        req_id = payload.get("request_id")
        sid = payload.get("subject_id")
        pred = payload.get("predicate")
        strategy = payload.get("strategy", "confidence")
        user = get_jwt_identity()
        uid = user.get("id") if isinstance(user, dict) else user
        # Apply remediation
        result = remediate_conflict(sid, pred, strategy=strategy, dry_run=False, escalate=False, user_id=str(uid) if uid else None)
        # Mark request approved
        from ..utils.neo4j_client import get_client
        client = get_client()
        client.run_query(
            """
            MATCH (rr:ResolutionRequest {id: $id})
            SET rr.status='approved', rr.approvedAt=timestamp(), rr.approvedBy=$uid
            """,
            {"id": req_id, "uid": str(uid) if uid else None},
        )
        audit_event("kg_resolution.approved", {"request_id": req_id, "subject": sid, "predicate": pred, "strategy": strategy}, user)
        try:
            publish_exchange("kg.drift", "resolution.approved", {"request_id": req_id, "subject": sid, "predicate": pred})
            socketio.emit("kg_drift:resolution.approved", {"request_id": req_id, "subject": sid, "predicate": pred})
        except Exception:
            pass
        return {"approved": True, "result": result}


@ns.route("/resolution/reject")
class KGResolutionReject(Resource):
    @jwt_required()
    @ns.expect(reject_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        req_id = payload.get("request_id")
        reason = payload.get("reason")
        user = get_jwt_identity()
        uid = user.get("id") if isinstance(user, dict) else user
        from ..utils.neo4j_client import get_client
        client = get_client()
        client.run_query(
            """
            MATCH (rr:ResolutionRequest {id: $id})
            SET rr.status='rejected', rr.rejectedAt=timestamp(), rr.rejectedBy=$uid, rr.rejectionReason=$reason
            """,
            {"id": req_id, "uid": str(uid) if uid else None, "reason": reason},
        )
        audit_event("kg_resolution.rejected", {"request_id": req_id, "reason": reason}, user)
        try:
            publish_exchange("kg.drift", "resolution.rejected", {"request_id": req_id, "reason": reason})
            socketio.emit("kg_drift:resolution.rejected", {"request_id": req_id, "reason": reason})
        except Exception:
            pass
        return {"rejected": True}


@ns.route("/curation/dedup")
class KGCurationDedup(Resource):
    @jwt_required()
    @ns.expect(dedup_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        limit = int(payload.get("limit", 100))
        user = get_jwt_identity()
        candidates = find_dedup_candidates(limit=limit)
        audit_event("kg_curation.dedup", {"groups": len(candidates)}, user)
        try:
            socketio.emit("kg_curation:dedup", {"groups": len(candidates)})
        except Exception:
            pass
        return {"candidates": candidates, "count": len(candidates)}


@ns.route("/curation/merge")
class KGCurationMerge(Resource):
    @jwt_required()
    @ns.expect(merge_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        target = payload.get("target_id", "").strip()
        dups = payload.get("duplicate_ids") or []
        dry_run = bool(payload.get("dry_run", True))
        if not target or not isinstance(dups, list) or not dups:
            ns.abort(400, "target_id and duplicate_ids are required")
        user = get_jwt_identity()
        uid = user.get("id") if isinstance(user, dict) else user
        result = merge_entities(target, dups, dry_run=dry_run, user_id=str(uid) if uid else None)
        audit_event("kg_curation.merge", {"target": target, "dups": len(dups), "dry_run": dry_run}, user)
        try:
            socketio.emit("kg_curation:merge", {"target": target, "dups": len(dups), "dry_run": dry_run})
        except Exception:
            pass
        return result


@ns.route("/curation/enrich_embeddings")
class KGCurationEnrichEmbeddings(Resource):
    @jwt_required()
    @ns.expect(enrich_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        limit = int(payload.get("limit", 200))
        result = enrich_embeddings(limit=limit)
        user = get_jwt_identity()
        audit_event("kg_curation.enrich_embeddings", {"updated": result.get("updated")}, user)
        try:
            socketio.emit("kg_curation:enrich_embeddings", {"updated": result.get("updated")})
        except Exception:
            pass
        return result
