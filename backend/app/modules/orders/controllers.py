from flask import request
from ...common.responses import error_response, success_response
from .services import OrderService


class OrderController:
    def __init__(self, order_service: OrderService = None):
        self.order_service = order_service or OrderService()

    def get_orders(self):
        page = max(request.args.get("page", 1, type=int), 1)
        page_size = min(max(request.args.get("pageSize", 10, type=int), 1), 100)
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().lower()
        rider_id = request.args.get("rider_id", type=int)
        order_date = request.args.get("order_date", "").strip()
        sort_by = request.args.get("sortBy", "newest").strip().lower()

        success, message, data, status_code = self.order_service.get_paginated_orders(
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            rider_id=rider_id,
            order_date=order_date,
            sort_by=sort_by
        )

        if not success:
            return error_response(message, status_code)

        return success_response(message, data, status_code)

    def get_order(self, order_id: int):
        success, message, data, status_code = self.order_service.get_order_by_id(order_id)
        if not success:
            return error_response(message, status_code)
        return success_response(message, data, status_code)

    def create_order(self):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error_response("A valid JSON object is required.", 400)

        success, message, result, status_code = self.order_service.create_order(data)
        if not success:
            return error_response(message, status_code)

        return success_response(message, result, status_code)

    def update_order(self, order_id: int):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error_response("A valid JSON object is required.", 400)

        success, message, result, status_code = self.order_service.update_order(order_id, data)
        if not success:
            return error_response(message, status_code)

        return success_response(message, result, status_code)

    def update_order_status(self, order_id: int):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error_response("A valid JSON body is required.", 400)

        new_status = str(data.get("status", "")).strip().lower()
        success, message, result, status_code = self.order_service.update_order_status(order_id, new_status)
        if not success:
            return error_response(message, status_code)

        return success_response(message, result, status_code)

    def assign_rider(self, order_id: int):
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or "rider_id" not in data:
            return error_response("A JSON object containing rider_id is required.", 400)

        requested_id = data.get("rider_id")
        success, message, result, status_code = self.order_service.assign_rider(order_id, requested_id)
        if not success:
            return error_response(message, status_code)

        return success_response(message, result, status_code)

    def delete_order(self, order_id: int):
        success, message, result, status_code = self.order_service.delete_order(order_id)
        if not success:
            return error_response(message, status_code)

        return success_response(message, result, status_code)
