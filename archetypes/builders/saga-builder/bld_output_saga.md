---
quality: null
quality: null
id: bld_output_template_saga
kind: knowledge_card
pillar: P05
title: "Output Template: saga"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: saga
tags:
  - "output_template"
  - "saga"
  - "P12"
llm_function: PRODUCE
tldr: "Canonical output template for saga artifacts."
8f: "F3_inject"
keywords:
  - "output template"
  - "output_template"
  - "saga"
  - "## body template"
  - "frontmatter template"
  - "body template"
  - "compensating action"
  - "on failure"
  - "saga_name steps_count"
  - "topology topology"
density_score: null
related:
  - bld_schema_saga
---
# Output Template: saga

## Frontmatter Template
```yaml
---
id: p12_saga_{{name_slug}}
kind: saga
pillar: P12
version: 1.0.0
saga_name: "{{saga_name}}"
steps_count: {{steps_count}}
topology: {{topology}}
on_failure: {{on_failure}}
domain: "{{domain}}"
created: "{{date}}"
updated: "{{date}}"
author: "{{author}}"
quality: null
tags: [saga, {{domain}}]
tldr: "{{saga_name}}: {{steps_count}}-step distributed transaction via {{topology}}"
---
```

## Body Template
```markdown
# {{saga_name}}

## Goal
{{one_sentence_goal}}

## Steps
| ID | Participant | Action | Compensating Action | On Failure |
|----|-------------|--------|---------------------|------------|
| {{step_id}} | {{participant}} | {{action}} | {{compensating_action}} | {{compensate|retry|skip}} |

## Rollback Sequence
On failure at step {{k}}:
1. Compensate step {{k-1}}: {{compensating_action_k_minus_1}}
2. Compensate step {{k-2}}: {{compensating_action_k_minus_2}}
...

## Topology
**{{topology}}**
{{topology_description}}
```

## Output Template Checklist

- Verify output format matches target kind schema
- Validate all frontmatter fields are present in template
- Cross-reference with eval gate for completeness
- Test template rendering with sample data before publishing

## Output Pattern

```yaml
# Output validation
format_match: true
frontmatter_complete: true
eval_gate_aligned: true
sample_rendered: true
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope {BUILDER}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_saga]] | downstream | 0.37 |
