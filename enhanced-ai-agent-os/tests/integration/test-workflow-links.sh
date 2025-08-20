#!/usr/bin/env bash
set -euo pipefail

# Verifies presence of core workflows and tool workflows expected by the system

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }
need() { command -v "$1" >/dev/null 2>&1 || { err "$1 not found"; exit 2; }; }
need jq

root="enhanced-ai-agent-os/workflows"

expected=(
  "$root/planning-agent.json"
  "$root/execution-agent.json"
  "$root/quality-assurance-agent.json"
  "$root/planning-tools/resource-allocation.json"
  "$root/planning-tools/timeline-optimization.json"
  "$root/execution-tools/parallel-processing.json"
  "$root/execution-tools/error-recovery.json"
  "$root/qa-tools/automated-testing.json"
  "$root/qa-tools/compliance-checking.json"
)

for f in "${expected[@]}"; do
  info "Checking existence: $f"
  [[ -f "$f" ]] || { err "Missing file: $f"; exit 3; }
  jq '.' "$f" >/dev/null || { err "Invalid JSON: $f"; exit 4; }
  # must have at least 1 node
  jq '.nodes|length>0' "$f" | grep -q true || { err "No nodes in: $f"; exit 5; }
done

info "Integration links check passed"
