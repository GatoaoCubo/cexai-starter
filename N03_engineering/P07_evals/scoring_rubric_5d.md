---
id: p07_sr_quality_5d_n03
kind: scoring_rubric
8f: F7_govern
pillar: P07
title: 5-Dimension Quality Scoring (5D)
version: 1.0.0
created: 2026-03-30
updated: 2026-03-30
author: builder_agent
domain: meta-construction
quality: null
tags: [scoring-rubric, 5d, quality, dimensions, measurement, govern]
tldr: Every artifact is scored on 5 orthogonal dimensions. Final score = weighted average. Thresholds enforce build/no-build decisions.
when_to_use: "Apply (F7 GOVERN) to score an artifact and decide promote/publish/iterate/reject. Consult for 'what are the 5 dimensions, their weights, and the threshold actions?'"
primary_8f: GOVERN
keywords: [density_score, scope creep, interface contracts, signal(golden), signal(complete), signal(failed)]
density_score: 0.93
related:
  - p06_vs_artifact_output
  - p11_qg_builder_nucleus
  - p07_gt_n03
  - bld_schema_scoring_rubric
---

# 5-Dimension Quality Scoring (5D)

### How to use

```text
8F verb: GOVERN (F7). Score each dimension 1-10, take the weighted Final Score
Calculation, then apply the Threshold Actions (golden/publish/iterate/reject) and
emit the matching signal. Use the Builder-Specific Floors to raise the bar for
N03/meta artifacts. Tune the open knobs below per context:
```

```yaml
weights: {{weights}}              # D1=.25 D2=.20 D3=.25 D4=.15 D5=.15 (must sum to 1.0)
publish_floor: {{publish_floor}} # min Final Score to commit (default 8.0)
golden_floor: {{golden_floor}}   # min Final Score to promote (default 9.5)
context_floor: {{context_floor}} # builder-specific floor (N03 = 8.5)
```

## The 5 Dimensions

| # | Dimension | Weight | What It Measures | 10/10 Looks Like |
|---|-----------|--------|------------------|-------------------|
| D1 | **Structural Integrity** | 25% | Frontmatter, schema compliance, naming, pillar alignment | Perfect frontmatter pass, zero structural issues |
| D2 | **Content Density** | 20% | Signal-to-noise ratio, tables over prose, decision trees | density_score >= 0.90, every line carries meaning |
| D3 | **Actionability** | 25% | Can a builder USE this artifact without additional context? | Self-contained, copy-paste usable, no tribal knowledge |
| D4 | **Boundary Discipline** | 15% | Single kind, single responsibility, no scope creep | Artifact does ONE thing, references others for the rest |
| D5 | **Composability** | 15% | Can this artifact combine with others in a crew/pipeline? | Clean inputs/outputs, follows interface contracts |

## Scoring Scale

Each dimension: 1-10 integer.

| Score | Meaning |
|-------|---------|
| 10 | Exemplary. Reference-quality. |
| 9 | Excellent. Minor polish possible. |
| 8 | Good. Publishable without changes. |
| 7 | Acceptable. Needs iteration. |
| 6 | Weak. Specific flaws identified. |
| 5 | Below standard. Major rework. |
| 1-4 | Reject. Rebuild from scratch. |

## Final Score Calculation

```
final = (D1 * 0.25) + (D2 * 0.20) + (D3 * 0.25) + (D4 * 0.15) + (D5 * 0.15)
```

Example: D1=9, D2=8, D3=9, D4=8, D5=9
  = (9*0.25) + (8*0.20) + (9*0.25) + (8*0.15) + (9*0.15)
  = 2.25 + 1.60 + 2.25 + 1.20 + 1.35
  = 8.65

## Threshold Actions

| Final Score | Tier | Action | Signal |
|-------------|------|--------|--------|
| >= 9.5 | GOLDEN | Promote to reference examples | signal(golden) |
| 8.0 - 9.4 | PUBLISH | Commit to repository | signal(complete) |
| 7.0 - 7.9 | ITERATE | Retry F6-F7 (max 2) | no signal yet |
| < 7.0 | REJECT | Delete draft, restart from F4 | signal(failed) |

## Builder-Specific Floors

| Context | Minimum Score | Rationale |
|---------|--------------|-----------|
| N03 (meta-construction) | 8.5 | Builders build builders. Higher standard. |
| N07 (orchestration) | 8.0 | Dispatch artifacts need reliability. |
| N01-N06 (domain) | 8.0 | Standard publication quality. |
| Grid batch (headless) | 8.0 | Same quality as interactive. No degradation. |

## Dimension Deep Dive

How each dimension is judged in practice:

- **Structural**: automated -- required frontmatter fields typed correctly,
  sections match pillar schema, naming follows kinds_meta, file in the right
  P-directory, size within max_bytes.
- **Density**: heuristic -- table lines / total >= 0.30, code lines / total
  >= 0.15, line length 40-100 chars, zero filler phrases.
- **Actionability**: the "stranger test" -- a builder who has never seen the
  system can USE this in 2 minutes, or the score drops below 7.
- **Boundary**: one artifact = one kind = one pillar; if a knowledge_card starts
  explaining a workflow, split it out.
- **Composability**: clear inputs/outputs, referenceable by others, fit for a
  builder-crew or pipeline composition.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_vs_artifact_output]] | related | 0.26 |
| [[p11_qg_builder_nucleus]] | related | 0.25 |
| [[p07_gt_n03]] | sibling | 0.24 |
| [[bld_schema_scoring_rubric]] | related | 0.20 |
