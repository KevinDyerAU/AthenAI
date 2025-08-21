import os
import requests
from typing import Any, Dict

BASE_URL = os.getenv("N8N_BASE_URL", "http://localhost:5678")
API_KEY = os.getenv("N8N_API_KEY")
TIMEOUT = int(os.getenv("N8N_HTTP_TIMEOUT", "10"))


def _headers() -> Dict[str, str]:
    h: Dict[str, str] = {"Content-Type": "application/json"}
    if API_KEY:
        h["X-N8N-API-KEY"] = API_KEY
    return h


def trigger_webhook(path: str, payload: Dict[str, Any]) -> requests.Response:
    """Trigger an n8n webhook (path without leading slash is fine). E.g., 'webhook/agent-execute'."""
    url = f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    resp = requests.post(url, json=payload, headers=_headers(), timeout=TIMEOUT)
    resp.raise_for_status()
    return resp
