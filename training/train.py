import json
from pathlib import Path
from typing import Any

import torch
import yaml
from datasets import Dataset
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
)
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)


CONFIG_PATH = Path(
    "training/configs/training_config.yaml"
)

TRAIN_PATH = Path(
    "data/processed/train.jsonl"
)

VALIDATION_PATH = Path(
    "data/processed/validation.jsonl"
)


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return yaml.safe_load(file)


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


def check_environment() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA GPU not available. "
            "QLoRA training requires a compatible GPU."
        )

    print(
        f"GPU: {torch.cuda.get_device_name(0)}"
    )

    print(
        f"CUDA version: {torch.version.cuda}"
    )


def create_tokenizer(
    model_name: str,
):
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = (
            tokenizer.eos_token
        )

    tokenizer.padding_side = "right"

    return tokenizer


def create_model(
    config: dict[str, Any],
):
    model_config = config["model"]
    quantization_config = config[
        "quantization"
    ]

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=quantization_config[
            "load_in_4bit"
        ],
        bnb_4bit_quant_type=(
            quantization_config[
                "quant_type"
            ]
        ),
        bnb_4bit_use_double_quant=(
            quantization_config[
                "use_double_quant"
            ]
        ),
        bnb_4bit_compute_dtype=(
            torch.float16
        ),
    )

    model = (
        AutoModelForCausalLM
        .from_pretrained(
            model_config["name"],
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.float16,
        )
    )

    model.config.use_cache = False

    model = prepare_model_for_kbit_training(
        model
    )

    return model


def apply_lora(
    model,
    config: dict[str, Any],
):
    lora_config = config["lora"]

    peft_config = LoraConfig(
        r=lora_config["r"],
        lora_alpha=lora_config[
            "alpha"
        ],
        lora_dropout=lora_config[
            "dropout"
        ],
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )

    model = get_peft_model(
        model,
        peft_config,
    )

    model.print_trainable_parameters()

    return model


def create_dataset(
    records: list[dict[str, Any]],
    tokenizer,
    max_length: int,
) -> Dataset:
    texts = []

    for record in records:
        text = tokenizer.apply_chat_template(
            record["messages"],
            tokenize=False,
            add_generation_prompt=False,
        )

        texts.append(
            {
                "text": text,
            }
        )

    dataset = Dataset.from_list(
        texts
    )

    def tokenize(
        batch: dict[str, list[str]],
    ):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_length,
            padding=False,
        )

    return dataset.map(
        tokenize,
        batched=True,
        remove_columns=["text"],
    )


def main() -> None:
    check_environment()

    config = load_config()

    model_name = config["model"]["name"]
    max_length = config[
        "model"
    ]["max_length"]

    output_dir = Path(
        config["output"]["directory"]
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("Loading tokenizer...")

    tokenizer = create_tokenizer(
        model_name
    )

    print("Loading quantized model...")

    model = create_model(
        config
    )

    print("Applying LoRA...")

    model = apply_lora(
        model,
        config,
    )

    print()
    print("Loading datasets...")

    train_records = load_jsonl(
        TRAIN_PATH
    )

    validation_records = load_jsonl(
        VALIDATION_PATH
    )

    train_dataset = create_dataset(
        train_records,
        tokenizer,
        max_length,
    )

    validation_dataset = create_dataset(
        validation_records,
        tokenizer,
        max_length,
    )

    print(
        f"Train examples: "
        f"{len(train_dataset)}"
    )

    print(
        f"Validation examples: "
        f"{len(validation_dataset)}"
    )

    training_config = config[
        "training"
    ]

    training_args = TrainingArguments(
        output_dir=str(output_dir),

        num_train_epochs=training_config[
            "epochs"
        ],

        learning_rate=training_config[
            "learning_rate"
        ],

        per_device_train_batch_size=(
            training_config[
                "per_device_train_batch_size"
            ]
        ),

        per_device_eval_batch_size=(
            training_config[
                "per_device_eval_batch_size"
            ]
        ),

        gradient_accumulation_steps=(
            training_config[
                "gradient_accumulation_steps"
            ]
        ),

        warmup_steps=training_config[
            "warmup_steps"
        ],

        weight_decay=training_config[
            "weight_decay"
        ],

        logging_steps=training_config[
            "logging_steps"
        ],

        eval_strategy="epoch",
        save_strategy="epoch",

        save_total_limit=2,

        fp16=True,
        bf16=False,

        gradient_checkpointing=True,

        report_to="none",

        seed=training_config["seed"],

        load_best_model_at_end=True,

        metric_for_best_model="eval_loss",
        greater_is_better=False,
    )

    data_collator = (
        DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        data_collator=data_collator,
    )

    print()
    print("=" * 70)
    print("STARTING QLORA TRAINING")
    print("=" * 70)
    print()

    trainer.train()

    print()
    print("Saving LoRA adapter...")

    trainer.model.save_pretrained(
        output_dir
    )

    tokenizer.save_pretrained(
        output_dir
    )

    print()
    print(
        f"Training completed. "
        f"Adapter saved to {output_dir}"
    )


if __name__ == "__main__":
    main()