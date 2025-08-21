#!/usr/bin/env python3
"""
verify_content.py

Validates repository content presence and basic functionality across:
- scripts (backup, maintenance, monitoring, security, setup, testing, utilities)
- documentation (api, configuration, developer-guides, monitoring, operations, testing, workflows)
- tests (ai-capabilities, e2e, integration, performance, unit, workflows)
- workflows (analysis-tools, communication-tools, creative-tools, development-tools, execution-tools, planning-tools, qa-tools, research-tools)

Usage:
  python scripts/verification/verify_content.py --level basic
Exit code 0 on success, non-zero on issues.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[2]

EXPECTED = {
    "scripts": [
        "backup", "maintenance", "monitoring", "security", "setup", "testing", "utilities"
    ],
    "documentation": [
        "api", "configuration", "developer-guides", "monitoring", "operations", "testing", "workflows"
    ],
    "tests": [
        "ai-capabilities", "e2e", "integration", "performance", "unit", "workflows"
    ],
    "workflows": [
        "analysis-tools", "communication-tools", "creative-tools", "development-tools",
        "execution-tools", "planning-tools", "qa-tools", "research-tools"
    ],
}

DOC_MIN_FILES = {
    "configuration": ["ENVIRONMENT_CONFIG.md"],
}


def check_dir_exists(base: Path, required: List[str]) -> Tuple[List[str], List[str]]:
    missing = []
    present = []
    for name in required:
        p = base / name
        if not p.exists():
            missing.append(str(p))
        else:
            present.append(str(p))
    return present, missing


def has_any_files(p: Path, exts: List[str] | None = None) -> bool:
    if not p.exists():
        return False
    for root, _, files in os.walk(p):
        for f in files:
            if not exts or any(f.lower().endswith(e) for e in exts):
                return True
    return False


def check_scripts(base: Path) -> List[str]:
    issues: List[str] = []
    for cat in EXPECTED["scripts"]:
        d = base / cat
        if not d.exists():
            issues.append(f"Missing scripts category: {d}")
            continue
        if not has_any_files(d, exts=[".sh", ".ps1"]):
            issues.append(f"No scripts found in {d}")
    return issues


def check_docs(base: Path) -> List[str]:
    issues: List[str] = []
    for cat in EXPECTED["documentation"]:
        d = base / cat
        if not d.exists():
            issues.append(f"Missing documentation category: {d}")
            continue
        if not has_any_files(d, exts=[".md"]):
            issues.append(f"No markdown docs found in {d}")
        # Required files per category
        req = DOC_MIN_FILES.get(cat, [])
        for f in req:
            if not (d / f).exists():
                issues.append(f"Missing required doc file: {(d / f)}")
    return issues


def check_tests(base: Path) -> List[str]:
    issues: List[str] = []
    for cat in EXPECTED["tests"]:
        d = base / cat
        if not d.exists():
            issues.append(f"Missing tests category: {d}")
            continue
        if not has_any_files(d, exts=[".sh", ".ps1", ".py", ".js"]):
            issues.append(f"No test files found in {d}")
    return issues


def check_workflows(base: Path) -> List[str]:
    issues: List[str] = []
    for cat in EXPECTED["workflows"]:
        d = base / cat
        if not d.exists():
            issues.append(f"Missing workflows category: {d}")
            continue
        # At minimum, a README.md or a .json workflow
        if not has_any_files(d, exts=[".md", ".json"]):
            issues.append(f"No workflows or docs found in {d}")
        # n8n JSON validity (basic): ensure any .json file parses
        for wf in d.glob("**/*.json"):
            try:
                json.loads(wf.read_text(encoding="utf-8"))
            except Exception as e:
                issues.append(f"Invalid JSON in workflow: {wf}: {e}")
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["basic", "strict"], default="basic")
    args = parser.parse_args()

    issues: List[str] = []

    scripts_dir = ROOT / "scripts"
    docs_dir = ROOT / "documentation"
    tests_dir = ROOT / "tests"
    workflows_dir = ROOT / "workflows"

    # Ensure base directories exist
    for name, path in [("scripts", scripts_dir), ("documentation", docs_dir), ("tests", tests_dir), ("workflows", workflows_dir)]:
        if not path.exists():
            issues.append(f"Missing top-level directory: {name} -> {path}")

    # Detailed checks
    issues += check_scripts(scripts_dir)
    issues += check_docs(docs_dir)
    issues += check_tests(tests_dir)
    issues += check_workflows(workflows_dir)

    if issues:
        print("Content verification FAILED:\n")
        for i in issues:
            print(f" - {i}")
        raise SystemExit(1)

    print("Content verification PASSED: all required components present.")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
