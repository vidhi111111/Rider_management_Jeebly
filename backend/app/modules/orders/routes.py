from flask import Blueprint
from ...common.middleware import auth_required
from .controllers import OrderController

orders_bp = Blueprint("orders", __name__)
controller = OrderController()


@orders_bp.get("/orders")
@auth_required
def orders():
    return controller.get_orders()


@orders_bp.post("/orders")
@auth_required
def create_order():
    return controller.create_order()


@orders_bp.get("/orders/<int:order_id>")
@auth_required
def get_order(order_id):
    return controller.get_order(order_id)


@orders_bp.put("/orders/<int:order_id>")
@auth_required
def update_order(order_id):
    return controller.update_order(order_id)


@orders_bp.patch("/orders/<int:order_id>/status")
@auth_required
def update_order_status(order_id):
    return controller.update_order_status(order_id)


@orders_bp.post("/orders/<int:order_id>/assign-rider")
@orders_bp.patch("/orders/<int:order_id>/assign-rider")
@auth_required
def assign_rider(order_id):
    return controller.assign_rider(order_id)


@orders_bp.delete("/orders/<int:order_id>")
@auth_required
def delete_order(order_id):
    return controller.delete_order(order_id)
