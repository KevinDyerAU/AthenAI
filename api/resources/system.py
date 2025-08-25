import os
import platform
import time
from datetime import datetime
from flask import Response
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ..extensions import db

try:
    from neo4j import GraphDatabase  # type: ignore
except Exception:  # pragma: no cover
    GraphDatabase = None  # type: ignore

try:
    import pika  # type: ignore
except Exception:  # pragma: no cover
    pika = None  # type: ignore

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

try:
    from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST  # type: ignore
except Exception:  # pragma: no cover
    Counter = Gauge = generate_latest = CONTENT_TYPE_LATEST = None  # type: ignore

ns = Namespace("system", description="System monitoring endpoints")

health_model = ns.model("Health", {
    "status": fields.String,
    "time": fields.Float,
    "timestamp": fields.String,
    "services": fields.Raw,
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

# Prometheus metrics (optional if lib available)
if Gauge is not None:
    API_UP = Gauge("api_up", "API up status (1=up)")
    DEP_SERVICE_UP = Gauge("dependency_up", "Dependency up status (1=up)", ["service"]) 
    HEALTH_CHECKS_TOTAL = Counter("health_checks_total", "Total health checks", ["result"])
else:  # no-op stubs
    API_UP = DEP_SERVICE_UP = HEALTH_CHECKS_TOTAL = None


@ns.route("/health")
class Health(Resource):
    @ns.marshal_with(health_model)
    def get(self):
        status = "healthy"
        services = {}

        # PostgreSQL via SQLAlchemy
        try:
            db.session.execute("SELECT 1")
            services["postgresql"] = {"status": "healthy"}
            if DEP_SERVICE_UP: DEP_SERVICE_UP.labels("postgresql").set(1)
        except Exception as e:  # pragma: no cover
            services["postgresql"] = {"status": "unhealthy", "error": str(e)}
            status = "degraded"
            if DEP_SERVICE_UP: DEP_SERVICE_UP.labels("postgresql").set(0)

        # Neo4j
        neo_uri = os.getenv("NEO4J_URI")
        neo_user = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME")
        neo_pass = os.getenv("NEO4J_PASSWORD")
        if neo_uri and GraphDatabase is not None:
            try:
                driver = GraphDatabase.driver(neo_uri, auth=(neo_user, neo_pass))
                with driver.session() as session:
                    session.run("RETURN 1 AS ok").single()
                driver.close()
                services["neo4j"] = {"status": "healthy"}
                if DEP_SERVICE_UP: DEP_SERVICE_UP.labels("neo4j").set(1)
            except Exception as e:  # pragma: no cover
                services["neo4j"] = {"status": "unhealthy", "error": str(e)}
                status = "degraded"
                if DEP_SERVICE_UP: DEP_SERVICE_UP.labels("neo4j").set(0)
        else:
            services["neo4j"] = {"status": "unknown", "reason": "not_configured_or_client_missing"}

        # RabbitMQ
        rabbit_url = os.getenv("RABBITMQ_URL")
        if rabbit_url and pika is not None:
            try:
                params = pika.URLParameters(rabbit_url)
                params.socket_timeout = 2
                conn = pika.BlockingConnection(params)
                conn.close()
                services["rabbitmq"] = {"status": "healthy"}
                if DEP_SERVICE_UP: DEP_SERVICE_UP.labels("rabbitmq").set(1)
            except Exception as e:  # pragma: no cover
                services["rabbitmq"] = {"status": "unhealthy", "error": str(e)}
                status = "degraded"
                if DEP_SERVICE_UP: DEP_SERVICE_UP.labels("rabbitmq").set(0)
        else:
            services["rabbitmq"] = {"status": "unknown", "reason": "not_configured_or_client_missing"}

        # AI Provider (OpenAI minimal)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and requests is not None:
            try:
                resp = requests.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {openai_key}"},
                    timeout=2,
                )
                if resp.status_code < 500:
                    services["ai_provider"] = {"status": "healthy"}
                else:
                    services["ai_provider"] = {"status": "unhealthy", "code": resp.status_code}
                    status = "degraded"
            except Exception as e:  # pragma: no cover
                services["ai_provider"] = {"status": "unhealthy", "error": str(e)}
                status = "degraded"
        else:
            services["ai_provider"] = {"status": "unknown", "reason": "not_configured_or_client_missing"}

        # Base service health
        if API_UP: API_UP.set(1)
        if HEALTH_CHECKS_TOTAL: HEALTH_CHECKS_TOTAL.labels(status).inc()

        return {
            "status": status,
            "time": time.time(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "services": services,
        }


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


@ns.route("/health/deep")
class DeepHealth(Resource):
    @jwt_required(optional=True)
    def get(self):
        # For now, reuse the basic health and extend with uptime and config presence
        base = Health().get()
        base["uptime_seconds"] = time.time() - _start_time
        base["config"] = {
            "has_database_url": bool(os.getenv("DATABASE_URL")),
            "has_neo4j": bool(os.getenv("NEO4J_URI")),
            "has_rabbitmq": bool(os.getenv("RABBITMQ_URL")),
            "has_ai_key": bool(os.getenv("OPENAI_API_KEY")),
        }
        return base


@ns.route("/logs")
class Logs(Resource):
    @jwt_required()
    def get(self):
        # Placeholder: integrate with central logging. For now return a static message.
        return {"message": "Logs endpoint not yet integrated with monitoring backend"}


@ns.route("/metrics")
class Metrics(Resource):
    @jwt_required(optional=True)
    def get(self):
        # Prefer Prometheus text format if library is available
        if generate_latest and CONTENT_TYPE_LATEST:
            data = generate_latest()  # type: ignore
            return Response(response=data, status=200, mimetype=CONTENT_TYPE_LATEST)  # type: ignore
        # Fallback minimal JSON metrics
        return {
            "uptime_seconds": time.time() - _start_time,
        }
