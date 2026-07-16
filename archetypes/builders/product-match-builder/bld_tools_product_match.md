---
kind: tools
id: bld_tools_product_match
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for product_match production
quality: null
title: "Tools Product Match"
version: "1.0.0"
author: n03_builder
tags: [product_match, builder, examples]
tldr: "Golden and anti-examples for product_match construction, demonstrating ideal structure and common pitfalls."
domain: "product match construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F5_call"
keywords: [product match construction, tools product match, product_match, builder, examples, production tools, data sources, match engine reference, join keys, real implementation]
density_score: 0.90
related:
  - bld_tools_vision_tool
  - bld_tools_output_validator
  - bld_schema_product_match
  - bld_config_product_match
---
# Tools: product-match-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing product_match artifacts in pool | Phase 1 (check duplicates) | CONDITIONAL |
| validate_artifact.py | Generic artifact validator | Phase 3 | [PLANNED] |
| cex_run_capability.py --capability product_match | Exercise the REAL generator against sample items (ground-truth check) | Phase 1/3 | AVAILABLE |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX kind registry | `.cex/kinds_meta.json` (key `product_match`) | pillar, max_bytes, naming, depends_on, primary_8f |
| Real generator (ground truth) | `_tools/capability_generators/product_match.py` | actual `build()` behavior -- fields, sections, gate, score formula |
| Contract mirror | `apps/dashboard_web/lib/capability_contracts_v1.0.md` section 16 | dashboard-facing input/output contract table |
| Mold (frozen shape) | `apps/dashboard_web/lib/molds.ts` (`MOLD_PRODUCT_MATCH`) | example mock rows, `contract_version` |
| Runtime wiring | `_tools/cex_run_capability.py` `_BASE_CAPABILITIES["product_match"]` | nucleus=N03, pillar=P04, verb=analyze |
| Origin ADR | `N06_commercial/P08_architecture/p08_adr_opportunity_matrix_kind.md` | why the kind exists, join-key rationale |
| Domain rigor | `_docs/specs/contract/n01_sourcing_rigor.md`, `n03_schema.md`, `n03_validation.md` | S1-S5 sourcing rigor + type/validation doctrine |
## Match Engine Reference (status as implemented -- see bld_knowledge_product_match.md for the full matrix)
| Engine | Type | Implemented? | Notes |
|--------|------|:---:|-------|
| none | default | N/A (forces offline) | Every row honest-NAO at 0.0 confidence |
| reverse_image | enum value | NO | Would eventually wrap a `vision_tool` primitive (ADR intent); no code path exists |
| embedding | enum value | NO | No vector-similarity call exists |
| manual | enum value | NO | No manual-review queue integration exists |
## Shared Pure Helpers (importable by name -- product_match.py `__all__`)
| Helper | Signature | Consumer |
|--------|-----------|----------|
| `_normalize_join_key` | `(item, join_keys, exclude_keys) -> str` | `sourcing_opportunity.py` (soft-import, product_match.py:314-330) |
| `_audit_text_vs_photo` | `(item, min_photo_px=200) -> Optional[str]` | `sourcing_opportunity.py` (same soft-import block) |
Both are PURE (no I/O), TOTAL (never raise -- degrade-never), and ASCII-safe per the code-rule.
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
No automated validator exists yet for product_match spec artifacts. Manually check each
`p11_qg_product_match.md` gate against the produced artifact. Key checks: YAML parses, id pattern
matches `p04_pm_`, output sections match `MOLD_PRODUCT_MATCH` order+layout, body <= 5120 bytes,
quality == null, match_engine is one of the 4 closed-enum values, EAN/GTIN/barcode never listed
as an active join key.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_vision_tool]] | sibling | 0.49 |
| [[bld_tools_output_validator]] | sibling | 0.46 |
| [[bld_schema_product_match]] | upstream | 0.40 |
| [[bld_config_product_match]] | sibling | 0.38 |
| n01_sourcing_rigor | related | 0.33 |
