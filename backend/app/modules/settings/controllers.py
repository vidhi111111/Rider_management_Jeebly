from ...common.responses import success_response
from ...common.middleware import get_current_user_id
from .services import SettingsService


class SettingsController:
    def __init__(self, settings_service: SettingsService = None):
        self.settings_service = settings_service or SettingsService()

    def get_settings(self):
        user_id = get_current_user_id()
        data = self.settings_service.get_settings(user_id)
        return success_response("Settings retrieved successfully.", data, 200)
