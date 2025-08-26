from __future__ import annotations
import os
import yaml
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set

POLICY_PATH = os.getenv("RBAC_POLICY_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                                         "infrastructure", "security", "rbac", "policies.yaml"))

class Policy:
    def __init__(self, data: Dict[str, Any]):
        self.roles = {r["name"]: r for r in data.get("roles", [])}

    def allowed(self, roles: Set[str], resource: str, action: str, attributes: Optional[Dict[str, Any]] = None) -> bool:
        # Simple RBAC allow with wildcard support; ABAC hook via attributes placeholder
        for role in roles:
            r = self.roles.get(role)
            if not r:
                continue
            for rule in r.get("allow", []):
                res = rule.get("resource", "")
                acts = set(rule.get("actions", []))
                if (res == "*" or res == resource) and ("*" in acts or action in acts):
                    # ABAC: evaluate conditions if present
                    cond = rule.get("when")
                    if cond and not self._eval_condition(cond, attributes or {}):
                        continue
                    return True
        return False

    def _eval_condition(self, cond: Dict[str, Any], attrs: Dict[str, Any]) -> bool:
        """
        Evaluate ABAC condition grammar with logical operators and common comparators.
        Supported forms:
          - {"equals": {"key": "env", "value": "prod"}}
          - {"not_equals": {"key": "dataset_classification", "value": "restricted"}}
          - {"in": {"key": "dataset_classification", "values": ["public", "internal"]}}
          - {"not_in": {"key": "actor_org", "values": ["ext"]}}
          - {"contains": {"key": "scopes", "value": "security:read"}}
          - {"gt"|"gte"|"lt"|"lte": {"key": "risk", "value": 0.8}}
          - {"and": [ ... ]}, {"or": [ ... ]}, {"not": { ... }}
        """
        try:
            if "and" in cond:
                return all(self._eval_condition(c, attrs) for c in cond.get("and", []))
            if "or" in cond:
                arr = cond.get("or", [])
                return any(self._eval_condition(c, attrs) for c in arr) if arr else False
            if "not" in cond:
                return not self._eval_condition(cond.get("not") or {}, attrs)

            def getv(key: str):
                return attrs.get(key)

            if "equals" in cond:
                c = cond["equals"]; return getv(c.get("key")) == c.get("value")
            if "not_equals" in cond:
                c = cond["not_equals"]; return getv(c.get("key")) != c.get("value")
            if "in" in cond:
                c = cond["in"]; vals = c.get("values", [])
                return getv(c.get("key")) in vals
            if "not_in" in cond:
                c = cond["not_in"]; vals = c.get("values", [])
                return getv(c.get("key")) not in vals
            if "contains" in cond:
                c = cond["contains"]
                v = getv(c.get("key"))
                if isinstance(v, (list, set, tuple)):
                    return c.get("value") in v
                if isinstance(v, str):
                    return str(c.get("value")) in v
                return False
            if "gt" in cond:
                c = cond["gt"]; v = getv(c.get("key"))
                return (v is not None) and (float(v) > float(c.get("value")))
            if "gte" in cond:
                c = cond["gte"]; v = getv(c.get("key"))
                return (v is not None) and (float(v) >= float(c.get("value")))
            if "lt" in cond:
                c = cond["lt"]; v = getv(c.get("key"))
                return (v is not None) and (float(v) < float(c.get("value")))
            if "lte" in cond:
                c = cond["lte"]; v = getv(c.get("key"))
                return (v is not None) and (float(v) <= float(c.get("value")))
        except Exception:
            return False
        return False

@lru_cache(maxsize=1)
def load_policy() -> Policy:
    try:
        with open(POLICY_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Policy(data)
    except Exception:
        return Policy({"roles": []})


def get_user_roles(identity: Any) -> Set[str]:
    # Identity can be a dict or string. Expect roles in identity["roles"] or comma-separated in identity["role"]
    roles: Set[str] = set()
    if isinstance(identity, dict):
        r = identity.get("roles") or identity.get("role")
        if isinstance(r, list):
            roles.update([str(x) for x in r])
        elif isinstance(r, str):
            roles.update([x.strip() for x in r.split(",") if x.strip()])
    return roles
