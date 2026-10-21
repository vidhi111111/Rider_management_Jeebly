
import os
import uuid
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from flask import (
    Blueprint, Flask, current_app, jsonify, request,
    send_from_directory, url_for
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
TERMINAL_STATUSES = {"delivered", "cancelled", "completed"}

# Business workflow statuses. Keep these consistent with the frontend.
ORDER_STATUSES = {
    "pending", "accepted", "picked_up", "in_transit",
    "delivered", "cancelled"
}


def register_routes(app: Flask) -> None:
    app.register_blueprint(routes)


# =========================================================
# IMAGE HELPERS: CLOUDINARY OPTIONAL, LOCAL FALLBACK
# =========================================================

def cloudinary_enabled():
    return bool(
        current_app.config.get("CLOUDINARY_CLOUD_NAME")
        or os.getenv("CLOUDINARY_CLOUD_NAME")
    )


def upload_rider_image(file):
    if not file or not file.filename:
        return None, None

    safe_name = secure_filename(file.filename)
    if not safe_name or "." not in safe_name:
        return None, "Invalid image filename."

    extension = safe_name.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return None, "Only JPG, JPEG, PNG and WEBP images are allowed."

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)

    if size == 0:
        return None, "The selected image is empty."
    if size > MAX_IMAGE_SIZE:
        return None, "Image size must not exceed 5 MB."

    if cloudinary_enabled():
        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=(
                    current_app.config.get("CLOUDINARY_CLOUD_NAME")
                    or os.getenv("CLOUDINARY_CLOUD_NAME")
                ),
                api_key=(
                    current_app.config.get("CLOUDINARY_API_KEY")
                    or os.getenv("CLOUDINARY_API_KEY")
                ),
                api_secret=(
                    current_app.config.get("CLOUDINARY_API_SECRET")
                    or os.getenv("CLOUDINARY_API_SECRET")
                ),
                secure=True
            )

            result = cloudinary.uploader.upload(
                file,
                folder="jeebly/riders",
                resource_type="image"
            )
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "storage": "cloudinary"
            }, None

        except Exception:
            current_app.logger.exception("Cloudinary upload failed.")
            return None, "Unable to upload image to Cloudinary."

    # Local fallback when Cloudinary credentials are not configured.
    folder = Path(current_app.root_path) / "uploads"
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{extension}"

    try:
        file.save(str(folder / filename))
    except OSError:
        current_app.logger.exception("Local image upload failed.")
        return None, "Unable to save uploaded image."

    return {
        "url": url_for(
            "routes.rider_upload",
            filename=filename,
            _external=True
        ),
        "public_id": filename,
        "storage": "local"
    }, None


def delete_rider_image(image_value):
    if not image_value:
        return

    # Existing records may contain a Cloudinary URL or local filename.
    value = str(image_value)

    if "res.cloudinary.com/" in value:
        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=(
                    current_app.config.get("CLOUDINARY_CLOUD_NAME")
                    or os.getenv("CLOUDINARY_CLOUD_NAME")
                ),
                api_key=(
                    current_app.config.get("CLOUDINARY_API_KEY")
                    or os.getenv("CLOUDINARY_API_KEY")
                ),
                api_secret=(
                    current_app.config.get("CLOUDINARY_API_SECRET")
                    or os.getenv("CLOUDINARY_API_SECRET")
                ),
                secure=True
            )

            # URL alone does not safely identify every Cloudinary asset's
            # public_id. Do not guess and accidentally delete another asset.
            current_app.logger.info(
                "Cloudinary image retained; store public_id to enable deletion."
            )
        except Exception:
            current_app.logger.exception("Cloudinary cleanup failed.")
        return

    filename = os.path.basename(value)
    folder = Path(current_app.root_path) / "uploads"

    try:
        path = folder / filename
        if path.is_file():
            path.unlink()
    except OSError:
        current_app.logger.exception("Unable to delete local rider image.")


@routes.get("/rider-uploads/<path:filename>")
def rider_upload(filename):
    return send_from_directory(
        Path(current_app.root_path) / "uploads",
        filename
    )


# =========================================================
# SERIALIZATION
# =========================================================

def serialize_rider(rider):
    image = rider.profile_image

    # If stored value is already a URL, return it directly.
    if image and str(image).startswith(("https://", "http://")):
        image_url = image
    elif image:
        image_url = url_for(
            "routes.rider_upload",
            filename=image,
            _external=True
        )
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


def serialize_order(order):
    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "mobile": order.mobile,
        "pickup": order.pickup,
        "delivery": order.delivery,
        "amount": float(order.amount) if order.amount is not None else None,
        "currency": order.currency,
        "status": order.status,
        "created_at": (
            order.created_at.isoformat()
            if order.created_at else None
        ),
        "rider_id": order.rider_id,
        "rider": serialize_rider(order.rider) if order.rider else None
    }


# =========================================================
# REQUEST HELPERS
# =========================================================

def read_request_data():
    if request.is_json:
        return request.get_json(silent=True)
    if request.form:
        return request.form.to_dict()
    return None


def get_user_id():
    return getattr(request, "user_id", None)


# =========================================================
# RIDER VALIDATION AND AVAILABILITY
# =========================================================

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
    if rider.status in {"inactive", "absent", "scheduled_break"}:
        rider.availability = "unavailable"
        return

    active_orders = Order.query.filter(
        Order.rider_id == rider.id,
        db.func.lower(Order.status).notin_(
            ["delivered", "cancelled", "completed"]
        )
    ).count()

    if active_orders > 0:
        rider.availability = "busy"
        rider.status = "on_order"
    else:
        rider.availability = "available"
        if rider.status == "on_order":
            rider.status = "active"

    if active_orders:
        rider.availability = "busy"
        if rider.status in {"active", "available"}:
            rider.status = "on_order"
    else:
        rider.availability = "available"
        if rider.status == "on_order":
            rider.status = "active"


# =========================================================
# HEALTH, REGISTRATION AND LOGIN
# =========================================================

@routes.get("/health")
def health():
    return jsonify({
        "success": True,
        "message": "Flask API is running."
    }), 200


@routes.post("/register")
def register():
    if not request.is_json:
        return error_response("Content-Type must be application/json.", 415)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("A valid JSON object is required.", 400)

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
        password=bcrypt.generate_password_hash(password).decode("utf-8")
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
        return error_response("Content-Type must be application/json.", 415)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("A valid JSON object is required.", 400)

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return error_response("Email and password are required.", 400)

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return error_response("Invalid email or password.", 401)

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=2)
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


# =========================================================
# RIDER LIST AND DETAILS
# =========================================================

@routes.get("/riders")
@auth_required
def riders():
    try:
        page = max(request.args.get("page", 1, type=int), 1)
        page_size = min(max(request.args.get("pageSize", 10, type=int), 1), 100)
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().lower()
        availability = request.args.get("availability", "").strip().lower()
        sort_by = request.args.get("sortBy", "id").strip()
        sort_order = request.args.get("sortOrder", "asc").strip().lower()

        query = Rider.query

        if search:
            value = f"%{search}%"
            query = query.filter(or_(
                Rider.name.ilike(value),
                Rider.mobile.ilike(value),
                Rider.email.ilike(value)
            ))

        if status:
            query = query.filter(db.func.lower(Rider.status) == status)

        if availability in {"available", "busy", "unavailable"}:
            query = query.filter(Rider.availability == availability)

        sort_columns = {
            "id": Rider.id, "name": Rider.name,
            "mobile": Rider.mobile, "email": Rider.email,
            "vehicle": Rider.vehicle, "status": Rider.status,
            "availability": Rider.availability, "date": Rider.date
        }
        column = sort_columns.get(sort_by, Rider.id)
        query = query.order_by(
            column.desc() if sort_order == "desc" else column.asc()
        )

        pagination = query.paginate(
            page=page, per_page=page_size, error_out=False
        )

        return success_response("Riders retrieved successfully.", {
            "riders": [serialize_rider(r) for r in pagination.items],
            "page": pagination.page,
            "pageSize": pagination.per_page,
            "totalRecords": pagination.total,
            "totalPages": pagination.pages
        })
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to retrieve riders.")
        return error_response("Unable to retrieve riders.", 500)


@routes.get("/riders/available")
@auth_required
def available_riders():
    try:
        # Reconcile availability before returning the list.
        rider_list = Rider.query.order_by(Rider.name.asc()).all()
        for rider in rider_list:
            refresh_rider_availability(rider)
        db.session.commit()

        eligible = [
            r for r in rider_list
            if r.availability == "available"
            and r.status not in {
                "inactive", "absent", "scheduled_break", "on_order"
            }
        ]

        return success_response("Available riders retrieved successfully.", {
            "riders": [serialize_rider(r) for r in eligible]
        })
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to retrieve available riders.")
        return error_response("Unable to retrieve available riders.", 500)


@routes.get("/riders/<int:rider_id>")
@auth_required
def get_rider(rider_id):
    rider = db.session.get(Rider, rider_id)
    if rider is None:
        return error_response("Rider not found.", 404)
    return success_response("Rider retrieved successfully.", serialize_rider(rider))


@routes.post("/riders")
@auth_required
def create_rider():
    data = read_request_data()
    if not isinstance(data, dict):
        return error_response("A valid JSON or form body is required.", 400)

    errors, values = validate_rider_data(data)
    if errors:
        return jsonify({
            "success": False, "message": "Validation failed.", "errors": errors
        }), 400

    if Rider.query.filter_by(mobile=values["mobile"]).first():
        return error_response("Mobile number already registered.", 409)
    if Rider.query.filter_by(email=values["email"]).first():
        return error_response("Email already registered.", 409)

    uploaded = None
    image_file = request.files.get("profile_image")
    if image_file and image_file.filename:
        uploaded, image_error = upload_rider_image(image_file)
        if image_error:
            return error_response(image_error, 400)

    # NOTE: profile_image stores a string in the existing model.
    image_value = uploaded["url"] if uploaded else None

    rider = Rider(
        name=values["name"],
        mobile=values["mobile"],
        email=values["email"],
        vehicle=values["vehicle"],
        status=values["status"],
        availability=values["availability"],
        date=values["date"],
        profile_image=image_value
    )

    try:
        db.session.add(rider)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to create rider.")
        return error_response("Database error occurred.", 500)

    return success_response("Rider created successfully.", serialize_rider(rider), 201)


@routes.put("/riders/<int:rider_id>")
@auth_required
def update_rider(rider_id):
    rider = db.session.get(Rider, rider_id)
    if rider is None:
        return error_response("Rider not found.", 404)

    data = read_request_data()
    if not isinstance(data, dict):
        return error_response("A valid JSON or form body is required.", 400)

    errors, values = validate_rider_data(data)
    if errors:
        return jsonify({
            "success": False, "message": "Validation failed.", "errors": errors
        }), 400

    if Rider.query.filter(
        Rider.mobile == values["mobile"], Rider.id != rider_id
    ).first():
        return error_response("Mobile number already registered for another rider.", 409)

    if Rider.query.filter(
        Rider.email == values["email"], Rider.id != rider_id
    ).first():
        return error_response("Email already registered for another rider.", 409)

    image_file = request.files.get("profile_image")
    new_image = None
    if image_file and image_file.filename:
        new_image, image_error = upload_rider_image(image_file)
        if image_error:
            return error_response(image_error, 400)

    rider.name = values["name"]
    rider.mobile = values["mobile"]
    rider.email = values["email"]
    rider.vehicle = values["vehicle"]
    rider.status = values["status"]
    rider.availability = values["availability"]
    rider.date = values["date"]

    if new_image:
        old_image = rider.profile_image
        rider.profile_image = new_image["url"]
    else:
        old_image = None

    try:
        refresh_rider_availability(rider)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to update rider.")
        return error_response("Database error occurred.", 500)

    if old_image:
        delete_rider_image(old_image)

    return success_response("Rider updated successfully.", serialize_rider(rider))


@routes.delete("/riders/<int:rider_id>")
@auth_required
def delete_rider(rider_id):
    rider = db.session.get(Rider, rider_id)
    if rider is None:
        return error_response("Rider not found.", 404)

    try:
        Order.query.filter_by(rider_id=rider.id).update(
            {"rider_id": None}, synchronize_session=False
        )
        image = rider.profile_image
        db.session.delete(rider)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to delete rider.")
        return error_response("Unable to delete rider.", 500)

    delete_rider_image(image)
    return success_response("Rider deleted successfully.", {"id": rider_id})


# =========================================================
# ORDERS: SERVER-SIDE SEARCH, FILTERS, SORTING, PAGINATION
# =========================================================

@routes.get("/orders")
@auth_required
def orders():
    try:
        page = max(request.args.get("page", 1, type=int), 1)
        page_size = min(max(request.args.get("pageSize", 10, type=int), 1), 100)
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().lower()
        rider_id = request.args.get("rider_id", type=int)
        order_date = request.args.get("order_date", "").strip()
        sort_by = request.args.get("sortBy", "newest").strip().lower()

        query = Order.query

        if search:
            value = f"%{search}%"
            conditions = [
                Order.customer_name.ilike(value),
                Order.mobile.ilike(value)
            ]
            if search.isdigit():
                conditions.append(Order.id == int(search))
            query = query.filter(or_(*conditions))

        if status:
            query = query.filter(db.func.lower(Order.status) == status)

        if rider_id is not None:
            query = query.filter(Order.rider_id == rider_id)

        if order_date:
            try:
                parsed_date = datetime.strptime(order_date, "%Y-%m-%d").date()
                query = query.filter(db.func.date(Order.created_at) == parsed_date)
            except ValueError:
                return error_response("Invalid order_date. Use YYYY-MM-DD.", 400)

        if sort_by == "oldest":
            query = query.order_by(Order.created_at.asc(), Order.id.asc())
        else:
            query = query.order_by(Order.created_at.desc(), Order.id.desc())

        pagination = query.paginate(
            page=page, per_page=page_size, error_out=False
        )

        return success_response("Orders retrieved successfully.", {
            "orders": [serialize_order(o) for o in pagination.items],
            "page": pagination.page,
            "pageSize": pagination.per_page,
            "totalRecords": pagination.total,
            "totalPages": pagination.pages
        })
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to retrieve orders.")
        return error_response("Unable to retrieve orders.", 500)


@routes.post("/orders")
@auth_required
def create_order():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("A valid JSON object is required.", 400)

    customer_name = str(data.get("customer_name", "")).strip()
    mobile = str(data.get("mobile") or "").strip()
    pickup = str(data.get("pickup") or "").strip()
    delivery = str(data.get("delivery") or "").strip()
    currency = str(data.get("currency") or "AED").strip().upper()

    if not customer_name:
        return error_response("Customer name is required.", 400)
    if len(customer_name) > 100:
        return error_response("Customer name cannot exceed 100 characters.", 400)
    if len(mobile) > 20:
        return error_response("Mobile number cannot exceed 20 characters.", 400)
    if len(pickup) > 255 or len(delivery) > 255:
        return error_response("Pickup and delivery must not exceed 255 characters.", 400)
    if not currency or len(currency) > 10:
        return error_response("Invalid currency.", 400)

    amount = data.get("amount")
    if amount is not None:
        try:
            amount = float(amount)
            if not math.isfinite(amount) or amount < 0:
                raise ValueError
        except (TypeError, ValueError):
            return error_response("Amount must be a valid non-negative number.", 400)

    order = Order(
        customer_name=customer_name,
        mobile=mobile or None,
        pickup=pickup or None,
        delivery=delivery or None,
        amount=amount,
        currency=currency,
        status="pending",
        rider_id=None
    )

    try:
        db.session.add(order)
        db.session.commit()
        return success_response("Order created successfully.", serialize_order(order), 201)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to create order.")
        return error_response("Unable to create order.", 500)


@routes.get("/orders/<int:order_id>")
@auth_required
def get_order(order_id):
    order = db.session.get(Order, order_id)
    if order is None:
        return error_response("Order not found.", 404)
    return success_response("Order details retrieved successfully.", serialize_order(order))


@routes.patch("/orders/<int:order_id>/status")
@auth_required
def update_order_status(order_id):
    try:
        order = db.session.get(Order, order_id)
        if order is None:
            return error_response("Order not found.", 404)

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error_response("A valid JSON body is required.", 400)

        new_status = str(data.get("status", "")).strip().lower()
        if new_status not in ORDER_STATUSES:
            return error_response("Invalid order status.", 400)

        current_status = str(order.status or "").strip().lower()
        if current_status in TERMINAL_STATUSES:
            return error_response(
                "Delivered or cancelled orders cannot be changed.", 409
            )

        order.status = new_status
        db.session.flush()

        if order.rider:
            refresh_rider_availability(order.rider)

        db.session.commit()
        return success_response(
            "Order status updated successfully.", serialize_order(order)
        )
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to update order status.")
        return error_response("Unable to update order status.", 500)


@routes.post("/orders/<int:order_id>/assign-rider")
@routes.patch("/orders/<int:order_id>/assign-rider")
@auth_required
def assign_rider(order_id):
    try:
        order = db.session.get(Order, order_id)
        if order is None:
            return error_response("Order not found.", 404)

        if str(order.status or "").lower() in TERMINAL_STATUSES:
            return error_response("Cannot assign a rider to a terminal order.", 409)

        data = request.get_json(silent=True)
        if not isinstance(data, dict) or "rider_id" not in data:
            return error_response("A JSON object containing rider_id is required.", 400)

        previous_rider = order.rider
        requested_id = data.get("rider_id")

        if requested_id is None:
            order.rider_id = None
        else:
            try:
                requested_id = int(requested_id)
                if requested_id <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                return error_response("Invalid rider ID.", 400)

            rider = db.session.get(Rider, requested_id)
            if rider is None:
                return error_response("Rider not found.", 404)

            # Do not reassign an order to its current rider as a duplicate.
            if order.rider_id != rider.id:
                if rider.status in {"inactive", "absent", "scheduled_break", "on_order"}:
                    return error_response("Only eligible riders can be assigned.", 409)

                if rider.availability != "available":
                    return error_response("Only available riders can be assigned.", 409)

            order.rider_id = rider.id

        db.session.flush()

        if previous_rider:
            refresh_rider_availability(previous_rider)

        current_rider = order.rider
        if current_rider:
            refresh_rider_availability(current_rider)

        db.session.commit()
        return success_response(
            "Order assignment updated successfully.", serialize_order(order)
        )
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to assign rider.")
        return error_response("Unable to assign rider.", 500)

# DASHBOARD

@routes.get("/dashboard")
@auth_required
def dashboard():
    try:
        total_orders = Order.query.count()
        delivered = Order.query.filter(
            db.func.lower(Order.status).in_(["delivered", "completed"])
        ).count()
        cancelled = Order.query.filter(
            db.func.lower(Order.status) == "cancelled"
        ).count()
        in_progress = Order.query.filter(
            db.func.lower(Order.status).notin_(list(TERMINAL_STATUSES))
        ).count()

        riders_list = Rider.query.all()
        for rider in riders_list:
            refresh_rider_availability(rider)
        db.session.commit()

        available_riders = [
            r for r in riders_list if r.availability == "available"
        ]
        busy_riders = [r for r in riders_list if r.availability == "busy"]

        recent_orders = Order.query.order_by(
            Order.created_at.desc(), Order.id.desc()
        ).limit(5).all()

        return success_response("Dashboard data retrieved successfully.", {
            "summary": {
                "total_orders": total_orders,
                "delivered_orders": delivered,
                "cancelled_orders": cancelled,
                "in_progress_orders": in_progress
            },
            "rider_summary": {
                "total": len(riders_list),
                "active": sum(1 for r in riders_list if r.status not in {"inactive", "absent"}),
                "available": len(available_riders),
                "busy": len(busy_riders)
            },
            "recent_orders": [{
                "id": o.id,
                "status": o.status,
                "customer": o.customer_name,
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "rider_id": o.rider_id
            } for o in recent_orders],
            "available_riders": [serialize_rider(r) for r in available_riders[:10]]
        })
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to retrieve dashboard.")
        return error_response("Unable to retrieve dashboard.", 500)


# =========================================================
# PROFILE AND CHANGE PASSWORD
# =========================================================

@routes.get("/profile")
@auth_required
def profile():
    user = db.session.get(User, get_user_id())
    if user is None:
        return error_response("User not found.", 404)

    return success_response("Profile retrieved successfully.", {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "mobile": user.mobile
    })


@routes.put("/profile")
@auth_required
def update_profile():
    user = db.session.get(User, get_user_id())
    if user is None:
        return error_response("User not found.", 404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("A valid JSON object is required.", 400)

    name = str(data.get("name", user.name)).strip()
    mobile = str(data.get("mobile", user.mobile)).strip()

    if not name or len(name) > 100:
        return error_response("Name is required and must be at most 100 characters.", 400)
    if not mobile.isdigit() or len(mobile) != 10:
        return error_response("Mobile number must contain exactly 10 digits.", 400)

    duplicate = User.query.filter(
        User.mobile == mobile, User.id != user.id
    ).first()
    if duplicate:
        return error_response("Mobile number already registered.", 409)

    user.name = name
    user.mobile = mobile

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to update profile.")
        return error_response("Unable to update profile.", 500)

    return success_response("Profile updated successfully.", {
        "id": user.id, "name": user.name,
        "email": user.email, "mobile": user.mobile
    })


@routes.put("/change-password")
@auth_required
def change_password():
    user = db.session.get(User, get_user_id())
    if user is None:
        return error_response("User not found.", 404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("A valid JSON object is required.", 400)

    current_password = str(data.get("current_password", ""))
    new_password = str(data.get("new_password", ""))

    if not current_password or not new_password:
        return error_response("Current and new passwords are required.", 400)

    if not bcrypt.check_password_hash(user.password, current_password):
        return error_response("Current password is incorrect.", 400)

    if len(new_password) < 8:
        return error_response("New password must be at least 8 characters.", 400)

    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Unable to change password.")
        return error_response("Unable to change password.", 500)

    return success_response("Password changed successfully.", None)


# =========================================================
# SETTINGS
# =========================================================

@routes.get("/settings")
@auth_required
def settings():
    return success_response("Settings retrieved successfully.", {
        "user_id": get_user_id(),
        "settings": {
            "notifications": True,
            "dark_mode": True
        }
    })
