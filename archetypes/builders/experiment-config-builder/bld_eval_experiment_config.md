---
kind: quality_gate
id: p11_qg_experiment_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of experiment_config artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: experiment_config"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, experiment-config, ab-test, variants, metrics, P11]
tldr: "Gates for experiment_config: validates variant structure, traffic splits, metric definitions, and statistical parameter completeness."
domain: "experiment_config -- A/B test and prompt experiment configurations with variants, metrics, and traffic splits"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [experiment_config -- a, and traffic splits, gates for experiment_config, validates variant structure, traffic splits, metric definitions, and statistical parameter completeness]
density_score: 0.92
related:
  - bld_schema_experiment_config
---
## Quality Gate

# Gate: experiment_config
## Definition
| Field | Value |
|-------|-------|
| metric | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator | AND (all HARD) + weighted_sum (SOFT) |
| scope | All artifacts where `kind: experiment_config` |

## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID | Check | Failure message |
|----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p09_ec_[a-z][a-z0-9_]+$` | "ID fails experiment_config namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"experiment_config"` | "Kind is not 'experiment_config'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, hypothesis, variants, primary_metric, traffic_split, status, version, created, author, tags | "Missing required field(s)" |

## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Hypothesis quality | 1.0 | Falsifiable, specifies variant change + expected outcome + metric |
| Variant definition completeness | 1.0 | Each variant has name, type (control/treatment), description, key changes |
| Guardrail metric coverage | 1.0 | Non-empty guardrail list; metrics cover latency, error rate, or critical features |
| Statistical rigor | 1.0 | significance_threshold, MDE, and sample_size_target all specified |
| Traffic split rationale | 0.5 | Equal split or documented reason for unequal allocation |
| Segment accuracy | 0.5 | Segment field accurately scopes who participates |
Weight sum: 1.0+1.0+1.0+1.0+0.5+0.5+1.0+1.0+0.5+1.0+0.5+1.0 = 10.0 (100%)

## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool as golden exemplar |
| >= 8.0 | PUBLISH | Publish to pool |
| >= 7.0 | REVIEW | Flag for human review before publish |
| < 7.0 | REJECT | Return to author with failure report |

## Bypass
| Field | Value |
|-------|-------|
| conditions | Early-stage experiment sketches where MDE is not yet calculable (status: draft only) |
| approver | Experiment owner approval required (written); H01-H09 gates never bypassed |

## Examples

# Examples: experiment-config-builder
## Golden Example
INPUT: "A/B test two prompt styles for the code review agent -- current verbose prompt vs. concise prompt"
OUTPUT:
```yaml
id: p09_ec_code_review_prompt_style
kind: experiment_config
pillar: P09
version: "1.0.0"
created: "2026-04-13"
updated: "2026-04-13"
author: "builder_agent"
hypothesis: "If code review prompt is made concise (<= 200 tokens) then review_acceptance_rate increases by >= 3pct vs verbose baseline"
```
## Overview
Testing whether a concise code review prompt (under 200 tokens) improves review acceptance
rate compared to the current verbose prompt (avg 420 tokens).
Decision enabled: adopt concise prompt as default or retain verbose baseline.
## Variants
| Variant | Type | Description | Key Changes |
|---------|------|-------------|-------------|
| control | control | Current verbose prompt (avg 420 tokens) | Baseline -- no changes |
| concise_prompt | treatment | Compressed prompt (<= 200 tokens) | Removed preamble, inline examples replaced with references |
## Traffic Split
| Variant | Allocation | Segment |
|---------|-----------|---------|
| control | 50% | all |
| concise_prompt | 50% | all |
Allocation total: 100%. No hold-out; all traffic participates.
## Metrics
### Primary Metric
| Metric | Direction | Winning Threshold |
|--------|-----------|-------------------|
| review_acceptance_rate | higher is better | +3pct vs control |
### Guardrail Metrics
| Metric | Acceptable Limit | Action if Breached |
|--------|-----------------|-------------------|
| critical_issue_detection_rate | >= 95pct of baseline | pause experiment |
| p99_latency_ms | <= 120pct of baseline | pause experiment |
## Statistical Parameters
| Parameter | Value | Notes |
|-----------|-------|-------|
| Significance threshold | 0.05 | alpha = 5pct |
| Min detectable effect | +3pct relative | baseline ~68pct acceptance |
| Sample size (per variant) | 1,200 | 80pct power, two-tailed z-test |
| Duration | 14 days | ~170 reviews/day estimated |
## Lifecycle
| Field | Value |
|-------|-------|
| Status | draft |
| Created | 2026-04-13 |
| Launch target | 2026-04-20 |
| Conclusion criteria | p < 0.05 AND min 14 days runtime |
| Decision owner | N03 builder team |

WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p09_ec_ pattern (H02 pass)
- kind: experiment_config (H04 pass)
- variants list starts with "control" (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` populated (3-15), 1+ upstream, 1+ downstream
- Penalty: -0.3 if empty

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_experiment_config]] | upstream | 0.31 |
