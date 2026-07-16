---
kind: config
id: bld_config_product_match
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints
pattern: CONFIG restricts SCHEMA, never contradicts it
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Product Match"
version: "1.0.0"
author: n03_builder
tags: [product_match, builder, examples]
tldr: "Golden and anti-examples for product_match construction, demonstrating ideal structure and common pitfalls."
domain: "product match construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, product match construction, config product match, product_match, builder, examples, "p04_pm_{name}.md"]
density_score: 0.90
related:
  - bld_tools_product_match
  - bld_config_vision_tool
---
# Config: product_match Production Rules
## Naming Convention
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | `p04_pm_{name}.md` | `p04_pm_supplier_ml_catalog.md` |
| Builder directory | kebab-case | `product-match-builder/` |
| Frontmatter fields | snake_case | `match_join_keys`, `match_engine`, `match_confidence_floor` |
| Name slug | snake_case, lowercase, no hyphens | `supplier_ml_catalog`, `fornecedor_amazon_audit` |
| Match engine values | snake_case, lowercase, closed enum | `reverse_image`, `embedding`, `manual`, `none` |
| Join key names | snake_case, lowercase | `photo`, `dimension`, `supplier_code`, `code` |
Rule: id MUST equal filename stem. Hyphens in id = HARD FAIL.
## File Paths
- Output: `N03_engineering/P04_tools/examples/p04_pm_{name}.md`
- Compiled: `N03_engineering/P04_tools/compiled/p04_pm_{name}.yaml`
- Real implementation (reference only, NEVER edit from this builder): `_tools/capability_generators/product_match.py`
- Contract mirror (reference only): `apps/dashboard_web/lib/molds.ts` (`MOLD_PRODUCT_MATCH`),
  `apps/dashboard_web/lib/capability_contracts_v1.0.md` section 16
- Runtime wiring (reference only): `_tools/cex_run_capability.py` `_BASE_CAPABILITIES["product_match"]`
## Size Limits (aligned with SCHEMA + kinds_meta.json)
- Body: max 5120 bytes (`.cex/kinds_meta.json` -> product_match.max_bytes)
- Density: >= 0.80 (no filler)
## Match Engine Enum (closed vocab -- product_match.py `_MATCH_ENGINE_ENUM`)
| Value | Default | Implemented today? |
|-------|---------|---------------------|
| none | YES (`_DEFAULT_MATCH_ENGINE`) | N/A -- forces `offline=True` unconditionally |
| reverse_image | no | NOT implemented -- same honest-NAO row as offline, reason text differs only |
| embedding | no | NOT implemented -- same honest-NAO row |
| manual | no | NOT implemented -- same honest-NAO row |
An unrecognized value falls back to `none` with a note; never a silent crash (product_match.py:340-344).
## Join Key Enum
| Value | Item field alias (first non-empty wins) | Notes |
|-------|------------------------------------------|-------|
| photo | photo_uri, photo, image, image_uri | Default member |
| dimension | dimension, dim, size | Default member |
| supplier_code | code, supplier_code, sku | Default member |
| code | code, supplier_code, sku | Same alias set as supplier_code |
## Exclude Key Enum (never enter the join)
`ean` | `gtin` | `barcode` -- default `_DEFAULT_EXCLUDE_KEYS`. A join key that also appears in
`match_exclude_keys` is stripped defensively and logged as a note (product_match.py:372-377);
a spec documents the exclusion as INTENTIONAL, never as a workaround.
## Output Section Names (frozen, order-sensitive)
1. `Resultado do match` (layout: table)
2. `Auditoria de catalogo` (layout: list)
3. `Proveniencia` (layout: fields)
4. `Veredito` (layout: fields)
Reordering, renaming, or re-layouting any of the four is a HARD FAIL against
`capability_contracts_v1.0.md` ("the SHAPE is frozen; only the data is real").

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_product_match]] | upstream | 0.33 |
| [[bld_prompt_product_match]] | upstream | 0.29 |
| [[bld_config_vision_tool]] | sibling | 0.28 |
