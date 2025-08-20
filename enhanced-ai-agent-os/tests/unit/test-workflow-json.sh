#!/usr/bin/env bash
set -euo pipefail

# Validates workflow JSON files and basic required fields

LOG_TS() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
info() { echo "[INFO] $(LOG_TS) $*"; }
warn() { echo "[WARN] $(LOG_TS) $*"; }
err()  { echo "[ERROR] $(LOG_TS) $*" 1>&2; }

need() { command -v "$1" >/dev/null 2>&1 || { err "$1 not found"; exit 2; }; }
need jq

ROOT="enhanced-ai-agent-os/workflows"
[ -d "$ROOT" ] || { err "Workflows dir not found: $ROOT"; exit 3; }

shopt -s globstar nullglob
files=( "$ROOT"/**/*.json )
if [[ ${#files[@]} -eq 0 ]]; then err "No workflow JSON files found"; exit 4; fi

pass=0; fail=0
for f in "${files[@]}"; do
  info "Validating JSON: $f"
  if ! jq 'type=="object"' "$f" >/dev/null; then err "Invalid JSON: $f"; ((fail++)); continue; fi
  # Basic structure sanity: nodes array exists
  if ! jq '.nodes and (.nodes|type=="array")' "$f" | grep -q true; then err "Missing or invalid nodes[]: $f"; ((fail++)); continue; fi
  ((pass++))
done
info "Unit JSON validation: pass=$pass fail=$fail"
[[ $fail -eq 0 ]]
