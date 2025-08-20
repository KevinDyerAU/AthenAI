#!/usr/bin/env python3
import os
import sys
import json
import base64
import urllib.request

BASE = os.getenv("N8N_BASE_URL", "http://localhost:5678").rstrip("/")
API_KEY = os.getenv("N8N_API_KEY")
BASIC_USER = os.getenv("N8N_USER")
BASIC_PASS = os.getenv("N8N_PASS")


def _auth_headers():
    hdrs = {"Content-Type": "application/json"}
    if API_KEY:
        hdrs["X-N8N-API-KEY"] = API_KEY
    elif BASIC_USER and BASIC_PASS:
        token = base64.b64encode(f"{BASIC_USER}:{BASIC_PASS}".encode()).decode()
        hdrs["Authorization"] = f"Basic {token}"
    return hdrs


def get_workflows():
    url = f"{BASE}/rest/workflows"
    req = urllib.request.Request(url, headers=_auth_headers(), method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def planning_agent():
    url = f"{BASE}/webhook/planning-agent"
    payload = {
        "project": {"name": "Website Revamp", "methodology": "agile"},
        "tasks": [{"id": "T1", "skills": ["design"]}],
        "resources": [{"name": "Alice", "skills": ["design"], "capacity": 2}],
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if action == "list":
        print(json.dumps(get_workflows(), indent=2))
    else:
        print(json.dumps(planning_agent(), indent=2))
