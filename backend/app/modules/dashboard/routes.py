from flask import Blueprint
from ...common.middleware import auth_required
from .controllers import DashboardController

dashboard_bp = Blueprint("dashboard", __name__)
controller = DashboardController()


@dashboard_bp.get("/dashboard")
@auth_required
def dashboard():
    """
    Get aggregated dashboard metrics
    ---
    tags:
      - dashboard
    summary: Retrieve operational dashboard analytics
    description: Fetches consolidated analytics for the management overview, including order status counts (total, delivered, cancelled, in_progress), rider availability metrics (total, active, available, busy), the 5 most recent orders, and the list of currently available riders. Requires JWT Bearer authorization.
    operationId: dashboard_get
    security:
      - Bearer: []
    produces:
      - application/json
    responses:
      200:
        description: Dashboard data retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Dashboard data retrieved successfully."
            data:
              $ref: '#/definitions/DashboardData'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.get_dashboard()
