import os
from pathlib import Path
from flask import Flask, jsonify, redirect, send_file
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
from .resources.documents import ns as documents_ns
from .resources.substrate import ns as substrate_ns
from .resources.autonomy import ns as autonomy_ns
from .resources.kg_drift import ns as kg_drift_ns
from .resources.self_healing import ns as self_healing_ns
from .resources import coordination
from .resources import validation
from .resources import security as security_resources
from .ws.events import register_socketio_events
from .utils.rabbitmq import ensure_coordination_bindings
from .errors import register_error_handlers
from .security.jwt_callbacks import register_jwt_callbacks
from .metrics import init_metrics
from .db_metrics import init_sqlalchemy_metrics
import logging
from .services.autonomy.agent_lifecycle_manager import AgentLifecycleManager


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Extensions
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    register_jwt_callbacks(jwt)
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}}, supports_credentials=True)

    # Metrics and logging
    init_metrics(app)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

    # Root landing page with links to ReDoc and Swagger UI
    @app.route("/")
    def index():
        return (
            """
            <!doctype html>
            <html>
              <head>
                <meta charset=\"utf-8\" />
                <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
                <title>NeoV3 API</title>
                <style>
                  body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif; margin: 2rem; }
                  a { color: #2563eb; text-decoration: none; }
                  .links a { display:block; margin: .5rem 0; }
                </style>
              </head>
              <body>
                <h1>NeoV3 API</h1>
                <p>Choose a documentation view:</p>
                <div class=\"links\">
                  <a href=\"/redoc\">ReDoc (recommended)</a>
                  <a href=\"/api/docs\">Swagger UI (/api/docs)</a>
                </div>
              </body>
            </html>
            """,
            200,
            {"Content-Type": "text/html; charset=utf-8"},
        )
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
    restx_api.add_namespace(autonomy_ns)
    restx_api.add_namespace(kg_drift_ns)
    restx_api.add_namespace(self_healing_ns, path="/self_healing")
    restx_api.add_namespace(coordination.ns, path="/coordination")
    restx_api.add_namespace(validation.ns, path="/validation")
    restx_api.add_namespace(security_resources.ns, path="/security")
    restx_api.add_namespace(documents_ns)

    # Socket.IO
    register_socketio_events(socketio)
    socketio.init_app(app, cors_allowed_origins=app.config.get("CORS_ORIGINS", "*"))

    # Error handlers
    register_error_handlers(app)

    # Optional local Redoc bundle path
    REDOC_LOCAL_PATH = Path(__file__).resolve().parent.parent / "documentation" / "api" / "vendor" / "redoc.standalone.js"

    # Serve local Redoc bundle if enabled and present
    @app.route("/assets/redoc.js")
    def redoc_js():
        if os.getenv("USE_LOCAL_REDOC", "false").lower() == "true" and REDOC_LOCAL_PATH.exists():
            return send_file(str(REDOC_LOCAL_PATH), mimetype="application/javascript")
        return jsonify({"error": "Local ReDoc not enabled or missing"}), 404

    # ReDoc documentation at /redoc (uses local bundle when enabled, else pinned CDN)
    @app.route("/redoc")
    def redoc():
        use_local = os.getenv("USE_LOCAL_REDOC", "false").lower() == "true" and REDOC_LOCAL_PATH.exists()
        script_src = "/assets/redoc.js" if use_local else "https://cdn.jsdelivr.net/npm/redoc@2.1.4/bundles/redoc.standalone.js"
        html = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset=\"utf-8\"/>
              <title>NeoV3 API – ReDoc</title>
              <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>
              <style> body {{ margin: 0; padding: 0; }} </style>
            </head>
            <body>
              <redoc spec-url='/api/swagger.json'></redoc>
              <script src=\"{script_src}\"></script>
            </body>
            </html>
        """
        return (html, 200, {"Content-Type": "text/html; charset=utf-8"})

    # DB create (dev only) and attach SQLAlchemy metrics listeners
    with app.app_context():
        # Attach query timing metrics
        init_sqlalchemy_metrics(db)
        if app.config.get("DB_AUTO_CREATE", False):
            db.create_all()

        # Initialize Lifecycle Manager singleton and optionally autostart
        lm = AgentLifecycleManager()
        app.extensions["lifecycle_manager"] = lm
        if os.getenv("LIFECYCLE_MANAGER_AUTOSTART", "false").lower() == "true":
            lm.start()

    # Best-effort broker setup
    try:
        ensure_coordination_bindings()
    except Exception:
        pass
    return app


if __name__ == "__main__":
    app = create_app()
    # Use gevent for WebSocket support
    socketio.run(app, host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", 8000)))
