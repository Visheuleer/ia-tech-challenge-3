import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from medical_assistant.llm.prompt_loader import (
    load_prompt,
)

from training.anonymize import anonymize_record


MEDQUAD_PATH = Path(
    "data/interim/medquad_hypertension.jsonl"
)

SYNTHETIC_PATH = Path(
    "data/raw/datasets/synthetic/"
    "hypertension_qa.jsonl"
)

OUTPUT_DIR = Path(
    "data/processed"
)

RANDOM_SEED = 42

TRAIN_RATIO = 0.8
VALIDATION_RATIO = 0.1
TEST_RATIO = 0.1


def normalize_text(
    text: str,
) -> str:
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def read_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    records: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(
            file,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                records.append(
                    json.loads(line)
                )

            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at "
                    f"{path}:{line_number}"
                ) from exc

    return records


def prepare_medquad_record(
    record: dict[str, Any],
    system_prompt: str,
) -> dict[str, Any]:
    record = anonymize_record(record)

    question = normalize_text(
        record["question"]
    )

    answer = normalize_text(
        record["answer"]
    )

    return {
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": question,
            },
            {
                "role": "assistant",
                "content": answer,
            },
        ],
        "metadata": {
            "dataset": "MedQuAD",
            "source": record.get(
                "source"
            ),
            "document_id": record.get(
                "document_id"
            ),
            "qid": record.get(
                "qid"
            ),
            "qtype": record.get(
                "qtype"
            ),
            "focus": record.get(
                "focus"
            ),
        },
    }


def prepare_synthetic_record(
    record: dict[str, Any],
    system_prompt: str,
) -> dict[str, Any]:
    record = anonymize_record(record)

    instruction = normalize_text(
        record["instruction"]
    )

    response = normalize_text(
        record["response"]
    )

    return {
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": instruction,
            },
            {
                "role": "assistant",
                "content": response,
            },
        ],
        "metadata": {
            "dataset": "synthetic",
            "category": record.get(
                "category"
            ),
        },
    }


def split_medquad_by_document(
    records: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    groups: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(list)

    for record in records:
        metadata = record["metadata"]

        group_id = (
            f"{metadata.get('source')}::"
            f"{metadata.get('document_id')}"
        )

        groups[group_id].append(
            record
        )

    group_ids = list(
        groups.keys()
    )

    random.shuffle(
        group_ids
    )

    total = len(group_ids)

    train_end = int(
        total * TRAIN_RATIO
    )

    validation_end = train_end + int(
        total * VALIDATION_RATIO
    )

    train_groups = group_ids[
        :train_end
    ]

    validation_groups = group_ids[
        train_end:validation_end
    ]

    test_groups = group_ids[
        validation_end:
    ]

    def flatten(
        selected_groups: list[str],
    ) -> list[dict[str, Any]]:
        return [
            record
            for group_id in selected_groups
            for record in groups[group_id]
        ]

    return (
        flatten(train_groups),
        flatten(validation_groups),
        flatten(test_groups),
    )


def split_synthetic_by_category(
    records: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    categories: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(list)

    for record in records:
        category = (
            record["metadata"].get(
                "category"
            )
            or "unknown"
        )

        categories[category].append(
            record
        )

    train: list[dict[str, Any]] = []
    validation: list[dict[str, Any]] = []
    test: list[dict[str, Any]] = []

    for category_records in (
        categories.values()
    ):
        random.shuffle(
            category_records
        )

        count = len(
            category_records
        )

        if count >= 4:
            test.append(
                category_records[0]
            )

            validation.append(
                category_records[1]
            )

            train.extend(
                category_records[2:]
            )

        elif count == 3:
            test.append(
                category_records[0]
            )

            validation.append(
                category_records[1]
            )

            train.append(
                category_records[2]
            )

        else:
            train.extend(
                category_records
            )

    return (
        train,
        validation,
        test,
    )


def remove_duplicates(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()

    for record in records:
        user_message = next(
            message["content"]
            for message in record["messages"]
            if message["role"] == "user"
        )

        key = user_message.casefold()

        if key in seen:
            continue

        seen.add(key)
        unique.append(
            record
        )

    return unique


def write_jsonl(
    path: Path,
    records: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
            )

            file.write("\n")


def print_dataset_summary(
    name: str,
    records: list[dict[str, Any]],
) -> None:
    counts: dict[str, int] = {}

    for record in records:
        dataset = (
            record["metadata"][
                "dataset"
            ]
        )

        counts[dataset] = (
            counts.get(dataset, 0)
            + 1
        )

    print(
        f"{name}: {len(records)} examples"
    )

    for dataset, count in sorted(
        counts.items()
    ):
        print(
            f"  {dataset}: {count}"
        )


def main() -> None:
    random.seed(
        RANDOM_SEED
    )

    system_prompt = load_prompt(
        "system/medical_assistant.md"
    )

    medquad_raw = read_jsonl(
        MEDQUAD_PATH
    )

    synthetic_raw = read_jsonl(
        SYNTHETIC_PATH
    )

    medquad = [
        prepare_medquad_record(
            record,
            system_prompt,
        )
        for record in medquad_raw
    ]

    synthetic = [
        prepare_synthetic_record(
            record,
            system_prompt,
        )
        for record in synthetic_raw
    ]

    medquad = remove_duplicates(
        medquad
    )

    synthetic = remove_duplicates(
        synthetic
    )

    (
        medquad_train,
        medquad_validation,
        medquad_test,
    ) = split_medquad_by_document(
        medquad
    )

    (
        synthetic_train,
        synthetic_validation,
        synthetic_test,
    ) = split_synthetic_by_category(
        synthetic
    )

    train = (
        medquad_train
        + synthetic_train
    )

    validation = (
        medquad_validation
        + synthetic_validation
    )

    test = (
        medquad_test
        + synthetic_test
    )

    random.shuffle(train)
    random.shuffle(validation)
    random.shuffle(test)

    write_jsonl(
        OUTPUT_DIR / "train.jsonl",
        train,
    )

    write_jsonl(
        OUTPUT_DIR / "validation.jsonl",
        validation,
    )

    write_jsonl(
        OUTPUT_DIR / "test.jsonl",
        test,
    )

    print()
    print("=" * 60)
    print("DATASET PREPARATION SUMMARY")
    print("=" * 60)

    print(
        f"MedQuAD input: "
        f"{len(medquad_raw)}"
    )

    print(
        f"Synthetic input: "
        f"{len(synthetic_raw)}"
    )

    print()

    print_dataset_summary(
        "Train",
        train,
    )

    print_dataset_summary(
        "Validation",
        validation,
    )

    print_dataset_summary(
        "Test",
        test,
    )

    print()

    print(
        f"Total: "
        f"{len(train) + len(validation) + len(test)}"
    )

    print()
    print(
        "Processed datasets saved to "
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()