import re


PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"
        ),
        "[CPF]",
    ),
    (
        re.compile(
            r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"
        ),
        "[EMAIL]",
    ),
    (
        re.compile(
            r"\b(?:\+?55\s*)?"
            r"(?:\(?\d{2}\)?\s*)?"
            r"\d{4,5}[-\s]?\d{4}\b"
        ),
        "[PHONE]",
    ),
    (
        re.compile(
            r"\bPaciente\s+\d+\b",
            flags=re.IGNORECASE,
        ),
        "[PATIENT]",
    ),
]


def anonymize_text(text: str) -> str:
    result = text

    for pattern, replacement in PATTERNS:
        result = pattern.sub(
            replacement,
            result,
        )

    return result


def anonymize_record(
    record: dict,
) -> dict:
    anonymized = record.copy()

    for field in (
        "question",
        "answer",
        "instruction",
        "response",
    ):
        value = anonymized.get(field)

        if isinstance(value, str):
            anonymized[field] = (
                anonymize_text(value)
            )

    return anonymized