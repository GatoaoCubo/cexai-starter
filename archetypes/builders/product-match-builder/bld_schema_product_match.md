---
kind: schema
id: bld_schema_product_match
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for product_match
pattern: TEMPLATE derives from this. CONFIG restricts this.
quality: null
title: "Schema Product Match"
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
8f: "F1_constrain"
keywords:
  - "formal schema"
  - "product match construction"
  - "schema product match"
  - "product_match"
  - "builder"
  - "examples"
  - "^p04_pm_[a-z][a-z0-9_]+$"
  - "## overview"
  - "## input contract"
  - "## output sections"
density_score: 0.90
related:
  - bld_schema_vision_tool
  - bld_schema_data_contract
  - bld_schema_output_validator
  - bld_config_product_match
  - bld_output_template_product_match
---

# Schema: product_match
## Frontmatter Fields
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p04_pm_{name}) | YES | - | Namespace compliance |
| kind | literal "product_match" | YES | - | Type integrity |
| pillar | literal "P04" | YES | - | Pillar assignment (kinds_meta.json) |
| version | semver string | YES | "1.0.0" | Artifact versioning |
| created | date YYYY-MM-DD | YES | - | Creation date |
| updated | date YYYY-MM-DD | YES | - | Last update |
| author | string | YES | - | Producer identity |
| name | string | YES | - | Human-readable spec name |
| contract_version | string | YES | "1.0" | Mirrors `MOLD_PRODUCT_MATCH.contract_version` (molds.ts) |
| match_join_keys | list[string] | REC | [photo, dimension, supplier_code] | Composite non-key join fields |
| match_exclude_keys | list[string] | REC | [ean, gtin, barcode] | Never enter the join (every reseller recodes them) |
| match_engine | enum: reverse_image, embedding, manual, none | REC | none | Closed vocab -- `_MATCH_ENGINE_ENUM` in product_match.py |
| match_confidence_floor | float 0.0-1.0 | REC | 0.7 | Piso a match must clear to count as SIM |
| audit_enabled | boolean | REC | true | Toggles the catalog-audit side-effect |
| audit_min_photo_px | integer | REC | 200 | Below this, a photo is flagged low-res |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | - | Must include "product_match" |
| tldr | string <= 160ch | YES | - | Dense summary |
| description | string <= 200ch | REC | - | What the spec matches/audits |
## ID Pattern
Regex: `^p04_pm_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem. Source: `.cex/kinds_meta.json` naming `p04_pm_{{name}}.md`.
## Body Structure (required sections)
1. `## Overview` -- what is matched/audited, who consumes the output, offline-first framing
2. `## Input Contract` -- the 6 dashboard-exposed fields (items, match_join_keys, match_engine,
   match_confidence_floor, audit_enabled, audit_min_photo_px) + the internal-only
   `match_exclude_keys` override (read by the generator, absent from `MOLD_PRODUCT_MATCH`)
3. `## Output Sections` -- the 4 frozen sections in order: Resultado do match (table),
   Auditoria de catalogo (list), Proveniencia (fields), Veredito (fields)
4. `## Gate` -- the named gate `match_confiavel` + its blocker vocabulary
## Constraints
- max_bytes: 5120 (body only -- `.cex/kinds_meta.json` max_bytes for product_match)
- naming: p04_pm_{name}.md
- machine_format: yaml (compiled artifact via cex_compile.py)
- id == filename stem
- output section order+layout is FROZEN to `MOLD_PRODUCT_MATCH` (apps/dashboard_web/lib/molds.ts)
  -- a spec MUST NOT reorder, rename, or re-layout a section (StructuredResultView is frozen to
  fields|table|list; see `capability_contracts_v1.0.md` "How to build to this contract")
- match_join_keys MUST never silently admit an excluded key -- product_match.py:372-377 strips any
  leaked exclude-key defensively and logs a note; a spec documents the same exclusion, not a
  workaround
- quality: null always
- NO implementation code in body -- spec only (the real implementation lives in
  `_tools/capability_generators/product_match.py`, owned by N03 engineering, not by this kind's
  spec artifacts)
- depends_on (kinds_meta.json, DECLARED taxonomy dependency, NOT a Python import):
  `vision_tool`, `data_contract`, `output_validator` -- verified via grep that
  `product_match.py` imports NEITHER a vision_tool module (none exists in
  `_tools/capability_generators/`) NOR any schema/validator module; the dependency is
  compositional (a full spec cites the vision primitive its `match_engine` would eventually
  call, the data contract for `items`, and the output validator for the 4 sections), not a
  runtime `import`.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_vision_tool]] | sibling | 0.55 |
| [[bld_schema_data_contract]] | upstream | 0.40 |
| [[bld_schema_output_validator]] | upstream | 0.38 |
| [[bld_config_product_match]] | downstream | 0.35 |
| [[bld_output_template_product_match]] | downstream | 0.35 |
