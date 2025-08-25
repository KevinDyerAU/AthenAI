#!/usr/bin/env bash
set -euo pipefail
# Wrapper to run the Python validator with a given env file and environment
# Usage: scripts/config/validate.sh .env.development.example development

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <env-file> <environment>" >&2
  exit 1
fi

ENV_FILE="$1"
ENVIRONMENT="$2"

python3 "$(dirname "$0")/validate_env.py" --env-file "$ENV_FILE" --environment "$ENVIRONMENT"
