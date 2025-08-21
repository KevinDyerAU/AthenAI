import json
import os
from pathlib import Path
from flask import Response
from flask_restx import Namespace, Resource

ns = Namespace("tools", description="Tools registry endpoints for n8n agents")


def _default_registry_path() -> Path:
    # Resolve to project root based on this file location: api/resources/ -> api/ -> project root
    here = Path(__file__).resolve()
    project_root = here.parents[2]
    return project_root / "workflows" / "tools_registry.json"


@ns.route("/registry")
class ToolsRegistry(Resource):
    def get(self):
        # Allow override via env var
        env_path = os.environ.get("TOOLS_REGISTRY_PATH")
        path = Path(env_path) if env_path else _default_registry_path()
        if not path.exists():
            # Return empty registry if not built yet
            return {"registry": {}, "message": f"registry not found at {str(path)}"}, 200
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            return {"error": f"failed to read registry: {e}"}, 500
        # Return raw JSON mapping
        return Response(json.dumps(data), mimetype="application/json")
