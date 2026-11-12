from .modules.auth.schemas import validate_registration_payload


def validate_registration(data: dict) -> dict:
    return validate_registration_payload(data)
