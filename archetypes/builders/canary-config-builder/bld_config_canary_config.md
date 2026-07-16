---
id: bld_context_sources_canary_config
kind: knowledge_card
pillar: P01
title: "Context Sources: canary_config Builder"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: canary_config
quality: null
tags: [context_sources, canary_config, P09]
llm_function: CONSTRAIN
tldr: "Ordered context sources for F3 INJECT in canary_config builds."
8f: "F3_inject"
keywords: [context sources, canary_config builder, inject in canary_config builds, context_sources, canary_config, injection order, knowledge card, quality gate, configuration checklist, archetypes builders]
density_score: null
related:
  - bld_context_sources_deployment_manifest
  - bld_context_sources_slo_definition
  - bld_context_sources_lineage_record
  - bld_context_sources_saga
  - bld_context_sources_bounded_context
---
# Context Sources: canary_config Builder

## Injection Order (F3 INJECT)
| Priority | Source | Path | Why |
|----------|--------|------|-----|
| 1 | Schema | archetypes/builders/canary-config-builder/bld_schema_canary_config.md | Field constraints |
| 2 | Knowledge Card | N00_genesis/P01_knowledge/library/kind/kc_canary_config.md | Traffic stages + rollback triggers |
| 3 | Examples | archetypes/builders/canary-config-builder/bld_examples_canary_config.md | Golden reference |
| 4 | Quality Gate | archetypes/builders/canary-config-builder/bld_quality_gate_canary_config.md | Validation rules |
| 5 | slo_definition KC | N00_genesis/P01_knowledge/library/kind/kc_slo_definition.md | Rollback trigger signals |
| 6 | deployment_manifest KC | N00_genesis/P01_knowledge/library/kind/kc_deployment_manifest.md | Boundary context |
| 7 | Memory | archetypes/builders/canary-config-builder/bld_memory_canary_config.md | Recalled corrections |

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
| [[bld_context_sources_deployment_manifest]] | sibling | 0.55 |
| [[bld_context_sources_slo_definition]] | sibling | 0.49 |
| [[bld_context_sources_lineage_record]] | sibling | 0.46 |
| [[bld_context_sources_saga]] | sibling | 0.40 |
| [[bld_context_sources_bounded_context]] | downstream | 0.38 |
