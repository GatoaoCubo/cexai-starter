---
id: bld_config_marketplace_listing
kind: env_config
pillar: P09
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Config: marketplace_listing build knobs"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, config, P09]
tldr: "Build-time knobs for a marketplace_listing: marketplace channel, listing_type_id default, condition default, currency, and the readiness pass threshold."
density_score: 0.88
related:
  - bld_schema_marketplace_listing
  - bld_prompt_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_architecture_marketplace_listing
  - bld_tools_marketplace_listing
---

# Config: marketplace_listing build knobs
CONFIG restricts SCHEMA; it never adds fields the schema does not know.
## Knobs
| Knob | Default | Range | Effect |
|------|---------|-------|--------|
| marketplace | mercado_livre | mercado_livre (only channel `CHANNEL_ADAPTERS` wires today) | target channel; the OUTPUT shape stays ML-specific regardless of value |
| listing_type_id | gold_special | gold_special, gold_pro, gold_premium, silver, bronze, free | ML listing tier |
| condition | novo | novo\|usado\|recondicionado (-> new\|used\|refurbished; unknown defaults new) | product condition |
| currency_id | BRL | BRL (fixed) | ML Brazil constant, never overridden |
| title_max_len | 60 | fixed (ML_TITLE_MAX) | soft-warn only past this length, never hard-truncated by this builder |
| pass_threshold | 0.70 | fixed | score floor for `passed=true` (also requires zero missing_required) |

## Invariants (cannot override)
- quality stays null (the CEX meta-quality; distinct from the embedded `score` field).
- currency_id is always BRL; there is no multi-currency path in the shipped generator.
- BRAND/SELLER_SKU auto-injection never overwrites an attribute the row already declares.
- missing_required only ever contains `titulo_ml->title`, `categoria_ml->category_id`,
  `preco->price` -- no other field can appear there (estoque/condicao/marca/fotos are
  soft-warned, never hard-gated, in the shipped generator).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | upstream | 0.5 |
| [[bld_prompt_marketplace_listing]] | sibling | 0.42 |
| [[bld_eval_marketplace_listing]] | downstream | 0.4 |
| [[bld_architecture_marketplace_listing]] | related | 0.38 |
| [[bld_tools_marketplace_listing]] | related | 0.36 |
