---
kind: quality_gate
id: p11_qg_funnel_diag
pillar: P11
llm_function: GOVERN
purpose: Gate de qualidade com pontuação HARD e SOFT para o tool_card de funnel_diag
quality: null
title: "Gate de Qualidade: Diagnóstico de Funil"
version: "1.0.0"
author: n03_builder
tags: [funnel_diag, tool_card, builder, quality_gate]
tldr: "7 gates HARD (cobertura dos 5 estágios, ranking com fórmula explícita, zero número sem origem) + scoring SOFT em 6 dimensões."
domain: "diagnóstico de funil (funnel_diag)"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F7_govern"
keywords: [gate de qualidade, anti-fabricação, cobertura de estágios, funnel_diag]
density_score: 0.90
related:
  - bld_schema_funnel_diag
  - funnel-diagnostic-builder
---
## Quality Gate
# Gate: tool_card (funnel_diag)

## Definição
| Campo | Valor |
|---|---|
| métrica | score SOFT ponderado + todos os gates HARD aprovados |
| limiar | 7.0 para publicar . 8.0 para pool . 9.5 para golden |
| operador | AND (todos os HARD) + média ponderada (SOFT) |
| escopo | qualquer artefato com `kind: tool_card` e `domain` de funil |

## Gates HARD
Todos devem passar. Qualquer falha = rejeição imediata.
| ID | Checagem | Condição de falha |
|---|---|---|
| H01 | Frontmatter parseia como YAML válido | Erro de parse em qualquer campo |
| H02 | id casa com `^p11_tc_[a-z][a-z0-9_]+$` | Prefixo ausente ou caractere inválido |
| H03 | kind == literal `tool_card` | Qualquer outro valor |
| H04 | quality == null | Qualquer valor não-nulo |
| H05 | Os 5 estágios (atrair/engajar/converter/reter/expandir) aparecem no corpo | Estágio ausente sem marcação `[A CONFIRMAR]` |
| H06 | Pelo menos 1 fix ranqueado com fórmula ICE/RICE explícita | Ranking sem fórmula ou sem valores por eixo |
| H07 | Todo número rastreia a uma origem declarada | Número sem `data_sources`, `benchmark` ou `[A CONFIRMAR]` |

## Pontuação SOFT
Pesos somam 100%.
| ID | Dimensão | Peso | 10 pts | 5 pts | 0 pts |
|---|---|---|---|---|---|
| S01 | Especificidade das métricas | 1.0 | Valores concretos com origem em todos os 5 estágios | Mix de concreto e genérico | Inteiramente genérico |
| S02 | Rigor da priorização | 1.0 | Fórmula + valores por eixo explícitos para cada fix | Fórmula citada mas sem valores por eixo | Ranking sem método visível |
| S03 | Identificação do vazamento principal | 1.0 | 1-3 vazamentos com justificativa numérica clara | Vazamento apontado sem número | Nenhum vazamento identificado |
| S04 | Atribuição de origem | 1.0 | Toda métrica rastreável à fonte específica | Fonte mencionada mas vaga | Sem fontes |
| S05 | Tratamento do "problema do denominador" | 0.5 | Compara perda absoluta, não só percentual | Menciona mas não aplica | Ignora completamente |
| S06 | Disciplina anti-fabricação | 1.0 | Toda lacuna marcada `[A CONFIRMAR]`, zero número inventado | Uma lacuna não marcada | Múltiplos números sem origem |

**Score = soma(pontos * peso) / soma(pontos_max * peso) * 10**

## Ações
| Score | Nível | Ação |
|---|---|---|
| >= 9.5 | Golden | Publicar como referência |
| >= 8.0 | Qualificado | Publicar + registrar padrão |
| >= 7.0 | Aprendendo | Usar mas sinalizar para melhoria |
| < 7.0 | Rejeitado | Devolver ao autor com o relatório do gate |

## Exemplo Golden
INPUT: "Diagnostica o funil de um SaaS B2B: 10.000 visitas/mês, 3% ativa trial, 18% do trial converte, churn 2.5%/mês, upsell quase zero."

OUTPUT (recorte):
```yaml
biggest_leak: "Reter"
prioritization_method: "ICE"
```
Vazamento principal: churn de 2.5%/mês equivale, em 12 meses, a perder ~27% da base -- maior perda absoluta de receita que qualquer ganho possível em otimizar a conversão de trial (18%). Fix #1: programa de onboarding pós-venda (Impacto 9, Confiança 7, Facilidade 6 -> score 7.3).

## Anti-Exemplo: vazamento apontado sem número
"O funil parece fraco na conversão, recomendo melhorar o site." -- falha H06 (sem fórmula) e S01/S03 (sem número, sem vazamento localizado).

### H_RELATED: Checagem de Referências Cruzadas (HARD)
- [ ] Campo `related:` preenchido (mínimo 3 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo
- [ ] Pelo menos 1 referência upstream e 1 downstream ou sibling

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_funnel_diag]] | sibling | 0.50 |
| [[funnel-diagnostic-builder]] | sibling | 0.46 |
| [[p11_fb_funnel_diag]] | sibling | 0.42 |
