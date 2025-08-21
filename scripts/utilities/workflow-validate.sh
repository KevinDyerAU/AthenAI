#!/usr/bin/env bash
set -euo pipefail
WORKFLOWS_DIR=${1:-"workflows"}
FAIL=0
while IFS= read -r -d '' f; do
  echo "[workflow] Validating $f"
  python -c "import json,sys;json.load(open(sys.argv[1]));print('OK')" "$f" || FAIL=1
done < <(find "$WORKFLOWS_DIR" -type f -name '*.json' -print0)
exit $FAIL
