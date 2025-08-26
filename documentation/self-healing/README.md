# Self-Healing and Adaptation

This document describes configuration, operations, and safety for the Self-Healing system implemented in `api/services/self_healing.py` and exposed via `api/resources/self_healing.py`.

## Capabilities

- Intelligent failure detection (adaptive baselines, z-score anomalies)
- Knowledge-based diagnosis and root-cause hypotheses
- Strategy library and adaptive selection based on historical success
- Automated recovery execution with verification and rollback stubs
- Time-series storage of metric snapshots and anomaly events (Neo4j)
- Predictive baselines (EWMA and simple Holt–Winters level/trend)
- Audit logs and RabbitMQ/Socket.IO events for observability

## Endpoints

- POST `/api/self_healing/analyze` — detect anomalies and compute diagnosis
- POST `/api/self_healing/heal` — select and execute healing strategy (dry-run by default)
- GET `/api/self_healing/strategies` — list available strategies
- GET `/api/self_healing/learning` — selection effectiveness stats

All endpoints require JWT. Socket.IO events:
- `self_healing:analyze`, `self_healing:heal`

## Configuration

Environment variables (optional):
- `CORS_ORIGINS` — Origins for Socket.IO/REST
- `LIFECYCLE_MANAGER_AUTOSTART` — Unrelated but part of app lifecycle

Code-level tuning in `SelfHealingService`:
- `self._ewma_alpha` — EWMA smoothing for baselines (default 0.3)
- `self._hw_alpha`, `self._hw_beta` — Holt–Winters level/trend factors
- `anomaly thresholds` — implicit via z-score >= 2 (medium), >= 3 (high)

Safety controls:
- Heal endpoint defaults to `dry_run=True`
- Docker operations guarded by SDK availability and context `containers` allowlist
- Verification hook: provide `context["verify"] = callable` returning bool
- Rollback stubs for scale and no-op/idempotent for other actions

## Operations

1) Analyze flow
- POST `/api/self_healing/analyze` with metrics and context
- System updates adaptive baselines and logs anomalies
- Emits events and records time-series snapshots/anomalies in Neo4j

2) Heal flow
- POST `/api/self_healing/heal` with diagnosis (from analyze) and context
- Strategy selected based on recommendation list and learned success rates
- Dry-run returns a plan; set `dry_run=false` to apply
- After execution: verification and conditional rollback
- Result and attempt recorded; learning updated

3) Context fields (examples)
- `services`: ["api", "worker"] — for impact assessment
- `queues`: ["events", "tasks"] — for backpressure
- `containers`: ["container_id_1", "container_id_2"] — for Docker actions
- `verify`: callable returning bool to validate success (e.g., probe health)

## Data Model (Neo4j)

- `(MetricSnapshot {id, at, metrics})`
- `(AnomalyEvent {id, at, metric, value, baseline, zscore, severity, hint})`
- `(HealingAttempt {id, at, strategy, dryRun, applied, verified, issueType, rootCause})`

IDs are Python UUIDs; no APOC dependency.

## Extending Diagnosis and Strategies

- Add a new predicate to `DiagnosisEngine.rules` with a corresponding outcome
- Add a new `HealingStrategy` in `StrategyLibrary` with `actions`
- Implement action side-effects in `RecoveryExecutor.execute`
- Provide a safe rollback mapping in `_rollback`

## Best Practices

- Keep heal operations `dry_run` unless confident in verification
- Provide a robust `verify` callable that checks real health signals
- Start with conservative strategies (restart/rebalance) before scaling
- Monitor `learning` endpoint to refine strategy effectiveness

## Examples

Analyze
```
POST /api/self_healing/analyze
{
  "metrics": {"error_rate": 0.08, "cpu_load": 0.92, "latency_p95": 450},
  "context": {"services": ["api"], "queues": ["events"]}
}
```

Heal (dry-run)
```
POST /api/self_healing/heal
{
  "issue": {"diagnosis": {"issue_type": "degradation", "root_cause": "elevated error rate", "confidence": 0.8,
    "impacted_components": ["api"], "recommended_strategies": ["restart_unhealthy", "scale_service"]}},
  "context": {"services": ["api"], "containers": ["abc123"]},
  "dry_run": true
}
```

Heal (apply with verification)
```
POST /api/self_healing/heal
{
  "issue": {"diagnosis": {"issue_type": "degradation", "root_cause": "elevated error rate", "confidence": 0.8,
    "impacted_components": ["api"], "recommended_strategies": ["restart_unhealthy", "scale_service"]}},
  "context": {"services": ["api"], "containers": ["abc123"], "verify": "server-side callable wired in"},
  "dry_run": false
}
```

