---
quality: null
id: p11_fb_funnel_diag
kind: builder_default
pillar: P11
title: "Feedback: Diagnóstico de Funil"
domain: funnel_diag
version: 1.1.0
tags: [feedback, anti-patterns, P11, funnel_diag]
8f: "F7_govern"
keywords: [anti-padrões, modos de falha, protocolo de correção, funnel_diag]
tldr: "Anti-padrões e protocolo de correção para o builder de funnel_diag: 6 regras NUNCA + 4 modos de falha + correção em 3 passos."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-07-17"
updated: "2026-07-17"
related:
  - p11_fb_quality_gate
  - p11_fb__builder
  - pricing_page_cexai_s1
  - p11_fb_kind
  - p11_fb_skill
  - p11_fb_audit_log
  - p11_fb_agent
  - p11_fb_workflow
  - p11_fb_domain_vocabulary
  - p11_fb_data_contract
---
# Feedback: Diagnóstico de Funil

## Anti-Padrões (NUNCA fazer)
| Regra | Violação | Gate |
|---|---|---|
| Sem auto-pontuação | Nunca atribuir score de qualidade ao próprio diagnóstico | H04 |
| Sem alucinação de métrica | Toda métrica cita origem; nenhum número inventado | H07 |
| Sem estágio omitido | Os 5 estágios sempre aparecem, mesmo que como lacuna | H05 |
| Sem ranking sem fórmula | Todo fix ranqueado mostra Impacto/Confiança/Facilidade explícitos | H06 |
| Sem output parcial | Artefato completo, sem truncamento nem "..." | H01 |
| Sem confundir com roi_calculator | Nunca calcula payback/NPV -- só diagnostica e prioriza | -- |

## Modos de Falha Comuns
| Modo de Falha | Sinal | Correção |
|---|---|---|
| Vazamento apontado sem número | "parece fraco em X" sem dado | Exigir métrica + origem antes de concluir |
| Ranking só por facilidade | Fixes ordenados por "mais fácil primeiro" | Recalcular com Impacto x Confiança incluídos |
| Percentual sem volume absoluto | Conclusão baseada só na pior taxa | Aplicar o filtro de perda absoluta (ver P10 memória) |
| Lacuna preenchida silenciosamente | Número aparece sem `[A CONFIRMAR]` nem origem | Rotular explicitamente e devolver para o usuário confirmar |

## Protocolo de Correção
| Passo | Ação | Gate |
|---|---|---|
| 1 | Identificar qual gate H01-H07 falhou | F7 |
| 2 | Retornar a F6 PRODUCE com instrução de correção explícita | F6 |
| 3 | Re-rodar F7 GOVERN | F7 |
| 4 | Máximo 2 tentativas antes de escalar para revisão humana | F8 |

## Comportamentos-Chave
- O builder DEVE carregar os 12 ISOs (1:1 com os pilares) antes de produzir qualquer diagnóstico.
- O builder DEVE rodar o gate F7 GOVERN antes de salvar a saída.
- O builder DEVE sinalizar toda lacuna de dado como `[A CONFIRMAR]`, nunca estimar silenciosamente.
- O builder NÃO DEVE se auto-pontuar -- o campo `quality` é sempre `null`.

## Limiares de Qualidade
| Dimensão | Peso | Meta | Gate |
|---|---|---|---|
| Cobertura dos 5 estágios | 30% | >= 8.0 | H05 |
| Rigor da priorização (fórmula explícita) | 30% | >= 8.0 | H06 |
| Disciplina anti-fabricação | 40% | >= 8.5 | H07 |
| Densidade | -- | >= 0.85 | S09 |


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_fb_quality_gate]] | sibling | 0.21 |
| [[p11_fb__builder]] | sibling | 0.21 |
| [[pricing_page_cexai_s1]] | upstream | 0.20 |
| [[p11_fb_kind]] | sibling | 0.20 |
| [[p11_fb_skill]] | sibling | 0.20 |
| [[p11_fb_audit_log]] | sibling | 0.20 |
| [[p11_fb_agent]] | sibling | 0.20 |
| [[p11_fb_workflow]] | sibling | 0.20 |
| [[p11_fb_domain_vocabulary]] | sibling | 0.20 |
| [[p11_fb_data_contract]] | sibling | 0.19 |
