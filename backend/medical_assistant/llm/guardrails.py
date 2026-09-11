import re
from dataclasses import dataclass


@dataclass
class SafetyValidationResult:
    status: str
    violations: list[str]


BLOCK_PATTERNS = {
    "direct_prescription": [
        r"\bcomece a tomar\b",
        r"\binicie\b.*\bmg\b",
        r"\bprescrevo\b",
        r"\btome\s+\d+\s*mg\b",
    ],

    "dose_change": [
        r"\baumente a dose\b",
        r"\breduza a dose\b",
        r"\bdobre a dose\b",
        r"\baltere a dose\b",
    ],

    "treatment_suspension": [
        r"\bsuspenda\b.*\bmedicamento\b",
        r"\bpare de tomar\b",
        r"\binterrompa\b.*\bmedicamento\b",
    ],

    "fabricated_certainty": [
        r"\bcertamente tem\b",
        r"\bdiagnóstico definitivo\b",
        r"\bcom certeza é\b",
    ],
}


REVIEW_PATTERNS = {
    "therapeutic_language": [
        r"\brecomendo\b",
        r"\btratamento indicado\b",
        r"\bconduta indicada\b",
    ],

    "diagnostic_language": [
        r"\bo diagnóstico é\b",
        r"\bindica que o paciente tem\b",
    ],
}


def _matches_any(
    text: str,
    patterns: list[str],
) -> bool:
    return any(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
        for pattern in patterns
    )


def validate_response(
    response: str,
) -> SafetyValidationResult:
    violations: list[str] = []

    for name, patterns in BLOCK_PATTERNS.items():
        if _matches_any(
            response,
            patterns,
        ):
            violations.append(name)

    if violations:
        return SafetyValidationResult(
            status="blocked",
            violations=violations,
        )

    review_flags: list[str] = []

    for name, patterns in REVIEW_PATTERNS.items():
        if _matches_any(
            response,
            patterns,
        ):
            review_flags.append(name)

    if review_flags:
        return SafetyValidationResult(
            status="needs_review",
            violations=review_flags,
        )

    return SafetyValidationResult(
        status="safe",
        violations=[],
    )