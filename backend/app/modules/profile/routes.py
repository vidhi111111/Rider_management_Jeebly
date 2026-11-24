from flask import Blueprint
from ...common.middleware import auth_required
from .controllers import ProfileController

profile_bp = Blueprint("profile", __name__)
controller = ProfileController()


@profile_bp.get("/profile")
@auth_required
def profile():
    """
    Get authenticated user profile
    ---
    tags:
      - profile
    summary: Retrieve current user profile
    description: Retrieves profile details (id, name, email, mobile) for the currently authenticated user identified from the JWT Bearer token. Requires JWT Bearer authorization.
    operationId: profile_get
    security:
      - Bearer: []
    produces:
      - application/json
    responses:
      200:
        description: Profile retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Profile retrieved successfully."
            data:
              $ref: '#/definitions/User'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: User not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.get_profile()


@profile_bp.put("/profile")
@auth_required
def update_profile():
    """
    Update authenticated user profile
    ---
    tags:
      - profile
    summary: Update profile name and mobile
    description: Updates the full name and mobile number for the authenticated user. Marshmallow validation enforces non-empty name (max 100 characters) and mobile number consisting of exactly 10 digits. Validates uniqueness of mobile number across other users. Requires JWT Bearer authorization.
    operationId: profile_update
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Profile update payload
        schema:
          $ref: '#/definitions/UpdateProfileRequest'
    responses:
      200:
        description: Profile updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Profile updated successfully."
            data:
              $ref: '#/definitions/User'
      400:
        description: Validation failed (e.g. invalid name or mobile)
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Unauthorized (Missing, invalid, or expired Bearer token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: User not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      409:
        description: Conflict - Mobile number already registered by another user
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.update_profile()


@profile_bp.put("/change-password")
@auth_required
def change_password():
    """
    Change account password
    ---
    tags:
      - profile
    summary: Change user account password
    description: Updates the account password for the currently authenticated user. Verifies the current password using bcrypt and validates that the new password is at least 8 characters long. Requires JWT Bearer authorization.
    operationId: profile_change_password
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        description: Current and new password payload
        schema:
          $ref: '#/definitions/ChangePasswordRequest'
    responses:
      200:
        description: Password updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Password updated successfully."
      400:
        description: Validation failed (missing passwords or new password < 8 characters)
        schema:
          $ref: '#/definitions/ErrorResponse'
      401:
        description: Unauthorized (Current password is incorrect, or missing/invalid token)
        schema:
          $ref: '#/definitions/ErrorResponse'
      404:
        description: User not found
        schema:
          $ref: '#/definitions/ErrorResponse'
      500:
        description: Internal server or database error
        schema:
          $ref: '#/definitions/ErrorResponse'
    """
    return controller.change_password()


@profile_bp.post("/profile/avatar")
@auth_required
def upload_avatar():
    """Upload user profile avatar"""
    return controller.upload_avatar()


@profile_bp.delete("/profile/avatar")
@auth_required
def remove_avatar():
    """Remove user profile avatar"""
    return controller.remove_avatar()


@profile_bp.get("/profile-uploads/<path:filename>")
def profile_upload_file(filename):
    """Serve uploaded profile photo from server uploads directory"""
    import os
    from pathlib import Path
    from flask import current_app, send_from_directory
    folder = Path(current_app.root_path) / "uploads"
    return send_from_directory(str(folder), filename)
