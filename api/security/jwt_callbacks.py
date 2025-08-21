from flask import jsonify
from flask_jwt_extended import JWTManager, get_jwt
from .token_blocklist import add as block_add, is_blocked


def register_jwt_callbacks(jwt: JWTManager):
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict):
        jti = jwt_payload.get("jti")
        return is_blocked(jti)

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"error": {"type": "RevokedToken", "message": "Token has been revoked", "status": 401}}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(reason: str):
        return (
            jsonify({"error": {"type": "InvalidToken", "message": reason, "status": 422}}),
            422,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(reason: str):
        return (
            jsonify({"error": {"type": "MissingToken", "message": reason, "status": 401}}),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"error": {"type": "ExpiredToken", "message": "Token has expired", "status": 401}}),
            401,
        )


def revoke_current_jwt():
    claims = get_jwt()
    jti = claims.get("jti")
    block_add(jti)
