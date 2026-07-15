---
kind: output_template
id: bld_output_template_product_match
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce a product_match artifact
pattern: every field here exists in SCHEMA.md -- template derives, never invents
quality: null
title: "Output Template Product Match"
version: "1.0.0"
author: n03_builder
tags:
  - "product_match"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for product_match construction, demonstrating ideal structure and common pitfalls."
domain: "product match construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F6_produce"
keywords:
  - "template with"
  - "product match construction"
  - "output template product match"
  - "product_match"
  - "builder"
  - "examples"
  - "## overview"
  - "## input contract ###"
  - "## output sections ###"
  - "confianca filtrada em:"
density_score: 0.90
related:
  - bld_schema_product_match
  - bld_instruction_product_match
  - bld_output_template_vision_tool
  - p11_qg_product_match
  - bld_output_template_output_validator
---
# Output Template: product_match
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
### `items` (required)
`object[]` -- `{{shape_description_e.g._code_photo_uri_dimension_desc}}`
### `match_join_keys`
`{{default_photo_dimension_supplier_code_and_why}}`
### `match_exclude_keys` (internal override, not in the dashboard mold)
`{{default_ean_gtin_barcode_and_reseller_recoding_rationale}}`
### `match_engine`
`{{closed_enum_choice_and_current_implementation_status}}`
### `match_confidence_floor`
`{{default_0.7_and_role_in_SIM_PARCIAL_NAO_split}}`
### `audit_enabled` / `audit_min_photo_px`
`{{defaults_true_200_and_what_the_audit_flags}}`
## Output Sections
### `Resultado do match` (table)
Columns: `{{Codigo, Match?, Fonte casada, Confianca}}`. Confianca filtrada em:
`{{match_confidence_floor}}`.
### `Auditoria de catalogo` (list)
`{{cadastral_and_photo_divergence_flags_local_data_only}}`
### `Proveniencia` (fields)
`{{Motor de match, Chave de casamento, Fontes consultadas, Status por fonte, Honest-null offline}}`
### `Veredito` (fields)
`{{match_confiavel_gate}}`, `{{Cobertura}}`, `{{Bloqueadores}}`

## Template Standards

1. Define all required sections for this output kind
2. Include frontmatter schema with mandatory fields
3. Provide structural markers for post-validation
4. Specify format constraints for markdown YAML JSON
5. Reference the validation_schema for automated checks

## Properties

| Property | Value |
|----------|-------|
| Kind | `output_template` |
| Pillar | P05 |
| Domain | product match construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_product_match]] | downstream | 0.38 |
| [[bld_instruction_product_match]] | upstream | 0.35 |
| [[bld_output_template_vision_tool]] | sibling | 0.33 |
| [[p11_qg_product_match]] | downstream | 0.33 |
| [[bld_output_template_output_validator]] | sibling | 0.31 |
