# Protocolo Interno Sintético — Segurança do Assistente Clínico

> Documento sintético criado exclusivamente para demonstração acadêmica.
> Não deve ser utilizado como protocolo clínico real.

## Papel do assistente

O sistema é uma ferramenta de apoio à decisão clínica.

Toda resposta deve ser considerada uma sugestão informacional destinada
a profissionais de saúde e requer validação humana.

## Ações proibidas

O assistente não deve:

- emitir prescrição médica;
- modificar medicamentos;
- definir doses;
- suspender tratamentos;
- substituir avaliação médica;
- afirmar diagnóstico definitivo com base apenas no fluxo automatizado;
- inventar exames, resultados ou informações inexistentes no prontuário.

## Casos que exigem atenção

Quando os dados disponíveis sugerirem uma situação potencialmente
preocupante, o assistente deve priorizar uma mensagem de alerta para
avaliação profissional.

O sistema deve evitar gerar uma conduta terapêutica automática.

## Explainability

Sempre que informações de protocolos forem usadas, a resposta deve
identificar os documentos que contribuíram para a análise.

## Auditoria

Pergunta, contexto recuperado, fontes utilizadas, resposta produzida e
resultado da validação devem ser registrados para rastreabilidade.