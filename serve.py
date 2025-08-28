#!/usr/bin/env python3
"""
NeoV3 - Simple local server for index.html

- Serves index.html from repo root with environment-driven port substitution.
- Reads process environment first, then falls back to .env file (if present),
  then to hardcoded defaults that match docker-compose.yml.

Usage:
  python serve.py            # serves on http://localhost:8088
  SERVE_PORT=8080 python serve.py

Environment keys (examples):
  API_PORT=8000
  N8N_PORT=5678
  GRAFANA_PORT=3000
  PROMETHEUS_PORT=9090
  ALERTMANAGER_PORT=9093
  LOKI_PORT=3100
  RABBITMQ_MGMT_PORT=15672
  NEO4J_HTTP_PORT=7474

This does NOT require external packages.
"""
from __future__ import annotations

import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parent
INDEX_FILE = REPO_ROOT / "index.html"
ENV_FILE = REPO_ROOT / ".env"

# Placeholder tokens inside index.html
TOKENS = [
    "__API_PORT__",
    "__N8N_PORT__",
    "__GRAFANA_PORT__",
    "__PROMETHEUS_PORT__",
    "__ALERTMANAGER_PORT__",
    "__LOKI_PORT__",
    "__RABBITMQ_MGMT_PORT__",
    "__NEO4J_HTTP_PORT__",
]

# Defaults aligned with docker-compose.yml typical mappings
DEFAULTS = {
    "API_PORT": "8000",
    "N8N_PORT": "5678",
    "GRAFANA_PORT": "3000",
    "PROMETHEUS_PORT": "9090",
    "ALERTMANAGER_PORT": "9093",
    "LOKI_PORT": "3100",
    "RABBITMQ_MGMT_PORT": "15672",
    "NEO4J_HTTP_PORT": "7474",
}


def parse_env_file(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not path.exists():
        return data
    try:
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            # allow simple KEY=VALUE without export
            if line.startswith("export "):
                line = line[len("export "):]
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('\"').strip("'")
            if k:
                data[k] = v
    except Exception:
        pass
    return data


def build_context() -> Dict[str, str]:
    ctx = {}
    env_file_vals = parse_env_file(ENV_FILE)

    def get(name: str) -> str:
        # Priority: process env -> .env -> default
        return os.environ.get(name) or env_file_vals.get(name) or DEFAULTS.get(name, "")

    # Map placeholders to resolved values
    ctx["__API_PORT__"] = get("API_HOST_PORT") or get("API_PORT")  # allow either
    ctx["__N8N_PORT__"] = get("N8N_PORT")
    ctx["__GRAFANA_PORT__"] = get("GRAFANA_PORT")
    ctx["__PROMETHEUS_PORT__"] = get("PROMETHEUS_PORT")
    ctx["__ALERTMANAGER_PORT__"] = get("ALERTMANAGER_PORT")
    ctx["__LOKI_PORT__"] = get("LOKI_PORT")
    ctx["__RABBITMQ_MGMT_PORT__"] = get("RABBITMQ_MGMT_PORT") or get("RABBITMQ_MANAGEMENT_PORT")
    ctx["__NEO4J_HTTP_PORT__"] = get("NEO4J_HTTP_PORT") or get("NEO4J_PORT_HTTP") or get("NEO4J_PORT")

    # Ensure none left empty; backfill with defaults as last resort
    for token in TOKENS:
        if not ctx.get(token):
            # Strip __ and __ then append _PORT to find a matching default
            # but default mapping is already exhaustive; just set to '0' if somehow missing
            ctx[token] = "0"
    return ctx


class IndexHandler(SimpleHTTPRequestHandler):
    def _write(self, content: bytes, status: int = 200, ctype: str = "text/html; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):  # noqa: N802 (http-server naming)
        # Serve processed index with token substitution
        if self.path in ("/", "/index.html"):
            if not INDEX_FILE.exists():
                self._write(b"index.html not found", status=404, ctype="text/plain; charset=utf-8")
                return
            try:
                raw = INDEX_FILE.read_text(encoding="utf-8")
                ctx = build_context()
                processed = raw
                for token, val in ctx.items():
                    processed = processed.replace(token, str(val))
                self._write(processed.encode("utf-8"))
                return
            except Exception as exc:  # pragma: no cover
                self._write(f"Error rendering index: {exc}".encode("utf-8"), status=500, ctype="text/plain; charset=utf-8")
                return
        # Otherwise, fall back to normal static serving
        return super().do_GET()


def main() -> int:
    host = os.environ.get("SERVE_HOST", "0.0.0.0")
    try:
        port = int(os.environ.get("SERVE_PORT", "8088"))
    except ValueError:
        port = 8088

    os.chdir(REPO_ROOT)
    httpd = ThreadingHTTPServer((host, port), IndexHandler)

    print("\nNeoV3 Local Portal Server")
    print(f"Serving index.html at http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print("Port mapping (env -> effective):")
    ctx = build_context()
    for k, v in ctx.items():
        print(f"  {k} = {v}")
    print("\nCTRL+C to stop\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
