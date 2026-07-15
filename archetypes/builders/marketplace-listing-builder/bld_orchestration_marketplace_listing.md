---
id: bld_orchestration_marketplace_listing
kind: workflow
pillar: P12
llm_function: COLLABORATE
8f: F8_collaborate
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Orchestration: dispatching + composing marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, orchestration, dual-output, P12]
tldr: "How marketplace_listing builds are dispatched (one SKU per build) and how the SEPARATE runtime path (cex_run_capability + capability_generators + cex_dual_output) actually serves a live tenant."
density_score: 0.88
related:
  - bld_architecture_marketplace_listing
  - bld_prompt_marketplace_listing
  - bld_tools_marketplace_listing
  - spec_dual_output_contract
  - output-validator-builder
---

# Orchestration: marketplace_listing
## Single build (this builder's path)
`marketplace-listing-builder` runs F1-F8 on one G1 row -> one `p05_ml_{sku}.md` instance.
Standard 8F: F1 constrains kind/pillar/naming, F2 loads ISOs, F3 injects the G1 row +
[[bld_knowledge_marketplace_listing]], F4 plans the field mapping + gate math, F5 checks
tools, F6 authors the 6 sections, F7 validates gates, F8 compiles + commits.

## The SEPARATE runtime path (what a live tenant actually triggers)
A tenant clicking "gerar" on the dashboard's marketplace_listing capability does NOT run
this builder. It runs: `cex_run_capability.py` resolves
`capability_generators.get_generator("marketplace_listing")` -> `build(inputs)` (pure
Python, deterministic) -> `cex_dual_output.to_dual_output("marketplace_listing", struct,
media_requests=listing_media_requests(inputs), produced_media=listing_produced_media(inputs))`
-> `{machine_md, human_html, media_slots}`, persisted tenant-scoped (RLS). This builder's
job is to keep the ARCHETYPAL `p05_ml_*` contract byte-shape-identical to that runtime path
-- not to replace it.

## Downstream composition
A builder-authored instance is a reference/fixture/golden example (documentation, QA,
onboarding before a tenant has live G1 data) -- consumed wherever a governed example of
"what a marketplace_listing looks like" is needed. It composes with
[[output-validator-builder]] (the sibling P05 kind this one `depends_on` per
`.cex/kinds_meta.json`) for a future validation pass, and with
spec_dual_output_contract for the dual-output shape it must stay compatible with.

## Convergence
No swarm/library-coverage loop exists yet for this kind (unlike `motion_scene`'s
design_system x primitive matrix) -- today's coverage axis is one instance per SKU, built
on demand, not pre-populated.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_marketplace_listing]] | upstream | 0.5 |
| [[bld_prompt_marketplace_listing]] | sibling | 0.42 |
| [[bld_tools_marketplace_listing]] | related | 0.4 |
| spec_dual_output_contract | related | 0.4 |
| [[output-validator-builder]] | related | 0.38 |
