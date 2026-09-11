from medical_assistant.graph.workflow import (
    create_clinical_workflow,
)


def main() -> None:
    workflow = (
        create_clinical_workflow()
    )

    result = workflow.invoke(
        {
            "patient_id": 2,
            "question": (
                "Analise a situação atual "
                "deste paciente e destaque "
                "os principais pontos de atenção."
            ),
        }
    )

    print()
    print("=" * 80)
    print("SAFETY STATUS")
    print("=" * 80)
    print(
        result["safety_status"]
    )

    print()
    print("=" * 80)
    print("SAFETY VIOLATIONS")
    print("=" * 80)
    print(
        result["safety_violations"]
    )

    print()
    print("=" * 80)
    print("FINAL RESPONSE")
    print("=" * 80)
    print(
        result["final_response"]
    )


if __name__ == "__main__":
    main()