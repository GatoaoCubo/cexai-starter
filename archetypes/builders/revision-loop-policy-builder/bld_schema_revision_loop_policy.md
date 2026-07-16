---
id: p11_schema_revision_loop_policy
kind: validation_schema
pillar: P11
llm_function: CONSTRAIN
purpose: F1 CONSTRAIN schema for revision_loop_policy artifacts
quality: null
title: "Schema: Revision Loop Policy"
version: "1.0.0"
author: n03_builder
tags:
 - "schema"
 - "revision_loop_policy"
 - "builder"
 - "p11"
 - "governance"
domain: "revision_loop_policy construction"
created: "2026-04-18"
updated: "2026-04-18"
tldr: "F1 CONSTRAIN schema for revision_loop_policy artifacts"
8f: "F1_constrain"
keywords:
 - "revision_loop_policy construction"
 - "revision loop policy"
 - "schema"
 - "revision_loop_policy"
 - "builder"
 - "governance"
 - "## naming convention"
 - "p11_rlp_{{name}}.yaml"
 - "| | h02 |"
density_score: 0.90
---
## Frontmatter Schema

```yaml
id:
 type: string
 required: true
 pattern: "^rlp_[a-z0-9_]+$"
 example: "rlp_standard"

kind:
 type: string
 required: true
 const: "revision_loop_policy"

pillar:
 type: string
 required: true
 const: "P11"

title:
 type: string
 required: true
 pattern: "^Revision Policy:.+"

max_iterations:
 type: integer
 required: true
 minimum: 1
 maximum: 10
 default: 3

iteration_on_quality_floor:
 type: float
 required: true
 minimum: 0.0
 maximum: 10.0
 default: 8.5

priority_order:
 type: array
 required: true
 items:
 type: string
 enum: [security, quality, implementation]
 minItems: 3
 maxItems: 3
 note: "Must contain all three; order determines conflict resolution priority"

escalation_target:
 type: string
 required: true
 enum: [user, senior_nucleus, freeze]
 default: "user"

escalation_message_template:
 type: string
 required: true
 must_contain: ["{{max_iterations}}", "{{failing_gates}}"]

per_scenario_overrides:
 type: object
 required: false
 default: {}
 additionalProperties:
 type: integer
 minimum: 1
 recommended_keys: [security_critical, documentation]

version:
 type: string
 required: true
 pattern: "^[0-9]+\\.[0-9]+\\.[0-9]+$"

quality:
 type: null
 required: true
 const: null

tags:
 type: array
 required: true
 items:
 type: string
  must_include: [hermes_origin, revision, escalation, policy]

upstream_source:
 type: string
 required: false
 example: "multi-agent-pattern"
```

## Naming Convention
```
p11_rlp_{{name}}.yaml
```
Where `name` is a lowercase slug identifying the policy scope (e.g., `standard`, `security_critical`, `api_pipeline`).

## Size Constraint
- Max bytes: 2048
- Target density: >= 0.85 (tables and structured content preferred over prose)

## HARD Gates
| ID | Check |
|----|-------|
| H01 | `kind == "revision_loop_policy"` |
| H02 | `max_iterations` is positive integer |
| H03 | `priority_order` is exactly `[security, quality, implementation]` |
| H04 | `escalation_target` in `{user, senior_nucleus, freeze}` |
| H05 | `escalation_message_template` contains `{{max_iterations}}` AND `{{failing_gates}}` |
| H06 | `quality == null` |

## Body Sections (required)
1. `## Policy: {{name}}` -- human-readable name
2. `### Revision Loop Behavior` -- parameter table
3. `### Scenario Overrides` -- override table
4. `### Escalation Protocol` -- numbered steps
5. `### Boundaries` -- NOT-items (4 minimum)
6. `### Usage in pipeline_template` -- code block
