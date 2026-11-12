from ...common.responses import error_response, success_response
from .services import DashboardService


class DashboardController:
    def __init__(self, dashboard_service: DashboardService = None):
        self.dashboard_service = dashboard_service or DashboardService()

    def get_dashboard(self):
        success, message, data, status_code = self.dashboard_service.get_dashboard_data()
        if not success:
            return error_response(message, status_code)
        return success_response(message, data, status_code)
