# API Reference by Namespace

Base prefix: `/api` (see `api/extensions.py`). Some namespaces are mounted at explicit paths (e.g., `/api/self_healing`). Many routes require JWT; some allow optional.

Tip: Open Swagger UI at `/api/docs` and ReDoc at `/redoc`.

## documents
- POST `/api/documents/enqueue`
  - Body: `{ doc_id, file_name | file_path, content_type = pdf|text, metadata }`
  - 202 Accepted, enqueues to `UNSTRUCTURED_QUEUE` (default `documents.process`).
  - Auth: optional.
  - Example:
```bash
curl -fsS -X POST http://localhost:8000/api/documents/enqueue \
  -H 'Content-Type: application/json' \
  -d '{"doc_id":"doc-n8n-guide","file_name":"The Ultimate n8n Guide.pdf","content_type":"pdf","metadata":{"source":"api"}}'
```
  - Request schema (from `api/resources/documents.py`):
    - `doc_id: string (required)`
    - `file_name: string` (under `data/unstructured/input`)
    - `file_path: string` (absolute worker path)
    - `content_type: enum[pdf,text]` (default `pdf`)
    - `metadata: object`
  - Response schema:
    - `{ enqueued: bool, queue: string, doc_id: string, file_path: string }`

## system
- GET `/api/system/health` — Basic health (no auth)
- GET `/api/system/status` — Status snapshot (auth optional)
- GET `/api/system/health/deep` — Expanded health (auth optional)
- GET `/api/system/logs` — Placeholder logs endpoint (auth required)
- GET `/api/system/metrics` — Exposes app metrics (auth optional)
  - Models (from `api/resources/system.py`):
    - Health: `{ status: string, time: number, timestamp: string, services: object }`
    - Status: `{ platform: string, python_version: string, pid: int, uptime_seconds: number }`

## validation (mounted at `/api/validation`)
- POST `/api/validation/run`
- GET `/api/validation/report/last`
- GET `/api/validation/history?limit=`
- GET `/api/validation/gates`
- Auth: required.
  - Request model (run):
    - `{ unit_selectors?: string[], integration_scenarios?: string[], load_profile?: any, behavior_suites?: string[], include_performance?: bool, include_behavior?: bool }`
  - Quality gates model: `{ min_pass_rate?: float, max_error_rate?: float, max_p95_latency_ms?: float|null }`

## tools
- GET `/api/tools/registry` — Returns tools registry JSON. No auth required.

## knowledge
- POST `/api/knowledge/query` — Body contains read-only Cypher `cypher`.
- POST `/api/knowledge/insert` — Insert facts (see model in code).
- Auth: required.
  - Models:
    - Query: `{ cypher: string (required), params?: object }`
    - Insert: `{ facts: object[] (required), conflict_policy?: string (default: prefer_latest) }`
    - Search: `{ query: string (required), limit?: int }`

  - Item endpoints:
    - GET `/api/knowledge/relations/{rid}` — Fetch a single relation by composite id.
      - Path param `rid`: `subject_id|predicate|object_id` (URL-safe, pipe-separated)
      - 200 OK: `{ relation: object }`
      - 404 Not Found
    - DELETE `/api/knowledge/relations/{rid}` — Deactivate a relation (soft delete with provenance).
      - 200 OK: `{ message: "Relation deactivated" }`
      - 404 Not Found

  - Example:
```bash
curl -fsS \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/knowledge/relations/ent-123%7CRELATED_TO%7Cent-456
```

## self_healing (mounted at `/api/self_healing`)
- POST `/api/self_healing/analyze`
- POST `/api/self_healing/heal`
- GET `/api/self_healing/strategies`
- GET `/api/self_healing/learning`
- GET `/api/self_healing/metrics/trend?metric=&window=`
- GET `/api/self_healing/metrics/forecast?metric=&window=`
- Auth: required.
  - Models (from `api/resources/self_healing.py`):
    - Analyze: `{ metrics: object (required), context?: object }`
    - Heal: `{ issue?: object, context?: object, strategy?: string, dry_run?: bool=true }`

## security (mounted at `/api/security`)
- GET `/api/security/compliance/assess`
- GET `/api/security/incidents`
- POST `/api/security/incidents`
- GET `/api/security/incidents/{incident_id}` — Fetch single incident
- GET `/api/security/sandbox/policy`
- POST `/api/security/sandbox/evaluate`
- Auth: required; permission `security:read` enforced.
  - Models (from `api/resources/security.py`):
    - ComplianceReport: `{ ok: bool, at: int, checks: object }`
    - SecurityIncident: `{ id: string, kind: string, severity: string, message: string, context: object, at: int }`
    - IncidentCreate: `{ kind: string!, severity: string! (info|low|medium|high|critical), message: string!, context?: object }`
    - SandboxPolicy: `{ cpu_quota: float, memory_mb: int, network: string, filesystem: string, dynamic: bool }`
    - SandboxEvaluate: `{ risk_score: float! }`

  - Item endpoint details:
    - GET `/api/security/incidents/{incident_id}`
      - 200 OK: `SecurityIncident`
      - 404 Not Found

## workflows
- GET `/api/workflows` — List
- POST `/api/workflows` — Create
- GET `/api/workflows/{wf_id}` — Read
- PUT `/api/workflows/{wf_id}` — Update
- DELETE `/api/workflows/{wf_id}` — Delete
- POST `/api/workflows/{wf_id}/run` — Enqueue run
- POST `/api/workflows/batch/run` — Batch enqueue
- Auth: required.
  - Models (from `api/resources/workflows.py`):
    - Workflow: `{ id: int, name: string, definition: any, status: string, created_at: datetime, updated_at: datetime }`
    - List: `{ items: Workflow[], total: int }`
    - Create: `{ name: string!, definition: any! }`
    - Update: `{ name?: string, definition?: any, status?: string }`

## substrate
- POST `/api/substrate/entity` — Create entity
- PUT `/api/substrate/entity/{entity_id}` — Update entity
- POST `/api/substrate/search/semantic` — Semantic search
- GET `/api/substrate/provenance/{entity_id}` — Provenance
- POST `/api/substrate/traverse` — Traverse
- POST `/api/substrate/graph/centrality` — Centrality
- POST `/api/substrate/graph/communities` — Communities
- GET `/api/substrate/temporal/{entity_id}` — Temporal view
- Auth: required.
  - Models (from `api/resources/substrate.py`):
    - CreateEntity: `{ content: string!, entity_type: string!, created_by: string!, embedding?: float[], metadata?: object }`
    - UpdateEntity: `{ updates: object!, updated_by: string!, strategy?: string=merge }`
    - SemanticSearch: `{ embedding: float[]!, limit?: int=10, threshold?: float=0.7 }`
    - Traverse: `{ start_id: string!, max_depth?: int=2, rel_types?: string[], limit?: int=50 }`
    - Centrality: `{ top_n?: int=20, relationship?: string=SIMILAR_TO }`
    - Communities: `{ write_property?: string=communityId }`

## auth
- POST `/api/auth/register` — Create account
- POST `/api/auth/login` — Obtain access/refresh tokens
- POST `/api/auth/refresh` — Exchange refresh for new tokens
- GET `/api/auth/me` — Current user
- POST `/api/auth/logout` — Revoke current token
  - Models (from `api/resources/auth.py`):
    - Register: `{ email: string!, password: string!, role?: string }`
    - Login: `{ email: string!, password: string! }`
    - Tokens: `{ access_token: string, refresh_token: string }`
    - UserPublic: `{ id: int, email: string, role: string, is_active: bool, created_at: datetime }`
  - Curl examples:
```bash
# Login
curl -fsS -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"secret"}'

# Refresh
curl -fsS -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN"
```

## Notes
- Back-compat health endpoint without prefix: `GET /system/health`.
- OpenAPI: `GET /api/swagger.json`.
- WebSocket is exposed (see `api/extensions.py`), typically on port 5001 if mapped.
