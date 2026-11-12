from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple
import jwt
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from ...extensions import bcrypt
from .repositories import UserRepository
from .schemas import serialize_user


class AuthService:
    def __init__(self, user_repo: UserRepository = None):
        self.user_repo = user_repo or UserRepository()

    def register(self, name: str, email: str, mobile: str, password: str) -> Tuple[bool, str, Any, int]:
        if self.user_repo.get_by_email(email):
            return False, "Email already registered.", None, 409

        if self.user_repo.get_by_mobile(mobile):
            return False, "Mobile number already registered.", None, 409

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = self.user_repo.create(name, email, mobile, password_hash)

        try:
            self.user_repo.commit()
        except SQLAlchemyError:
            self.user_repo.rollback()
            current_app.logger.exception("Unable to register user.")
            return False, "Database error occurred.", None, 500

        return True, "Registration successful.", serialize_user(user), 201

    def login(self, email: str, password: str) -> Tuple[bool, str, Dict[str, Any], int]:
        user = self.user_repo.get_by_email(email)
        if not user or not bcrypt.check_password_hash(user.password, password):
            return False, "Invalid email or password.", None, 401

        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.now(timezone.utc) + timedelta(hours=2)
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        return True, "Login successful.", {
            "token": token,
            "user": serialize_user(user)
        }, 200
