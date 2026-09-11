import json
from pathlib import Path
from typing import Any

from peft import PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)

from medical_assistant.core.config import settings


TEST_PATH = Path("data/processed/test.jsonl")

OUTPUT_PATH = Path(
    "artifacts/evaluation/model_comparison.jsonl"
)


def load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(
                    json.loads(line)
                )

    return records


def load_base_model():
    tokenizer = AutoTokenizer.from_pretrained(
        settings.llm_base_model
    )

    model = AutoModelForCausalLM.from_pretrained(
        settings.llm_base_model,
        torch_dtype="auto",
        device_map="auto",
    )

    model.eval()

    return tokenizer, model


def load_finetuned_model():
    tokenizer = AutoTokenizer.from_pretrained(
        settings.llm_base_model
    )

    base_model = (
        AutoModelForCausalLM.from_pretrained(
            settings.llm_base_model,
            torch_dtype="auto",
            device_map="auto",
        )
    )

    model = PeftModel.from_pretrained(
        base_model,
        settings.llm_adapter_path,
    )

    model.eval()

    return tokenizer, model


def generate_response(
    tokenizer,
    model,
    messages: list[dict[str, str]],
) -> str:
    prompt_messages = [
        message
        for message in messages
        if message["role"] != "assistant"
    ]

    text = tokenizer.apply_chat_template(
        prompt_messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        text,
        return_tensors="pt",
    ).to(model.device)

    generated_ids = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=False,
    )

    new_tokens = generated_ids[
        :,
        inputs.input_ids.shape[1]:
    ]

    return tokenizer.batch_decode(
        new_tokens,
        skip_special_tokens=True,
    )[0].strip()


def get_reference(
    messages: list[dict[str, str]],
) -> str:
    for message in messages:
        if message["role"] == "assistant":
            return message["content"]

    raise ValueError(
        "Reference assistant message not found."
    )


def main() -> None:
    records = load_jsonl(
        TEST_PATH
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Loading base model...")

    base_tokenizer, base_model = (
        load_base_model()
    )

    print("Loading fine-tuned model...")

    ft_tokenizer, ft_model = (
        load_finetuned_model()
    )

    results: list[dict[str, Any]] = []

    for index, record in enumerate(
        records,
        start=1,
    ):
        messages = record["messages"]

        question = next(
            message["content"]
            for message in messages
            if message["role"] == "user"
        )

        reference = get_reference(
            messages
        )

        print(
            f"[{index}/{len(records)}] "
            f"{question[:70]}"
        )

        base_response = generate_response(
            base_tokenizer,
            base_model,
            messages,
        )

        finetuned_response = (
            generate_response(
                ft_tokenizer,
                ft_model,
                messages,
            )
        )

        results.append(
            {
                "metadata": record[
                    "metadata"
                ],
                "question": question,
                "reference": reference,
                "base_response": (
                    base_response
                ),
                "finetuned_response": (
                    finetuned_response
                ),
            }
        )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        for result in results:
            file.write(
                json.dumps(
                    result,
                    ensure_ascii=False,
                )
            )
            file.write("\n")

    print()
    print(
        f"Evaluation completed: "
        f"{len(results)} examples."
    )

    print(
        f"Results saved to "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()