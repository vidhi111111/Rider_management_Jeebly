from flask import Blueprint
from ...common.middleware import auth_required
from .controllers import SettingsController

settings_bp = Blueprint("settings", __name__)
controller = SettingsController()


@settings_bp.get("/settings")
@auth_required
def settings():
    return controller.get_settings()
