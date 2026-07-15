---
id: bld_instruction_canonical_product
kind: instruction
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for canonical_product
version: 1.0.0
quality: null
tags: [canonical_product, builder, instruction]
title: "Instruction Canonical Product Builder"
author: builder
tldr: "Step-by-step production process for canonical_product"
8f: "F6_produce"
keywords: [instruction canonical product builder, canonical_product, builder, instruction, prompt construction checklist, golden record, provenance, structural law, sibling]
density_score: 0.85
created: "2026-07-03"
updated: "2026-07-03"
related:
  - bld_schema_canonical_product
  - bld_eval_canonical_product
  - data-contract-builder
  - validation-schema-builder
  - kc_canonical_product
---
# Instructions: How to Produce a canonical_product

## Phase 1: IDENTIFY
1. Identify the SKU / product_id; confirm >=1 per-source normalized record exists (`docs/schema/product_catalog_schema.yaml` shape, produced by `cex_product_catalog_adapter.normalize_product()`)
2. Confirm a golden record is available via `cex_catalog_merge.merge_records()`, OR call `merge_to_canonical(records_by_source)` directly to run merge+bridge in one step
3. Determine fresh build vs update to an existing `p06_cp_*.md` instance
4. Confirm both `depends_on` prerequisites are understood: `data_contract` (schema+SLA boundary) and `validation_schema` (post-generation output check) -- neither is canonical_product itself
5. Confirm a real downstream consumer exists for this record (`marketplace_listing` via `cex_channel_adapter.ChannelAdapter`, or grounded ad copy via `cex_grounded_copy.py` / `cex_content_factory.py`) -- canonical_product is a bridge, never a dead end

## Phase 2: COMPOSE
1. Read `bld_schema_canonical_product.md` for the 42 `CANONICAL_FIELDS` (10 groups) + 2 meta-trails
2. Set `id: cp_{sku_snake}`, naming `p06_cp_{{name}}.md`
3. Populate identity -> classification -> prose -> structured -> specs -> commerce -> media -> logistics -> checkout_binding -> link-state, in that order
4. Keep `PROSE_FIELDS` (description, long_description, why_it_works) SEPARATE from `STRUCTURED_FIELDS` (key_features, benefits_functional, benefits_emotional, attributes, colors, materials, audience_tags) -- the structural law
5. Carry `_provenance` and `_conflicts` from the source merge untouched; a cross-source disagreement is FLAGGED, never averaged or silently overwritten
6. If numeric dims are absent, try `parse_freetext_dims()` on a free-text dims string; on failure, flag `dims:unparsed`, never invent a number
7. Set `quality: null` -- never self-score

## Phase 3: VALIDATE
1. HARD gates:
   - id follows pattern `cp_{name}`, kind == `canonical_product`, quality == null
   - all 42 `CANONICAL_FIELDS` keys present (null allowed)
   - condition in `{new, used, refurbished}`
   - no `STRUCTURED_FIELDS` value duplicated verbatim (>=12 chars) inside a `PROSE_FIELDS` value (structural-law gate)
   - file size <= 6144 bytes (kinds_meta.json `max_bytes`)
2. SOFT gates:
   - `provenance_coverage()` near 1.0 for populated, source-derived fields
   - `field_union_coverage()` tracked as a completeness signal
   - every cross-source disagreement preserved in `_conflicts`
   - `checkout_binding` present when buyability is expected (FR-012 gate)

## Prompt Construction Checklist
- Verify prompt follows target kind's instruction template
- Validate variable placeholders use standard naming convention
- Cross-reference with `data_contract` + `validation_schema` (the 2 `depends_on`) for boundary completeness
- Test with the real `--demo` fixture (`_tools/cex_canonical_product.py --demo`) before publishing a new instance

## Prompt Pattern
```yaml
# Prompt validation
template_match: true
variables_valid: true
structural_law_checked: true
provenance_carried: true
```
```bash
python _tools/cex_canonical_product.py --self-test
python _tools/cex_compile.py {FILE}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_canonical_product]] | downstream | 0.35 |
| bld_eval_canonical_product | sibling | 0.34 |
| [[data-contract-builder]] | related | 0.33 |
| [[validation-schema-builder]] | related | 0.32 |
| [[kc_canonical_product]] | upstream | 0.31 |
