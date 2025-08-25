from __future__ import annotations

import time
import uuid
from typing import Optional

from flask import Response, g, request
from flask_jwt_extended import get_jwt_identity
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# Dedicated registry for API metrics (can be scraped via /metrics)
api_registry = CollectorRegistry()

# API request metrics
api_requests_total = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status_code", "user_type"],
    registry=api_registry,
)
api_request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=api_registry,
)

# Knowledge management metrics
knowledge_operations_total = Counter(
    "knowledge_operations_total",
    "Total number of knowledge management operations",
    ["operation_type", "entity_type", "status"],
    registry=api_registry,
)
knowledge_search_duration = Histogram(
    "knowledge_search_duration_seconds",
    "Knowledge search operation duration",
    ["search_type"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0],
    registry=api_registry,
)

# WebSocket metrics
websocket_connections_active = Gauge(
    "websocket_connections_active",
    "Number of active WebSocket connections",
    registry=api_registry,
)
websocket_messages_total = Counter(
    "websocket_messages_total",
    "Total number of WebSocket messages",
    ["message_type", "direction"],
    registry=api_registry,
)

# Database operation metrics
database_operations_total = Counter(
    "database_operations_total",
    "Total number of database operations",
    ["database_type", "operation", "status"],
    registry=api_registry,
)
database_query_duration = Histogram(
    "database_query_duration_seconds",
    "Database query duration in seconds",
    ["database_type", "operation"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0],
    registry=api_registry,
)

# Agent workflow metrics
agent_workflow_executions_total = Counter(
    "agent_workflow_executions_total",
    "Total number of agent workflow executions",
    ["workflow_name", "agent_type", "status"],
    registry=api_registry,
)
agent_workflow_duration = Histogram(
    "agent_workflow_duration_seconds",
    "Agent workflow execution duration",
    ["workflow_name", "agent_type"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0],
    registry=api_registry,
)

# Consciousness substrate metrics
consciousness_operations_total = Counter(
    "consciousness_operations_total",
    "Total consciousness substrate operations",
    ["operation_type", "status"],
    registry=api_registry,
)
consciousness_query_duration = Histogram(
    "consciousness_query_duration_seconds",
    "Consciousness substrate query duration",
    ["query_type"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
    registry=api_registry,
)


# ---------------- Public helpers to record metrics ----------------

def record_knowledge_operation(operation_type: str, entity_type: str, duration_sec: float, success: bool = True) -> None:
    status = "success" if success else "error"
    knowledge_operations_total.labels(operation_type=operation_type, entity_type=entity_type, status=status).inc()
    if operation_type == "search":
        knowledge_search_duration.labels(search_type=entity_type).observe(max(0.0, float(duration_sec)))


def record_database_operation(db_type: str, operation: str, duration_sec: float, success: bool = True) -> None:
    status = "success" if success else "error"
    database_operations_total.labels(database_type=db_type, operation=operation, status=status).inc()
    database_query_duration.labels(database_type=db_type, operation=operation).observe(max(0.0, float(duration_sec)))


ess_connections = 0

def record_websocket_connection(connected: bool) -> None:
    global ess_connections
    ess_connections += 1 if connected else -1
    if ess_connections < 0:
        ess_connections = 0
    websocket_connections_active.set(ess_connections)


def record_websocket_message(message_type: str, direction: str) -> None:
    websocket_messages_total.labels(message_type=message_type, direction=direction).inc()


def record_agent_workflow(workflow_name: str, agent_type: str, duration_sec: float, success: bool = True) -> None:
    status = "success" if success else "error"
    agent_workflow_executions_total.labels(workflow_name=workflow_name, agent_type=agent_type, status=status).inc()
    agent_workflow_duration.labels(workflow_name=workflow_name, agent_type=agent_type).observe(max(0.0, float(duration_sec)))


def record_consciousness_operation(operation_type: str, duration_sec: float, success: bool = True) -> None:
    status = "success" if success else "error"
    consciousness_operations_total.labels(operation_type=operation_type, status=status).inc()
    consciousness_query_duration.labels(query_type=operation_type).observe(max(0.0, float(duration_sec)))


# ---------------- Flask integration ----------------

def _user_type() -> str:
    try:
        return "authenticated" if get_jwt_identity() else "anonymous"
    except Exception:
        return "anonymous"


def init_metrics(app):
    @app.before_request
    def _start_timer():
        g._metrics_start = time.time()
        # Set correlation id if not present
        if not getattr(g, "correlation_id", None):
            g.correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

    @app.after_request
    def _record_metrics(response):
        try:
            start = getattr(g, "_metrics_start", None)
            if start is not None:
                duration = time.time() - start
                method = request.method
                endpoint = request.endpoint or request.path or "unknown"
                status_code = response.status_code
                api_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code, user_type=_user_type()).inc()
                api_request_duration.labels(method=method, endpoint=endpoint).observe(max(0.0, float(duration)))
        finally:
            # Always propagate correlation id to responses
            if getattr(g, "correlation_id", None):
                response.headers["X-Correlation-ID"] = g.correlation_id
            return response

    @app.route("/metrics")
    def metrics_endpoint():
        data = generate_latest(api_registry)
        return Response(data, mimetype=CONTENT_TYPE_LATEST)
