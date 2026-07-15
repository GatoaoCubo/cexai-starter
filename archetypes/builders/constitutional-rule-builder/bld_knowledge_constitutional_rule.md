---
quality: null
id: bld_knowledge_card_constitutional_rule
kind: knowledge_card
pillar: P11
title: "Constitutional Rule Builder -- Knowledge Card"
version: 1.0.0
quality: null
tags: [builder, constitutional_rule, knowledge]
llm_function: INJECT
created: "2026-04-17"
updated: "2026-04-22"
author: builder
domain: constitutional_rule
tldr: "Domain knowledge for building constitutional_rule artifacts -- absolute behavioral constraints that admit no bypass."
8f: "F3_inject"
keywords: [builder, constitutional_rule, knowledge, rule_id, scope, prohibition, rationale, examples_violating, bypass_verdict, core concept

constitutional rule]
density_score: 0.87
related:
  - bld_schema_guardrail
  - bld_schema_bugloop
  - bld_schema_quickstart_guide
  - bld_schema_rbac_policy
  - bld_schema_usage_report
---
# Knowledge: constitutional_rule

## Core Concept

Constitutional Rule is an absolute behavioral constraint for an agent.
Differs from guardrail: no bypass, no approver, no audit trail that unlocks it.
Origin: Anthropic Constitutional AI (2022) -- principles that cannot be trained away.

## Kind Taxonomy

| Kind | Constraint Type | Bypass Allowed? | Audit Trail? |
|------|-----------------|-----------------|--------------|
| constitutional_rule | Absolute value-derived | Never | No |
| guardrail | Operational policy | Yes (with approver) | Yes |
| quality_gate | Output quality floor | Yes (explicit accept) | Yes |
| permission | Access control | Yes (role-based) | Yes |
| safety_policy | Human-readable policy | Yes (exception process) | Yes |

## When to Use

| Condition | Use constitutional_rule? |
|-----------|--------------------------|
| Agent must NEVER do X under any circumstances | YES |
| Prohibition derived from a fundamental value | YES |
| No legitimate business scenario justifies exception | YES |
| Rule must hold even if operator instructs otherwise | YES |
| Bypass exists for security hotfix | NO -- use guardrail |
| Constraint is about output quality | NO -- use quality_gate |
| Constraint is about access control | NO -- use permission |
| Document is for humans, not agents | NO -- use safety_policy |

## The Bypass Test

Before creating a constitutional_rule, ask:
"Is there ANY scenario -- security hotfix, regulatory requirement, executive override --
where this should be bypassed?"

- YES to any: it is a guardrail, not a constitutional_rule
- NO to all: proceed with constitutional_rule

## CEX Integration

| Property | Value |
|----------|-------|
| Pillar | P11 (Feedback) |
| Builder | constitutional-rule-builder (12 ISOs) |
| core | true -- applied to all nuclei, cannot be scoped away |
| Produced by | N07 (Orchestrator) -- core rules come from orchestrator |
| Related | guardrail (P11), quality_gate (P11) |
| max_bytes | 2048 |

## Structural Requirements

| Field | Required | Notes |
|-------|----------|-------|
| `rule_id` | YES | Unique, stable identifier across versions |
| `scope` | YES | Which agents/nuclei this applies to |
| `prohibition` | YES | Exact statement of what is prohibited |
| `rationale` | YES | Value or principle that grounds the rule |
| `examples_violating` | YES | At least 2 concrete violation examples |
| `bypass_verdict` | YES | Explicit "no bypass" declaration |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_guardrail]] | upstream | 0.43 |
| bld_schema_bugloop | related | 0.42 |
| bld_schema_quickstart_guide | upstream | 0.42 |
| [[bld_schema_rbac_policy]] | upstream | 0.41 |
| bld_schema_usage_report | upstream | 0.41 |
