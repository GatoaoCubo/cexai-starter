---
id: bld_rules_canonical_product
kind: collaboration
pillar: P12
llm_function: COLLABORATE
version: 1.0.0
quality: null
tags: [canonical_product, rules, guardrail]
title: "Collaboration + Rules: canonical_product Builder"
author: builder
tldr: "Collaboration ISO slot for canonical_product-builder; body retained as originally authored (ALWAYS/NEVER, edge cases, naming, size budget) -- a full crew-role/handoff writeup is a follow-up, not fabricated here"
8f: "F8_collaborate"
keywords: [canonical_product builder, rules, guardrail, builder rules, naming conventions, size budget, edge cases, free-text dims]
density_score: 0.88
created: "2026-07-03"
updated: "2026-07-04"
related:
  - canonical-product-builder
  - bld_memory_canonical_product
  - kc_canonical_product
---
# Collaboration: canonical_product-builder (Builder Rules Retained)

> **Taxonomy-hygiene note (R-262c, 2026-07-04):** this ISO occupies the
> `bld_orchestration_canonical_product.md` slot; its `kind:` is corrected here
> from the misfiled `guardrail` to the slot's canonical `collaboration`
> (verified against 9 clean sibling builders). The body below was authored as
> builder construction Rules (ALWAYS/NEVER/edge cases/naming/size budget), not
> a crew-role/handoff writeup -- preserved verbatim per hygiene policy (never
> delete content). A canonical "My Role in Crews" / "Handoff Protocol"
> writeup for this slot is a follow-up, not fabricated here. Full evidence:
> `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md` Section 9.

## ALWAYS
- ALWAYS populate all 42 CANONICAL_FIELDS keys (null/[]/{} allowed, never omitted)
- ALWAYS keep STRUCTURED_FIELDS out of PROSE_FIELDS verbatim (the structural law, Article II)
- ALWAYS carry `_provenance` and `_conflicts` through from the source merge, untouched
- ALWAYS flag a cross-source numeric disagreement in `_conflicts`; never average or silently overwrite
- ALWAYS set `quality: null`

## NEVER
- NEVER use canonical_product for a per-channel payload (use marketplace_listing)
- NEVER use canonical_product for the rendered buyer page (use product_ad, capability layer)
- NEVER invent a value for a field absent from every source (never-fabricate)
- NEVER re-implement the merge/bridge in another language (bridge `cex_catalog_merge.py`, Article VII)
- NEVER claim provenance for a system-defaulted field (currency=BRL default, synthetic id, unsourced condition=new)

## EDGE CASES
| Case | Rule |
|------|------|
| Free-text dims string, no numeric axes | `parse_freetext_dims()` best-effort; unparseable -> `dims:unparsed` flag, never an invented number |
| Numeric conflict (e.g. weight 900g vs 450g) | Flag in `_conflicts`; keep the precedence winner in the field; never average |
| GTIN absent | Use `gtin_absent_reason` as the escape hatch (mirrors ML `EMPTY_GTIN_REASON`) |
| Empty golden record (no sources) | degrade-never: return a valid all-`None`/`[]`/`{}` shape, never crash |
| `condition` unsourced by any channel | Default to "new" WITHOUT claiming provenance for that default |
| BR decimal comma in free-text dims ("12,5 x 8 x 4 cm") | Normalize comma to dot before parsing |

## Naming Conventions
| Pattern | Example |
|---------|---------|
| `cp_{sku_snake}` | `cp_demo_sku001` |
| File: `p06_cp_{{name}}.md` | `p06_cp_demo_sku001.md` |
| SKU is the tenant's own stable identifier | `demo_sku001` (verbatim, not re-cased) |

## Size Budget
`max_bytes: 6144` (from `.cex/kinds_meta.json`, REAL value). Field-group tables
+ provenance/conflict trails = ~3-4KB typical. Table format preferred over
inline YAML for the 10 field groups.

## Orchestration Checklist
- Verify the merge->bridge->adapter pipeline topology matches the real dependency graph
- Validate the handoff to `cex_channel_adapter.py` (downstream) is well-formed
- Cross-reference `data_contract`/`validation_schema` (both prerequisites) for boundary correctness
- Test with `python _tools/cex_canonical_product.py --demo` before live dispatch

## Orchestration Pattern
```yaml
topology: verified
handoffs: validated
routing: checked
sequencing: tested
```
```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope canonical-product-builder
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[canonical-product-builder]] | upstream | 0.40 |
| [[bld_memory_canonical_product]] | upstream | 0.33 |
| [[kc_canonical_product]] | upstream | 0.32 |
