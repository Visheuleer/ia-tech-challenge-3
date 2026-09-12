from medical_assistant.graph.workflow import (
    create_clinical_workflow,
)


class AssistantService:
    def __init__(self) -> None:
        self.workflow = (
            create_clinical_workflow()
        )

    def ask(
        self,
        patient_id: int,
        question: str,
    ) -> dict:
        return self.workflow.invoke(
            {
                "patient_id": patient_id,
                "question": question,
            }
        )