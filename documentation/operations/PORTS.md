# Ports and URLs Matrix (Local)

This table maps container services to internal/external ports and example URLs. Values resolve from `docker-compose.yml` and `.env`.

| Service | Container | Internal | Host (default) | Env Var | Example URL |
|---|---|---:|---:|---|---|
| API | enhanced-ai-agent-api | 5000, 5001 | 5000, 5001 | (none) | http://localhost:5000/api/docs |
| Postgres | enhanced-ai-postgres | 5432 | ${POSTGRES_PORT:-5432} | POSTGRES_PORT | psql: postgres:5432 |
| Neo4j HTTP | enhanced-ai-neo4j | 7474 | ${NEO4J_HTTP_PORT:-7474} | NEO4J_HTTP_PORT | http://localhost:7474 |
| Neo4j Bolt | enhanced-ai-neo4j | 7687 | ${NEO4J_BOLT_PORT:-7687} | NEO4J_BOLT_PORT | bolt://localhost:7687 |
| RabbitMQ AMQP | enhanced-ai-rabbitmq | 5672 | ${RABBITMQ_PORT:-5672} | RABBITMQ_PORT | amqp://localhost:5672 |
| RabbitMQ Mgmt | enhanced-ai-rabbitmq | 15672 | ${RABBITMQ_MANAGEMENT_PORT:-15672} | RABBITMQ_MANAGEMENT_PORT | http://localhost:15672 |
| RabbitMQ Metrics | enhanced-ai-rabbitmq | 15692 | ${RABBITMQ_METRICS_PORT:-15692} | RABBITMQ_METRICS_PORT | http://localhost:15692/metrics |
| n8n | enhanced-ai-n8n | 5678 | ${N8N_PORT:-5678} | N8N_PORT | http://localhost:5678 |
| Prometheus | enhanced-ai-prometheus | 9090 | ${PROMETHEUS_PORT:-9090} | PROMETHEUS_PORT | http://localhost:9090 |
| Grafana | enhanced-ai-grafana | 3000 | ${GRAFANA_PORT:-3000} | GRAFANA_PORT | http://localhost:3000 |
| Loki | enhanced-ai-loki | 3100 | ${LOKI_PORT:-3100} | LOKI_PORT | http://localhost:3100 |
| Alertmanager | enhanced-ai-alertmanager | 9093 | ${ALERTMANAGER_PORT:-9093} | ALERTMANAGER_PORT | http://localhost:9093 |
| Node Exporter | enhanced-ai-node-exporter | 9100 | ${NODE_EXPORTER_PORT:-9100} | NODE_EXPORTER_PORT | http://localhost:9100/metrics |
| Nginx (proxy) | enhanced-ai-nginx | 80, 443 | ${EXTERNAL_PORT:-80}, 443 | EXTERNAL_PORT | http://localhost:80 |
| OTEL Collector | enhanced-ai-otel-collector | 4317, 4318, 8888 | 4317, 4318, 8888 | (none) | http://localhost:8888/metrics |

Notes:
- If your `PROMETHEUS_PORT` is set to 9464 in `.env`, query Prometheus on `http://localhost:9464`.
- The API exposes Swagger UI at `/api/docs` and ReDoc at `/redoc` on the API port.
- Some endpoints (health) also exist at the root (e.g., `/system/health`).
