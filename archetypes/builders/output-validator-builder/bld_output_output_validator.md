---
kind: output_template
id: bld_output_template_output_validator
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce a output_validator artifact
pattern: every field here exists in SCHEMA.md — template derives, never invents
quality: null
title: "Output Template Output Validator"
version: "1.0.0"
author: n03_builder
tags:
  - "output_validator"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for output validator construction, demonstrating ideal structure and common pitfalls."
domain: "output validator construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F6_produce"
keywords:
  - "template with"
  - "output validator construction"
  - "output template output validator"
  - "output_validator"
  - "builder"
  - "examples"
  - "## overview"
  - "## checks"
  - "## failure actions"
  - "## integration"
density_score: 0.90
related:
  - bld_output_template_hook_config
  - bld_output_template_runtime_rule
  - bld_output_template_constraint_spec
  - bld_instruction_output_validator
  - bld_output_template_retriever_config
---
# Output Template: output_validator
```yaml
id: p05_oval_{{slug}}
kind: output_validator
pillar: P05
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"
name: "{{name}}}}"
checks: "{{checks}}}}"
on_fail: "{{on_fail}}}}"
quality: null
tags: [output_validator, {{tag_2}}, {{tag_3}}]
tldr: "{{dense_summary_max_160ch}}"
description: "{{description}}}}"
retry_count: "{{retry_count}}}}"
fix_prompt: "{{fix_prompt}}}}"
severity: "{{severity}}}}"
applies_to: "{{applies_to}}}}"
```
## Overview
`{{overview_content}}`
## Checks
`{{checks_content}}`
## Failure Actions
`{{failure_actions_content}}`
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
| Domain | output validator construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_output_template_hook_config | sibling | 0.38 |
| bld_output_template_runtime_rule | sibling | 0.37 |
| [[bld_output_template_constraint_spec]] | sibling | 0.36 |
| [[bld_prompt_output_validator]] | upstream | 0.36 |
| [[bld_output_template_retriever_config]] | sibling | 0.35 |
