#!/usr/bin/env bash
set -euo pipefail

# aggregate-metrics.sh
# Aggregates k6 JSON summaries into a consolidated markdown and JSON report.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

usage() {
  cat <<USAGE
Usage: $0 --results-dir ./test-results
USAGE
}

RESULTS_DIR="./test-results"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --results-dir) RESULTS_DIR="${2:-./test-results}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 1;;
  esac
done

mkdir -p "$RESULTS_DIR"
OUT_JSON="$RESULTS_DIR/metrics-summary.json"
OUT_MD="$RESULTS_DIR/metrics-summary.md"

echo '{"endpoints":[]}' > "$OUT_JSON"
: > "$OUT_MD"

join_json() {
  # $1: base json path, $2: file to append, $3: key
  jq --argfile item "$2" '.endpoints += [$item]' "$1" > "$1.tmp" && mv "$1.tmp" "$1"
}

summarize() {
  local f="$1"
  local ep=$(jq -r '.endpoint' "$f" 2>/dev/null || echo "unknown")
  local http_reqs=$(jq -r '.metrics.http_reqs.count // .metrics.http_reqs.values.count // 0' "$f" 2>/dev/null || echo 0)
  local rps=$(jq -r '.metrics.http_reqs.rate // 0' "$f" 2>/dev/null || echo 0)
  local p95=$(jq -r '.metrics.http_req_duration.p(95) // .metrics.http_req_duration.values.p95 // 0' "$f" 2>/dev/null || echo 0)
  local fail_rate=$(jq -r '.metrics.checks.fails // .metrics.checks.failures // 0' "$f" 2>/dev/null || echo 0)
  printf "- endpoint: %s\n  http_reqs: %s\n  rps: %s\n  p95_ms: %s\n  check_failures: %s\n" "$ep" "$http_reqs" "$rps" "$p95" "$fail_rate"
}

if compgen -G "$RESULTS_DIR/k6_*.json" > /dev/null; then
  for f in "$RESULTS_DIR"/k6_*.json; do
    info "Aggregating $f"
    # Append to consolidated JSON
    join_json "$OUT_JSON" "$f"
    # Append to markdown
    echo "## $(basename "$f")" >> "$OUT_MD"
    summarize "$f" >> "$OUT_MD" || true
    echo "" >> "$OUT_MD"
  done
  info "Metrics aggregated: $OUT_JSON, $OUT_MD"
else
  warn "No k6_*.json files found in $RESULTS_DIR"
fi
