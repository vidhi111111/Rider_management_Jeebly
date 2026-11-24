from typing import Dict, Any, Tuple, Optional
from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from ...common.utils import format_marshmallow_errors


class UpdateProfileSchema(Schema):
    name = fields.String(allow_none=True, load_default=None)
    mobile = fields.String(allow_none=True, load_default=None)
    profile_image = fields.String(allow_none=True, load_default=None)
    remove_photo = fields.Boolean(allow_none=True, load_default=False)

    @validates("name")
    def validate_name(self, value, **kwargs):
        if value is not None:
            stripped = str(value or "").strip()
            if not stripped or len(stripped) > 100:
                raise ValidationError("Name is required and must be at most 100 characters.")

    @validates("mobile")
    def validate_mobile(self, value, **kwargs):
        if value is not None:
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
    profile_image = fields.String(dump_only=True)


update_profile_schema = UpdateProfileSchema()
change_password_schema = ChangePasswordSchema()
profile_schema = ProfileSchema()


def validate_profile_payload(data: Dict[str, Any], current_name: str, current_mobile: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    if not isinstance(data, dict):
        return False, "A valid payload is required.", {}

    name = data.get("name")
    if name is not None:
        name_val = str(name).strip()
        if not name_val:
            return False, "Name cannot be empty.", {}
        if len(name_val) > 100:
            return False, "Name must be at most 100 characters.", {}
    else:
        name_val = current_name

    mobile = data.get("mobile")
    if mobile is not None:
        mobile_val = str(mobile).strip()
        if not mobile_val.isdigit() or len(mobile_val) != 10:
            return False, "Mobile number must contain exactly 10 digits.", {}
    else:
        mobile_val = current_mobile

    cleaned = {
        "name": name_val,
        "mobile": mobile_val,
        "profile_image": data.get("profile_image"),
        "remove_photo": bool(data.get("remove_photo", False))
    }
    return True, None, cleaned


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
