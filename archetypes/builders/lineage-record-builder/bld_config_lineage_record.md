---
id: bld_context_sources_lineage_record
kind: knowledge_card
pillar: P01
title: "Context Sources: lineage_record Builder"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: lineage_record
quality: null
tags: [context_sources, lineage_record, P01]
llm_function: CONSTRAIN
tldr: "Ordered context sources for F3 INJECT in lineage_record builds."
8f: "F3_inject"
keywords: [context sources, lineage_record builder, inject in lineage_record builds, context_sources, lineage_record, injection order, knowledge card, quality gate, configuration checklist, archetypes builders]
density_score: null
related:
  - bld_context_sources_deployment_manifest
  - bld_context_sources_canary_config
  - bld_context_sources_slo_definition
  - bld_tools_lineage_record
  - bld_context_sources_saga
---
# Context Sources: lineage_record Builder

## Injection Order (F3 INJECT)
| Priority | Source | Path | Why |
|----------|--------|------|-----|
| 1 | Schema | archetypes/builders/lineage-record-builder/bld_schema_lineage_record.md | Field constraints |
| 2 | Knowledge Card | N00_genesis/P01_knowledge/library/kind/kc_lineage_record.md | PROV-O vocabulary |
| 3 | Examples | archetypes/builders/lineage-record-builder/bld_examples_lineage_record.md | Golden reference |
| 4 | Quality Gate | archetypes/builders/lineage-record-builder/bld_quality_gate_lineage_record.md | Validation rules |
| 5 | citation KC | N00_genesis/P01_knowledge/library/kind/kc_citation.md | Boundary clarification |
| 6 | Memory | archetypes/builders/lineage-record-builder/bld_memory_lineage_record.md | Recalled corrections |

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
| [[bld_context_sources_deployment_manifest]] | sibling | 0.50 |
| [[bld_context_sources_canary_config]] | sibling | 0.47 |
| [[bld_context_sources_slo_definition]] | sibling | 0.47 |
| [[bld_tools_lineage_record]] | sibling | 0.42 |
| [[bld_context_sources_saga]] | sibling | 0.40 |
