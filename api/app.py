import os
from flask import Flask, jsonify
from flask_cors import CORS
from .config import get_config
from .extensions import db, ma, jwt, api as restx_api, socketio
from .resources.auth import ns as auth_ns
from .resources.agents import ns as agents_ns
from .resources.workflows import ns as workflows_ns
from .resources.system import ns as system_ns
from .resources.config_api import ns as config_ns
from .resources.tools import ns as tools_ns
from .resources.knowledge import ns as knowledge_ns
from .resources.conversations import ns as conversations_ns
from .resources.kg_admin import ns as kg_admin_ns
from .resources.kg_consensus import ns as kg_consensus_ns
from .resources.integrations import ns as integrations_ns
from .resources.substrate import ns as substrate_ns
from .ws.events import register_socketio_events
from .errors import register_error_handlers
from .security.jwt_callbacks import register_jwt_callbacks


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Extensions
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    register_jwt_callbacks(jwt)
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}}, supports_credentials=True)

    # Root route for convenience (register BEFORE RESTX so it takes precedence)
    @app.route("/")
    def index():
        return jsonify({
            "status": "ok",
            "message": "Enhanced AI Agent API",
            "endpoints": {
                "health": "/system/health",
                "auth": "/auth",
                "agents": "/agents",
                "workflows": "/workflows",
            }
        })
    # Note: Do not register an empty path ('') — Flask requires leading '/'

    # Back-compat health endpoint at root scope (RESTX is under /api now)
    @app.route("/system/health")
    def root_health():
        return jsonify({"status": "ok"})

    # RESTX API
    restx_api.init_app(app)
    restx_api.add_namespace(auth_ns)
    restx_api.add_namespace(agents_ns)
    restx_api.add_namespace(workflows_ns)
    restx_api.add_namespace(system_ns)
    restx_api.add_namespace(config_ns)
    restx_api.add_namespace(tools_ns)
    restx_api.add_namespace(knowledge_ns)
    restx_api.add_namespace(conversations_ns)
    restx_api.add_namespace(kg_admin_ns)
    restx_api.add_namespace(kg_consensus_ns)
    restx_api.add_namespace(integrations_ns)
    restx_api.add_namespace(substrate_ns)

    # Socket.IO
    register_socketio_events(socketio)
    socketio.init_app(app, cors_allowed_origins=app.config.get("CORS_ORIGINS", "*"))

    # Error handlers
    register_error_handlers(app)

    # DB create (dev only)
    with app.app_context():
        if app.config.get("DB_AUTO_CREATE", False):
            db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    # Use gevent for WebSocket support
    socketio.run(app, host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", 8000)))
