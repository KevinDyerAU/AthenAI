#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${1:-neov3}
APP_LABEL=${2:-api-service}
LOCAL_PORT=${3:-18080}

# Check namespace exists
kubectl get ns "$NAMESPACE" >/dev/null

# Check deployment available
DEPLOY=$(kubectl -n "$NAMESPACE" get deploy -l app=$APP_LABEL -o jsonpath='{.items[0].metadata.name}')
if [[ -z "$DEPLOY" ]]; then
  echo "Deployment with label app=$APP_LABEL not found in $NAMESPACE" >&2
  exit 2
fi

# Check pods ready
kubectl -n "$NAMESPACE" get deploy "$DEPLOY" -o json | jq -e '.status.availableReplicas >= 1' >/dev/null || {
  echo "Deployment $DEPLOY has no available replicas" >&2
  exit 3
}

# Check service exists
kubectl -n "$NAMESPACE" get svc "$APP_LABEL" >/dev/null || {
  echo "Service $APP_LABEL not found in $NAMESPACE" >&2
  exit 4
}

# Check HPA exists
kubectl -n "$NAMESPACE" get hpa "$APP_LABEL" >/dev/null || echo "Warning: HPA $APP_LABEL not found (non-fatal)"

echo "Starting port-forward to Service/$APP_LABEL on localhost:$LOCAL_PORT ..."
PF_PID=""
set +e
kubectl -n "$NAMESPACE" port-forward svc/"$APP_LABEL" "$LOCAL_PORT":80 >/dev/null 2>&1 &
PF_PID=$!
set -e

cleanup() {
  if [[ -n "$PF_PID" ]]; then
    kill "$PF_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

# Wait for port-forward
for i in {1..20}; do
  if curl -fsS "http://127.0.0.1:$LOCAL_PORT/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

echo "HTTP health check: /health"
curl -fsS "http://127.0.0.1:$LOCAL_PORT/health" | sed -e 's/.*/Health OK/' || {
  echo "Health check failed" >&2
  exit 5
}

echo "Basic perf probe: 20 sequential requests to /health"
START=$(date +%s%3N)
for i in {1..20}; do curl -fsS "http://127.0.0.1:$LOCAL_PORT/health" >/dev/null; done
END=$(date +%s%3N)
TOTAL_MS=$((END-START))
AVG_MS=$((TOTAL_MS/20))
echo "Average latency: ${AVG_MS}ms over 20 requests"

echo "Scraping /metrics sample (first 5 lines)"
curl -fsS "http://127.0.0.1:$LOCAL_PORT/metrics" | head -n 5 || echo "No metrics endpoint exposed"

echo "Validation succeeded for $APP_LABEL in $NAMESPACE"
