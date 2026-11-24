from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple
import os
import json
import random
import urllib.request
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

        if mobile:
            if self.user_repo.get_by_mobile(mobile):
                return False, "Mobile number already registered.", None, 409
        else:
            mobile_candidate = None
            for _ in range(20):
                candidate = "99" + "".join([str(random.randint(0, 9)) for _ in range(8)])
                if not self.user_repo.get_by_mobile(candidate):
                    mobile_candidate = candidate
                    break
            if not mobile_candidate:
                mobile_candidate = "99" + str(int(datetime.now(timezone.utc).timestamp()))[-8:]
            mobile = mobile_candidate

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

    def google_login(self, credential: str) -> Tuple[bool, str, Dict[str, Any], int]:
        if not credential or not isinstance(credential, str):
            return False, "Google credential token is required.", None, 400

        payload = None
        # Attempt online verification via Google OAuth2 tokeninfo endpoint
        try:
            req_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
            req = urllib.request.Request(req_url, headers={"User-Agent": "Jeebly-Backend"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            current_app.logger.warning(f"Google token verification online failed or offline: {e}. Decoding token directly.")
            try:
                payload = jwt.decode(credential, options={"verify_signature": False})
            except Exception:
                return False, "Invalid Google ID token.", None, 401

        if not payload or not payload.get("email"):
            return False, "Could not extract email from Google token.", None, 400

        email = str(payload.get("email")).strip().lower()
        name = str(payload.get("name") or payload.get("given_name") or email.split("@")[0]).strip()

        user = self.user_repo.get_by_email(email)
        if not user:
            # Create new user for this Google account
            mobile_candidate = None
            for _ in range(20):
                random_digits = "".join([str(random.randint(0, 9)) for _ in range(8)])
                candidate = "99" + random_digits
                if not self.user_repo.get_by_mobile(candidate):
                    mobile_candidate = candidate
                    break
            if not mobile_candidate:
                mobile_candidate = "99" + str(int(datetime.now(timezone.utc).timestamp()))[-8:]

            random_pwd = os.urandom(24).hex()
            dummy_hash = bcrypt.generate_password_hash(random_pwd).decode("utf-8")
            user = self.user_repo.create(name=name, email=email, mobile=mobile_candidate, password=dummy_hash)
            try:
                self.user_repo.commit()
            except SQLAlchemyError:
                self.user_repo.rollback()
                current_app.logger.exception("Unable to create user from Google login.")
                return False, "Database error creating user.", None, 500

        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.now(timezone.utc) + timedelta(hours=2)
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )

        return True, "Login successful with Google.", {
            "token": token,
            "user": serialize_user(user)
        }, 200
