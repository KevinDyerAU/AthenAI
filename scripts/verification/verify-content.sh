#!/usr/bin/env bash
set -euo pipefail
LEVEL=${1:-basic}
python scripts/verification/verify_content.py --level "$LEVEL"
