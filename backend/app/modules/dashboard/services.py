from typing import Tuple, Any
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ..riders.services import refresh_rider_availability
from ..riders.schemas import serialize_rider
from .repositories import DashboardRepository


class DashboardService:
    def __init__(self, dashboard_repo: DashboardRepository = None):
        self.dashboard_repo = dashboard_repo or DashboardRepository()

    def get_dashboard_data(self) -> Tuple[bool, str, Any, int]:
        try:
            total_orders, delivered, cancelled, in_progress = self.dashboard_repo.get_order_summary_counts()

            riders_list = self.dashboard_repo.get_all_riders()
            for rider in riders_list:
                refresh_rider_availability(rider)
            self.dashboard_repo.commit()

            available_riders = [
                r for r in riders_list if r.availability == "available"
            ]
            busy_riders = [r for r in riders_list if r.availability == "busy"]

            recent_orders = self.dashboard_repo.get_recent_orders(limit=5)

            data = {
                "summary": {
                    "total_orders": total_orders,
                    "delivered_orders": delivered,
                    "cancelled_orders": cancelled,
                    "in_progress_orders": in_progress
                },
                "rider_summary": {
                    "total": len(riders_list),
                    "active": sum(1 for r in riders_list if r.status not in {"inactive", "absent"}),
                    "available": len(available_riders),
                    "busy": len(busy_riders)
                },
                "recent_orders": [{
                    "id": o.id,
                    "status": o.status,
                    "customer": o.customer_name,
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                    "rider_id": o.rider_id
                } for o in recent_orders],
                "available_riders": [serialize_rider(r) for r in available_riders[:10]]
            }

            return True, "Dashboard data retrieved successfully.", data, 200

        except SQLAlchemyError:
            self.dashboard_repo.rollback()
            current_app.logger.exception("Unable to retrieve dashboard.")
            return False, "Unable to retrieve dashboard.", None, 500
