from flask import Blueprint
from ...common.middleware import auth_required
from .controllers import ProfileController

profile_bp = Blueprint("profile", __name__)
controller = ProfileController()


@profile_bp.get("/profile")
@auth_required
def profile():
    return controller.get_profile()


@profile_bp.put("/profile")
@auth_required
def update_profile():
    return controller.update_profile()


@profile_bp.put("/change-password")
@auth_required
def change_password():
    return controller.change_password()
