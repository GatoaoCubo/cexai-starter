---
quality: null
id: bld_rules_value_object
kind: knowledge_card
pillar: P06
title: "Value Object Builder -- Rules"
version: 1.0.0
quality: null
tags: [builder, value_object, rules]
llm_function: COLLABORATE
author: builder
tldr: "Value Object schema: workflow coordination, handoffs, and lifecycle management"
8f: "F3_inject"
keywords: [value object schema, workflow coordination, and lifecycle management, builder, value_object, rules, absolute rules, soft rules, boundary rules, specific rules]
density_score: 0.81
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_rules_aggregate_root
  - bld_rules_process_manager
  - bld_rules_event_stream
  - bld_rules_data_contract
  - bld_knowledge_card_value_object
---
# Rules: value_object
## Absolute Rules (HARD -- never violate)
1. No identity fields: never add id, uuid, or pk to a value object.
2. Immutability: no setters, no mutation methods, no mutable state.
3. Structural equality: two instances with same attributes are equal (always).
4. Validation at construction: if invalid state can be constructed, the design is broken.
5. Transformations return new instances: withX() -> new VO, never this.x = x.
6. quality: null always -- never self-score.
## Soft Rules (RECOMMEND)
1. Keep attribute count <= 5. More than 5 suggests decomposing into nested value objects.
2. Always specify hashable: true/false explicitly.
3. Include at least 2 invalid state examples to document the validation contract.
4. Name transformations with `with` or `to` prefix for clarity.
## Boundary Rules
1. THIS BUILDER handles: value_object (P06)
2. NOT this builder: type_def (generic alias without DDD contract) -> type-def-builder
3. NOT this builder: enum_def (fixed constants) -> enum-def-builder
4. NOT this builder: aggregate_root (entity with identity) -> aggregate-root-builder
5. NOT this builder: input_schema (raw input validation) -> input-schema-builder
## CEX-Specific Rules
1. id pattern: p06_vo_{slug} -- always prefix p06_vo_
2. Pillar: always P06 (Schema)
3. Producing nucleus: N03 (Engineering)
4. max_bytes: 2048 (smaller than aggregate_root, value objects are concise)

## Orchestration Checklist

- Verify workflow topology matches dependency graph
- Validate handoff protocol between upstream and downstream
- Cross-reference with dispatch rules for routing correctness
- Test wave sequencing with dry-run before live dispatch

## Orchestration Pattern

```yaml
# Workflow validation
topology: verified
handoffs: validated
routing: checked
sequencing: tested
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope orchestration
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_rules_aggregate_root]] | sibling | 0.42 |
| [[bld_rules_process_manager]] | sibling | 0.36 |
| [[bld_rules_event_stream]] | sibling | 0.32 |
| [[bld_rules_data_contract]] | downstream | 0.32 |
| [[bld_knowledge_card_value_object]] | sibling | 0.30 |
