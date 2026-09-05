from sqlalchemy.orm import Session

from medical_assistant.database.models import Patient
from medical_assistant.repositories.patient_repository import PatientRepository


class PatientNotFoundError(Exception):
    pass


class PatientService:
    def __init__(self, db: Session) -> None:
        self.repository = PatientRepository(db)

    def list_patients(self) -> list[Patient]:
        return self.repository.list_all()

    def get_patient(self, patient_id: int) -> Patient:
        patient = self.repository.get_by_id(patient_id)

        if patient is None:
            raise PatientNotFoundError(
                f"Patient with id {patient_id} was not found."
            )

        return patient