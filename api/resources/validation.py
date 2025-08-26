from __future__ import annotations
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.validation import ValidationService
from ..utils.audit import audit_event
from ..extensions import socketio

ns = Namespace("validation", description="Testing, validation and quality assurance APIs")
svc = ValidationService()

run_model = ns.model("ValidationRun", {
    "unit_selectors": fields.List(fields.String, required=False),
    "integration_scenarios": fields.List(fields.String, required=False),
    "load_profile": fields.Raw(required=False),
    "behavior_suites": fields.List(fields.String, required=False),
    "include_performance": fields.Boolean(required=False, default=True),
    "include_behavior": fields.Boolean(required=False, default=True)
})

gates_model = ns.model("QualityGates", {
    "min_pass_rate": fields.Float(required=False, description="0..1"),
    "max_error_rate": fields.Float(required=False, description="0..1"),
    "max_p95_latency_ms": fields.Float(required=False, description="milliseconds or null")
})


@ns.route("/run")
class ValidationRunResource(Resource):
    @jwt_required()
    @ns.expect(run_model, validate=False)
    def post(self):
        cfg = request.get_json(silent=True) or {}
        res = svc.run_all(cfg)
        audit_event("qa.validation.run", {"id": res.get("id"), "ok": res.get("gate", {}).get("ok")}, get_jwt_identity())
        try:
            socketio.emit("qa.validation.report", res)
            socketio.emit("qa.validation.report", res, namespace="/qa")
        except Exception:
            pass
        return res


@ns.route("/report/last")
class ValidationLastReport(Resource):
    @jwt_required()
    def get(self):
        return svc.get_last_report() or {}


@ns.route("/history")
class ValidationHistory(Resource):
    @jwt_required()
    def get(self):
        try:
            limit = int(request.args.get("limit", 20))
        except Exception:
            limit = 20
        return {"items": svc.list_history(limit=limit)}


@ns.route("/gates")
class ValidationGates(Resource):
    @jwt_required()
    def get(self):
        return {"gates": svc.set_gates({})["gates"]}

    @jwt_required()
    @ns.expect(gates_model, validate=False)
    def post(self):
        body = request.get_json(silent=True) or {}
        out = svc.set_gates(body)
        try:
            socketio.emit("qa.gates.updated", out)
            socketio.emit("qa.gates.updated", out, namespace="/qa")
        except Exception:
            pass
        return out
