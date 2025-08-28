#!/usr/bin/env bash
# Start the NeoV3 local portal (index.html) with env-driven ports
# Usage:
#   ./start-index.sh                # serves on 8088
#   ./start-index.sh 8090           # custom serve port
#   SERVE_PORT=8090 ./start-index.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-${SERVE_PORT:-8088}}"
export SERVE_PORT="$PORT"

# Pass through common ports if present in current shell
forward_vars=(
  API_HOST_PORT API_PORT N8N_PORT GRAFANA_PORT PROMETHEUS_PORT \
  ALERTMANAGER_PORT LOKI_PORT RABBITMQ_MGMT_PORT RABBITMQ_MANAGEMENT_PORT \
  NEO4J_HTTP_PORT NEO4J_PORT_HTTP NEO4J_PORT
)
for k in "${forward_vars[@]}"; do
  v="${!k-}"
  if [[ -n "${v:-}" ]]; then export "$k"="$v"; fi
done

cd "$SCRIPT_DIR"

# Prefer venv python if available
if [[ -x ".venv/bin/python" ]]; then
  PYBIN=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYBIN="python3"
else
  PYBIN="python"
fi

echo "Starting NeoV3 local portal on http://localhost:${PORT}"
exec "$PYBIN" "serve.py"
