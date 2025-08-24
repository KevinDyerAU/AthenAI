#!/usr/bin/env bash
# NeoV3 - Unified Local Deployment
# Location: repo root
set -euo pipefail

# --- Paths ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE_CANDIDATES=("$PROJECT_DIR/.env.example" "$PROJECT_DIR/unified.env.example")
LOG_FILE="$PROJECT_DIR/deployment.local.log"

# Temp deployment root (per-run)
TIMESTAMP="$(date +'%Y%m%d-%H%M%S')"
DEPLOY_TMP_ROOT="$PROJECT_DIR/deploy_tmp/$TIMESTAMP"
OVERRIDE_FILE="$DEPLOY_TMP_ROOT/docker-compose.override.yml"

# --- Colors ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

log()  { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"; }
info() { echo -e "${CYAN}[INFO]${NC} $*" | tee -a "$LOG_FILE"; }
success(){ echo -e "${GREEN}[SUCCESS]${NC} $*" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*" | tee -a "$LOG_FILE"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE"; exit 1; }

usage() {
  cat <<'EOF'
NeoV3 Local Deployment

Usage: ./deploy-local.sh [--fresh | --reuse] [--status] [--check] [--help]

Options:
  --fresh   Bring the stack down (-v) and recreate containers
  --reuse   Reuse existing containers (no recreate), skip pulls
  --status  Print docker compose ps and per-container health and exit
  --check   Validate tools, .env keys, and compose config (no changes)
  --help    Show this help and exit

Phases:
  1) Core services: postgres, neo4j, rabbitmq (wait healthy)
  2) Monitoring: prometheus, grafana, loki, promtail, alertmanager, otel-collector
  3) Orchestration: n8n
  4) API service: build and start

Requires .env at repo root. If missing, it will be created from .env.example or unified.env.example.
EOF
}

# --- Args ---
SKIP_PULL=false; FRESH_START=false; DOCKER_UP_ARGS=""; STATUS_ONLY=false; CHECK_ONLY=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --reuse) SKIP_PULL=true; FRESH_START=false; DOCKER_UP_ARGS="--no-recreate" ;;
    --fresh) SKIP_PULL=false; FRESH_START=true;  DOCKER_UP_ARGS="--force-recreate --build" ;;
    --status) STATUS_ONLY=true ;;
    --check) CHECK_ONLY=true ;;
    --help|-h) usage; exit 0 ;;
    *) warn "Unknown option: $1"; usage; exit 1 ;;
  esac
  shift
done

# --- Helpers ---
docker_compose(){ if docker compose version --short >/dev/null 2>&1; then docker compose "$@"; else docker-compose "$@"; fi }

require_tools(){ command -v docker >/dev/null || err "Docker not found"; docker info >/dev/null 2>&1 || err "Docker daemon not running"; docker_compose version >/dev/null 2>&1 || err "Docker Compose not available"; }

ensure_env(){
  if [[ -f "$ENV_FILE" ]]; then log ".env found"; return; fi
  for cand in "${ENV_EXAMPLE_CANDIDATES[@]}"; do
    if [[ -f "$cand" ]]; then cp -f "$cand" "$ENV_FILE"; warn "Created .env from $(basename "$cand"). Review secrets before first run"; return; fi
  done
  err "No .env found. Add $ENV_FILE first."
}

generate_secret(){
  local len="${1:-32}"
  # Portable secret: base64, strip non-alnum with a few symbols
  head -c 64 /dev/urandom | base64 | tr -dc 'A-Za-z0-9!#$%&@' | head -c "$len"
}

set_env_if_missing(){
  local key="$1" val="$2"
  grep -qE "^\s*${key}\s*=" "$ENV_FILE" 2>/dev/null || { echo "${key}=${val}" >>"$ENV_FILE"; log "Initialized ${key} in .env"; }
}

# Replace an env var's value in-place in .env (handles macOS/Linux sed)
replace_env_value(){
  local key="$1" val="$2"
  if [[ "$OSTYPE" == darwin* ]]; then
    sed -i '' -E "s|^\s*${key}\s*=.*$|${key}=${val}|" "$ENV_FILE"
  else
    sed -i -E "s|^\s*${key}\s*=.*$|${key}=${val}|" "$ENV_FILE"
  fi
  log "Updated ${key} in .env"
}

# Ensure a secret is present and non-empty.
# - When FRESH_START=true: if missing OR empty, set to generated value
# - Otherwise: only set if missing
ensure_secret_nonempty(){
  local key="$1" gen_len="${2:-32}"
  local generated
  generated="$(generate_secret "$gen_len")"

  if [[ "$FRESH_START" == true ]]; then
    if ! grep -qE "^\s*${key}\s*=" "$ENV_FILE" 2>/dev/null; then
      echo "${key}=${generated}" >>"$ENV_FILE"; log "Initialized ${key} in .env (fresh)";
    else
      # If empty (e.g., KEY=, KEY="", KEY='') replace with generated
      if grep -qE "^\s*${key}\s*=\s*(""|''|\s*)$" "$ENV_FILE"; then
        replace_env_value "$key" "$generated"
      fi
    fi
  else
    set_env_if_missing "$key" "$generated"
  fi
}

ensure_secrets(){
  log "Ensuring required secrets in .env"
  set_env_if_missing POSTGRES_USER postgres
  set_env_if_missing POSTGRES_DB enhanced_ai_os

  # Core service passwords/secrets must be non-empty on fresh runs
  ensure_secret_nonempty POSTGRES_PASSWORD 32
  ensure_secret_nonempty NEO4J_PASSWORD 32
  set_env_if_missing RABBITMQ_DEFAULT_USER ai_agent_user
  ensure_secret_nonempty RABBITMQ_DEFAULT_PASS 32

  # Platform/application secrets
  ensure_secret_nonempty API_SECRET_KEY 48
  ensure_secret_nonempty GRAFANA_SECURITY_ADMIN_PASSWORD 32
  ensure_secret_nonempty N8N_ENCRYPTION_KEY 48

  # Additional common secrets from .env.example that are often left blank
  ensure_secret_nonempty JWT_SECRET 48
  ensure_secret_nonempty ENCRYPTION_KEY 48
  ensure_secret_nonempty HMAC_SECRET 48
  ensure_secret_nonempty WEBHOOK_SECRET 32
  ensure_secret_nonempty N8N_BASIC_AUTH_PASSWORD 32
  ensure_secret_nonempty DB_PASSWORD 32
}

ensure_dirs(){
  mkdir -p "$DEPLOY_TMP_ROOT"
  local paths=(
    "enhanced-ai-agent-os/data/postgres"
    "enhanced-ai-agent-os/backups/postgres"
    "enhanced-ai-agent-os/data/neo4j/data"
    "enhanced-ai-agent-os/data/neo4j/logs"
    "enhanced-ai-agent-os/data/neo4j/import"
    "enhanced-ai-agent-os/data/neo4j/plugins"
    "enhanced-ai-agent-os/backups/neo4j"
    "enhanced-ai-agent-os/data/rabbitmq"
    "enhanced-ai-agent-os/logs/rabbitmq"
    "enhanced-ai-agent-os/backups/rabbitmq"
    "enhanced-ai-agent-os/data/n8n"
    "enhanced-ai-agent-os/logs/n8n"
    "enhanced-ai-agent-os/backups/n8n"
    "enhanced-ai-agent-os/data/prometheus"
    "enhanced-ai-agent-os/data/grafana"
    "enhanced-ai-agent-os/logs/grafana"
    "enhanced-ai-agent-os/data/alertmanager"
    "enhanced-ai-agent-os/data/loki"
    "logs/api"
    "data/api"
  )
  for p in "${paths[@]}"; do mkdir -p "$DEPLOY_TMP_ROOT/$p"; done
}

ensure_network(){ if ! docker network ls --format '{{.Name}}' | grep -q '^agentnet$'; then docker network create agentnet >/dev/null; fi }

fresh_down(){ if [[ -f "$COMPOSE_FILE" ]]; then docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down -v || true; fi }

fresh_reset(){
  log "Performing full reset: clearing deploy_tmp, removing .env"
  local root_tmp="$PROJECT_DIR/deploy_tmp"
  if [[ -d "$root_tmp" ]]; then rm -rf "$root_tmp" || true; fi
  if [[ -f "$ENV_FILE" ]]; then rm -f "$ENV_FILE" || true; fi
}

wait_healthy(){
  local name="$1"; local timeout="${2:-360}"; local elapsed=0
  while (( elapsed < timeout )); do
    local state
    state=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$name" 2>/dev/null || true)
    [[ "$state" == "healthy" ]] && { success "$name healthy"; return 0; }
    sleep 5; elapsed=$((elapsed+5))
  done
  err "Timeout waiting for $name to be healthy"
}

print_health(){
  local name="$1"
  local state
  state=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$name" 2>/dev/null || true)
  if [[ -z "$state" ]]; then echo "${name}: not found"; else echo "${name}: ${state}"; fi
}

check_env_keys(){
  local required=(
    POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB
    NEO4J_PASSWORD
    RABBITMQ_DEFAULT_USER RABBITMQ_DEFAULT_PASS
    API_SECRET_KEY N8N_ENCRYPTION_KEY GRAFANA_SECURITY_ADMIN_PASSWORD
  )
  [[ -f "$ENV_FILE" ]] || { err ".env not found at $ENV_FILE"; }
  local missing=()
  local text
  text=$(cat "$ENV_FILE")
  for k in "${required[@]}"; do
    if ! grep -qE "^\s*${k}\s*=\S+" <<<"$text"; then missing+=("$k"); fi
  done
  if (( ${#missing[@]} > 0 )); then
    err "Missing required keys in .env: ${missing[*]}"
  fi
  success "All required .env keys present"
}

run_check(){
  log "Running preflight checks (no changes)"
  require_tools
  check_env_keys
  if docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" config >/dev/null 2>&1; then success "docker compose config OK"; else err "docker compose config failed"; fi
  echo -e "\n=== existing containers (if any) ==="; docker_compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps || true
  echo -e "\n=== health (if running) ===";
  for c in \
    enhanced-ai-postgres \
    enhanced-ai-neo4j \
    enhanced-ai-rabbitmq \
    enhanced-ai-n8n \
    enhanced-ai-prometheus \
    enhanced-ai-grafana \
    enhanced-ai-loki \
    enhanced-ai-alertmanager \
    enhanced-ai-agent-api; do
    print_health "$c"
  done
}

check_http(){
  local label="$1" url="$2"; local code
  code=$(curl -fsS -o /dev/null -w '%{http_code}' "$url" 2>/dev/null || true)
  if [[ "$code" == "200" || "$code" == "204" ]]; then success "${label} HTTP OK (${code}) - $url"; else warn "${label} HTTP check failed (${code:-no-conn}) - $url"; fi
}

phase_core(){
  log "Starting core: postgres, neo4j, rabbitmq"
  docker_compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" up -d $DOCKER_UP_ARGS postgres neo4j rabbitmq
  wait_healthy enhanced-ai-postgres 300
  wait_healthy enhanced-ai-neo4j 480
  wait_healthy enhanced-ai-rabbitmq 300
}

phase_monitoring(){
  log "Starting monitoring: prometheus grafana loki promtail alertmanager otel-collector"
  docker_compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" up -d $DOCKER_UP_ARGS prometheus grafana loki promtail alertmanager otel-collector || true
  # Lightweight HTTP checks on common ports
  local gp="${GRAFANA_PORT:-3000}" pp="${PROMETHEUS_PORT:-9090}" lp="${LOKI_PORT:-3100}" ap="${ALERTMANAGER_PORT:-9093}"
  check_http "Grafana" "http://localhost:${gp}/api/health"
  check_http "Prometheus" "http://localhost:${pp}/-/ready"
  check_http "Alertmanager" "http://localhost:${ap}/-/ready"
  check_http "Loki" "http://localhost:${lp}/ready"
}

phase_orchestration(){
  log "Starting orchestration: n8n"
  docker_compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" up -d $DOCKER_UP_ARGS n8n
  wait_healthy enhanced-ai-n8n 420 || warn "n8n health check not yet green; continuing"
}

phase_api(){
  log "Building and starting API"
  docker_compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" build api-service
  docker_compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" up -d $DOCKER_UP_ARGS api-service
  wait_healthy enhanced-ai-agent-api 300
}

summary(){
  echo -e "\n=== docker compose ps ===" | tee -a "$LOG_FILE"
  docker_compose -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" --env-file "$ENV_FILE" ps | tee -a "$LOG_FILE"
  echo -e "\n=== health summary ==="
  for c in \
    enhanced-ai-postgres \
    enhanced-ai-neo4j \
    enhanced-ai-rabbitmq \
    enhanced-ai-n8n \
    enhanced-ai-prometheus \
    enhanced-ai-grafana \
    enhanced-ai-loki \
    enhanced-ai-alertmanager \
    enhanced-ai-agent-api; do
    print_health "$c"
  done | tee -a "$LOG_FILE"
}

generate_override(){
  cat >"$OVERRIDE_FILE" <<EOF
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/postgres
  postgres_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/backups/postgres

  neo4j_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/neo4j/data
  neo4j_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/neo4j/logs
  neo4j_import:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/neo4j/import
  neo4j_plugins:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/neo4j/plugins
  neo4j_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/backups/neo4j

  rabbitmq_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/rabbitmq
  rabbitmq_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/logs/rabbitmq
  rabbitmq_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/backups/rabbitmq

  n8n_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/n8n
  n8n_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/logs/n8n
  n8n_backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/backups/n8n

  prometheus_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/prometheus

  grafana_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/grafana
  grafana_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/logs/grafana

  alertmanager_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/alertmanager

  loki_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/enhanced-ai-agent-os/data/loki

  api-logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/logs/api
  api-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DEPLOY_TMP_ROOT}/data/api
EOF
}

ensure_gitignore(){
  local gi="$PROJECT_DIR/.gitignore"
  if [[ ! -f "$gi" ]]; then
    {
      echo 'deploy_tmp/'
      echo '.env'
      echo 'deployment.local.log'
    } > "$gi"
  else
    grep -qx 'deploy_tmp/' "$gi" || echo 'deploy_tmp/' >> "$gi"
    grep -qx '\.env' "$gi" || echo '.env' >> "$gi"
    grep -qx 'deployment\.local\.log' "$gi" || echo 'deployment.local.log' >> "$gi"
  fi
}

main(){
  : >"$LOG_FILE"
  require_tools
  if [[ "$CHECK_ONLY" == true ]]; then run_check; exit 0; fi
  ensure_env
  if [[ "$FRESH_START" == true ]]; then fresh_down; fresh_reset; ensure_env; fi
  ensure_secrets
  ensure_dirs
  generate_override
  ensure_gitignore
  ensure_network
  [[ "$SKIP_PULL" == false ]] && { log "docker compose pull"; docker_compose -f "$COMPOSE_FILE" -f "$OVERRIDE_FILE" --env-file "$ENV_FILE" pull || true; }
  if [[ "$STATUS_ONLY" == true ]]; then
    summary; exit 0
  fi
  phase_core
  phase_monitoring
  phase_orchestration
  phase_api
  summary
  success "Local deployment completed. Access: API http://localhost:5000, Grafana http://localhost:3000, Prometheus http://localhost:9090, n8n http://localhost:5678"
}

main "$@"
