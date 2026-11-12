from flask import Blueprint
from ...common.middleware import auth_required
from .controllers import DashboardController

dashboard_bp = Blueprint("dashboard", __name__)
controller = DashboardController()


@dashboard_bp.get("/dashboard")
@auth_required
def dashboard():
    return controller.get_dashboard()
