from marshmallow import Schema, fields, validate


class BlacklistCreateSchema(Schema):
    email = fields.Email(required=True)
    app_uuid = fields.UUID(required=True)
    blocked_reason = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=255),
    )
