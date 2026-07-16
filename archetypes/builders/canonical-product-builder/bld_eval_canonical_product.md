---
id: bld_qg_canonical_product
kind: quality_gate
pillar: P11
llm_function: GOVERN
version: 1.0.0
quality: null
tags: [canonical_product, quality-gate, golden-record, provenance]
title: "Quality Gate: canonical_product"
tldr: "Canonical Product feedback: quality gate with scoring dimensions and pass/fail criteria"
8f: "F7_govern"
keywords: [quality gate, canonical product feedback, fail criteria, canonical_product, quality-gate, structural law, cp id pattern, fail condition, score tiers, cama donut demo]
density_score: 0.95
updated: "2026-07-03"
related:
  - bld_schema_canonical_product
  - canonical-product-builder
---
## Quality Gate

# Quality Gate: canonical_product
## HARD Gates
| ID | Check | Fail Condition |
|----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Parse error |
| H02 | id matches `^cp_[a-z][a-z0-9_]+$` | Wrong prefix or format |
| H03 | kind == "canonical_product" | Wrong kind |
| H04 | quality == null | Non-null value |
| H05 | All 42 `CANONICAL_FIELDS` keys present (null/[]/{} allowed) | Any key missing |
| H06 | condition in {new, used, refurbished} | Invalid or missing |
| H07 | STRUCTURAL LAW: no structured value (>=12 chars) duplicated verbatim in a prose field | Violation found |
| H08 | List/object/number fields typed correctly (`_LIST_FIELDS`/`_OBJECT_FIELDS`/`_NUMBER_FIELDS`) | Wrong type |
| H09 | `depends_on: [data_contract, validation_schema]` present | Missing or wrong |
| H10 | Total file size <= 6144 bytes (kinds_meta max_bytes) | Exceeds max_bytes |

## SOFT Scoring
| ID | Dimension | Weight | 10pts | 5pts | 0pts |
|----|-----------|--------|-------|------|------|
| S01 | `provenance_coverage()` ratio | 1.0 | Near 1.0 for populated fields | Partial | Absent |
| S02 | `field_union_coverage()` completeness | 1.0 | High union coverage | Partial | Sparse |
| S03 | Conflict trail preserved | 0.8 | Every disagreement in `_conflicts` | Some preserved | Silently resolved |
| S04 | `checkout_binding` present | 0.7 | Set (buyability gate, FR-012) | Partial | Null |
| S05 | Media coverage | 0.5 | >=1 image, cover first | Some images | None |

## Score Tiers
| Score | Action |
|-------|--------|
| >= 9.0 | Publish; downstream `ChannelAdapter` may project |
| >= 7.0 | Use with monitoring; improve provenance/conflict coverage |
| < 7.0 | Return: fix structural-law violations and missing fields first |

## Examples

# Examples: canonical_product
## Example 1: a pet donut-bed SKU (the shape of the tool's built-in `--demo` fixture, brand-neutralized)
```yaml
id: cp_demo_sku001
kind: canonical_product
pillar: P06
title: "Pet Donut Bed -- Canonical Product (DEMO-SKU-001)"
sku: DEMO-SKU-001
condition: new
depends_on: [data_contract, validation_schema]
quality: null
tags: [sample-tenant, canonical-product, golden-record]
```
Sources: erp (weight 900g, gtin present), marketplace (weight 450g, colors+materials,
marketplace_item_id MKT0000000000), own_site (storefront_variant_id 00000000000).
weight_grams: 900 (erp wins; `_conflicts.weight` flags 900 vs 450, NOT averaged).
checkout_binding: 00000000000 (from shopify_variant_id). images: union of all 3
sources' urls. This is the exact scenario `cex_canonical_product.py --demo` proves
(re-verified this session: `--self-test` -> all checks OK).

## Example 2: Minimal golden (self-test fixture)
```yaml
id: cp_cb1
kind: canonical_product
sku: CB1
condition: new
```
title from `name`; weight_grams 900 from `weight.grams`; available_quantity 3
(int) from `quantity`; currency defaults BRL (system default, excluded from the
provenance denominator); video_url absent -> null (never-fabricate).

## Anti-example (WRONG)
```yaml
id: ml_listing_demo_sku001     # WRONG: this is marketplace_listing, a per-channel PROJECTION
kind: canonical_product   # WRONG: a channel projection is not the channel-neutral union
# key_features buried inside long_description  # WRONG: structural-law violation
```

### H_RELATED: Cross-Reference Check (HARD)
- [ ] `related:` frontmatter populated (min 3 entries)
- [ ] `## Related Artifacts` section present in body
- [ ] At least 1 upstream (`data_contract`/`validation_schema`) and 1 downstream (`marketplace_listing`) reference
- Gate: REJECT if < 3 entries

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` populated (3-15 entries)
- [ ] Both upstream and downstream referenced
- Penalty: -0.3 if empty

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_canonical_product]] | upstream | 0.45 |
| [[canonical-product-builder]] | upstream | 0.40 |
| [[bld_prompt_canonical_product]] | sibling | 0.35 |
