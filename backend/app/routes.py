from flask import Blueprint, Flask, request

from .extensions import db, bcrypt
from .models import User, Rider, Order
from .validators import validate_registration
from .Middleware import auth_required
from .responses import success_response, error_response

from .modules.auth import auth_bp
from .modules.riders import (
    riders_bp, serialize_rider, validate_rider_data, refresh_rider_availability
)
from .modules.orders import orders_bp, serialize_order, ORDER_STATUSES, TERMINAL_STATUSES
from .modules.dashboard import dashboard_bp
from .modules.profile import profile_bp
from .modules.settings import settings_bp
from .common.upload_service import (
    upload_rider_image, delete_rider_image, cloudinary_enabled,
    ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE
)

routes = Blueprint("routes", __name__)


def register_routes(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(riders_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(routes)


# REQUEST HELPERS

def read_request_data():
    if request.is_json:
        return request.get_json(silent=True)
    if request.form:
        return request.form.to_dict()
    return None


def get_user_id():
    return getattr(request, "user_id", None)
