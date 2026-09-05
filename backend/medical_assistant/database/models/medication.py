from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medical_assistant.database.base import Base


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    dosage: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    frequency: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    patient = relationship(
        "Patient",
        back_populates="medications",
    )