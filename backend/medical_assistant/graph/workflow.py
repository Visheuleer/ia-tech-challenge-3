from langgraph.graph import END, START, StateGraph

from medical_assistant.graph.nodes import (
    add_review_warning,
    build_final_response,
    build_clinical_context,
    build_safe_response,
    check_blood_pressure,
    check_pending_exams,
    generate_response,
    load_patient,
    retrieve_protocols,
    safety_validation,
)
from medical_assistant.graph.state import ClinicalAssistantState


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
        "generate_response",
        generate_response,
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
        "add_review_warning",
        add_review_warning,
    )

    graph.add_node(
        "build_safe_response",
        build_safe_response,
    )

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
        "generate_response",
    )

    graph.add_edge(
        "generate_response",
        "safety_validation",
    )

    graph.add_conditional_edges(
        "safety_validation",
        route_after_validation,
        {
            "safe": "add_sources",
            "needs_review": (
                "add_review_warning"
            ),
            "blocked": (
                "build_safe_response"
            ),
        },
    )

    graph.add_edge(
        "add_sources",
        END,
    )

    graph.add_edge(
        "add_review_warning",
        END,
    )

    graph.add_edge(
        "build_safe_response",
        END,
    )

    return graph.compile()


def route_after_validation(
    state: ClinicalAssistantState,
) -> str:
    return state["safety_status"]