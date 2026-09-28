from flask import Flask, Blueprint, jsonify, request, current_app
import jwt
from datetime import datetime, timedelta, timezone

from .extensions import db, bcrypt
from .models import User
from .validators import validate_registration
from .Middleware import auth_required
from .responses import success_response


routes = Blueprint("routes", __name__)


def register_routes(app: Flask) -> None:
    app.register_blueprint(routes)


@routes.get("/health")
def health():
    return jsonify({
        "success": True,
        "message": "Flask API is running."
    }), 200


@routes.post("/register")
def register():
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "Content-Type must be application/json."
        }), 415

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Request body must contain a valid JSON object."
        }), 400

    errors = validate_registration(data)

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": errors
        }), 400

    name = str(data["name"]).strip()
    email = str(data["email"]).strip().lower()
    mobile = str(data["mobile"]).strip()
    password = str(data["password"])

    existing_email = User.query.filter_by(email=email).first()

    if existing_email:
        return jsonify({
            "success": False,
            "message": "Email already registered."
        }), 409

    existing_mobile = User.query.filter_by(mobile=mobile).first()

    if existing_mobile:
        return jsonify({
            "success": False,
            "message": "Mobile number already registered."
        }), 409

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        name=name,
        email=email,
        mobile=mobile,
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Registration successful.",
        "data": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile
        }
    }), 201


@routes.post("/login")
def login():
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "Content-Type must be application/json."
        }), 415

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Request body must contain a valid JSON object."
        }), 400

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile
        }
    }), 200


@routes.get("/dashboard")
@auth_required
def dashboard():
    return success_response(
        "Dashboard data retrieved successfully.",
        {
            "user_id": request.user_id
        }
    )