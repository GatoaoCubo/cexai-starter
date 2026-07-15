---
kind: architecture
id: bld_architecture_product_match
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of product_match -- inventory, dependencies, and architectural position
quality: null
title: "Architecture Product Match"
version: "1.0.0"
author: n03_builder
tags: [product_match, builder, examples]
tldr: "Golden and anti-examples for product_match construction, demonstrating ideal structure and common pitfalls."
domain: "product match construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords: [component map of product_match, and architectural position, product match construction, architecture product match, product_match, builder, examples, component inventory, dependency graph, boundary table]
density_score: 0.90
related:
  - product-match-builder
  - p11_qg_product_match
  - bld_architecture_vision_tool
  - opportunity-matrix-builder
  - n01_sourcing_rigor
---
## Component Inventory
| Name | Role | Owner | Status |
|------|------|-------|--------|
| items | Supplier item list to match/audit (code, photo_uri, dimension, desc) | product_match | required |
| match_join_keys | Composite non-key join fields | product_match | required |
| match_exclude_keys | Fields NEVER in the join (ean, gtin, barcode) | product_match | internal (not in dashboard mold) |
| match_engine | Backing matcher (reverse_image/embedding/manual/none) | product_match | required |
| match_confidence_floor | Piso a match must clear to count SIM | product_match | required |
| audit_enabled | Toggles the catalog-audit side-effect | product_match | recommended |
| audit_min_photo_px | Low-res threshold for the photo audit | product_match | recommended |
| match_confiavel | Named verdict gate (F7) | product_match | required |
| generator | `_tools/capability_generators/product_match.py` `@register("product_match")` | N03 | implementation |
| mold | `MOLD_PRODUCT_MATCH` (apps/dashboard_web/lib/molds.ts) | N03 | contract mirror |
| consumer (shared helpers) | `sourcing_opportunity.py` (N06) imports `_normalize_join_key` + `_audit_text_vs_photo` | N06 | consumer |
## Dependency Graph
```
items               --feeds-->        match_join_keys
match_join_keys     --composes-->     _normalize_join_key (composite key)
match_exclude_keys  --strips-->       match_join_keys (defensive, logged as note)
match_engine        --selects-->      Resultado do match rows
match_confidence_floor --gates-->     match_confiavel
audit_enabled       --toggles-->      Auditoria de catalogo
audit_min_photo_px  --thresholds-->   _audit_text_vs_photo (low-res flag)
Resultado do match  --feeds-->        Veredito (Cobertura)
Auditoria de catalogo --feeds-->      Veredito (Bloqueadores, no-photo/low-res items)
sourcing_opportunity.py --imports--> _normalize_join_key + _audit_text_vs_photo (N06 reuse)
```
| From | To | Type | Data |
|------|----|------|------|
| items | match_join_keys | feeds | raw item dicts |
| match_join_keys | Resultado do match | composes | composite match key string |
| match_engine | Resultado do match | selects | row reason text ("nao executado" vs "pendente") |
| match_confidence_floor | Veredito | gates | Cobertura ratio + match_confiavel |
| audit_min_photo_px | Auditoria de catalogo | thresholds | low-res flag emission |
| Resultado do match + Auditoria de catalogo | Veredito | feeds | Cobertura + Bloqueadores |
| product_match.py | sourcing_opportunity.py | shared helper | `_normalize_join_key`, `_audit_text_vs_photo` (soft-import, product_match.py:314-330) |
## Boundary Table
| product_match IS | product_match IS NOT |
|-------------------|------------------------|
| A composite NON-key join (photo+dimension+supplier_code) between a supplier item and a marketplace listing | A raw visual-analysis primitive that returns arbitrary image labels (vision_tool) |
| A catalog auditor that runs offline on LOCAL item data (text-vs-photo, low-res, piece-count) | A buy-side cost x demand ranking (opportunity_matrix, sibling capability #15, P11/N06) |
| Degrade-never: offline (match_engine=none or no credential) always returns honest NAO, never a fabricated match | A channel-projection publish-readiness report (marketplace_listing, P05/N06) |
| Spec-only: no reverse-image/embedding implementation code in the .md artifact | A competitor feature battle card (competitive_matrix) |
| Shared-helper source for `sourcing_opportunity.py`'s own visual audit stage | A live reverse-image search -- as implemented, `reverse_image`/`embedding`/`manual` are enum values with NO working code path (product_match.py:396-406 emits the same honest placeholder as `none`) |
## Layer Map
| Layer | Components | Purpose |
|-------|-----------|---------|
| input | items, match_join_keys, match_exclude_keys | Define what is matched and by which composite key |
| processing | match_engine, match_confidence_floor, audit_enabled, audit_min_photo_px | Select engine, gate confidence, run the audit |
| output | Resultado do match, Auditoria de catalogo, Proveniencia, Veredito | 4 frozen sections (MOLD_PRODUCT_MATCH order) |
| governance | match_confiavel gate, score formula (product_match.py:511-522) | F7 GOVERN verdict + score |
| callers | dashboard run (N03, verb=analyze), sourcing_opportunity.py (N06, shared helpers) | Runtime consumers |
## Confusion Zones
| Scenario | Seems Like | Actually Is | Rule |
|---|---|---|---|
| "Analyze this product photo" (no join target) | product_match | vision_tool | vision_tool=analyze one image; product_match=join TWO records via composite key |
| "Rank suppliers by cost vs demand" | product_match | opportunity_matrix | opportunity_matrix=buy-side economics (P11/N06); product_match=record-linkage (P04/N03) |
| "Is this listing ready to publish on Mercado Livre" | product_match | marketplace_listing | marketplace_listing=channel-projection readiness (P05/N06); product_match=match+audit only |
| "Match by EAN/GTIN barcode" | product_match | (unsupported by design) | EAN/GTIN/barcode are structurally EXCLUDED -- every reseller recodes them |
## Decision Tree
- Join a supplier item to a marketplace listing by photo/dimension/code, EAN excluded? -> product_match
- Analyze one image with no join target? -> vision_tool
- Rank buy-side opportunities by cost vs demand? -> opportunity_matrix
- Assess channel publish-readiness of an already-matched listing? -> marketplace_listing
## Neighbor Comparison
| Dimension | product_match | opportunity_matrix | Difference |
|---|---|---|---|
| Pillar | P04 (tools) | P11 (feedback/gate) | Different pillar despite both being "sourcing" (catalog #15/#16) |
| llm_function | CALL | GOVERN | product_match executes a join; opportunity_matrix renders a verdict |
| Nucleus | N03 | N06 | RACI: N03 engineering builds tools; N06 commercial owns pricing/sourcing economics |
| Output shape | table+list+fields+fields (4) | fields+table+table+fields+table+table+fields+fields (8, per capability_contracts_v1.0.md #15) | product_match is the narrower, shared visual-audit primitive |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[product-match-builder]] | upstream | 0.50 |
| [[p11_qg_product_match]] | downstream | 0.44 |
| [[bld_architecture_vision_tool]] | sibling | 0.40 |
| [[opportunity-matrix-builder]] | sibling | 0.36 |
| n01_sourcing_rigor | related | 0.34 |
