from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import Workflow
from ..schemas import WorkflowSchema, WorkflowCreateSchema, WorkflowUpdateSchema, WorkflowRunSchema

ns = Namespace("workflows", description="Workflow management endpoints")

workflow_model = ns.model("Workflow", {
    "id": fields.Integer,
    "name": fields.String,
    "definition": fields.Raw,
    "status": fields.String,
    "created_at": fields.DateTime,
    "updated_at": fields.DateTime,
})

workflow_list_model = ns.model("WorkflowList", {
    "items": fields.List(fields.Nested(workflow_model)),
    "total": fields.Integer,
})

workflow_schema = WorkflowSchema()
workflow_create_schema = WorkflowCreateSchema()
workflow_update_schema = WorkflowUpdateSchema()
workflow_run_schema = WorkflowRunSchema()


@ns.route("")
class WorkflowCollection(Resource):
    @jwt_required()
    @ns.marshal_with(workflow_list_model)
    def get(self):
        q = Workflow.query
        total = q.count()
        items = q.order_by(Workflow.created_at.desc()).all()
        return {"items": [workflow_schema.dump(w) for w in items], "total": total}

    @jwt_required()
    @ns.expect(ns.model("WorkflowCreate", {
        "name": fields.String(required=True),
        "definition": fields.Raw(required=True),
    }), validate=True)
    @ns.marshal_with(workflow_model, code=201)
    def post(self):
        payload = request.get_json() or {}
        data = workflow_create_schema.load(payload)
        if Workflow.query.filter_by(name=data["name"]).first():
            ns.abort(409, "Workflow name already exists")
        wf = Workflow(**data)
        db.session.add(wf)
        db.session.commit()
        return workflow_schema.dump(wf), 201


@ns.route("/<int:wf_id>")
class WorkflowItem(Resource):
    @jwt_required()
    @ns.marshal_with(workflow_model)
    def get(self, wf_id: int):
        wf = Workflow.query.get_or_404(wf_id)
        return workflow_schema.dump(wf)

    @jwt_required()
    @ns.expect(ns.model("WorkflowUpdate", {
        "name": fields.String,
        "definition": fields.Raw,
        "status": fields.String,
    }), validate=True)
    @ns.marshal_with(workflow_model)
    def put(self, wf_id: int):
        wf = Workflow.query.get_or_404(wf_id)
        payload = request.get_json() or {}
        data = workflow_update_schema.load(payload)
        for k, v in data.items():
            setattr(wf, k, v)
        db.session.commit()
        return workflow_schema.dump(wf)

    @jwt_required()
    def delete(self, wf_id: int):
        wf = Workflow.query.get_or_404(wf_id)
        db.session.delete(wf)
        db.session.commit()
        return {"message": "Deleted"}, 204


@ns.route("/<int:wf_id>/run")
class WorkflowRun(Resource):
    @jwt_required()
    def post(self, wf_id: int):
        # TODO: integrate with n8n to trigger workflow execution
        wf = Workflow.query.get_or_404(wf_id)
        wf.status = "queued"
        db.session.commit()
        return {"message": "Workflow queued", "workflow_id": wf.id}, 202


@ns.route("/batch/run")
class WorkflowBatchRun(Resource):
    @jwt_required()
    def post(self):
        payload = request.get_json() or {}
        ids = payload.get("ids", [])
        updated = []
        for wf_id in ids:
            wf = Workflow.query.get(wf_id)
            if wf:
                wf.status = "queued"
                updated.append(wf_id)
        if updated:
            db.session.commit()
        return {"message": "Workflows queued", "ids": updated}, 202
