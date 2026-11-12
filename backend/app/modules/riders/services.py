from typing import Optional, Dict, Any, Tuple
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ...common.upload_service import upload_rider_image, delete_rider_image
from .repositories import RiderRepository
from .schemas import serialize_rider

TERMINAL_STATUSES = {"delivered", "cancelled", "completed"}


def refresh_rider_availability(rider) -> None:
    if rider is None:
        return

    if rider.status in {"inactive", "absent", "scheduled_break"}:
        rider.availability = "unavailable"
        return

    active_orders = RiderRepository.count_active_orders_for_rider(
        rider.id, TERMINAL_STATUSES
    )

    if active_orders > 0:
        rider.availability = "busy"
        if rider.status in {"active", "available"}:
            rider.status = "on_order"
    else:
        rider.availability = "available"
        if rider.status == "on_order":
            rider.status = "active"


class RiderService:
    def __init__(self, rider_repo: RiderRepository = None):
        self.rider_repo = rider_repo or RiderRepository()

    def get_paginated_riders(
        self,
        page: int,
        page_size: int,
        search: str,
        status: str,
        availability: str,
        sort_by: str,
        sort_order: str
    ) -> Tuple[bool, str, Any, int]:
        try:
            pagination = self.rider_repo.filter_and_paginate(
                search=search,
                status=status,
                availability=availability,
                sort_by=sort_by,
                sort_order=sort_order,
                page=page,
                page_size=page_size
            )

            data = {
                "riders": [serialize_rider(r) for r in pagination.items],
                "page": pagination.page,
                "pageSize": pagination.per_page,
                "totalRecords": pagination.total,
                "totalPages": pagination.pages
            }
            return True, "Riders retrieved successfully.", data, 200

        except SQLAlchemyError:
            self.rider_repo.rollback()
            current_app.logger.exception("Unable to retrieve riders.")
            return False, "Unable to retrieve riders.", None, 500

    def get_available_riders(self) -> Tuple[bool, str, Any, int]:
        try:
            rider_list = self.rider_repo.get_all(order_by_name=True)
            for rider in rider_list:
                refresh_rider_availability(rider)
            self.rider_repo.commit()

            eligible = [
                r for r in rider_list
                if r.availability == "available"
                and r.status not in {
                    "inactive", "absent", "scheduled_break", "on_order"
                }
            ]

            return True, "Available riders retrieved successfully.", {
                "riders": [serialize_rider(r) for r in eligible]
            }, 200

        except SQLAlchemyError:
            self.rider_repo.rollback()
            current_app.logger.exception("Unable to retrieve available riders.")
            return False, "Unable to retrieve available riders.", None, 500

    def get_rider_by_id(self, rider_id: int) -> Tuple[bool, str, Any, int]:
        rider = self.rider_repo.get_by_id(rider_id)
        if rider is None:
            return False, "Rider not found.", None, 404
        return True, "Rider retrieved successfully.", serialize_rider(rider), 200

    def create_rider(self, values: Dict[str, Any], image_file=None) -> Tuple[bool, str, Any, int]:
        if self.rider_repo.get_by_mobile(values["mobile"]):
            return False, "Mobile number already registered.", None, 409

        if self.rider_repo.get_by_email(values["email"]):
            return False, "Email already registered.", None, 409

        uploaded = None
        if image_file and image_file.filename:
            uploaded, image_error = upload_rider_image(image_file)
            if image_error:
                return False, image_error, None, 400

        image_value = uploaded["url"] if uploaded else None
        rider = self.rider_repo.create(values, profile_image=image_value)

        try:
            self.rider_repo.commit()
        except SQLAlchemyError:
            self.rider_repo.rollback()
            current_app.logger.exception("Unable to create rider.")
            return False, "Database error occurred.", None, 500

        return True, "Rider created successfully.", serialize_rider(rider), 201

    def update_rider(self, rider_id: int, values: Dict[str, Any], image_file=None) -> Tuple[bool, str, Any, int]:
        rider = self.rider_repo.get_by_id(rider_id)
        if rider is None:
            return False, "Rider not found.", None, 404

        if self.rider_repo.find_duplicate_mobile(values["mobile"], rider_id):
            return False, "Mobile number already registered for another rider.", None, 409

        if self.rider_repo.find_duplicate_email(values["email"], rider_id):
            return False, "Email already registered for another rider.", None, 409

        new_image = None
        if image_file and image_file.filename:
            new_image, image_error = upload_rider_image(image_file)
            if image_error:
                return False, image_error, None, 400

        rider.name = values["name"]
        rider.mobile = values["mobile"]
        rider.email = values["email"]
        rider.vehicle = values["vehicle"]
        rider.status = values["status"]
        rider.availability = values["availability"]
        rider.date = values["date"]

        if new_image:
            old_image = rider.profile_image
            rider.profile_image = new_image["url"]
        elif values.get("remove_photo"):
            old_image = rider.profile_image
            rider.profile_image = None
        else:
            old_image = None

        try:
            refresh_rider_availability(rider)
            self.rider_repo.commit()
        except SQLAlchemyError:
            self.rider_repo.rollback()
            current_app.logger.exception("Unable to update rider.")
            return False, "Database error occurred.", None, 500

        if old_image:
            delete_rider_image(old_image)

        return True, "Rider updated successfully.", serialize_rider(rider), 200

    def delete_rider(self, rider_id: int) -> Tuple[bool, str, Any, int]:
        rider = self.rider_repo.get_by_id(rider_id)
        if rider is None:
            return False, "Rider not found.", None, 404

        try:
            self.rider_repo.unlink_orders(rider.id)
            image = rider.profile_image
            self.rider_repo.delete(rider)
            self.rider_repo.commit()
        except SQLAlchemyError:
            self.rider_repo.rollback()
            current_app.logger.exception("Unable to delete rider.")
            return False, "Unable to delete rider.", None, 500

        delete_rider_image(image)
        return True, "Rider deleted successfully.", {"id": rider_id}, 200
