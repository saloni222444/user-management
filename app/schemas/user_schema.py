import re

from marshmallow import Schema, ValidationError, fields, validates

from app.errors import ValidationAPIError

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Order in which field errors are reported when several are invalid at once,
# so responses are deterministic (e.g. a payload missing both name and
# email always reports the name error first).
_FIELD_PRIORITY = ["name", "email", "role"]


class UserSchema(Schema):
    name = fields.Str(required=True, error_messages={"required": "Name is required"})
    email = fields.Str(required=True, error_messages={"required": "Email is required"})
    role = fields.Str(required=True, error_messages={"required": "Role is required"})

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Name is required")

    @validates("email")
    def validate_email(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Email is required")
        if not EMAIL_REGEX.match(value.strip()):
            raise ValidationError("Invalid email format")

    @validates("role")
    def validate_role(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Role is required")


_schema = UserSchema()


def validate_user_payload(payload):
    """Validate a raw JSON body for user creation.

    Returns a cleaned dict (trimmed strings, lowercased email) on success,
    or raises ValidationAPIError with a single, user-facing message.
    """
    if not isinstance(payload, dict):
        raise ValidationAPIError("Request body must be a JSON object")

    errors = _schema.validate(payload)
    if errors:
        for field in _FIELD_PRIORITY:
            if field in errors:
                raise ValidationAPIError(errors[field][0])
        # Fallback for any field not in the priority list above.
        raise ValidationAPIError(next(iter(errors.values()))[0])

    return {
        "name": payload["name"].strip(),
        "email": payload["email"].strip().lower(),
        "role": payload["role"].strip(),
    }
