---
id: bld_rules_data_contract
kind: collaboration
pillar: P12
llm_function: COLLABORATE
version: 1.0.0
quality: null
tags: [data_contract, rules, guardrail]
title: "Collaboration + Rules: data_contract Builder"
author: builder
tldr: "Collaboration ISO slot for data_contract-builder; body retained as originally authored (ALWAYS/NEVER, edge cases, naming, size budget) -- a full crew-role/handoff writeup is a follow-up, not fabricated here"
8f: "F8_collaborate"
keywords: [data_contract builder, data contract feedback, workflow coordination, and lifecycle management, data_contract, rules, guardrail, builder rules, naming conventions, size budget]
density_score: 0.88
created: "2026-04-17"
updated: "2026-07-04"
related:
  - data-contract-builder
  - bld_rules_domain_vocabulary
  - bld_rules_value_object
  - bld_rules_alert_rule
  - bld_memory_data_contract
---
# Collaboration: data_contract-builder (Builder Rules Retained)

> **Taxonomy-hygiene note (R-262c, 2026-07-04):** this ISO occupies the
> `bld_orchestration_data_contract.md` slot; its `kind:` is corrected here
> from the misfiled `guardrail` to the slot's canonical `collaboration`
> (verified against 9 clean sibling builders). The body below was authored as
> builder construction Rules (ALWAYS/NEVER/edge cases/naming/size budget), not
> a crew-role/handoff writeup -- preserved verbatim per hygiene policy (never
> delete content). A canonical "My Role in Crews" / "Handoff Protocol"
> writeup for this slot is a follow-up, not fabricated here. Full evidence:
> `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md` Section 9.

## ALWAYS
- ALWAYS name both producer_system and consumer_system explicitly
- ALWAYS version the contract independently from the service version
- ALWAYS use numeric SLA thresholds (< 200ms, 99.9%, < 5s)
- ALWAYS type every schema field (string, uuid, decimal, ISO-4217, etc.)
- ALWAYS set quality: null

## NEVER
- NEVER use data_contract for LLM output validation (use validation_schema)
- NEVER use data_contract for data catalog (use dataset_card)
- NEVER write vague SLAs ("fast", "reliable", "near real-time")
- NEVER tie contract_version to service implementation version
- NEVER omit nullable flag for schema fields

## EDGE CASES
| Case | Rule |
|------|------|
| Bidirectional contract (A->B and B->A) | Create two contracts, one per direction |
| Contract with multiple consumers | One contract per consumer (consumer-driven) |
| Schema change breaking | New contract_version (semver major bump) + migration guide |
| Deprecated field | Keep in schema with deprecated: true + removal_date |

## Naming Conventions
| Pattern | Example |
|---------|---------|
| dc_{producer}_{consumer}_{entity} | dc_sales_billing_order |
| Entity is PascalCase | Order, ClickEvent, UserProfile |
| Systems are kebab-case | sales-service, analytics-warehouse |

## Size Budget
max_bytes: 4096 (schema table + SLA table + versioning = ~2.5KB typical)
Table format preferred over YAML blocks for schema fields.

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
| [[data-contract-builder]] | upstream | 0.35 |
| [[bld_rules_domain_vocabulary]] | sibling | 0.34 |
| bld_rules_value_object | upstream | 0.32 |
| bld_rules_alert_rule | sibling | 0.32 |
| [[bld_memory_data_contract]] | upstream | 0.32 |
