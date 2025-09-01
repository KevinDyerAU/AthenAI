# Configuration Overview

This directory explains how to configure NeoV3 locally and in other environments. For the full, exhaustive list of variables and defaults, see `documentation/configuration/ENVIRONMENT_CONFIG.md`.

## Key environment variables (summary)

Refer to `.env.example` and `unified.env.example` in repo root. These are consumed by `docker-compose.yml` and the API.

- API
  - HOST, PORT (default 8000)
  - FLASK_ENV, SECRET_KEY
- RabbitMQ
  - RABBITMQ_DEFAULT_USER (default ai_agent_queue_user)
  - RABBITMQ_DEFAULT_PASS (set this in your `.env`)
  - RABBITMQ_URL (derived): `amqp://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@rabbitmq:5672/`
- Neo4j
  - NEO4J_URI (default `bolt://neo4j:7687`)
  - NEO4J_USER, NEO4J_PASSWORD
- Postgres
  - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
  - DATABASE_URL for API (psql URL)
- Observability
  - Grafana, Prometheus, Alertmanager: ports are mapped in `docker-compose*.yml`
  - OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME (for services emitting traces/metrics)
- Unstructured Worker
  - UNSTRUCTURED_QUEUE (default `documents.process`)
  - OPENAI_API_KEY, OPENAI_API_BASE (if embeddings required)

See `ENVIRONMENT_CONFIG.md` for all supported variables.

## API base paths and docs

- RESTX prefix is `/api` (defined in `api/extensions.py` via `prefix="/api"`).
- Health (back-compat): `GET /system/health` (defined in `api/app.py`).
- Swagger UI: `GET /api/docs`
- ReDoc: `GET /redoc` (spec at `GET /api/swagger.json`).

## Document ingestion endpoint

- Path: `POST /api/documents/enqueue`
- JSON body:
  - `doc_id` (string, required)
  - `file_name` or `file_path` (one required)
  - `content_type` (`pdf`|`text`, default `pdf`)
  - `metadata` (object)
- Queue used: `UNSTRUCTURED_QUEUE` (default `documents.process`).

## Quick start

- Create `.env` from `.env.example` and set secrets.
- Start: `./deploy-local.sh --fresh` (or PowerShell equivalents).
- Open local portal: `index.html` in repo root.
