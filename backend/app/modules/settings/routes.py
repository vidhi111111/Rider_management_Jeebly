from flask import Blueprint
from ...common.middleware import auth_required
from .controllers import SettingsController

settings_bp = Blueprint("settings", __name__)
controller = SettingsController()


@settings_bp.get("/settings")
@auth_required
def settings():
    """
    Get user settings and preferences
    ---
    tags:
      - settings
    summary: Retrieve user configuration and preferences
    description: Retrieves application settings and preferences (e.g. notifications enabled, dark mode active) for the currently authenticated user. Requires JWT Bearer authorization.
    operationId: settings_get
    security:
      - Bearer: []
    produces:
      - application/json
    responses:
      200:
        description: Settings retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Settings retrieved successfully."
            data:
              $ref: '#/definitions/SettingsData'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.get_settings()
