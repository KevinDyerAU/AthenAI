from __future__ import annotations
from typing import Any, Dict
import os

DEFAULTS = {
    "cpu_quota": 0.5,           # cores
    "memory_mb": 512,          # MiB
    "network": "isolated",    # isolated|limited|open
    "filesystem": "ro",       # ro|rw
}

class SandboxService:
    def __init__(self) -> None:
        pass

    def current_policy(self) -> Dict[str, Any]:
        # Read overrides from env for simplicity; in production, source from policy store
        return {
            "cpu_quota": float(os.getenv("AGENT_CPU_QUOTA", DEFAULTS["cpu_quota"])),
            "memory_mb": int(os.getenv("AGENT_MEMORY_MB", DEFAULTS["memory_mb"])),
            "network": os.getenv("AGENT_NETWORK_MODE", DEFAULTS["network"]),
            "filesystem": os.getenv("AGENT_FS_MODE", DEFAULTS["filesystem"]),
            "dynamic": os.getenv("AGENT_DYNAMIC_ISOLATION", "false").lower() == "true",
        }

    def evaluate(self, risk_score: float) -> Dict[str, Any]:
        # Dynamically tighten isolation based on risk score (0..1)
        base = self.current_policy()
        if risk_score >= 0.8:
            base.update({"cpu_quota": min(base["cpu_quota"], 0.25), "network": "isolated", "filesystem": "ro"})
        elif risk_score >= 0.5:
            base.update({"cpu_quota": min(base["cpu_quota"], 0.4), "network": "limited"})
        return base
