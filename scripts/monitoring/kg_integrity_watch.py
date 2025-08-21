#!/usr/bin/env python3
"""
Periodic KG integrity monitor.

Runs lightweight checks against Neo4j using api.utils.kg_schema.monitor_consistency
and sends alerts via api.utils.alerts.send_alert when thresholds are exceeded.

Environment:
  INTERVAL_SECONDS=60 (poll interval)
  ALERT_WEBHOOK_URL=<http endpoint to receive alerts>
  ALERT_MIN_SEVERITY=warning (info|warning|error)
  THRESH_ORPHANS=0
  THRESH_CONTRADICTIONS=0
  THRESH_MISSING=0
  NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD (required)

Usage:
  python scripts/monitoring/kg_integrity_watch.py
"""
from __future__ import annotations
import os
import time
from typing import Any, Dict

# Ensure package import works when run from repo root
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from api.utils.kg_schema import monitor_consistency
from api.utils.alerts import send_alert

INTERVAL = int(os.getenv("INTERVAL_SECONDS", "60"))
THRESH_ORPHANS = int(os.getenv("THRESH_ORPHANS", "0"))
THRESH_CONTRADICTIONS = int(os.getenv("THRESH_CONTRADICTIONS", "0"))
THRESH_MISSING = int(os.getenv("THRESH_MISSING", "0"))


def check_once() -> Dict[str, Any]:
    data = monitor_consistency(limit=500)
    orphans = data.get("orphans", [])
    contradictions = data.get("contradictions", [])
    missing = data.get("missing_props", [])

    # Determine severity
    sev = "info"
    if (len(orphans) > THRESH_ORPHANS) or (len(contradictions) > THRESH_CONTRADICTIONS) or any(
        x.get("count", 0) > THRESH_MISSING for x in missing
    ):
        sev = "warning"
    if len(contradictions) > 5 * max(1, THRESH_CONTRADICTIONS):
        sev = "error"

    payload = {
        "orphans_count": len(orphans),
        "contradictions_count": len(contradictions),
        "missing_props": missing,
    }

    if sev != "info":
        send_alert("KG Integrity", payload, severity=sev)

    return {"severity": sev, **payload}


def main():
    print(f"[kg_integrity_watch] Starting with interval={INTERVAL}s")
    while True:
        try:
            res = check_once()
            print(f"[kg_integrity_watch] {res}")
        except Exception as e:
            # Do not crash the watcher; surface as error alert
            send_alert("KG Integrity Watcher Error", {"error": str(e)}, severity="error")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
