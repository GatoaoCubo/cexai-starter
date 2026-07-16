---
id: bld_rules_domain_event
kind: collaboration
pillar: P12
llm_function: COLLABORATE
version: 1.0.0
quality: null
tags: [domain_event, rules, guardrail]
title: "Collaboration + Rules: domain_event Builder"
author: builder
tldr: "Collaboration ISO slot for domain_event-builder; body retained as originally authored (ALWAYS/NEVER, edge cases, naming, size budget) -- a full crew-role/handoff writeup is a follow-up, not fabricated here"
8f: "F8_collaborate"
keywords: [domain_event builder, domain event feedback, workflow coordination, and lifecycle management, domain_event, rules, guardrail, builder rules, naming conventions, size budget]
density_score: 0.88
created: "2026-04-17"
updated: "2026-07-04"
related:
  - domain-event-builder
---
# Collaboration: domain_event-builder (Builder Rules Retained)

> **Taxonomy-hygiene note (R-262c, 2026-07-04):** this ISO occupies the
> `bld_orchestration_domain_event.md` slot; its `kind:` is corrected here
> from the misfiled `guardrail` to the slot's canonical `collaboration`
> (verified against 9 clean sibling builders). The body below was authored as
> builder construction Rules (ALWAYS/NEVER/edge cases/naming/size budget), not
> a crew-role/handoff writeup -- preserved verbatim per hygiene policy (never
> delete content). A canonical "My Role in Crews" / "Handoff Protocol"
> writeup for this slot is a follow-up, not fabricated here. Full evidence:
> `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md` Section 9.

## ALWAYS
- ALWAYS name events in past tense (OrderPlaced, UserRegistered, PaymentFailed)
- ALWAYS identify the aggregate root -- events belong to aggregates, not services
- ALWAYS set quality: null
- ALWAYS include occurred_at with ISO-8601 UTC timestamp
- ALWAYS populate payload with at least 1 typed field

## NEVER
- NEVER name an event as a command (ProcessOrder, CreateUser)
- NEVER include mutable state in payload (no foreign key lookups at read time)
- NEVER conflate domain_event with signal (signal = system, domain_event = business)
- NEVER conflate domain_event with audit_log (audit = compliance, event = domain model)
- NEVER assign an event to a service -- only aggregates emit domain events

## EDGE CASES
| Case | Rule |
|------|------|
| Event spans multiple aggregates | Split into N events, one per aggregate |
| Event carries sensitive PII | Add pii_fields list; note retention policy |
| Event schema changes | Increment event_version (v1 -> v2), keep old version alive |
| Saga spans multiple BCs | Use correlation_id to link related events |

## Naming Conventions
| Pattern | Example |
|---------|---------|
| Entity + past verb | OrderPlaced, UserDeactivated |
| With qualifier | PaymentFailedDueToFraud (only when ambiguous) |
| ID prefix in file | de_{aggregate}_{verb}.md |

## Size Budget
max_bytes: 3072 (payload schema + causal chain + consumers = ~2KB typical)
Payload table preferred over inline YAML for density.

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
| [[domain-event-builder]] | downstream | 0.40 |
