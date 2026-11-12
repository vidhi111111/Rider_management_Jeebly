from typing import Optional
from ...extensions import db
from ...models import User


class UserRepository:
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_mobile(mobile: str) -> Optional[User]:
        return User.query.filter_by(mobile=mobile).first()

    @staticmethod
    def find_duplicate_mobile(mobile: str, exclude_user_id: int) -> Optional[User]:
        return User.query.filter(User.mobile == mobile, User.id != exclude_user_id).first()

    @staticmethod
    def create(name: str, email: str, mobile: str, password_hash: str) -> User:
        user = User(
            name=name,
            email=email,
            mobile=mobile,
            password=password_hash
        )
        db.session.add(user)
        return user

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
