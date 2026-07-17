---
id: bld_tools_marketplace_listing
kind: toolkit
pillar: P04
llm_function: CALL
8f: F5_call
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Tools: building + validating a marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, tools, P04]
tldr: "The tool inventory a marketplace_listing build calls: compile, doctor, score, index, plus the runtime references it must stay contract-identical to (read-only)."
density_score: 0.88
related:
  - bld_prompt_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_orchestration_marketplace_listing
  - bld_architecture_marketplace_listing
  - output-validator-builder
---

# Tools: marketplace_listing
## Build + govern
| Tool | Use |
|------|-----|
| `cex_compile.py` | compile the instance .md -> .yaml (mandatory F8) |
| `cex_doctor.py` | builder-dir health (this ISO set passes 12/12) |
| `cex_score.py` | peer score (never self-score) |
| `cex_index.py` | index frontmatter + wikilinks |

## Domain checks
| Check | How |
|-------|-----|
| Section shape | assert the 6 body sections match [[bld_schema_marketplace_listing]] titles/order/layout exactly |
| ml_listing keys | assert all 7 required keys present (title/category_id/price/currency_id/available_quantity/condition/listing_type_id) |
| Gate math | recompute score from the deduction table; assert it matches the frontmatter `score` |
| Condition vocabulary | assert condicao mapped through the 3-way table, never a 4th value |
| BRAND/SELLER_SKU | assert both present when marca/sku were given, absent (not fabricated) when not |
| Body size | assert body <= 6144 bytes |

## Runtime references (READ-ONLY -- this builder mirrors their contract, never edits them)
| Path | Role |
|------|------|
| `_tools/capability_generators/marketplace_listing.py` | the SHIPPED generator this builder's contract mirrors 1:1 |
| `_tools/capability_generators/_base.py` | the StructuredOutput interface (`register`, `fields_section`/`table_section`/`list_section`, `structured_output`) |
| `_tools/cex_run_capability.py` | the runtime dispatcher (`get_generator("marketplace_listing")`) |
| `_tools/cex_dual_output.py` | the dual-output projection (`to_dual_output`) -> machine_md + human_html |
| `apps/dashboard_web/lib/molds.ts` | `MOLD_MARKETPLACE_LISTING` -- the frontend input form + on-screen mold mirror |
| `_tools/tests/test_marketplace_listing.py` | the generator's own test proof (11 tests) -- another stream owns this file |
| `_tools/cex_channel_adapter.py` | the lower-level, differently-shaped seam (`.cex/kinds_meta.json` `upstream_source`) |

## Discipline
Tools VALIDATE; they never invent a field value. A marketplace_listing's price, photos,
and attributes are authored from the real G1 row, then verified against the gate -- never
guessed to make a gate pass.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_marketplace_listing]] | upstream | 0.45 |
| [[bld_prompt_marketplace_listing]] | related | 0.42 |
| [[bld_orchestration_marketplace_listing]] | sibling | 0.4 |
| [[bld_architecture_marketplace_listing]] | related | 0.4 |
| [[output-validator-builder]] | related | 0.36 |
