---
kind: config
id: bld_config_usage_report
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for usage_report production
quality: null
title: "Config Usage Report"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [usage_report, builder, config]
tldr: "Production constraints for usage report: naming (p07_ur_{{name}}.yaml), output paths (P07/), size limit 3072B. Usage analytics spec."
domain: "usage_report construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for usage_report production, usage_report construction, config usage report, output paths, size limit, usage analytics spec, usage_report, builder, config, p07_ur_<report_name>.yaml]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_usage_quota
  - bld_config_api_reference
  - bld_config_collaboration_pattern
  - bld_config_agents_md
---

## Naming Convention
Pattern: `p07_ur_<report_name>.yaml`
Examples:
- `p07_ur_monthly.yaml`
- `p07_ur_q4.yaml`

## Paths
- Artifacts: `/artifacts/reports/usage/`
- Raw data: `/artifacts/reports/usage/raw/`
- Processed: `/artifacts/reports/usage/processed/`
- Logs: `/artifacts/reports/usage/logs/`

## Limits
- max_bytes: 3072
- max_turns: 5
- effort_level: medium

## Hooks
- pre_build: null
- post_build: null
- on_error: null
- on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Usage analytics spec |
| Dependencies | eval_metric, knowledge_card |
| Primary 8F function | F7_govern |
| Max artifact size | 3072 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 3072 bytes | Trim prose sections; preserve tables |
| Dependency eval_metric not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | usage report construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_ab_test_config]] | sibling | 0.48 |
| [[bld_config_usage_quota]] | sibling | 0.47 |
| [[bld_config_api_reference]] | sibling | 0.46 |
| [[bld_config_collaboration_pattern]] | sibling | 0.45 |
| [[bld_config_agents_md]] | sibling | 0.44 |
