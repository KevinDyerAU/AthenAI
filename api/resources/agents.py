from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import Agent, AgentRun
from ..schemas import AgentSchema, AgentCreateSchema, AgentUpdateSchema
from ..utils.audit import audit_event
from ..utils.n8n_client import trigger_webhook
from datetime import datetime

ns = Namespace("agents", description="Agent management endpoints")

agent_model = ns.model("Agent", {
    "id": fields.Integer,
    "name": fields.String,
    "type": fields.String,
    "status": fields.String,
    "config": fields.Raw,
    "created_at": fields.DateTime,
    "updated_at": fields.DateTime,
})

agent_list_model = ns.model("AgentList", {
    "items": fields.List(fields.Nested(agent_model)),
    "total": fields.Integer,
})

agent_schema = AgentSchema()
agent_create_schema = AgentCreateSchema()
agent_update_schema = AgentUpdateSchema()


@ns.route("")
class AgentCollection(Resource):
    @jwt_required()
    @ns.marshal_with(agent_list_model)
    def get(self):
        q = Agent.query
        total = q.count()
        items = q.order_by(Agent.created_at.desc()).all()
        return {"items": [agent_schema.dump(a) for a in items], "total": total}

    @jwt_required()
    @ns.expect(ns.model("AgentCreate", {
        "name": fields.String(required=True),
        "type": fields.String(required=True),
        "config": fields.Raw,
    }), validate=True)
    @ns.marshal_with(agent_model, code=201)
    def post(self):
        payload = request.get_json() or {}
        data = agent_create_schema.load(payload)
        if Agent.query.filter_by(name=data["name"]).first():
            ns.abort(409, "Agent name already exists")
        agent = Agent(**data)
        db.session.add(agent)
        db.session.commit()
        return agent_schema.dump(agent), 201


@ns.route("/<int:agent_id>")
class AgentItem(Resource):
    @jwt_required()
    @ns.marshal_with(agent_model)
    def get(self, agent_id: int):
        agent = Agent.query.get_or_404(agent_id)
        return agent_schema.dump(agent)

    @jwt_required()
    @ns.expect(ns.model("AgentUpdate", {
        "name": fields.String,
        "type": fields.String,
        "status": fields.String,
        "config": fields.Raw,
    }), validate=True)
    @ns.marshal_with(agent_model)
    def put(self, agent_id: int):
        agent = Agent.query.get_or_404(agent_id)
        payload = request.get_json() or {}
        data = agent_update_schema.load(payload)
        for k, v in data.items():
            setattr(agent, k, v)
        db.session.commit()
        return agent_schema.dump(agent)

    @jwt_required()
    def delete(self, agent_id: int):
        agent = Agent.query.get_or_404(agent_id)
        db.session.delete(agent)
        db.session.commit()
        return {"message": "Deleted"}, 204


@ns.route("/<int:agent_id>/execute")
class AgentExecute(Resource):
    @jwt_required()
    def post(self, agent_id: int):
        agent = Agent.query.get_or_404(agent_id)
        agent.status = "running"
        # create an AgentRun placeholder
        execution_id = f"run-{agent.id}-{int(datetime.utcnow().timestamp())}"
        run = AgentRun(
            agent_id=agent.id,
            execution_id=execution_id,
            status="queued",
            started_at=datetime.utcnow(),
        )
        db.session.add(run)
        db.session.commit()
        # Trigger n8n webhook (configure corresponding workflow to receive this)
        payload = {"agent_id": agent.id, "name": agent.name, "type": agent.type, "execution_id": execution_id}
        try:
            trigger_webhook("webhook/agent-execute", payload)
            audit_event("agent.execute.queued", payload, None)
        except Exception as e:
            audit_event("agent.execute.error", {"agent_id": agent.id, "error": str(e)}, None)
        return {"message": "Execution started", "agent_id": agent.id, "execution_id": execution_id}, 202


@ns.route("/<int:agent_id>/status")
class AgentStatus(Resource):
    @jwt_required()
    def get(self, agent_id: int):
        agent = Agent.query.get_or_404(agent_id)
        return {"id": agent.id, "status": agent.status}


run_model = ns.model("AgentRun", {
    "id": fields.Integer,
    "execution_id": fields.String,
    "status": fields.String,
    "started_at": fields.DateTime,
    "finished_at": fields.DateTime,
    "duration_ms": fields.Integer,
    "result": fields.Raw,
    "error": fields.String,
    "metrics": fields.Raw,
})


@ns.route("/<int:agent_id>/runs")
class AgentRuns(Resource):
    @jwt_required()
    @ns.marshal_with(ns.model("AgentRunList", {
        "items": fields.List(fields.Nested(run_model)),
        "total": fields.Integer,
    }))
    def get(self, agent_id: int):
        agent = Agent.query.get_or_404(agent_id)
        status = request.args.get("status")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        q = AgentRun.query.filter_by(agent_id=agent.id)
        if status:
            q = q.filter(AgentRun.status == status)
        q = q.order_by(AgentRun.id.desc())
        total = q.count()
        items = q.offset(offset).limit(limit).all()
        def to_dict(r: AgentRun):
            return {
                "id": r.id,
                "execution_id": r.execution_id,
                "status": r.status,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
                "duration_ms": r.duration_ms,
                "result": r.result,
                "error": r.error,
                "metrics": r.metrics,
            }
        return {"items": [to_dict(r) for r in items], "total": total}


@ns.route("/<int:agent_id>/metrics")
class AgentMetrics(Resource):
    @jwt_required()
    def get(self, agent_id: int):
        Agent.query.get_or_404(agent_id)
        # Simple aggregates; for complex metrics, consider Prometheus or timeseries storage
        total = AgentRun.query.filter_by(agent_id=agent_id).count()
        completed = AgentRun.query.filter_by(agent_id=agent_id, status="completed").count()
        failed = AgentRun.query.filter_by(agent_id=agent_id, status="failed").count()
        avg_duration = db.session.execute(
            db.text("SELECT AVG(duration_ms) FROM agent_runs WHERE agent_id = :aid AND duration_ms IS NOT NULL"),
            {"aid": agent_id}
        ).scalar()
        return {
            "total_runs": total,
            "completed": completed,
            "failed": failed,
            "avg_duration_ms": int(avg_duration) if avg_duration is not None else None,
        }
