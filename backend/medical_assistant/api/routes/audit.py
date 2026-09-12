from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from medical_assistant.database.session import (
    get_db,
)
from medical_assistant.repositories.audit_repository import (
    AuditRepository,
)
from medical_assistant.schemas.audit import (
    AuditLogResponse,
)


router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=list[
        AuditLogResponse
    ],
)
def list_audit_logs(
    db: DatabaseSession,
) -> list[AuditLogResponse]:
    repository = AuditRepository(db)

    return repository.list_all()


@router.get(
    "/{audit_id}",
    response_model=AuditLogResponse,
)
def get_audit_log(
    audit_id: int,
    db: DatabaseSession,
) -> AuditLogResponse:
    repository = AuditRepository(db)

    log = repository.get_by_id(
        audit_id
    )

    if log is None:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found.",
        )

    return log


@router.get(
    "/patient/{patient_id}",
    response_model=list[
        AuditLogResponse
    ],
)
def list_patient_audit_logs(
    patient_id: int,
    db: DatabaseSession,
) -> list[AuditLogResponse]:
    repository = AuditRepository(db)

    return repository.list_by_patient(
        patient_id
    )