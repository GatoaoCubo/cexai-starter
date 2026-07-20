---
id: kc_product_match
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P01
title: "Product Match -- Deep Knowledge for product_match"
version: 1.0.0
created: 2026-07-20
updated: 2026-07-20
author: n03_builder
domain: product_match
quality: null
tags: [product_match, P04, CALL, kind-kc, record-linkage, catalog-audit, entity-resolution, sourcing]
tldr: "Visual record-linkage by composite non-key (photo+dimension+supplier-code, EAN excluded) that doubles as an offline catalog auditor; the shared identity resolver behind both buy-side sourcing and outbound listing merge."
when_to_use: "Before trusting a supplier-item-to-listing match, or before publishing a catalog row whose photo/text cadastral consistency has not been audited."
keywords: [product match, record linkage, entity resolution, catalog audit, ean exclusion, composite join key, match confiavel, offline deterministic]
density_score: null
related:
  - product-match-builder
  - bld_schema_product_match
  - p01_kc_vision_tool
  - p01_kc_data_contract
  - p01_kc_output_validator
---

# Product Match

## Definition
A `product_match` joins a supplier item to a marketplace listing by a composite NON-key (photo + dimension + supplier_code) -- entity resolution / record-linkage in industry terms -- with EAN/GTIN/barcode deliberately EXCLUDED, because every reseller re-codes them (the hard-won rule behind [[p08_adr_opportunity_matrix_kind]]). Registered `pillar: P04`, owning `nucleus: N03`, `llm_function: CALL`, `primary_8f: F4_reason` (notably F4, not F5, despite the CALL function -- `.cex/kinds_meta.json`), `depends_on: [vision_tool, data_contract, output_validator]`, `requires_external_context: true`. It doubles as a catalog auditor: even fully offline, it flags text-vs-photo cadastral divergence and low-res/missing photos on LOCAL item data, zero network calls required. It is the shared matcher behind both the buy-side `opportunity_matrix` audit step and the outbound canonical-product merge.

## Boundaries
**What it is:** a two-record JOIN (supplier item x marketplace listing) plus a local catalog audit.

**What it is NOT:**
- NOT `vision_tool` -- the raw visual-analysis primitive `product_match`'s `match_engine` would eventually wrap; `vision_tool` analyzes ONE image with no join target.
- NOT `competitive_matrix` -- a competitor comparison document, unrelated to record-linkage.
- NOT `opportunity_matrix` -- that kind RANKS buy-side cost x demand (P11/N06); `product_match` (P04/N03) only resolves identity and audits, sharing only the Match/auditoria section contract.

**Honest engine status (verify before citing "reverse_image" as functional):** the closed `match_engine` enum has 4 values (`none` default, `reverse_image`, `embedding`, `manual`) but only `none` is actually implemented -- every branch, engine or no engine, currently returns an honest NAO at 0.0 confidence (degrade-never, never a fabricated match). `matched_count` is therefore always 0 by construction, so the `match_confiavel` gate cannot currently pass. Only the catalog-audit side is currently functional.

## Naming Convention
| Property | Value |
|---|---|
| Naming pattern | `p04_pm_{{name}}.md`; id equals filename stem |
| ID regex (bld_schema) | `^p04_pm_[a-z][a-z0-9_]+$` |
| max_bytes | 5120 (body) |
| RUN_MODE | offline-deterministic |

## Key Fields
| Field | Type | Default | Notes |
|---|---|---|---|
| match_join_keys | list[string] | `[photo, dimension, supplier_code]` | composite non-key join fields |
| match_exclude_keys | list[string] | `[ean, gtin, barcode]` | structurally stripped even if leaked into match_join_keys |
| match_engine | enum | `none` | `reverse_image\|embedding\|manual\|none` -- closed vocabulary |
| match_confidence_floor | float 0.0-1.0 | 0.7 | floor a match row must clear to count as SIM |
| audit_min_photo_px | integer | 200 | below this, a photo is flagged low-res |

4 FROZEN output sections (exact order): Resultado do match (table) -> Auditoria de catalogo (list) -> Proveniencia (fields) -> Veredito (fields, named gate `match_confiavel`).

## When to Use
- Before cross-marketplace deduplication or a buy-side match audit -- never use EAN/GTIN/barcode as the join key.
- To surface catalog data-quality issues (photo/text mismatch, low-res photos) even with zero live match engine.
- As the identity-resolution step feeding into [[p08_adr_opportunity_matrix_kind]]-style sourcing decisions or an outbound canonical-product merge.

## Related Kinds
- [[p01_kc_vision_tool]] -- the raw visual primitive a future `match_engine` implementation would call; not yet wired.
- [[p01_kc_data_contract]] / [[p01_kc_output_validator]] -- the other two `depends_on` kinds: the shape of `items` input and the 4-section output check, respectively.
- `opportunity_matrix` -- consumes this kind's result inside its own Match/auditoria section without re-implementing it.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[product-match-builder]] | downstream (builder identity) | 0.55 |
| [[bld_schema_product_match]] | downstream (schema, source of truth) | 0.52 |
| [[p01_kc_vision_tool]] | upstream (depends_on) | 0.44 |
| [[p01_kc_data_contract]] | upstream (depends_on) | 0.38 |
| [[p01_kc_output_validator]] | upstream (depends_on) | 0.36 |
