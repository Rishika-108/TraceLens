import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any
from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "TraceLens"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Storage & Uploads
    STORAGE_PATH: str = str(Path(__file__).resolve().parent.parent.parent / "storage" / "evidence")

    # PostgreSQL
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "tracelens"
    DATABASE_URL_ENV: str | None = Field(default=None, validation_alias="DATABASE_URL")
    DATABASE_URL_OVERRIDE: str | None = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL_ENV: str | None = Field(default=None, validation_alias="REDIS_URL")

    # Security
    SECRET_KEY: str = "change_this_in_production_tracelens_forensics_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_DIMENSION: int = 384

    # CORS
    ALLOWED_ORIGINS: str | list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        defaults = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
        if isinstance(v, str):
            if not v.strip():
                return defaults
            if v.strip() == "*":
                return ["*"]
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = json.loads(v)
                    return list(dict.fromkeys(parsed + defaults))
                except Exception:
                    pass
            origins = [i.strip() for i in v.split(",") if i.strip()]
            return list(dict.fromkeys(origins + defaults))
        elif isinstance(v, (list, tuple, set)):
            return list(dict.fromkeys([str(i) for i in v] + defaults))
        return defaults

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        raw = self.DATABASE_URL_OVERRIDE or self.DATABASE_URL_ENV
        if raw:
            url = raw.strip()
            # Render and Heroku provide postgres:// which is deprecated in SQLAlchemy 2.0+
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+psycopg2://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url
        return (
            f"postgresql+psycopg2://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_URL_ENV:
            return self.REDIS_URL_ENV
        return (
            f"redis://"
            f"{self.REDIS_HOST}:"
            f"{self.REDIS_PORT}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()