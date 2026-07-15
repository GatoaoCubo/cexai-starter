---
id: bld_architecture_design_system
kind: pattern
pillar: P06
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Architecture: where design_system sits"
domain: design_system
quality: null
tags: [design_system, builder, architecture, composition, P06]
tldr: "How design_system fits CEXAI: governed by the contract, selected by brand_config, injected into surface generators, scaled by the taste loop."
density_score: 0.9
related:
  - p06_vs_design_system
  - p08_adr_design_system_kind
  - p03_ps_design_system_library_scale
  - bld_orchestration_design_system
  - p01_kc_design_system
---

# Architecture: where design_system sits
## Position in the kind graph
| Relation | Kind | Direction |
|----------|------|-----------|
| governed by | validation_schema (p06_vs_design_system) | upstream contract |
| selected by | brand_config | upstream selector |
| injected into | landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck | downstream consumers |
| scaled by | variant_shotgun_taste_loop | sideways (library growth) |
## Layering
design_system is a P06 CONTENT asset (concrete values), distinct from the P06 CONTRACT (shape) and the brand_config (identity). It binds at F1 CONSTRAIN (declared as a constraint) and F3 INJECT (tokens injected).
## Why a kind, not a composition
A doc + a pattern + a constraint_spec per system fragments each system across ~4 files with no atomic "pick this system" handle (~600 files for 150 systems). The library use case demands an atomic, selectable unit -- the new-kind signal (p08_adr_design_system_kind).
## Library shape
The systems form a coverage matrix over five aesthetic axes; each instance owns a distinct coordinate. No two systems read as siblings (p03_ps_design_system_library_scale).
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p06_vs_design_system | upstream | 0.5 |
| p08_adr_design_system_kind | upstream | 0.48 |
| p03_ps_design_system_library_scale | related | 0.45 |
| [[bld_orchestration_design_system]] | sibling | 0.4 |
| [[p01_kc_design_system]] | related | 0.4 |
