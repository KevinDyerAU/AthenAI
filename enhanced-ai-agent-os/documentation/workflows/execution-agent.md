# Execution Agent Workflow

- __Purpose__: Task execution, workflow management, parallel orchestration, progress tracking, quality assurance, and operations coordination.
- __Entry__: `POST /webhook/execution/run`
- __Tools__: Parallel Processing, Error Recovery

## Nodes
- __Webhook Execution Input__: receives `{ tasks, policy?, monitoring?, metadata? }`.
- __Normalize Input__: validates input and sets defaults for `policy` and `monitoring`.
- __Parallel Processing Plan__: `/webhook/execution/tools/parallel-processing` creates topological batches limited by `policy.parallelism`.
- __Error Recovery Policy__: `/webhook/execution/tools/error-recovery` builds retry/backoff/circuit-breaker/dead-letter policies.
- __Init Progress Tracking__: computes initial counters for `progress`.
- __AI Synthesize Execution Plan__: generates strict-JSON orchestration, quality gates, monitoring, and escalation.
- __Respond__: returns `{ status, plan, parallel, recovery, progress }`.

## Example Request
```json
{
  "tasks": [
    {"id": "E1", "title": "Fetch Data", "deps": []},
    {"id": "E2", "title": "Transform", "deps": ["E1"]},
    {"id": "E3", "title": "Validate", "deps": ["E2"], "qualityGate": {"type": "schema"}},
    {"id": "E4", "title": "Publish", "deps": ["E3"]}
  ],
  "policy": {"parallelism": 3, "maxRetries": 3, "backoff": "exponential"},
  "monitoring": {"enabled": true}
}
```

## Outputs
- __plan__: strict JSON including `orchestration, error_policies, progress_model, quality_gates, monitoring, escalation, runbook, risks, next_steps`.
- __parallel__: `{ batches, parallelism }`.
- __recovery__: retry/backoff/circuit-breaker policy object.
- __progress__: counters `{ total, completed, failed, in_progress }`.

## Notes
- Replace Function tool nodes with real executors (queue/workers), monitoring (Prometheus/Grafana), and alerting (PagerDuty) via the same webhooks.
- Configure AI provider credentials in n8n for `n8n-nodes-base.aiAgent`.
