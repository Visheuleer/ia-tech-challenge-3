# Hypertension Assistant LoRA Adapter

Adapter LoRA fine-tuned para o modelo:

`Qwen/Qwen2.5-1.5B-Instruct`

Este artefato foi treinado para o projeto acadêmico **Medical Assistant**, com foco em suporte ao acompanhamento de pacientes com hipertensão arterial.

## Arquivos principais

- `adapter_config.json`: configuração do adapter LoRA
- `adapter_model.safetensors`: pesos treinados do adapter

O modelo base não é versionado neste repositório e deve ser carregado separadamente a partir do Hugging Face.

## Uso

O backend carrega o modelo base e aplica este adapter em runtime com PEFT.

Em ambientes com GPU/CUDA, a aplicação pode utilizar aceleração por GPU. Em ambientes sem GPU, a inferência pode ser executada em CPU, com maior latência.

> Artefato destinado exclusivamente a fins acadêmicos e demonstrativos.