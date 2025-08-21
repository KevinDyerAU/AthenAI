#!/usr/bin/env bash
set -euo pipefail
TARGET=${1:-"./tmp"}
echo "[maintenance] Cleaning $TARGET"
rm -rf "$TARGET" && mkdir -p "$TARGET"
echo "[maintenance] Done"
