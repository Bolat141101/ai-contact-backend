import re

from marshmallow import RAISE, Schema, ValidationError, fields, pre_load, validate, validates

PHONE_PATTERN = re.compile(r"^\+?[0-9()\-\s]{7,24}$")


class ContactCreateSchema(Schema):
    class Meta:
        unknown = RAISE

    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    phone = fields.String(required=True)
    email = fields.Email(required=True, validate=validate.Length(max=254))
    comment = fields.String(required=True, validate=validate.Length(min=10, max=3000))

    @pre_load
    def strip_strings(self, data, **kwargs):
        if not isinstance(data, dict):
            return data
        return {
            key: value.strip() if isinstance(value, str) else value for key, value in data.items()
        }

    @validates("phone")
    def validate_phone(self, value, **kwargs):
        if not PHONE_PATTERN.fullmatch(value):
            raise ValidationError("Invalid phone number format.")
        digit_count = sum(character.isdigit() for character in value)
        if not 7 <= digit_count <= 15:
            raise ValidationError("Phone number must contain 7 to 15 digits.")


class AIContactResponseSchema(Schema):
    category = fields.String(required=True)
    sentiment = fields.String(required=True)
    priority = fields.String(required=True)
    reply = fields.String(required=True)


class ContactResponseSchema(Schema):
    id = fields.Integer(required=True)
    status = fields.String(required=True)
    message = fields.String(required=True)
    ai_processed = fields.Boolean(required=True)
    ai = fields.Nested(AIContactResponseSchema, required=True)
