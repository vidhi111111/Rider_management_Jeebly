from datetime import datetime
from typing import Optional, List
from sqlalchemy import or_
from ...extensions import db
from ...models import Order, Rider
from .schemas import TERMINAL_STATUSES


class OrderRepository:
    @staticmethod
    def get_by_id(order_id: int) -> Optional[Order]:
        return db.session.get(Order, order_id)

    @staticmethod
    def filter_and_paginate(
        search: str = "",
        status: str = "",
        rider_id: Optional[int] = None,
        order_date: Optional[str] = "",
        sort_by: str = "newest",
        page: int = 1,
        page_size: int = 10
    ):
        # Eager load rider relationship to eliminate N+1 queries during serialization
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

        if order_date:
            try:
                parsed_date = datetime.strptime(order_date, "%Y-%m-%d").date()
                start_dt = datetime.combine(parsed_date, datetime.min.time())
                end_dt = datetime.combine(parsed_date, datetime.max.time())
                # Range filter utilizes index on created_at efficiently
                query = query.filter(Order.created_at >= start_dt, Order.created_at <= end_dt)
            except (ValueError, TypeError):
                pass

        if sort_by == "oldest":
            query = query.order_by(Order.created_at.asc(), Order.id.asc())
        else:
            query = query.order_by(Order.created_at.desc(), Order.id.desc())

        return query.paginate(
            page=page, per_page=page_size, error_out=False
        )

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
