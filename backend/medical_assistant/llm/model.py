from functools import lru_cache
from pathlib import Path

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)

from medical_assistant.core.config import settings


class MedicalLLM:
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            settings.llm_base_model,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            settings.llm_base_model,
            torch_dtype="auto",
            device_map="auto",
        )

        self.model.eval()

        self.adapter_loaded = False

        self._load_adapter_if_available()

    def _load_adapter_if_available(self) -> None:
        adapter_path = Path(settings.llm_adapter_path)

        if not adapter_path.exists():
            return

        try:
            from peft import PeftModel

            self.model = PeftModel.from_pretrained(
                self.model,
                str(adapter_path),
            )

            self.model.eval()
            self.adapter_loaded = True

        except Exception as exc:
            raise RuntimeError(
                f"Failed to load LoRA adapter from {adapter_path}"
            ) from exc

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
        ).to(self.model.device)

        with torch.inference_mode():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=settings.llm_max_new_tokens,
                temperature=settings.llm_temperature,
                do_sample=settings.llm_temperature > 0,
            )

        new_tokens = generated_ids[
            :,
            inputs.input_ids.shape[1] :
        ]

        response = self.tokenizer.batch_decode(
            new_tokens,
            skip_special_tokens=True,
        )[0]

        return response.strip()


@lru_cache
def get_medical_llm() -> MedicalLLM:
    return MedicalLLM()