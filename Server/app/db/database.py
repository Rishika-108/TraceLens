import os
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.core.logging import logger


class Base(DeclarativeBase):
    """
    Base class for all database models.
    """
    metadata = MetaData()


def get_postgres_engine():
    """
    Creates and configures the PostgreSQL database engine with connection pooling.
    Standardized exclusively on PostgreSQL for data consistency and pgvector support.
    """
    url = settings.DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    logger.info(f"Connecting to PostgreSQL database...")

    engine = create_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
        connect_args={"connect_timeout": 15},
    )

    return engine


engine = get_postgres_engine()
metadata = Base.metadata