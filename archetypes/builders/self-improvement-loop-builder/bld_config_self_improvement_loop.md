---
kind: config
id: bld_config_self_improvement_loop
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for self_improvement_loop production
quality: null
title: "Config Self Improvement Loop"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [self_improvement_loop, builder, config]
tldr: "Production constraints for self improvement loop: naming (p11_sil_{{name}}.md), output paths (P11/), size limit 5120B. Self-improvement loop."
domain: "self_improvement_loop construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for self_improvement_loop production, self_improvement_loop construction, config self improvement loop, output paths, size limit, self-improvement loop, self_improvement_loop, builder, config, naming convention
pattern]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_collaboration_pattern
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_search_strategy
---

## Naming Convention
Pattern: p11_sil_{{name}}.md
Examples: p11_sil_daily_journal.md, p11_sil_weekly_review.md

## Paths
Artifacts: /opt/cex/loop/artifacts/p11_sil_{{name}}
Symlink: /opt/cex/loop/current → latest version

## Limits
max_bytes: 5120
max_turns: 10
effort_level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Self-improvement loop |
| Dependencies | quality_gate, reward_signal |
| Primary 8F function | F7_govern |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency quality_gate not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | self improvement loop construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.50 |
| [[bld_config_collaboration_pattern]] | sibling | 0.50 |
| [[bld_config_ab_test_config]] | sibling | 0.49 |
| [[bld_config_agents_md]] | sibling | 0.49 |
| [[bld_config_search_strategy]] | sibling | 0.48 |
