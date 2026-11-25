from typing import Tuple, Any
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ..riders.schemas import serialize_rider
from .repositories import DashboardRepository
from .schemas import dashboard_data_schema


class DashboardService:
    def __init__(self, dashboard_repo: DashboardRepository = None):
        self.dashboard_repo = dashboard_repo or DashboardRepository()

    def get_dashboard_data(self) -> Tuple[bool, str, Any, int]:
        try:
            total_orders, delivered, cancelled, in_progress = self.dashboard_repo.get_order_summary_counts()

            riders_list = self.dashboard_repo.get_all_riders()
            active_counts = self.dashboard_repo.get_active_order_counts_by_rider()

            # In-memory batch availability refresh (O(1) queries instead of O(N) database calls)
            for rider in riders_list:
                status_clean = str(rider.status or "").strip().lower()
                if status_clean in {"inactive", "absent", "scheduled_break"}:
                    rider.availability = "unavailable"
                else:
                    active_orders = active_counts.get(rider.id, 0)
                    if active_orders > 0:
                        rider.availability = "busy"
                    else:
                        rider.availability = "available"

            self.dashboard_repo.commit()

            available_riders = [
                r for r in riders_list
                if r.availability == "available"
                and str(r.status or "").strip().lower() not in {"inactive", "absent", "scheduled_break"}
            ]
            busy_riders = [r for r in riders_list if r.availability == "busy"]
            active_riders = [
                r for r in riders_list
                if str(r.status or "").strip().lower() not in {"inactive", "absent"}
            ]
            inactive_riders = [
                r for r in riders_list
                if str(r.status or "").strip().lower() in {"inactive", "absent"}
            ]

            recent_orders = self.dashboard_repo.get_recent_orders(limit=5)

            raw_data = {
                "summary": {
                    "total_orders": total_orders,
                    "delivered_orders": delivered,
                    "cancelled_orders": cancelled,
                    "in_progress_orders": in_progress
                },
                "rider_summary": {
                    "total": len(riders_list),
                    "active": len(active_riders),
                    "inactive": len(inactive_riders),
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

            # Serialize through Marshmallow
            serialized_data = dashboard_data_schema.dump(raw_data)

            return True, "Dashboard data retrieved successfully.", serialized_data, 200

        except SQLAlchemyError:
            self.dashboard_repo.rollback()
            current_app.logger.exception("Unable to retrieve dashboard.")
            return False, "Unable to retrieve dashboard.", None, 500
