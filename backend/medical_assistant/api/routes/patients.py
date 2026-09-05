from fastapi import APIRouter, HTTPException, status

from medical_assistant.api.dependencies import DatabaseSession
from medical_assistant.schemas.patient import (
    PatientDetailResponse,
    PatientListResponse,
)
from medical_assistant.services.patient_service import (
    PatientNotFoundError,
    PatientService,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.get(
    "",
    response_model=list[PatientListResponse],
)
def list_patients(
    db: DatabaseSession,
) -> list[PatientListResponse]:
    service = PatientService(db)

    return service.list_patients()


@router.get(
    "/{patient_id}",
    response_model=PatientDetailResponse,
)
def get_patient(
    patient_id: int,
    db: DatabaseSession,
) -> PatientDetailResponse:
    service = PatientService(db)

    try:
        return service.get_patient(patient_id)

    except PatientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc