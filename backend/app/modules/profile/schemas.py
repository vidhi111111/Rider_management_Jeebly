from typing import Dict, Any, Tuple, Optional


def validate_profile_payload(data: Dict[str, Any], current_name: str, current_mobile: str) -> Tuple[bool, Optional[str], Dict[str, str]]:
    if not isinstance(data, dict):
        return False, "A valid JSON object is required.", {}

    name = str(data.get("name", current_name)).strip()
    mobile = str(data.get("mobile", current_mobile)).strip()

    if not name or len(name) > 100:
        return False, "Name is required and must be at most 100 characters.", {}

    if not mobile.isdigit() or len(mobile) != 10:
        return False, "Mobile number must contain exactly 10 digits.", {}

    return True, None, {
        "name": name,
        "mobile": mobile
    }


def validate_change_password_payload(data: Dict[str, Any]) -> Tuple[bool, Optional[str], str, str]:
    if not isinstance(data, dict):
        return False, "A valid JSON object is required.", "", ""

    current_password = str(data.get("current_password", ""))
    new_password = str(data.get("new_password", ""))

    if not current_password or not new_password:
        return False, "Current and new passwords are required.", "", ""

    if len(new_password) < 8:
        return False, "New password must be at least 8 characters.", "", ""

    return True, None, current_password, new_password


def serialize_profile(user) -> Dict[str, Any]:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile": user.mobile
    }
