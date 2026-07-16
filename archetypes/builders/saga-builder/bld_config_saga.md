---
id: bld_context_sources_saga
kind: knowledge_card
pillar: P01
title: "Context Sources: saga Builder"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: saga
quality: null
tags: [context_sources, saga, P12]
llm_function: CONSTRAIN
tldr: "Ordered context sources for F3 INJECT in saga builds."
8f: "F3_inject"
keywords: [context sources, saga builder, inject in saga builds, context_sources, saga, injection order, knowledge card, quality gate, configuration checklist, archetypes builders]
density_score: null
related:
  - bld_context_sources_deployment_manifest
  - bld_context_sources_lineage_record
  - bld_context_sources_canary_config
  - bld_context_sources_slo_definition
  - bld_context_sources_process_manager
---
# Context Sources: saga Builder

## Injection Order (F3 INJECT)
| Priority | Source | Path | Why |
|----------|--------|------|-----|
| 1 | Schema | archetypes/builders/saga-builder/bld_schema_saga.md | Field constraints |
| 2 | Knowledge Card | N00_genesis/P01_knowledge/library/kind/kc_saga.md | Garcia-Molina + compensation model |
| 3 | Examples | archetypes/builders/saga-builder/bld_examples_saga.md | Golden reference |
| 4 | Quality Gate | archetypes/builders/saga-builder/bld_quality_gate_saga.md | Compensation completeness gate |
| 5 | workflow KC | N00_genesis/P01_knowledge/library/kind/kc_workflow.md | Boundary clarification |
| 6 | Memory | archetypes/builders/saga-builder/bld_memory_saga.md | Recalled corrections |

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
| [[bld_context_sources_deployment_manifest]] | sibling | 0.51 |
| [[bld_context_sources_lineage_record]] | sibling | 0.48 |
| [[bld_context_sources_canary_config]] | sibling | 0.48 |
| [[bld_context_sources_slo_definition]] | sibling | 0.47 |
| [[bld_context_sources_process_manager]] | sibling | 0.39 |
