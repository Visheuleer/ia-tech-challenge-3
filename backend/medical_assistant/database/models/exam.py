from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medical_assistant.database.base import Base


class LabExam(Base):
    __tablename__ = "lab_exams"

    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
    )

    exam_type: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reference_range: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    performed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    patient = relationship(
        "Patient",
        back_populates="lab_exams",
    )