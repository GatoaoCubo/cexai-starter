---
kind: schema
id: bld_schema_lifecycle_rule
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema — SINGLE SOURCE OF TRUTH for lifecycle_rule
pattern: TEMPLATE derives from this. CONFIG restricts this.
quality: null
title: "Schema Lifecycle Rule"
version: "1.0.0"
author: n03_builder
tags:
  - "lifecycle_rule"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for lifecycle rule construction, demonstrating ideal structure and common pitfalls."
domain: "lifecycle rule construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords:
  - "formal schema"
  - "lifecycle rule construction"
  - "schema lifecycle rule"
  - "lifecycle_rule"
  - "builder"
  - "examples"
  - "^p11_lc_[a-z][a-z0-9_]+$"
  - "## definition"
  - "## states"
  - "## transitions"
density_score: 0.90
related:
  - bld_schema_guardrail
  - bld_schema_scoring_rubric
  - bld_schema_golden_test
  - bld_schema_runtime_state
  - bld_schema_smoke_eval
---

# Schema: lifecycle_rule
## Frontmatter Fields
### Required
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p11_lc_{rule_slug}) | YES | — | Namespace compliance |
| kind | literal "lifecycle_rule" | YES | — | Type integrity |
| pillar | literal "P11" | YES | — | Pillar assignment |
| title | string "Lifecycle: {name}" | YES | — | Human label |
| version | semver string | YES | "1.0.0" | Versioning |
| created | date YYYY-MM-DD | YES | — | Creation date |
| updated | date YYYY-MM-DD | YES | — | Last update |
| author | string | YES | — | Producer identity |
| scope | string | YES | — | What artifact kind this rule governs |
| freshness_days | integer | YES | — | Days before artifact becomes stale |
| review_cycle | enum (weekly, monthly, quarterly, yearly) | YES | — | How often to re-evaluate |
| ownership | string | YES | — | Who is responsible for review |
| domain | string | YES | — | Domain this rule covers |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | — | Searchability |
| tldr | string <= 160ch | YES | — | Dense summary |
### Recommended
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| notification | enum (signal, email, log, none) | REC | signal | How staleness is communicated |
| automation | enum (full, semi, manual) | REC | semi | Level of automated transitions |
| linked_artifacts | object {primary, related} | REC | — | Cross-references |
| density_score | float 0.80-1.00 | REC | — | Content density |
## ID Pattern
Regex: `^p11_lc_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem.
## Body Structure (required sections)
1. `## Definition` — what artifact kind it governs and why freshness matters
2. `## States` — table of lifecycle states with entry criteria
3. `## Transitions` — table of state changes with triggers and actions
4. `## Review Protocol` — who reviews, when, what they check
5. `## Automation` — which transitions are automated vs manual
## Constraints
- max_bytes: 4096 (body only)
- naming: p11_lc_{rule_slug}.yaml
- id == filename stem
- freshness_days MUST be positive integer
- review_cycle MUST be valid enum
- States table MUST have >= 3 states
- Transitions table MUST have >= 3 transitions
- quality: null always

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_guardrail]] | sibling | 0.60 |
| [[bld_schema_scoring_rubric]] | sibling | 0.59 |
| [[bld_schema_golden_test]] | sibling | 0.58 |
| [[bld_schema_runtime_state]] | sibling | 0.58 |
| bld_schema_smoke_eval | sibling | 0.57 |
