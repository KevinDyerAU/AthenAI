from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_socketio import SocketIO


db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
authorizations = {
    "BearerAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Add: Bearer <access_token>"
    }
}
api = Api(
    version="1.0",
    title="NeoV3 API",
    description="REST API for NeoV3",
    doc="/docs",
    authorizations=authorizations,
    security="BearerAuth",
    prefix="/api",
)
socketio = SocketIO(async_mode="gevent")
