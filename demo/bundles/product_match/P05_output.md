---
kind: output_template
id: bld_output_template_product_match
pillar: P05
llm_function: PRODUCE
purpose: Modelo com {{vars}} que o LLM preenche para produzir um artefato product_match
pattern: todo campo aqui existe no SCHEMA.md -- o modelo deriva, nunca inventa
quality: null
title: "Modelo de Saída -- Product Match"
version: "1.0.0"
author: n03_builder
tags:
  - "product_match"
  - "builder"
  - "examples"
tldr: "Exemplos ideais (golden) e anti-exemplos para a construção de product_match, demonstrando a estrutura ideal e as armadilhas comuns."
domain: "construção de product_match"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F6_produce"
keywords:
  - "modelo com"
  - "construção de product_match"
  - "modelo de saída product match"
  - "product_match"
  - "builder"
  - "examples"
  - "## overview"
  - "## input contract ###"
  - "## output sections ###"
  - "confiança filtrada em:"
density_score: 0.90
related:
  - bld_schema_product_match
---
# Modelo de Saída: product_match
```yaml
id: p04_pm_{{name_slug}}
kind: product_match
pillar: P04
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"
name: "{{human_readable_spec_name}}"
contract_version: "{{1.0}}"
match_join_keys:
  - {{photo|dimension|supplier_code|code}}
  - {{photo|dimension|supplier_code|code}}
match_exclude_keys:
  - {{ean|gtin|barcode}}
match_engine: {{reverse_image|embedding|manual|none}}
match_confidence_floor: {{0.0_to_1.0_default_0.7}}
audit_enabled: {{true|false}}
audit_min_photo_px: {{integer_default_200}}
quality: null
tags: [product_match, {{tag_2}}, {{tag_3}}]
tldr: "{{dense_summary_max_160ch}}"
description: "{{what_is_matched_and_audited_max_200ch}}"
```
## Overview
`{{what_supplier_x_listing_join_this_spec_covers_1_to_2_sentences}}`
`{{who_consumes_it_dashboard_run_and_or_sourcing_opportunity}}`
## Input Contract
### `items` (obrigatório)
`object[]` -- `{{shape_description_e.g._code_photo_uri_dimension_desc}}`
### `match_join_keys`
`{{default_photo_dimension_supplier_code_and_why}}`
### `match_exclude_keys` (override interno, ausente do mold do dashboard)
`{{default_ean_gtin_barcode_and_reseller_recoding_rationale}}`
### `match_engine`
`{{closed_enum_choice_and_current_implementation_status}}`
### `match_confidence_floor`
`{{default_0.7_and_role_in_SIM_PARCIAL_NAO_split}}`
### `audit_enabled` / `audit_min_photo_px`
`{{defaults_true_200_and_what_the_audit_flags}}`
## Output Sections
### `Resultado do match` (table)
Colunas: `{{Codigo, Match?, Fonte casada, Confianca}}`. Confiança filtrada em:
`{{match_confidence_floor}}`.
### `Auditoria de catalogo` (list)
`{{cadastral_and_photo_divergence_flags_local_data_only}}`
### `Proveniencia` (fields)
`{{Motor de match, Chave de casamento, Fontes consultadas, Status por fonte, Honest-null offline}}`
### `Veredito` (fields)
`{{match_confiavel_gate}}`, `{{Cobertura}}`, `{{Bloqueadores}}`

## Padrões do Modelo

1. Defina todas as seções obrigatórias para este kind de saída
2. Inclua o schema de frontmatter com os campos obrigatórios
3. Forneça marcadores estruturais para pós-validação
4. Especifique restrições de formato para markdown, YAML e JSON
5. Referencie o validation_schema para checagens automatizadas

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `output_template` |
| Pillar | P05 |
| Domain | construção de product_match |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_schema_product_match]] | downstream | 0.38 |
| [[bld_prompt_product_match]] | upstream | 0.35 |
