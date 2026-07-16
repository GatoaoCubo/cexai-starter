---
kind: output_template
id: bld_output_template_thinking_config
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for thinking_config production
quality: null
title: "Output Template Thinking Config"
version: "1.0.0"
author: wave1_builder_gen
tags: [thinking_config, builder, output_template]
tldr: "Output template for thinking config: frontmatter field guide, required body sections, filled example, and quality gate checklist for extended thinking and budget token settings."
domain: "thinking_config construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F6_produce"
keywords: [thinking_config construction, output template thinking config, frontmatter field guide, required body sections, filled example, thinking_config, builder, output_template, quality gate checklist, pass condition]
density_score: 0.85
related:
  - bld_config_thinking_config
---
This ISO configures a thinking budget: how many tokens the model may spend on internal reasoning before emitting.

```yaml
name: {{name}}
description: {{description}}
version: {{version}}
author: {{author}}
date: {{date}}

objectives:
  - {{objective_1}}
  - {{objective_2}}

steps:
  - {{step_1}}
  - {{step_2}}

constraints:
  - {{constraint_1}}
  - {{constraint_2}}

outputs:
  - {{output_1}}
  - {{output_2}}
```

## Quality Gate Checklist

| Gate | Check | Pass Condition |
|------|-------|---------------|
| H01 | Frontmatter complete | All required fields present with valid types |
| H02 | ID matches filename | id field equals filename stem |
| H03 | Naming convention | Follows p09_thk_{{name}}.yaml pattern |
| H04 | Body sections present | All required sections non-empty |
| H05 | Size within limits | Total <= 2048 bytes |
| H06 | No placeholder text | No `{{var}}` unreplaced |
| H07 | quality: null | Never self-scored |

## Properties

| Property | Value |
|----------|-------|
| Kind | `output` |
| Pillar | P05 |
| Domain | thinking config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_thinking_config]] | downstream | 0.33 |
