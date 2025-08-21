from marshmallow import Schema, fields, validate


class UserRegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    role = fields.String(load_default="user")


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email()
    role = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime()
