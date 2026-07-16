---
id: bld_context_sources_bounded_context
kind: rag_source
pillar: P10
llm_function: CONSTRAIN
version: 1.0.0
quality: null
tags: [bounded_context, context, rag]
title: "Context Sources: bounded_context"
author: builder
tldr: "Bounded Context memory: naming conventions, output paths, and production limits"
8f: "F3_inject"
keywords: [context sources, bounded context memory, naming conventions, output paths, and production limits, bounded_context, context, mandatory sources, optional sources, search queries]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_context_sources_data_contract
  - bld_context_sources_domain_vocabulary
  - bld_context_sources_domain_event
  - bld_context_sources_deployment_manifest
  - bld_context_sources_alert_rule
---
# Context Sources: bounded_context
## Mandatory Sources (load at F3 INJECT)
| Source | Path | Why |
|--------|------|-----|
| Kind KC | N00_genesis/P01_knowledge/library/kind/kc_bounded_context.md | Definition + boundary |
| Schema | archetypes/builders/bounded-context-builder/bld_schema_bounded_context.md | Required fields |
| Examples | archetypes/builders/bounded-context-builder/bld_examples_bounded_context.md | Golden patterns |

## Optional Sources (load if relevant)
| Source | Path | When to Load |
|--------|------|-------------|
| domain_vocabulary KC | N00_genesis/P01_knowledge/library/kind/kc_domain_vocabulary.md | Vocabulary governance |
| domain_event KC | N00_genesis/P01_knowledge/library/kind/kc_domain_event.md | Published events |
| data_contract KC | N00_genesis/P01_knowledge/library/kind/kc_data_contract.md | Integration contracts |
| Nucleus defs | N0X_*/P08_architecture/nucleus_def_n0X.md | BC maps to nucleus |

## Search Queries for Retrieval
- "DDD bounded context context map integration pattern"
- "Anti-Corruption Layer Open Host Service Conformist"
- "domain model boundary team ownership aggregate"
- "Evans context mapping upstream downstream"

## Anti-Sources (do NOT confuse with)
- component_map (deployment topology, not semantic boundary)
- namespace (code organization, not domain model)
- agent_card (capability definition, not domain boundary)

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
| [[bld_context_sources_data_contract]] | sibling | 0.54 |
| [[bld_context_sources_domain_vocabulary]] | sibling | 0.49 |
| [[bld_context_sources_domain_event]] | sibling | 0.47 |
| [[bld_context_sources_deployment_manifest]] | upstream | 0.46 |
| [[bld_context_sources_alert_rule]] | sibling | 0.44 |
