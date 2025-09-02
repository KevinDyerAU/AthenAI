#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔄 Loading n8n workflows during deployment..."

if ! docker-compose ps n8n | grep -q "Up"; then
    echo "❌ n8n service is not running. Cannot load workflows."
    exit 1
fi

if [ -f "$PROJECT_ROOT/scripts/load-workflows.sh" ]; then
    echo "📋 Executing workflow loader..."
    bash "$PROJECT_ROOT/scripts/load-workflows.sh"
else
    echo "❌ Workflow loader script not found at $PROJECT_ROOT/scripts/load-workflows.sh"
    exit 1
fi

echo "✅ n8n workflow loading completed"
