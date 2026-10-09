from flask import Flask, Blueprint, jsonify, request, current_app

import jwt

from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy import or_

from .extensions import db, bcrypt
from .models import User, Rider, Order
from .validators import validate_registration
from .Middleware import auth_required
from .responses import success_response


routes = Blueprint("routes", __name__)


def register_routes(app: Flask) -> None:
    app.register_blueprint(routes)


def validate_rider_data(data):
    errors = {}

    name = str(data.get("name", "")).strip()
    mobile = str(data.get("mobile", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    vehicle = str(data.get("vehicle", "")).strip()
    status = str(data.get("status", "")).strip().lower()
    availability = str(data.get("availability", "")).strip().lower()
    date_value = str(data.get("date", "")).strip()

    if not name:
        errors["name"] = "Name is required."

    if not mobile:
        errors["mobile"] = "Mobile number is required."
    elif not mobile.isdigit() or len(mobile) != 10:
        errors["mobile"] = "Mobile number must contain exactly 10 digits."

    if not email:
        errors["email"] = "Email is required."
    elif "@" not in email or "." not in email.split("@")[-1]:
        errors["email"] = "Enter a valid email address."

    if not vehicle:
        errors["vehicle"] = "Vehicle is required."

    allowed_statuses = {
        "available",
        "on_order",
        "scheduled_break",
        "absent"
    }

    if not status:
        errors["status"] = "Status is required."
    elif status not in allowed_statuses:
        errors["status"] = "Invalid status."

    allowed_availability = {
        "available",
        "unavailable"
    }

    if not availability:
        errors["availability"] = "Availability is required."
    elif availability not in allowed_availability:
        errors["availability"] = "Invalid availability."

    parsed_date = None

    if not date_value:
        errors["date"] = "Date is required."
    else:
        try:
            parsed_date = datetime.strptime(
                date_value,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            errors["date"] = "Date must be in YYYY-MM-DD format."

    return errors, {
        "name": name,
        "mobile": mobile,
        "email": email,
        "vehicle": vehicle,
        "status": status,
        "availability": availability,
        "date": parsed_date
    }


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


@routes.post("/riders")
@auth_required
def create_rider():
    if request.content_type and request.content_type.startswith(
        "multipart/form-data"
    ):
        data = request.form.to_dict()
        profile_image = request.files.get("profile_image")

    else:
        if not request.is_json:
            return jsonify({
                "success": False,
                "message": "Content-Type must be application/json or multipart/form-data."
            }), 415

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "message": "Request body must contain a valid JSON object."
            }), 400

        profile_image = None

    errors, rider_data = validate_rider_data(data)

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": errors
        }), 400

    existing_mobile = Rider.query.filter_by(
        mobile=rider_data["mobile"]
    ).first()

    if existing_mobile:
        return jsonify({
            "success": False,
            "message": "Mobile number already registered for a rider."
        }), 409

    existing_email = Rider.query.filter_by(
        email=rider_data["email"]
    ).first()

    if existing_email:
        return jsonify({
            "success": False,
            "message": "Email already registered for a rider."
        }), 409

    profile_image_name = None

    if profile_image:
        profile_image_name = profile_image.filename

    rider = Rider(
        name=rider_data["name"],
        mobile=rider_data["mobile"],
        email=rider_data["email"],
        vehicle=rider_data["vehicle"],
        status=rider_data["status"],
        availability=rider_data["availability"],
        date=rider_data["date"],
        profile_image=profile_image_name
    )

    try:
        db.session.add(rider)
        db.session.commit()

    except SQLAlchemyError as error:
        print(error)
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Database error occurred."
        }), 500

    return success_response(
        "Rider created successfully.",
        {
            "id": rider.id,
            "name": rider.name,
            "mobile": rider.mobile,
            "email": rider.email,
            "vehicle": rider.vehicle,
            "status": rider.status,
            "availability": rider.availability,
            "date": rider.date.isoformat(),
            "profile_image": rider.profile_image
        }
    ), 201


# get rider details using rider id
@routes.get("/riders/<int:rider_id>")
@auth_required
def get_rider(rider_id):
    rider = Rider.query.get(rider_id)

    if not rider:
        return jsonify({
            "success": False,
            "message": "Rider not found."
        }), 404

    return success_response(
        "Rider retrieved successfully.",
        {
            "id": rider.id,
            "name": rider.name,
            "mobile": rider.mobile,
            "email": rider.email,
            "vehicle": rider.vehicle,
            "status": rider.status,
            "availability": rider.availability,
            "date": rider.date.isoformat(),
            "profile_image": rider.profile_image
        }
    ), 200


# update rider details using rider id
@routes.put("/riders/<int:rider_id>")
@auth_required
def update_rider(rider_id):
    rider = Rider.query.get(rider_id)

    if not rider:
        return jsonify({
            "success": False,
            "message": "Rider not found."
        }), 404

    if request.content_type and request.content_type.startswith(
        "multipart/form-data"
    ):
        data = request.form.to_dict()
        profile_image = request.files.get("profile_image")

    else:
        if not request.is_json:
            return jsonify({
                "success": False,
                "message": "Content-Type must be application/json or multipart/form-data."
            }), 415

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "message": "Request body must contain a valid JSON object."
            }), 400

        profile_image = None

    errors, rider_data = validate_rider_data(data)

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": errors
        }), 400

    # ignore the current rider while checking duplicate mobile
    existing_mobile = Rider.query.filter(
        Rider.mobile == rider_data["mobile"],
        Rider.id != rider_id
    ).first()

    if existing_mobile:
        return jsonify({
            "success": False,
            "message": "Mobile number already registered for another rider."
        }), 409

    # ignore the current rider while checking duplicate email
    existing_email = Rider.query.filter(
        Rider.email == rider_data["email"],
        Rider.id != rider_id
    ).first()

    if existing_email:
        return jsonify({
            "success": False,
            "message": "Email already registered for another rider."
        }), 409

    rider.name = rider_data["name"]
    rider.mobile = rider_data["mobile"]
    rider.email = rider_data["email"]
    rider.vehicle = rider_data["vehicle"]
    rider.status = rider_data["status"]
    rider.availability = rider_data["availability"]
    rider.date = rider_data["date"]

    if profile_image:
        rider.profile_image = profile_image.filename

    try:
        db.session.commit()

    except SQLAlchemyError as error:
        print(error)
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Database error occurred."
        }), 500

    return success_response(
        "Rider updated successfully.",
        {
            "id": rider.id,
            "name": rider.name,
            "mobile": rider.mobile,
            "email": rider.email,
            "vehicle": rider.vehicle,
            "status": rider.status,
            "availability": rider.availability,
            "date": rider.date.isoformat(),
            "profile_image": rider.profile_image
        }
    ), 200


@routes.get("/dashboard")
@auth_required
def dashboard():
    total_orders = Order.query.count()
    delivered_orders = Order.query.filter_by(status="delivered").count()
    cancelled_orders = Order.query.filter_by(status="cancelled").count()
    in_progress_orders = Order.query.filter_by(status="in_progress").count()

    available_riders = Rider.query.filter_by(status="available").count()
    on_order_riders = Rider.query.filter_by(status="on_order").count()
    scheduled_break_riders = Rider.query.filter_by(
        status="scheduled_break"
    ).count()
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

        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().lower()
        availability = request.args.get("availability", "").strip().lower()

        sort_by = request.args.get("sortBy", "id").strip()
        sort_order = request.args.get("sortOrder", "asc").strip().lower()

        if page < 1:
            page = 1

        if page_size < 1:
            page_size = 10

        query = Rider.query

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                or_(
                    Rider.name.ilike(search_value),
                    Rider.mobile.ilike(search_value),
                    Rider.email.ilike(search_value)
                )
            )

        if status:
            query = query.filter(
                Rider.status == status
            )

        if availability:
            query = query.filter(
                Rider.availability == availability
            )

        sort_columns = {
            "id": Rider.id,
            "name": Rider.name,
            "mobile": Rider.mobile,
            "email": Rider.email,
            "vehicle": Rider.vehicle,
            "status": Rider.status,
            "availability": Rider.availability,
            "date": Rider.date
        }

        sort_column = sort_columns.get(
            sort_by,
            Rider.id
        )

        if sort_order == "desc":
            query = query.order_by(
                sort_column.desc()
            )
        else:
            query = query.order_by(
                sort_column.asc()
            )

        pagination = query.paginate(
            page=page,
            per_page=page_size,
            error_out=False
        )

        riders_data = [
            {
                "id": rider.id,
                "name": rider.name,
                "mobile": rider.mobile,
                "email": rider.email,
                "vehicle": rider.vehicle,
                "status": rider.status,
                "availability": rider.availability,
                "date": rider.date.isoformat(),
                "profile_image": rider.profile_image
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

    except Exception as error:
        print(error)
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