from flask import request, jsonify
from marshmallow import ValidationError
from ...common.responses import error_response, success_response
from ...common.utils import format_marshmallow_errors
from .schemas import register_schema, login_schema
from .services import AuthService


class AuthController:
    def __init__(self, auth_service: AuthService = None):
        self.auth_service = auth_service or AuthService()

    def health(self):
        return jsonify({
            "success": True,
            "message": "Flask API is running."
        }), 200

    def register(self):
        if not request.is_json:
            return error_response("Content-Type must be application/json.", 415)

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error_response("A valid JSON object is required.", 400)

        try:
            validated = register_schema.load(data)
        except ValidationError as err:
            return jsonify({
                "success": False,
                "message": "Validation failed.",
                "errors": format_marshmallow_errors(err.messages)
            }), 400

        name = str(validated["name"]).strip()
        email = str(validated["email"]).strip().lower()
        mobile = str(validated["mobile"]).strip()
        password = str(validated["password"])

        success, message, user_data, status_code = self.auth_service.register(
            name=name,
            email=email,
            mobile=mobile,
            password=password
        )

        if not success:
            return error_response(message, status_code)

        return success_response(message, user_data, status_code)

    def login(self):
        if not request.is_json:
            return error_response("Content-Type must be application/json.", 415)

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error_response("A valid JSON object is required.", 400)

        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))

        if not email or not password:
            return error_response("Email and password are required.", 400)

        try:
            validated = login_schema.load({"email": email, "password": password})
        except ValidationError:
            return error_response("Email and password are required.", 400)

        success, message, auth_data, status_code = self.auth_service.login(
            email=validated["email"].lower(),
            password=validated["password"]
        )

        if not success:
            return error_response(message, status_code)

        return jsonify({
            "success": True,
            "message": message,
            "token": auth_data["token"],
            "user": auth_data["user"]
        }), status_code
