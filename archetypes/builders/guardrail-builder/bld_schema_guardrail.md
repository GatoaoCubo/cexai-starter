---
kind: schema
id: bld_schema_guardrail
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema — SINGLE SOURCE OF TRUTH for guardrail
pattern: TEMPLATE derives from this. CONFIG restricts this.
quality: null
title: "Schema Guardrail"
version: "1.0.0"
author: n03_builder
tags:
  - "guardrail"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for guardrail construction, demonstrating ideal structure and common pitfalls."
domain: "guardrail construction"
created: "2026-04-07"
updated: "2026-07-04"
8f: "F1_constrain"
keywords:
  - "formal schema"
  - "guardrail construction"
  - "schema guardrail"
  - "guardrail"
  - "builder"
  - "examples"
  - "^p11_gr_[a-z][a-z0-9_]+$"
  - "## definition"
  - "## rules"
  - "## violations"
density_score: 0.90
related:
  - bld_schema_smoke_eval
  - bld_schema_golden_test
  - bld_schema_unit_eval
  - bld_schema_action_prompt
  - bld_schema_e2e_eval
---

# Schema: guardrail
## Frontmatter Fields

> **Tiering policy (R-259, 2026-07-04):** fields below are split ENFORCED (H05 gates on
> these -- see `bld_eval_guardrail.md` H05) vs RECOMMENDED (documented, encouraged, not
> gated). Verdict derived from an 18-artifact population audit: population >= 85% ->
> ENFORCED; below 85% -> RECOMMENDED. Dissent recorded: `scope`/`severity`/`enforcement`/
> `applies_to` are the semantic core of what a guardrail contract means and the population
> gap looks like incomplete rollout rather than archetype mismatch -- ship RECOMMENDED now
> (evidence-driven default), candidate to re-promote to ENFORCED once population crosses
> 85% honestly. Full evidence:
> `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md` Section 4.

### Required (ENFORCED — H05 gates on these 10)
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p11_gr_{scope_slug}) | YES | — | Namespace compliance |
| kind | literal "guardrail" | YES | — | Type integrity |
| pillar | literal "P11" | YES | — | Pillar assignment |
| title | string "Guardrail: {name}" | YES | — | Human label |
| version | semver string | YES | "1.0.0" | Versioning |
| created | date YYYY-MM-DD | YES | — | Creation date |
| updated | date YYYY-MM-DD | YES | — | Last update |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | — | Searchability |
| tldr | string <= 160ch | YES | — | Dense summary |
### Recommended (documented, encouraged, NOT H05-gated)
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| bypass_approver | string | REC | — | Who can override |
| remediation | string | REC | — | How to fix a violation |
| linked_artifacts | object {primary, related} | REC | — | Cross-references |
| density_score | float 0.80-1.00 | REC | — | Content density |
| author | string | REC | — | Producer identity |
| scope | string | REC | — | What this guardrail protects |
| severity | enum (critical, high, medium, low) | REC | — | Impact classification |
| enforcement | enum (block, warn, log) | REC | — | How violation is handled |
| applies_to | list[string] | REC | — | Agent kinds or pipeline stages |
| domain | string | REC | — | Domain this guardrail covers |
## ID Pattern
Regex: `^p11_gr_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem.

> **Status: LIVE-ENFORCED for new 8F builds (corrected 2026-07-04 -- the first
> draft said dormant; judge-refuted by execution, N07-reproduced).** H02 in
> `_tools/cex_8f_runner.py` extracts the backtick-labeled Regex line in this
> section (extraction at ~503-511) and the gate fires on every 8F run of this
> kind. The `_schema.yaml` `id_pattern` lane stays unpopulated/dormant, but
> that does not idle the gate. CONSEQUENCE: this regex binds every NEW
> guardrail build today, while 9/18 (50%) of the EXISTING corpus (the
> cybersec-distillation cluster + hand-named exceptions) predates the p11_gr_
> convention and would fail a retroactive check -- the dedicated id-rename
> sweep (register R-263) closes that gap. Full evidence:
> `.claude/rules/8f-reasoning.md` H02 note;
> `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md` Section 1.

> **Exemption: cybersec-derived corpus (explicit, never silent).** The 8
> guardrail files under `N05_operations/cybersec/` + `cybersec_distilled/`
> (`cybersec_*_p11_guardrail.md`, `p11_g_pii_output_filter.md`) are an
> externally-derived research corpus with its own derivation naming -- the
> same precedent already established for hydration accounting
> (`N05_CYBERSEC_EXEMPT_PREFIXES` in `_tools/cex_check_registry.py`;
> `docs/HYDRATION_MAP.md` Section 2, "N05 Cybersec Exemption"). They are never
> rebuilt via 8F, so H02 never fires on them. Register R-263 keeps their
> derivation naming EXEMPT-DOCUMENTED rather than renaming to `p11_gr_*` --
> the sweep renamed the hand-authored/genesis CORE corpus only (2 files).

## Body Structure (required sections)
1. `## Definition` — what it protects and why (threat model)
2. `## Rules` — numbered, concrete, measurable restrictions
3. `## Violations` — specific examples of what breaks this guardrail
4. `## Enforcement` — how violations are detected (automated/manual) and handled
5. `## Bypass` — conditions, approver, audit trail
## Constraints
- max_bytes: 4096 (body only)
- naming: p11_gr_{scope_slug}.md
- id == filename stem
- severity MUST be valid enum
- enforcement MUST be valid enum
- rules MUST be concrete (no subjective language)
- quality: null always

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_schema_smoke_eval | sibling | 0.61 |
| [[bld_schema_golden_test]] | sibling | 0.60 |
| [[bld_schema_unit_eval]] | sibling | 0.59 |
| [[bld_schema_action_prompt]] | sibling | 0.59 |
| bld_schema_e2e_eval | sibling | 0.59 |
