# Monitoring & Observability Quick Start

This guide documents how to run the monitoring stack and wire your services so AI metrics, alerts, dashboards, and tracing work end‑to‑end.

## Stack Overview

- Prometheus for metrics (`infrastructure/monitoring/prometheus/prometheus.yml`)
- Alertmanager for alert routing (`infrastructure/monitoring/alertmanager/alertmanager.yml`)
- Pushgateway for ephemeral/push metrics (agents/workflows)
- Grafana for dashboards (auto-provisioned)
- Jaeger for distributed tracing (via OpenTelemetry Collector)
- OpenTelemetry Collector (OTLP receiver -> Jaeger exporter)

Dashboards live in `infrastructure/monitoring/dashboards/`.
Alert rules live in `infrastructure/monitoring/alerts/`.
Custom metrics are defined in `infrastructure/monitoring/custom-metrics/ai_metrics.yaml`.

## Quick Start (Docker Compose)

1) Create the shared Docker network (one time):

```bash
docker network create agentnet
```

2) Launch the monitoring stack:

```bash
docker compose -f infrastructure/monitoring/docker-compose.monitoring.yml up -d
```

- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093
- Grafana: http://localhost:3000 (admin / admin)
- Pushgateway: http://localhost:9091
- Jaeger: http://localhost:16686
- OTLP endpoints (from OTel Collector):
  - HTTP: http://localhost:4318
  - gRPC: http://localhost:4317

3) Attach your main stack to the shared network.
In `enhanced-ai-agent-os/docker-compose.yml` the shared network `agentnet` is already declared and services are attached. If you add new services, join them to `agentnet`:

```yaml
services:
  your-service:
    # ...
    networks:
      - enhanced-ai-network
      - agentnet

networks:
  agentnet:
    external: true
    name: agentnet
```

## Emitting AI Metrics

Use Pushgateway for simple Docker-based deployments or the textfile exporter + node_exporter if you run on a host.

- Script: `scripts/monitoring/collect-ai-metrics.sh` (defaults PUSHGATEWAY to `http://pushgateway:9091` on the shared network)

Example:

```bash
scripts/monitoring/collect-ai-metrics.sh \
  --agent planning --endpoint /webhook/planning-agent \
  --latency 0.45 --tokens-prompt 300 --tokens-completion 120 \
  --cost-usd 0.01 --status success
```

Prometheus will ingest from Pushgateway. Grafana dashboards are pre-wired to show:
- Agents: `infrastructure/monitoring/dashboards/agents.json`
- Workflows: `infrastructure/monitoring/dashboards/workflows.json`
- Knowledge Graph: `infrastructure/monitoring/dashboards/knowledge_graph.json`
- Capacity: `infrastructure/monitoring/dashboards/capacity.json`

## Alerts

Prometheus loads alert rules from `infrastructure/monitoring/alerts/`. Alertmanager uses `infrastructure/monitoring/alertmanager/alertmanager.yml`.

- Update receivers (Slack/PagerDuty/email) in `alertmanager.yml` and point the top-level route to your desired receiver.

## Tracing

Send traces to the OTel Collector and view in Jaeger:
- OTLP HTTP: `http://otel-collector:4318/v1/traces`
- OTLP gRPC: `http://otel-collector:4317`
- Jaeger UI: `http://localhost:16686`

In `enhanced-ai-agent-os/docker-compose.yml`, `n8n` has defaults:
- `OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318`
- `OTEL_SERVICE_NAME=n8n`

Add similar env vars to other services to enable tracing.

## Knowledge Graph & Capacity Dashboards

- Knowledge Graph health: totals, growth, errors (`infrastructure/monitoring/dashboards/knowledge_graph.json`)
- Capacity planning: CPU/memory utilization, queue depth, projected capacity
  (`infrastructure/monitoring/dashboards/capacity.json`)

## Operational Analysis (CLI)

Use `scripts/monitoring/analyze-metrics.sh` for quick insights with PromQL via API:

```bash
PROMETHEUS_URL=http://localhost:9090 scripts/monitoring/analyze-metrics.sh
```

## Kubernetes (Optional)

We can provide a minimal k8s starter (Helm or YAML) for Prometheus/Grafana/Alertmanager/Jaeger/OTel Collector. Request if needed.

## Notes & Conventions

- Shared network: all services that need monitoring must join `agentnet`.
- Metrics naming aligns with `ai_metrics.yaml` for consistency and aggregation.
- Start small with alert thresholds; tune to reduce noise.
- Secure Grafana and Alertmanager credentials for non-local environments.
