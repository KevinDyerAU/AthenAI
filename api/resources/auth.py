from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User
from ..schemas import UserRegisterSchema, UserLoginSchema, UserSchema
from ..security.jwt_callbacks import revoke_current_jwt

ns = Namespace("auth", description="Authentication endpoints")

user_public_model = ns.model("UserPublic", {
    "id": fields.Integer,
    "email": fields.String,
    "role": fields.String,
    "is_active": fields.Boolean,
    "created_at": fields.DateTime,
})

token_model = ns.model("Tokens", {
    "access_token": fields.String,
    "refresh_token": fields.String,
})

register_schema = UserRegisterSchema()
login_schema = UserLoginSchema()
user_schema = UserSchema()


@ns.route("/register")
class Register(Resource):
    @ns.expect(ns.model("Register", {
        "email": fields.String(required=True),
        "password": fields.String(required=True),
        "role": fields.String,
    }), validate=True)
    @ns.marshal_with(user_public_model, code=201)
    def post(self):
        payload = request.get_json() or {}
        data = register_schema.load(payload)

        if User.query.filter_by(email=data["email"]).first():
            ns.abort(409, "Email already registered")
        user = User(email=data["email"], role=data.get("role", "user"))
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user), 201


@ns.route("/login")
class Login(Resource):
    @ns.expect(ns.model("Login", {
        "email": fields.String(required=True),
        "password": fields.String(required=True),
    }), validate=True)
    @ns.marshal_with(token_model)
    def post(self):
        payload = request.get_json() or {}
        data = login_schema.load(payload)
        user = User.query.filter_by(email=data["email"]).first()
        if not user or not user.check_password(data["password"]):
            ns.abort(401, "Invalid credentials")
        if not user.is_active:
            ns.abort(403, "User is inactive")
        identity = {"id": user.id, "email": user.email, "role": user.role}
        access = create_access_token(identity=identity)
        refresh = create_refresh_token(identity=identity)
        return {"access_token": access, "refresh_token": refresh}


@ns.route("/refresh")
class Refresh(Resource):
    @jwt_required(refresh=True)
    @ns.marshal_with(token_model)
    def post(self):
        identity = get_jwt_identity()
        access = create_access_token(identity=identity)
        refresh = create_refresh_token(identity=identity)
        return {"access_token": access, "refresh_token": refresh}


@ns.route("/me")
class Me(Resource):
    @jwt_required()
    @ns.marshal_with(user_public_model)
    def get(self):
        identity = get_jwt_identity()
        user = User.query.get(identity["id"]) if isinstance(identity, dict) else None
        if not user:
            ns.abort(404, "User not found")
        return user_schema.dump(user)


@ns.route("/logout")
class Logout(Resource):
    @jwt_required()
    def post(self):
        revoke_current_jwt()
        return {"message": "Token revoked"}
