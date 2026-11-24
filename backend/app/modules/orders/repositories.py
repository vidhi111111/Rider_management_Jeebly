from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import or_
from ...extensions import db
from ...models import Order, Rider
from .schemas import TERMINAL_STATUSES


def parse_date_safely(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    cleaned = str(date_str).strip()
    if not cleaned:
        return None
    if "T" in cleaned:
        cleaned = cleaned.split("T")[0]
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%m-%d-%Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


class OrderRepository:
    @staticmethod
    def get_by_id(order_id: int) -> Optional[Order]:
        return db.session.get(Order, order_id)

    @staticmethod
    def _build_query(
        search: str = "",
        status: str = "",
        rider_id: Optional[int] = None,
        order_date: Optional[str] = "",
        created_from: Optional[str] = "",
        created_to: Optional[str] = "",
        sort_by: str = "newest"
    ):
        query = Order.query.options(db.joinedload(Order.rider))

        if search:
            value = f"%{search}%"
            conditions = [
                Order.customer_name.ilike(value),
                Order.mobile.ilike(value)
            ]

            order_prefix = "ORD-JB"
            search_id = search.strip().upper()

            if search_id.isdigit():
                conditions.append(Order.id == int(search_id))
            elif search_id.startswith(order_prefix):
                suffix = search_id[len(order_prefix):]
                if suffix.isdigit():
                    conditions.append(Order.id == int(suffix))

            query = query.filter(or_(*conditions))

        if status:
            query = query.filter(db.func.lower(Order.status) == status)

        if rider_id is not None:
            query = query.filter(Order.rider_id == rider_id)

        if created_from:
            dt_from = parse_date_safely(created_from)
            if dt_from:
                start_boundary = datetime.combine(dt_from.date(), datetime.min.time())
                query = query.filter(Order.created_at >= start_boundary)

        if created_to:
            dt_to = parse_date_safely(created_to)
            if dt_to:
                end_boundary = datetime.combine(dt_to.date(), datetime.max.time())
                query = query.filter(Order.created_at <= end_boundary)
        elif order_date and not created_from:
            dt_single = parse_date_safely(order_date)
            if dt_single:
                start_boundary = datetime.combine(dt_single.date(), datetime.min.time())
                end_boundary = datetime.combine(dt_single.date(), datetime.max.time())
                query = query.filter(Order.created_at >= start_boundary, Order.created_at <= end_boundary)

        if sort_by == "oldest":
            query = query.order_by(Order.created_at.asc(), Order.id.asc())
        else:
            query = query.order_by(Order.created_at.desc(), Order.id.desc())

        return query

    @staticmethod
    def filter_and_paginate(
        search: str = "",
        status: str = "",
        rider_id: Optional[int] = None,
        order_date: Optional[str] = "",
        created_from: Optional[str] = "",
        created_to: Optional[str] = "",
        sort_by: str = "newest",
        page: int = 1,
        page_size: int = 10
    ):
        query = OrderRepository._build_query(
            search=search,
            status=status,
            rider_id=rider_id,
            order_date=order_date,
            created_from=created_from,
            created_to=created_to,
            sort_by=sort_by
        )
        return query.paginate(
            page=page, per_page=page_size, error_out=False
        )

    @staticmethod
    def get_all_matching(
        search: str = "",
        status: str = "",
        rider_id: Optional[int] = None,
        order_date: Optional[str] = "",
        created_from: Optional[str] = "",
        created_to: Optional[str] = "",
        sort_by: str = "newest"
    ) -> List[Order]:
        query = OrderRepository._build_query(
            search=search,
            status=status,
            rider_id=rider_id,
            order_date=order_date,
            created_from=created_from,
            created_to=created_to,
            sort_by=sort_by
        )
        return query.all()

    @staticmethod
    def create(data: dict) -> Order:
        order = Order(
            customer_name=data["customer_name"],
            mobile=data.get("mobile"),
            pickup=data.get("pickup"),
            delivery=data.get("delivery"),
            amount=data.get("amount"),
            currency=data.get("currency", "AED"),
            status="pending",
            rider_id=None
        )
        db.session.add(order)
        return order

    @staticmethod
    def find_active_order_for_rider(rider_id: int, exclude_order_id: int) -> Optional[Order]:
        return Order.query.filter(
            Order.rider_id == rider_id,
            Order.id != exclude_order_id,
            db.func.lower(Order.status).notin_(list(TERMINAL_STATUSES))
        ).first()

    @staticmethod
    def delete(order: Order):
        db.session.delete(order)

    @staticmethod
    def flush():
        db.session.flush()

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
