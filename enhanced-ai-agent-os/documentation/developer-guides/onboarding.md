# Developer Onboarding Guide

Welcome to Enhanced AI Agent OS development. This guide covers setup, running services, and contributing.

## Prerequisites
- Git, Docker (recommended), Bash, jq, curl
- Optional: k6, ApacheBench, Node.js, Python 3

## Setup
1. Copy env: `cp .env.example .env` (or use `enhanced-ai-agent-os/scripts/setup/configure-environment.sh`).
2. Start services (Docker or local as per your stack). Ensure n8n is reachable at `http://localhost:5678`.
3. Validate env: `enhanced-ai-agent-os/scripts/validate-environment.sh --env-file .env`.

## Running Tests
- All tests: `enhanced-ai-agent-os/scripts/testing/run-all-tests.sh --category all`
- API spec & smoke: `tests/api/run-api-tests.sh --all`

## API and Webhooks
- OpenAPI: `api/openapi.yaml`
- Docs: `enhanced-ai-agent-os/documentation/api/README.md`
- Examples: `examples/integrations/`

## Auth
- Use `X-N8N-API-KEY` header or Basic Auth. Prefer HTTPS in non-local environments.

## Rate Limiting
- Configure in ingress/gateway (e.g., NGINX rate limit, API Gateway). See `documentation/api/README.md`.

## Monitoring & Observability
- Read: `enhanced-ai-agent-os/documentation/monitoring/README.md` for the full quick start.
- Bring up the monitoring stack:
  - Create shared network once: `docker network create agentnet`
  - Start stack: `docker compose -f infrastructure/monitoring/docker-compose.monitoring.yml up -d`
- Ensure app services join `agentnet` (already patched in `enhanced-ai-agent-os/docker-compose.yml`).
- Emit AI metrics (agents/workflows) via Pushgateway:
  ```bash
  scripts/monitoring/collect-ai-metrics.sh \
    --agent planning --endpoint /webhook/planning-agent \
    --latency 0.45 --tokens-prompt 300 --tokens-completion 120 \
    --cost-usd 0.01 --status success
  ```
- Prometheus UI: `http://localhost:9090`
- Grafana UI: `http://localhost:3000` (admin/admin). Dashboards auto-load from `infrastructure/monitoring/dashboards/`.
- Alerts: edit `infrastructure/monitoring/alertmanager/alertmanager.yml` to add real receivers.
- Tracing: send OTLP to `http://otel-collector:4318` (HTTP) or `:4317` (gRPC). Jaeger UI `http://localhost:16686`.

## Contributing
- Follow shell best practices (`set -euo pipefail`).
- Add tests for new endpoints/workflows.
- Update OpenAPI and examples when changing contracts.
