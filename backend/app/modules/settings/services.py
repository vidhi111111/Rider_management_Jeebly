class SettingsService:
    @staticmethod
    def get_settings(user_id: int):
        return {
            "user_id": user_id,
            "settings": {
                "notifications": True,
                "dark_mode": True
            }
        }
