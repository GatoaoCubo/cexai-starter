---
id: bld_context_sources_domain_vocabulary
kind: rag_source
pillar: P10
llm_function: CONSTRAIN
version: 1.0.0
quality: null
tags: [domain_vocabulary, context, rag]
title: "Context Sources: domain_vocabulary"
author: builder
tldr: "Domain Vocabulary memory: naming conventions, output paths, and production limits"
8f: "F3_inject"
keywords: [context sources, domain vocabulary memory, naming conventions, output paths, and production limits, domain_vocabulary, context, mandatory sources, optional sources, search queries]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_context_sources_bounded_context
  - bld_context_sources_data_contract
  - bld_context_sources_domain_event
  - bld_tools_domain_vocabulary
  - bld_context_sources_alert_rule
---
# Context Sources: domain_vocabulary
## Mandatory Sources (load at F3 INJECT)
| Source | Path | Why |
|--------|------|-----|
| Kind KC | N00_genesis/P01_knowledge/library/kind/kc_domain_vocabulary.md | Definition + boundary |
| Schema | archetypes/builders/domain-vocabulary-builder/bld_schema_domain_vocabulary.md | Required structure |
| Examples | archetypes/builders/domain-vocabulary-builder/bld_examples_domain_vocabulary.md | Golden patterns |
| UL rule | .claude/rules/ubiquitous-language.md | Loading protocol |

## Optional Sources (load if relevant)
| Source | Path | When to Load |
|--------|------|-------------|
| bounded_context KC | N00_genesis/P01_knowledge/library/kind/kc_bounded_context.md | BC scoping rules |
| Existing vocabulary | {nucleus}/P01_*/dv_*.md | Consistency with existing vocabs |
| Nucleus vocabulary KCs | N0X_{domain}/P01_knowledge/kc_{domain}_vocabulary.md | Maps to this kind |

## Search Queries for Retrieval
- "ubiquitous language domain model DDD bounded context"
- "controlled vocabulary semantic drift prevention"
- "term registry canonical terms anti-patterns"
- "F2b SPEAK vocabulary loading protocol"

## Anti-Sources (do NOT confuse with)
- glossary_entry (single term, not registry)
- ontology (formal relations, not term registry)
- knowledge_card (facts about domain, not term governance)

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
| [[bld_context_sources_data_contract]] | sibling | 0.45 |
| bld_context_sources_domain_event | sibling | 0.39 |
| [[bld_tools_domain_vocabulary]] | upstream | 0.39 |
| bld_context_sources_alert_rule | sibling | 0.38 |
