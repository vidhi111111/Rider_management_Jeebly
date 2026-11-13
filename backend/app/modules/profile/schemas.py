from typing import Dict, Any, Tuple, Optional
from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from ...common.utils import format_marshmallow_errors


class UpdateProfileSchema(Schema):
    name = fields.String(
        required=True,
        error_messages={"required": "Name is required and must be at most 100 characters."}
    )
    mobile = fields.String(
        required=True,
        error_messages={"required": "Mobile number must contain exactly 10 digits."}
    )

    @validates("name")
    def validate_name(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped or len(stripped) > 100:
            raise ValidationError("Name is required and must be at most 100 characters.")

    @validates("mobile")
    def validate_mobile(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped.isdigit() or len(stripped) != 10:
            raise ValidationError("Mobile number must contain exactly 10 digits.")


class ChangePasswordSchema(Schema):
    current_password = fields.String(
        required=True,
        error_messages={"required": "Current and new passwords are required."}
    )
    new_password = fields.String(
        required=True,
        error_messages={"required": "Current and new passwords are required."}
    )

    @validates("new_password")
    def validate_new_password(self, value, **kwargs):
        if not value or len(value) < 8:
            raise ValidationError("New password must be at least 8 characters.")

    @validates_schema(skip_on_field_errors=True)
    def validate_passwords(self, data, **kwargs):
        current_pw = data.get("current_password")
        new_pw = data.get("new_password")
        if not current_pw or not new_pw:
            raise ValidationError("Current and new passwords are required.")


class ProfileSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    email = fields.String(dump_only=True)
    mobile = fields.String(dump_only=True)


update_profile_schema = UpdateProfileSchema()
change_password_schema = ChangePasswordSchema()
profile_schema = ProfileSchema()


def validate_profile_payload(data: Dict[str, Any], current_name: str, current_mobile: str) -> Tuple[bool, Optional[str], Dict[str, str]]:
    if not isinstance(data, dict):
        return False, "A valid JSON object is required.", {}

    name = str(data.get("name", current_name)).strip()
    mobile = str(data.get("mobile", current_mobile)).strip()

    try:
        cleaned = update_profile_schema.load({"name": name, "mobile": mobile})
        return True, None, cleaned
    except ValidationError as err:
        errors = format_marshmallow_errors(err.messages)
        first_msg = next(iter(errors.values())) if errors else "Validation failed."
        return False, first_msg, {}


def validate_change_password_payload(data: Dict[str, Any]) -> Tuple[bool, Optional[str], str, str]:
    if not isinstance(data, dict):
        return False, "A valid JSON object is required.", "", ""

    current_pw = str(data.get("current_password", ""))
    new_pw = str(data.get("new_password", ""))

    if not current_pw or not new_pw:
        return False, "Current and new passwords are required.", "", ""

    try:
        cleaned = change_password_schema.load({"current_password": current_pw, "new_password": new_pw})
        return True, None, cleaned["current_password"], cleaned["new_password"]
    except ValidationError as err:
        errors = format_marshmallow_errors(err.messages)
        first_msg = next(iter(errors.values())) if errors else "Validation failed."
        return False, first_msg, "", ""


def serialize_profile(user) -> Dict[str, Any]:
    if user is None:
        return {}
    return profile_schema.dump(user)
