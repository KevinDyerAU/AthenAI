# Validation & Quality Assurance Framework

This document describes how to use the NeoV3 validation framework to run unit/integration tests, performance tests with k6, evaluate quality gates, persist results for history, and view live analytics.

## Components

- Validation Service: `api/services/validation.py`
- REST API: `api/resources/validation.py` (namespace `/api/validation`)
- WebSocket namespace: `/qa` (see `api/ws/events.py`)
- CI Gate Script: `scripts/testing/quality_gate.py`
- UI: `examples/ui/qa_analytics.html`

## Endpoints

- POST `/api/validation/run` (JWT)
  - Body (all optional):
    ```json
    {
      "unit_selectors": ["tests/unit"],
      "integration_scenarios": ["tests/api"],
      "load_profile": {
        "k6_script": "./tests/perf/sample.js",
        "vus": 10,
        "duration_s": 10,
        "rps": 50
      },
      "behavior_suites": ["pkg.module:function"],
      "include_performance": true,
      "include_behavior": true
    }
    ```
  - Emits Socket.IO events: `qa.validation.report` (default namespace and `/qa`).

- GET `/api/validation/report/last` (JWT)
  - Returns last validation report (if persistence enabled).

- GET `/api/validation/history?limit=20` (JWT)
  - Returns recent validation runs: `{ items: [{id, at, ok, passRate, errorRate, latencyP95}] }`.

- GET/POST `/api/validation/gates` (JWT)
  - `POST` body:
    ```json
    { "min_pass_rate": 0.95, "max_error_rate": 0.02, "max_p95_latency_ms": 200 }
    ```
  - Emits `qa.gates.updated` (default namespace and `/qa`).

## k6 Integration (precise metrics)

When `k6` is available and `load_profile.k6_script` is provided, the service runs:

```
k6 run --vus <vus> --duration <duration>s --summary-export <tmp>/k6-summary.json <script>
```

It parses `k6-summary.json` to extract:
- `latency_p95_ms` from `metrics.http_req_duration.percentiles["p(95)"]`
- `error_rate` from `metrics.http_req_failed.rate`
- `rps` from `metrics.http_reqs.rate` (or estimates from count/duration)

If `k6` is not present or no script, synthetic metrics are returned.

## Environment Variables

- `VALIDATION_PERSIST_DISABLED=true` to skip Neo4j writes and RabbitMQ publish (used in CI).
- `DISABLE_PERF=true` to skip performance tests.
- `K6_SCRIPT`, `K6_RPS`, `K6_DURATION`, `K6_VUS` can be used by the CI gate script.
- `BEHAVIOR_SUITES` comma-separated Python `module:function` entries.

## CI Quality Gate

Run locally or in CI:

```bash
python scripts/testing/quality_gate.py
```

Exit codes:
- `0` → gates passed
- `2` → gate violation (fail pipeline)

The script sets `VALIDATION_PERSIST_DISABLED=true` automatically for CI tolerance.

## WebSocket Namespace `/qa`

Connect with Socket.IO to receive QA events:

```js
const socket = io('/qa', { transports: ['websocket'], auth: { token: '<JWT-optional>' } });
socket.on('connected', (p) => console.log('QA WS connected', p));
socket.on('qa.validation.report', (report) => console.log(report));
socket.on('qa.gates.updated', (g) => console.log(g));
```

## QA Analytics UI

Open `examples/ui/qa_analytics.html` in a browser.
- Enter API base (e.g., `http://localhost:8000/api`) and JWT.
- Click "Connect WS" to join `/qa` namespace.
- Click "Run Validation" or "Refresh History" to fetch recent runs.
- View live KPIs and a pass-rate trend line.

## Persistence Schema (Neo4j)

- `(:ValidationRun {id, at, ok, passRate, errorRate, latencyP95})`
- `(:ValidationCheck {id, type, key, passed, metrics})-[:OF_RUN]->(:ValidationRun)`
- `(:QualityMetric {id, key, value, at})` for trend analysis

If `VALIDATION_PERSIST_DISABLED=true`, the service returns results without writing to Neo4j.
