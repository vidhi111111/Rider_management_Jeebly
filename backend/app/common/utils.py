from typing import Any, Dict, Optional
from flask import request


def read_request_data() -> Optional[Dict[str, Any]]:
    """
    Extract request data from JSON body or multipart/x-www-form-urlencoded form.
    Returns None if request content is empty or not a valid dictionary.
    """
    if request.is_json:
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else None

    if request.form:
        return request.form.to_dict()

    return None


def get_user_id() -> Optional[int]:
    """Retrieve the authenticated user's ID attached by auth_required middleware."""
    return getattr(request, "user_id", None)


def format_marshmallow_errors(errors: Dict[str, Any]) -> Dict[str, str]:
    """
    Convert Marshmallow's error structure into a clean, flat dictionary of field -> error message.
    Preserves exact contract expected by frontend components.
    Example:
        {'name': ['Name is required.']} -> {'name': 'Name is required.'}
    """
    formatted = {}
    for field, message_data in errors.items():
        if isinstance(message_data, list) and len(message_data) > 0:
            first_msg = message_data[0]
            if isinstance(first_msg, dict):
                formatted[field] = str(first_msg)
            else:
                formatted[field] = str(first_msg)
        elif isinstance(message_data, dict):
            # Nested error dict
            sub_errors = format_marshmallow_errors(message_data)
            for sub_field, sub_msg in sub_errors.items():
                formatted[f"{field}.{sub_field}"] = sub_msg
        else:
            formatted[field] = str(message_data)
    return formatted
