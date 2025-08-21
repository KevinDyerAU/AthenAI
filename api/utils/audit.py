import json
import os
import time
from typing import Any, Dict

_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "./audit.log")


def audit_event(event: str, data: Dict[str, Any] | None = None, user: Any | None = None) -> None:
    try:
        rec = {
            "ts": int(time.time() * 1000),
            "event": event,
            "user": user if isinstance(user, dict) else {"id": user} if user is not None else None,
            "data": data or {},
        }
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        # Never block on audit failures
        pass
