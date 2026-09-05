from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medical_assistant.database.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    retrieved_context: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    model_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    validation_result: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    sources: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    patient = relationship(
        "Patient",
        back_populates="audit_logs",
    )