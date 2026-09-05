from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class MedicalHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    condition: str
    diagnosis_date: date | None
    notes: str | None


class BloodPressureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    systolic: int
    diastolic: int
    measured_at: datetime


class MedicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    dosage: str
    frequency: str
    start_date: date | None
    active: bool


class LabExamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exam_type: str
    result: str | None
    reference_range: str | None
    status: str
    performed_at: datetime | None


class PatientListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    birth_date: date
    sex: str


class PatientDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    birth_date: date
    sex: str
    weight_kg: float | None
    height_cm: float | None

    medical_history: list[MedicalHistoryResponse]
    blood_pressure_measurements: list[BloodPressureResponse]
    medications: list[MedicationResponse]
    lab_exams: list[LabExamResponse]