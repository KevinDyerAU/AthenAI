from __future__ import annotations
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.self_healing import SelfHealingService
from ..utils.audit import audit_event
from ..utils.rabbitmq import publish_exchange
from ..extensions import socketio

ns = Namespace("self_healing", description="Self-Healing and Adaptation APIs")
svc = SelfHealingService()

analyze_model = ns.model("SHAnalyze", {
    "metrics": fields.Raw(required=True, description="key->float metrics"),
    "context": fields.Raw(required=False, description="context including services/queues/containers"),
})

heal_model = ns.model("SHHeal", {
    "issue": fields.Raw(required=False, description="diagnosis from analyze"),
    "context": fields.Raw(required=False),
    "strategy": fields.String(required=False),
    "dry_run": fields.Boolean(default=True),
})


@ns.route("/analyze")
class SHAnalyze(Resource):
    @jwt_required()
    @ns.expect(analyze_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        metrics = payload.get("metrics") or {}
        context = payload.get("context") or {}
        user = get_jwt_identity()
        context["user"] = user
        result = svc.analyze(metrics, context)
        audit_event("self_healing.api.analyze", {"anomalies": len(result.get("anomalies", []))}, user)
        try:
            socketio.emit("self_healing:analyze", result)
        except Exception:
            pass
        return result


@ns.route("/heal")
class SHHeal(Resource):
    @jwt_required()
    @ns.expect(heal_model, validate=True)
    def post(self):
        payload = request.get_json() or {}
        issue = payload.get("issue") or {}
        context = payload.get("context") or {}
        strategy = payload.get("strategy")
        dry_run = bool(payload.get("dry_run", True))
        user = get_jwt_identity()
        context["user"] = user
        result = svc.heal(issue, context, dry_run=dry_run, strategy=strategy)
        audit_event("self_healing.api.heal", {"strategy": result.get("strategy")}, user)
        try:
            socketio.emit("self_healing:heal", result)
        except Exception:
            pass
        return result


@ns.route("/strategies")
class SHStrategies(Resource):
    @jwt_required()
    def get(self):
        return {"strategies": svc.strategies()}


@ns.route("/learning")
class SHLearning(Resource):
    @jwt_required()
    def get(self):
        return svc.learning_stats()
