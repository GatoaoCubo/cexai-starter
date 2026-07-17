---
id: bld_memory_marketplace_listing
kind: learning_record
pillar: P10
llm_function: INJECT
8f: F3_inject
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Patterns: marketplace_listing builds"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, memory, patterns, P10]
tldr: "Learned patterns + recurring failure modes from marketplace_listing builds: map-first, gate-math verified upfront, honest placeholders, and the divergence traps."
density_score: 0.9
related:
  - bld_knowledge_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_feedback_marketplace_listing
  - bld_config_marketplace_listing
  - output-validator-builder
---

# Patterns: marketplace_listing builds
## What scored high
| Pattern | Why |
|---------|-----|
| Map-first | walking the G1->G2 table before writing a single section -> no field left unmapped |
| Gate math verified upfront | computing score/passed/missing_required at F4 REASON, before F6 -> no H06 surprise at F7 |
| Honest placeholders, verbatim | using the generator's exact strings ("(sem sku)", "(sem marca -- obrigatorio pelo ML)") -> the artifact reads identically to a live tenant run |
| BRAND/SELLER_SKU order preserved | BRAND prepended, SELLER_SKU appended, matching the generator's own list-construction order -> the Atributos table matches byte-for-byte |
| Readiness in frontmatter, not a 7th section | score/passed/missing_required/notes live in frontmatter, mirroring the generator's StructuredOutput -- never invented as a body section |

## Recurring failures
| Failure | Fix |
|---------|-----|
| Assuming an https filter | the shipped generator has none; only the lower-level `cex_channel_adapter.py` seam filters -- do not add a filter the artifact does not reflect |
| Assuming a stock (available_quantity<=0) hard block | the shipped generator never gates on stock; only `buyability()` in the OTHER seam does |
| Truncating the title | the shipped generator only warns past 60 chars, never truncates -- truncation is the OTHER seam's `clean_ml_title` behavior |
| Section renamed "Payload ML" without the suffix | the exact title is `Payload ML (pronto para publicar)` -- dropping the suffix breaks H05 |
| Conflating `quality` and `score` | `quality` is always `null` (CEX meta); `score` is the embedded 0.0-1.0 readiness float -- two different frontmatter fields |
| Inventing a `_meta` block | the shipped generator's `ml_listing` has none; `_meta` belongs to the other seam's `map()` output |

## Library shape
One instance per (SKU x marketplace) coordinate; today `marketplace` is effectively fixed
to `mercado_livre` (the only entry in `CHANNEL_ADAPTERS`), so the coverage axis is SKU only
until a second channel is wired.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_marketplace_listing]] | upstream | 0.45 |
| [[bld_eval_marketplace_listing]] | sibling | 0.42 |
| [[bld_feedback_marketplace_listing]] | sibling | 0.4 |
| [[bld_config_marketplace_listing]] | related | 0.38 |
| [[output-validator-builder]] | related | 0.36 |
