from typing import Any, TypedDict


class ClinicalAssistantState(TypedDict, total=False):
    patient_id: int
    question: str

    patient: dict[str, Any]

    blood_pressure_status: str
    blood_pressure_summary: dict[str, Any]

    pending_exams: list[dict[str, Any]]

    protocol_results: list[dict[str, str]]

    clinical_context: str

    generated_response: str

    safety_status: str
    safety_violations: list[str]

    final_response: str

    sources: list[str]