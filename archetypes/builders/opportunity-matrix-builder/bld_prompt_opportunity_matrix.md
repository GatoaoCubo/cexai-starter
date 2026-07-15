---
kind: instruction
id: bld_instruction_opportunity_matrix
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for opportunity_matrix
quality: null
title: "Instruction Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, instruction]
tldr: "Step-by-step production process for opportunity_matrix"
domain: "opportunity_matrix construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F6_produce"
keywords: [opportunity_matrix construction, instruction opportunity matrix, opportunity_matrix, builder, instruction, catalog_sources, opp_score, sourcing_confiavel, demand join, margin math]
density_score: 0.85
related:
  - p10_mem_opportunity_matrix_builder
  - p11_qg_opportunity_matrix
  - opportunity-matrix-builder
  - bld_knowledge_card_opportunity_matrix
  - sourcing
---
## Phase 1: RESEARCH
1. Read the 9 inputs from the frozen `input_contract` (`apps/dashboard_web/lib/molds.ts` `MOLD_SOURCING_OPPORTUNITY`): `catalog_sources` (required, object[]), `cost_source_strategy`, `tax_pct`, `region`, `demand_signal_basis`, `fee_model`, `freight_model`, `verify_top_n`, `show_net_margin`.
2. Read the generator that actually produces this kind: `_tools/capability_generators/sourcing_opportunity.py` (`@register("opportunity_matrix")`) -- it is the single source of truth for field names, defaults, and section text.
3. Read the sourcing rigor contract (`_docs/specs/contract/n01_sourcing_rigor.md`): S1 triangulation+confidence, S2 provenance-as-section, S3 freshness band, S4 named gate, S5 honest-null.
4. Read the margin/take-rate discipline referenced by the capability contract (`_docs/specs/contract/n06_unit_econ.md`, cited generically for cost->price->take-rate->margin math -- note this doc's own worked LTV/CAC section bundle targets `content_monetization`/`subscription_tier`, NOT this kind; opportunity_matrix implements its own gross/net margin math directly in the generator).
5. Identify the join key: normalized `product_type` (lowercase, whitespace-collapsed) crosses supplier cost against market demand -- NEVER EAN/GTIN/barcode (`match_exclude_keys` default).
6. Note the two row buckets the generator keeps (never drops): `priced` rows (derivable unit_cost) and the manual bucket `"manual / sem preco"` (no derivable cost -- kept, surfaced in Cobertura).

## Phase 2: COMPOSE
1. Define schema in `bld_schema_opportunity_matrix.md`: frontmatter fields, ID pattern `^p11_om_[a-z][a-z0-9_]+$`, naming `p11_om_{{name}}.md`, max_bytes 5120.
2. Build the 8 sections in FROZEN order (title + layout + columns byte-identical to `MOLD_SOURCING_OPPORTUNITY`): Resumo executivo (fields) -> Matriz de oportunidade (table, 9 cols) -> Leitura por categoria (table, 5 cols) -> Cobertura (fields) -> Verificacao top-N (table, 5 cols) -> Match / auditoria (table, 4 cols) -> Proveniencia (fields) -> Veredito + proximos passos (fields).
3. Compute margin: `gross_margin = sell - cost`; `net_margin = sell - cost - fee - freight` (fee via `fee_model`, freight via `freight_model`); the display column shows BRUTA unless `show_net_margin=true`.
4. Compute `opp_score` as the weighted sum of normalized margin/demand/stock/confidence factors (`score_weights`, default 0.4/0.3/0.2/0.1), then rank descending with the tie-break order.
5. Render every missing market/demand cell as honest-null (`"nao pesquisado"`) when offline (no credential or no `demand_sources`) -- never invent a sell price.
6. Populate Section 6 (Match / auditoria) ONLY when a row carries visual input (`photo_uri` or `dimension`); otherwise emit the single honest-skip row.
7. Close with Section 8: name the gate `sourcing_confiavel`, spell out its boolean conditions, and state the next chainable step (feeds `marketplace_listing` / TUDAO on a passing gate).
8. Peer-review section shapes against `_tools/tests/test_capgen_sourcing.py` expectations (read-only reference -- do not edit that file).
9. Finalize artifact with `quality: null` and version control.

## Phase 3: VALIDATE
1. [ ] Verify all 8 section titles + layouts match `MOLD_SOURCING_OPPORTUNITY` exactly.
2. [ ] Verify every table row has exactly `len(columns)` cells (no-drift rule).
3. [ ] Confirm the gate `sourcing_confiavel` is named with explicit conditions, not just a boolean.
4. [ ] Confirm no fabricated sell price/demand level appears where the source is offline or blocked.
5. [ ] Confirm EAN/GTIN/barcode never appear as the join key.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p10_mem_opportunity_matrix_builder]] | downstream | 0.49 |
| [[p11_qg_opportunity_matrix]] | downstream | 0.45 |
| [[opportunity-matrix-builder]] | downstream | 0.44 |
| [[bld_knowledge_opportunity_matrix]] | upstream | 0.40 |
| sourcing | related | 0.38 |
