from functools import lru_cache
from pathlib import Path


PROMPTS_DIR = Path(__file__).parent


@lru_cache
def load_prompt(relative_path: str) -> str:
    prompt_path = PROMPTS_DIR / "prompts" / relative_path

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_path}"
        )

    return prompt_path.read_text(
        encoding="utf-8"
    ).strip()