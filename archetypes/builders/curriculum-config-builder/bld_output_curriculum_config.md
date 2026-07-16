---
kind: output_template
id: bld_output_curriculum_config
pillar: P05
llm_function: PRODUCE
purpose: Template for producing a curriculum_config artifact
quality: null
title: "Curriculum Config Builder - Output ISO"
version: "1.0.0"
author: n03_builder
tags:
  - "curriculum_config"
  - "builder"
  - "output"
tldr: "Output template for curriculum config: frontmatter field guide, required body sections, filled example, and quality gate checklist for training data ordering, difficulty scheduling, and adaptive pacing configuration."
domain: "training curriculum"
created: "2026-04-23"
updated: "2026-04-23"
8f: "F6_produce"
keywords:
  - "training curriculum"
  - "frontmatter field guide"
  - "required body sections"
  - "filled example"
  - "difficulty scheduling"
  - "and adaptive pacing configuration"
  - "curriculum_config"
  - "builder"
  - "output"
  - "## strategy"
density_score: 0.88
related:
  - bld_output_inference_config
  - bld_output_synthetic_data_config
  - bld_output_query_optimizer
  - bld_output_retrieval_evaluator
  - bld_output_tokenizer_config
---
# Output Template: curriculum_config

```yaml
id: p07_cc_{{config_slug}}
kind: curriculum_config
pillar: P07
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"
strategy: "{{easy_to_hard_or_self_paced_or_mixing}}"
difficulty_metric: "{{perplexity_or_length_or_complexity}}"
num_phases: {{integer}}
warmup_fraction: {{float}}
data_sources: [{{source_list}}]
domain: "{{domain_value}}"
quality: null
tags: [curriculum, training, {{strategy_tag}}]
tldr: "{{dense_summary_max_160ch}}"
```

## Strategy
`{{selected_approach_with_rationale}}`

## Data Sources
`{{sources_sizes_mixing_ratios}}`

## Difficulty Progression
`{{metric_definition_and_schedule}}`

## Schedule
`{{warmup_phases_annealing}}`

## Checkpoints
`{{evaluation_points_and_competence_gates}}`

## Quality Gate Checklist

| Gate | Check | Pass Condition |
|------|-------|---------------|
| H01 | Frontmatter complete | All required fields present with valid types |
| H02 | ID matches filename | id field equals filename stem |
| H03 | Naming convention | Follows p07_cc_{{name}}.md + .yaml pattern |
| H04 | Body sections present | All required sections non-empty |
| H05 | Size within limits | Total <= 4096 bytes |
| H06 | No placeholder text | No `{{var}}` unreplaced |
| H07 | quality: null | Never self-scored |

## Properties

| Property | Value |
|----------|-------|
| Kind | `output` |
| Pillar | P05 |
| Domain | curriculum config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_inference_config]] | sibling | 0.43 |
| [[bld_output_synthetic_data_config]] | sibling | 0.42 |
| [[bld_output_query_optimizer]] | sibling | 0.42 |
| [[bld_output_retrieval_evaluator]] | sibling | 0.41 |
| [[bld_output_tokenizer_config]] | sibling | 0.41 |
