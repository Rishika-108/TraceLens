from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:

    @staticmethod
    def create(db: Session, user_data: UserCreate) -> User:
        hashed_pwd = hash_password(user_data.password)
        user = User(
            username=user_data.username.strip(),
            email=user_data.email.strip().lower(),
            hashed_password=hashed_pwd,
            role=user_data.role or "INVESTIGATOR",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: str) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        clean_name = username.strip()
        return (
            db.query(User)
            .filter(func.lower(User.username) == clean_name.lower())
            .first()
        )

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        clean_email = email.strip()
        return (
            db.query(User)
            .filter(func.lower(User.email) == clean_email.lower())
            .first()
        )

    @staticmethod
    def get_by_username_or_email(db: Session, identifier: str) -> User | None:
        clean_id = identifier.strip().lower()
        return (
            db.query(User)
            .filter(
                (func.lower(User.username) == clean_id) |
                (func.lower(User.email) == clean_id)
            )
            .first()
        )

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> User | None:
        # Accepts either username or email address, case-insensitively
        user = UserRepository.get_by_username_or_email(db, username)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
