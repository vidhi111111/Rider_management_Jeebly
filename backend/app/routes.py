import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from flask import (
    Blueprint,
    Flask,
    current_app,
    jsonify,
    request,
    send_from_directory,
    url_for
)
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from .extensions import db, bcrypt
from .models import User, Rider, Order
from .validators import validate_registration
from .Middleware import auth_required
from .responses import success_response, error_response


routes = Blueprint("routes", __name__)

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def register_routes(app: Flask) -> None:
    app.register_blueprint(routes)


def get_upload_folder():
    folder = Path(current_app.root_path) / "uploads"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_rider_image(file):
    if not file or not file.filename:
        return None, None

    safe_name = secure_filename(file.filename)

    if not safe_name or "." not in safe_name:
        return None, "Invalid image filename."

    extension = safe_name.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return None, "Only JPG, JPEG, PNG and WEBP images are allowed."

    file.stream.seek(0, os.SEEK_END)
    file_size = file.stream.tell()
    file.stream.seek(0)

    if file_size == 0:
        return None, "The selected image is empty."

    if file_size > MAX_IMAGE_SIZE:
        return None, "Image size must not exceed 5 MB."

    filename = f"{uuid.uuid4().hex}.{extension}"
    destination = get_upload_folder() / filename

    try:
        file.save(str(destination))
    except OSError:
        current_app.logger.exception("Unable to save rider image.")
        return None, "Unable to save the uploaded image."

    return filename, None


def delete_rider_image(filename):
    if not filename:
        return

    safe_name = os.path.basename(filename)

    try:
        image_path = get_upload_folder() / safe_name

        if image_path.is_file():
            image_path.unlink()
    except OSError:
        current_app.logger.exception("Unable to delete rider image.")


@routes.get("/rider-uploads/<path:filename>")
def rider_upload(filename):
    return send_from_directory(get_upload_folder(), filename)


def serialize_rider(rider):
    image_url = None

    if rider.profile_image:
        image_url = url_for(
            "routes.rider_upload",
            filename=rider.profile_image,
            _external=True
        )

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


def serialize_order(order):
    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "status": order.status,
        "created_at": (
            order.created_at.isoformat()
            if order.created_at else None
        ),
        "rider_id": order.rider_id,
        "rider": serialize_rider(order.rider) if order.rider else None
    }


def validate_rider_data(data):
    errors = {}

    name = str(data.get("name", "")).strip()
    mobile = str(data.get("mobile", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    vehicle = str(data.get("vehicle", "")).strip()
    status = str(data.get("status", "active")).strip().lower()
    availability = str(
        data.get("availability", "available")
    ).strip().lower()
    date_value = str(data.get("date", "")).strip()

    if not name:
        errors["name"] = "Name is required."
    elif len(name) < 2 or len(name) > 100:
        errors["name"] = "Name must contain between 2 and 100 characters."

    if not mobile:
        errors["mobile"] = "Mobile number is required."
    elif not mobile.isdigit() or len(mobile) != 10:
        errors["mobile"] = "Mobile number must contain exactly 10 digits."

    if not email:
        errors["email"] = "Email is required."
    elif "@" not in email or "." not in email.split("@")[-1]:
        errors["email"] = "Enter a valid email address."
    elif len(email) > 120:
        errors["email"] = "Email cannot exceed 120 characters."

    if not vehicle:
        errors["vehicle"] = "Vehicle is required."
    elif len(vehicle) > 100:
        errors["vehicle"] = "Vehicle cannot exceed 100 characters."

    if status not in {"active", "inactive"}:
        errors["status"] = "Status must be active or inactive."

    if availability not in {"available", "busy", "unavailable"}:
        errors["availability"] = (
            "Availability must be available, busy, or unavailable."
        )

    parsed_date = None

    if not date_value:
        errors["date"] = "Date is required."
    else:
        try:
            parsed_date = datetime.strptime(
                date_value, "%Y-%m-%d"
            ).date()
        except ValueError:
            errors["date"] = "Date must be in YYYY-MM-DD format."

    if status == "inactive":
        availability = "unavailable"

    return errors, {
        "name": name,
        "mobile": mobile,
        "email": email,
        "vehicle": vehicle,
        "status": status,
        "availability": availability,
        "date": parsed_date
    }


def refresh_rider_availability(rider):
    if rider.status == "inactive":
        rider.availability = "unavailable"
        return

    active_orders = Order.query.filter(
        Order.rider_id == rider.id,
        Order.status.notin_(
            ["delivered", "cancelled", "completed"]
        )
    ).count()

    rider.availability = "busy" if active_orders else "available"


def read_request_data():
    if request.form:
        return request.form.to_dict()

    if request.is_json:
        return request.get_json(silent=True)

    return None


@routes.get("/health")
def health():
    return jsonify({
        "success": True,
        "message": "Flask API is running."
    }), 200


@routes.post("/register")
def register():
    if not request.is_json:
        return error_response(
            "Content-Type must be application/json.",
            415
        )

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response(
            "A valid JSON object is required.",
            400
        )

    errors = validate_registration(data)

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": errors
        }), 400

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    mobile = str(data.get("mobile", "")).strip()
    password = str(data.get("password", ""))

    if User.query.filter_by(email=email).first():
        return error_response("Email already registered.", 409)

    if User.query.filter_by(mobile=mobile).first():
        return error_response("Mobile number already registered.", 409)

    user = User(
        name=name,
        email=email,
        mobile=mobile,
        password=bcrypt.generate_password_hash(
            password
        ).decode("utf-8")
    )

    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to register user.")
        return error_response("Database error occurred.", 500)

    return success_response(
        "Registration successful.",
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile
        },
        201
    )


@routes.post("/login")
def login():
    if not request.is_json:
        return error_response(
            "Content-Type must be application/json.",
            415
        )

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response(
            "A valid JSON object is required.",
            400
        )

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return error_response(
            "Email and password are required.",
            400
        )

    user = User.query.filter_by(email=email).first()

    if (
        not user
        or not bcrypt.check_password_hash(user.password, password)
    ):
        return error_response("Invalid email or password.", 401)

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


@routes.get("/riders")
@auth_required
def riders():
    try:
        page = max(request.args.get("page", 1, type=int), 1)
        page_size = min(
            max(request.args.get("pageSize", 10, type=int), 1),
            100
        )

        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().lower()
        availability = request.args.get(
            "availability", ""
        ).strip().lower()
        sort_by = request.args.get("sortBy", "id").strip()
        sort_order = request.args.get(
            "sortOrder", "asc"
        ).strip().lower()

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

        if status in {"active", "inactive"}:
            query = query.filter(Rider.status == status)

        if availability in {
            "available", "busy", "unavailable"
        }:
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

        sort_column = sort_columns.get(sort_by, Rider.id)

        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        pagination = query.paginate(
            page=page,
            per_page=page_size,
            error_out=False
        )

        return success_response(
            "Riders retrieved successfully.",
            {
                "riders": [
                    serialize_rider(rider)
                    for rider in pagination.items
                ],
                "page": pagination.page,
                "pageSize": pagination.per_page,
                "totalRecords": pagination.total,
                "totalPages": pagination.pages
            }
        )

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to retrieve riders.")
        return error_response("Unable to retrieve riders.", 500)


@routes.post("/riders")
@auth_required
def create_rider():
    data = read_request_data()

    if not isinstance(data, dict):
        return error_response(
            "A valid JSON or form body is required.",
            400
        )

    errors, rider_data = validate_rider_data(data)

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": errors
        }), 400

    if Rider.query.filter_by(
        mobile=rider_data["mobile"]
    ).first():
        return error_response(
            "Mobile number already registered.",
            409
        )

    if Rider.query.filter_by(
        email=rider_data["email"]
    ).first():
        return error_response(
            "Email already registered.",
            409
        )

    image_file = request.files.get("profile_image")
    image_filename = None

    if image_file and image_file.filename:
        image_filename, image_error = save_rider_image(image_file)

        if image_error:
            return error_response(image_error, 400)

    rider = Rider(
        name=rider_data["name"],
        mobile=rider_data["mobile"],
        email=rider_data["email"],
        vehicle=rider_data["vehicle"],
        status=rider_data["status"],
        availability=rider_data["availability"],
        date=rider_data["date"],
        profile_image=image_filename
    )

    try:
        db.session.add(rider)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        delete_rider_image(image_filename)
        current_app.logger.exception("Unable to create rider.")
        return error_response("Database error occurred.", 500)

    return success_response(
        "Rider created successfully.",
        serialize_rider(rider),
        201
    )


@routes.get("/riders/<int:rider_id>")
@auth_required
def get_rider(rider_id):
    try:
        rider = db.session.get(Rider, rider_id)

        if rider is None:
            return error_response("Rider not found.", 404)

        return success_response(
            "Rider retrieved successfully.",
            serialize_rider(rider),
            200
        )

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception(
            "Unable to retrieve rider %s.", rider_id
        )
        return error_response(
            "Unable to retrieve rider details.", 500
        )


@routes.put("/riders/<int:rider_id>")
@auth_required
def update_rider(rider_id):
    rider = db.session.get(Rider, rider_id)

    if rider is None:
        return error_response("Rider not found.", 404)

    data = read_request_data()

    if not isinstance(data, dict):
        return error_response(
            "A valid JSON or form body is required.",
            400
        )

    errors, rider_data = validate_rider_data(data)

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed.",
            "errors": errors
        }), 400

    existing_mobile = Rider.query.filter(
        Rider.mobile == rider_data["mobile"],
        Rider.id != rider_id
    ).first()

    if existing_mobile:
        return error_response(
            "Mobile number already registered for another rider.",
            409
        )

    existing_email = Rider.query.filter(
        Rider.email == rider_data["email"],
        Rider.id != rider_id
    ).first()

    if existing_email:
        return error_response(
            "Email already registered for another rider.",
            409
        )

    image_file = request.files.get("profile_image")
    new_image_filename = None

    if image_file and image_file.filename:
        new_image_filename, image_error = save_rider_image(image_file)

        if image_error:
            return error_response(image_error, 400)

    old_image_filename = rider.profile_image

    rider.name = rider_data["name"]
    rider.mobile = rider_data["mobile"]
    rider.email = rider_data["email"]
    rider.vehicle = rider_data["vehicle"]
    rider.status = rider_data["status"]
    rider.availability = rider_data["availability"]
    rider.date = rider_data["date"]

    if new_image_filename:
        rider.profile_image = new_image_filename

    try:
        refresh_rider_availability(rider)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        delete_rider_image(new_image_filename)
        current_app.logger.exception(
            "Unable to update rider %s.", rider_id
        )
        return error_response("Database error occurred.", 500)

    if new_image_filename:
        delete_rider_image(old_image_filename)

    return success_response(
        "Rider updated successfully.",
        serialize_rider(rider)
    )


@routes.delete("/riders/<int:rider_id>")
@auth_required
def delete_rider(rider_id):
    rider = db.session.get(Rider, rider_id)

    if rider is None:
        return error_response("Rider not found.", 404)

    image_filename = rider.profile_image

    try:
        Order.query.filter_by(rider_id=rider.id).update(
            {"rider_id": None},
            synchronize_session=False
        )

        db.session.delete(rider)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception(
            "Unable to delete rider %s.", rider_id
        )
        return error_response("Unable to delete rider.", 500)

    delete_rider_image(image_filename)

    return success_response(
        "Rider deleted successfully.",
        {"id": rider_id}
    )


@routes.get("/orders")
@auth_required
def orders():
    try:
        page = max(request.args.get("page", 1, type=int), 1)
        page_size = min(
            max(request.args.get("pageSize", 10, type=int), 1),
            100
        )

        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().lower()
        rider_id = request.args.get("rider_id", type=int)

        query = Order.query

        if search:
            query = query.filter(
                Order.customer_name.ilike(f"%{search}%")
            )

        if status:
            query = query.filter(Order.status == status)

        if rider_id is not None:
            query = query.filter(Order.rider_id == rider_id)

        pagination = query.order_by(
            Order.created_at.desc()
        ).paginate(
            page=page,
            per_page=page_size,
            error_out=False
        )

        return success_response(
            "Orders retrieved successfully.",
            {
                "orders": [
                    serialize_order(order)
                    for order in pagination.items
                ],
                "page": pagination.page,
                "pageSize": pagination.per_page,
                "totalRecords": pagination.total,
                "totalPages": pagination.pages
            }
        )

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to retrieve orders.")
        return error_response("Unable to retrieve orders.", 500)


@routes.patch("/orders/<int:order_id>/assign-rider")
@auth_required
def assign_rider(order_id):
    order = db.session.get(Order, order_id)

    if order is None:
        return error_response("Order not found.", 404)

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response(
            "A valid JSON object is required.",
            400
        )

    previous_rider = order.rider
    rider_id = data.get("rider_id")

    if rider_id is None:
        order.rider_id = None
    else:
        try:
            rider_id = int(rider_id)
        except (TypeError, ValueError):
            return error_response("Invalid rider ID.", 400)

        rider = db.session.get(Rider, rider_id)

        if rider is None:
            return error_response("Rider not found.", 404)

        if rider.status != "active":
            return error_response(
                "Only active riders can be assigned.",
                400
            )

        order.rider_id = rider.id

    try:
        db.session.flush()

        if previous_rider:
            refresh_rider_availability(previous_rider)

        if order.rider and (
            previous_rider is None
            or order.rider.id != previous_rider.id
        ):
            refresh_rider_availability(order.rider)

        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to assign rider.")
        return error_response("Unable to assign rider.", 500)

    return success_response(
        "Order assignment updated successfully.",
        serialize_order(order)
    )


@routes.get("/dashboard")
@auth_required
def dashboard():
    try:
        total_orders = Order.query.count()

        delivered_orders = Order.query.filter_by(
            status="delivered"
        ).count()

        cancelled_orders = Order.query.filter_by(
            status="cancelled"
        ).count()

        in_progress_orders = Order.query.filter(
            Order.status.notin_(
                ["delivered", "cancelled", "completed"]
            )
        ).count()

        total_riders = Rider.query.count()

        active_riders = Rider.query.filter_by(
            status="active"
        ).count()

        available_riders = Rider.query.filter_by(
            availability="available",
            status="active"
        ).count()

        busy_riders = Rider.query.filter_by(
            availability="busy"
        ).count()

        recent_orders = Order.query.order_by(
            Order.created_at.desc()
        ).limit(5).all()

        available_rider_list = Rider.query.filter_by(
            status="active",
            availability="available"
        ).order_by(Rider.id.asc()).limit(10).all()

        data = {
            "summary": {
                "total_orders": total_orders,
                "delivered_orders": delivered_orders,
                "cancelled_orders": cancelled_orders,
                "in_progress_orders": in_progress_orders
            },
            "rider_summary": {
                "total": total_riders,
                "active": active_riders,
                "available": available_riders,
                "busy": busy_riders
            },
            "recent_orders": [
                {
                    "id": order.id,
                    "status": order.status,
                    "customer": order.customer_name,
                    "created_at": (
                        order.created_at.isoformat()
                        if order.created_at else None
                    ),
                    "rider_id": order.rider_id
                }
                for order in recent_orders
            ],
            "available_riders": [
                serialize_rider(rider)
                for rider in available_rider_list
            ]
        }

        return success_response(
            "Dashboard data retrieved successfully.",
            data
        )

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception(
            "Unable to retrieve dashboard."
        )
        return error_response("Unable to retrieve dashboard.", 500)


@routes.get("/profile")
@auth_required
def profile():
    user = db.session.get(User, request.user_id)

    if user is None:
        return error_response("User not found.", 404)

    return success_response(
        "Profile retrieved successfully.",
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile
        }
    )


@routes.get("/settings")
@auth_required
def settings():
    return success_response(
        "Settings retrieved successfully.",
        {
            "user_id": request.user_id,
            "settings": {
                "notifications": True,
                "dark_mode": False
            }
        }
    )