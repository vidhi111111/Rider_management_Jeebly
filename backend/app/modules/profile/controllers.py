from flask import request
from ...common.responses import error_response, success_response
from ...common.middleware import get_current_user_id
from .services import ProfileService


class ProfileController:
    def __init__(self, profile_service: ProfileService = None):
        self.profile_service = profile_service or ProfileService()

    def get_profile(self):
        user_id = get_current_user_id()
        success, message, data, status_code = self.profile_service.get_profile(user_id)
        if not success:
            return error_response(message, status_code)
        return success_response(message, data, status_code)

    def update_profile(self):
        user_id = get_current_user_id()
        data = {}
        file = None
        if request.is_json:
            data = request.get_json(silent=True) or {}
        else:
            data = request.form.to_dict() if request.form else {}
            if "profile_image" in request.files:
                file = request.files["profile_image"]
            elif "avatar" in request.files:
                file = request.files["avatar"]
            elif "file" in request.files:
                file = request.files["file"]

        success, message, result, status_code = self.profile_service.update_profile(user_id, data, file=file)
        if not success:
            return error_response(message, status_code)
        return success_response(message, result, status_code)

    def upload_avatar(self):
        user_id = get_current_user_id()
        file = None
        if "profile_image" in request.files:
            file = request.files["profile_image"]
        elif "avatar" in request.files:
            file = request.files["avatar"]
        elif "file" in request.files:
            file = request.files["file"]

        if not file:
            return error_response("Please select a valid image file.", 400)

        success, message, result, status_code = self.profile_service.update_profile(user_id, {}, file=file)
        if not success:
            return error_response(message, status_code)
        return success_response("Profile photo uploaded successfully.", result, status_code)

    def remove_avatar(self):
        user_id = get_current_user_id()
        success, message, result, status_code = self.profile_service.update_profile(user_id, {"remove_photo": True})
        if not success:
            return error_response(message, status_code)
        return success_response("Profile photo removed successfully.", result, status_code)

    def change_password(self):
        user_id = get_current_user_id()
        data = request.get_json(silent=True)
        success, message, result, status_code = self.profile_service.change_password(user_id, data)
        if not success:
            return error_response(message, status_code)
        return success_response(message, result, status_code)
