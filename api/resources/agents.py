from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import Agent
from ..schemas import AgentSchema, AgentCreateSchema, AgentUpdateSchema

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
        # TODO: integrate with real execution engine / n8n
        agent = Agent.query.get_or_404(agent_id)
        agent.status = "running"
        db.session.commit()
        return {"message": "Execution started", "agent_id": agent.id}, 202


@ns.route("/<int:agent_id>/status")
class AgentStatus(Resource):
    @jwt_required()
    def get(self, agent_id: int):
        agent = Agent.query.get_or_404(agent_id)
        return {"id": agent.id, "status": agent.status}
