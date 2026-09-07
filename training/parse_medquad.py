import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


MEDQUAD_DIR = Path("data/raw/datasets/medquad")
OUTPUT_PATH = Path("data/interim/medquad_hypertension.jsonl")


PRIMARY_FOCUS_KEYWORDS = {
    "hypertension",
    "high blood pressure",
    "blood pressure medicines",
    "pulmonary hypertension",
}


SECONDARY_FOCUS_KEYWORDS = {
    "kidney",
    "renal",
    "diabetes",
    "heart",
    "cardiovascular",
    "coronary",
    "stroke",
    "cholesterol",
    "vascular",
}


CLINICAL_CONTEXT_KEYWORDS = {
    "hypertension",
    "high blood pressure",
    "blood pressure",
    "antihypertensive",
    "losartan",
    "amlodipine",
    "ace inhibitor",
    "angiotensin receptor blocker",
    "arb",
    "diuretic",
    "systolic",
    "diastolic",
}


ALLOWED_QUESTION_TYPES = {
    "information",
    "symptoms",
    "exams and tests",
    "treatment",
    "prevention",
    "considerations",
    "susceptibility",
    "causes",
}


def normalize_text(text: str | None) -> str:
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def contains_any(
    text: str,
    keywords: set[str],
) -> bool:
    text = text.lower()

    return any(
        keyword in text
        for keyword in keywords
    )


def is_primary_topic(
    focus: str,
) -> bool:
    return contains_any(
        focus,
        PRIMARY_FOCUS_KEYWORDS,
    )


def is_secondary_topic(
    focus: str,
    question: str,
    answer: str,
) -> bool:
    if not contains_any(
        focus,
        SECONDARY_FOCUS_KEYWORDS,
    ):
        return False

    qa_text = f"{question} {answer}"

    return contains_any(
        qa_text,
        CLINICAL_CONTEXT_KEYWORDS,
    )


def is_relevant(
    focus: str,
    question: str,
    answer: str,
    qtype: str,
) -> bool:
    if qtype not in ALLOWED_QUESTION_TYPES:
        return False

    if is_primary_topic(focus):
        return True

    return is_secondary_topic(
        focus=focus,
        question=question,
        answer=answer,
    )


def parse_xml_file(
    file_path: Path,
) -> list[dict]:
    try:
        tree = ET.parse(file_path)
    except ET.ParseError as exc:
        print(
            f"[WARN] Could not parse {file_path}: {exc}"
        )
        return []

    root = tree.getroot()

    source = root.attrib.get(
        "source",
        "unknown",
    )

    url = root.attrib.get(
        "url",
        "",
    )

    document_id = root.attrib.get(
        "id",
        "",
    )

    focus_element = root.find("Focus")

    focus = normalize_text(
        "".join(focus_element.itertext())
        if focus_element is not None
        else ""
    )

    qa_pairs_element = root.find("QAPairs")

    if qa_pairs_element is None:
        return []

    records: list[dict] = []

    for qa_pair in qa_pairs_element.findall(
        "QAPair"
    ):
        question_element = qa_pair.find(
            "Question"
        )

        answer_element = qa_pair.find(
            "Answer"
        )

        if (
            question_element is None
            or answer_element is None
        ):
            continue

        question = normalize_text(
            "".join(
                question_element.itertext()
            )
        )

        answer = normalize_text(
            "".join(
                answer_element.itertext()
            )
        )

        if not question or not answer:
            continue

        qid = question_element.attrib.get(
            "qid",
            "",
        )

        qtype = normalize_text(
            question_element.attrib.get(
                "qtype",
                "unknown",
            )
        ).lower()

        if not is_relevant(
            focus=focus,
            question=question,
            answer=answer,
            qtype=qtype,
        ):
            continue

        records.append(
            {
                "dataset": "MedQuAD",
                "document_id": document_id,
                "source": source,
                "url": url,
                "focus": focus,
                "qid": qid,
                "qtype": qtype,
                "question": question,
                "answer": answer,
                "file": str(file_path),
            }
        )

    return records


def parse_medquad(
    root_dir: Path,
) -> list[dict]:
    xml_files = sorted(
        root_dir.rglob("*.xml")
    )

    if not xml_files:
        raise FileNotFoundError(
            f"No XML files found in {root_dir}"
        )

    print(
        f"Found {len(xml_files)} XML files."
    )

    records: list[dict] = []

    for index, file_path in enumerate(
        xml_files,
        start=1,
    ):
        records.extend(
            parse_xml_file(file_path)
        )

        if index % 500 == 0:
            print(
                f"Processed "
                f"{index}/{len(xml_files)} "
                "XML files."
            )

    return records


def remove_duplicates(
    records: list[dict],
) -> list[dict]:
    unique_records: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for record in records:
        key = (
            record["question"].lower(),
            record["answer"].lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_records.append(record)

    return unique_records


def save_jsonl(
    records: list[dict],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
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


def print_summary(
    records: list[dict],
) -> None:
    sources: dict[str, int] = {}
    question_types: dict[str, int] = {}
    focuses: dict[str, int] = {}

    for record in records:
        source = record["source"]
        qtype = record["qtype"]
        focus = record["focus"]

        sources[source] = (
            sources.get(source, 0) + 1
        )

        question_types[qtype] = (
            question_types.get(qtype, 0) + 1
        )

        focuses[focus] = (
            focuses.get(focus, 0) + 1
        )

    print()
    print("=" * 70)
    print("MEDQUAD CURATION SUMMARY")
    print("=" * 70)

    print(
        f"Relevant QA pairs: {len(records)}"
    )

    print()
    print("By source:")

    for source, count in sorted(
        sources.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"  {source}: {count}")

    print()
    print("By question type:")

    for qtype, count in sorted(
        question_types.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"  {qtype}: {count}")

    print()
    print("Top focuses:")

    for focus, count in sorted(
        focuses.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:20]:
        print(
            f"  {focus}: {count}"
        )


def main() -> None:
    records = parse_medquad(
        MEDQUAD_DIR
    )

    print(
        f"Relevant before deduplication: "
        f"{len(records)}"
    )

    records = remove_duplicates(
        records
    )

    save_jsonl(
        records=records,
        output_path=OUTPUT_PATH,
    )

    print_summary(
        records
    )

    print()
    print(
        "Curated dataset saved to "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()