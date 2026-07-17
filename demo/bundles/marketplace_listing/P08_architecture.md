---
id: bld_architecture_marketplace_listing
kind: pattern
pillar: P08
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Architecture: where marketplace_listing sits"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, architecture, channel-adapter, P08]
tldr: "How marketplace_listing fits CEXAI: kind-defined by kinds_meta.json (upstream_source=cex_channel_adapter.py), computed at runtime by the capability_generators generator, dual-projected by cex_dual_output, mirrored on the dashboard by molds.ts."
density_score: 0.9
related:
  - bld_schema_marketplace_listing
  - bld_orchestration_marketplace_listing
  - bld_tools_marketplace_listing
  - output-validator-builder
---

# Architecture: where marketplace_listing sits
## Position in the kind graph
| Relation | Kind / File | Direction |
|----------|------|-----------|
| kind-defined by | `.cex/kinds_meta.json` (`marketplace_listing` entry: pillar P05, naming `p05_ml_{name}.md`, max_bytes 6144, depends_on canonical_product + output_validator) | upstream contract |
| computed at runtime by | `_tools/capability_generators/marketplace_listing.py` (`@register("marketplace_listing")`, `build(inputs)`) | upstream reference computation -- this builder mirrors it 1:1 |
| dual-projected by | `_tools/cex_dual_output.py` (`to_dual_output`) -> machine_md + human_html + media_slots | downstream runtime projection |
| dispatched by | `_tools/cex_run_capability.py` (`capability_generators.get_generator("marketplace_listing")`) | runtime orchestration |
| mirrored on the dashboard by | `apps/dashboard_web/lib/molds.ts` (`MOLD_MARKETPLACE_LISTING`) -- the input form + on-screen mold | sibling (frontend) |
| depends_on (kinds_meta) | canonical_product (P06, no builder exists yet -- a real gap), output_validator (P05, [[output-validator-builder]] exists) | upstream |
| NOT | partner_listing (a directory/sales listing; different concept) nor canonical_product (the channel-neutral superset) | boundary exclusion |

## Two vocabularies for the same idea (read before authoring)
`.cex/kinds_meta.json`'s `boundary`/`description` describe the LOWER-LEVEL seam
`_tools/cex_channel_adapter.py` (`MercadoLivreAdapter`, its declared `upstream_source`):
canonical_product -> a payload WITH a `_meta` block + a `PUBLISH-READY`/`NOT-READY`
readiness report (`missing[]`/`warnings[]`, each `{field, severity, message}`). That seam
also filters pictures to `https://` only and hard-blocks on `available_quantity<=0` via a
separate `buyability()` check.

The SHIPPED capability generator (`capability_generators/marketplace_listing.py` --
docstring: "capability slug = kind") reads the dashboard's G1 fields directly, has NO
`_meta` block, does NOT filter non-https picture URLs, and does NOT block on zero stock.
Its readiness verdict is `score`/`passed`/`missing_required`/`notes` instead of
`missing[]`/`warnings[]`/`PUBLISH-READY`. Same underlying idea (a channel projection + a
gate), two different, NOT-yet-unified implementations. This builder authors to the
SHIPPED generator's shape because that is what a tenant's dashboard actually dispatches --
see [[bld_knowledge_marketplace_listing]] for the full divergence list.

## Layering
marketplace_listing is a P05 OUTPUT asset (an LLM/builder-authored declarative
projection), distinct from:
- the RUNTIME GENERATOR (`capability_generators/marketplace_listing.py` -- deterministic
  Python, not an LLM artifact; this builder's contract mirrors its output, never edits it)
- the LOWER-LEVEL SEAM (`cex_channel_adapter.py` -- a different field-naming layer, above)
- the DUAL-OUTPUT EMITTER (`cex_dual_output.py` -- projects a StructuredOutput into
  machine_md + human_html; a builder-authored instance is upstream of that projection)

## Why a kind, not a composition
A per-product, per-channel listing needs an atomic, selectable, swarm-buildable unit (one
SKU x one channel = one coordinate), the same way bld_architecture_motion_scene
justifies motion_scene: a pipeline_template + generator + schema per listing would
fragment one product's ML listing across 3+ files with no single "this is SKU X's ML
listing" handle.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | sibling | 0.5 |
| [[bld_orchestration_marketplace_listing]] | sibling | 0.45 |
| [[bld_tools_marketplace_listing]] | sibling | 0.42 |
| [[output-validator-builder]] | related | 0.4 |
| spec_dual_output_contract | related | 0.38 |
