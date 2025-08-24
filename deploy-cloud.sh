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

# Cleanup temp prelude (not critical)
rm -f "$PROJECT_DIR/.cloud_prelude.tmp.sh" || true
