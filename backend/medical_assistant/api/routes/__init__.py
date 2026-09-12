from medical_assistant.api.routes.health import router as health_router
from medical_assistant.api.routes.patients import router as patients_router
from medical_assistant.api.routes.assistant import router as assistant_router
from medical_assistant.api.routes.audit import router as audit_router

__all__ = [
    "health_router",
    "patients_router",
    "assistant_router",
    "audit_router",
]