import os
import json
from typing import Any, Dict

import requests

ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL")
ALERT_MIN_SEVERITY = os.getenv("ALERT_MIN_SEVERITY", "info")  # info|warning|error


def _should_send(severity: str) -> bool:
    order = {"info": 0, "warning": 1, "error": 2}
    return order.get(severity, 0) >= order.get(ALERT_MIN_SEVERITY, 0)


def send_alert(title: str, payload: Dict[str, Any], severity: str = "warning") -> None:
    if not ALERT_WEBHOOK_URL or not _should_send(severity):
        return
    try:
        requests.post(
            ALERT_WEBHOOK_URL,
            data=json.dumps({"title": title, "severity": severity, "payload": payload}),
            headers={"Content-Type": "application/json"},
            timeout=8,
        )
    except Exception:
        # Never raise on alerting failures
        pass
