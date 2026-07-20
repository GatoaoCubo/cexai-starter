---
id: kc_opportunity_matrix
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P01
title: "Opportunity Matrix -- Deep Knowledge for opportunity_matrix"
version: 1.0.0
created: 2026-07-20
updated: 2026-07-20
author: n03_builder
domain: opportunity_matrix
quality: null
tags: [opportunity_matrix, P11, GOVERN, kind-kc, sourcing, buy-side, procurement, ranking]
tldr: "Scored/ranked join of supplier cost vs market price+demand for buy-side sourcing decisions; the inbound twin of marketplace_listing, sharing the canonical_product seam and the product_match identity resolver."
when_to_use: "When ranking a supplier catalog's cost rows against market price and demand to decide what to buy, or when gating a sourcing decision behind a named go/no-go verdict."
keywords: [opportunity matrix, sourcing, buy-side, take rate, opp score, sourcing confiavel, offline deterministic, cost vs demand]
density_score: null
related:
  - opportunity-matrix-builder
  - bld_schema_opportunity_matrix
  - kc_roi_calculator
  - p01_kc_research_pipeline
  - p01_kc_scoring_rubric
---

# Opportunity Matrix

## Definition
An `opportunity_matrix` quantifies a buy-side sourcing decision by crossing supplier cost (the OFFER side, parsed from tenant catalogs) against market price and demand per product type, then ranks the result. Registered `pillar: P11`, owning `nucleus: N06`, `llm_function: GOVERN`, `primary_8f: F4_reason`, `f7_enforce: true`, `depends_on: [roi_calculator, research_pipeline, scoring_rubric]`, `requires_external_context: true` (`.cex/kinds_meta.json`). The real generator (`_tools/capability_generators/sourcing_opportunity.py`, capability slug `sourcing_opportunity`) is offline-deterministic: it never calls a network or an LLM, and degrades to honest-null cells rather than fabricating market data when no credential or `demand_sources` is supplied.

## Boundaries
**What it is:** the inbound (buy-side) twin of `marketplace_listing` (the outbound/channel-projection kind) -- both share exactly one seam, the `canonical_product` record, and both reuse `product_match` for identity resolution.

**What it is NOT:**
- NOT `competitive_matrix` -- a competitor FEATURE battle card, not a cost x demand join.
- NOT `roi_calculator` -- single-row margin math; `opportunity_matrix` COMPOSES `roi_calculator` across a ranked, multi-row catalog rather than duplicating it.
- NOT a live market-research call -- offline-deterministic by design; live demand data requires an explicit credential plus `demand_sources`.

## Naming Convention
| Property | Value |
|---|---|
| Naming pattern | `p11_om_{{name}}.md` |
| ID regex (bld_schema) | `^p11_om_[a-z][a-z0-9_]+$` |
| max_bytes | 5120 (body) |
| region | default `Global` -- the demand market cut |

## Key Fields
| Field | Type | Required | Notes |
|---|---|---|---|
| cost_source_strategy | enum | YES | one of `column\|filename\|fixed\|formula\|none` |
| demand_signal_basis | enum | YES | one of `reviews\|price_scrape\|sales_rank\|spec_sheet\|manual` |
| verify_top_n | int | REC | skeptical re-check count, default 10 -- treats web price as a CEILING, never a floor |
| fee_model / freight_model | string | REC | combine into the take-rate; `net_margin = sell - cost - fee - freight` |
| opp_score | computed | -- | weighted rank: 0.4 margin + 0.3 demand + 0.2 stock + 0.1 confidence (default weights, overridable) |

8 FROZEN body sections (exact order): Resumo executivo -> Matriz de oportunidade (9-col table) -> Leitura por categoria -> Cobertura -> Verificacao top-N -> Match/auditoria -> Proveniencia -> Veredito + proximos passos (the named gate).

## When to Use
- When a supplier catalog (CSV/XLSX/PDF/image) needs ranking against market demand before a purchasing decision.
- When a passing `sourcing_confiavel` gate is the prerequisite to chain forward into a [[kc_marketplace_listing]] publish step.
- Never for a single-item margin check alone -- use [[kc_roi_calculator]] directly for that narrower case.

## Related Kinds
- [[kc_roi_calculator]] -- the per-item margin primitive this kind composes across a ranked catalog, never duplicates.
- [[p01_kc_research_pipeline]] -- supplies the demand-side research this kind joins against cost.
- [[p01_kc_scoring_rubric]] -- supplies the ranking criteria behind `opp_score`.
- `product_match` -- the shared visual matcher surfaced in the Match/auditoria section; this kind only displays that engine's result, never implements it.
- [[kc_marketplace_listing]] -- the outbound twin; a passing gate here is the natural upstream of a channel listing there.

Named gate `sourcing_confiavel`: `margem_bruta_top >= 25% AND top-N verificado AND nenhum item critico sem preco AND frescor != RED`. EAN/GTIN/barcode are NEVER a valid join key -- every reseller re-barcodes white-label products; the join key is always a normalized `product_type`.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[opportunity-matrix-builder]] | downstream (builder identity) | 0.55 |
| [[bld_schema_opportunity_matrix]] | downstream (schema, source of truth) | 0.52 |
| [[kc_roi_calculator]] | upstream (depends_on) | 0.44 |
| [[p01_kc_research_pipeline]] | upstream (depends_on) | 0.40 |
| [[p01_kc_scoring_rubric]] | upstream (depends_on) | 0.38 |
