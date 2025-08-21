import os
import platform
import time
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required

ns = Namespace("system", description="System monitoring endpoints")

health_model = ns.model("Health", {
    "status": fields.String,
    "time": fields.Float,
})

status_model = ns.model("Status", {
    "platform": fields.String,
    "python_version": fields.String,
    "pid": fields.Integer,
    "uptime_seconds": fields.Float,
})

metrics_model = ns.model("Metrics", {
    "requests_total": fields.Integer,
    "uptime_seconds": fields.Float,
})

_start_time = time.time()


@ns.route("/health")
class Health(Resource):
    @ns.marshal_with(health_model)
    def get(self):
        return {"status": "ok", "time": time.time()}


@ns.route("/status")
class Status(Resource):
    @jwt_required(optional=True)
    @ns.marshal_with(status_model)
    def get(self):
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "pid": os.getpid(),
            "uptime_seconds": time.time() - _start_time,
        }


@ns.route("/metrics")
class Metrics(Resource):
    @jwt_required(optional=True)
    @ns.marshal_with(metrics_model)
    def get(self):
        # Placeholder metrics; in CI you can replace with Prometheus client or your monitoring stack
        return {
            "requests_total": 0,
            "uptime_seconds": time.time() - _start_time,
        }


@ns.route("/logs")
class Logs(Resource):
    @jwt_required()
    def get(self):
        # Placeholder: integrate with central logging. For now return a static message.
        return {"message": "Logs endpoint not yet integrated with monitoring backend"}
