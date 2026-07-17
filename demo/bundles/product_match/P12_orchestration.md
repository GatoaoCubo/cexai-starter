---
kind: collaboration
id: bld_collaboration_product_match
pillar: P12
llm_function: COLLABORATE
purpose: How product-match-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Product Match"
version: "1.0.0"
author: n03_builder
tags: [product_match, builder, examples]
tldr: "Golden and anti-examples for product_match construction, demonstrating ideal structure and common pitfalls."
domain: "product match construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F8_collaborate"
keywords: [product match construction, collaboration product match, product_match, builder, examples, "### crew: sourcing audit", "### crew: golden-record merge", my role, crew compositions, catalog audit]
density_score: 0.90
related:
  - product-match-builder
  - opportunity-matrix-builder
---
# Collaboration: product-match-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what composite key joins a supplier item to a
marketplace listing, and what cadastral divergence does the audit surface along the way?"
I do not implement reverse-image search or embeddings. I do not rank buy-side opportunities.
I do not assess channel publish-readiness. I specify a record-linkage + catalog-audit contract
so a dashboard run (N03) and other generators (e.g. N06's sourcing audit) can compose against it.
NOTE: at RUNTIME, the `product_match` capability generation is fully owned by the deterministic
Python generator (`@register("product_match")` in `_tools/capability_generators/product_match.py`)
-- the F2 BECOME step is deliberately skipped at runtime ("the structured-generator seam OWNS the
output", `_tools/cex_run_capability.py:129,141`). I author/evolve the KIND's .md spec artifact
(the CONTRACT documentation) that the generator is held to; I do not replace or run instead of it.
## Crew Compositions
### Crew: "Sourcing Audit"
```
  1. product-match-builder      -> "supplier x listing match + catalog audit spec"
  2. opportunity-matrix-builder -> "buy-side cost x demand join that consumes the audit flags"
  3. data-contract-builder      -> "producer-consumer schema for the `items` input list"
```
### Crew: "Golden-Record Merge" (TUDAO / marketplace_listing)
```
  1. product-match-builder -> "composite join key spec (photo+dimension+supplier_code)"
  2. output-validator-builder -> "validates the 4 frozen output sections post-LLM"
  3. vision-tool-builder    -> "the reverse-image/embedding primitive product_match would wrap"
```
### Crew: "Catalog Quality Gate"
```
  1. product-match-builder -> "text-vs-photo divergence + low-res photo audit spec"
  2. quality-gate-builder  -> "match_confiavel gate definition + blocker vocabulary"
  3. scoring-rubric-builder -> "score formula (offline penalty, no-photo penalty)"
```
## Handoff Protocol
### I Receive
- seeds: the supplier-item shape being matched (code, photo_uri, dimension, desc), the target
  marketplace, any match_engine preference, confidence-floor requirements
### I Produce
- product_match artifact (.md + .yaml frontmatter)
- committed to: `N03_engineering/P04_tools/examples/p04_pm_{name}.md`
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with specific gate failures
## Builders I Depend On
`vision_tool` (P04, the raw visual primitive `match_engine=reverse_image` would eventually wrap --
NOT yet implemented; `data_contract` (P06, the `items` producer-consumer schema); `output_validator`
(P05, validates the 4 frozen sections) -- all three are DECLARED taxonomy dependencies
(`.cex/kinds_meta.json` `depends_on`), not Python imports (verified: product_match.py imports
none of them).
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| opportunity-matrix-builder | Section 6 "Match / auditoria" of `opportunity_matrix` surfaces MY engine's result (per `bld_model_opportunity_matrix.md` Crew Role: "does NOT perform visual product matching... that is product_match") |
| marketplace-listing-builder | The TUDAO golden-record merge shares my `_normalize_join_key` + `_audit_text_vs_photo` helpers (per the ADR's stated intent; not yet wired as of this read) |
| agent-builder | Agents that run a sourcing/catalog-audit workflow invoke `product_match` as a step |
## Boundary Enforcement
| Request | My response |
|---------|-------------|
| "Analyze this one product photo for labels/objects" | Redirect to vision-tool-builder (no join target = vision_tool, not product_match) |
| "Rank my suppliers by cost vs market demand" | Redirect to opportunity-matrix-builder (P11/N06 buy-side economics) |
| "Is this listing ready to publish on Mercado Livre" | Redirect to marketplace-listing-builder (P05/N06 channel readiness) |
| "Match these two products by EAN/barcode" | Explain the structural exclusion (every reseller recodes EAN/GTIN/barcode); offer the composite photo+dimension+supplier_code key instead |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[product-match-builder]] | upstream | 0.41 |
| [[bld_orchestration_vision_tool]] | sibling | 0.35 |
| [[bld_prompt_product_match]] | upstream | 0.32 |
| [[opportunity-matrix-builder]] | sibling | 0.30 |
