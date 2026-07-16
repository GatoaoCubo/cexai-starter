---
kind: quality_gate
id: bld_eval_inference_config
pillar: P07
llm_function: GOVERN
purpose: Quality gate for inference_config artifacts
quality: null
title: "Inference Config Builder - Eval ISO"
version: "1.0.0"
author: n03_builder
tags: [inference_config, builder, quality_gate]
tldr: "Quality gate for inference config: validates framework, quantization, and performance targets."
domain: "model inference"
created: "2026-04-23"
updated: "2026-04-23"
8f: "F7_govern"
keywords: [model inference, validates framework, and performance targets, inference_config, builder, quality_gate, eval, quality gate, fail condition, scoring guide]
density_score: 0.88
related:
  - bld_eval_query_optimizer
  - bld_eval_curriculum_config
  - bld_eval_synthetic_data_config
  - bld_eval_tokenizer_config
  - bld_eval_distillation_config
---
## Quality Gate

## HARD Gates

| ID | Check | Fail Condition |
|----|-------|----------------|
| H01 | YAML frontmatter valid | Invalid YAML syntax |
| H02 | ID matches pattern | ID does not match ^p09_ic_[a-z][a-z0-9_]+$ |
| H03 | kind field matches | kind is not 'inference_config' |
| H04 | framework defined | framework field missing or not in enum |
| H05 | quality is null | quality must be null |
| H06 | model_id defined | model_id field missing or empty |
| H07 | quantization defined | quantization field missing or not in enum |

## SOFT Scoring

| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| D1 | Framework config | 0.15 | Framework specified with version and settings |
| D2 | Quantization rationale | 0.15 | Level justified with quality/memory trade-off |
| D3 | Memory budget | 0.15 | VRAM budget calculated and documented |
| D4 | Latency targets | 0.15 | TTFT and throughput with numeric targets |
| D5 | Batching strategy | 0.10 | Strategy explained for use case |
| D6 | Hardware spec | 0.10 | GPU model and fallback documented |
| D7 | Fallback plan | 0.10 | Alternative serving path defined |
| D8 | Documentation | 0.10 | tldr captures key info |

## Actions

| Score | Action |
|-------|--------|
| >=9.5 | GOLDEN |
| >=8.0 | PUBLISH |
| >=7.0 | REVIEW |
| <7.0 | REJECT |

## Validation Checklist

| Check | Method | Automated |
|-------|--------|-----------|
| Frontmatter schema | cex_compile.py --validate | Yes |
| Naming convention | Regex match against p09_ic_{{name}}.md + .yaml | Yes |
| Size limit | Byte count <= 4096 | Yes |
| Density score | Token/byte ratio >= 0.85 | Yes |
| Cross-references valid | Link resolution check | Partial |

## Properties

| Property | Value |
|----------|-------|
| Kind | `eval` |
| Pillar | P07 |
| Domain | inference config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
