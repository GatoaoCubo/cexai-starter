---
kind: output_template
id: bld_output_template_white_label_config
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for white_label_config production
quality: null
title: "Output Template White Label Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [white_label_config, builder, output_template]
tldr: "Output template for white label config: frontmatter field guide, required body sections, filled example, and quality gate checklist for white-label/reseller configuration for branded deployments."
domain: "white_label_config construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [white_label_config construction, frontmatter field guide, required body sections, filled example, white_label_config, builder, output_template, example value, quality gate checklist, pass condition]
density_score: 0.85
related:
  - bld_config_white_label_config
  - bld_output_template_collaboration_pattern
  - bld_output_template_thinking_config
  - bld_output_template_visual_workflow
  - bld_output_template_dataset_card
---
```yaml
---
id: {{id}} <!-- Pattern: ^p09_wl_[a-z][a-z0-9_]+.yaml$ -->
name: {{name}} <!-- Human-readable label for the white label -->
description: {{description}} <!-- Brief purpose of this configuration -->
config:
  theme: {{theme}} <!-- UI/UX theme (e.g., "dark", "light") -->
  language: {{language}} <!-- Default language code (e.g., "en", "es") -->
quality: null <!-- Must remain null -->
```

| Parameter   | Example Value | Description                  |
|-------------|---------------|------------------------------|
| theme       | dark          | UI theme for the platform    |
| language    | en            | Default language             |
| max_users   | 1000          | Maximum concurrent users     |

```yaml
# Example config block
config:
  theme: dark
  language: en
  max_users: 1000
  features:
    - trading
    - wallet
```

## Quality Gate Checklist

| Gate | Check | Pass Condition |
|------|-------|---------------|
| H01 | Frontmatter complete | All required fields present with valid types |
| H02 | ID matches filename | id field equals filename stem |
| H03 | Naming convention | Follows p09_wl_{{name}}.yaml pattern |
| H04 | Body sections present | All required sections non-empty |
| H05 | Size within limits | Total <= 4096 bytes |
| H06 | No placeholder text | No `{{var}}` unreplaced |
| H07 | quality: null | Never self-scored |

## Properties

| Property | Value |
|----------|-------|
| Kind | `output` |
| Pillar | P05 |
| Domain | white label config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_white_label_config]] | downstream | 0.32 |
| bld_output_template_collaboration_pattern | sibling | 0.29 |
| bld_output_template_thinking_config | sibling | 0.29 |
| bld_output_template_visual_workflow | sibling | 0.28 |
| [[bld_output_template_dataset_card]] | sibling | 0.28 |
