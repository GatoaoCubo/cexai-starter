---
id: bld_context_sources_domain_event
kind: rag_source
pillar: P10
llm_function: CONSTRAIN
version: 1.0.0
quality: null
tags: [domain_event, context, rag]
title: "Context Sources: domain_event"
author: builder
tldr: "Domain Event memory: naming conventions, output paths, and production limits"
8f: "F3_inject"
keywords: [context sources, domain event memory, naming conventions, output paths, and production limits, domain_event, context, mandatory sources, optional sources, search queries]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_tools_domain_event
---
# Context Sources: domain_event
## Mandatory Sources (load at F3 INJECT)
| Source | Path | Why |
|--------|------|-----|
| Kind KC | N00_genesis/P01_knowledge/library/kind/kc_domain_event.md | Definition + boundary |
| Schema | archetypes/builders/domain-event-builder/bld_schema_domain_event.md | Required fields |
| Examples | archetypes/builders/domain-event-builder/bld_examples_domain_event.md | Golden patterns |
| Bounded context KC | N00_genesis/P01_knowledge/library/kind/kc_bounded_context.md | Ownership rules |

## Optional Sources (load if available)
| Source | Path | When to Load |
|--------|------|-------------|
| Existing domain events | {nucleus}/P12_*/de_*.md | Reuse + consistency check |
| Data contract | {nucleus}/P06_*/dc_*.md | If event crosses BC boundary |
| Workflow | {nucleus}/P12_*/wf_*.md | If event triggers workflow |

## Search Queries for Retrieval
- "domain event aggregate root past tense"
- "DDD event sourcing immutable record"
- "bounded context event catalog"
- "causation correlation id tracing"

## Anti-Sources (do NOT confuse with)
- signal artifacts (P11, system telemetry)
- audit_log artifacts (P11, compliance)
- workflow triggers (P12, process control)

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
| [[bld_tools_domain_event]] | downstream | 0.40 |
