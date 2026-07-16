---
kind: quality_gate
id: p11_qg_response_format
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of response_format artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Response Format'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: 'Quality gate for LLM output structure specs: verifies format type, injection
  point, section definitions, and downstream parseability.'
domain: response_format
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
keywords: [response format, verifies format type, kind: response_format, yaml.safe_load(frontmatter), p05_rf_*, id.startswith("p05_rf_"), path(file).stem == id]
density_score: 0.85
---
## Quality Gate

## Definition
A response format artifact specifies the exact output structure an LLM must produce. It declares a format type (json, yaml, markdown, csv, or plaintext), an injection point where the spec is delivered to the model (system prompt or user message), and a section structure with field-level definitions. The artifact is consumed by the LLM at generation time — it is not a post-generation validator.
Scope: files with `kind: response_format`. Does not apply to validation schemas (P06), which check outputs after generation.
## HARD Gates
Failure on any single gate means REJECT regardless of soft score.
| ID  | Predicate | How to test |
|-----|-----------|-------------|
| H01 | Frontmatter parses as valid YAML | `yaml.safe_load(frontmatter)` raises no error |
| H02 | `id` matches namespace `p05_rf_*` | `id.startswith("p05_rf_")` is true |
| H03 | `id` equals filename stem | `Path(file).stem == id` |
| H04 | `kind` equals literal `response_format` | string equality check |
| H05 | `quality` is null at authoring time | `quality is None` |
| H06 | All required frontmatter fields present and non-empty | id, kind, pillar, title, version, created, updated, author, domain, tags, tldr all present |
## SOFT Scoring
Score each dimension 0 (absent or fails) to 1 (present and passes). Weights are 0.5 or 1.0.
| #  | Dimension | Weight |
|----|-----------|--------|
| 1  | `density_score` field present and >= 0.80 | 1.0 |
| 2  | Each section has explicit field definitions (name, type, required/optional) | 1.0 |
| 3  | At least one complete example output present for the declared format | 1.0 |
| 4  | Injection point matches the use case (system for persistent structure, user for per-request) | 1.0 |
| 5  | Format is parseable by a downstream consumer without ambiguity | 1.0 |
| 6  | Tags list includes `response-format` | 0.5 |
**Formula**: `final_score = (sum of score_i * weight_i) / (sum of weight_i) * 10`
Weight total: 9.0. Each dimension contributes proportionally. Score range: 0.0 to 10.0.
## Actions
| Tier | Threshold | Action |
|------|-----------|--------|
| GOLDEN | >= 9.5 | Publish to pool as golden; use as reference for format design |
| PUBLISH | >= 8.0 | Publish to pool; mark production-ready |
| REVIEW | >= 7.0 | Return to author with scored dimension feedback; one revision cycle allowed |
| REJECT | < 7.0 | Block from pool; full rewrite required before re-evaluation |
## Bypass
| Field | Value |
|-------|-------|
| condition | Format is under active negotiation with a new model provider whose output style is not yet finalized |
| approver | Domain lead must approve in writing before bypass takes effect |
| audit_log | Record in `records/pool/audits/bypasses.md` with date, approver, and reason |
| expiry | 14 days from bypass grant; format must reach full compliance once model behavior is confirmed |

## Examples

# Examples: response-format-builder
## Golden Example
INPUT: "Create response_format para knowledge_card output em YAML frontmatter + markdown"
OUTPUT:
```yaml
id: p05_rf_knowledge_card
kind: response_format
pillar: P05
title: "Response Format: Knowledge Card"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
```yaml
id: p01_kc_example_topic
kind: knowledge_card
pillar: P01
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
domain: "example"
quality: null
tags: [example, knowledge-card, template]
tldr: "Example KC showing expected output structure with all 7 sections"
## TL;DR
Example knowledge card demonstrating the response format structure.
## Core Concepts
- First key concept with concrete data
- Second key concept with specific reference
- Third key concept with actionable detail
## Patterns
- Pattern 1: when X, do Y (proven in context Z)
- Pattern 2: use A instead of B (measured 30% improvement)
## Anti-Patterns
- Anti-pattern 1: avoid X because Y (causes Z failure)
## Quick Reference
| Command | Purpose |
|---------|---------|
| `example_cmd` | Does specific thing |
## Injection Instructions
- **Point**: system_prompt
- **Position**: after identity rules, before task instructions
- **Template**: "When producing a knowledge_card, use the following output format:"
- **Composable**: false — KC format is self-contained

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
