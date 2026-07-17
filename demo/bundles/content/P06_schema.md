---
kind: schema
id: bld_schema_knowledge_card
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema for knowledge_card — SINGLE SOURCE OF TRUTH
pattern: TEMPLATE derives from this. CONFIG restricts this. Never the inverse.
source: P01_knowledge/_schema.yaml v4.0 + validate_kc.py v2.0 + 721 real KCs
quality: null
title: "Schema Knowledge Card"
version: "1.0.0"
author: n03_builder
tags:
  - "knowledge_card"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for knowledge card construction, demonstrating ideal structure and common pitfalls."
domain: "knowledge card construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords:
  - "formal schema for knowledge_card"
  - "single source of truth"
  - "knowledge card construction"
  - "schema knowledge card"
  - "knowledge_card"
  - "builder"
  - "examples"
  - "^p01_kc_[a-z][a-z0-9_]+$"
  - "— yaml: topic"
  - "scope"
  - "owner"
  - "criticality 2."
  - "— bullets >= 3"
  - "concrete examples 3."
density_score: 0.90
related:
  - bld_schema_golden_test
  - bld_schema_retriever_config
  - bld_schema_axiom
  - bld_schema_action_prompt
  - bld_schema_output_validator
---

# Schema: knowledge_card
## Frontmatter Fields (Required — 14)
| Field | Type | Required | Default | Validator |
|-------|------|----------|---------|-----------|
| id | string (p01_kc_{slug}) | YES | — | H02, H03 |
| kind | literal "knowledge_card" | YES | — | H04 |
| pillar | literal "P01" | YES | — | H06 |
| title | string 5-100 chars | YES | — | H06, S03 |
| version | semver X.Y.Z | YES | "1.0.0" | H06, S04 |
| created | date YYYY-MM-DD | YES | — | H06, S05 |
| updated | date YYYY-MM-DD | YES | — | H06, S05 |
| author | string (not orchestrator) | YES | — | H06, H10 |
| domain | string | YES | — | H06 |
| quality | null | YES | null | H05 |
| tags | list[string], len 3-7 | YES | — | H07 |
| tldr | string <= 160 chars, must contain concrete data | YES | — | S01, S02 |
| when_to_use | string (specific context, not "when needed") | YES | — | H06 |
| axioms | list[string], len >= 1, ALWAYS/NEVER/IF-THEN form | YES | — | S18 |
## Frontmatter Fields (CEX Extended — 5)
| Field | Type | Required | Validator |
|-------|------|----------|-----------|
| keywords | list[string], len 2-5 (terms user would literally type) | REC | S16 |
| long_tails | list[string], len 2-3 (full natural-language phrases) | REC | S17 |
| linked_artifacts | object {primary, related} | REC | S14, S20 |
| density_score | float 0.80-1.00 | REC | — |
| data_source | URL or artifact ref | REC | S15 |
## ID Pattern
Regex: `^p01_kc_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem (H02). Underscores only.
## Naming Conventions (load-bearing filename populations)
The Regex above is the FORWARD gate for new ids -- it does not retroactively govern 6 populations
proven LOAD-BEARING or PATTERN-INADMISSIBLE by live breakage during the R-307 lane-4 rename sweep
(af9552aaaf reverted 191/383 renames after exactly this). `identity_doctor`
(`_tools/cex_check_registry.py`) carries the SAME 6 in its `EXEMPT_ID_CONVENTIONS` constant
(R-314): removed from the counted mismatch total, but always visible via `exempted_by_convention`.
| Population | Count | Example | Why exempt |
|---|---|---|---|
| `library/kind/kc_{kind}.md` (bare) | 156 | `kc_ab_test_config` | `load_kc_library()` globs `kc_*.md` by filename; ~14 _tools modules build this path from the kind name |
| `kc_oss_*` | 26 | `kc_oss_ruff` | `license_doctor` globs `kc_oss_*.md` |
| `kc_lens_*` | 8 | `kc_lens_bible` | `cex_teach_lesson.py` LENS_DIR builds `kc_lens_{lens}.md` |
| `kc_*_vocabulary` | 6 | `kc_intelligence_vocabulary` | `cex_distill._carry_vocabulary_kcs()` globs per nucleus |
| `kc_competitor_hermes` | 1 | (exact name) | `cex_hygiene.py` R09 hardcodes this filename |
| `kc_8f_*` (digit-leading) | 5 | `kc_8f_mode_a` | PATTERN-INADMISSIBLE: H02 needs `[a-z]` after the prefix; "8f" starts with a digit -- no rename can ever admit it |
None of the 6 is retroactively "fixed" here -- mirrors `bld_schema_output_template.md`'s own
"resolved not blessed" precedent (R-299). New knowledge_card ids still author against the Regex
above; this is a closed, cited exception list, not a precedent for new drift.
## Linked Artifacts Object
```yaml
linked_artifacts:
  primary: null            # or artifact_id
  related: [p01_kc_xxx]   # list of related ids
```
Both `primary` and `related` keys required (S20).
## Body Structure: domain_kc
1. `## Quick Reference` — yaml: topic, scope, owner, criticality
2. `## Key Concepts` — bullets >= 3, concrete examples
3. `## Strategy Phases` — numbered steps with outcomes
4. `## Golden Rules` — actionable rules >= 3
5. `## Flow` — text/ascii diagram
6. `## Comparativo` — comparison table
7. `## References` — artifact refs + URLs
## Body Structure: meta_kc
1. `## Executive Summary` — dense overview (2-3 sentences)
2. `## Spec Table` — key-value specs
3. `## Patterns` — what works
4. `## Anti-Patterns` — what fails
5. `## Application` — how to apply
6. `## References` — artifact refs + URLs
Density hierarchy (most to least info/token): tables > code blocks > bullet lists > ASCII diagrams > short paragraphs.
## Constraints
- max_bytes: 5120 (body) — H08. Covers 97%+ of 721 real KCs (p95=4274B)
- min_bytes: 200 — KCs below 200B are empty/stub
- min_bullets: 3
- density_min: 0.80
- bullet_max_chars: 80 — S10
- naming: p01_kc_{topic_slug}.md
- no internal paths (records/, .claude/, /home/) — H09
- no filler phrases — S09
- no self-references in tldr — S02

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_golden_test]] | sibling | 0.55 |
| [[bld_schema_retriever_config]] | sibling | 0.54 |
| [[bld_schema_axiom]] | sibling | 0.54 |
| [[bld_schema_action_prompt]] | sibling | 0.53 |
| [[bld_schema_output_validator]] | sibling | 0.53 |
