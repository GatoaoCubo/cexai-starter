---
kind: schema
id: bld_schema_benchmark
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema — SINGLE SOURCE OF TRUTH for benchmark
pattern: TEMPLATE derives from this. CONFIG restricts this.
quality: null
title: "Schema Benchmark"
version: "1.0.0"
author: n03_builder
tags:
  - "benchmark"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for benchmark construction, demonstrating ideal structure and common pitfalls."
domain: "benchmark construction"
created: "2026-04-07"
updated: "2026-07-04"
8f: "F1_constrain"
keywords:
  - "formal schema"
  - "benchmark construction"
  - "schema benchmark"
  - "benchmark"
  - "builder"
  - "examples"
  - "^p07_bm_[a-z][a-z0-9_]+$"
  - "## benchmark overview"
  - "## methodology"
  - "## metrics"
density_score: 0.90
related:
  - bld_schema_usage_report
  - bld_schema_unit_eval
  - bld_schema_smoke_eval
  - bld_schema_reranker_config
  - bld_schema_golden_test
---

# Schema: benchmark
## Frontmatter Fields

> **Tiering policy (R-259, 2026-07-04):** fields below are split ENFORCED (H05 gates on
> these -- see `bld_eval_benchmark.md` H05) vs RECOMMENDED (documented, encouraged, not
> gated). Verdict derived from a 27-artifact population audit + confirmed structured-data
> consumer check: population >= 85% -> ENFORCED; below 85% -> RECOMMENDED unless a confirmed
> tool consumer overrides (found once: `tldr`, read by `cex_retriever.py`). Full evidence:
> `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md` Section 3.

### Required (ENFORCED — H05 gates on these 9)
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p07_bm_{metric_slug}) | YES | — | Namespace compliance |
| kind | literal "benchmark" | YES | — | Type integrity |
| pillar | literal "P07" | YES | — | Pillar assignment |
| title | string "Benchmark: {name}" | YES | — | Human label |
| version | semver string | YES | "1.0.0" | Versioning |
| created | date YYYY-MM-DD | YES | — | Creation date |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | — | Searchability |
| tldr | string <= 160ch | YES | — | Dense summary |
### Recommended (documented, encouraged, NOT H05-gated)
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| comparison_subjects | list[string] | REC | — | What entities are compared |
| statistical_test | string | REC | — | Significance test (t-test, Mann-Whitney) |
| confidence_interval | float 0.0-1.0 | REC | 0.95 | Confidence level |
| density_score | float 0.80-1.00 | REC | — | Content density |
| linked_artifacts | object {primary, related} | REC | — | Cross-references |
| updated | date YYYY-MM-DD | REC | — | Last update |
| author | string | REC | — | Producer identity |
| metric | string | REC | — | What is being measured (e.g., latency, throughput, cost) |
| unit | string | REC | — | Measurement unit (ms, tokens/s, USD, req/s) |
| direction | enum: lower_is_better, higher_is_better, informational | REC | — | Optimization direction. `informational` = disclosed non-enum value for count/audit metrics where neither direction is honest (e.g. an incident-catch count) |
| baseline | number | REC | — | Current measured value |
| target | number | REC | — | Goal value |
| iterations | integer >= 10 | REC | — | Number of measurement runs |
| warmup | integer >= 1 | REC | — | Warmup runs before measurement |
| percentiles | list[integer] | REC | [50, 95, 99] | Which percentiles to report |
| environment | string | REC | — | Hardware/software description |
| domain | string | REC | — | Domain this benchmark covers |
## ID Pattern
Regex: `^p07_bm_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem.

> **Status: LIVE-ENFORCED for new 8F builds (corrected 2026-07-04 -- the first
> draft said dormant; judge-refuted by execution, N07-reproduced).** H02 in
> `_tools/cex_8f_runner.py` extracts the backtick-labeled Regex line in this
> section (extraction at ~503-511) and the gate fires on every 8F run of this
> kind (`! H02: id '' does not match /^p07_bm_.../` live repro). The
> `_schema.yaml` `id_pattern` lane stays unpopulated/dormant, but that does not
> idle the gate. CONSEQUENCE: this regex binds every NEW benchmark build
> today, while 9/27 (33%) of the EXISTING corpus predates the convention and
> would fail a retroactive check -- the dedicated id-rename sweep (register
> R-263) closes that gap. Full evidence: `.claude/rules/8f-reasoning.md` H02
> note; `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md` Section 1.

## Body Structure (required sections)
1. `## Benchmark Overview` — what is measured, why, and business impact
2. `## Methodology` — how the benchmark runs (iterations, warmup, environment)
3. `## Metrics` — table: metric, unit, baseline, target, direction
4. `## Environment` — hardware, software, configuration for reproducibility
5. `## Results Template` — percentile table structure for recording results
## Constraints
- max_bytes: 4096 (body only)
- naming: p07_bm_{metric_slug}.md + .yaml
- id == filename stem
- iterations MUST be >= 10
- warmup MUST be >= 1
- percentiles MUST include at least p50 and p95
- baseline and target MUST use same unit
- direction MUST be explicit (no implicit assumptions)
- quality: null always

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_usage_report]] | sibling | 0.61 |
| [[bld_schema_unit_eval]] | sibling | 0.60 |
| [[bld_schema_smoke_eval]] | sibling | 0.60 |
| [[bld_schema_reranker_config]] | sibling | 0.59 |
| [[bld_schema_golden_test]] | sibling | 0.59 |
