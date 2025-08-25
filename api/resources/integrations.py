import os
from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from ..extensions import db, socketio
from ..models import Agent, AgentRun
from ..utils.audit import audit_event
from ..metrics import record_agent_workflow

ns = Namespace("integrations", description="Inbound integration webhooks (e.g., n8n)")

run_update_model = ns.model("RunUpdate", {
    "execution_id": fields.String(required=True),
    "status": fields.String(required=True, description="queued|running|completed|failed"),
    "result": fields.Raw,
    "error": fields.String,
    "metrics": fields.Raw,
})


def _check_integration_secret():
    secret = os.getenv("INTEGRATION_SECRET")
    if not secret:
        # If no secret configured, reject to avoid unauthenticated updates
        ns.abort(403, "Integration secret not configured")
    inbound = request.headers.get("X-Integration-Token") or request.headers.get("X-INT-TOKEN")
    if inbound != secret:
        ns.abort(403, "Invalid integration token")


@ns.route("/n8n/runs")
class N8nRunUpdate(Resource):
    @ns.expect(run_update_model, validate=True)
    def post(self):
        _check_integration_secret()
        payload = request.get_json() or {}
        execution_id = payload.get("execution_id")
        status = (payload.get("status") or "").lower()
        result = payload.get("result")
        error = payload.get("error")
        metrics = payload.get("metrics")

        run: AgentRun | None = AgentRun.query.filter_by(execution_id=execution_id).first()
        if not run:
            ns.abort(404, "Run not found")

        # Update run
        now = datetime.utcnow()
        run.status = status
        if status in ("completed", "failed"):
            run.finished_at = now
            run.compute_duration()
        if result is not None:
            run.result = result
        if error:
            run.error = error
        if metrics is not None:
            run.metrics = metrics

        # Update agent status
        agent = Agent.query.get(run.agent_id)
        if agent:
            agent.status = "idle" if status == "completed" else ("error" if status == "failed" else status)

        db.session.commit()
        audit_event("agent.run.update", {"execution_id": execution_id, "status": status}, None)

        # Emit Prometheus workflow metrics on terminal states
        if status in ("completed", "failed"):
            try:
                duration_sec = (run.duration_ms or 0) / 1000.0
                record_agent_workflow(
                    workflow_name=agent.name if agent and agent.name else "agent",
                    agent_type=agent.type if agent and agent.type else "generic",
                    duration_sec=duration_sec,
                    success=(status == "completed"),
                )
            except Exception:
                pass
        # Emit WS update for real-time consumers: room by execution_id and by agent_id
        try:
            payload = {
                "execution_id": run.execution_id,
                "agent_id": run.agent_id,
                "status": run.status,
                "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                "duration_ms": run.duration_ms,
                "metrics": run.metrics,
                "error": run.error,
            }
            socketio.emit("agent_run:update", payload, room=run.execution_id)
            socketio.emit("agent_run:update", payload, room=f"agent:{run.agent_id}")
        except Exception:
            pass
        return {"message": "updated", "execution_id": execution_id, "status": status}
