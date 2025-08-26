from __future__ import annotations
import os
import time
import uuid
from typing import Any, Dict
from ..utils.neo4j_client import get_client
from ..security.policy import load_policy

class ComplianceService:
    def __init__(self) -> None:
        pass

    def assess(self) -> Dict[str, Any]:
        checks: Dict[str, Any] = {}
        # JWT configured
        checks["jwt_configured"] = bool(os.getenv("JWT_SECRET_KEY"))
        # RBAC policy loadable
        try:
            pol = load_policy()
            checks["rbac_policy_loaded"] = bool(pol.roles)
        except Exception:
            checks["rbac_policy_loaded"] = False
        # TLS hint (reverse proxy typically)
        checks["tls_enabled_hint"] = os.getenv("FORCE_TLS", "false").lower() == "true"
        # Data protection hints
        checks["data_encryption_at_rest_hint"] = os.getenv("ENCRYPTION_AT_REST", "false").lower() == "true"
        checks["data_encryption_in_transit_hint"] = os.getenv("TLS_TERMINATION", "false").lower() == "true"
        # Key rotation policy present (env flag)
        checks["key_rotation_policy"] = os.getenv("KEY_ROTATION_DAYS") is not None
        # Audit logging enabled (env flag or default path configured)
        checks["audit_logging_enabled"] = bool(os.getenv("AUDIT_LOG_PATH", ""))
        # Compute overall
        ok = all([checks["jwt_configured"], checks["rbac_policy_loaded"], checks["audit_logging_enabled"]])
        return {"ok": ok, "checks": checks, "at": int(time.time() * 1000)}

    def persist_report(self, report: Dict[str, Any]) -> None:
        if os.getenv("COMPLIANCE_PERSIST_DISABLED", "false").lower() == "true":
            return
        try:
            q = (
                "CREATE (r:ComplianceReport {id: $id, ok: $ok, at: $at, checks: $checks}) RETURN r"
            )
            get_client().run_query(q, {"id": str(uuid.uuid4()), "ok": bool(report.get("ok")), "at": int(report.get("at")), "checks": report.get("checks")})
        except Exception:
            pass
