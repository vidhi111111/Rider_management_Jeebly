from datetime import datetime
from typing import Tuple, Dict, Any, Optional
from flask import url_for


def serialize_rider(rider) -> Dict[str, Any]:
    if rider is None:
        return None

    image = rider.profile_image

    if image and str(image).startswith(("https://", "http://")):
        image_url = image
    elif image:
        try:
            image_url = url_for("riders.rider_upload", filename=image, _external=True)
        except Exception:
            try:
                image_url = url_for("routes.rider_upload", filename=image, _external=True)
            except Exception:
                image_url = f"/rider-uploads/{image}"
    else:
        image_url = None

    return {
        "id": rider.id,
        "name": rider.name,
        "mobile": rider.mobile,
        "email": rider.email,
        "vehicle": rider.vehicle,
        "status": rider.status,
        "availability": rider.availability,
        "date": rider.date.isoformat() if rider.date else None,
        "profile_image": image_url
    }


def validate_rider_data(data: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, Any]]:
    errors = {}

    name = str(data.get("name", "")).strip()
    mobile = str(data.get("mobile", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    vehicle = str(data.get("vehicle", "")).strip()
    status = str(data.get("status", "active")).strip().lower()
    availability = str(data.get("availability", "available")).strip().lower()
    date_value = str(data.get("date", "")).strip()

    if not name or not 2 <= len(name) <= 100:
        errors["name"] = "Name must contain 2 to 100 characters."

    if not mobile.isdigit() or len(mobile) != 10:
        errors["mobile"] = "Mobile number must contain 10 digits."

    if (
        not email
        or "@" not in email
        or "." not in email.split("@")[-1]
        or len(email) > 120
    ):
        errors["email"] = "Enter a valid email address."

    if not vehicle or len(vehicle) > 100:
        errors["vehicle"] = "Vehicle is required (maximum 100 characters)."

    valid_rider_statuses = {
        "active", "inactive", "available", "on_order",
        "scheduled_break", "absent"
    }

    if status not in valid_rider_statuses:
        errors["status"] = "Invalid rider status."

    if availability not in {"available", "busy", "unavailable"}:
        errors["availability"] = "Invalid rider availability."

    parsed_date = None
    try:
        parsed_date = datetime.strptime(date_value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        errors["date"] = "Date must use YYYY-MM-DD format."

    if status in {"inactive", "absent", "scheduled_break"}:
        availability = "unavailable"
    elif status == "on_order":
        availability = "busy"

    remove_photo = str(data.get("remove_photo", "")).strip().lower() in ("true", "1", "yes")

    return errors, {
        "name": name,
        "mobile": mobile,
        "email": email,
        "vehicle": vehicle,
        "status": status,
        "availability": availability,
        "date": parsed_date,
        "remove_photo": remove_photo
    }
