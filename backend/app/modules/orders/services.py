from typing import Optional, Dict, Any, Tuple
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ..riders.services import refresh_rider_availability
from ..riders.repositories import RiderRepository
from .repositories import OrderRepository
from .schemas import (
    serialize_order, validate_order_payload,
    ORDER_STATUSES, TERMINAL_STATUSES, ALLOWED_STATUS_TRANSITIONS
)


class OrderService:
    def __init__(self, order_repo: OrderRepository = None, rider_repo: RiderRepository = None):
        self.order_repo = order_repo or OrderRepository()
        self.rider_repo = rider_repo or RiderRepository()

    def get_paginated_orders(
        self,
        page: int,
        page_size: int,
        search: str,
        status: str,
        rider_id: Optional[int],
        order_date: str,
        sort_by: str
    ) -> Tuple[bool, str, Any, int]:
        try:
            pagination = self.order_repo.filter_and_paginate(
                search=search,
                status=status,
                rider_id=rider_id,
                order_date=order_date,
                sort_by=sort_by,
                page=page,
                page_size=page_size
            )

            data = {
                "orders": [serialize_order(o) for o in pagination.items],
                "page": pagination.page,
                "pageSize": pagination.per_page,
                "totalRecords": pagination.total,
                "totalPages": pagination.pages
            }
            return True, "Orders retrieved successfully.", data, 200

        except ValueError:
            return False, "Invalid order_date. Use YYYY-MM-DD.", None, 400
        except SQLAlchemyError:
            self.order_repo.rollback()
            current_app.logger.exception("Unable to retrieve orders.")
            return False, "Unable to retrieve orders.", None, 500

    def get_order_by_id(self, order_id: int) -> Tuple[bool, str, Any, int]:
        order = self.order_repo.get_by_id(order_id)
        if order is None:
            return False, "Order not found.", None, 404
        return True, "Order details retrieved successfully.", serialize_order(order), 200

    def create_order(self, data: Dict[str, Any]) -> Tuple[bool, str, Any, int]:
        valid, err_msg, values = validate_order_payload(data)
        if not valid:
            return False, err_msg, None, 400

        order = self.order_repo.create(values)
        try:
            self.order_repo.commit()
            return True, "Order created successfully.", serialize_order(order), 201
        except SQLAlchemyError:
            self.order_repo.rollback()
            current_app.logger.exception("Unable to create order.")
            return False, "Unable to create order.", None, 500

    def update_order(self, order_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Any, int]:
        try:
            order = self.order_repo.get_by_id(order_id)
            if order is None:
                return False, "Order not found.", None, 404

            if str(order.status or "").strip().lower() in TERMINAL_STATUSES:
                return False, "Delivered or cancelled orders cannot be edited.", None, 409

            valid, err_msg, values = validate_order_payload(data, is_update=True, existing_order=order)
            if not valid:
                return False, err_msg, None, 400

            order.customer_name = values["customer_name"]
            order.mobile = values["mobile"]
            order.pickup = values["pickup"]
            order.delivery = values["delivery"]
            order.amount = values["amount"]
            order.currency = values["currency"]

            self.order_repo.commit()
            return True, "Order updated successfully.", serialize_order(order), 200

        except SQLAlchemyError:
            self.order_repo.rollback()
            current_app.logger.exception("Unable to update order.")
            return False, "Unable to update order.", None, 500

    def update_order_status(self, order_id: int, new_status: str) -> Tuple[bool, str, Any, int]:
        try:
            order = self.order_repo.get_by_id(order_id)
            if order is None:
                return False, "Order not found.", None, 404

            clean_status = str(new_status or "").strip().lower()
            if clean_status not in ORDER_STATUSES:
                return False, "Invalid order status.", None, 400

            current_status = str(order.status or "").strip().lower()
            if current_status in TERMINAL_STATUSES:
                return False, "Delivered or cancelled orders cannot be changed.", None, 409

            allowed = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())
            if clean_status not in allowed:
                return False, f"Cannot change status from {current_status} to {clean_status}.", None, 409

            order.status = clean_status
            self.order_repo.flush()

            if order.rider:
                refresh_rider_availability(order.rider)

            self.order_repo.commit()
            return True, "Order status updated successfully.", serialize_order(order), 200

        except SQLAlchemyError:
            self.order_repo.rollback()
            current_app.logger.exception("Unable to update order status.")
            return False, "Unable to update order status.", None, 500

    def assign_rider(self, order_id: int, requested_rider_id: Any) -> Tuple[bool, str, Any, int]:
        try:
            order = self.order_repo.get_by_id(order_id)
            if order is None:
                return False, "Order not found.", None, 404

            order_status = str(order.status or "").strip().lower()
            if order_status in TERMINAL_STATUSES:
                return False, "Cannot assign a rider to a completed or cancelled order.", None, 409

            previous_rider = order.rider

            if requested_rider_id is None:
                order.rider_id = None
                order.rider = None
                current_rider = None
            else:
                try:
                    rider_id = int(requested_rider_id)
                    if rider_id <= 0:
                        raise ValueError
                except (TypeError, ValueError):
                    return False, "Invalid rider ID.", None, 400

                rider = self.rider_repo.get_by_id(rider_id)
                if rider is None:
                    return False, "Rider not found.", None, 404

                if order.rider_id != rider.id:
                    rider_status = str(rider.status or "").strip().lower()
                    if rider_status in {"inactive", "absent", "scheduled_break", "on_order"}:
                        return False, "This rider is not eligible for assignment.", None, 409

                    existing_order = self.order_repo.find_active_order_for_rider(rider.id, order.id)
                    if existing_order:
                        return False, "This rider already has an active order.", None, 409

                    availability = str(rider.availability or "").strip().lower()
                    if availability != "available":
                        return False, "This rider is currently unavailable. Please select an available rider.", None, 409

                order.rider_id = rider.id
                order.rider = rider
                current_rider = rider

            self.order_repo.flush()

            if previous_rider:
                refresh_rider_availability(previous_rider)

            if current_rider:
                refresh_rider_availability(current_rider)

            self.order_repo.commit()
            return True, "Order assignment updated successfully.", serialize_order(order), 200

        except SQLAlchemyError:
            self.order_repo.rollback()
            current_app.logger.exception("Unable to assign rider to order %s.", order_id)
            return False, "Unable to assign rider.", None, 500

    def delete_order(self, order_id: int) -> Tuple[bool, str, Any, int]:
        try:
            order = self.order_repo.get_by_id(order_id)
            if order is None:
                return False, "Order not found.", None, 404

            assigned_rider = order.rider
            self.order_repo.delete(order)
            self.order_repo.flush()

            if assigned_rider:
                refresh_rider_availability(assigned_rider)

            self.order_repo.commit()
            return True, "Order deleted successfully.", {"id": order_id}, 200

        except SQLAlchemyError:
            self.order_repo.rollback()
            current_app.logger.exception("Unable to delete order.")
            return False, "Unable to delete order. Check database constraints.", None, 500
