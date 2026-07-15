---
kind: tools
id: bld_tools_eval_metric
pillar: P04
llm_function: CALL
purpose: Tools available for eval_metric production
quality: null
title: "Tools Eval Metric"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [eval_metric, builder, tools]
tldr: "Tools available for eval_metric production"
domain: "eval_metric construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [eval_metric construction, tools eval metric, eval_metric, builder, tools, production tools, validation tools, external references, related artifacts, tools tool]
density_score: 0.85
related:
  - bld_tools_benchmark_suite
  - bld_tools_memory_benchmark
  - bld_tools_rbac_policy
  - bld_tools_churn_prevention_playbook
  - bld_tools_competitive_matrix
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile eval_metric artifact after save | F8 COLLABORATE |
| cex_score.py | Score artifact against quality gate (--apply flag) | F7 GOVERN |
| cex_retriever.py | Find similar eval_metric artifacts for template reuse | F3 INJECT |
| cex_doctor.py | Validate builder health and ISO completeness | F7 GOVERN |
| cex_wave_validator.py | Run schema + frontmatter validation on builder ISOs | Pre-commit |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| python -m pytest | Run unit tests for eval_metric artifacts | CI gate |
| python _tools/cex_hooks.py pre-commit | Pre-commit hook: ASCII check + frontmatter | Before git add |

## External References
- evaluate (huggingface.co/docs/evaluate): Standard NLP metric library (BLEU, ROUGE, BERTScore)
- scikit-learn metrics (sklearn.metrics): F1, precision, recall, ROC-AUC
- sacrebleu: Reproducible BLEU scoring with standardized tokenization

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_tools_benchmark_suite | sibling | 0.43 |
| bld_tools_memory_benchmark | sibling | 0.39 |
| [[bld_tools_rbac_policy]] | sibling | 0.35 |
| bld_tools_churn_prevention_playbook | sibling | 0.34 |
| [[bld_tools_competitive_matrix]] | sibling | 0.34 |
