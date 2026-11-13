import re
from marshmallow import Schema, fields, validate, validates, ValidationError
from ...common.utils import format_marshmallow_errors


class RegisterSchema(Schema):
    name = fields.String(
        required=True,
        error_messages={"required": "Name is required."}
    )
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Please provide a valid email address."
        }
    )
    mobile = fields.String(
        required=True,
        error_messages={"required": "Mobile number is req."}
    )
    password = fields.String(
        required=True,
        error_messages={"required": "Password is req."}
    )

    @validates("name")
    def validate_name(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped:
            raise ValidationError("Name is required.")
        if len(stripped) < 2:
            raise ValidationError("Name must contain at least 2 characters.")
        if len(stripped) > 100:
            raise ValidationError("Name cannot exceed 100 characters.")

    @validates("email")
    def validate_email_field(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped:
            raise ValidationError("Email is required.")
        if len(stripped) > 120:
            raise ValidationError("Email cannot exceed 120 characters.")

    @validates("mobile")
    def validate_mobile(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped:
            raise ValidationError("Mobile number is req.")
        if not re.fullmatch(r"[0-9]{10}", stripped):
            raise ValidationError("Mobile number must contain exactly 10 digits.")

    @validates("password")
    def validate_password(self, value, **kwargs):
        if not value:
            raise ValidationError("Password is req.")
        if len(value) < 8:
            raise ValidationError("Password must contain at least 8 characters.")


class LoginSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Please provide a valid email address."
        }
    )
    password = fields.String(
        required=True,
        error_messages={"required": "Password is required."}
    )

    @validates("email")
    def validate_email_field(self, value, **kwargs):
        if not str(value or "").strip():
            raise ValidationError("Email is required.")

    @validates("password")
    def validate_password(self, value, **kwargs):
        if not value:
            raise ValidationError("Password is required.")


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    email = fields.String(dump_only=True)
    mobile = fields.String(dump_only=True)


# Singletons
register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserSchema()


def validate_registration_payload(data: dict) -> dict:
    """Validate registration payload using RegisterSchema and return formatted errors."""
    if not isinstance(data, dict):
        return {"payload": "A valid JSON object is required."}
    try:
        register_schema.load(data)
        return {}
    except ValidationError as err:
        return format_marshmallow_errors(err.messages)


def serialize_user(user) -> dict:
    """Serialize a User model instance using Marshmallow."""
    if user is None:
        return {}
    return user_schema.dump(user)
