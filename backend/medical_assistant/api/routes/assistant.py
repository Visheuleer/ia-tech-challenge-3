from fastapi import APIRouter, HTTPException

from medical_assistant.schemas.assistant import (
    AssistantRequest,
    AssistantResponse,
)
from medical_assistant.services.assistant_service import (
    AssistantService,
)
from medical_assistant.services.patient_service import (
    PatientNotFoundError,
)


router = APIRouter(
    prefix="/assistant",
    tags=["assistant"],
)

service = AssistantService()


@router.post(
    "/chat",
    response_model=AssistantResponse,
)
def chat(
    request: AssistantRequest,
) -> AssistantResponse:
    try:
        result = service.ask(
            patient_id=request.patient_id,
            question=request.question,
        )

        return AssistantResponse(
            patient_id=request.patient_id,
            response=result[
                "final_response"
            ],
            safety_status=result[
                "safety_status"
            ],
            safety_violations=result.get(
                "safety_violations",
                []
            ),
            sources=result.get(
                "sources",
                []
            ),
            audit_log_id=result[
                "audit_log_id"
            ],
        )

    except PatientNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc