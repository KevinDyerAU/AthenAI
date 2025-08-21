from marshmallow import Schema, fields, validate


class AgentCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    type = fields.String(required=True)
    config = fields.Dict(load_default=dict)


class AgentUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=2, max=120))
    type = fields.String()
    status = fields.String(validate=validate.OneOf(["idle", "running", "error", "paused"]))
    config = fields.Dict()


class AgentSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    type = fields.String()
    status = fields.String()
    config = fields.Dict()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
