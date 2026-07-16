---
id: bld_output_bounded_context
kind: output_template
pillar: P05
llm_function: PRODUCE
version: 1.0.0
quality: null
tags: [bounded_context, template, output]
title: "Output Template: bounded_context"
author: builder
tldr: "Bounded Context prompt: output template, formatting rules, and structure"
8f: "F6_produce"
keywords: [output template, bounded context prompt, formatting rules, and structure, bounded_context, template, output, bounded context, key invariants, integration patterns]
density_score: 1.0
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bounded-context-builder
  - bld_schema_bounded_context
---
# Output Template: bounded_context
```markdown
---
id: bc_{{context_snake}}
kind: bounded_context
pillar: P08
title: "{{ContextName}} Bounded Context"
version: 1.0.0
quality: null
context_name: {{ContextNamePascalCase}}
team_owner: {{team_name}}
scope_statement: "{{What domain model applies within this boundary -- 1-2 sentences.}}"
domain_vocabulary: dv_{{context_snake}}_vocabulary
tags: [{{context}}, bounded-context, ddd]
---

# {{ContextName}} Bounded Context

## Scope
{{scope_statement expanded: what domain model applies here, what does NOT apply here.}}

## Aggregates
| Aggregate | Role | Key Invariants |
|-----------|------|---------------|
| {{AggName}} | {{role}} | {{business_rule}} |

## Integration Patterns
| Neighbor Context | Pattern | Direction | Rationale |
|-----------------|---------|-----------|-----------|
| {{bc_neighbor}} | {{ACL/OHS/CF/Partnership}} | upstream/downstream | {{why this pattern}} |

## Domain Events Published
| Event | Consumers |
|-------|-----------|
| {{EventName}} | [{{bc_consumer_1}}, {{bc_consumer_2}}] |

## Key Business Rules
- {{rule that holds WITHIN this BC and NOT in other BCs}}

## Context Map Position
{{Brief description of where this BC sits in the overall context map.}}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bounded-context-builder]] | downstream | 0.51 |
| [[bld_schema_bounded_context]] | downstream | 0.44 |
