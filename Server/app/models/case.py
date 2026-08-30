from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.evidence import Evidence
    from app.models.entity import Entity
    from app.models.relationship import Relationship
    from app.models.timeline import Timeline
    from app.models.report import Report


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    evidences: Mapped[list["Evidence"]] = relationship(
        "Evidence",
        back_populates="case",
        cascade="all, delete-orphan",
    )

    entities: Mapped[list["Entity"]] = relationship(
        "Entity",
        back_populates="case",
        cascade="all, delete-orphan",
    )

    relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        back_populates="case",
        cascade="all, delete-orphan",
    )

    timeline_events: Mapped[list["Timeline"]] = relationship(
        "Timeline",
        back_populates="case",
        cascade="all, delete-orphan",
    )

    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="case",
        cascade="all, delete-orphan",
    )