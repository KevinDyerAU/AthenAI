#!/usr/bin/env bash
set -euo pipefail

# health-check.sh
# Performs system health assessment for Enhanced AI Agent OS components.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

N8N_URL="${N8N_BASE_URL:-http://localhost:5678}"
TIMEOUT="${TIMEOUT_SEC:-5}"

check_http() {
  local url="$1"
  if command -v curl >/dev/null 2>&1; then
    if curl -fsS --max-time "$TIMEOUT" "$url" >/dev/null; then
      ok=true
    else
      ok=false
    fi
  else
    warn "curl not found; skipping HTTP check for $url"
    ok=skip
  fi
  echo "$ok"
}

# Summary structure
STATUS=()
append_status() { STATUS+=("$1") ; }

info "Starting health check..."

# n8n basic check (root should render UI)
res=$(check_http "$N8N_URL")
if [[ "$res" == true ]]; then append_status "n8n:up"; else append_status "n8n:down"; fi

# Prometheus endpoint (if enabled)
if [[ "${ENABLE_PROMETHEUS:-false}" == "true" ]]; then
  purl="${N8N_URL%/}/metrics"
  res=$(check_http "$purl")
  if [[ "$res" == true ]]; then append_status "metrics:up"; else append_status "metrics:down"; fi
else
  append_status "metrics:disabled"
fi

# Redis (if URL provided)
if [[ -n "${REDIS_URL:-}" ]]; then
  if command -v redis-cli >/dev/null 2>&1; then
    if redis-cli -u "$REDIS_URL" ping | grep -qi PONG; then append_status "redis:up"; else append_status "redis:down"; fi
  else
    append_status "redis:cli-missing"
  fi
else
  append_status "redis:unset"
fi

# Neo4j (if URI provided)
if [[ -n "${NEO4J_URI:-}" ]]; then
  if command -v cypher-shell >/dev/null 2>&1; then
    if echo 'RETURN 1;' | cypher-shell -a "$NEO4J_URI" -u "${NEO4J_USER:-neo4j}" -p "${NEO4J_PASSWORD:-}" >/dev/null 2>&1; then
      append_status "neo4j:up"
    else
      append_status "neo4j:down"
    fi
  else
    append_status "neo4j:cli-missing"
  fi
else
  append_status "neo4j:unset"
fi

# AI provider key presence
prov="${AI_DEFAULT_PROVIDER:-openai}"
case "$prov" in
  openai) [[ -n "${OPENAI_API_KEY:-}" ]] && append_status "ai:openai:set" || append_status "ai:openai:missing" ;;
  anthropic) [[ -n "${ANTHROPIC_API_KEY:-}" ]] && append_status "ai:anthropic:set" || append_status "ai:anthropic:missing" ;;
  google) [[ -n "${GOOGLE_API_KEY:-}" ]] && append_status "ai:google:set" || append_status "ai:google:missing" ;;
  azure) [[ -n "${AZURE_OPENAI_API_KEY:-}" && -n "${AZURE_OPENAI_ENDPOINT:-}" ]] && append_status "ai:azure:set" || append_status "ai:azure:missing" ;;
  *) append_status "ai:unknown" ;;
esac

info "Health summary: ${STATUS[*]}"
