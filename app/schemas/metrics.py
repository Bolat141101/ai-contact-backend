from marshmallow import Schema, fields


class MetricsResponseSchema(Schema):
    total = fields.Integer(required=True)
    last_24_hours = fields.Integer(required=True)
    ai_fallbacks = fields.Integer(required=True)
    email_failures = fields.Integer(required=True)
    by_category = fields.Dict(
        keys=fields.String(),
        values=fields.Integer(),
        required=True,
    )
