#!/usr/bin/env bash
set -euo pipefail

# End-to-end smoke tests that hit expected webhook endpoints if n8n is running.
# Skips gracefully if service is unreachable.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

need() { command -v "$1" >/dev/null 2>&1 || { err "$1 not found"; exit 2; }; }
need curl
need jq

BASE="${N8N_BASE_URL:-http://localhost:5678}"
TIMEOUT=5

# Expected endpoints (may be adjusted per deployment)
endpoints=("/webhook/planning-agent" "/webhook/execution-agent" "/webhook/quality-assurance-agent")

# Quick reachability check
if ! curl -fsS --max-time "$TIMEOUT" "$BASE" >/dev/null; then
  warn "n8n not reachable at $BASE; skipping e2e tests"
  exit 0
fi

pass=0; fail=0

post_and_check() {
  local url="$1" payload="$2" jqcheck="$3"
  info "POST $url with contract payload"
  resp=$(curl -fsS -H 'Content-Type: application/json' --data "$payload" --max-time "$TIMEOUT" "$url" || true)
  if [[ -z "$resp" ]]; then warn "Empty response from $url"; ((fail++)); return; fi
  if echo "$resp" | jq '.' >/dev/null 2>&1; then
    if [[ -n "$jqcheck" ]]; then
      if echo "$resp" | jq -e "$jqcheck" >/dev/null 2>&1; then ((pass++)); else warn "Response JSON missing expected fields for $url"; ((fail++)); fi
    else
      ((pass++))
    fi
  else
    warn "Non-JSON response from $url"; ((fail++))
  fi
}

for ep in "${endpoints[@]}"; do
  url="${BASE%/}${ep}"
  case "$ep" in
    "/webhook/planning-agent")
      payload='{"project":{"name":"Test","methodology":"agile"},"tasks":[{"id":"T1","skills":["js"]}],"resources":[{"name":"Dev1","skills":["js"],"capacity":1}]}'
      jqcheck='has("plan") or has("planning") or .status? == "ok"'
      ;;
    "/webhook/execution-agent")
      payload='{"tasks":[{"id":"A","deps":[]},{"id":"B","deps":["A"]}],"concurrency":2}'
      jqcheck='has("batches") or has("orchestration") or .status? == "ok"'
      ;;
    "/webhook/quality-assurance-agent")
      payload='{"artifacts":[{"type":"code","content":"print(1)"}],"standards":["basic","security"]}'
      jqcheck='has("qualityReport") or has("results") or .status? == "ok"'
      ;;
    *) payload='{"ping":true}'; jqcheck='.';;
  esac
  post_and_check "$url" "$payload" "$jqcheck"
done

info "E2E endpoint smoke/contracts: pass=$pass fail=$fail"
[[ $fail -eq 0 ]]
