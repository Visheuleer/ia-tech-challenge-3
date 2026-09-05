from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from medical_assistant.database.models import Patient


class PatientRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Patient]:
        statement = select(Patient).order_by(Patient.id)

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_id(self, patient_id: int) -> Patient | None:
        statement = (
            select(Patient)
            .where(Patient.id == patient_id)
            .options(
                selectinload(Patient.medical_history),
                selectinload(Patient.blood_pressure_measurements),
                selectinload(Patient.medications),
                selectinload(Patient.lab_exams),
            )
        )

        return self.db.scalars(statement).first()