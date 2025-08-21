from flask import jsonify
from werkzeug.exceptions import HTTPException
from .extensions import api as restx_api


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        response = {
            "error": {
                "type": e.__class__.__name__,
                "message": e.description,
                "status": e.code,
            }
        }
        return jsonify(response), e.code

    @app.errorhandler(Exception)
    def handle_exception(e: Exception):
        restx_api.logger.exception("Unhandled exception")
        response = {
            "error": {
                "type": e.__class__.__name__,
                "message": str(e),
                "status": 500,
            }
        }
        return jsonify(response), 500
