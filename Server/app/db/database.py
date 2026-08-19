# pyrefly: ignore [missing-import]
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine

from app.core.config import settings


class Base(DeclarativeBase):
    """
    Base class for all database models.
    """

    metadata = MetaData()


engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)


metadata = Base.metadata