---
kind: memory
id: p10_mem_opportunity_matrix_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for opportunity_matrix construction
quality: null
title: "Memory Opportunity Matrix Builder"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, memory]
tldr: "Learned patterns and pitfalls for opportunity_matrix construction"
domain: "opportunity_matrix construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F3_inject"
keywords: [opportunity_matrix construction, memory opportunity matrix builder, opportunity_matrix, builder, memory, observation, pattern, evidence, honest-null discipline, gate conditions]
density_score: 0.85
related:
  - bld_instruction_opportunity_matrix
  - opportunity-matrix-builder
  - p11_qg_opportunity_matrix
  - bld_knowledge_card_opportunity_matrix
  - p08_adr_opportunity_matrix_kind
---
## Observation
The generator's first production surface (W3 CAPGEN, `sourcing_opportunity.py`) shipped OFFLINE-only: no live network or LLM call at this level, so every early artifact built against it will show an offline scaffold (gate BLOQUEADO, demand cells honest-null) unless a credential + `demand_sources` are supplied. Builders that skip reading the generator source first tend to draft a "live-looking" example that the real output can never produce.

## Pattern
Successful artifacts transcribe section titles/columns byte-for-byte from `MOLD_SOURCING_OPPORTUNITY` (`apps/dashboard_web/lib/molds.ts`) rather than paraphrasing them -- the renderer and `test_capgen_sourcing.py` both assert exact string equality on titles, layouts, and column arrays.

## Evidence
`_tools/tests/test_capgen_sourcing.py` (516 lines, read-only reference) locks section count = 8, section titles/layouts to a fixed list, and per-table column arrays for Matriz/Leitura/Verificacao/Match -- any drafted example that reorders or renames a section would fail these tests if it were ever used as generator test data (it is not; it is documentation, but the same shape discipline applies).

## Recommendations
- Read `_tools/capability_generators/sourcing_opportunity.py` before drafting any example -- it is the single source of truth, not `capability_contracts_v1.0.md` (which summarizes it) or this memory file.
- Keep the manual bucket ("manual / sem preco") and long-tail counts visible in Cobertura -- a builder that only shows the top-N ranked rows without accounting for the rest fails the S5 honest-null / no-silent-drop discipline.
- State the `sourcing_confiavel` gate's 4 boolean conditions verbatim, not just the resulting true/false.
- Do not import `n06_unit_econ`'s LTV/CAC section bundle into this kind's output -- that aspect targets `content_monetization`/`subscription_tier` only; opportunity_matrix computes its own gross/net margin directly.
- Do not build the sibling `product_match` builder as part of an opportunity_matrix task -- it is a separate ADR-approved leaf kind (P04/N03) with its own follow-on scaffolding work.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_opportunity_matrix]] | upstream | 0.47 |
| [[opportunity-matrix-builder]] | downstream | 0.41 |
| [[p11_qg_opportunity_matrix]] | downstream | 0.36 |
| [[bld_knowledge_card_opportunity_matrix]] | upstream | 0.32 |
| p08_adr_opportunity_matrix_kind | upstream | 0.30 |
