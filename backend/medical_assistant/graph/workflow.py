from langgraph.graph import END, START, StateGraph

from medical_assistant.graph.nodes import (
    build_attention_points,
    build_clinical_context,
    build_final_response,
    build_safe_response,
    check_blood_pressure,
    check_pending_exams,
    generate_summary,
    load_patient,
    retrieve_protocols,
    safety_validation,
    save_audit_log,
)
from medical_assistant.graph.state import ClinicalAssistantState


def route_after_validation(
    state: ClinicalAssistantState,
) -> str:
    return state["safety_status"]


def create_clinical_workflow():
    graph = StateGraph(
        ClinicalAssistantState
    )

    graph.add_node(
        "load_patient",
        load_patient,
    )

    graph.add_node(
        "check_blood_pressure",
        check_blood_pressure,
    )

    graph.add_node(
        "check_pending_exams",
        check_pending_exams,
    )

    graph.add_node(
        "retrieve_protocols",
        retrieve_protocols,
    )

    graph.add_node(
        "build_clinical_context",
        build_clinical_context,
    )

    graph.add_node(
        "build_attention_points",
        build_attention_points,
    )

    graph.add_node(
        "generate_summary",
        generate_summary,
    )

    graph.add_node(
        "safety_validation",
        safety_validation,
    )

    graph.add_node(
        "build_final_response",
        build_final_response,
    )

    graph.add_node(
        "build_safe_response",
        build_safe_response,
    )

    graph.add_node(
        "save_audit_log",
        save_audit_log,
    )

    # Fluxo principal
    graph.add_edge(
        START,
        "load_patient",
    )

    graph.add_edge(
        "load_patient",
        "check_blood_pressure",
    )

    graph.add_edge(
        "check_blood_pressure",
        "check_pending_exams",
    )

    graph.add_edge(
        "check_pending_exams",
        "retrieve_protocols",
    )

    graph.add_edge(
        "retrieve_protocols",
        "build_clinical_context",
    )

    graph.add_edge(
        "build_clinical_context",
        "build_attention_points",
    )

    graph.add_edge(
        "build_attention_points",
        "generate_summary",
    )

    graph.add_edge(
        "generate_summary",
        "safety_validation",
    )

    graph.add_conditional_edges(
        "safety_validation",
        route_after_validation,
        {
            "safe": "build_final_response",
            "needs_review": "build_final_response",
            "blocked": "build_safe_response",
        },
    )

    graph.add_edge(
        "build_final_response",
        "save_audit_log",
    )

    graph.add_edge(
        "build_safe_response",
        'save_audit_log',
    )

    graph.add_edge(
        "save_audit_log",
        END,
    )

    return graph.compile()