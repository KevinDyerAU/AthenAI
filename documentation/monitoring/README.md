# Monitoring Guide

This guide explains how to observe, alert, and troubleshoot the NeoV3 platform.

## Components
- API metrics: expose via `/system/metrics` (placeholder) and logs via `/system/logs`.
- Prometheus: scrape API and exporters.
- Grafana: dashboards for API latency, error rates, DB health.
- Alertmanager: routing for alerts (pager/email).
- Tracing: OpenTelemetry to OTLP endpoint.

## Configuration
- ENABLE_PROMETHEUS=true
- PROMETHEUS_PORT=9090
- ENABLE_TRACING=true
- OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
- SENTRY_DSN=... (optional)

## Dashboards
- API Overview: requests/s, latency p50/p95/p99, error rate, 5xx, WebSocket connections.
- DB: pool usage, query time, errors.
- Queues: RabbitMQ rates, queue length, consumers.
- Neo4j: connection status, query time.

## Alerts (examples)
- High error rate (>5% for 5m)
- Elevated latency (p95 > 1s for 10m)
- DB connection saturation (>90% pool usage)
- Queue backlog growing (>1k messages)

## Logs
- Structure logs as JSON in production where possible.
- Correlate with trace IDs (include `trace_id` where available).

## Health Checks
- `/system/health`: liveness & readiness.
- `/system/status`: version, git sha, deps status.

## Troubleshooting
- Spikes in latency: inspect DB pool metrics and slow queries.
- Frequent 401/403: validate JWT config, clock drift, CORS.
- WebSocket disconnects: check proxy timeouts and Socket.IO transports.
