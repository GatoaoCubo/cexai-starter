---
id: p11_qg_naming_rule
pillar: P11
llm_function: GOVERN
kind: quality_gate
domain: naming_rule
version: "1.0.0"
quality: null
title: "Gate: naming_rule"
author: "builder_agent"
tags: [quality-gate, naming-rule, P11, P05, governance, conventions]
tldr: "Gates for naming_rule artifacts — pattern, scope, case style, and collision resolution for consistent identifiers."
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.85
---
## Quality Gate

# Gate: naming_rule
## Definition
| Field     | Value                                          |
|-----------|------------------------------------------------|
| metric    | pattern validity + scope coverage + example completeness |
| threshold | 8.0                                            |
| operator  | >=                                             |
| scope     | all naming_rule artifacts (P05)                |
## HARD Gates
All must pass. Failure on any = final score 0.
| Gate | Check | Why |
|------|-------|-----|
| H01 | YAML frontmatter parses valid YAML | Broken YAML = rule silently ignored |
| H02 | id matches `^p05_nr_[a-z][a-z0-9_]+$` | Namespace compliance |
| H03 | id == filename stem | Brain search relies on this |
| H04 | kind == "naming_rule" | Type integrity |
| H05 | quality == null | Never self-score |
| H06 | All required fields present: id, kind, pillar, version, created, updated, author, domain, quality, tags, tldr | Completeness |
## SOFT Scoring
| Gate | Check | Weight |
|------|-------|--------|
| S01 | tldr <= 160 chars, non-empty, references scope and pattern | 1.0 |
| S02 | tags is list, len >= 3, includes "naming-rule" | 0.5 |
| S03 | density_score >= 0.80 | 0.5 |
| S04 | pattern is a valid regex (compiles without error) and tested against all examples | 1.0 |
| S05 | invalid_examples list has >= 2 entries with stated violation reason | 1.0 |
| S06 | separator field documented (hyphen, underscore, dot, none, or other) | 0.5 |
Weights sum: 9.0. Normalize: divide each by 9.0 before scoring.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — pool as canonical naming convention reference |
| >= 8.0 | PUBLISH — enforce in linting and authoring guides |
| >= 7.0 | REVIEW — tighten pattern, add missing examples or rationale |
| < 7.0  | REJECT — rework pattern definition and scope boundary |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Migration window requiring temporary dual-format support before full rename |
| approver | p05-chief |
| audit_trail | Log in records/audits/ with bypass reason, affected artifacts, and timestamp |
| expiry | 72h — rule must fully pass before expiry or migration reverts |
| never_bypass | H01 (YAML), H05 (quality null) |

## Examples

# Examples — Naming Rule Builder
## Golden Example: Knowledge Card Naming Rule
```yaml
id: p05_nr_knowledge_card
kind: naming_rule
pillar: P05
version: 1.0.0
created: "2026-03-26"
updated: "2026-03-26"
author: builder
scope: "Naming convention for knowledge card artifacts stored in the CEX pool under pillar P01"
pattern: "^p01_kc_[a-z][a-z0-9_]+\\.md$"
prefix: "p01_kc_"
suffix: ".md"
separator: "_"
case_style: snake_case
versioning: null
collision_strategy: reject
domain: knowledge_card
quality: 8.9
tags: [naming-rule, knowledge-card, p01, pool, convention]
tldr: "Naming rule for P01 knowledge card files: p01_kc_{topic_slug}.md in snake_case"
keywords: [knowledge_card, p01, kc, topic_slug, snake_case, pool, naming, convention]
density_score: REC
```
## Scope
Governs the file naming of all knowledge card artifacts (`kind: knowledge_card`) stored in the CEX artifact pool under pillar P01. Every file that constitutes a knowledge card must comply with this pattern.
Artifacts governed by this rule: `knowledge_card`
## Pattern Definition
**Regex**: `^p01_kc_[a-z][a-z0-9_]+\.md$`
**Human-readable**: Pillar prefix `p01_`, kind abbreviation `kc_`, followed by a topic slug in snake_case (lowercase letters and digits, segments separated by underscores), with `.md` extension.
**Segments**:
| Position | Segment | Required | Description |
|----------|---------|----------|-------------|
| 1 | `p01_` | yes | Pillar prefix — scopes artifact to knowledge layer |
| 2 | `kc_` | yes | Kind abbreviation — identifies artifact as knowledge card |
| 3 | `{topic_slug}` | yes | Snake_case descriptor of the knowledge topic |
| 4 | `.md` | yes | File extension — all knowledge cards are Markdown |
## Examples
**Valid**:
- `p01_kc_vector_search.md` — standard topic slug
- `p01_kc_pep8_style_guide.md` — multi-segment slug with digit
- `p01_kc_llm_context_window.md` — three-segment topic slug
**Invalid**:
- `kc_vector_search.md` — VIOLATES: missing pillar prefix `p01_`
- `p01_kc_VectorSearch.md` — VIOLATES: PascalCase in slug, must be snake_case
## Collision Resolution
Strategy: `reject`
If a file named `p01_kc_{topic_slug}.md` already exists, refuse to create a duplicate. Surface a naming conflict error to the caller. Resolution: either choose a more specific topic slug or update the existing knowledge card in place.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
