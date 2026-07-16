---
quality: null
quality: null
kind: output_template
id: bld_output_template_state_machine
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce a state_machine artifact
pattern: every field here exists in SCHEMA.md -- template derives, never invents
title: "Output Template State Machine"
version: "1.0.0"
author: n03_builder
tags: [state_machine, builder, output_template]
tldr: "Fill-in template for state_machine: states table, transitions with guards/actions, guard definitions, action definitions."
domain: "state machine construction"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F6_produce"
keywords: [template with, state machine construction, output template state machine, fill-in template for state_machine, states table, transitions with guards, guard definitions, action definitions, state_machine, builder]
density_score: 0.90
related:
  - bld_schema_state_machine
  - bld_instruction_state_machine
  - state-machine-builder
  - kc_state_machine
  - bld_knowledge_card_state_machine
---
# Output Template: state_machine

```yaml
id: p12_sm_{{entity_slug}}
kind: state_machine
pillar: P12
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"
entity: "{{EntityName}}"
initial_state: "{{INITIAL_STATE}}"
final_states: ["{{FINAL_STATE_1}}", "{{FINAL_STATE_2_optional}}"]
states_count: {{integer}}
transitions_count: {{integer}}
quality: null
tags: [state_machine, {{entity_slug}}, {{domain_tag}}]
tldr: "{{entity}} lifecycle FSM: {{states_count}} states, {{transitions_count}} transitions. {{brief_lifecycle_summary}}."
```

## States

| State | Type | Description |
|-------|------|-------------|
| `{{STATE_1}}` | initial | `{{description}}` |
| `{{STATE_2}}` | intermediate | `{{description}}` |
| `{{STATE_N}}` | final | `{{description}}` |

## Transitions

| from_state | event | to_state | guard | action |
|------------|-------|----------|-------|--------|
| `{{FROM}}` | `{{EVENT}}` | `{{TO}}` | {{guard_name()||"-"}} | {{action_name()||"-"}} |

## Guards

| Guard | Expression | Notes |
|-------|-----------|-------|
| {{guardName()}} | `{{boolean_expression}}` | `{{when_it_is_true}}` |

## Actions

| Action | Trigger | Effect |
|--------|---------|--------|
| {{actionName()}} | `{{from_state}}` -> `{{to_state}}` | `{{what_happens}}` |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_state_machine]] | downstream | 0.51 |
| [[bld_instruction_state_machine]] | upstream | 0.43 |
| [[state-machine-builder]] | downstream | 0.39 |
| [[kc_state_machine]] | upstream | 0.35 |
| [[bld_knowledge_card_state_machine]] | upstream | 0.35 |
