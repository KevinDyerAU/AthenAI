from __future__ import annotations
from functools import wraps
from typing import Callable
from flask import request
from flask_restx import abort
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from .policy import load_policy, get_user_roles


def require_permission(resource: str, action: str):
    """
    Decorator to enforce RBAC/ABAC permissions using loaded policy.
    Reads roles from JWT identity (if present). Anonymous users have no roles.
    """
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # In JWT-Extended v4+, use verify_jwt_in_request(optional=True) to allow anonymous access
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            roles = get_user_roles(identity)
            attrs = {
                "method": request.method,
                "path": request.path,
                "ip": request.remote_addr,
                "env": request.headers.get("X-Env") or None,
            }
            if not load_policy().allowed(roles, resource=resource, action=action, attributes=attrs):
                abort(403, "forbidden")
            return f(*args, **kwargs)
        return wrapper
    return decorator
