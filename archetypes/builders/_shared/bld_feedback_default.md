---
quality: null
quality: null
id: bld_feedback_default
kind: builder_default
pillar: P11
source: shared
title: "Feedback Default: Universal Anti-Patterns"
tags:
  - "feedback"
  - "anti-patterns"
  - "P11"
  - "shared"
  - "default"
tldr: "_Shared feedback: anti-patterns, regression signals, and quality improvement triggers"
8f: "F7_govern"
keywords:
  - "feedback default"
  - "universal anti-patterns"
  - "shared feedback"
  - "regression signals"
  - "and quality improvement triggers"
  - "feedback"
  - "anti-patterns"
  - "shared"
  - "version: 1.1.0 quality: null"
  - "quality: null"
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-22"
related:
  - bld_eval_default
  - p11_fb_quality_gate
  - p11_fb_pattern
  - p11_fb_kind
  - p11_fb_data_contract
---
# P11 Feedback — Universal Anti-Patterns

## NEVER Do (Hard Rules)

| Anti-Pattern | Rule | Consequence |
|-------------|------|-------------|
| Self-score | Never assign quality score to own output | quality must stay `null` |
| Hallucinate | Do not invent facts, metrics, or paths | H05 gate fail |
| Non-ASCII in code | No emoji/accented chars in .py/.ps1/.sh | pre-commit hook rejects |
| Truncate output | No "..." or "continues below" in artifacts | H04 density fail |
| Skip frontmatter | Every artifact starts with valid YAML block | H01 gate fail |
| Override decisions | Never contradict decision_manifest.yaml | GDP protocol violation |

## Common Failure Modes (Universal)

1. **Vague body** -- lists of keywords instead of structured data with context
2. **Prose-only** -- paragraphs where tables belong (density drops below 0.85)
3. **Missing `version: 1.1.0
quality: null`** -- builder assigns its own score (audit catches this)
4. **Wrong pillar dir** -- artifact saved to P02 when kind belongs to P08
5. **Stale cross-references** -- references to files that no longer exist
6. **Over-engineering** -- adding sections not required by the schema

## Hard Gates (H01-H07) -- ALL must pass

| Gate | Check | Fail Action |
|------|-------|-------------|
| H01 | Frontmatter present and valid YAML | Return to F6, add frontmatter |
| H02 | `quality: null` in frontmatter (never self-score) | Remove score, set null |
| H03 | Required fields: id, kind, 8f, pillar, title | Add missing fields |
| H04 | Body density >= 0.85 (content lines / total lines) | Add structured data, remove filler |
| H05 | No hallucinated sources (cited paths must exist) | Remove or verify citations |
| H06 | ASCII-only in any generated code blocks | Replace non-ASCII per cex_sanitize rules |
| H07 | Output matches pillar schema constraints | Restructure to match schema |

## Scoring Dimensions (5D)

| Dimension | Weight | Criteria |
|-----------|--------|---------|
| D1 Structural | 30% | Frontmatter complete, naming correct, file in right pillar dir |
| D2 Content | 25% | Density >= 0.85, no filler, tables preferred over prose |
| D3 Accuracy | 20% | No hallucination, sources verified, constraints respected |
| D4 Usefulness | 15% | Actionable, implementable, unambiguous |
| D5 CEX fit | 10% | Kind/pillar/nucleus alignment, 8F stage correctness |

## Correction Protocol

```
F7 FAIL detected
  |
  +-- H01 fail -> add/fix frontmatter
  +-- H02 fail -> set quality: null
  +-- H03 fail -> add missing required fields (id, kind, 8f, pillar, title)
  +-- H04 fail -> replace prose with tables, add structured data
  +-- H05 fail -> remove unverified citations
  +-- H06 fail -> run cex_sanitize.py --fix
  +-- H07 fail -> restructure body to match pillar schema
  |
  v
Return to F6 (max 2 retries)
  |
  v
If still failing after 2 retries -> signal N07 with failure details
```

## Quality Signals Worth Logging

After any build where the following occurred, write a learning_record:
- First time building this kind (baseline observation)
- H gate failed twice on same issue (structural problem in builder)
- Score exceeded 9.5 (document what worked exceptionally well)

## Key Behaviors

- Builder MUST load all 12 ISOs (1:1 with pillars) before producing any artifact
- Builder MUST run F7 GOVERN quality gate before saving output
- Builder MUST compile output via cex_compile.py after saving (F8 COLLABORATE)
- Builder MUST signal completion with quality score to N07 orchestrator
- Builder MUST NOT self-score: quality field is always null in own output

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_default]] | sibling | 0.53 |
| p11_fb_quality_gate | sibling | 0.53 |
| [[p11_fb_pattern]] | sibling | 0.52 |
| p11_fb_kind | sibling | 0.52 |
| [[p11_fb_data_contract]] | sibling | 0.51 |
