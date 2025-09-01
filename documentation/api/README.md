# API Documentation

## Base and Documentation
- Base path prefix: `/api` (set in `api/extensions.py`).
- Health (back-compat): `GET /system/health`.
- Swagger UI: `GET /api/docs`.
- ReDoc: `GET /redoc` (spec at `GET /api/swagger.json`).

## Namespaces (selection)
- `auth`, `agents`, `workflows`, `system`, `config`, `tools`, `knowledge`, `conversations`, `kg_admin`, `kg_consensus`, `integrations`, `substrate`, `autonomy`, `kg_drift`, `self_healing` (at `/api/self_healing`), `coordination` (at `/api/coordination`), `validation` (at `/api/validation`), `security` (at `/api/security`), and `documents`.

## Key Endpoints
- Ingestion: `POST /api/documents/enqueue`
  - Body:
    - `doc_id` (string, required)
    - `file_name` or `file_path` (one required)
    - `content_type` (`pdf`|`text`, default `pdf`)
    - `metadata` (object)
  - Returns 202 on success and enqueues to RabbitMQ.

## Environment Variables
- API: `HOST`, `PORT` (default 8000), `FLASK_ENV`, `SECRET_KEY`.
- RabbitMQ: `RABBITMQ_URL` (derived from `RABBITMQ_DEFAULT_USER`/`RABBITMQ_DEFAULT_PASS`).
- Databases: `DATABASE_URL` (Postgres), `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.
- Observability: `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`.

## Examples
```bash
curl -fsS http://localhost:8000/system/health | jq .

curl -fsS -X POST http://localhost:8000/api/documents/enqueue \
  -H 'Content-Type: application/json' \
  -d '{
        "doc_id":"doc-n8n-guide",
        "file_name":"The Ultimate n8n Guide.pdf",
        "content_type":"pdf",
        "metadata":{"source":"api"}
      }' | jq .
```
