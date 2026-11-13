from .schemas import settings_response_schema


class SettingsService:
    @staticmethod
    def get_settings(user_id: int):
        raw_data = {
            "user_id": user_id,
            "settings": {
                "notifications": True,
                "dark_mode": True
            }
        }
        return settings_response_schema.dump(raw_data)
