---
id: p11_fb_canonical_product
kind: builder_default
pillar: P11
title: "Feedback: Canonical Product"
domain: canonical_product
version: 1.0.0
quality: null
tags: [feedback, anti-patterns, P11, canonical_product]
8f: "F7_govern"
keywords: [canonical product, never rules, failure modes, step correction, feedback, anti-patterns, canonical_product, common failure modes, failure mode, correction protocol]
tldr: "Anti-patterns and correction protocol for canonical_product builders. NEVER rules + failure modes + correction protocol."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-07-03"
updated: "2026-07-03"
related:
  - kc_canonical_product
  - canonical-product-builder
---
# Feedback: Canonical Product

## Anti-Patterns (NEVER do)

| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign a quality score to own output | H04 |
| No fabrication | Never invent a field value absent from every source | H05 |
| No structural-law breach | Never bury a structured value verbatim in prose | H07 |
| No silent conflict resolution | Never average/overwrite a cross-source disagreement | S03 |
| No frontmatter omission | Every artifact starts with valid YAML frontmatter | H01 |
| No boundary confusion | Never use canonical_product for a per-channel projection or a rendered page | H03 |

## Common Failure Modes

| Failure Mode | Signal | Fix |
|-------------|--------|-----|
| Missing CANONICAL_FIELDS key | Fewer than 42 keys present | Re-read `bld_schema_canonical_product.md`, add all keys (null allowed) |
| Prose contains a duplicated bullet | A structural-law violation is flagged | Move the value out of prose; keep in the structured field only |
| Provenance missing for a populated field | `provenance_coverage()` ratio low | Carry `_merge_provenance` through; do not drop it during formatting |
| Conflated with marketplace_listing | Content describes a single channel's payload, not the union | Re-derive from the golden record via `canonical_from_merged()` |

## Correction Protocol

| Step | Action | Gate |
|------|--------|------|
| 1 | Identify which H01-H10 gate failed | F7 |
| 2 | Return to F6 PRODUCE with the explicit fix (e.g. "re-add missing field X") | F6 |
| 3 | Re-run F7 GOVERN, including `validate_against_schema()`-equivalent checks | F7 |
| 4 | Max 2 retries before escalating to N07 | F8 |

## Key Behaviors

- Builder MUST load all 12 ISOs before producing any artifact
- Builder MUST run F7 GOVERN (HARD gates H01-H10) before saving output
- Builder MUST compile output via `cex_compile.py` after saving (F8 COLLABORATE)
- Builder MUST signal completion with quality score to N07 orchestrator
- Builder MUST NOT self-score: `quality` field is always null in own output

## Quality Thresholds

| Dimension | Weight | Target | Gate |
|-----------|--------|--------|------|
| Structural completeness (42 fields) | 30% | >= 8.0 | H05 |
| Structural-law compliance | 30% | >= 8.0 | H07 |
| Provenance + conflict fidelity | 40% | >= 8.5 | S01/S03 |
| Density score | -- | >= 0.85 | S05 |

## Gate Check

```bash
python _tools/cex_canonical_product.py --self-test
python _tools/cex_score.py {FILE} --layer structural
```
```yaml
structural: 8.5+
rubric: 7.5+
average: 8.0+
gates_passed: 10/10
density: 0.85+
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_canonical_product]] | upstream | 0.42 |
| [[canonical-product-builder]] | upstream | 0.40 |
