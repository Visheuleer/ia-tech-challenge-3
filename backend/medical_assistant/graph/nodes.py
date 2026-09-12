from statistics import mean
from typing import Any

from medical_assistant.database.session import SessionLocal
from medical_assistant.graph.state import ClinicalAssistantState
from medical_assistant.services.patient_service import (
    PatientNotFoundError,
    PatientService,
)
from medical_assistant.services.protocol_service import ProtocolService
from medical_assistant.llm.model import get_medical_llm
from medical_assistant.llm.prompt_loader import load_prompt
from medical_assistant.llm.guardrails import (
    validate_response,
)

def serialize_patient(patient: Any) -> dict[str, Any]:
    return {
        "id": patient.id,
        "name": patient.name,
        "birth_date": patient.birth_date.isoformat(),
        "sex": patient.sex,
        "weight_kg": patient.weight_kg,
        "height_cm": patient.height_cm,
        "medical_history": [
            {
                "condition": item.condition,
                "diagnosis_date": (
                    item.diagnosis_date.isoformat()
                    if item.diagnosis_date
                    else None
                ),
                "notes": item.notes,
            }
            for item in patient.medical_history
        ],
        "blood_pressure_measurements": [
            {
                "systolic": item.systolic,
                "diastolic": item.diastolic,
                "measured_at": item.measured_at.isoformat(),
            }
            for item in patient.blood_pressure_measurements
        ],
        "medications": [
            {
                "name": item.name,
                "dosage": item.dosage,
                "frequency": item.frequency,
                "active": item.active,
            }
            for item in patient.medications
        ],
        "lab_exams": [
            {
                "exam_type": item.exam_type,
                "result": item.result,
                "reference_range": item.reference_range,
                "status": item.status,
                "performed_at": (
                    item.performed_at.isoformat()
                    if item.performed_at
                    else None
                ),
            }
            for item in patient.lab_exams
        ],
    }


def load_patient(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    patient_id = state["patient_id"]

    with SessionLocal() as db:
        service = PatientService(db)

        try:
            patient = service.get_patient(patient_id)
        except PatientNotFoundError as exc:
            raise ValueError(str(exc)) from exc

        return {
            "patient": serialize_patient(patient),
        }


def check_blood_pressure(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    measurements = state["patient"]["blood_pressure_measurements"]

    if not measurements:
        return {
            "blood_pressure_status": "unknown",
            "blood_pressure_summary": {
                "count": 0,
                "average_systolic": None,
                "average_diastolic": None,
            },
        }

    systolic_values = [
        measurement["systolic"]
        for measurement in measurements
    ]

    diastolic_values = [
        measurement["diastolic"]
        for measurement in measurements
    ]

    avg_systolic = round(mean(systolic_values), 1)
    avg_diastolic = round(mean(diastolic_values), 1)

    if avg_systolic >= 180 or avg_diastolic >= 110:
        status = "critical_attention"

    elif avg_systolic >= 140 or avg_diastolic >= 90:
        status = "elevated"

    else:
        status = "stable"

    return {
        "blood_pressure_status": status,
        "blood_pressure_summary": {
            "count": len(measurements),
            "average_systolic": avg_systolic,
            "average_diastolic": avg_diastolic,
        },
    }


def check_pending_exams(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    exams = state["patient"]["lab_exams"]

    pending_exams = [
        exam
        for exam in exams
        if exam["status"] == "pending"
    ]

    return {
        "pending_exams": pending_exams,
    }


def retrieve_protocols(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    patient = state["patient"]
    question = state["question"]

    query_parts = [
        question,
        f"Blood pressure status: {state['blood_pressure_status']}",
    ]

    if state["pending_exams"]:
        pending_names = [
            exam["exam_type"]
            for exam in state["pending_exams"]
        ]

        query_parts.append(
            f"Pending exams: {', '.join(pending_names)}"
        )

    conditions = [
        item["condition"]
        for item in patient["medical_history"]
    ]

    if conditions:
        query_parts.append(
            f"Medical history: {', '.join(conditions)}"
        )

    query = "\n".join(query_parts)

    service = ProtocolService()
    results = service.search(query, k=3)

    return {
        "protocol_results": [
            {
                "content": result.content,
                "source": result.source,
            }
            for result in results
        ]
    }


def build_clinical_context(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    patient = state["patient"]

    history = patient.get(
        "medical_history",
        []
    )

    measurements = patient.get(
        "blood_pressure_measurements",
        []
    )

    medications = patient.get(
        "medications",
        []
    )

    pending_exams = state.get(
        "pending_exams",
        []
    )

    protocol_results = state.get(
        "protocol_results",
        []
    )

    lines = [
        "## PERGUNTA DO PROFISSIONAL",
        state["question"],
        "",
        "## DADOS DO PACIENTE",
        f"ID: {patient['id']}",
        f"Nome: {patient['name']}",
        "",
        "## HISTÓRICO CLÍNICO REGISTRADO",
    ]

    if history:
        for item in history:
            lines.append(
                f"- {item['condition']}"
                + (
                    f": {item['notes']}"
                    if item.get("notes")
                    else ""
                )
            )
    else:
        lines.append(
            "- Nenhuma condição registrada."
        )

    lines.extend([
        "",
        "## MEDIÇÕES DE PRESSÃO ARTERIAL",
    ])

    if measurements:
        for item in measurements:
            lines.append(
                f"- {item['measured_at']}: "
                f"{item['systolic']}/"
                f"{item['diastolic']} mmHg"
            )
    else:
        lines.append(
            "- Nenhuma medição disponível."
        )

    lines.extend([
        "",
        "## FATOS CALCULADOS PELO SISTEMA",
        (
            "- Status das medições de pressão: "
            f"{state['blood_pressure_status']}"
        ),
    ])

    summary = state.get(
        "blood_pressure_summary",
        {}
    )

    if summary:
        lines.append(
            "- Média sistólica calculada: "
            f"{summary.get('average_systolic')}"
        )

        lines.append(
            "- Média diastólica calculada: "
            f"{summary.get('average_diastolic')}"
        )

    lines.extend([
        "",
        "## MEDICAMENTOS ATIVOS REGISTRADOS",
    ])

    active_medications = [
        medication
        for medication in medications
        if medication.get("active")
    ]

    if active_medications:
        for medication in active_medications:
            lines.append(
                f"- {medication['name']} "
                f"{medication['dosage']} "
                f"({medication['frequency']})"
            )
    else:
        lines.append(
            "- Nenhum medicamento ativo "
            "registrado."
        )

    lines.extend([
        "",
        "## EXAMES PENDENTES",
    ])

    if pending_exams:
        for exam in pending_exams:
            lines.append(
                f"- {exam['exam_type']}"
            )
    else:
        lines.append(
            "- Nenhum exame pendente."
        )

    lines.extend([
        "",
        "## PROTOCOLOS RECUPERADOS",
    ])

    for result in protocol_results:
        lines.append(
            f"\nFonte: {result['source']}\n"
            f"{result['content']}"
        )

    return {
        "clinical_context": "\n".join(
            lines
        )
    }


def build_attention_points(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    patient = state["patient"]

    points: list[str] = []

    bp_status = state.get(
        "blood_pressure_status"
    )

    measurements = patient.get(
        "blood_pressure_measurements",
        []
    )

    if bp_status == "elevated":
        points.append(
            "As medições recentes de pressão arterial "
            "apresentam valores elevados segundo a regra "
            "de classificação utilizada pelo sistema."
        )

    elif bp_status == "critical_attention":
        points.append(
            "As medições recentes de pressão arterial "
            "atingiram o nível de atenção crítica definido "
            "pelas regras internas do sistema."
        )

    history = patient.get(
        "medical_history",
        []
    )

    for item in history:
        condition = item.get("condition")

        if condition:
            points.append(
                f"Condição registrada no histórico: "
                f"{condition}."
            )

    medications = patient.get(
        "medications",
        []
    )

    for medication in medications:
        if medication.get("active"):
            points.append(
                "Medicação registrada como ativa: "
                f"{medication['name']} "
                f"{medication['dosage']} "
                f"({medication['frequency']})."
            )

    return {
        "attention_points": points,
    }


def generate_summary(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    llm = get_medical_llm()

    system_prompt = load_prompt(
        "system/medical_assistant.md"
    )

    generation_prompt = load_prompt(
        "generation/clinical_summary.md"
    )

    user_prompt = (
        f"{generation_prompt}\n\n"
        "## FATOS DISPONÍVEIS\n\n"
        f"{state['clinical_context']}"
    )

    response = llm.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    return {
        "clinical_summary": response.strip(),
    }


def safety_validation(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    result = validate_response(
        state["clinical_summary"]
    )

    return {
        "safety_status": result.status,
        "safety_violations": result.violations,
    }


def build_safe_response(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    return {
        "final_response": (
            "A resposta gerada foi bloqueada "
            "pelos mecanismos de segurança. "
            "Os dados disponíveis devem ser "
            "avaliados diretamente pelo "
            "profissional responsável."
        )
    }


def build_final_response(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    sources = sorted(
        {
            item["source"]
            for item in state[
                "protocol_results"
            ]
        }
    )

    parts = [
        "### Resumo clínico",
        "",
        state["clinical_summary"],
        "",
        "### Pontos de atenção",
        "",
    ]

    attention_points = state.get(
        "attention_points",
        []
    )

    if attention_points:
        parts.extend(
            f"- {point}"
            for point in attention_points
        )
    else:
        parts.append(
            "- Nenhum ponto de atenção "
            "identificado pelas regras do sistema."
        )

    parts.extend([
        "",
        "### Exames pendentes",
        "",
    ])

    pending_exams = state.get(
        "pending_exams",
        []
    )

    if pending_exams:
        parts.extend(
            f"- {exam['exam_type']}"
            for exam in pending_exams
        )
    else:
        parts.append(
            "- Nenhum exame pendente "
            "identificado."
        )

    parts.extend([
        "",
        "### Fontes utilizadas",
        "",
    ])

    parts.extend(
        f"- {source}"
        for source in sources
    )

    parts.extend([
        "",
        "Esta resposta é um suporte à decisão "
        "clínica e requer validação do "
        "profissional responsável.",
    ])

    return {
        "final_response": "\n".join(parts),
        "sources": sources,
    }