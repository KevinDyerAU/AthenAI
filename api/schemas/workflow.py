from marshmallow import Schema, fields, validate


class WorkflowCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    definition = fields.Dict(required=True)


class WorkflowUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=2, max=120))
    definition = fields.Dict()
    status = fields.String(validate=validate.OneOf(["draft", "queued", "running", "failed", "completed"]))


class WorkflowRunSchema(Schema):
    parameters = fields.Dict(load_default=dict)
    async_mode = fields.Boolean(load_default=True)


class WorkflowSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    definition = fields.Dict()
    status = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
