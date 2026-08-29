import os
from pathlib import Path
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """
    Base class for all database models.
    """
    metadata = MetaData()


def create_resilient_engine():
    """
    Creates a SQLAlchemy database engine.
    Tries PostgreSQL first; if offline or misconfigured, gracefully falls back to local SQLite.
    """
    url = settings.DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

    # 1. Try configured PostgreSQL URL
    if url.startswith("postgresql"):
        try:
            pg_engine = create_engine(
                url,
                echo=False,
                pool_pre_ping=True,
                connect_args={"connect_timeout": 5},
            )
            with pg_engine.connect() as conn:
                pass
            return pg_engine
        except Exception:
            pass

    # 2. Local SQLite database fallback
    server_dir = Path(__file__).resolve().parent.parent.parent
    db_path = server_dir / "tracelens.db"
    sqlite_url = f"sqlite:///{db_path}"
    return create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )


engine = create_resilient_engine()
metadata = Base.metadata