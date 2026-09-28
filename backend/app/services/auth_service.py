from datetime import datetime, timedelta, timezone

import jwt

from flask import current_app

from ..extensions import bcrypt
from ..models import User


def authenticate_user(email, password):

    user = User.query.filter_by(email=email).first()

    if not user:
        return None

    if not bcrypt.check_password_hash(user.password, password):
        return None

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile
        }
    }