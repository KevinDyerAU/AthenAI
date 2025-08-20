# Quality Assurance Agent Workflow

- __Purpose__: Automated testing, validation, compliance verification, performance benchmarking, and continuous quality improvement across all agent outputs and system operations.
- __Entry__: `POST /webhook/quality-assurance/run`
- __Tools__: Automated Testing, Compliance Checking

## Nodes
- __Webhook QA Input__: receives `{ artifacts, standards?, quality?, context? }`.
- __Normalize Input__: validates artifacts and sets defaults for `standards` and `quality.thresholds`.
- __Automated Testing__: `/webhook/qa/tools/automated-testing` generates and executes automated tests across artifact types; returns test results and metrics.
- __Compliance Checking__: `/webhook/qa/tools/compliance-checking` validates artifacts against provided standards/regulations.
- __AI Synthesize QA Report__: composes a strict-JSON quality report with coverage, pass rate, performance, defects, compliance, recommendations, and dashboards.
- __Respond__: returns `{ status, report, tests, metrics, compliance }`.

## Example Request
```json
{
  "artifacts": [
    {"id": "A1", "type": "code", "content": "function main(){ eval('2+2') }"},
    {"id": "A2", "type": "email", "content": "Hello", "metadata": {"unsubscribe": false}}
  ],
  "standards": ["CAN-SPAM", "OWASP"],
  "quality": {"thresholds": {"passRate": 0.95, "p95_latency_ms": 800}}
}
```

## Outputs
- __report__: strict JSON including `summary, coverage, pass_rate, failures, performance, defects, compliance, recommendations, continuous_improvement, dashboards, certification, next_steps`.
- __tests__: `{ results: [...], failures: [...] }`.
- __metrics__: `{ pass_rate, total, passed, failed, p50_latency_ms, p90_latency_ms, p95_latency_ms }`.
- __compliance__: `{ status, issues, summary }`.

## Notes
- Replace Function tool nodes with external QA systems (e.g., unit/integration test runners, performance tools, compliance scanners) using the same webhook contracts.
- Configure AI provider credentials in n8n for `n8n-nodes-base.aiAgent`.
