---
id: bld_rules_alert_rule
kind: collaboration
pillar: P12
llm_function: COLLABORATE
version: 1.0.0
quality: null
tags: [alert_rule, rules, guardrail]
title: "Collaboration + Rules: alert_rule Builder"
author: builder
tldr: "Collaboration ISO slot for alert_rule-builder; body retained as originally authored (ALWAYS/NEVER, edge cases, naming, size budget) -- a full crew-role/handoff writeup is a follow-up, not fabricated here"
8f: "F8_collaborate"
keywords: [alert_rule builder, alert rule feedback, workflow coordination, and lifecycle management, alert_rule, rules, guardrail, builder rules, naming conventions, size budget]
density_score: 0.88
created: "2026-04-17"
updated: "2026-07-04"
related:
  - alert-rule-builder
  - bld_rules_data_contract
  - bld_memory_alert_rule
  - bld_rules_bounded_context
  - bld_rules_domain_vocabulary
---
# Collaboration: alert_rule-builder (Builder Rules Retained)

> **Taxonomy-hygiene note (R-262c, 2026-07-04):** this ISO occupies the
> `bld_orchestration_alert_rule.md` slot; its `kind:` is corrected here
> from the misfiled `guardrail` to the slot's canonical `collaboration`
> (verified against 9 clean sibling builders). The body below was authored as
> builder construction Rules (ALWAYS/NEVER/edge cases/naming/size budget), not
> a crew-role/handoff writeup -- preserved verbatim per hygiene policy (never
> delete content). A canonical "My Role in Crews" / "Handoff Protocol"
> writeup for this slot is a follow-up, not fabricated here. Full evidence:
> `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md` Section 9.

## ALWAYS
- ALWAYS include a numeric threshold in metric_expression
- ALWAYS set for_duration (prevents flapping; 0s valid for critical)
- ALWAYS align routing with severity (critical -> page; warning -> ticket)
- ALWAYS provide runbook_url or remediation_steps for critical alerts
- ALWAYS set quality: null

## NEVER
- NEVER use alert_rule for LLM behavior constraints (use guardrail)
- NEVER use alert_rule for artifact quality scoring (use quality_gate)
- NEVER write vague metric expressions ("when it's slow", "if errors happen")
- NEVER page on warning severity -- warning creates tickets, not pages
- NEVER omit routing target

## EDGE CASES
| Case | Rule |
|------|------|
| Alert should suppress others | Add inhibit_rules referencing other alert IDs |
| SLO-based alert | Use burn_rate expression (not raw threshold) |
| Composite condition (A AND B) | Single expression using PromQL AND operator |
| Maintenance window suppression | Add silence configuration (separate from rule) |

## Naming Conventions
| Pattern | Example |
|---------|---------|
| ar_{system}_{metric}_{level} | ar_api_error_rate_high |
| alert_name PascalCase | ApiErrorRateHigh |
| severity levels | critical, warning, info (lowercase) |

## Size Budget
max_bytes: 2048 (minimal kind -- expression + routing + runbook = ~1KB typical)

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
| [[alert-rule-builder]] | upstream | 0.40 |
| [[bld_rules_data_contract]] | sibling | 0.35 |
| [[bld_memory_alert_rule]] | upstream | 0.34 |
| [[bld_rules_bounded_context]] | sibling | 0.33 |
| [[bld_rules_domain_vocabulary]] | sibling | 0.32 |
