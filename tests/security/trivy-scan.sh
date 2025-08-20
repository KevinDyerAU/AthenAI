#!/usr/bin/env bash
set -euo pipefail

IMAGES=( enhanced-ai-n8n enhanced-ai-postgres enhanced-ai-neo4j enhanced-ai-rabbitmq enhanced-ai-grafana enhanced-ai-prometheus )

for img in "${IMAGES[@]}"; do
  echo "Scanning $img"
  docker run --rm aquasec/trivy:0.54.1 image --severity HIGH,CRITICAL --no-progress "$img" || true
  echo
done
