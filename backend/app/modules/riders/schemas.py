import re
from datetime import datetime, date
from typing import Dict, Any, Tuple
from flask import url_for
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from ...common.utils import format_marshmallow_errors

VALID_RIDER_STATUSES = [
    "active", "inactive", "available", "on_order",
    "scheduled_break", "absent"
]

VALID_RIDER_AVAILABILITIES = ["available", "busy", "unavailable"]


class RiderInputSchema(Schema):
    name = fields.String(
        required=True,
        error_messages={"required": "Name must contain 2 to 100 characters."}
    )
    mobile = fields.String(
        required=True,
        error_messages={"required": "Mobile number must contain 10 digits."}
    )
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Enter a valid email address.",
            "invalid": "Enter a valid email address."
        }
    )
    vehicle = fields.String(
        required=True,
        error_messages={"required": "Vehicle is required (maximum 100 characters)."}
    )
    status = fields.String(
        load_default="active",
        validate=validate.OneOf(VALID_RIDER_STATUSES, error="Invalid rider status.")
    )
    availability = fields.String(
        load_default="available",
        validate=validate.OneOf(VALID_RIDER_AVAILABILITIES, error="Invalid rider availability.")
    )
    date = fields.Date(
        required=True,
        format="%Y-%m-%d",
        error_messages={
            "required": "Date must use YYYY-MM-DD format.",
            "invalid": "Date must use YYYY-MM-DD format."
        }
    )
    remove_photo = fields.Boolean(load_default=False)

    @validates("name")
    def validate_name(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not (2 <= len(stripped) <= 100):
            raise ValidationError("Name must contain 2 to 100 characters.")

    @validates("mobile")
    def validate_mobile(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped.isdigit() or len(stripped) != 10:
            raise ValidationError("Mobile number must contain 10 digits.")

    @validates("email")
    def validate_email_field(self, value, **kwargs):
        stripped = str(value or "").strip().lower()
        if not stripped or "@" not in stripped or "." not in stripped.split("@")[-1] or len(stripped) > 120:
            raise ValidationError("Enter a valid email address.")

    @validates("vehicle")
    def validate_vehicle(self, value, **kwargs):
        stripped = str(value or "").strip()
        if not stripped or len(stripped) > 100:
            raise ValidationError("Vehicle is required (maximum 100 characters).")

    @validates_schema(skip_on_field_errors=True)
    def normalize_and_validate_availability(self, data, **kwargs):
        status = str(data.get("status", "active")).strip().lower()
        availability = str(data.get("availability", "available")).strip().lower()

        if status in {"inactive", "absent", "scheduled_break"}:
            data["availability"] = "unavailable"
        elif status == "on_order":
            data["availability"] = "busy"
        else:
            data["availability"] = availability

        data["name"] = str(data.get("name", "")).strip()
        data["mobile"] = str(data.get("mobile", "")).strip()
        data["email"] = str(data.get("email", "")).strip().lower()
        data["vehicle"] = str(data.get("vehicle", "")).strip()
        data["status"] = status


class RiderSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    mobile = fields.String(dump_only=True)
    email = fields.String(dump_only=True)
    vehicle = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    availability = fields.String(dump_only=True)
    date = fields.Method("get_date", dump_only=True)
    profile_image = fields.Method("get_profile_image", dump_only=True)

    def get_date(self, obj) -> str:
        if hasattr(obj, "date") and obj.date:
            return obj.date.isoformat()
        return None

    def get_profile_image(self, obj) -> str:
        image = getattr(obj, "profile_image", None)
        if not image:
            return None
        if str(image).startswith(("https://", "http://")):
            return image
        try:
            return url_for("riders.rider_upload", filename=image, _external=True)
        except Exception:
            try:
                return url_for("routes.rider_upload", filename=image, _external=True)
            except Exception:
                return f"/rider-uploads/{image}"


# Singletons
rider_input_schema = RiderInputSchema()
rider_schema = RiderSchema()
riders_list_schema = RiderSchema(many=True)


def serialize_rider(rider) -> Dict[str, Any]:
    """Serialize a Rider instance using Marshmallow."""
    if rider is None:
        return None
    return rider_schema.dump(rider)


def validate_rider_data(data: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, Any]]:
    """Validate rider data using RiderInputSchema and return (errors, cleaned_values)."""
    if not isinstance(data, dict):
        return {"payload": "A valid JSON or form body is required."}, {}

    # Handle string boolean for remove_photo from multipart/form-data
    raw_data = dict(data)
    if "remove_photo" in raw_data:
        val = str(raw_data["remove_photo"]).strip().lower()
        raw_data["remove_photo"] = val in ("true", "1", "yes")

    try:
        cleaned = rider_input_schema.load(raw_data)
        return {}, cleaned
    except ValidationError as err:
        return format_marshmallow_errors(err.messages), {}
