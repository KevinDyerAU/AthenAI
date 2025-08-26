from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from ..utils import neo4j_client
from ..utils.rabbitmq import publish_exchange
import uuid
from datetime import datetime
from ..services.autonomy.agent_lifecycle_manager import AgentLifecycleManager, AgentNeed
from ..services.autonomy.autonomous_agent_base import AgentCapability

ns = Namespace("autonomy", description="Autonomous agent management endpoints")

lifecycle_model = ns.model(
    "LifecycleEvent",
    {
        "state": fields.String(required=True, description="Lifecycle state", example="started"),
        "reason": fields.String(required=False, example="manual"),
        "metadata": fields.Raw(required=False),
        "event_id": fields.String(required=False, description="Optional event id (UUID)")
    },
)

metrics_model = ns.model(
    "AgentMetrics",
    {
        "cpu": fields.Float(required=False, example=0.25),
        "mem": fields.Float(required=False, example=512.0),
        "latency_ms": fields.Float(required=False, example=120.5),
        "success_rate": fields.Float(required=False, example=0.99),
        "throughput": fields.Float(required=False, example=12.0),
        "metadata": fields.Raw(required=False),
        "metric_id": fields.String(required=False, description="Optional metric id (UUID)"),
        "timestamp": fields.String(required=False, description="ISO timestamp (defaults now)")
    },
)

drift_model = ns.model(
    "KnowledgeDriftAlert",
    {
        "signal": fields.String(required=True, example="embedding_shift"),
        "severity": fields.String(required=True, example="medium"),
        "details": fields.Raw(required=False),
        "alert_id": fields.String(required=False, description="Optional alert id (UUID)"),
        "timestamp": fields.String(required=False, description="ISO timestamp (defaults now)")
    },
)


def _now_iso():
    return datetime.utcnow().isoformat() + "Z"


@ns.route("/agents/<string:agent_id>/lifecycle")
class AgentLifecycle(Resource):
    @ns.expect(lifecycle_model, validate=True)
    def post(self, agent_id: str):
        payload = request.get_json(force=True)
        event_id = payload.get("event_id") or str(uuid.uuid4())
        state = payload.get("state")
        reason = payload.get("reason")
        metadata = payload.get("metadata") or {}
        timestamp = _now_iso()

        # Persist to Neo4j (upsert agent then add lifecycle event)
        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MERGE (a:Agent {agent_id: $agent_id})\n"
                    "ON CREATE SET a.state=$state, a.name=coalesce(a.name,$agent_id), a.created_at=datetime(), a.updated_at=datetime()\n"
                    "ON MATCH SET a.state=$state, a.updated_at=datetime()",
                    {"agent_id": agent_id, "state": state},
                ),
                (
                    "MATCH (a:Agent {agent_id: $agent_id})\n"
                    "MERGE (e:LifecycleEvent {event_id: $event_id})\n"
                    "ON CREATE SET e.agent_id=$agent_id, e.timestamp=$timestamp, e.state=$state, e.reason=$reason, e.metadata=$metadata\n"
                    "MERGE (a)-[:HAS_EVENT]->(e)",
                    {
                        "agent_id": agent_id,
                        "event_id": event_id,
                        "timestamp": timestamp,
                        "state": state,
                        "reason": reason,
                        "metadata": metadata,
                    },
                ),
            ])
        finally:
            client.close()

        # Publish to RabbitMQ
        publish_exchange("agents.lifecycle", f"lifecycle.{state or 'unknown'}", {
            "agent_id": agent_id,
            "event_id": event_id,
            "timestamp": timestamp,
            "state": state,
            "reason": reason,
            "metadata": metadata,
        })
        return {"status": "ok", "event_id": event_id}, 201


@ns.route("/agents/<string:agent_id>/metrics")
class AgentMetrics(Resource):
    @ns.expect(metrics_model, validate=True)
    def post(self, agent_id: str):
        payload = request.get_json(force=True)
        metric_id = payload.get("metric_id") or str(uuid.uuid4())
        timestamp = payload.get("timestamp") or _now_iso()
        cpu = payload.get("cpu")
        mem = payload.get("mem")
        latency_ms = payload.get("latency_ms")
        success_rate = payload.get("success_rate")
        throughput = payload.get("throughput")
        metadata = payload.get("metadata") or {}

        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MATCH (a:Agent {agent_id: $agent_id})\n"
                    "MERGE (m:AgentMetrics {metric_id: $metric_id})\n"
                    "ON CREATE SET m.agent_id=$agent_id, m.timestamp=$timestamp, m.cpu=$cpu, m.mem=$mem, m.latency_ms=$latency_ms, m.success_rate=$success_rate, m.throughput=$throughput, m.metadata=$metadata\n"
                    "MERGE (a)-[:HAS_METRIC]->(m)",
                    {
                        "agent_id": agent_id,
                        "metric_id": metric_id,
                        "timestamp": timestamp,
                        "cpu": cpu,
                        "mem": mem,
                        "latency_ms": latency_ms,
                        "success_rate": success_rate,
                        "throughput": throughput,
                        "metadata": metadata,
                    },
                ),
            ])
        finally:
            client.close()

        publish_exchange("agents.health", "health.metrics", {
            "agent_id": agent_id,
            "metric_id": metric_id,
            "timestamp": timestamp,
            "cpu": cpu,
            "mem": mem,
            "latency_ms": latency_ms,
            "success_rate": success_rate,
            "throughput": throughput,
            "metadata": metadata,
        })
        return {"status": "ok", "metric_id": metric_id}, 201


@ns.route("/agents/<string:agent_id>/drift")
class AgentDrift(Resource):
    @ns.expect(drift_model, validate=True)
    def post(self, agent_id: str):
        payload = request.get_json(force=True)
        alert_id = payload.get("alert_id") or str(uuid.uuid4())
        timestamp = payload.get("timestamp") or _now_iso()
        signal = payload.get("signal")
        severity = payload.get("severity")
        details = payload.get("details")

        client = neo4j_client.get_client()
        try:
            client.run_queries_atomic([
                (
                    "MATCH (a:Agent {agent_id: $agent_id})\n"
                    "MERGE (d:KnowledgeDriftAlert {alert_id: $alert_id})\n"
                    "ON CREATE SET d.agent_id=$agent_id, d.timestamp=$timestamp, d.signal=$signal, d.severity=$severity, d.details=$details\n"
                    "MERGE (a)-[:RAISED_DRIFT]->(d)",
                    {
                        "agent_id": agent_id,
                        "alert_id": alert_id,
                        "timestamp": timestamp,
                        "signal": signal,
                        "severity": severity,
                        "details": details,
                    },
                ),
            ])
        finally:
            client.close()

        publish_exchange("agents.drift", f"drift.{signal or 'signal'}", {
            "agent_id": agent_id,
            "alert_id": alert_id,
            "timestamp": timestamp,
            "signal": signal,
            "severity": severity,
            "details": details,
        })
        return {"status": "ok", "alert_id": alert_id}, 201


# ---------------- Manual Lifecycle Requests ----------------

manual_request_model = ns.model(
    "ManualAgentCreationRequest",
    {
        "need_type": fields.String(required=True, description="AgentNeed enum value"),
        "required_capabilities": fields.List(fields.String, required=False, description="List of AgentCapability enum values"),
        "priority": fields.Integer(required=False, default=7),
        "justification": fields.String(required=False, default="manual"),
        "performance_requirements": fields.Raw(required=False, description="Perf requirements"),
        "integration_requirements": fields.List(fields.String, required=False),
    },
)


@ns.route("/lifecycle/requests")
class ManualLifecycleRequests(Resource):
    @ns.expect(manual_request_model, validate=True)
    def post(self):
        payload = request.get_json(force=True)
        need_type = payload.get("need_type")
        try:
            need_enum = AgentNeed(need_type)
        except Exception:
            return {"error": f"invalid need_type: {need_type}"}, 400

        caps = set()
        for c in payload.get("required_capabilities", []) or []:
            try:
                caps.add(AgentCapability(c))
            except Exception:
                pass

        need = {
            "type": need_enum,
            "required_capabilities": caps,
            "priority": int(payload.get("priority", 7)),
            "justification": payload.get("justification", "manual"),
            "performance_requirements": payload.get("performance_requirements", {}),
            "integration_requirements": payload.get("integration_requirements", []),
        }
        mgr = current_app.extensions.get("lifecycle_manager") or AgentLifecycleManager()
        request_id = mgr._create_agent_request(need)
        return {"status": "queued", "request_id": request_id}, 202


# ---------------- Lifecycle Manager controls ----------------

@ns.route("/lifecycle/manager/start")
class LifecycleManagerStart(Resource):
    def post(self):
        lm = current_app.extensions.get("lifecycle_manager")
        if not lm:
            return {"error": "lifecycle manager not initialized"}, 500
        lm.start()
        return {"status": "started"}, 200


@ns.route("/lifecycle/manager/stop")
class LifecycleManagerStop(Resource):
    def post(self):
        lm = current_app.extensions.get("lifecycle_manager")
        if not lm:
            return {"error": "lifecycle manager not initialized"}, 500
        lm.stop()
        return {"status": "stopped"}, 200


@ns.route("/lifecycle/manager/status")
class LifecycleManagerStatus(Resource):
    def get(self):
        lm = current_app.extensions.get("lifecycle_manager")
        if not lm:
            return {"error": "lifecycle manager not initialized"}, 500
        return {
            "running": lm._running,
            "active_requests": list(lm._active_requests.keys()),
            "deployed_agents": [
                {
                    "agent_id": aid,
                    **meta,
                }
                for aid, meta in lm._deployed_agents.items()
            ],
            "threads": len(lm._threads),
        }, 200


@ns.route("/lifecycle/retire")
class LifecycleAgentRetire(Resource):
    def post(self):
        payload = request.get_json(force=True) or {}
        agent_id = payload.get("agent_id")
        if not agent_id:
            return {"error": "agent_id required"}, 400
        lm = current_app.extensions.get("lifecycle_manager")
        if not lm:
            return {"error": "lifecycle manager not initialized"}, 500
        ok = lm.retire_agent(agent_id)
        if not ok:
            return {"error": "agent not found or already retired"}, 404
        return {"status": "retired", "agent_id": agent_id}, 200
