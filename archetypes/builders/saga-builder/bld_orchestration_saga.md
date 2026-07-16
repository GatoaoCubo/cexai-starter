---
quality: null
quality: null
id: bld_rules_saga
kind: knowledge_card
pillar: P08
title: "Rules: saga Builder Constraints"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: saga
tags:
  - "rules"
  - "saga"
  - "P12"
llm_function: COLLABORATE
tldr: "Hard constraints and edge cases for saga builder."
8f: "F3_inject"
keywords:
  - "saga builder constraints"
  - "rules"
  - "saga"
  - "^p12_saga_[a-z][a-z0-9_]+$"
  - "retry"
  - "p12_saga_{name_slug}.md"
  - "p12_saga_{name_slug}"
  - "hard constraints"
  - "edge cases"
  - "naming rules"
density_score: null
related:
  - kc_saga
  - bld_manifest_saga
  - bld_memory_saga
  - bld_knowledge_card_saga
  - bld_quality_gate_saga
---
# Rules: saga Builder

## Hard Constraints
1. EVERY step MUST have a non-null compensating_action
2. steps_count MUST equal len(steps list)
3. topology MUST be specified: choreography | orchestration
4. on_failure MUST be specified at saga level
5. quality MUST be null
6. id pattern: `^p12_saga_[a-z][a-z0-9_]+$`
7. max_bytes: 4096 body

## Edge Cases
| Situation | Resolution |
|-----------|-----------|
| Step cannot be undone (e.g., send email) | Use idempotent compensation (send cancellation email) |
| User conflates with workflow | Teach: workflow has no compensation; saga does |
| User wants 2-phase commit | Redirect: 2PC for ACID; saga for eventual consistency |
| Saga too long (>10 steps) | Split into sub-sagas with handoff signals |
| Compensating action may fail | Mark as `retry` on_failure; compensating actions must be idempotent |
| Choreography vs orchestration unclear | Default to orchestration (easier to trace); document rationale |

## Naming Rules
- File: `p12_saga_{name_slug}.md`
- ID: `p12_saga_{name_slug}`
- Tags: MUST include "saga" + domain

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_saga]] | sibling | 0.48 |
| [[bld_manifest_saga]] | downstream | 0.45 |
| [[bld_memory_saga]] | sibling | 0.45 |
| [[bld_knowledge_card_saga]] | sibling | 0.44 |
| [[bld_quality_gate_saga]] | upstream | 0.43 |
