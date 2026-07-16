---
kind: output_template
id: bld_output_template_hook_config
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce a hook_config artifact
pattern: every field here exists in SCHEMA.md — template derives, never invents
quality: null
title: "Output Template Hook Config"
version: "1.0.0"
author: n03_builder
tags:
  - "hook_config"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for hook config construction, demonstrating ideal structure and common pitfalls."
domain: "hook config construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
keywords:
  - "template with"
  - "hook config construction"
  - "output template hook config"
  - "hook_config"
  - "builder"
  - "examples"
  - "## overview"
  - "## hooks"
  - "## lifecycle"
  - "## integration"
density_score: 0.90
related:
  - bld_output_template_effort_profile
  - bld_output_template_output_validator
  - bld_output_template_runtime_rule
  - bld_output_template_feature_flag
  - bld_output_template_constraint_spec
---
# Output Template: hook_config
```yaml
id: p04_hookconf_{{slug}}
kind: hook_config
pillar: P04
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"
name: "{{name}}"
target_builder: "{{target_builder}}"
phases: [{{phases_list}}]
quality: null
tags: [hook_config, {{tag_2}}, {{tag_3}}]
tldr: "{{dense_summary_max_160ch}}"
description: "{{description}}"
priority_mode: "{{priority_mode}}"
error_strategy: "{{error_strategy}}"
```
## Overview
`{{overview_content}}`
## Hooks
`{{hooks_table_content}}`
## Lifecycle
`{{lifecycle_content}}`
## Integration
`{{integration_content}}`

## Template Standards

1. Define all required sections for this output kind
2. Include frontmatter schema with mandatory fields
3. Provide structural markers for post-validation
4. Specify format constraints for markdown YAML JSON
5. Reference the validation_schema for automated checks

## Properties

| Property | Value |
|----------|-------|
| Kind | `output_template` |
| Pillar | P05 |
| Domain | hook config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_effort_profile]] | sibling | 0.38 |
| [[bld_output_template_output_validator]] | sibling | 0.38 |
| [[bld_output_template_runtime_rule]] | sibling | 0.36 |
| [[bld_output_template_feature_flag]] | sibling | 0.36 |
| [[bld_output_template_constraint_spec]] | sibling | 0.35 |
