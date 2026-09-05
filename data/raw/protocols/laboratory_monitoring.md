# Protocolo Interno Sintético — Monitoramento Laboratorial

> Documento sintético criado exclusivamente para demonstração acadêmica.
> Não deve ser utilizado como protocolo clínico real.

## Objetivo

Orientar o fluxo automatizado de identificação de exames laboratoriais
disponíveis ou pendentes em pacientes acompanhados pelo sistema.

## Exames pendentes

Quando um exame estiver registrado com status "pending", o assistente
deve apresentar esse exame na seção de informações pendentes.

O sistema não deve inferir um resultado para exames ainda não realizados.

## Resultados disponíveis

Resultados laboratoriais disponíveis podem ser apresentados como parte
do contexto clínico enviado ao modelo.

Quando um resultado estiver fora do intervalo de referência registrado
no prontuário, o assistente pode destacá-lo como ponto de atenção.

A interpretação e qualquer conduta decorrente do resultado devem ser
validadas por profissional habilitado.

## Função renal

Informações relacionadas à função renal devem receber atenção adicional
quando o prontuário também registrar doença renal ou outras condições
associadas.

O assistente deve apresentar os dados existentes sem prescrever
alterações terapêuticas.