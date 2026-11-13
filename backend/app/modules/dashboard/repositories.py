from typing import List, Tuple, Dict
from sqlalchemy import func, case
from ...extensions import db
from ...models import Order, Rider
from ..orders.schemas import TERMINAL_STATUSES


class DashboardRepository:
    @staticmethod
    def get_order_summary_counts() -> Tuple[int, int, int, int]:
        """
        Aggregate total, delivered, cancelled, and in-progress order counts
        in a single optimized SQL aggregation query instead of 4 round trips.
        """
        row = db.session.query(
            func.count(Order.id).label("total"),
            func.count(
                case((func.lower(Order.status).in_(["delivered", "completed"]), 1))
            ).label("delivered"),
            func.count(
                case((func.lower(Order.status) == "cancelled", 1))
            ).label("cancelled"),
            func.count(
                case((func.lower(Order.status).notin_(list(TERMINAL_STATUSES)), 1))
            ).label("in_progress")
        ).one()

        return row.total, row.delivered, row.cancelled, row.in_progress

    @staticmethod
    def get_active_order_counts_by_rider() -> Dict[int, int]:
        """
        Batch query all active order counts grouped by rider_id in 1 query.
        Eliminates the N+1 query problem during rider availability recalculation.
        """
        results = db.session.query(
            Order.rider_id,
            func.count(Order.id)
        ).filter(
            Order.rider_id.isnot(None),
            func.lower(Order.status).notin_(list(TERMINAL_STATUSES))
        ).group_by(Order.rider_id).all()

        return {r_id: count for r_id, count in results}

    @staticmethod
    def get_all_riders() -> List[Rider]:
        return Rider.query.all()

    @staticmethod
    def get_recent_orders(limit: int = 5) -> List[Order]:
        """Selectively fetch only the columns required by the dashboard recent orders card."""
        return Order.query.options(
            db.load_only(
                Order.id,
                Order.status,
                Order.customer_name,
                Order.created_at,
                Order.rider_id
            )
        ).order_by(
            Order.created_at.desc(),
            Order.id.desc()
        ).limit(limit).all()

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
