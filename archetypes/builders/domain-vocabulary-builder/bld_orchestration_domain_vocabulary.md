---
id: bld_rules_domain_vocabulary
kind: collaboration
pillar: P12
llm_function: COLLABORATE
version: 1.0.0
quality: null
tags: [domain_vocabulary, rules, guardrail]
title: "Collaboration + Rules: domain_vocabulary Builder"
author: builder
tldr: "Collaboration ISO slot for domain_vocabulary-builder; body retained as originally authored (ALWAYS/NEVER, edge cases, naming, size budget) -- a full crew-role/handoff writeup is a follow-up, not fabricated here"
8f: "F8_collaborate"
keywords: [domain_vocabulary builder, domain vocabulary feedback, workflow coordination, and lifecycle management, domain_vocabulary, rules, guardrail, builder rules, naming conventions, size budget]
density_score: 0.88
created: "2026-04-17"
updated: "2026-07-04"
related:
  - bld_rules_data_contract
  - bld_rules_bounded_context
  - domain-vocabulary-builder
  - p01_kc_domain_vocabulary
  - bld_instruction_domain_vocabulary
---
# Collaboration: domain_vocabulary-builder (Builder Rules Retained)

> **Taxonomy-hygiene note (R-262c, 2026-07-04):** this ISO occupies the
> `bld_orchestration_domain_vocabulary.md` slot; its `kind:` is corrected here
> from the misfiled `guardrail` to the slot's canonical `collaboration`
> (verified against 9 clean sibling builders). The body below was authored as
> builder construction Rules (ALWAYS/NEVER/edge cases/naming/size budget), not
> a crew-role/handoff writeup -- preserved verbatim per hygiene policy (never
> delete content). A canonical "My Role in Crews" / "Handoff Protocol"
> writeup for this slot is a follow-up, not fabricated here. Full evidence:
> `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md` Section 9.

## ALWAYS
- ALWAYS scope to a single bounded_context (not global)
- ALWAYS include anti_patterns per term (drift prevention)
- ALWAYS list governed_agents (who must load this)
- ALWAYS track lifecycle: proposed -> active -> deprecated
- ALWAYS include loading instructions (F2b SPEAK protocol)
- ALWAYS set quality: null

## NEVER
- NEVER create a global vocabulary spanning all bounded contexts
- NEVER include formal ontological relations (IS-A, PART-OF) -- use ontology kind
- NEVER duplicate glossary_entry content -- reference it instead
- NEVER delete deprecated terms -- mark deprecated + replaced_by
- NEVER list terms without at least a definition and status

## EDGE CASES
| Case | Rule |
|------|------|
| Same word in two BCs | Two separate entries in two separate vocabularies |
| Term needs formal definition | Link to glossary_entry; keep summary in vocabulary |
| Vocabulary for a sub-context | Extend parent vocabulary, don't duplicate |
| Term from external framework (Evans, NIST) | Credit in industry_standard field |

## Naming Conventions
| Pattern | Example |
|---------|---------|
| dv_{bounded_context}_vocabulary | dv_sales_vocabulary |
| Terms in PascalCase in headings | ### Order, ### Customer |
| status values | proposed, active, deprecated |

## Size Budget
max_bytes: 5120 (core: true kind -- gets 5KB like knowledge_card)
Table format per term preferred over free prose.

## Orchestration Checklist

- Verify workflow topology matches dependency graph
- Validate handoff protocol between upstream and downstream
- Cross-reference with dispatch rules for routing correctness
- Test wave sequencing with dry-run before live dispatch

## Orchestration Pattern

```yaml
# Workflow validation
topology: verified
handoffs: validated
routing: checked
sequencing: tested
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope orchestration
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_rules_data_contract]] | sibling | 0.37 |
| bld_rules_bounded_context | sibling | 0.37 |
| [[domain-vocabulary-builder]] | upstream | 0.36 |
| [[p01_kc_domain_vocabulary]] | upstream | 0.33 |
| [[bld_instruction_domain_vocabulary]] | upstream | 0.32 |
