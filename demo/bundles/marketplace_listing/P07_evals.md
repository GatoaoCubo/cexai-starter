---
id: bld_eval_marketplace_listing
kind: quality_gate
pillar: P11
llm_function: GOVERN
8f: F7_govern
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Gate: marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, eval, quality_gate, P11]
tldr: "HARD + SOFT gates for marketplace_listing: 6 FROZEN sections, embedded ml_listing payload with 7 required keys, condition vocabulary, BRAND/SELLER_SKU injection, readiness gate honesty, body <= 6144B."
density_score: 0.9
related:
  - bld_schema_marketplace_listing
  - bld_output_marketplace_listing
  - marketplace-listing-builder
  - bld_feedback_marketplace_listing
  - output-validator-builder
---

# Gate: marketplace_listing
## HARD gates (any FAIL -> REJECT, no score)
| ID | Check | Rule |
|----|-------|------|
| H01 | Frontmatter parses | valid YAML, complete |
| H02 | id pattern | `^p05_ml_[a-z][a-z0-9_]+$`, equals filename stem |
| H03 | kind literal | `kind` is exactly `marketplace_listing` |
| H04 | quality null | `quality` is null |
| H05 | six sections present | Listagem ML, Preco e Estoque, Fotos, Atributos, Descricao, Payload ML (pronto para publicar) -- exact titles, exact order |
| H06 | payload consistency | the 7 ML keys (title/category_id/price/currency_id/available_quantity/condition/listing_type_id) appear consistently in BOTH the Listagem ML + Preco e Estoque field rows AND the Payload ML section's JSON do anuncio string |
| H07 | body within limit | body <= 6144 bytes |

## SOFT scoring (0 or 10 x weight)
| Dimension | Weight | Pass condition |
|-----------|--------|----------------|
| titulo_ml mapped + <=60 chars | 1.0 | title non-empty; length <=60 or a [WARN] note present |
| categoria_ml mapped | 1.0 | category_id non-empty |
| preco mapped | 1.0 | price > 0 |
| BRAND + SELLER_SKU injection | 1.0 | attributes[] carries BRAND (from marca) and SELLER_SKU (from sku) when those inputs were given |
| condition vocabulary correct | 1.0 | novo/usado/recondicionado map to new/used/refurbished (unknown defaults new) |
| currency + listing_type defaults | 0.5 | currency_id==BRL; listing_type_id defaults gold_special when absent |
| readiness gate honesty | 1.0 | score/passed/missing_required/notes computed per the deduction table, never hand-waved |
| clean-room | 1.0 | no fabricated photo URL, price, or attribute value |
| Fotos/Descricao/Marca soft-warned | 0.5 | absence produces a [WARN] note, not a silent drop |
Sum weights 8.0; `soft = sum(weight*score)/8.0*10`.

## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN -- canonical library entry |
| >= 8.0 | PUBLISH |
| >= 7.0 | REVISE -- gate math or section shape needs work |
| < 7.0 | REJECT |

## Golden vs Anti
- GOLDEN pattern: a complete G1 row (see the runtime sample `_output/g2_sample_listing.md`
  -- Arranhador Torre Sisal 1.2m, 2 photos, BRAND+SELLER_SKU auto-injected, readiness
  score 1.0, passed=true) -- 6 sections, all 7 ml_listing keys populated, zero
  missing_required.
- ANTI: a section retitled or reordered; a fabricated photo URL; category_id left empty
  with no [FAIL] note; BRAND omitted when marca was given; `quality` non-null; the
  readiness `score` written into `quality` (the two fields are distinct).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | upstream | 0.55 |
| [[bld_output_marketplace_listing]] | sibling | 0.45 |
| [[marketplace-listing-builder]] | sibling | 0.42 |
| [[bld_feedback_marketplace_listing]] | downstream | 0.4 |
| [[output-validator-builder]] | related | 0.38 |
