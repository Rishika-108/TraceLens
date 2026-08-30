from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.artifact import Artifact


class Timeline(Base):
    __tablename__ = "timeline_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    case_id: Mapped[str] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    artifact_id: Mapped[str] = mapped_column(
        ForeignKey("artifacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    event_state: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    modality: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    actor: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    target: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    referenced_time: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    referenced_location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_synthetic_timestamp: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    artifact: Mapped["Artifact"] = relationship(
        "Artifact",
    )

    case: Mapped["Case"] = relationship(
        "Case",
        back_populates="timeline_events",
    )