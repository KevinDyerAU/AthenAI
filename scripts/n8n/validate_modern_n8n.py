#!/usr/bin/env python3
"""
Validate that workflows use modern n8n (>=1.19.4) built-in AI capabilities and do not
reference community packages such as '@n8n/n8n-nodes-langchain'.

Usage:
  python scripts/n8n/validate_modern_n8n.py --workflows-dir workflows --fail-on-warnings
Exit 0 if OK, non-zero if violations found.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from typing import List

BANNED_SUBSTRINGS = [
    "@n8n/n8n-nodes-langchain",
    "community",
]

RECOMMENDED_NODE_HINTS = [
    "n8n-nodes-langchain.agent",   # Built-in Agent node family
    "n8n-nodes-base.ai",          # Placeholder hint: built-in AI nodes prefix
]


def scan_file(p: Path) -> List[str]:
    issues: List[str] = []
    try:
        text = p.read_text(encoding="utf-8")
        data = json.loads(text)
    except Exception as e:
        return [f"{p}: invalid JSON: {e}"]

    raw = json.dumps(data)
    for banned in BANNED_SUBSTRINGS:
        if banned in raw:
            issues.append(f"{p}: references banned pattern '{banned}'")

    # Optional hints for modernization
    # Not a hard error, but warn if no AI agent-like nodes exist.
    if not any(h in raw for h in RECOMMENDED_NODE_HINTS):
        issues.append(f"{p}: no modern AI Agent node hints detected (informational)")

    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflows-dir", default="workflows")
    ap.add_argument("--fail-on-warnings", action="store_true")
    args = ap.parse_args()

    wf_dir = Path(args.workflows_dir)
    if not wf_dir.exists():
        print(f"Workflows dir not found: {wf_dir}")
        sys.exit(1)

    errors: List[str] = []
    infos: List[str] = []

    for f in wf_dir.rglob("*.json"):
        issues = scan_file(f)
        for i in issues:
            if "banned pattern" in i:
                errors.append(i)
            else:
                infos.append(i)

    if infos:
        print("Info/Warnings:")
        for i in infos:
            print(f" - {i}")

    if errors or (infos and args.fail_on_warnings):
        if errors:
            print("Errors:")
            for e in errors:
                print(f" - {e}")
        sys.exit(1)

    print("Modern n8n validation passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
