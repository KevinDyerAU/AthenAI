#!/usr/bin/env python3
"""
Build a Node-as-Tools registry for n8n.

This script inspects workflow JSON files (exported from n8n) and compiles a registry
of referenced nodes with semantic hints. Optionally, users can supply extra hints.

It does NOT call n8n APIs (keeps offline), but you can merge real metadata later.

Usage:
  python scripts/n8n/build_tools_registry.py --workflows-dir workflows --output workflows/tools_registry.json --extra-hints scripts/n8n/tool_hints.json
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Dict, Any, Set

DEFAULT_HINTS = {
    "n8n-nodes-base.httpRequest": {
        "category": "http",
        "description": "Perform HTTP requests to RESTful services. Useful for integrating external APIs.",
        "capabilities": ["GET", "POST", "PUT", "DELETE", "headers", "auth"],
    },
    "n8n-nodes-base.function": {
        "category": "code",
        "description": "Run small pieces of JavaScript to transform data.",
        "capabilities": ["transform", "map", "filter"],
    },
    "n8n-nodes-base.set": {
        "category": "data",
        "description": "Set, rename, or remove fields on items.",
        "capabilities": ["set", "rename", "remove"],
    },
    "n8n-nodes-base.start": {
        "category": "control",
        "description": "Start node marks workflow entry point.",
        "capabilities": ["trigger"],
    }
}


def node_key(node: Dict[str, Any]) -> str:
    # n8n uses 'type' as unique node key (e.g., n8n-nodes-base.httpRequest)
    return str(node.get("type", ""))


def collect_nodes(workflows_dir: Path) -> Set[str]:
    found: Set[str] = set()
    for p in workflows_dir.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        nodes = data.get("nodes") or []
        for n in nodes:
            t = node_key(n)
            if t:
                found.add(t)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflows-dir", default="workflows")
    ap.add_argument("--output", default="workflows/tools_registry.json")
    ap.add_argument("--extra-hints", help="Path to JSON with additional node hints", default=None)
    args = ap.parse_args()

    wf_dir = Path(args.workflows_dir)
    if not wf_dir.exists():
        raise SystemExit(f"Workflows dir not found: {wf_dir}")

    hints = dict(DEFAULT_HINTS)
    if args.extra_hints:
        extra_path = Path(args.extra_hints)
        if extra_path.exists():
            try:
                extra = json.loads(extra_path.read_text(encoding="utf-8"))
                hints.update(extra)
            except Exception as e:
                print(f"Warning: failed to load extra hints: {e}")

    node_types = collect_nodes(wf_dir)
    registry = {}
    for t in sorted(node_types):
        entry = hints.get(t, {
            "category": "unknown",
            "description": f"No hint for {t}. Provide one in extra-hints.",
            "capabilities": [],
        })
        registry[t] = entry

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(f"Wrote tools registry: {out_path} ({len(registry)} nodes)")


if __name__ == "__main__":
    main()
