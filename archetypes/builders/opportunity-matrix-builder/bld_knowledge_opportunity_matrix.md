---
kind: knowledge_card
id: bld_knowledge_card_opportunity_matrix
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for opportunity_matrix production
quality: null
title: "Knowledge Card Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, knowledge_card]
tldr: "Domain knowledge for opportunity_matrix production"
domain: "opportunity_matrix construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F3_inject"
keywords: [opportunity_matrix construction, knowledge card opportunity matrix, opportunity_matrix, builder, knowledge_card, domain overview, key concepts, buy-side sourcing, take-rate, opp_score]
density_score: 0.85
related:
  - p08_adr_opportunity_matrix_kind
  - roi-calculator-builder
  - opportunity-matrix-builder
  - bld_instruction_opportunity_matrix
  - p11_qg_opportunity_matrix
---
## Domain Overview
`opportunity_matrix` (P11, N06, verb `analyze`) quantifies buy-side sourcing decisions by crossing supplier cost (the OFFER side, parsed from tenant catalogs) against market price+demand per product type. It is the inbound twin of `marketplace_listing` (the outbound/TUDAO channel-projection mold): both share exactly one seam, the `canonical_product` record, and both reuse the same visual matcher (`product_match`) for identity resolution. The real generator (`_tools/capability_generators/sourcing_opportunity.py`, capability slug `sourcing_opportunity`) is offline-deterministic: it never calls a network or an LLM, and it degrades to honest-null cells rather than fabricating market data when no credential/`demand_sources` is supplied.

## Key Concepts
| Concept | Definition | Source |
|---------|-----------|--------|
| Cost-source strategy | How unit_cost is derived from a catalog row: column\|filename\|fixed\|formula\|none | sourcing_opportunity.py::_row_cost |
| Manual bucket | Rows with no derivable cost -- KEPT (never dropped), surfaced in Cobertura as "manual / sem preco" | sourcing_opportunity.py |
| Take-rate | fee_model x freight_model combined; net_margin = sell - cost - fee - freight | sourcing_opportunity.py::_fee_amount/_freight_amount |
| opp_score | Weighted rank: 0.4 margin + 0.3 demand + 0.2 stock + 0.1 confidence (defaults, overridable via score_weights) | sourcing_opportunity.py::_DEFAULT_SCORE_WEIGHTS |
| sourcing_confiavel | Named go/no-go gate: margem_bruta_top >= 25% AND top-N verificado AND nenhum item critico sem preco AND frescor != RED | sourcing_opportunity.py Section 8 |
| S1-S5 sourcing rigor | Triangulation+confidence, provenance-as-section, freshness band, named gate, honest-null | _docs/specs/contract/n01_sourcing_rigor.md |
| Join key | Normalized product_type (lowercase, whitespace-collapsed); EAN/GTIN/barcode explicitly EXCLUDED | sourcing_opportunity.py::_DEFAULT_MATCH_EXCLUDE_KEYS |

## Industry Standards
- Buy-side procurement / arbitrage sourcing analysis (retail + wholesale cost-vs-demand ranking)
- Freshness banding pattern shared with `competitor_benchmark` (GREEN/AMBER/RED)
- Named-gate chaining pattern shared with `ready_for_ads` (N01 research verticals)

## Common Patterns
1. Keep every parsed row somewhere (priced / manual bucket / long-tail) -- never silent-drop (S5)
2. Treat verified web price as a CEILING on the skeptical top-N re-check, not a floor
3. Display BRUTA margin by default; LIQUIDA only when `show_net_margin=true` (opt-in)
4. Chain a passing gate (`sourcing_confiavel: true`) into `marketplace_listing` (TUDAO) as the next step
5. Emit Section 6 (Match/auditoria) only when visual input (photo/dimension) exists on a row

## Pitfalls
- Fabricating a sell price or demand level when offline (no credential / no demand_sources) -- must render "nao pesquisado"
- Using EAN/GTIN/barcode as the cross-marketplace join key (every reseller re-barcodes white-label products)
- Truncating long-tail SKUs silently instead of reporting them in Cobertura (type_cap default is 0 = no truncation)
- Confusing this kind with `roi_calculator` (single-row margin math) or `competitive_matrix` (competitor feature battlecard) -- `opportunity_matrix` is the ranked multi-row cost x demand JOIN

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p08_adr_opportunity_matrix_kind | upstream | 0.55 |
| [[roi-calculator-builder]] | sibling | 0.45 |
| [[opportunity-matrix-builder]] | downstream | 0.42 |
| [[bld_prompt_opportunity_matrix]] | downstream | 0.38 |
| [[p11_qg_opportunity_matrix]] | downstream | 0.35 |
