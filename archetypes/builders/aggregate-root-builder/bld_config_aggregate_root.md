---
id: bld_context_sources_aggregate_root
kind: knowledge_card
pillar: P06
title: "Aggregate Root Builder -- Context Sources"
version: 1.0.0
quality: null
tags: [builder, aggregate_root, context]
llm_function: CONSTRAIN
author: builder
tldr: "Aggregate Root schema: naming conventions, output paths, and production limits"
8f: "F3_inject"
keywords: [aggregate root schema, naming conventions, output paths, and production limits, builder, aggregate_root, context, kind: aggregate_root, context sources, mandatory loads]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_tools_aggregate_root
  - bld_context_sources_value_object
  - bld_knowledge_aggregate_root
  - bld_instruction_aggregate_root
  - bld_rules_aggregate_root
---
# Context Sources: aggregate_root
## Mandatory Loads (F3 INJECT)
| Source | Path | Purpose |
|--------|------|---------|
| Kind KC | N00_genesis/P01_knowledge/library/kind/kc_aggregate_root.md | Primary definition |
| Schema | archetypes/builders/aggregate-root-builder/bld_schema_aggregate_root.md | Field constraints |
| Output template | archetypes/builders/aggregate-root-builder/bld_output_template_aggregate_root.md | Structure guide |
| Examples | archetypes/builders/aggregate-root-builder/bld_examples_aggregate_root.md | Golden patterns |
| Pillar schema | N00_genesis/P06_schema/_schema.yaml | Pillar constraints |
## Related Kind KCs
| KC | Relationship |
|----|-------------|
| kc_value_object.md | members inside the aggregate cluster |
| kc_interface.md | repository contract that aggregate depends on |
| kc_input_schema.md | validates data before it enters the aggregate |
| kc_domain_event.md | facts emitted by the aggregate |
## External References
| Source | Relevance |
|--------|----------|
| Evans DDD (2003) Ch. 6 | Original aggregate pattern definition |
| Vernon IDDD (2013) Ch. 10 | Aggregate sizing, event sourcing integration |
| Microsoft DDD guide | Aggregate root in CQRS + event sourcing contexts |
## CEX Artifact Examples
Search: `kind: aggregate_root` in any N03_engineering or N05_operations directory

## Configuration Checklist

- Verify all required fields are present in frontmatter before saving
- Validate config values against schema constraints (type, range, enum)
- Cross-reference with related configs to avoid contradictions
- Test config loading in target runtime before committing

## Validation

```yaml
# Required config validation
fields_present: true
types_valid: true
ranges_checked: true
cross_refs_verified: true
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope {BUILDER}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_aggregate_root]] | sibling | 0.49 |
| [[bld_context_sources_value_object]] | sibling | 0.46 |
| [[bld_knowledge_aggregate_root]] | sibling | 0.44 |
| [[bld_instruction_aggregate_root]] | related | 0.40 |
| [[bld_rules_aggregate_root]] | sibling | 0.39 |
