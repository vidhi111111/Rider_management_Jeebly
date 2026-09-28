from functools import wraps

import jwt

from flask import request, jsonify, current_app


def auth_required(function):

    @wraps(function)
    def decorated(*args, **kwargs):

        authorization = request.headers.get("Authorization")

        if not authorization:
            return jsonify({
                "success": False,
                "message": "Authorization header is required."
            }), 401

        parts = authorization.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({
                "success": False,
                "message": "Invalid authorization format."
            }), 401

        token = parts[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            user_id = payload.get("user_id")

            if not user_id:
                return jsonify({
                    "success": False,
                    "message": "Invalid token."
                }), 401

            request.user_id = user_id

        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "message": "Token has expired."
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid token."
            }), 401

        return function(*args, **kwargs)

    return decorated