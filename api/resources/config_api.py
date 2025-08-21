import os
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

ns = Namespace("config", description="Configuration management endpoints")

env_get_model = ns.model("EnvGet", {
    "variables": fields.Raw,
})

env_set_model = ns.model("EnvSet", {
    "key": fields.String(required=True),
    "value": fields.String(required=True),
})

config_get_model = ns.model("ConfigGet", {
    "config": fields.Raw,
})


SAFE_ENV_PREFIXES = ("NEO", "N8N_", "APP_", "CORS_", "DATABASE", "JWT_", "FLASK_")


def _require_admin():
    ident = get_jwt_identity()
    if not isinstance(ident, dict) or ident.get("role") != "admin":
        ns.abort(403, "Admin privileges required")


@ns.route("/env")
class Env(Resource):
    @jwt_required()
    @ns.marshal_with(env_get_model)
    def get(self):
        # Return only safe environment variables
        safe = {k: v for k, v in os.environ.items() if k.startswith(SAFE_ENV_PREFIXES)}
        return {"variables": safe}

    @jwt_required()
    @ns.expect(env_set_model, validate=True)
    def post(self):
        _require_admin()
        payload = request.get_json() or {}
        key = payload.get("key")
        value = payload.get("value")
        if not key or not isinstance(key, str):
            ns.abort(400, "Invalid key")
        # Set for current process; persist via deployment tooling outside runtime
        os.environ[key] = str(value)
        return {"message": "Environment variable set", "key": key}


@ns.route("/service")
class ServiceConfig(Resource):
    @jwt_required()
    @ns.marshal_with(config_get_model)
    def get(self):
        # Limited view of Flask config for safety
        from flask import current_app
        cfg = {k: v for k, v in current_app.config.items() if k in [
            "CORS_ORIGINS", "SQLALCHEMY_DATABASE_URI", "N8N_BASE_URL", "NEO4J_URI"
        ]}
        return {"config": cfg}

    @jwt_required()
    def put(self):
        _require_admin()
        from flask import current_app
        payload = request.get_json() or {}
        allowed = {"CORS_ORIGINS", "N8N_BASE_URL"}
        updated = {}
        for k, v in payload.items():
            if k in allowed:
                current_app.config[k] = v
                updated[k] = v
        return {"message": "Service configuration updated", "updated": updated}
