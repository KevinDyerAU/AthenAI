#!/usr/bin/env bash
set -euo pipefail

TARGET_URL="${TARGET_URL:-http://localhost:5678}"
CONTEXT_FILE="${CONTEXT_FILE:-}"

docker run --rm -v "$PWD:/zap/wrk" -t owasp/zap2docker-stable zap-baseline.py \
  -t "$TARGET_URL" \
  ${CONTEXT_FILE:+-c "$CONTEXT_FILE"} \
  -r zap-report.html

echo "ZAP baseline scan complete. See zap-report.html"
