---
kind: instruction
id: bld_instruction_product_match
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for product_match
pattern: 3-phase pipeline (research -> compose -> validate)
quality: null
title: "Instruction Product Match"
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
  - "product match construction"
  - "instruction product match"
  - "product_match"
  - "builder"
  - "examples"
  - "{{vars}}"
  - "^p04_pm_[a-z][a-z0-9_]+$"
  - "p04_pm_"
  - "reverse image match"
  - "catalog audit"
density_score: 0.90
related:
  - bld_instruction_vision_tool
  - bld_instruction_output_validator
  - bld_instruction_data_contract
  - bld_schema_product_match
  - bld_output_template_product_match
---
# Instructions: How to Produce a product_match
## Phase 1: RESEARCH
1. Identify the record-linkage task: which supplier catalog joins to which marketplace listing set
2. Read `_tools/capability_generators/product_match.py` `build()` end-to-end -- the generator IS
   the ground truth; a spec that contradicts it is wrong by definition
3. Confirm the 6 dashboard-exposed input fields against `MOLD_PRODUCT_MATCH.input_contract`
   (apps/dashboard_web/lib/molds.ts): items, match_join_keys, match_engine,
   match_confidence_floor, audit_enabled, audit_min_photo_px
4. Note the internal-only `match_exclude_keys` override (read by the generator, absent from the
   dashboard mold) -- default `[ean, gtin, barcode]`
5. Confirm the 4 output sections + frozen order/layout against `MOLD_PRODUCT_MATCH.output_sections`
6. Check the match_engine implementation status (bld_knowledge_product_match.md) -- do NOT
   describe an enum value as functional unless the code proves it
7. Check for existing product_match artifacts to avoid duplicates (`p04_pm_*.md`)
8. Confirm capability slug for id: snake_case, lowercase, no hyphens
## Phase 2: COMPOSE
1. Read `bld_schema_product_match.md` -- source of truth for all fields
2. Read `bld_output_product_match.md` -- fill `{{vars}}` following SCHEMA constraints
3. Fill frontmatter: all required fields (quality: null -- never self-score)
4. Write Overview section: what is matched/audited, who consumes the output (dashboard run,
   `sourcing_opportunity.py`), offline-first framing
5. Write Input Contract section: all 6 dashboard fields + the internal `match_exclude_keys`
   override, each with type/required/default exactly as in `MOLD_PRODUCT_MATCH`
6. Write Output Sections: Resultado do match (table), Auditoria de catalogo (list), Proveniencia
   (fields), Veredito (fields) -- in this exact order, with the exact declared columns/keys
7. Write Gate section: the named gate `match_confiavel` + its blocker vocabulary (missing public
   photo URL, low-res photo, match_engine still `none`)
8. Verify body <= 5120 bytes
9. Verify id matches `^p04_pm_[a-z][a-z0-9_]+$`
## Phase 3: VALIDATE
1. Check `p11_qg_product_match.md` -- verify each HARD gate manually
2. Confirm YAML frontmatter parses without errors
3. Confirm id matches `p04_pm_` prefix
4. Confirm kind == product_match
5. Confirm the 4 output sections match `MOLD_PRODUCT_MATCH` order, layout, and columns exactly
6. Confirm match_engine is one of the 4 closed-enum values (reverse_image, embedding, manual, none)
7. Confirm EAN/GTIN/barcode are documented as EXCLUDED, never as an active join key
8. Confirm the offline honest-null rule is stated: match_engine=none or no credential -> every
   match row is NAO at 0.0, never fabricated
9. Cross-check boundary: record-linkage + catalog audit only (not vision_tool, not
   opportunity_matrix, not marketplace_listing)?
10. Revise if score < 8.0 before outputting

## ISO Loading

```yaml
loader: cex_skill_loader
injection_point: F3_compose
priority: high
```

```bash
python _tools/cex_skill_loader.py --verify product_match
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `instruction` |
| Pillar | P03 |
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
| [[bld_instruction_vision_tool]] | sibling | 0.49 |
| [[bld_instruction_output_validator]] | sibling | 0.47 |
| [[bld_instruction_data_contract]] | sibling | 0.45 |
| [[bld_schema_product_match]] | upstream | 0.40 |
| [[bld_output_template_product_match]] | downstream | 0.38 |
