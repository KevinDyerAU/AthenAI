from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from ..utils.rabbitmq import publish_task

ns = Namespace("documents", description="Document ingestion endpoints (enqueue for Unstructured worker)")

enqueue_model = ns.model("DocumentEnqueue", {
    "doc_id": fields.String(required=True, description="Unique document id"),
    "file_name": fields.String(required=False, description="File name under data/unstructured/input, e.g. The Ultimate n8n Guide.pdf"),
    "file_path": fields.String(required=False, description="Absolute path as seen by worker, e.g. /app/data/input/file.pdf"),
    "content_type": fields.String(required=False, enum=["pdf", "text"], default="pdf"),
    "metadata": fields.Raw(required=False, description="Additional metadata to persist on the document node"),
})

response_model = ns.model("DocumentEnqueueResponse", {
    "enqueued": fields.Boolean,
    "queue": fields.String,
    "doc_id": fields.String,
    "file_path": fields.String,
})


@ns.route("/enqueue")
class DocumentEnqueue(Resource):
    @jwt_required(optional=True)
    @ns.expect(enqueue_model, validate=True)
    @ns.marshal_with(response_model, code=202)
    def post(self):
        payload = request.get_json() or {}
        doc_id = (payload.get("doc_id") or "").strip()
        file_name = (payload.get("file_name") or "").strip()
        file_path = (payload.get("file_path") or "").strip()
        content_type = (payload.get("content_type") or "pdf").strip()
        metadata = payload.get("metadata") or {}

        if not doc_id:
            ns.abort(400, "doc_id is required")
        if not file_path and not file_name:
            ns.abort(400, "Provide either file_path (container path) or file_name under data/unstructured/input")

        # If only file_name provided, construct the path as seen by the worker container
        if not file_path:
            # Worker mounts ./data/unstructured -> /app/data
            file_path = f"/app/data/input/{file_name}"

        queue = os.getenv("UNSTRUCTURED_QUEUE", "documents.process")
        message = {
            "doc_id": doc_id,
            "file_path": file_path,
            "content_type": content_type,
            "metadata": metadata,
        }
        ok = publish_task(message, routing_key=queue)
        if not ok:
            ns.abort(503, "RabbitMQ unavailable or not configured")

        # Identify user if present
        user = get_jwt_identity()
        _ = user  # reserved for audit in future

        return {"enqueued": True, "queue": queue, "doc_id": doc_id, "file_path": file_path}, 202
