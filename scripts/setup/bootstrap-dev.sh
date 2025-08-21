#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
cp .env.development.example .env || true
echo "[setup] Development environment bootstrapped."
