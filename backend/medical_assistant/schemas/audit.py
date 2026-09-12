from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    patient_id: int

    question: str
    model_response: str

    retrieved_context: dict[str, Any]
    validation_result: dict[str, Any]
    sources: list[str]

    created_at: datetime