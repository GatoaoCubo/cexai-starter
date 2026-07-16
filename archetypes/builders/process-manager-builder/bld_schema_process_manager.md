---
quality: null
id: bld_schema_process_manager
kind: schema
pillar: P12
title: "Process Manager Builder -- Schema"
version: 1.0.0
quality: null
tags:
  - "builder"
  - "process_manager"
  - "schema"
llm_function: CONSTRAIN
author: builder
tldr: "Process Manager orchestration: data contract, field types, and validation rules"
8f: "F8_collaborate"
keywords:
  - "process manager orchestration"
  - "data contract"
  - "field types"
  - "and validation rules"
  - "builder"
  - "process_manager"
  - "schema"
  - "p12_pm_{slug}"
  - "^p12_pm_[a-z][a-z0-9_]+$"
  - "## correlation"
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_schema_aggregate_root
  - bld_schema_value_object
  - bld_schema_model_registry
  - bld_schema_experiment_tracker
---
# Schema: process_manager
## Frontmatter Fields
### Required
| Field | Type | Notes |
|-------|------|-------|
| id | string `p12_pm_{slug}` | namespace + slug |
| kind | literal `process_manager` | type integrity |
| pillar | literal `P12` | pillar assignment |
| title | string | human label |
| version | semver | versioning |
| correlation_key | string | field that ties events to process instance |
| start_event | string | domain event that creates a new instance |
| terminal_states | list[string] | states that end the process (success + failure) |
| states | list[string] | all possible states including start and terminal |
| subscribed_events | list[string] | domain events this process manager listens to |
| commands_issued | list[string] | commands dispatched by this process manager |
| quality | null | never self-score |
| tags | list[string] >= 3 | searchability |
| tldr | string <= 160ch | dense summary |
### Recommended
| Field | Type | Notes |
|-------|------|-------|
| timeout_strategy | object | per_state timeouts + actions |
| compensation | list[string] | rollback commands per failure state |
| persistence | enum(in_memory, database, event_sourced) | how process state is stored |
| idempotency_key | string | ensures at-most-once processing |
## ID Pattern
Regex: `^p12_pm_[a-z][a-z0-9_]+$`
## Body Structure
1. `## Correlation` -- key used to track process instances
2. `## States` -- state machine diagram/table with transitions
3. `## Event Routing` -- event -> transition + command table
4. `## Commands` -- each command issued with target and payload
5. `## Timeout` -- per-state timeouts and timeout actions
6. `## Compensation` -- failure rollback commands
## Constraints
- max_bytes: 4096
- naming: p12_pm_{slug}.md
- process manager holds state only, never domain data
- all commands target external services or aggregates
- quality: null always

## Schema Validation Checklist

- Verify all required fields have type annotations
- Validate enum values against domain vocabulary
- Cross-reference with related schemas for consistency
- Test schema parsing with sample data before publishing

## Schema Pattern

```yaml
# Schema validation contract
types_annotated: true
enums_valid: true
cross_refs_checked: true
sample_data_tested: true
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_schema_hydrate.py --check
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_aggregate_root]] | sibling | 0.43 |
| [[bld_schema_value_object]] | sibling | 0.40 |
| [[bld_schema_model_registry]] | sibling | 0.39 |
| [[bld_schema_experiment_tracker]] | sibling | 0.37 |
