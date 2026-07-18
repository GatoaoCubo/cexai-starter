---
kind: output_template
id: bld_output_template_competitive_matrix
pillar: P05
llm_function: PRODUCE
purpose: Template com variáveis para produção de competitive_matrix
quality: null
title: "Output Template Competitive Matrix"
version: "1.1.0"
author: wave1_builder_gen_v2
tags: [competitive_matrix, builder, output_template]
tldr: "Template de feature-parity grid + battle card + posicionamento Gartner MQ para matriz competitiva"
domain: "construção de competitive_matrix"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [competitive_matrix construction, output template competitive matrix, feature-parity grid, battle card, competitive_matrix, builder, output_template, competitive matrix, market context, analysis date]
density_score: 0.85
related:
  - bld_schema_competitive_matrix
---
```yaml
---
id: p01_cm_{{slug}}.md
kind: competitive_matrix
pillar: P01
title: "Matriz Competitiva de {{market_segment}}"
version: "1.0.0"
author: "{{analyst_name}}"
domain: "{{market_domain}}"
quality: null
tags: [{{market_tag}}, competitive_matrix, battle_card]
tldr: "{{our_product}} vs {{competitor_count}} concorrentes em {{dimension_count}} dimensões"
competitors: [{{competitor_1}}, {{competitor_2}}, {{competitor_3}}]
metrics: [{{metric_1}}, {{metric_2}}, {{metric_3}}]
analysis_date: "{{AAAA-MM-DD}}"
key_insights: "{{top_differentiator_one_sentence}}"
---
```

## Contexto de Mercado
| Campo | Valor |
|-------|-------|
| Segmento | `{{market_segment}}` |
| Data da Análise | {{AAAA-MM-DD}} |
| Fontes de Dados | `{{source_list}}` |
| Analista | `{{analyst_name}}` |

## Feature Parity Grid
<!-- Linhas = capacidades, Colunas = nos + concorrentes. Usar: Sim / Não / Parcial / Roadmap -->

| Capacidade | `{{our_product}}` | `{{competitor_1}}` | `{{competitor_2}}` | `{{competitor_3}}` | Notas |
|------------|-----------------|------------------|------------------|------------------|-------|
| `{{feature_1}}` | `{{val}}` | `{{val}}` | `{{val}}` | `{{val}}` | `{{note}}` |
| `{{feature_2}}` | `{{val}}` | `{{val}}` | `{{val}}` | `{{val}}` | `{{note}}` |
| `{{feature_3}}` | `{{val}}` | `{{val}}` | `{{val}}` | `{{val}}` | `{{note}}` |

<!-- feature_n: capacidade específica, não categoria vaga -->
<!-- val: Sim / Não / Parcial / Roadmap (Q`{{quarter}}` `{{year}}`) -->

## Posicionamento Gartner MQ (Qualitativo)
<!-- Completude de Visão x Capacidade de Execução conforme a metodologia Gartner MQ -->

| Fornecedor | Capacidade de Execução (1-5) | Completude de Visão (1-5) | Quadrante |
|--------|--------------------------|------------------------------|----------|
| `{{our_product}}` | `{{score}}` | `{{score}}` | {{Leaders/Challengers/Visionaries/Niche}} |
| `{{competitor_1}}` | `{{score}}` | `{{score}}` | `{{quadrant}}` |
| `{{competitor_2}}` | `{{score}}` | `{{score}}` | `{{quadrant}}` |

## Battle Card: Nos vs `{{primary_competitor}}`
<!-- Pronto para vendas, comparação um concorrente de cada vez -->

| Dimensão | `{{our_product}}` | `{{primary_competitor}}` | Razão de Vitória |
|-----------|-----------------|------------------------|------------|
| `{{capability_1}}` | `{{our_strength}}` | `{{their_weakness}}` | `{{why_we_win}}` |
| `{{capability_2}}` | `{{our_strength}}` | `{{their_weakness}}` | `{{why_we_win}}` |
| Precificação | `{{our_pricing}}` | `{{their_pricing}}` | `{{pricing_rationale}}` |
| Suporte | `{{our_support}}` | `{{their_support}}` | `{{support_rationale}}` |
| Integrações | `{{our_count}}`+ | `{{their_count}}`+ | `{{integration_rationale}}` |

**Objeção provável deles:** "`{{competitor_objection}}`"
**Nosso contra-argumento:** "`{{objection_counter}}`"

## Comparação de Preços
| Fornecedor | Camada de Entrada | Camada Intermediária | Enterprise | Modelo de Precificação |
|--------|-----------|----------|------------|---------------|
| `{{our_product}}` | `{{price}}` | `{{price}}` | `{{price}}` | {{per_user/flat/usage}} |
| `{{competitor_1}}` | `{{price}}` | `{{price}}` | `{{price}}` | `{{model}}` |
| `{{competitor_2}}` | `{{price}}` | `{{price}}` | `{{price}}` | `{{model}}` |

## Insights Estratégicos
**Nossos principais diferenciais:**
1. `{{differentiator_1}}` -- vs `{{competitor_benefiting_from}}`
2. `{{differentiator_2}}` -- vs `{{competitor_benefiting_from}}`
3. `{{differentiator_3}}` -- vs `{{competitor_benefiting_from}}`

**Lacunas a tratar:**
- `{{gap_1}}` (`{{competitor_leading_here}}` lidera aqui)
- `{{gap_2}}` (`{{competitor_leading_here}}` lidera aqui)

**Guia Anti-FUD:**
<!-- Respostas factuais a alegações FUD comuns de concorrentes -->
- Se o prospect disser "`{{competitor_fud_claim}}`": responda com "`{{factual_response_with_source}}`"

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_schema_competitive_matrix]] | downstream | 0.35 |
| [[bld_knowledge_competitive_matrix]] | upstream | 0.28 |
| p08_pat_pricing_framework | downstream | 0.26 |
| p01_kc_supabase_api | upstream | 0.23 |
