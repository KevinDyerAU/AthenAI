#!/usr/bin/env bash
set -euo pipefail

# Performance/load test for n8n webhook endpoints.
# Uses k6 if available, else ApacheBench (ab), else a simple curl concurrency loop.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

BASE="${N8N_BASE_URL:-http://localhost:5678}"
RESULTS_DIR="${RESULTS_DIR:-./test-results}"
mkdir -p "$RESULTS_DIR"
ENDPOINTS=(
  "/webhook/planning-agent"
  "/webhook/execution-agent"
  "/webhook/quality-assurance-agent"
)
DURATION="${DURATION:-30s}"      # k6 duration
VUS="${VUS:-5}"                   # k6 virtual users
TOTAL_REQ="${TOTAL_REQ:-200}"     # ab/curl total requests
CONCURRENCY="${CONCURRENCY:-10}"  # ab/curl concurrency
PAYLOAD='{"load":true}'

# Quick reachability check
if ! command -v curl >/dev/null 2>&1; then err "curl required"; exit 2; fi
if ! curl -fsS --max-time 5 "$BASE" >/dev/null; then
  warn "n8n not reachable at $BASE; skipping performance test"
  exit 0
fi

run_k6() {
  local url="$1"
  local script="$(mktemp).js"
  local name="$(echo "$url" | sed 's#https\?://##; s#[^A-Za-z0-9_\-]#_#g')"
  local outJson="$RESULTS_DIR/k6_${name}.json"
  cat > "$script" <<K6
import http from 'k6/http';
import { check, sleep } from 'k6';
export const options = { vus: ${VUS}, duration: '${DURATION}' };
export default function () {
  const res = http.post('${url}', '${PAYLOAD}', { headers: { 'Content-Type': 'application/json' } });
  check(res, { 'status is 2xx': r => r.status >= 200 && r.status < 300 });
  sleep(0.1);
}
K6
  info "k6 running ${url} vus=${VUS} duration=${DURATION}"
  K6_SUMMARY_EXPORT="$outJson" k6 run --summary-export "$outJson" "$script" || warn "k6 run reported issues"
  # annotate endpoint into JSON for aggregator if possible
  if command -v jq >/dev/null 2>&1 && [[ -f "$outJson" ]]; then
    jq --arg ep "$url" '. + {endpoint: $ep}' "$outJson" > "$outJson.tmp" && mv "$outJson.tmp" "$outJson"
  fi
}

run_ab() {
  local url="$1"
  info "ab running ${url} n=${TOTAL_REQ} c=${CONCURRENCY}"
  ab -n "$TOTAL_REQ" -c "$CONCURRENCY" -p <(echo -n "$PAYLOAD") -T 'application/json' "$url" || warn "ab reported issues"
}

run_curl_loop() {
  local url="$1"
  info "curl loop ${url} total=${TOTAL_REQ} conc=${CONCURRENCY}"
  tmp="$(mktemp)"
  sem="$(mktemp -u)"; mkfifo "$sem"; exec 3<>"$sem"; rm "$sem"
  for ((i=0;i<CONCURRENCY;i++)); do echo >&3; done
  for ((i=0;i<TOTAL_REQ;i++)); do
    read -u 3
    {
      t=$( { time -p curl -fsS -o /dev/null -w "%{http_code}\n" -H 'Content-Type: application/json' --data "$PAYLOAD" "$url"; } 2>&1 | awk '/real/ {print $2}' )
      echo "$t" >> "$tmp" || true
      echo >&3
    } &
  done
  wait
  exec 3>&-
  if command -v awk >/dev/null 2>&1; then
    count=$(wc -l < "$tmp")
    avg=$(awk '{sum+=$1} END { if (NR>0) printf "%.3f", sum/NR; }' "$tmp")
    info "curl loop results: requests=$count avg_seconds=$avg"
  fi
}

for ep in "${ENDPOINTS[@]}"; do
  url="${BASE%/}${ep}"
  if command -v k6 >/dev/null 2>&1; then run_k6 "$url"
  elif command -v ab >/dev/null 2>&1; then run_ab "$url"
  else run_curl_loop "$url"; fi
done

info "Performance test completed"
