---
kind: quality_gate
id: p11_qg_benchmark
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of benchmark artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: benchmark"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "benchmark"
  - "P11"
  - "P07"
  - "governance"
  - "performance"
  - "measurement"
tldr: "Gates for benchmark artifacts — quantitative performance measurements with methodology and reproducibility."
domain: benchmark
created: "2026-03-27"
updated: "2026-07-04"
8f: "F7_govern"
keywords:
  - "gates for benchmark artifacts"
  - "quality-gate"
  - "benchmark"
  - "governance"
  - "performance"
  - "measurement"
  - "^p07_bm_[a-z][a-z0-9_]+$"
density_score: 0.91
related:
  - benchmark-builder
  - bld_architecture_benchmark
  - bld_schema_benchmark
---
## Quality Gate

# Gate: benchmark
## Definition
| Field     | Value                                                    |
|-----------|----------------------------------------------------------|
| metric    | measurement rigor + reproducibility completeness         |
| threshold | 8.0                                                      |
| operator  | >=                                                       |
| scope     | all benchmark artifacts (P07)                            |
## HARD Gates
All must pass. Failure on any = final score 0. Numbering matches
`.claude/rules/8f-reasoning.md` (canonical) and `cex_8f_runner.py` (code) exactly —
renumbered 2026-07-04 (R-259) to fold the id/filename-stem check into H02 (both are
id-validity concerns) instead of inserting it as an extra gate that shifted everything
else out of sync with the canonical list.
| Gate | Check | Why |
|------|-------|-----|
| H01 | YAML frontmatter parses valid YAML | Broken YAML = benchmark unreachable |
| H02 | id matches `^p07_bm_[a-z][a-z0-9_]+$` AND id == filename stem | Namespace compliance; brain search relies on this |
| H03 | kind == "benchmark" | Type integrity |
| H04 | quality == null | Never self-score |
| H05 | All 9 enforced fields present (id, kind, pillar, version, quality, tags, title, created, tldr) — see `bld_schema_benchmark.md` Recommended table for the 12 soft-tier fields | Completeness |
| H06 | body <= 4096 bytes (max_bytes) | Size ceiling |
## SOFT Scoring
| Gate | Check | Weight |
|------|-------|--------|
| S01 | tldr <= 160 chars, non-empty | 1.0 |
| S02 | tags is list, len >= 3, includes "benchmark" | 0.5 |
| S03 | direction in [lower_is_better, higher_is_better, informational] — explicit | 1.0 |
| S04 | baseline and target are numeric, same unit implied | 1.0 |
| S05 | Benchmark Overview section with metric rationale | 1.0 |
| S06 | Methodology section covers iterations, warmup, and protocol | 1.0 |
Weights sum: 10.0. Normalize: divide each by 10.0 before scoring.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — pool as canonical performance baseline |
| >= 8.0 | PUBLISH — active performance contract |
| >= 7.0 | REVIEW — add missing percentiles or environment detail |
| < 7.0  | REJECT — methodology incomplete or unit undefined |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Production incident requiring immediate performance baseline capture |
| approver | p07-chief |
| audit_trail | Log in records/audits/ with incident reference and timestamp |
| expiry | 48h — full methodology required before expiry |
| never_bypass | H01 (YAML), H05 (quality null) |

## Examples

# Examples: benchmark-builder
## Golden Example
INPUT: "Create benchmark de latency TTFT comparando Sonnet 4 vs Haiku 4.5"
OUTPUT:
```yaml
id: p07_bm_ttft_sonnet4_vs_haiku45
kind: benchmark
pillar: P07
title: "Benchmark: TTFT Sonnet 4 vs Haiku 4.5"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
metric: "time_to_first_token"
unit: "ms"
direction: "lower_is_better"
baseline: 850
target: 400
iterations: 100
warmup: 10
percentiles: [50, 75, 95, 99]
environment: "Railway PRO, us-east-1, Python 3.12, httpx 0.27, 2 vCPU / 4GB RAM"
domain: "llm_inference"
quality: 8.9
tags: [benchmark, ttft, latency, model-comparison, sonnet, haiku]
tldr: "TTFT benchmark: Sonnet 4 (850ms baseline) vs Haiku 4.5 (target 400ms), 100 iterations, p50/p95/p99 on Railway PRO"
comparison_subjects: [claude-sonnet-4-6, claude-haiku-4-5-20251001]
statistical_test: "Mann-Whitney U"
confidence_interval: 0.95
density_score: 0.91
linked_artifacts:
  primary: "p02_mc_anthropic_sonnet_4"
  related: [p02_mc_anthropic_haiku_45]
## Benchmark Overview
Measures Time To First Token (TTFT) for Claude Sonnet 4 vs Haiku 4.5 on identical prompts.
TTFT directly impacts perceived responsiveness in streaming UIs.
Business impact: Haiku 4.5 at <400ms enables sub-second perceived start for chat interfaces.
## Methodology
- **Iterations**: 100 runs per model
- **Warmup**: 10 runs discarded (connection pool, TLS handshake)
- **Protocol**: Send identical 500-token prompt via Anthropic API, measure time from request sent to first SSE chunk received
- **Statistical test**: Mann-Whitney U at 95% confidence (non-parametric, no normality assumption)
## Metrics
| Metric | Unit | Direction | Baseline (Sonnet 4) | Target (Haiku 4.5) |
|--------|------|-----------|---------------------|---------------------|
| TTFT | ms | lower_is_better | 850 | 400 |
| TTFT p95 | ms | lower_is_better | 1200 | 600 |
| TTFT p99 | ms | lower_is_better | 1800 | 900 |
## Environment
- **Hardware**: Railway PRO, us-east-1, 2 vCPU / 4GB RAM
- **Software**: Python 3.12, httpx 0.27, anthropic SDK 0.52
- **Config**: max_tokens=100, temperature=0, no system prompt, streaming=true
- **Date**: 2026-03-26
## Results Template
| Percentile | Sonnet 4 | Haiku 4.5 | Delta (ms) | Delta (%) |
|------------|----------|-----------|------------|-----------|
| p50 | — | — | — | — |
| p75 | — | — | — | — |
| p95 | — | — | — | — |
| p99 | — | — | — | — |
## Anti-Example
INPUT: "Benchmark de performance"
BAD OUTPUT:
```yaml
id: perf_bench
kind: benchmark
title: "Performance Test"
iterations: 3
warmup: 0
percentiles: [50]
baseline: "fast"
target: "faster"
quality: 8.5
tags: benchmark

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` populated (3-15), 1+ upstream, 1+ downstream
- Penalty: -0.3 if empty

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[benchmark-builder]] | upstream | 0.45 |
| [[bld_output_template_benchmark]] | upstream | 0.44 |
| [[bld_instruction_benchmark]] | upstream | 0.42 |
| [[bld_architecture_benchmark]] | upstream | 0.39 |
| [[bld_schema_benchmark]] | upstream | 0.37 |
