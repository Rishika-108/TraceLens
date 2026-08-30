from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.case import Case
    from app.models.entity import Entity


class Relationship(Base):
    __tablename__ = "relationships"

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

    source_entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_entity_id: Mapped[str] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    confidence: Mapped[str] = mapped_column(
        String(10),
        default="1.0",
    )

    supporting_artifact_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
    )

    evidence_snippet: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    case: Mapped["Case"] = relationship(
        "Case",
        back_populates="relationships",
    )

    source_entity: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[source_entity_id],
    )

    target_entity: Mapped["Entity"] = relationship(
        "Entity",
        foreign_keys=[target_entity_id],
    )

    @property
    def source_entity_value(self) -> str | None:
        return self.source_entity.value if self.source_entity else None

    @property
    def source_entity_type(self) -> str | None:
        return self.source_entity.entity_type if self.source_entity else None

    @property
    def target_entity_value(self) -> str | None:
        return self.target_entity.value if self.target_entity else None

    @property
    def target_entity_type(self) -> str | None:
        return self.target_entity.entity_type if self.target_entity else None