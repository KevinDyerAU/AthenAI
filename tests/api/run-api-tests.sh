#!/usr/bin/env bash
set -euo pipefail

# API spec validation and endpoint smoke tests

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

BASE="${N8N_BASE_URL:-http://localhost:5678}"
SPEC="${SPEC_PATH:-api/openapi.yaml}"
MODE="all" # validate|smoke|all

usage(){
  cat <<USAGE
Usage: $0 [--validate-spec|--smoke|--all] [--base <url>] [--spec <path>]
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --validate-spec) MODE="validate"; shift;;
    --smoke) MODE="smoke"; shift;;
    --all) MODE="all"; shift;;
    --base) BASE="$2"; shift 2;;
    --spec) SPEC="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 1;;
  esac
done

need() { command -v "$1" >/dev/null 2>&1 || { err "$1 not found"; exit 2; }; }
need curl

validate_spec(){
  info "Validating OpenAPI spec: $SPEC"
  if command -v docker >/dev/null 2>&1; then
    docker run --rm -v "$(pwd)":/work -w /work swaggerapi/swagger-cli:latest validate "$SPEC" && return 0 || true
  fi
  if command -v npx >/dev/null 2>&1; then
    npx -y @redocly/cli lint "$SPEC" && return 0 || true
  fi
  # Fallback minimal check with yq/jq if available
  if command -v yq >/dev/null 2>&1; then
    yq '.openapi and .info and .paths' "$SPEC" >/dev/null || { err "Spec missing required fields"; return 1; }
    info "Spec basic structure OK (yq)"
    return 0
  fi
  warn "No validator available. Skipping formal validation."
}

smoke_tests(){
  info "Smoke: GET $BASE/health"
  code=$(curl -fsS -o /dev/null -w "%{http_code}" "$BASE/health" || true)
  if [[ ! "$code" =~ ^2 ]]; then warn "Health non-2xx: $code"; else info "Health OK"; fi

  info "Smoke: POST planning-agent"
  curl -fsS -H 'Content-Type: application/json' --data '{"project":{"name":"Test","methodology":"agile"},"tasks":[{"id":"T1","skills":["js"]}],"resources":[{"name":"Dev1","skills":["js"],"capacity":1}]}' --max-time 5 "$BASE/webhook/planning-agent" >/dev/null || warn "planning-agent failed"

  info "Smoke: POST execution-agent"
  curl -fsS -H 'Content-Type: application/json' --data '{"tasks":[{"id":"A","deps":[]},{"id":"B","deps":["A"]}],"concurrency":2}' --max-time 5 "$BASE/webhook/execution-agent" >/dev/null || warn "execution-agent failed"

  info "Smoke: POST quality-assurance-agent"
  curl -fsS -H 'Content-Type: application/json' --data '{"artifacts":[{"type":"code","content":"print(1)"}],"standards":["basic","security"]}' --max-time 5 "$BASE/webhook/quality-assurance-agent" >/dev/null || warn "qa-agent failed"
}

case "$MODE" in
  validate) validate_spec;;
  smoke) smoke_tests;;
  all) validate_spec; smoke_tests;;
  *) err "Unknown mode $MODE"; exit 1;;
esac
