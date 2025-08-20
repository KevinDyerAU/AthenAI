#!/usr/bin/env bash
set -euo pipefail

# run-all-tests.sh
# Orchestrates unit, integration, e2e, performance, and AI capability tests.

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

usage() {
  cat <<USAGE
Usage: $0 [--category all|unit|integration|e2e|performance|ai] [--results-dir ./test-results] [--fail-fast]

Examples:
  $0 --category all
  $0 --category performance --results-dir ./test-results
USAGE
}

CATEGORY="all"
RESULTS_DIR="./test-results"
FAIL_FAST=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --category) CATEGORY="${2:-all}"; shift 2;;
    --results-dir) RESULTS_DIR="${2:-./test-results}"; shift 2;;
    --fail-fast) FAIL_FAST=true; shift;;
    -h|--help) usage; exit 0;;
    *) err "Unknown arg: $1"; usage; exit 1;;
  esac
done

mkdir -p "$RESULTS_DIR"
SUMMARY_FILE="$RESULTS_DIR/summary_$(date -u +%Y%m%dT%H%M%SZ).log"
: > "$SUMMARY_FILE"
export RESULTS_DIR

run_suite() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then warn "Suite dir not found: $dir"; return; fi
  shopt -s nullglob
  local scripts=("$dir"/*.sh)
  if [[ ${#scripts[@]} -eq 0 ]]; then warn "No tests in $dir"; return; fi
  for s in "${scripts[@]}"; do
    info "Running: $s" | tee -a "$SUMMARY_FILE"
    if bash "$s" >> "$SUMMARY_FILE" 2>&1; then
      info "PASS: $s" | tee -a "$SUMMARY_FILE"
    else
      err "FAIL: $s (see summary)" | tee -a "$SUMMARY_FILE"
      if [[ "$FAIL_FAST" == true ]]; then exit 1; fi
    fi
  done
}

case "$CATEGORY" in
  all|unit) run_suite "enhanced-ai-agent-os/tests/unit";;
esac
case "$CATEGORY" in
  all|integration) run_suite "enhanced-ai-agent-os/tests/integration";;
esac
case "$CATEGORY" in
  all|e2e) run_suite "enhanced-ai-agent-os/tests/e2e";;
 esac
case "$CATEGORY" in
  all|performance) run_suite "enhanced-ai-agent-os/tests/performance";;
 esac
if [[ "$CATEGORY" == "all" || "$CATEGORY" == "performance" ]]; then
  if [[ -f "enhanced-ai-agent-os/scripts/testing/aggregate-metrics.sh" ]]; then
    bash enhanced-ai-agent-os/scripts/testing/aggregate-metrics.sh --results-dir "$RESULTS_DIR" | tee -a "$SUMMARY_FILE" || true
  fi
fi
case "$CATEGORY" in
  all|ai) run_suite "enhanced-ai-agent-os/tests/ai-capabilities";;
 esac

info "All done. Summary: $SUMMARY_FILE"
