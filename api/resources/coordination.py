from __future__ import annotations
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.coordination import CoordinationService, Task
from ..utils.audit import audit_event
from ..services.self_healing import SelfHealingService

ns = Namespace("coordination", description="Agent coordination and communication APIs")
svc = CoordinationService()

agent_model = ns.model("AgentRegister", {
    "agent_id": fields.String(required=True),
    "role": fields.String(required=True, description="strategic|tactical|operational"),
    "capabilities": fields.List(fields.String, required=True),
    "perf_score": fields.Float(required=False, description="0..1")
})

heartbeat_model = ns.model("Heartbeat", {
    "agent_id": fields.String(required=True),
    "workload": fields.Float(required=False)
})

allocate_model = ns.model("TaskAllocate", {
    "id": fields.String(required=True),
    "type": fields.String(required=True),
    "requirements": fields.List(fields.String, required=True),
    "priority": fields.Integer(required=False, default=0)
})

conflict_model = ns.model("Conflict", {
    "parties": fields.List(fields.String, required=True),
    "resource": fields.String(required=True),
    "priority": fields.Raw(required=False, description="map agent_id->int")
})

consensus_model = ns.model("Consensus", {
    "participants": fields.List(fields.String, required=True),
    "proposal": fields.Raw(required=True),
    "weights": fields.Raw(required=False),
    "timeout_ms": fields.Integer(required=False, default=1000)
})

route_model = ns.model("Route", {
    "kind": fields.String(required=True),
    "payload": fields.Raw(required=True),
    "targets": fields.List(fields.String, required=False),
    "broadcast": fields.Boolean(required=False, default=False)
})

knowledge_model = ns.model("ShareKnowledge", {
    "topic": fields.String(required=True),
    "content": fields.Raw(required=True),
    "tags": fields.List(fields.String, required=False)
})


@ns.route("/agents")
class AgentsResource(Resource):
    @jwt_required()
    def get(self):
        return {"agents": svc.list_agents()}

    @jwt_required()
    @ns.expect(agent_model, validate=True)
    def post(self):
        data = request.get_json() or {}
        res = svc.register_agent(data["agent_id"], data["role"], data["capabilities"], data.get("perf_score", 0.5))
        audit_event("api.coord.agent.register", res, get_jwt_identity())
        return res


@ns.route("/agents/heartbeat")
class AgentHeartbeat(Resource):
    @jwt_required()
    @ns.expect(heartbeat_model, validate=True)
    def post(self):
        data = request.get_json() or {}
        out = svc.heartbeat(data["agent_id"], data.get("workload"))
        if isinstance(out, tuple):
            return out
        return out


@ns.route("/tasks/allocate")
class TaskAllocate(Resource):
    @jwt_required()
    @ns.expect(allocate_model, validate=True)
    def post(self):
        data = request.get_json() or {}
        task = Task(id=data["id"], type=data["type"], requirements=data["requirements"], priority=int(data.get("priority", 0)))
        sla = data.get("sla")
        predict_metric = data.get("predict_metric")  # e.g., 'cpu_load' or 'queue_depth'
        predictor = None
        if predict_metric:
            sh = SelfHealingService()
            # Predict per-agent metric using naming convention '<agent_id>.<metric>' if present
            def predictor_fn(agent_info):
                metric_name = f"{agent_info.id}.{predict_metric}"
                try:
                    return sh.forecast(metric_name, steps=1) or 0.0
                except Exception:
                    return 0.0
            predictor = predictor_fn
        out = svc.allocate_task(task, sla=sla, predict=predictor)
        return out, 200 if out.get("allocated") else 409


@ns.route("/rebalance")
class Rebalance(Resource):
    @jwt_required()
    def post(self):
        body = request.get_json(silent=True) or {}
        apply = bool(body.get("apply", False))
        return svc.rebalance(apply=apply)


@ns.route("/conflict/resolve")
class ConflictResolve(Resource):
    @jwt_required()
    @ns.expect(conflict_model, validate=True)
    def post(self):
        data = request.get_json() or {}
        return svc.resolve_conflict(data["parties"], data["resource"], data.get("priority") or {})


@ns.route("/consensus")
class Consensus(Resource):
    @jwt_required()
    @ns.expect(consensus_model, validate=True)
    def post(self):
        data = request.get_json() or {}
        return svc.consensus(data["participants"], data["proposal"], data.get("weights"), int(data.get("timeout_ms", 1000)))


@ns.route("/route")
class Route(Resource):
    @jwt_required()
    @ns.expect(route_model, validate=True)
    def post(self):
        data = request.get_json() or {}
        return svc.route_message(data["kind"], data["payload"], data.get("targets"), bool(data.get("broadcast", False)))


@ns.route("/knowledge/share")
class KnowledgeShare(Resource):
    @jwt_required()
    @ns.expect(knowledge_model, validate=True)
    def post(self):
        data = request.get_json() or {}
        user = get_jwt_identity()
        out = svc.share_knowledge(user, data["topic"], data["content"], data.get("tags"))
        return out
