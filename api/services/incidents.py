from __future__ import annotations
import os
import time
import uuid
from typing import Any, Dict, List, Optional
from ..utils.neo4j_client import get_client
from ..utils.audit import audit_event

class IncidentService:
    def __init__(self) -> None:
        pass

    def record(self, kind: str, severity: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        item = {
            "id": str(uuid.uuid4()),
            "kind": kind,
            "severity": severity,
            "message": message,
            "context": context or {},
            "at": int(time.time() * 1000),
        }
        audit_event("security.incident.recorded", item, None)
        if os.getenv("INCIDENT_PERSIST_DISABLED", "false").lower() != "true":
            try:
                q = (
                    "CREATE (i:SecurityIncident {id:$id, kind:$kind, severity:$sev, message:$msg, context:$ctx, at:$at}) RETURN i"
                )
                get_client().run_query(q, {"id": item["id"], "kind": kind, "sev": severity, "msg": message, "ctx": item["context"], "at": item["at"]})
            except Exception:
                pass
        return item

    def list(self, limit: int = 50, kind: Optional[str] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        if os.getenv("INCIDENT_PERSIST_DISABLED", "false").lower() == "true":
            return []
        try:
            where = []
            params: Dict[str, Any] = {"lim": int(max(1, min(limit, 200)))}
            if kind:
                where.append("i.kind = $kind"); params["kind"] = kind
            if severity:
                where.append("i.severity = $sev"); params["sev"] = severity
            q = "MATCH (i:SecurityIncident) " + ("WHERE " + " AND ".join(where) + " " if where else "") + "RETURN i ORDER BY i.at DESC LIMIT $lim"
            rows = get_client().run_query(q, params)
            out: List[Dict[str, Any]] = []
            for r in rows:
                i = r.get("i", {})
                out.append({
                    "id": i.get("id"),
                    "kind": i.get("kind"),
                    "severity": i.get("severity"),
                    "message": i.get("message"),
                    "context": i.get("context"),
                    "at": i.get("at"),
                })
            return out
        except Exception:
            return []
