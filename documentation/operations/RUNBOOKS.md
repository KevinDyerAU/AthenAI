# Operational Runbooks

## Runbook: Deploy New API Version (Dev)
1. Build/push image (or let CI do it).
2. Update image in overlay or via CI.
3. `kubectl -n <ns> rollout status deploy/api-service`.
4. `bash scripts/deploy/validate.sh <ns> api-service 18080`.

## Runbook: Deploy New API Version (Prod)
1. Ensure `prod` environment approval configured.
2. Trigger workflow with environment=prod, api_tag=<tag>, push_image=true/false.
3. Wait for validation step.
4. If failure, evaluate; no auto-rollback.

## Runbook: Rollback (Prod)
1. Re-run workflow with environment=prod, approve_rollback=true.
2. Monitor `rollout status` to completion.

## Runbook: Scale Out/In
- Edit HPA in overlay or patch live.
- Verify via `kubectl -n <ns> get hpa` and load test.

## Runbook: Update Config
- Edit `configmap.yaml` and apply.
- `kubectl -n <ns> rollout restart deploy/api-service`.
- Validate.

## Runbook: Incident - API Errors Spiking
1. Check logs: `kubectl -n <ns> logs deploy/api-service --tail=200`.
2. Inspect events: `kubectl -n <ns> describe deploy api-service`.
3. Validate dependencies (DBs, MQ).
4. Evaluate quick rollback if recent deploy.
