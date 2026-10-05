from flask import Flask, Blueprint, jsonify, request, current_app
import jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError

from .extensions import db, bcrypt
from .models import User, Rider, Order
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

    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError as error:
        print(error)
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Database error occurred."
        }), 500

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
    total_orders = Order.query.count()
    delivered_orders = Order.query.filter_by(status="delivered").count()
    cancelled_orders = Order.query.filter_by(status="cancelled").count()
    in_progress_orders = Order.query.filter_by(status="in_progress").count()

    available_riders = Rider.query.filter_by(status="available").count()
    on_order_riders = Rider.query.filter_by(status="on_order").count()
    scheduled_break_riders = Rider.query.filter_by(status="scheduled_break").count()
    absent_riders = Rider.query.filter_by(status="absent").count()

    recent_orders = (
        Order.query
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )

    available_rider_list = (
        Rider.query
        .filter_by(status="available")
        .limit(10)
        .all()
    )

    data = {
        "summary": {
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "in_progress_orders": in_progress_orders
        },
        "rider_summary": {
            "available": available_riders,
            "on_order": on_order_riders,
            "scheduled_break": scheduled_break_riders,
            "absent": absent_riders
        },
        "recent_orders": [
            {
                "id": order.id,
                "status": order.status,
                "customer": order.customer_name
            }
            for order in recent_orders
        ],
        "available_riders": [
            {
                "id": rider.id,
                "name": rider.name,
                "status": rider.status
            }
            for rider in available_rider_list
        ]
    }

    return success_response(
        "Dashboard data retrieved successfully.",
        data
    )


@routes.get("/profile")
@auth_required
def profile():
    user = User.query.get(request.user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found."
        }), 404

    return success_response(
        "Profile retrieved successfully.",
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile
        }
    )


@routes.get("/riders")
@auth_required
def riders():
    try:
        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("pageSize", 10, type=int)

        if page < 1:
            page = 1

        if page_size < 1:
            page_size = 10

        pagination = Rider.query.paginate(
            page=page,
            per_page=page_size,
            error_out=False
        )

        riders_data = [
            {
                "id": rider.id,
                "name": rider.name,
                "status": rider.status
            }
            for rider in pagination.items
        ]

        return success_response(
            "Riders retrieved successfully.",
            {
                "riders": riders_data,
                "page": pagination.page,
                "pageSize": pagination.per_page,
                "totalRecords": pagination.total,
                "totalPages": pagination.pages
            }
        )

    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Unable to retrieve riders."
        }), 500


@routes.get("/orders")
@auth_required
def orders():
    return success_response(
        "Orders data retrieved successfully.",
        {
            "user_id": request.user_id,
            "orders": []
        }
    )


@routes.get("/settings")
@auth_required
def settings():
    return success_response(
        "Settings data retrieved successfully.",
        {
            "user_id": request.user_id,
            "settings": {
                "notifications": True,
                "dark_mode": False
            }
        }
    )