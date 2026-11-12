from flask import Blueprint
from ...common.middleware import auth_required
from .controllers import RiderController

riders_bp = Blueprint("riders", __name__)
controller = RiderController()


@riders_bp.get("/riders")
@auth_required
def riders():
    return controller.get_riders()


@riders_bp.get("/riders/available")
@auth_required
def available_riders():
    return controller.get_available_riders()


@riders_bp.get("/riders/<int:rider_id>")
@auth_required
def get_rider(rider_id):
    return controller.get_rider(rider_id)


@riders_bp.post("/riders")
@auth_required
def create_rider():
    return controller.create_rider()


@riders_bp.put("/riders/<int:rider_id>")
@auth_required
def update_rider(rider_id):
    return controller.update_rider(rider_id)


@riders_bp.delete("/riders/<int:rider_id>")
@auth_required
def delete_rider(rider_id):
    return controller.delete_rider(rider_id)


@riders_bp.get("/rider-uploads/<path:filename>")
def rider_upload(filename):
    return controller.serve_upload(filename)
