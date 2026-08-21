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
        return db.query(User).filter(User.username == username.strip()).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email.strip().lower()).first()

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> User | None:
        user = UserRepository.get_by_username(db, username)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
