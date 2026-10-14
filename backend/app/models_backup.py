
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
    __tablename__ = "riders"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    vehicle = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")
    availability = db.Column(db.String(20), nullable=False, default="available")
    date = db.Column(db.Date, nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)

    orders = db.relationship("Order", back_populates="rider")


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(10), nullable=False)
    pickup = db.Column(db.String(255), nullable=False)
    delivery = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="AED")
    status = db.Column(db.String(30), nullable=False, default="pending")
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    rider_id = db.Column(
        db.Integer,
        db.ForeignKey("riders.id"),
        nullable=True
    )

    rider = db.relationship("Rider", back_populates="orders")
