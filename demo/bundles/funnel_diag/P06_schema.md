---
kind: schema
id: bld_schema_funnel_diag
pillar: P06
llm_function: CONSTRAIN
purpose: Schema formal do tool_card de funnel_diag -- fonte única da verdade
pattern: TEMPLATE deriva deste schema. CONFIG restringe este schema. Nunca o inverso.
quality: null
title: "Schema: Diagnóstico de Funil"
version: "1.0.0"
author: n03_builder
tags: [funnel_diag, tool_card, builder, schema]
tldr: "Campos obrigatórios do tool_card funnel_diag: framework de 5 estágios, método de priorização, data_sources, biggest_leak, fixes_ranked."
domain: "diagnóstico de funil (funnel_diag)"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F1_constrain"
keywords: [schema do tool_card, id pattern, estrutura do corpo, campos obrigatórios, funnel_diag]
density_score: 0.90
related:
  - bld_output_template_funnel_diag
  - p11_qg_funnel_diag
---
# Schema: tool_card (funnel_diag)

## Campos de Frontmatter (Obrigatórios)
| Campo | Tipo | Obrigatório | Default | Nota |
|---|---|---|---|---|
| id | string (p11_tc_funnel_diag_{{slug}}) | sim | -- | deve casar com o ID Pattern |
| kind | literal "tool_card" | sim | -- | classificação CEXAI |
| pillar | literal "P11" | sim | -- | pilar nativo do tool_card |
| title | string 5-100 caracteres | sim | -- | |
| version | semver X.Y.Z | sim | "1.0.0" | |
| created / updated | data YYYY-MM-DD | sim | -- | |
| author | string | sim | -- | |
| domain | string | sim | -- | modelo de negócio (SaaS, e-commerce, marketplace...) |
| quality | null | sim | null | nunca auto-pontuado -- revisão externa atribui |
| tags | list[string], 3-7 itens | sim | -- | |
| tldr | string <=160 caracteres | sim | -- | deve conter o vazamento principal, não descrição genérica |
| framework | list[string], os 5 estágios | sim | [atrair, engajar, converter, reter, expandir] | ordem fixa |
| prioritization_method | "ICE" ou "RICE" | sim | "ICE" | |
| data_sources | list[string] | sim | -- | cada métrica do corpo deve rastrear a uma entrada aqui |
| biggest_leak | string | sim | -- | qual estágio concentra o maior vazamento |

## Campos Recomendados
| Campo | Tipo | Nota |
|---|---|---|
| fixes_ranked | list[object {fix, impact, effort, score}] | espelha a tabela "Fixes Priorizados" do corpo |
| stages_missing_data | list[string] | estágios sem dado fornecido pelo usuário |
| benchmark_sources | list[string] | quando benchmark público foi usado |

## ID Pattern
Regex: `^p11_tc_[a-z][a-z0-9_]+$`
Regra: id deve ser igual ao nome do arquivo sem extensão. Apenas underscores.

## Estrutura do Corpo
1. `## Mapa do Funil` -- tabela com os 5 estágios + métrica principal + origem
2. `## Métricas por Estágio` -- tabela detalhada: métrica, valor, benchmark, gap
3. `## Análise de Vazamento` -- qual estágio, qual queda percentual, qual perda absoluta
4. `## Fixes Priorizados por ROI` -- tabela ranqueada com fórmula ICE/RICE explícita
5. `## Suposições e Dados a Confirmar` -- toda lacuna listada como `[A CONFIRMAR]`

## Restrições
- max_bytes (corpo): 5120 -- alinhado ao teto padrão CEXAI de tool_card
- min_bytes (corpo): 400 -- um diagnóstico com menos que isso não cobriu os 5 estágios
- Os 5 estágios do `framework` devem aparecer nas seções 1 e 2, mesmo que como lacuna
- Todo número no corpo deve rastrear a uma entrada em `data_sources` ou estar rotulado `[A CONFIRMAR]`/`estimado`
- Nomenclatura de arquivo: `p11_tc_funnel_diag_{{slug}}.md`

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_funnel_diag]] | sibling | 0.52 |
| [[p11_qg_funnel_diag]] | sibling | 0.48 |
| [[bld_config_funnel_diag]] | sibling | 0.40 |
