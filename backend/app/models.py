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
    status = db.Column(db.String(30), nullable=False, default="available")
    mobile = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    vehicle = db.Column(db.String(100), nullable=True)
    availability = db.Column(db.String(20), nullable=True, default="available")
    date = db.Column(db.Date, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="pending")
    created_at = db.Column(
        db.DateTime,
        nullable=True,
        default=lambda: datetime.now(timezone.utc)
    )
    rider_id = db.Column(db.Integer, db.ForeignKey("rider.id"), nullable=True)
    rider = db.relationship("Rider", backref="orders")

