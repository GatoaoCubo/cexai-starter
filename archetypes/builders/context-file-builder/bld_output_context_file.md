---
kind: output_template
id: bld_output_template_context_file
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce a context_file
pattern: every field here exists in bld_schema_context_file.md -- template derives, never invents
quality: null
title: "Output Template: context_file"
version: "1.0.0"
author: n03_builder
tags:
  - "context_file"
  - "builder"
  - "output_template"
  - "hermes_origin"
tldr: "Fill-in template for context_file artifacts: scope, injection_point, inheritance_chain, priority, instruction-only body."
domain: "workspace instruction auto-injection"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F6_produce"
keywords:
  - "template with"
  - "workspace instruction auto-injection"
  - "output template"
  - "instruction-only body"
  - "context_file"
  - "builder"
  - "output_template"
  - "hermes_origin"
  - "| snake_case scope name:"
  - "| pick narrowest scope that applies | |"
density_score: 0.91
related:
  - kc_context_file
  - bld_config_context_file
  - bld_memory_context_file
---
# Output Template: context_file

```yaml
id: ctx_{{scope_slug}}
kind: context_file
pillar: P03

title: "{{human_readable_scope_description}}"
scope: {{workspace|nucleus|session|global}}
injection_point: {{session_start|every_turn|f3_inject}}
inheritance_chain: {{[parent_ctx_ids]|[]}}

max_bytes: {{8192|custom_integer}}
priority: {{0_to_N}}
applies_to_nuclei: {{[all]|[n01,n02,...]}}

version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"

quality: null
tags: [context_file, {{scope_name}}, hermes_origin, {{additional_tag}}]
tldr: "{{dense_summary_max_160ch}}"
density_score: {{0.80-1.00}}
```

## `{{Primary Rule Section Title}}`
1. ALWAYS `{{rule_1}}`
2. NEVER `{{rule_2}}`
3. ALWAYS `{{rule_3}}`
{{...add more rules up to byte budget}}

## `{{Optional Second Section Title}}`
- `{{rule_A}}`
- `{{rule_B}}`
- `{{rule_C}}`

## `{{Optional Third Section Title}}`
{{...repeat as needed; all sections must be instructions, never facts or template vars}}

---

## Fill Guide

| Placeholder | How to fill |
|-------------|------------|
| `{{scope_slug}}` | snake_case scope name: `engineering_workspace`, `n03_nucleus`, `sprint42_session` |
| `{{human_readable_scope_description}}` | E.g.: "N03 Build Conventions", "Engineering Workspace Rules" |
| `{{workspace\|nucleus\|session\|global}}` | Pick narrowest scope that applies |
| `{{session_start\|every_turn\|f3_inject}}` | session_start unless compliance-critical or pipeline-specific |
| `{{[parent_ctx_ids]\|[]}}` | List parent IDs (must exist); empty list for root context_file |
| `{{0_to_N}}` | 0 = most authoritative; increment for narrower scopes |
| `{{[all]\|[n01,n02,...]}}` | [all] for cross-nucleus; explicit list for nucleus-specific |
| `{{rule_N}}` | Behavioral instruction: ALWAYS/NEVER pattern preferred; actionable and verifiable |
| Section titles | Match the rule domain: "Build Rules", "Commit Rules", "Quality Rules", etc. |

## Properties

| Property | Value |
|----------|-------|
| Kind | `output_template` |
| Pillar | P05 |
| Domain | workspace instruction auto-injection |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_context_file]] | upstream | 0.42 |
| [[bld_config_context_file]] | downstream | 0.41 |
| [[bld_memory_context_file]] | downstream | 0.41 |
