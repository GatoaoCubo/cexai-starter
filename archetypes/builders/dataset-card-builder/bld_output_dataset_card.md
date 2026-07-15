---
kind: output_template
id: bld_output_template_dataset_card
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for dataset_card production
quality: null
title: "Output Template Dataset Card"
version: "1.0.0"
author: wave1_builder_gen
tags: [dataset_card, builder, output_template]
tldr: "Output template for dataset card: frontmatter field guide, required body sections, filled example, and quality gate checklist for structured dataset documentation."
domain: "dataset_card construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F6_produce"
keywords: [dataset_card construction, output template dataset card, frontmatter field guide, required body sections, filled example, dataset_card, builder, output_template, dataset card, data collection]
density_score: 0.85
related:
  - bld_output_template_thinking_config
  - bld_config_dataset_card
  - bld_output_template_collaboration_pattern
  - bld_output_template_visual_workflow
  - bld_output_query_optimizer
---
```yaml
name: {{name}}
version: {{version}}
description: {{description}}
date: {{date}}
author: {{author}}
license: {{license}}
tags: {{tags}}
```

# Dataset Card: {{name}}
## Overview
`{{overview_summary}}`

## Data Collection
`{{collection_methodology_and_sources}}`

## Data Processing
`{{preprocessing_and_cleaning_steps}}`

## Intended Use
`{{use_cases_and_applications}}`

## Limitations & Biases
`{{limitations_and_potential_biases}}`

## Metadata
- **Pillar**: P01
- **Template Type**: dataset_card
- **Naming Convention**: p01_dc_{{name}}.md

## Quality Gate Checklist

| Gate | Check | Pass Condition |
|------|-------|---------------|
| H01 | Frontmatter complete | All required fields present with valid types |
| H02 | ID matches filename | id field equals filename stem |
| H03 | Naming convention | Follows p01_dc_{{name}}.md pattern |
| H04 | Body sections present | All required sections non-empty |
| H05 | Size within limits | Total <= 5120 bytes |
| H06 | No placeholder text | No `{{var}}` unreplaced |
| H07 | quality: null | Never self-scored |

## Properties

| Property | Value |
|----------|-------|
| Kind | `output` |
| Pillar | P05 |
| Domain | dataset card construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_output_template_thinking_config | sibling | 0.34 |
| [[bld_config_dataset_card]] | downstream | 0.34 |
| bld_output_template_collaboration_pattern | sibling | 0.34 |
| bld_output_template_visual_workflow | sibling | 0.33 |
| bld_output_query_optimizer | sibling | 0.30 |
