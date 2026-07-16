---
kind: tools
id: bld_tools_benchmark
pillar: P04
llm_function: CALL
purpose: Tools available for benchmark production
quality: null
title: "Tools Benchmark"
version: "1.0.0"
author: n03_builder
tags: [benchmark, builder, examples]
tldr: "Golden and anti-examples for benchmark construction, demonstrating ideal structure and common pitfalls."
domain: "benchmark construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [benchmark construction, tools benchmark, benchmark, builder, examples, production tools, data sources, model cards, tool permissions, interim validation
manually]
density_score: 0.90
related:
  - bld_tools_response_format
  - bld_tools_golden_test
  - bld_tools_unit_eval
  - bld_tools_scoring_rubric
  - bld_tools_validation_schema
---

# Tools: benchmark-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing benchmarks | Phase 1 (check duplicates) | CONDITIONAL |
| validate_artifact.py | Validate any artifact kind | Phase 3 | [PLANNED] |
| cex_forge.py | Generate artifact from seeds | Alternative compose | [PLANNED] |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | P07_evals/_schema.yaml | Field definitions for benchmark |
| CEX Examples | P07_evals/examples/ | Existing benchmark artifacts |
| Model Cards | P02_model/examples/ | Performance specs (latency, cost, TPS) |
| SEED_BANK | archetypes/SEED_BANK.yaml | P07_benchmark seeds |
| Anthropic API | https://docs.anthropic.com | Model performance data |
| LiteLLM | https://docs.litellm.ai | Cross-provider latency/cost data |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
Manually check each QUALITY_GATES.md gate against produced artifact.
1. [ ] YAML parses
2. [ ] id matches p07_bm_ prefix
3. [ ] iterations >= 10, warmup >= 1
4. [ ] percentiles include p50 + p95
5. [ ] baseline and target are numeric with same unit
6. [ ] direction is explicit

## Metadata

```yaml
id: bld_tools_benchmark
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-benchmark.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_response_format]] | sibling | 0.58 |
| [[bld_tools_golden_test]] | sibling | 0.56 |
| [[bld_tools_unit_eval]] | sibling | 0.56 |
| [[bld_tools_scoring_rubric]] | sibling | 0.55 |
| [[bld_tools_validation_schema]] | sibling | 0.55 |
