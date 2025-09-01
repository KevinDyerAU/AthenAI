#!/usr/bin/env python3
import json
import sys
import os
import re

# Ensure project root is on sys.path so `api` package is importable
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.app import create_app

CRITICAL_PATHS = [
    # system
    "/api/system/health",
    "/api/system/status",
    "/api/system/health/deep",
    "/api/system/metrics",

    # tools
    "/api/tools/registry",

    # documents
    "/api/documents/enqueue",

    # auth
    "/api/auth/register",
    "/api/auth/login",
    "/api/auth/refresh",
    "/api/auth/me",
    "/api/auth/logout",

    # validation
    "/api/validation/run",
    "/api/validation/report/last",
    "/api/validation/history",
    "/api/validation/gates",

    # security
    "/api/security/compliance/assess",
    "/api/security/incidents",
    "/api/security/sandbox/policy",
    "/api/security/sandbox/evaluate",

    # workflows (check collection paths; item paths vary by parameterization)
    "/api/workflows",
    "/api/workflows/batch/run",

    # knowledge
    "/api/knowledge/query",
    "/api/knowledge/insert",

    # self_healing
    "/api/self_healing/analyze",
    "/api/self_healing/heal",

    # substrate (sample of key operations)
    "/api/substrate/entity",
    "/api/substrate/search/semantic",
]

# Regex patterns for dynamic paths (pattern-aware checks)
# These ensure that item-level endpoints exist without hardcoding example IDs.
CRITICAL_PATTERNS = [
    # workflows item endpoints
    r"^/api/workflows/[^/]+$",            # GET/PUT/DELETE item
    r"^/api/workflows/[^/]+/run$",        # run a workflow by id

    # substrate item-style endpoints
    r"^/api/substrate/entity/[^/]+$",     # update by entity_id (PUT)
    r"^/api/substrate/provenance/[^/]+$", # provenance by entity_id
    r"^/api/substrate/temporal/[^/]+$",   # temporal view by entity_id

    # knowledge relations item endpoint (rid = subject|predicate|object)
    r"^/api/knowledge/relations/[^/]+$",

    # security incident item endpoint
    r"^/api/security/incidents/[^/]+$",
]

def main() -> int:
    app = create_app()
    with app.test_client() as c:
        resp = c.get("/api/swagger.json")
        if resp.status_code != 200:
            print(f"ERROR: /api/swagger.json returned {resp.status_code}")
            return 1
        try:
            spec = resp.get_json()
        except Exception:
            spec = json.loads(resp.data.decode("utf-8"))
        paths = set((spec.get("paths") or {}).keys())
        # Some Swagger generators include the Api.prefix only in basePath, not in each path.
        # Normalize by accepting both with and without '/api' prefix.
        normalized = set(paths)
        for p in list(paths):
            if not p.startswith("/api"):
                normalized.add("/api" + p)
        missing = [p for p in CRITICAL_PATHS if p not in normalized]

        # Pattern-aware checks
        missing_patterns = []
        for pattern in CRITICAL_PATTERNS:
            regex = re.compile(pattern)
            if not any(regex.search(p) for p in normalized):
                missing_patterns.append(pattern)
        if missing or missing_patterns:
            print("ERROR: Missing critical paths in OpenAPI:")
            for p in missing:
                print(f" - {p}")
            if missing_patterns:
                print("ERROR: Missing pattern matches (no path matched these regex patterns):")
                for pat in missing_patterns:
                    print(f" - {pat}")
            return 2
        print("OpenAPI validation OK. Found critical paths:")
        for p in CRITICAL_PATHS:
            print(f" - {p}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
