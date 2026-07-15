---
kind: schema
id: bld_schema_opportunity_matrix
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for opportunity_matrix
quality: null
title: "Schema Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, schema]
tldr: "Formal schema -- SINGLE SOURCE OF TRUTH for opportunity_matrix"
domain: "opportunity_matrix construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords: [opportunity_matrix construction, schema opportunity matrix, opportunity_matrix, builder, schema, frontmatter fields, body structure, input contract, output sections, sourcing_confiavel]
density_score: 0.85
related:
  - bld_output_template_opportunity_matrix
  - bld_instruction_opportunity_matrix
  - roi-calculator-builder
  - research-pipeline-builder
  - scoring-rubric-builder
---
## Frontmatter Fields
### Required
| Field | Type | Required | Default | Notes |
|------|------|----------|---------|-------|
| id | string | yes | null | Must match ID Pattern |
| kind | string | yes | "opportunity_matrix" | CEX kind identifier |
| pillar | string | yes | "P11" | Pillar classification |
| title | string | yes | null | Descriptive title |
| version | string | yes | "1.0.0" | Semantic versioning |
| created | datetime | yes | null | ISO 8601 format |
| updated | datetime | yes | null | ISO 8601 format |
| author | string | yes | null | Responsible party |
| domain | string | yes | "sourcing" | Domain context |
| quality | null | yes | null | Never self-score; peer review assigns |
| tags | list | yes | [] | Keyword metadata |
| tldr | string | yes | null | Summary of purpose |
| region | string | yes | "Global" | Demand market cut |
| cost_source_strategy | string | yes | "column" | One of column\|filename\|fixed\|formula\|none |
| demand_signal_basis | string | yes | "reviews" | One of reviews\|price_scrape\|sales_rank\|spec_sheet\|manual |

### Recommended
| Field | Type | Notes |
|------|------|-------|
| verify_top_n | int | Skeptical re-check count (default 10) |
| show_net_margin | boolean | Opt-in LIQUIDA display (default false) |
| fee_model | string | percent\|fixed_plus_percent\|fixed_per_unit\|tiered (default percent) |
| freight_model | string | none\|flat\|weight\|cubic (default none) |
| last_reviewed | datetime | Peer review timestamp |
| reviewers | list | Reviewer identifiers |

## ID Pattern
^p11_om_[a-z][a-z0-9_]+$

## Body Structure (8 sections, frozen order + layout -- MOLD_SOURCING_OPPORTUNITY)
1. **Resumo executivo** (fields) -- melhores apostas, volume play, margem bruta media, split por relevancia, alerta de dado critico
2. **Matriz de oportunidade** (table, 9 cols) -- `#, Produto, Fornecedor (desc%), Custo, Preco mercado, Margem, Demanda, Relevancia, Score`
3. **Leitura por categoria** (table, 5 cols) -- `Categoria, Itens, Custo, Preco verif., Veredito`
4. **Cobertura** (fields) -- tipos parseados/cruzados, cauda-longa nao coberta, itens sem preco verificado
5. **Verificacao (top-N)** (table, 5 cols) -- `Produto, Preco estimado, Preco real (verif.), Fontes, Confianca`
6. **Match / auditoria** (table, 4 cols) -- `Codigo, Match?, Confianca, Flag de auditoria`
7. **Proveniencia** (fields) -- fontes consultadas/sem dado, status por fonte, banda de frescor, take-rate usado
8. **Veredito + proximos passos** (fields) -- gate `sourcing_confiavel`, condicoes, avaliacao, acoes ranqueadas, proximo passo

## Constraints
- ID must match exact regex pattern; naming `p11_om_{{name}}.md` (per `.cex/kinds_meta.json`)
- All required fields must be present; body under 5120 bytes (`max_bytes`)
- Table row cell count MUST equal its section's column count (no-drift rule, `_base.py table_section`)
- `depends_on`: roi_calculator (per-item margin primitive), research_pipeline (demand research), scoring_rubric (rank criteria) -- per `.cex/kinds_meta.json`
- `requires_external_context: true` (web demand research); `requires_live_tools: false`; `primary_8f: F4_reason`
- Join key is normalized `product_type`; EAN/GTIN/barcode are NEVER a join key (source: generator `_DEFAULT_MATCH_EXCLUDE_KEYS`)
- Quality field must be peer-reviewed; versioning must follow semantic format

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_opportunity_matrix]] | sibling | 0.55 |
| [[bld_prompt_opportunity_matrix]] | sibling | 0.50 |
| [[roi-calculator-builder]] | related | 0.40 |
| [[research-pipeline-builder]] | related | 0.38 |
| [[scoring-rubric-builder]] | related | 0.36 |
