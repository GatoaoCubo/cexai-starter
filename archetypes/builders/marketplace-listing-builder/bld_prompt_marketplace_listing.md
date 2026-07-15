---
id: bld_prompt_marketplace_listing
kind: instruction
pillar: P03
llm_function: REASON
8f: F4_reason
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Process: build a marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, prompt, process, P03]
tldr: "Research > compose > validate process for producing one marketplace_listing that mirrors _tools/capability_generators/marketplace_listing.py's field mapping, section shape, and readiness gate exactly."
density_score: 0.9
related:
  - bld_schema_marketplace_listing
  - bld_output_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_knowledge_marketplace_listing
  - bld_config_marketplace_listing
---

# Process: build a marketplace_listing
## Inputs
A G1 catalog row (titulo_ml, descricao, categoria_ml, marca, condicao, preco, estoque,
fotos, atributos, sku) + optional marketplace (default `mercado_livre`) + the contract
[[bld_schema_marketplace_listing]].

## Step 1 -- RESEARCH (F3 INJECT)
- Load [[bld_schema_marketplace_listing]] (source of truth) + [[bld_knowledge_marketplace_listing]].
- Confirm marketplace defaults to `mercado_livre` (the only channel `CHANNEL_ADAPTERS` wires today).
- Read the G1 row; note which fields are present vs absent -- absence drives the gate, never
  a fabricated value.

## Step 2 -- COMPOSE (F6 PRODUCE)
- Map G1 -> G2 exactly: titulo_ml->title, descricao->description.plain_text,
  categoria_ml->category_id, condicao->condition (novo->new, usado->used,
  recondicionado->refurbished, unknown->new), preco->price, estoque->available_quantity,
  fotos->pictures[].url (comma-sep string OR JSON array; NO https filter in the shipped
  generator), atributos->attributes[]{id,value_name} (JSON object), sku->seller_custom_field.
- Inject BRAND from marca when absent from atributos (case-insensitive id check); inject
  SELLER_SKU from sku when absent. BRAND prepends, SELLER_SKU appends -- never overwrite an
  attribute the row already declares.
- listing_type_id defaults `gold_special`; currency_id is always `BRL`.
- Compose the 6 sections in FROZEN order (see [[bld_schema_marketplace_listing]]); use the
  exact honest placeholders when a field is absent: "(sem titulo_ml -- obrigatorio)",
  "(sem categoria_ml -- obrigatorio)", "(sem preco -- obrigatorio)", "(sem sku)",
  "(sem marca -- obrigatorio pelo ML)", "(sem descricao -- recomendado)", and for Fotos
  "(sem fotos -- adicione URLs em fotos ou envie via upload no slot abaixo)".
- Payload ML section: JSON-serialize the ml_listing dict (ASCII-safe), truncate the preview
  at 900 chars with "..." exactly like the generator's own preview convention.

## Step 3 -- VALIDATE (F7 GOVERN)
- Compute the readiness gate: score starts 1.0; -0.20 titulo_ml missing; -0.05 titulo_ml
  >60 chars; -0.15 categoria_ml missing; -0.15 preco<=0; -0.05 descricao missing; -0.10 no
  fotos; -0.05 marca missing; floor at 0.0. passed = zero missing_required (titulo_ml/
  categoria_ml/preco only) AND score >= 0.70.
- Confirm body <= 6144 bytes; confirm section titles/order match
  [[bld_schema_marketplace_listing]] exactly.
- Clean-room self-check: no fabricated photo URL, price, or attribute value.
- Set `quality: null`; compile.

## Output discipline
Emit only the artifact (frontmatter + body) per [[bld_output_marketplace_listing]]. No
preamble, no chatter.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | upstream | 0.55 |
| [[bld_output_marketplace_listing]] | downstream | 0.5 |
| [[bld_eval_marketplace_listing]] | downstream | 0.48 |
| [[bld_knowledge_marketplace_listing]] | related | 0.42 |
| [[bld_config_marketplace_listing]] | related | 0.38 |
