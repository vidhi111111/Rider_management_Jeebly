from datetime import datetime, timezone
from .extensions import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Rider(db.Model):
    __tablename__ = "rider"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="available", index=True)
    mobile = db.Column(db.String(10), nullable=True, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    vehicle = db.Column(db.String(100), nullable=True)
    availability = db.Column(db.String(20), nullable=True, default="available", index=True)
    date = db.Column(db.Date, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        db.Index("ix_rider_status_availability", "status", "availability"),
    )


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(
        db.String(100),
        nullable=False
    )

    mobile = db.Column(db.String(20), nullable=True)
    pickup = db.Column(db.String(255), nullable=True)
    delivery = db.Column(db.String(255), nullable=True)

    amount = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    currency = db.Column(
        db.String(10),
        nullable=False,
        default="AED"
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending",
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    rider_id = db.Column(
        db.Integer,
        db.ForeignKey("rider.id"),
        nullable=True,
        index=True
    )

    rider = db.relationship(
        "Rider",
        backref="orders"
    )

    __table_args__ = (
        db.Index("ix_order_rider_id_status", "rider_id", "status"),
    )