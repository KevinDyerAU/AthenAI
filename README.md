# NeoV3 — API Modernization Quickstart

This repository contains the modernized API layer for NeoV3 with knowledge management, persistent conversations, n8n workflow triggers, RabbitMQ-based agent delegation, and real-time WebSocket communication.

## Features

- Knowledge REST endpoints with conflict resolution, provenance, and optional vector search (OpenAI + Neo4j vector index)
- Conversations API with persistent memory in Neo4j
- Agent and Workflow endpoints that trigger n8n webhooks for execution
- WebSocket rooms per conversation for real-time context-preserving messages and agent status
- Audit logging of knowledge operations and trigger events

## Prerequisites

- Python 3.10+
- PostgreSQL (for SQLAlchemy models) and/or configured DB via `DATABASE_URL`
- Neo4j 5.x (with APOC recommended)
- RabbitMQ (optional but recommended)
- n8n (self-hosted)

## Environment variables

Create a `.env` based on `.env.development.example` or `.env.production.example`.
Key variables:

- API server:
  - `HOST=0.0.0.0`
  - `PORT=8000`
  - `DATABASE_URL=postgresql+psycopg2://...`
  - `JWT_SECRET_KEY=...`
  - `CORS_ORIGINS=*`
- Neo4j:
  - `NEO4J_URI=bolt://localhost:7687`
  - `NEO4J_USER=neo4j`
  - `NEO4J_PASSWORD=...`
- RabbitMQ (optional):
  - `RABBITMQ_URL=amqp://guest:guest@localhost:5672/`
- n8n integration:
  - `N8N_BASE_URL=http://localhost:5678`
  - `N8N_API_KEY` (optional)
- Integrations security:
  - `INTEGRATION_SECRET=<shared-token>` (required to authorize inbound webhooks like `/integrations/n8n/runs`)
- Vector search (optional):
  - `ENABLE_VECTOR_SEARCH=true`
  - `OPENAI_API_KEY=...`
  - `OPENAI_EMBEDDING_MODEL=text-embedding-3-small` (dim=1536)
- Misc:
  - `API_BASE_URL=http://localhost:8000`
  - `AUDIT_LOG_PATH=./audit.log`
  - `TOOLS_REGISTRY_PATH=./workflows/templates/model_selector.js`

### Autonomy-specific variables

Add these to `.env` (see `.env.example` / `unified.env.example` for defaults):

- `AUTONOMY_ENABLED=true` — Enable agent lifecycle/drift monitors and endpoints
- `AUTONOMY_API_EXPOSE=true` — Expose `/api/autonomy/*` endpoints (if feature-gated in your deployment)
- `AUTONOMY_DEFAULT_MONITOR_INTERVAL=30` — Seconds between health/drift scans
- `AUTONOMY_SAFETY_MODE=conservative` — conservative|balanced|aggressive
- `DRIFT_SCAN_INTERVAL=300` — Drift detector scan period (seconds)
- `HEALING_POLICY=restart_then_roll_back` — Self-healing strategy

RabbitMQ connection (used by publishers/consumers):
- `RABBITMQ_URL=amqp://user:pass@host:5672/`

## Install dependencies

```bash
pip install -r api/requirements.txt
```

## Database initialization

Schemas are applied automatically during deploys.

- **Local deploy** (`deploy-local.ps1` / `deploy-local.sh`): after `postgres` and `neo4j` are healthy, runs:
  - `scripts/migrations/apply-postgres.ps1` or `.sh`
  - `scripts/migrations/apply-neo4j.ps1` or `.sh`
- **Cloud deploy** (`deploy-cloud.sh`): after upstream Render deploy completes, runs:
  - `scripts/migrations/cloud-apply-postgres.sh` (uses `DATABASE_URL` or `PG*` vars from `.env.cloud`)
  - `scripts/migrations/cloud-apply-neo4j.sh` (uses `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`)

Source schemas:

- PostgreSQL: `db/postgres/schema.sql`
- Neo4j: `db/neo4j/schema.cypher`

Manual (optional):

```bash
# Local containers
scripts/migrations/apply-postgres.sh
scripts/migrations/apply-neo4j.sh

# Managed cloud services
scripts/migrations/cloud-apply-postgres.sh
scripts/migrations/cloud-apply-neo4j.sh
```

## Create Neo4j indexes

Use cypher-shell or Neo4j Browser to run `scripts/neo4j/create_indexes.cypher`:

```bash
cypher-shell -u neo4j -p <password> -f scripts/neo4j/create_indexes.cypher
```

This creates:
- Full-text index `entityIndex` on `:Entity(id,name,description)`
- Vector index `entityEmbedding` on `:Entity(embedding)` with cosine/1536 dims

Note: Vector search is used in `/knowledge/search` when `ENABLE_VECTOR_SEARCH=true` and `OPENAI_API_KEY` is set. Ensure you persist embeddings to `n.embedding` where applicable.

## Run the API

From `api/` directory or repo root:

```bash
python -m api.app
```

This starts Flask-SocketIO (gevent) on `HOST`/`PORT`.

Health check: `GET /system/health` → `{ "status": "ok" }`

## OpenAPI / API Docs

- OpenAPI and Swagger UI are provided by Flask-RESTX.
- In a default dev run, open the interactive docs at:
  - Swagger UI: `/` (root) or `/doc` depending on RESTX config
  - OpenAPI JSON: `/swagger.json`
- All endpoints indicate security requirements (JWT where applicable), request/response models, and example payloads.

Key namespaces exposed in `api/app.py`:
- `auth`, `agents`, `workflows`, `system`, `config`, `tools`, `knowledge`, `conversations`, `kg_admin`, `kg_consensus`, `integrations`, `substrate`.

### Autonomous agent management

New namespace: `autonomy` (registered under `/api/autonomy`). Endpoints:

- `POST /api/autonomy/agents/{agent_id}/lifecycle`
  - Body:
    ```json
    { "state": "started", "reason": "manual", "metadata": {"source":"test"} }
    ```
  - Persists `Agent` and `LifecycleEvent` in Neo4j and publishes to RabbitMQ exchange `agents.lifecycle` with routing key `lifecycle.<state>`.

- `POST /api/autonomy/agents/{agent_id}/metrics`
  - Body:
    ```json
    { "cpu": 0.25, "mem": 512, "latency_ms": 120.5, "success_rate": 0.99, "throughput": 12 }
    ```
  - Persists `AgentMetrics` in Neo4j and publishes to exchange `agents.health` with routing key `health.metrics`.

- `POST /api/autonomy/agents/{agent_id}/drift`
  - Body:
    ```json
    { "signal": "embedding_shift", "severity": "medium", "details": {"window":"24h"} }
    ```
  - Persists `KnowledgeDriftAlert` in Neo4j and publishes to exchange `agents.drift` with routing key `drift.<signal>`.

Auth: These endpoints inherit the API's default security config. If JWT is enabled globally, include `Authorization: Bearer <token>`.

## Consciousness Substrate (Neo4j) — Usage

The enhanced substrate provides provenance, conflict handling, semantic search, and graph reasoning over knowledge entities.

Documentation: `documentation/database/CONSCIOUSNESS_SUBSTRATE.md`

Key endpoints (JWT required):

- Create entity
  ```bash
  curl -X POST "$API_BASE_URL/api/substrate/entity" \
    -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
    -d '{
      "content": "Initial knowledge content",
      "entity_type": "note",
      "created_by": "user-123",
      "metadata": {"source": "example"}
    }'
  ```

- Update entity with conflict strategy (`merge|latest_wins|first_wins|strict`)
  ```bash
  curl -X PATCH "$API_BASE_URL/api/substrate/entity/<entity_id>" \
    -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
    -d '{
      "updates": {"content": "Revised"},
      "updated_by": "user-123",
      "strategy": "merge"
    }'
  ```

- Semantic search (requires vector index on `KnowledgeEntity.embedding`)
  ```bash
  curl -X POST "$API_BASE_URL/api/substrate/search/semantic" \
    -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
    -d '{
      "embedding": [0,0, ... 1536 dims ...],
      "limit": 5,
      "threshold": 0.7
    }'
  ```

- Provenance
  ```bash
  curl -H "Authorization: Bearer $JWT" \
    "$API_BASE_URL/api/substrate/provenance/<entity_id>"
  ```

- Traverse related
  ```bash
  curl -X POST "$API_BASE_URL/api/substrate/traverse" \
    -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
    -d '{"start_id": "<entity_id>", "max_depth": 2}'
  ```

Programmatic access is available via `api/utils/consciousness_substrate.py`.

## WebSocket usage

- Endpoint: same origin as API (Socket.IO). Connect with optional JWT:

```js
// Browser (Socket.IO v4)
const token = "<JWT>"; // optional
const socket = io("/", { transports: ["websocket"], auth: { token } });
socket.on("connected", (p) => console.log("WS connected", p));
socket.on("message:new", (m) => console.log("message", m));

// Join a conversation room (requires JWT with access)
socket.emit("room:join", { conversation_id: "<cid>" });

// Send a message (persists to Neo4j and broadcasts to room)
socket.emit("message:send", { conversation_id: "<cid>", message: "Hello" });
```

- Events:
  - `connected` → { connection_id, user_id }
  - `room:joined` → { conversation_id }
  - `history` → { conversation_id, messages: [...] }
  - `message:new` → persisted message payload
  - `permission:updated` → { conversation_id, user_id, role }
  - `permission:revoked` → { conversation_id, user_id }
  - `agent:update` → forwarded from RabbitMQ for the conversation
  - `agent_run:update` → run status updates (rooms: `agent:{agent_id}` and `{execution_id}`)
  - `error` → { message }

## RabbitMQ routing (agent updates)

- Default queue: `agent_updates` (override with `AGENT_UPDATES_QUEUE`).
- Payload must include `conversation_id` for room routing.

Example payload:

```json
{
  "conversation_id": "<cid>",
  "event": "agent:update",
  "status": "running",
  "agent_id": "agent-123",
  "data": { "progress": 0.42 }
}
```

See example publishers:
- Python: `examples/integrations/python/rabbitmq_publish_agent_update.py`
- Node: `examples/integrations/node/rabbitmq_publish_agent_update.js`

### RabbitMQ exchanges/queues for autonomy

Exchanges (topic):
- `agents.lifecycle`
- `agents.health`
- `agents.drift`
- `dead-letter.exchange` (DLQ target)

Queues (durable) with bindings:
- `agents.lifecycle.events` ← `agents.lifecycle` with `lifecycle.*`
- `agents.health.metrics` ← `agents.health` with `health.*`
- `agents.drift.alerts` ← `agents.drift` with `drift.*`
- Dead letter queues: `agents.lifecycle.dlq`, `agents.health.dlq`, `agents.drift.dlq`

Policies configure DLX routing; see `infrastructure/rabbitmq/definitions.json`.

Publisher helper available in API: `api/utils/rabbitmq.py` → `publish_exchange(exchange, routing_key, message)`.

## n8n webhooks

Import these workflows in n8n (UI → Import from file):

- `workflows/webhooks/agent-execute-webhook.json` (path: `/webhook/agent-execute`)
- `workflows/webhooks/workflow-run-webhook.json` (path: `/webhook/workflow-run`)

The API triggers these from:
- `POST /agents/{id}/execute` in `api/resources/agents.py`
- `POST /workflows/{id}/run` in `api/resources/workflows.py`

Ensure `N8N_BASE_URL` (and optionally `N8N_API_KEY`) are set in the API environment.

### Inbound run update webhook (integrations)

The API also exposes a secured inbound webhook for run status updates from n8n (or other orchestrators):

- `POST /integrations/n8n/runs`
- Headers: `X-Integration-Token: <INTEGRATION_SECRET>`
- Body:

```json
{
  "execution_id": "run-12-1724612981",
  "status": "completed",
  "result": { "ok": true },
  "metrics": { "latency_ms": 842 }
}
```

This updates the corresponding `AgentRun` row and emits a WebSocket `agent_run:update` event.

Set `INTEGRATION_SECRET` in the API environment. Requests without a matching token are rejected.

## Enhanced AI workflows (n8n)

Enhanced AI orchestration workflows are provided under `workflows/enhanced/`. Import them via n8n UI → Import from file:

- `workflows/enhanced/master-orchestration-agent.json`
- `workflows/enhanced/agent-handlers.json`
- `workflows/enhanced/research-agent.json`
- `workflows/enhanced/creative-agent.json`
- `workflows/enhanced/analysis-agent.json`
- `workflows/enhanced/development-agent.json`
- `workflows/enhanced/communication-agent.json`
- `workflows/enhanced/planning-agent.json`
- `workflows/enhanced/execution-agent.json`
- `workflows/enhanced/quality-assurance-agent.json`

Credentials required in n8n (or via environment):
- OpenAI API (for AI Agent nodes)
- Neo4j (bolt URI, username, password)
- Postgres (task memory persistence)
- RabbitMQ (agent status events)

Ensure the API has `N8N_BASE_URL` and (optionally) `N8N_API_KEY` set. The master orchestration flow coordinates specialized agents and reports progress via RabbitMQ and WebSockets. A previous copy of any legacy workflows was backed up under `backup/<timestamp>/workflows_old/` during migration.

See the detailed import and validation guide: `documentation/workflows/Enhanced-Workflows-Guide.md`.

### Import enhanced workflows via API (PowerShell)

Set environment variables then import all enhanced workflows:

```powershell
$Env:N8N_BASE_URL = "http://localhost:5678"
$Env:N8N_API_KEY  = "<your-n8n-api-key>"
powershell -ExecutionPolicy Bypass -File scripts\enhanced\n8n-import-enhanced.ps1
# To update if already present:
# powershell -ExecutionPolicy Bypass -File scripts\enhanced\n8n-import-enhanced.ps1 -UpdateIfExists
```

### Validate credentials and node resolution

Verify that required credentials (OpenAI, Neo4j, Postgres, RabbitMQ) referenced in the enhanced workflows are available in n8n:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\enhanced\n8n-validate.ps1
```

The report lists RequiredTypes/MissingTypes and RequiredNamed/MissingNamed per workflow. Create any missing credentials in n8n and re-run until resolved.

### Run a basic master orchestration test

Discover the master webhook from JSON, activate the workflow, and trigger it with a sample payload:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\enhanced\n8n-run-master-orchestration.ps1 -Activate
```

If `WebhookBase` differs from `N8N_BASE_URL`, pass `-WebhookBase "https://your-public-n8n"`. Provide a custom payload with `-SamplePayloadPath path\to\payload.json`.

### Related files

- Scripts: `scripts/enhanced/n8n-import-enhanced.ps1`, `scripts/enhanced/n8n-validate.ps1`, `scripts/enhanced/n8n-run-master-orchestration.ps1`
- Workflows: `workflows/enhanced/*.json`
- Guide: `documentation/workflows/Enhanced-Workflows-Guide.md`

## Quick test

Use the included simple integration test (requires API running locally and default envs):

```bash
python tests/integration/api_flows_test.py
```

The test covers:
- `/system/health`
- Create/Login user
- Create Agent → `POST /agents/{id}/execute`
- Create Workflow → `POST /workflows/{id}/run`

### Basic WebSocket test

Run the basic WS integration test (connect + auth enforcement):

```bash
python -m pytest -q tests/ws/test_ws_basic.py
```

Requires API running locally with default `HOST/PORT` and no extra setup.

## Audit logging

Audit events are written as JSONL to `AUDIT_LOG_PATH` (default `./audit.log`). Logging failures never block runtime.

## Monitoring and Observability

The API exposes Prometheus metrics, ships logs to Loki with correlation IDs, and provides Grafana dashboards and Prometheus alert rules.

- **Metrics endpoint**: `GET /metrics` (no auth)
  - API request counters, status codes, and latency histograms
  - WebSocket connections and message counters
  - Database metrics for Postgres and Neo4j:
    - `database_operations_total{database_type,operation,status}`
    - `database_query_duration_seconds_{bucket,sum,count}{database_type}`
  - Agent workflows:
    - `agent_workflow_executions_total{workflow_name,agent_type,status}`
    - `agent_workflow_duration_seconds_{bucket,sum,count}`

- **Code instrumentation**
  - Flask app middleware and metric registry: `api/metrics.py`, `api/app.py`
  - WebSockets: `api/ws/events.py`
  - Postgres (SQLAlchemy) listeners: `api/db_metrics.py` initialized in `create_app()`
  - Neo4j client timings: `api/utils/neo4j_client.py`
  - Agent runs: queued in `api/resources/agents.py`; terminal completion metrics in `api/resources/integrations.py`

- **Grafana dashboards** (JSON provisioning)
  - System overview: `infrastructure/monitoring/dashboards/system_overview.json`
  - API operations: `infrastructure/monitoring/dashboards/api_operations.json`
  - DB performance: `infrastructure/monitoring/dashboards/db_performance.json`
  - Agent coordination: `infrastructure/monitoring/dashboards/agent_coordination.json`
  - Import via Grafana or mount into Grafana's dashboards folder.

- **Prometheus alert rules**
  - API observability: `infrastructure/monitoring/prometheus/rules/api-observability.yml`
  - DB observability: `infrastructure/monitoring/prometheus/rules/db-observability.yml`
  - Ensure Prometheus loads rules (e.g., `rule_files: ["rules/**/*.yml"]`).

- **Loki / Promtail correlation IDs**
  - Promtail config: `infrastructure/monitoring/loki/promtail-config.yml`
    - Parses JSON logs to extract `correlation_id`
    - Fallback regex for plain logs to capture `X-Correlation-ID`
  - Filter logs in Grafana Explore: `{job="docker", correlation_id="<value>"}`
  - The API propagates `X-Correlation-ID` per request so you can pivot logs ↔ metrics.

### Quick validation

1. Hit a few API endpoints, open `/metrics`, confirm counters/histograms move.
2. In Grafana, open the four dashboards and verify timeseries populate.
3. In Prometheus, check alerts page; optionally simulate load/errors to trigger warnings.
4. In Loki, find a request log, copy `correlation_id`, then filter by it to trace the request.

## Repository paths of interest

- API entry/registration: `api/app.py`
- Knowledge API: `api/resources/knowledge.py`
- Conversations API: `api/resources/conversations.py`
- Agents API: `api/resources/agents.py`
  - `POST /agents/{id}/execute` (returns `execution_id`)
  - `GET /agents/{id}/runs?status=&limit=&offset=`
  - `GET /agents/{id}/metrics`
- Workflows API: `api/resources/workflows.py`
- WebSocket events: `api/ws/events.py`
- n8n client: `api/utils/n8n_client.py`
- Embeddings helper: `api/utils/embeddings.py`
- Audit helper: `api/utils/audit.py`
- Neo4j helper: `api/utils/neo4j_client.py`
 - Integrations API: `api/resources/integrations.py` (inbound `POST /integrations/n8n/runs`)
 - Knowledge API additions:
   - `POST /knowledge/relations/update`
   - `POST /knowledge/relations/delete`
   - `GET /knowledge/provenance?entityId=...&predicate=...&direction=out|in|both&limit=...`
 - Conversations API additions:
   - `GET /conversations/{cid}/messages?limit=&offset=&role=&since=&until=`
   - `GET /conversations/{cid}/messages/search?q=&limit=`
   - `GET /conversations/{cid}/participants`
   - `POST /conversations/{cid}/participants` (accepts optional `role`)
   - `DELETE /conversations/{cid}/participants/{user_id}`
   - `GET /conversations/{cid}/permissions`
   - `POST /conversations/{cid}/permissions` (set role)
   - `DELETE /conversations/{cid}/permissions/{user_id}`

## KG Integrity Monitoring (Scheduler)

A lightweight scheduler script periodically checks the Knowledge Graph for drift signals and can send alerts:

- Script: `scripts/monitoring/kg_integrity_watch.py`
- Env vars:
  - `INTERVAL_SECONDS=60` (poll interval)
  - `ALERT_WEBHOOK_URL` (HTTP endpoint to receive alerts)
  - `ALERT_MIN_SEVERITY=warning` (info|warning|error)
  - `THRESH_ORPHANS=0` (max allowed orphan Entities)
  - `THRESH_CONTRADICTIONS=0` (max allowed contradictions)
  - `THRESH_MISSING=0` (max allowed missing required props per label)
  - Neo4j: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

Run locally:

```bash
python scripts/monitoring/kg_integrity_watch.py
```

To schedule:

- Linux/macOS (cron): `* * * * * /usr/bin/python3 /path/NeoV3/scripts/monitoring/kg_integrity_watch.py`
- Windows (Task Scheduler): Create a Basic Task pointing to `python.exe` with argument `scripts/monitoring/kg_integrity_watch.py` and configure env vars.

## Next steps

- Persist embeddings for new/updated entities to leverage vector search fully.
- Expand CI tests to cover knowledge and conversation flows and WebSocket room events.
- Harden WebSocket authentication.
- Extend n8n flows to execute real agent logic using payloads received.

## Open TODOs (Health, Monitoring, Dependencies)

- Add DB pool status and pg_stat metrics integration (SQLAlchemy pool, pg_stat_database) and expose via /metrics.
- Add Neo4j cluster/connection metrics and simple Cypher timing to /metrics.
- Implement RabbitMQ queue depth, consumer count, and message rates via management API or Prometheus RMQ exporter; wire scrape targets.
- Implement backup status probe for Postgres/Neo4j and expose last snapshot time and success flag in deep health.
- Add alerting rules for degraded API health and dependency_up==0 in Prometheus rules.
- Add automatic retry/backoff wrappers for dependency initialization in the API and graceful degradation paths.
- Extend deploy-cloud.sh to verify API /api/system/health and abort/rollback on degraded state.
- Add recovery scripts to restart unhealthy services and escalate after N failures; log recovery actions.
