---
kind: output_template
id: bld_output_template_funnel_diag
pillar: P05
llm_function: PRODUCE
purpose: Template com {{vars}} para a produção do tool_card de funnel_diag
pattern: todo campo aqui existe no schema -- o template deriva, nunca inventa
quality: null
title: "Template de Saída: Diagnóstico de Funil"
version: "1.0.0"
author: n03_builder
tags: [funnel_diag, tool_card, builder, output_template]
tldr: "Frontmatter {{vars}} + corpo em 5 seções: mapa do funil, métricas por estágio, análise de vazamento, fixes priorizados por ROI, suposições."
domain: "diagnóstico de funil (funnel_diag)"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F6_produce"
density_score: 0.90
related:
  - bld_schema_funnel_diag
  - funnel-diagnostic-builder
---
# Template de Saída: tool_card (funnel_diag)

```yaml
id: p11_tc_funnel_diag_{{slug}}
kind: tool_card
pillar: P11
title: "Diagnóstico de Funil -- {{nome_do_produto}}"
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{nome_do_agente_ou_time}}"
domain: "{{modelo_de_negocio}}"
quality: null
tags: [funnel_diag, tool_card, diagnostico_de_funil]
tldr: "{{resumo denso <=160 caracteres com o vazamento principal encontrado}}"
framework: [atrair, engajar, converter, reter, expandir]
prioritization_method: "{{ICE|RICE}}"
data_sources: [{{fonte1}}, {{fonte2}}]
biggest_leak: "{{estágio com maior score de vazamento}}"
```

# {{Título}}

## Mapa do Funil
| Estágio | Métrica principal | Valor | Origem |
|---|---|---|---|
| Atrair | {{métrica}} | {{valor}} | {{fornecido pelo usuário\|benchmark\|estimado}} |
| Engajar | {{métrica}} | {{valor}} | {{origem}} |
| Converter | {{métrica}} | {{valor}} | {{origem}} |
| Reter | {{métrica}} | {{valor}} | {{origem}} |
| Expandir | {{métrica}} | {{valor}} | {{origem}} |

## Métricas por Estágio (detalhe)
| Estágio | Métrica | Valor observado | Benchmark de referência | Gap |
|---|---|---|---|---|
| {{estágio}} | {{métrica}} | {{valor}} | {{benchmark}} | {{delta}} |

## Análise de Vazamento
O estágio **{{estágio_vazamento}}** concentra a maior perda: {{queda_percentual}}% de queda, equivalente a {{perda_absoluta}} em volume/receita -- {{justificativa_numérica}}.

## Fixes Priorizados por ROI ({{ICE|RICE}})
| Fix | Estágio | Impacto | Confiança | Facilidade/Esforço | Score | Ordem |
|---|---|---|---|---|---|---|
| {{fix_1}} | {{estágio}} | {{1-10}} | {{1-10}} | {{1-10}} | {{score}} | 1 |
| {{fix_2}} | {{estágio}} | {{1-10}} | {{1-10}} | {{1-10}} | {{score}} | 2 |
| {{fix_3}} | {{estágio}} | {{1-10}} | {{1-10}} | {{1-10}} | {{score}} | 3 |

## Suposições e Dados a Confirmar
- {{lacuna_1}}: `[A CONFIRMAR]`
- {{lacuna_2}}: `[A CONFIRMAR]`
- Benchmarks usados são referências públicas de indústria, não medição do cliente.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_funnel_diag]] | upstream | 0.38 |
| [[funnel-diagnostic-builder]] | upstream | 0.36 |
| [[bld_knowledge_card_funnel_diag]] | upstream | 0.30 |
