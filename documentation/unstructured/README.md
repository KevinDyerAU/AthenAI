# Unstructured Worker Guide

This guide explains how documents are enqueued, processed, stored in Neo4j, and observed via Prometheus/Grafana.

## Flow overview
1. API receives `POST /api/documents/enqueue` with `{ doc_id, file_name | file_path, content_type, metadata }`.
2. API publishes a message to RabbitMQ queue `UNSTRUCTURED_QUEUE` (default `documents.process`).
3. Unstructured worker consumes the queue, reads the file, chunks content, writes `KnowledgeEntity` nodes and `HAS_PART` relationships to Neo4j.
4. Worker emits Prometheus metrics (processed counts, errors, durations).

## Message format
```json
{
  "doc_id": "doc-n8n-guide",
  "file_path": "/app/data/input/The Ultimate n8n Guide.pdf",
  "content_type": "pdf",
  "metadata": {"source": "api"}
}
```
- If only `file_name` is provided, the worker path is constructed as `/app/data/input/<file_name>`.

## Required environment
- `RABBITMQ_URL` — e.g., `amqp://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@rabbitmq:5672/`
- `UNSTRUCTURED_QUEUE` — default `documents.process`
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `OPENAI_API_KEY` (if embeddings are enabled)

See `documentation/configuration/ENVIRONMENT_CONFIG.md` for the full matrix.

## Metrics (Prometheus)
- `documents_processed_total{worker_id=..., status=...}`
- `processing_errors_total{worker_id=..., reason=...}`
- `document_processing_seconds_count` / `_sum` / `_bucket`

Prometheus UI (host): use the mapped port (default `${PROMETHEUS_PORT:-9090}`). On some local configs this is `9464`.

Examples:
```bash
# Total processed
curl -fsS "http://localhost:9464/api/v1/query?query=sum(documents_processed_total)"

# Error rate (5m)
curl -fsS "http://localhost:9464/api/v1/query?query=rate(processing_errors_total[5m])"
```

## Troubleshooting
- API returns "RabbitMQ unavailable or not configured": ensure user exists in RabbitMQ and `RABBITMQ_DEFAULT_PASS` in `.env` matches. Containers must be restarted to pick up env.
- No nodes in Neo4j: tail worker logs and verify it consumed a message; confirm file exists at `/app/data/input/..` inside the worker container.
- Prometheus empty results: ensure worker is running and metrics endpoint is scraped; verify host port mapping and targets config.
