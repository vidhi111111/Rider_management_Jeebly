from typing import List, Tuple
from ...extensions import db
from ...models import Order, Rider
from ..orders.schemas import TERMINAL_STATUSES


class DashboardRepository:
    @staticmethod
    def get_order_summary_counts() -> Tuple[int, int, int, int]:
        total_orders = Order.query.count()
        delivered = Order.query.filter(
            db.func.lower(Order.status).in_(["delivered", "completed"])
        ).count()
        cancelled = Order.query.filter(
            db.func.lower(Order.status) == "cancelled"
        ).count()
        in_progress = Order.query.filter(
            db.func.lower(Order.status).notin_(list(TERMINAL_STATUSES))
        ).count()
        return total_orders, delivered, cancelled, in_progress

    @staticmethod
    def get_all_riders() -> List[Rider]:
        return Rider.query.all()

    @staticmethod
    def get_recent_orders(limit: int = 5) -> List[Order]:
        return Order.query.order_by(
            Order.created_at.desc(), Order.id.desc()
        ).limit(limit).all()

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
