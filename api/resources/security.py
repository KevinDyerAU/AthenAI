from __future__ import annotations
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

from ..security.middleware import require_permission
from ..services.compliance import ComplianceService
from ..services.incidents import IncidentService
from ..services.sandbox import SandboxService

ns = Namespace("security", description="Security, compliance, sandboxing, and incidents APIs")

compliance_svc = ComplianceService()
incident_svc = IncidentService()
sandbox_svc = SandboxService()

compliance_model = ns.model("ComplianceReport", {
    "ok": fields.Boolean,
    "at": fields.Integer,
    "checks": fields.Raw,
})

incident_model = ns.model("SecurityIncident", {
    "id": fields.String,
    "kind": fields.String,
    "severity": fields.String,
    "message": fields.String,
    "context": fields.Raw,
    "at": fields.Integer,
})

sandbox_policy_model = ns.model("SandboxPolicy", {
    "cpu_quota": fields.Float,
    "memory_mb": fields.Integer,
    "network": fields.String,
    "filesystem": fields.String,
    "dynamic": fields.Boolean,
})


@ns.route("/compliance/assess")
class ComplianceAssess(Resource):
    @jwt_required()
    @require_permission("security", "read")
    @ns.marshal_with(compliance_model)
    def get(self):
        rep = compliance_svc.assess()
        # Best-effort persist (can be disabled by env)
        try:
            compliance_svc.persist_report(rep)
        except Exception:
            pass
        return rep


@ns.route("/incidents")
class Incidents(Resource):
    @jwt_required()
    @require_permission("security", "read")
    @ns.marshal_with(ns.model("IncidentList", {
        "items": fields.List(fields.Nested(incident_model)),
    }))
    def get(self):
        kind = request.args.get("kind")
        severity = request.args.get("severity")
        try:
            limit = int(request.args.get("limit", 50))
        except Exception:
            limit = 50
        return {"items": incident_svc.list(limit=limit, kind=kind, severity=severity)}

    @jwt_required()
    @require_permission("security", "write")
    @ns.expect(ns.model("IncidentCreate", {
        "kind": fields.String(required=True),
        "severity": fields.String(required=True, description="info|low|medium|high|critical"),
        "message": fields.String(required=True),
        "context": fields.Raw(required=False),
    }), validate=True)
    @ns.marshal_with(incident_model, code=201)
    def post(self):
        body = request.get_json() or {}
        it = incident_svc.record(
            kind=body.get("kind"),
            severity=body.get("severity"),
            message=body.get("message"),
            context=body.get("context") or {},
        )
        return it, 201


@ns.route("/sandbox/policy")
class SandboxPolicy(Resource):
    @jwt_required()
    @require_permission("security", "read")
    @ns.marshal_with(sandbox_policy_model)
    def get(self):
        return sandbox_svc.current_policy()


@ns.route("/sandbox/evaluate")
class SandboxEvaluate(Resource):
    @jwt_required()
    @require_permission("security", "read")
    @ns.expect(ns.model("SandboxEvaluate", {"risk_score": fields.Float(required=True)}), validate=True)
    @ns.marshal_with(sandbox_policy_model)
    def post(self):
        body = request.get_json() or {}
        rs = float(body.get("risk_score", 0.0))
        rs = max(0.0, min(1.0, rs))
        return sandbox_svc.evaluate(rs)
