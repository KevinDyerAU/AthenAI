#!/usr/bin/env python3
from __future__ import annotations
import os
import sys
import json

# Ensure API package on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from api.services.validation import ValidationService  # noqa: E402


def main() -> int:
    # Make CI runs tolerant of missing DB/MQ
    os.environ.setdefault("VALIDATION_PERSIST_DISABLED", "true")

    cfg = {
        "unit_selectors": ["tests/api"],
        "integration_scenarios": ["tests/api"],
        "include_performance": False if os.environ.get("DISABLE_PERF", "false").lower() == "true" else True,
        "include_behavior": True,
        # Optionally specify a k6 script path via env K6_SCRIPT
        "load_profile": {
            "rps": int(os.environ.get("K6_RPS", "50")),
            "duration_s": int(os.environ.get("K6_DURATION", "10")),
            "vus": int(os.environ.get("K6_VUS", "10")),
            "k6_script": os.environ.get("K6_SCRIPT", "") or None,
        },
        # Optional behavior suites: comma-separated module:function entries
    }
    suites_env = os.environ.get("BEHAVIOR_SUITES")
    if suites_env:
        cfg["behavior_suites"] = [s.strip() for s in suites_env.split(",") if s.strip()]

    svc = ValidationService()
    res = svc.run_all(cfg)
    print(json.dumps(res, indent=2))
    ok = bool(res.get("gate", {}).get("ok"))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
