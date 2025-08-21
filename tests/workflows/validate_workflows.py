#!/usr/bin/env python3
"""
Validate all workflow JSON files under the `workflows/` tree for JSON syntax
and minimal n8n structure (name, nodes, connections).

Usage:
  python tests/workflows/validate_workflows.py
Exit code 0 on success, non-zero on failure.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / "workflows"

REQUIRED_FIELDS = ["name", "nodes", "connections"]


def main() -> int:
    if not WF.exists():
        print(f"Missing workflows directory: {WF}")
        return 1

    failures = 0
    files = list(WF.rglob("*.json"))
    if not files:
        print("No workflow JSON files found.")
        return 1

    for f in files:
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[FAIL] {f}: invalid JSON: {e}")
            failures += 1
            continue
        missing = [k for k in REQUIRED_FIELDS if k not in doc]
        if missing:
            print(f"[FAIL] {f}: missing fields: {', '.join(missing)}")
            failures += 1
        else:
            print(f"[OK]   {f}")

    if failures:
        print(f"Validation failed: {failures} file(s) invalid")
        return 1
    print("All workflow files valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
