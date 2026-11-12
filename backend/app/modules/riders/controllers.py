from pathlib import Path
from flask import request, jsonify, current_app, send_from_directory

from ...common.responses import error_response, success_response
from .schemas import validate_rider_data
from .services import RiderService


def read_request_data():
    if request.is_json:
        return request.get_json(silent=True)
    if request.form:
        return request.form.to_dict()
    return None


class RiderController:
    def __init__(self, rider_service: RiderService = None):
        self.rider_service = rider_service or RiderService()

    def get_riders(self):
        page = max(request.args.get("page", 1, type=int), 1)
        page_size = min(max(request.args.get("pageSize", 10, type=int), 1), 100)
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().lower()
        availability = request.args.get("availability", "").strip().lower()
        sort_by = request.args.get("sortBy", "id").strip()
        sort_order = request.args.get("sortOrder", "asc").strip().lower()

        success, message, data, status_code = self.rider_service.get_paginated_riders(
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            availability=availability,
            sort_by=sort_by,
            sort_order=sort_order
        )

        if not success:
            return error_response(message, status_code)

        return success_response(message, data, status_code)

    def get_available_riders(self):
        success, message, data, status_code = self.rider_service.get_available_riders()
        if not success:
            return error_response(message, status_code)
        return success_response(message, data, status_code)

    def get_rider(self, rider_id: int):
        success, message, data, status_code = self.rider_service.get_rider_by_id(rider_id)
        if not success:
            return error_response(message, status_code)
        return success_response(message, data, status_code)

    def create_rider(self):
        data = read_request_data()
        if not isinstance(data, dict):
            return error_response("A valid JSON or form body is required.", 400)

        errors, values = validate_rider_data(data)
        if errors:
            return jsonify({
                "success": False,
                "message": "Validation failed.",
                "errors": errors
            }), 400

        image_file = request.files.get("profile_image")
        success, message, result, status_code = self.rider_service.create_rider(
            values=values,
            image_file=image_file
        )

        if not success:
            return error_response(message, status_code)

        return success_response(message, result, status_code)

    def update_rider(self, rider_id: int):
        data = read_request_data()
        if not isinstance(data, dict):
            return error_response("A valid JSON or form body is required.", 400)

        errors, values = validate_rider_data(data)
        if errors:
            return jsonify({
                "success": False,
                "message": "Validation failed.",
                "errors": errors
            }), 400

        image_file = request.files.get("profile_image")
        success, message, result, status_code = self.rider_service.update_rider(
            rider_id=rider_id,
            values=values,
            image_file=image_file
        )

        if not success:
            return error_response(message, status_code)

        return success_response(message, result, status_code)

    def delete_rider(self, rider_id: int):
        success, message, result, status_code = self.rider_service.delete_rider(rider_id)
        if not success:
            return error_response(message, status_code)
        return success_response(message, result, status_code)

    def serve_upload(self, filename: str):
        return send_from_directory(
            Path(current_app.root_path) / "uploads",
            filename
        )
