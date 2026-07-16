---
kind: config
id: bld_config_curriculum_config
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions and constraints for curriculum_config
quality: null
title: "Curriculum Config Builder - Config ISO"
version: "1.0.0"
author: n03_builder
tags: [curriculum_config, builder, config]
tldr: "Production config for curriculum config: naming, paths, and constraints."
domain: "training curriculum"
created: "2026-04-23"
updated: "2026-04-23"
8f: "F1_constrain"
keywords: [training curriculum, and constraints, curriculum_config, builder, config, production rules, naming convention, file paths, size limits, strategy reference]
density_score: 0.85
related:
  - bld_config_synthetic_data_config
  - bld_output_curriculum_config
  - bld_config_dataset_card
  - bld_config_ab_test_config
  - bld_config_tokenizer_config
---
# Config: curriculum_config Production Rules
## Naming Convention
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | p07_cc_{config_slug}.md | p07_cc_domain_adapt_v1.md |
| Builder directory | kebab-case | curriculum-config-builder/ |
| Frontmatter fields | snake_case | difficulty_metric, warmup_fraction |
## File Paths
1. Output: P07_evals/examples/p07_cc_{slug}.md
2. Compiled: P07_evals/compiled/p07_cc_{slug}.yaml
## Size Limits: max 2048B body, density >= 0.85
## Strategy Reference
| Strategy | Difficulty Progression | Data Requirement |
|----------|----------------------|------------------|
| easy_to_hard | Linear or stepped | Difficulty-scored dataset |
| self_paced | Loss-driven | Any dataset |
| competence_based | Gate-driven | Tiered dataset with checkpoints |
| data_mixing | Ratio-driven | Multiple data sources |
## Domain-Specific Constraints
| Constraint | Value |
|-----------|-------|
| Boundary | Training data ordering and adaptive pacing |
| Dependencies | dataset_card, training_method, eval_metric |
| Primary 8F function | F1_constrain |
| Max artifact size | 4096 bytes |
## Edge Cases
| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency dataset_card not found | Warn; proceed with defaults |
## Properties
| Property | Value |
|----------|-------|
| Kind / Pillar | `config` / P09 |
| Pipeline | 8F (F1-F8) |
| Tools | cex_score.py, cex_compile.py, cex_retriever.py |
| Quality / Density | 9.0+ / 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_synthetic_data_config]] | sibling | 0.39 |
| [[bld_output_curriculum_config]] | upstream | 0.39 |
| [[bld_config_dataset_card]] | sibling | 0.36 |
| [[bld_config_ab_test_config]] | sibling | 0.35 |
| [[bld_config_tokenizer_config]] | sibling | 0.34 |
