---
id: bld_output_domain_event
kind: output_template
pillar: P05
llm_function: PRODUCE
version: 1.0.0
quality: null
tags: [domain_event, template, output]
title: "Output Template: domain_event"
author: builder
tldr: "Domain Event prompt: output template, formatting rules, and structure"
8f: "F6_produce"
keywords: [output template, domain event prompt, formatting rules, and structure, domain_event, template, output, what happened, causal chain, bounded context]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_schema_domain_event
  - domain-event-builder
---
# Output Template: domain_event
```markdown
---
id: de_{{aggregate_snake}}_{{verb_past_tense}}
kind: domain_event
pillar: P12
title: "{{EventNamePastTense}}"
version: 1.0.0
quality: null
aggregate_root: {{AggregateClassName}}
bounded_context: {{context_name}}
event_version: v1
occurred_at: "{{YYYY-MM-DDTHH:MM:SSZ}}"
causation_id: "{{causation_uuid_or_null}}"
correlation_id: "{{saga_or_trace_id_or_null}}"
tags: [{{aggregate}}, {{context}}, domain-event]
---

# {{EventNamePastTense}}

## What Happened
{{One sentence: what domain fact this event records.}}

## Payload
| Field | Type | Value at Occurrence |
|-------|------|---------------------|
| {{field_1}} | {{type}} | {{example_value}} |
| {{field_2}} | {{type}} | {{example_value}} |

## Causal Chain
- Command/trigger: {{what_caused_this_event}}
- causation_id: {{uuid}}
- correlation_id: {{saga_id}}

## Consumers
| Bounded Context | Reaction |
|----------------|----------|
| {{context_name}} | {{what_it_does_with_event}} |

## Invariants
- {{business_rule_this_event_enforces}}
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
| [[bld_schema_domain_event]] | downstream | 0.31 |
| [[domain-event-builder]] | downstream | 0.30 |
