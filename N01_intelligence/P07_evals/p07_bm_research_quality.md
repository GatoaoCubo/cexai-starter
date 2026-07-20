---
id: p07_bm_research_quality
kind: benchmark
pillar: P07
nucleus: n01
title: "Benchmark -- N01 Research Output Quality"
version: 1.0.0
created: 2026-04-07
updated: 2026-04-07
author: n01_intelligence
domain: research-quality-measurement
target_system: N01 Intelligence research pipeline
quality: null
tags: [benchmark, research, quality, n01, metrics, evaluation]
tldr: "Quantitative benchmark for N01 research quality -- measures source density, triangulation rate, freshness compliance, output density, and pipeline throughput across research deliverables."
keywords: [triangulation rate, freshness compliance, output density score, schema compliance, source density]
density_score: 0.94
related:
  - p11_qg_research_n01
  - p06_td_n01
  - p03_ch_research_pipeline_n01
  - kc_research_methods
---

## Setup

### Environment

| Component | Requirement |
|-----------|-------------|
| Python | >= 3.11 |
| CEX SDK | `cex_score.py`, `cex_compile.py`, `cex_retriever.py` operational |
| Corpus | N01_intelligence/P05_output/ contains >= 10 research outputs |
| Quality gate | `p11_qg_research_n01.md` loaded |
| Type schema | `p06_td_n01.md` loaded |

### Fixtures

- Sample research queries: 20 predefined queries covering all output types (competitive grid, SWOT, market snapshot, trend report, benchmark report, executive summary)
- Expected source counts per query type (minimum triangulation targets)
- Known-good reference outputs for quality floor comparison

## Methodology

| Parameter | Value |
|-----------|-------|
| **Iterations** | 10 (run each query type at least 10 times) |
| **Warmup runs** | 1 (first run excluded from statistics) |
| **Percentiles** | p50, p95, p99 |
| **Significance threshold** | p < 0.05 (non-parametric test vs baseline) |
| **Measurement protocol** | Automated scoring via `cex_score.py --apply` + manual spot-check on 20% sample |

## Metrics

| Metric | Unit | Baseline | Target | Direction |
|--------|------|----------|--------|-----------|
| **Source density** | sources/claim | 1.5 | 3.0 | higher_is_better |
| **Triangulation rate** | % claims with 3+ sources | 45% | 80% | higher_is_better |
| **Freshness compliance** | % sources within freshness window | 70% | 90% | higher_is_better |
| **Output density score** | density (0.0-1.0) | 0.78 | 0.90 | higher_is_better |
| **Quality score (peer-reviewed)** | quality (0.0-10.0) | 7.8 | 9.0 | higher_is_better |
| **Pipeline latency** | minutes per research brief | 45 | 30 | lower_is_better |
| **Factual error rate** | errors per output | 1.2 | 0.1 | lower_is_better |
| **Schema compliance** | % outputs passing schema contracts | 85% | 100% | higher_is_better |

## Execution

```bash
# Run full benchmark suite
python _tools/cex_score.py --benchmark N01_intelligence/P05_output/ \
  --rubric N01_intelligence/P07_evals/scoring_rubric_intelligence.md \
  --iterations 10 \
  --output N01_intelligence/P07_evals/benchmark_results.yaml

# Run single metric: source density
python -c "
from pathlib import Path
import re
outputs = list(Path('N01_intelligence/P05_output').glob('*.md'))
for f in outputs:
    content = f.read_text(encoding='utf-8')
    sources = len(re.findall(r'https?://|Source:|\\[\\d+\\]|\\(\\d{4}\\)', content))
    claims = len(re.findall(r'\\|.*\\|.*\\||^- |^\\d+\\.', content, re.MULTILINE))
    density = sources / max(claims, 1)
    print(f'{f.name}: {sources} sources / {claims} claims = {density:.2f} density')
"
```

## Results Template

| Metric | p50 | p95 | p99 | vs Baseline | Pass? |
|--------|-----|-----|-----|-------------|-------|
| Source density | ___ | ___ | ___ | ___ | [ ] |
| Triangulation rate | ___ | ___ | ___ | ___ | [ ] |
| Freshness compliance | ___ | ___ | ___ | ___ | [ ] |
| Output density score | ___ | ___ | ___ | ___ | [ ] |
| Quality score | ___ | ___ | ___ | ___ | [ ] |
| Pipeline latency (min) | ___ | ___ | ___ | ___ | [ ] |
| Factual error rate | ___ | ___ | ___ | ___ | [ ] |
| Schema compliance | ___ | ___ | ___ | ___ | [ ] |

## Comparison to Operations Benchmarks

| Dimension | N01 Research Benchmark | N05 Operations Benchmark |
|-----------|----------------------|-------------------------|
| What's measured | Research output quality | Infrastructure performance |
| Key metric | Source density (sources/claim) | Deploy latency (seconds) |
| Data source | Research outputs + schema contracts | Logs + health endpoints |
| Iteration count | 10 | 50 (infra needs more samples) |
| Human review | 20% spot-check | Automated only |
| Improvement signal | More sources = better research | Lower latency = better ops |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_qg_research_n01]] | related | 0.38 |
| [[p06_td_n01]] | upstream | 0.30 |
| [[p03_ch_research_pipeline_n01]] | upstream | 0.28 |
| [[kc_research_methods]] | upstream | 0.22 |
