from langgraph.graph import END, START, StateGraph

from medical_assistant.graph.nodes import (
    build_clinical_context,
    check_blood_pressure,
    check_pending_exams,
    load_patient,
    retrieve_protocols,
)
from medical_assistant.graph.state import ClinicalAssistantState


def create_clinical_workflow():
    graph = StateGraph(ClinicalAssistantState)

    graph.add_node("load_patient", load_patient)
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

    graph.add_edge(START, "load_patient")
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
        END,
    )

    return graph.compile()