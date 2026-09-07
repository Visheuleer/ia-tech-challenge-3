from medical_assistant.graph.workflow import (
    create_clinical_workflow,
)


def main() -> None:
    workflow = create_clinical_workflow()

    result = workflow.invoke(
        {
            "patient_id": 2,
            "question": (
                "Analise a situação atual deste paciente "
                "e destaque pontos de atenção."
            ),
        }
    )

    print("=" * 80)
    print("BLOOD PRESSURE STATUS")
    print("=" * 80)
    print(result["blood_pressure_status"])

    print()

    print("=" * 80)
    print("PENDING EXAMS")
    print("=" * 80)
    print(result["pending_exams"])

    print()

    print("=" * 80)
    print("CLINICAL CONTEXT")
    print("=" * 80)
    print(result["clinical_context"])


if __name__ == "__main__":
    main()