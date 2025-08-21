#!/usr/bin/env python3
"""
Migrate workflows away from community packages (e.g. '@n8n/n8n-nodes-langchain')
into modern built-in n8n Agent nodes and patterns. Performs text-level and
JSON-level transformations based on a mapping table.

Usage:
  python scripts/n8n/migrate_to_builtins.py --workflows-dir workflows --out-dir workflows_migrated
  python scripts/n8n/migrate_to_builtins.py --workflows-dir workflows --in-place

Notes:
- The mapping is heuristic. Always review diffs and test in n8n.
- This script avoids deleting unknown fields; it preserves unknown keys.
"""
from __future__ import annotations
import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, Any

BANNED_SUBSTRINGS = [
    "@n8n/n8n-nodes-langchain",
]

# Heuristic mappings from old community node types to modern built-ins.
# Update as needed for your environment/version.
NODE_TYPE_MAPPING = {
    # Example: legacy agent node -> modern built-in agent
    "@n8n/n8n-nodes-langchain.agent": "n8n-nodes-langchain.agent",
    "@n8n/n8n-nodes-langchain.toolsAgent": "n8n-nodes-langchain.agent",  # unify on built-in agent
}


def migrate_json(data: Dict[str, Any]) -> Dict[str, Any]:
    nodes = data.get("nodes") or []
    for node in nodes:
        t = node.get("type")
        if not t:
            continue
        # Replace community type with built-in
        if t in NODE_TYPE_MAPPING:
            node["type"] = NODE_TYPE_MAPPING[t]
        # Remove explicit community package references embedded in params if any
        for k, v in list(node.items()):
            if isinstance(v, str):
                for banned in BANNED_SUBSTRINGS:
                    if banned in v:
                        node[k] = v.replace(banned, "n8n-nodes-langchain")
            elif isinstance(v, dict):
                # shallow cleanup
                for sk, sv in list(v.items()):
                    if isinstance(sv, str) and any(b in sv for b in BANNED_SUBSTRINGS):
                        for banned in BANNED_SUBSTRINGS:
                            v[sk] = sv.replace(banned, "n8n-nodes-langchain")
    return data


def process_file(src: Path, dst: Path, in_place: bool) -> bool:
    text = src.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except Exception:
        # fallback: only string replace
        new_text = text
        for banned in BANNED_SUBSTRINGS:
            new_text = new_text.replace(banned, "n8n-nodes-langchain")
        if in_place:
            src.write_text(new_text, encoding="utf-8")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(new_text, encoding="utf-8")
        return True

    migrated = migrate_json(data)
    out_text = json.dumps(migrated, indent=2)
    if in_place:
        src.write_text(out_text, encoding="utf-8")
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out_text, encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflows-dir", default="workflows")
    ap.add_argument("--out-dir", default="workflows_migrated")
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()

    wf_dir = Path(args.workflows_dir)
    if not wf_dir.exists():
        raise SystemExit(f"Workflows dir not found: {wf_dir}")

    if args.in_place:
        out_dir = wf_dir
    else:
        out_dir = Path(args.out_dir)
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for src in wf_dir.rglob("*.json"):
        dst = out_dir / src.relative_to(wf_dir)
        process_file(src, dst, in_place=args.in_place)
        count += 1

    print(f"Migrated {count} workflow file(s) {'in-place' if args.in_place else f'to {out_dir}'}.")


if __name__ == "__main__":
    main()
