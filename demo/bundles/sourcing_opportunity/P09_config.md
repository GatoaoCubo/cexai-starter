---
kind: config
id: bld_config_opportunity_matrix
pillar: P09
llm_function: CONSTRAIN
purpose: Nomenclatura, caminhos, limites para a produção de opportunity_matrix
quality: null
title: "Configuração -- Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, config]
tldr: "Restrições de produção para opportunity matrix: nomenclatura (p11_om_{{name}}.md), caminho de saída P11/, limite de tamanho 5120B. Decisão de sourcing buy-side pontuada de custo-de-fornecedor x demanda-de-mercado."
domain: "construção de opportunity_matrix"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords: [limites para a produção de opportunity_matrix, construção de opportunity_matrix, configuração opportunity matrix, caminhos de saída, limite de tamanho, opportunity_matrix, builder, config, p11_om_name.md]
density_score: 0.85
related:
  - bld_config_roi_calculator
  - bld_config_scoring_rubric
  - bld_config_research_pipeline
  - opportunity-matrix-builder
---
## Convenção de Nomenclatura
Padrão: `p11_om_{{name}}.md`
Exemplos: `p11_om_ferramentas_q3.md`, `p11_om_hardware_catalog_2026.md`

## Caminhos
Artefatos: `N06_commercial/P11_feedback/p11_om_{{name}}.md` (convenção pillar+nucleus; ainda sem instância em disco -- este kind foi registrado recentemente)
Logs: `.cex/runtime/logs/opportunity_matrix/{{name}}/`

## Limites
max_bytes: 5120
max_turns: 10
effort_level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Restrições Específicas de Domínio
| Restrição | Valor |
|-----------|-------|
| Fronteira | Join pontuado de custo-de-fornecedor x demanda-de-mercado para decisões de compra/sourcing (gêmeo inbound de marketplace_listing). NÃO é competitive_matrix nem roi_calculator. |
| Dependências | roi_calculator, research_pipeline, scoring_rubric |
| Função 8F primária | F4_reason |
| Tamanho máximo do artefato | 5120 bytes |
| requires_external_context | true (pesquisa de demanda web) |
| requires_live_tools | false |
| f7_enforce | true |

## Casos de Borda
| Cenário | Tratamento |
|----------|----------|
| Campo de frontmatter obrigatório ausente | Falha o gate H01; retorna para F6 |
| catalog_sources vazio/inválido | Gerador emite matriz vazia + nota "catalog_sources vazio ou invalido"; pontuação -0.3 |
| Sem credencial / sem demand_sources | Caminho offline: toda célula de mercado/demanda honest-null; pontuação -0.25 |
| data_window_days > 365 | Banda de frescor RED; nota "dado muito antigo"; pontuação -0.15 |
| Colisão de ID com artefato existente | Anexa sufixo de versão (_v2) |
| Corpo excede 5120 bytes | Corta seções de prosa; preserva tabelas |

## Propriedades
| Propriedade | Valor |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | construção de opportunity matrix |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_config_roi_calculator]] | sibling | 0.51 |
| [[bld_config_scoring_rubric]] | sibling | 0.44 |
| [[bld_config_research_pipeline]] | sibling | 0.42 |
| p08_adr_opportunity_matrix_kind | upstream | 0.40 |
| [[opportunity-matrix-builder]] | related | 0.38 |
