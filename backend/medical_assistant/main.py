from fastapi import FastAPI

from medical_assistant.api.routes.health import router as health_router
from medical_assistant.api.routes.patients import router as patients_router
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