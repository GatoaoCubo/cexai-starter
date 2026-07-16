---
id: bld_rules_bounded_context
kind: collaboration
pillar: P12
llm_function: COLLABORATE
version: 1.0.0
quality: null
tags: [bounded_context, rules, guardrail]
title: "Collaboration + Rules: bounded_context Builder"
author: builder
tldr: "Collaboration ISO slot for bounded_context-builder; body retained as originally authored (ALWAYS/NEVER, edge cases, naming, size budget) -- a full crew-role/handoff writeup is a follow-up, not fabricated here"
8f: "F8_collaborate"
keywords: [bounded_context builder, bounded context feedback, workflow coordination, and lifecycle management, bounded_context, rules, guardrail, builder rules, use partnership, naming conventions]
density_score: 0.99
created: "2026-04-17"
updated: "2026-07-04"
related:
  - bounded-context-builder
---
# Collaboration: bounded_context-builder (Builder Rules Retained)

> **Taxonomy-hygiene note (R-262c, 2026-07-04):** this ISO occupies the
> `bld_orchestration_bounded_context.md` slot; its `kind:` is corrected here
> from the misfiled `guardrail` to the slot's canonical `collaboration`
> (verified against 9 clean sibling builders). The body below was authored as
> builder construction Rules (ALWAYS/NEVER/edge cases/naming/size budget), not
> a crew-role/handoff writeup -- preserved verbatim per hygiene policy (never
> delete content). A canonical "My Role in Crews" / "Handoff Protocol"
> writeup for this slot is a follow-up, not fabricated here. Full evidence:
> `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md` Section 9.

## ALWAYS
- ALWAYS write scope_statement in SEMANTIC terms (domain model, not technical)
- ALWAYS identify team_owner (one team per BC)
- ALWAYS list key aggregates within the BC
- ALWAYS document integration patterns with neighboring contexts
- ALWAYS reference the domain_vocabulary for this BC
- ALWAYS set quality: null

## NEVER
- NEVER define a bounded_context by its technical implementation (service, container, namespace)
- NEVER conflate with component_map (deployment topology)
- NEVER allow a BC to be ownerless (anti-pattern: no team = no governance)
- NEVER model a BC that spans multiple teams without Partnership pattern
- NEVER omit integration patterns with neighboring contexts

## EDGE CASES
| Case | Rule |
|------|------|
| BC too large (> 10 aggregates) | Consider splitting into sub-contexts |
| Two teams share a BC | Use Partnership pattern; plan to split |
| BC model conflicts with upstream | Add ACL; protect your model |
| BC needs to be discoverable by others | Use OHS; publish a stable API |

## Naming Conventions
| Pattern | Example |
|---------|---------|
| bc_{domain_noun} | bc_sales, bc_billing, bc_identity |
| context_name PascalCase | Sales, Billing, CexOrchestration |
| Integration patterns | ACL, OHS, CF, Partnership, PL (abbreviations) |

## Size Budget
max_bytes: 4096 (aggregates + integration + rules = ~3KB typical)
Table format for aggregates and integration patterns required.

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
| [[bounded-context-builder]] | upstream | 0.33 |
