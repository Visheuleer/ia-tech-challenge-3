from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medical_assistant.database.base import Base


class BloodPressureMeasurement(Base):
    __tablename__ = "blood_pressure_measurements"

    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
    )

    systolic: Mapped[int] = mapped_column(nullable=False)
    diastolic: Mapped[int] = mapped_column(nullable=False)

    measured_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    patient = relationship(
        "Patient",
        back_populates="blood_pressure_measurements",
    )