---
id: bld_context_sources_canonical_product
kind: rag_source
pillar: P10
llm_function: CONSTRAIN
version: 1.0.0
quality: null
tags: [canonical_product, context, rag]
title: "Context Sources: canonical_product"
author: builder
tldr: "Canonical Product memory: mandatory + optional context sources, naming, and anti-sources"
8f: "F3_inject"
keywords: [context sources, canonical product memory, naming conventions, output paths, canonical_product, context, mandatory sources, optional sources, search queries]
density_score: 0.88
created: "2026-07-03"
updated: "2026-07-03"
related:
  - bld_config_validation_schema
  - bld_tools_canonical_product
  - kc_canonical_product
  - marketplace-listing-builder
---
# Context Sources: canonical_product
## Mandatory Sources (load at F3 INJECT)
| Source | Path | Why |
|--------|------|-----|
| Kind KC | `N00_genesis/P01_knowledge/library/kind/kc_canonical_product.md` | Definition + boundary + pipeline |
| Schema | `archetypes/builders/canonical-product-builder/bld_schema_canonical_product.md` | 42 required fields |
| JSON Schema contract | `docs/schema/contracts/canonical_product.schema.json` | Machine-checkable mirror |
| Tool | `_tools/cex_canonical_product.py` | The real bridge implementation |

## Optional Sources (load if relevant)
| Source | Path | When to Load |
|--------|------|--------------|
| data_contract KC | `N00_genesis/P01_knowledge/library/kind/kc_data_contract.md` | Understanding the `depends_on` schema+SLA concept |
| validation_schema KC | `N00_genesis/P01_knowledge/library/kind/kc_validation_schema.md` | Understanding the `depends_on` output-check concept |
| Existing instances | `{nucleus}/P06_*/p06_cp_*.md` | Consistency with existing canonical records |
| Test fixture | `tests/fixtures/corpus_50.json` | 50-product, >=2-source real corpus used by the acceptance suite |

## Search Queries for Retrieval
- "channel-neutral product golden record provenance conflicts"
- "merge product catalog data multiple sources single source of truth"
- "structural law specs separate from prose ecommerce"
- "CanonicalProduct field union coverage"

## Anti-Sources (do NOT confuse with)
- `marketplace_listing` (per-channel PROJECTION, not the union)
- `product_ad` (rendered buyer page, unregistered capability-layer kind)
- Raw per-source catalog rows (pre-merge, no provenance/conflict trail yet)

## Configuration Checklist
- Verify all mandatory sources loaded before F6 PRODUCE
- Validate JSON Schema contract path resolves (`docs/schema/contracts/canonical_product.schema.json`)
- Cross-reference with `data_contract`/`validation_schema` KCs to avoid boundary confusion
- Test config loading against a real fixture (`tests/fixtures/corpus_50.json`) before committing

## Validation
```yaml
fields_present: true
types_valid: true
structural_law_checked: true
cross_refs_verified: true
```
```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope canonical-product-builder
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_validation_schema]] | sibling | 0.48 |
| [[bld_tools_canonical_product]] | upstream | 0.42 |
| [[kc_canonical_product]] | upstream | 0.41 |
| [[marketplace-listing-builder]] | related | 0.35 |
