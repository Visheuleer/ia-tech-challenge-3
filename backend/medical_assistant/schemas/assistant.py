from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    patient_id: int
    question: str = Field(
        min_length=3,
        max_length=2000,
    )


class AssistantResponse(BaseModel):
    patient_id: int
    response: str
    safety_status: str
    safety_violations: list[str]
    sources: list[str]
    audit_log_id: int