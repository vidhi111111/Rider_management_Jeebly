from typing import Optional
from ...extensions import db
from ...models import User


class ProfileRepository:
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        return db.session.get(User, user_id)

    @staticmethod
    def find_duplicate_mobile(mobile: str, exclude_user_id: int) -> Optional[User]:
        return User.query.filter(User.mobile == mobile, User.id != exclude_user_id).first()

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
