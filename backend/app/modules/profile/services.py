from typing import Tuple, Any, Dict
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ...extensions import bcrypt
from ...common.upload_service import upload_rider_image, delete_rider_image
from .repositories import ProfileRepository
from .schemas import (
    validate_profile_payload, validate_change_password_payload, serialize_profile
)


class ProfileService:
    def __init__(self, profile_repo: ProfileRepository = None):
        self.profile_repo = profile_repo or ProfileRepository()

    def get_profile(self, user_id: int) -> Tuple[bool, str, Any, int]:
        if not user_id:
            return False, "User not found.", None, 404

        user = self.profile_repo.get_by_id(user_id)
        if user is None:
            return False, "User not found.", None, 404

        return True, "Profile retrieved successfully.", serialize_profile(user), 200

    def update_profile(self, user_id: int, data: Dict[str, Any], file=None) -> Tuple[bool, str, Any, int]:
        if not user_id:
            return False, "User not found.", None, 404

        user = self.profile_repo.get_by_id(user_id)
        if user is None:
            return False, "User not found.", None, 404

        valid, err_msg, values = validate_profile_payload(data or {}, user.name, user.mobile)
        if not valid:
            return False, err_msg, None, 400

        if values.get("mobile") and values["mobile"] != user.mobile:
            duplicate = self.profile_repo.find_duplicate_mobile(values["mobile"], user.id)
            if duplicate:
                return False, "Mobile number already registered.", None, 409
            user.mobile = values["mobile"]

        if values.get("name"):
            user.name = values["name"]

        # Handle profile image file upload
        if file:
            img_data, img_err = upload_rider_image(file)
            if img_err:
                return False, img_err, None, 400
            if img_data and "url" in img_data:
                # Cleanup old image if local
                if user.profile_image:
                    delete_rider_image(user.profile_image)
                user.profile_image = img_data["url"]
        elif values.get("remove_photo"):
            if user.profile_image:
                delete_rider_image(user.profile_image)
            user.profile_image = None
        elif values.get("profile_image") is not None:
            user.profile_image = values["profile_image"]

        try:
            self.profile_repo.commit()
            return True, "Profile updated successfully.", serialize_profile(user), 200
        except SQLAlchemyError:
            self.profile_repo.rollback()
            current_app.logger.exception("Unable to update profile.")
            return False, "Unable to update profile.", None, 500

    def change_password(self, user_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Any, int]:
        if not user_id:
            return False, "User not found.", None, 404

        user = self.profile_repo.get_by_id(user_id)
        if user is None:
            return False, "User not found.", None, 404

        valid, err_msg, current_password, new_password = validate_change_password_payload(data)
        if not valid:
            return False, err_msg, None, 400

        if not bcrypt.check_password_hash(user.password, current_password):
            return False, "Current password is incorrect.", None, 400

        user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

        try:
            self.profile_repo.commit()
            return True, "Password changed successfully.", None, 200
        except SQLAlchemyError:
            self.profile_repo.rollback()
            current_app.logger.exception("Unable to change password.")
            return False, "Unable to change password.", None, 500
