from datetime import datetime
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.core.config import settings
from app.db.database import Base


# Register SQLite compilation for Vector type to allow local SQLite fallback without pgvector binary
@compiles(Vector, "sqlite")
def compile_vector_sqlite(type_, compiler, **kw):
    return "BLOB"


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("evidence.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    artifact_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    content: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    raw_data: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    parser_stage: Mapped[str] = mapped_column(
        String(50),
        default="PARSED",
        nullable=False,
    )

    timestamp: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.VECTOR_DIMENSION),
        nullable=True,
    )

    evidence = relationship(
        "Evidence",
        back_populates="artifacts",
    )