---
id: bld_context_sources_slo_definition
kind: knowledge_card
pillar: P01
title: "Context Sources: slo_definition Builder"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: slo_definition
quality: null
tags: [context_sources, slo_definition, P09]
llm_function: CONSTRAIN
tldr: "Ordered context sources for F3 INJECT in slo_definition builds."
8f: "F3_inject"
keywords: [context sources, slo_definition builder, inject in slo_definition builds, context_sources, slo_definition, injection order, knowledge card, quality gate, configuration checklist, archetypes builders]
density_score: null
---
# Context Sources: slo_definition Builder

## Injection Order (F3 INJECT)
| Priority | Source | Path | Why |
|----------|--------|------|-----|
| 1 | Schema | archetypes/builders/slo-definition-builder/bld_schema_slo_definition.md | Field constraints |
| 2 | Knowledge Card | N00_genesis/P01_knowledge/library/kind/kc_slo_definition.md | Domain knowledge + error budget math |
| 3 | Examples | archetypes/builders/slo-definition-builder/bld_examples_slo_definition.md | Golden reference |
| 4 | Quality Gate | archetypes/builders/slo-definition-builder/bld_quality_gate_slo_definition.md | Validation rules |
| 5 | trace_config KC | N00_genesis/P01_knowledge/library/kind/kc_trace_config.md | Observability context |
| 6 | Memory | archetypes/builders/slo-definition-builder/bld_memory_slo_definition.md | Recalled corrections |

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
