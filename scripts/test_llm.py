from medical_assistant.llm.model import get_medical_llm
from medical_assistant.llm.prompt_loader import load_prompt


def main() -> None:
    llm = get_medical_llm()

    system_prompt = load_prompt(
        "system/medical_assistant.md"
    )

    response = llm.generate(
        system_prompt=system_prompt,
        user_prompt=(
            "Um paciente possui várias medições recentes "
            "de pressão arterial elevadas. "
            "Posso aumentar a dose da medicação automaticamente?"
        ),
    )

    print(response)


if __name__ == "__main__":
    main()