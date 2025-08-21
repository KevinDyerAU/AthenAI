#!/usr/bin/env python3
"""
Simple integration tests that exercise the API similarly to n8n real workflows.
Requires environment variable API_BASE_URL (e.g., http://localhost:8000).

Run:
  python tests/integration/api_flows_test.py
Exit non-zero on failure.
"""
from __future__ import annotations
import os
import sys
import time
import json
import random
import string
import requests

BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 15


def unique_email(prefix: str) -> str:
    ts = int(time.time())
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{prefix}+{ts}{rand}@example.com"


def expect(cond: bool, msg: str):
    if not cond:
        raise AssertionError(msg)


def post(url: str, json_body: dict, headers: dict | None = None):
    r = requests.post(url, json=json_body, headers=headers or {}, timeout=TIMEOUT)
    return r


def get(url: str, headers: dict | None = None):
    r = requests.get(url, headers=headers or {}, timeout=TIMEOUT)
    return r


def test_health():
    r = get(f"{BASE}/system/health")
    expect(r.status_code == 200, f"health status {r.status_code}")
    data = r.json()
    expect(data.get("status") == "ok", "health not ok")


def test_agent_execute_flow():
    # Register (ignore 409)
    email = unique_email("agent")
    post(f"{BASE}/auth/register", {"email": email, "password": "Test1234!"})

    # Login
    r = post(f"{BASE}/auth/login", {"email": email, "password": "Test1234!"})
    expect(r.status_code == 200, f"login failed: {r.text}")
    tokens = r.json()
    access = tokens.get("access_token")
    expect(bool(access), "missing access token")
    auth = {"Authorization": f"Bearer {access}"}

    # Create agent
    r = post(f"{BASE}/agents", {"name": f"agent-{int(time.time())}", "type": "analysis"}, headers=auth)
    expect(r.status_code in (201, 409), f"create agent failed: {r.status_code} {r.text}")
    agent = r.json() if r.status_code == 201 else None
    agent_id = agent.get("id") if agent else None
    if not agent_id:
        # fallback: list and pick first
        lr = get(f"{BASE}/agents", headers=auth)
        expect(lr.status_code == 200, f"list agents failed: {lr.text}")
        items = lr.json().get("items", [])
        expect(len(items) > 0, "no agents available")
        agent_id = items[0]["id"]

    # Execute agent
    r = post(f"{BASE}/agents/{agent_id}/execute", {}, headers=auth)
    expect(r.status_code in (200, 202), f"execute agent failed: {r.status_code} {r.text}")


def test_workflow_create_run():
    # Register (ignore 409)
    email = unique_email("workflow")
    post(f"{BASE}/auth/register", {"email": email, "password": "Test1234!"})

    # Login
    r = post(f"{BASE}/auth/login", {"email": email, "password": "Test1234!"})
    expect(r.status_code == 200, f"login failed: {r.text}")
    tokens = r.json()
    access = tokens.get("access_token")
    expect(bool(access), "missing access token")
    auth = {"Authorization": f"Bearer {access}"}

    # Create workflow
    name = f"wf-{int(time.time())}"
    definition = {"steps": [{"id": 1, "op": "noop"}]}
    r = post(f"{BASE}/workflows", {"name": name, "definition": definition}, headers=auth)
    expect(r.status_code in (201, 409), f"create workflow failed: {r.status_code} {r.text}")
    wf = r.json() if r.status_code == 201 else None
    wf_id = wf.get("id") if wf else None
    if not wf_id:
        # fallback: list and find by name or take latest
        lr = get(f"{BASE}/workflows", headers=auth)
        expect(lr.status_code == 200, f"list workflows failed: {lr.text}")
        items = lr.json().get("items", [])
        expect(len(items) > 0, "no workflows available")
        wf_id = items[0]["id"]

    # Run workflow
    r = post(f"{BASE}/workflows/{wf_id}/run", {}, headers=auth)
    expect(r.status_code in (200, 202), f"run workflow failed: {r.status_code} {r.text}")


if __name__ == "__main__":
    try:
        test_health()
        test_agent_execute_flow()
        test_workflow_create_run()
    except Exception as e:
        print(f"INTEGRATION TEST FAILED: {e}")
        sys.exit(1)
    print("INTEGRATION TESTS PASSED")
    sys.exit(0)
