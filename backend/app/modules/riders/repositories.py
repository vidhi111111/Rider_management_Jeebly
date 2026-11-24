from typing import Optional, List, Tuple
from sqlalchemy import or_
from ...extensions import db
from ...models import Rider, Order


class RiderRepository:
    @staticmethod
    def get_by_id(rider_id: int) -> Optional[Rider]:
        return db.session.get(Rider, rider_id)

    @staticmethod
    def get_by_mobile(mobile: str) -> Optional[Rider]:
        return Rider.query.filter_by(mobile=mobile).first()

    @staticmethod
    def get_by_email(email: str) -> Optional[Rider]:
        return Rider.query.filter_by(email=email).first()

    @staticmethod
    def find_duplicate_mobile(mobile: str, exclude_id: int) -> Optional[Rider]:
        return Rider.query.filter(Rider.mobile == mobile, Rider.id != exclude_id).first()

    @staticmethod
    def find_duplicate_email(email: str, exclude_id: int) -> Optional[Rider]:
        return Rider.query.filter(Rider.email == email, Rider.id != exclude_id).first()

    @staticmethod
    def get_all(order_by_name: bool = False) -> List[Rider]:
        query = Rider.query
        if order_by_name:
            query = query.order_by(Rider.name.asc())
        return query.all()

    @staticmethod
    def count_active_orders_for_rider(rider_id: int, terminal_statuses: set) -> int:
        return Order.query.filter(
            Order.rider_id == rider_id,
            db.func.lower(Order.status).notin_(list(terminal_statuses))
        ).count()

    @staticmethod
    def count_total_orders_for_rider(rider_id: int) -> int:
        return Order.query.filter(Order.rider_id == rider_id).count()

    @staticmethod
    def count_delivered_orders_for_rider(rider_id: int) -> int:
        return Order.query.filter(
            Order.rider_id == rider_id,
            db.func.lower(Order.status) == "delivered"
        ).count()

    @staticmethod
    def _build_query(
        search: str = "",
        status: str = "",
        availability: str = "",
        date_from: Optional[str] = "",
        date_to: Optional[str] = "",
        sort_by: str = "id",
        sort_order: str = "asc"
    ):
        from datetime import datetime
        query = Rider.query

        if search:
            value = f"%{search}%"
            query = query.filter(or_(
                Rider.name.ilike(value),
                Rider.mobile.ilike(value),
                Rider.email.ilike(value)
            ))

        if status:
            query = query.filter(db.func.lower(Rider.status) == status)

        if availability in {"available", "busy", "unavailable"}:
            query = query.filter(Rider.availability == availability)

        def _parse(val):
            if not val:
                return None
            c = str(val).strip()
            if "T" in c:
                c = c.split("T")[0]
            for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%m/%d/%Y"]:
                try:
                    return datetime.strptime(c, fmt).date()
                except ValueError:
                    continue
            return None

        if date_from:
            d_from = _parse(date_from)
            if d_from:
                query = query.filter(Rider.date >= d_from)

        if date_to:
            d_to = _parse(date_to)
            if d_to:
                query = query.filter(Rider.date <= d_to)

        sort_columns = {
            "id": Rider.id,
            "name": Rider.name,
            "mobile": Rider.mobile,
            "email": Rider.email,
            "vehicle": Rider.vehicle,
            "status": Rider.status,
            "availability": Rider.availability,
            "date": Rider.date
        }
        column = sort_columns.get(sort_by, Rider.id)
        query = query.order_by(
            column.desc() if sort_order == "desc" else column.asc()
        )
        return query

    @staticmethod
    def filter_and_paginate(
        search: str = "",
        status: str = "",
        availability: str = "",
        date_from: Optional[str] = "",
        date_to: Optional[str] = "",
        sort_by: str = "id",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 10
    ):
        query = RiderRepository._build_query(
            search=search,
            status=status,
            availability=availability,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return query.paginate(
            page=page, per_page=page_size, error_out=False
        )

    @staticmethod
    def get_all_matching(
        search: str = "",
        status: str = "",
        availability: str = "",
        date_from: Optional[str] = "",
        date_to: Optional[str] = "",
        sort_by: str = "id",
        sort_order: str = "asc"
    ) -> List[Rider]:
        query = RiderRepository._build_query(
            search=search,
            status=status,
            availability=availability,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return query.all()

    @staticmethod
    def create(data: dict, profile_image: Optional[str] = None) -> Rider:
        rider = Rider(
            name=data["name"],
            mobile=data["mobile"],
            email=data["email"],
            vehicle=data["vehicle"],
            status=data["status"],
            availability=data["availability"],
            date=data["date"],
            profile_image=profile_image
        )
        db.session.add(rider)
        return rider

    @staticmethod
    def unlink_orders(rider_id: int):
        Order.query.filter_by(rider_id=rider_id).update(
            {"rider_id": None}, synchronize_session=False
        )

    @staticmethod
    def delete(rider: Rider):
        db.session.delete(rider)

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
