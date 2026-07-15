---
id: bld_context_sources_data_contract
kind: rag_source
pillar: P10
llm_function: CONSTRAIN
version: 1.0.0
quality: null
tags: [data_contract, context, rag]
title: "Context Sources: data_contract"
author: builder
tldr: "Data Contract memory: naming conventions, output paths, and production limits"
8f: "F3_inject"
keywords: [context sources, data contract memory, naming conventions, output paths, and production limits, data_contract, context, mandatory sources, optional sources, search queries]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_context_sources_bounded_context
  - bld_context_sources_domain_event
  - bld_tools_data_contract
  - bld_context_sources_alert_rule
  - bld_context_sources_domain_vocabulary
---
# Context Sources: data_contract
## Mandatory Sources (load at F3 INJECT)
| Source | Path | Why |
|--------|------|-----|
| Kind KC | N00_genesis/P01_knowledge/library/kind/kc_data_contract.md | Definition + boundary |
| Schema | archetypes/builders/data-contract-builder/bld_schema_data_contract.md | Required fields |
| Examples | archetypes/builders/data-contract-builder/bld_examples_data_contract.md | Golden patterns |

## Optional Sources (load if relevant)
| Source | Path | When to Load |
|--------|------|-------------|
| domain_event KC | N00_genesis/P01_knowledge/library/kind/kc_domain_event.md | If contract formalizes event schema |
| bounded_context KC | N00_genesis/P01_knowledge/library/kind/kc_bounded_context.md | BC boundary context |
| Existing contracts | {nucleus}/P06_*/dc_*.md | Consistency with existing agreements |

## Search Queries for Retrieval
- "data contract producer consumer schema SLA"
- "DDD published language bounded context"
- "schema registry Avro Protobuf contract"
- "consumer-driven contract testing Pact"

## Anti-Sources (do NOT confuse with)
- validation_schema (LLM output validation, not cross-system contract)
- dataset_card (data asset metadata, not exchange agreement)
- input_schema (single system, not cross-boundary)

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
| bld_context_sources_bounded_context | sibling | 0.50 |
| bld_context_sources_domain_event | sibling | 0.45 |
| [[bld_tools_data_contract]] | upstream | 0.42 |
| bld_context_sources_alert_rule | sibling | 0.41 |
| [[bld_context_sources_domain_vocabulary]] | sibling | 0.40 |
