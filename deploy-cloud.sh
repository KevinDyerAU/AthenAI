#!/usr/bin/env bash
# NeoV3 - Unified Cloud Deployment (Render.com)
# Location: repo root
set -euo pipefail

# This script consolidates enhanced-ai-agent-os/deploy-cloud/deploy-cloud.sh
# to run from the repository root while preserving functionality.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
LOG_FILE="$PROJECT_DIR/cloud-deployment.log"
ENV_FILE="$PROJECT_DIR/.env.cloud"

# Reuse upstream logic by sourcing the original script into this shell
UPSTREAM_SCRIPT="$PROJECT_DIR/enhanced-ai-agent-os/deploy-cloud/deploy-cloud.sh"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
log()  { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE"; exit 1; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*" | tee -a "$LOG_FILE"; }

# Create API web service on Render (Flask API in /api)
create_api_web_service() {
  log "Creating/Deploying API web service on Render"
  if [[ -z "${RENDER_API_KEY:-}" || -z "${GITHUB_REPO_URL:-}" ]]; then
    err "RENDER_API_KEY and GITHUB_REPO_URL must be set in .env.cloud"
  fi

  local RENDER_API_BASE="https://api.render.com/v1"
  # Map optional CloudAMQP to our API expected env
  local rabbitmq_url_val="${RABBITMQ_URL:-${CLOUDAMQP_URL:-}}"
  local jwt_secret_val="${JWT_SECRET_KEY:-${API_JWT_SECRET:-}}"

  # Build env var array JSON
  # Note: Render web services must listen on $PORT; Gunicorn binding uses $PORT
  read -r -d '' ENV_VARS_JSON <<EOF
[
  {"key":"FLASK_ENV","value":"production"},
  {"key":"SECRET_KEY","value":"${API_SECRET_KEY:-${SECRET_KEY:-change-me}}"},
  {"key":"JWT_SECRET_KEY","value":"${jwt_secret_val:-change-me}"},
  {"key":"CORS_ORIGINS","value":"${CORS_ORIGINS:-*}"},
  {"key":"DATABASE_URL","value":"${DATABASE_URL:-}"},
  {"key":"NEO4J_URI","value":"${NEO4J_URI:-}"},
  {"key":"NEO4J_USER","value":"${NEO4J_USERNAME:-${NEO4J_USER:-neo4j}}"},
  {"key":"NEO4J_PASSWORD","value":"${NEO4J_PASSWORD:-}"},
  {"key":"RABBITMQ_URL","value":"${rabbitmq_url_val:-}"},
  {"key":"OPENAI_API_KEY","value":"${OPENAI_API_KEY:-}"}
]
EOF

  read -r -d '' SERVICE_JSON <<EOF
{
  "type": "web_service",
  "name": "enhanced-ai-api",
  "ownerId": "${RENDER_OWNER_ID:-}",
  "repo": "${GITHUB_REPO_URL}",
  "branch": "${GITHUB_BRANCH:-main}",
  "rootDir": "api",
  "buildCommand": "pip install --upgrade pip && pip install -r requirements.txt",
  "startCommand": "gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 0.0.0.0:$PORT api.wsgi:app",
  "plan": "${API_PLAN:-starter}",
  "region": "${RENDER_REGION:-oregon}",
  "autoDeploy": true,
  "envVars": ${ENV_VARS_JSON},
  "healthCheckPath": "/system/health",
  "numInstances": ${API_INSTANCES:-1}
}
EOF

  local response
  response=$(curl -s -w "%{http_code}" \
    -X POST \
    -H "Authorization: Bearer ${RENDER_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "${SERVICE_JSON}" \
    "${RENDER_API_BASE}/services" \
    -o /tmp/api_service_response.json)

  if [[ "$response" != "201" && "$response" != "200" ]]; then
    warn "API web service creation returned HTTP $response"
    if [[ -f /tmp/api_service_response.json ]]; then warn "Response: $(cat /tmp/api_service_response.json)"; fi
  else
    local service_id service_url
    service_id=$(jq -r '.id // .service.id' /tmp/api_service_response.json)
    service_url=$(jq -r '.serviceDetails.url // .url // empty' /tmp/api_service_response.json)
    export API_SERVICE_ID="$service_id"
    export API_SERVICE_URL="$service_url"
    log "API service created: ID=$service_id URL=${service_url:-<pending>}"

    # Reuse upstream wait function if available
    if declare -f wait_for_service_ready >/dev/null 2>&1; then
      log "Waiting for API service to become ready..."
      wait_for_service_ready "web_service" "$service_id" 600 || err "API service failed to become ready"
    else
      warn "wait_for_service_ready not found; skipping readiness wait"
    fi
  fi

  rm -f /tmp/api_service_response.json || true
}

usage() {
  cat <<'EOF'
NeoV3 Cloud Deployment (Render.com)

Usage: ./deploy-cloud.sh [--help]

Description:
  Wrapper that runs the upstream Render.com deploy script from
  enhanced-ai-agent-os/deploy-cloud/deploy-cloud.sh, but uses root-level
  .env.cloud and logging.

Options:
  --help   Show this help and exit

Requirements:
  - .env.cloud at repo root with RENDER_API_KEY, GITHUB_REPO_URL, NEO4J_*, OPENAI_API_KEY, ...
  - bash, curl, jq (upstream will attempt to install jq where possible)
EOF
}

: >"$LOG_FILE"

# Validate prerequisites for this wrapper
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then usage; exit 0; fi
if [[ $# -gt 0 ]]; then warn "Unknown option(s): $*"; usage; exit 1; fi
command -v bash >/dev/null || err "bash not found"
command -v curl >/dev/null || warn "curl not found; upstream will check and install if possible"

# Ensure env file exists at root (the upstream script expects its own .env.cloud, we override)
if [[ ! -f "$ENV_FILE" ]]; then
  warn ".env.cloud not found at root. Create it with required credentials (RENDER_API_KEY, GITHUB_REPO_URL, NEO4J_*, OPENAI_API_KEY, etc.)."
fi

# Export variables to influence upstream
export SCRIPT_DIR_UPSTREAM="$(cd "$PROJECT_DIR/enhanced-ai-agent-os/deploy-cloud" 2>/dev/null && pwd)"
export PROJECT_DIR_UPSTREAM="$PROJECT_DIR/enhanced-ai-agent-os"

# We shim the upstream variables by defining a small prelude that sets
# ENV_FILE and LOG_FILE to root-level files, then sources the original script.
cat >"$PROJECT_DIR/.cloud_prelude.tmp.sh" <<'EOF'
# Prelude to align upstream script paths to repo root
SCRIPT_DIR="$SCRIPT_DIR_UPSTREAM"
PROJECT_DIR="$PROJECT_DIR_UPSTREAM"
ENV_FILE="$PWD/.env.cloud"
LOG_FILE="$PWD/cloud-deployment.log"
EOF

# Execute: prelude + upstream script in the same shell
# shellcheck disable=SC1090
source "$PROJECT_DIR/.cloud_prelude.tmp.sh"
# shellcheck disable=SC1090
source "$UPSTREAM_SCRIPT"

# Build/deploy API web service on Render (uses DATABASE_URL created upstream)
create_api_web_service

# After upstream deploy completes, run database migrations against managed services
log "Running cloud database migrations (Postgres, Neo4j)"
CLOUD_PG_SCRIPT="$PROJECT_DIR/scripts/migrations/cloud-apply-postgres.sh"
CLOUD_NEO_SCRIPT="$PROJECT_DIR/scripts/migrations/cloud-apply-neo4j.sh"
if [[ -f "$CLOUD_PG_SCRIPT" ]]; then
  bash "$CLOUD_PG_SCRIPT" || err "Cloud Postgres migration failed"
else
  warn "Missing script: $CLOUD_PG_SCRIPT"
fi
if [[ -f "$CLOUD_NEO_SCRIPT" ]]; then
  bash "$CLOUD_NEO_SCRIPT" || err "Cloud Neo4j migration failed"
else
  warn "Missing script: $CLOUD_NEO_SCRIPT"
fi

# Cleanup temp prelude (not critical)
rm -f "$PROJECT_DIR/.cloud_prelude.tmp.sh" || true
