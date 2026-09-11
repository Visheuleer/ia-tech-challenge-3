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

    history = "\n".join(
        f"- {item['condition']}: {item['notes'] or 'Sem observações'}"
        for item in patient["medical_history"]
    )

    measurements = "\n".join(
        (
            f"- {item['measured_at']}: "
            f"{item['systolic']}/{item['diastolic']} mmHg"
        )
        for item in patient["blood_pressure_measurements"]
    )

    medications = "\n".join(
        (
            f"- {item['name']} {item['dosage']} "
            f"({item['frequency']})"
        )
        for item in patient["medications"]
        if item["active"]
    )

    pending_exams = (
        "\n".join(
            f"- {exam['exam_type']}"
            for exam in state["pending_exams"]
        )
        or "- Nenhum exame pendente"
    )

    protocols = "\n\n".join(
        (
            f"Fonte: {item['source']}\n"
            f"{item['content']}"
        )
        for item in state["protocol_results"]
    )

    context = f"""
        PERGUNTA DO MÉDICO
        {state["question"]}
        
        PACIENTE
        ID: {patient["id"]}
        Nome: {patient["name"]}
        Sexo: {patient["sex"]}
        Data de nascimento: {patient["birth_date"]}
        
        HISTÓRICO CLÍNICO
        {history}
        
        MEDIÇÕES DE PRESSÃO ARTERIAL
        {measurements}
        
        RESUMO DA PRESSÃO
        Status: {state["blood_pressure_status"]}
        Média sistólica: {state["blood_pressure_summary"]["average_systolic"]}
        Média diastólica: {state["blood_pressure_summary"]["average_diastolic"]}
        
        MEDICAMENTOS ATIVOS
        {medications}
        
        EXAMES PENDENTES
        {pending_exams}
        
        PROTOCOLOS RECUPERADOS
        {protocols}
        """.strip()

    return {
        "clinical_context": context,
    }


def generate_response(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    llm = get_medical_llm()

    system_prompt = load_prompt(
        "system/medical_assistant.md"
    )

    response = llm.generate(
        system_prompt=system_prompt,
        user_prompt=state[
            "clinical_context"
        ],
    )

    return {
        "generated_response": response,
    }


def safety_validation(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    result = validate_response(
        state["generated_response"]
    )

    return {
        "safety_status": result.status,
        "safety_violations": (
            result.violations
        ),
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


def add_review_warning(
    state: ClinicalAssistantState,
) -> ClinicalAssistantState:
    response = state[
        "generated_response"
    ]

    final_response = (
        f"{response}\n\n"
        "⚠️ Esta resposta contém elementos "
        "que requerem revisão clínica antes "
        "de qualquer decisão."
    )

    return {
        "final_response": final_response,
    }


def add_sources(
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

    source_text = "\n".join(
        f"- {source}"
        for source in sources
    )

    final_response = (
        f"{state['generated_response']}\n\n"
        "Fontes utilizadas:\n"
        f"{source_text}\n\n"
        "Esta resposta é um suporte à decisão "
        "clínica e requer validação do "
        "profissional responsável."
    )

    return {
        "final_response": final_response,
        "sources": sources,
    }