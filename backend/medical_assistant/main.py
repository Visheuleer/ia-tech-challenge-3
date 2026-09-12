from fastapi import FastAPI

from medical_assistant.api.routes import (
    health_router,
    patients_router,
    assistant_router,
    audit_router,
)
from medical_assistant.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Assistente clínico para apoio ao acompanhamento "
        "de pacientes com hipertensão."
    ),
)

app.include_router(health_router)
app.include_router(patients_router)
app.include_router(assistant_router)
app.include_router(audit_router)