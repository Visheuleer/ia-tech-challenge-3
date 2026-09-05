from __future__ import annotations

from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medical_assistant.database.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    sex: Mapped[str] = mapped_column(String(20), nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(nullable=True)
    height_cm: Mapped[float | None] = mapped_column(nullable=True)

    medical_history = relationship(
        "MedicalHistory",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    blood_pressure_measurements = relationship(
        "BloodPressureMeasurement",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    medications = relationship(
        "Medication",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    lab_exams = relationship(
        "LabExam",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="patient",
        cascade="all, delete-orphan",
    )