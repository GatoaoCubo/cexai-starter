---
kind: quality_gate
id: p11_qg_validation_schema
pillar: P06
llm_function: GOVERN
purpose: Golden and anti-examples of validation_schema artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Validation Schema'
version: 1.0.0
author: builder
tags:
- eval
- P06
- quality_gate
- examples
tldr: Validates post-generation contracts for field types, constraints, on_failure
  strategy, and system-only scope.
domain: validation_schema
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
keywords:
  - "validation schema"
  - "^p06_vs_[a-z][a-z0-9_]+$"
  - "validation_schema"
  - "quality"
  - "target_kind"
  - "fields"
  - "on_failure"
density_score: 0.85
related:
  - validation-schema-builder
  - p11_qg_validator
  - bld_collaboration_validation_schema
  - bld_knowledge_card_validation_schema
  - p11_qg_quality_gate
---
## Quality Gate

## Definition
A validation schema is a post-generation contract applied by the system after an artifact is produced. It defines fields, types, constraints, and violation behavior (reject, warn, auto-fix). The model never sees this schema; the pipeline enforces it. This gate ensures every validation schema is machine-enforceable, clearly bounded, and safe to apply automatically.
## HARD Gates
Failure on any HARD gate causes immediate REJECT. No score is computed.
| ID  | Check | Rule |
|-----|-------|------|
| H01 | Frontmatter parses | YAML frontmatter is valid and complete with no syntax errors |
| H02 | ID matches namespace | `id` matches pattern `^p06_vs_[a-z][a-z0-9_]+$` |
| H03 | ID equals filename | `id` slug matches the parent directory or filename stem |
| H04 | Kind matches literal | `kind` is exactly `validation_schema` |
| H05 | Quality is null | `quality` field is `null` (not yet scored) |
| H06 | Required fields present | `target_kind`, `fields`, `on_failure` all defined and non-empty |
## SOFT Scoring
Score each dimension 0 or 10. Multiply by weight. Divide total by sum of weights, scale to 0-10.
| Dimension | Weight | Pass Condition |
|-----------|--------|----------------|
| Density >= 0.80 | 1.0 | No prose restating what the field table already shows |
| Constraints are machine-enforceable | 1.0 | Each constraint is checkable by a program without LLM interpretation |
| on_failure justified per field | 1.0 | Each `on_failure` choice has a brief reason |
| Tags include validation-schema | 0.5 | `tags` contains `"validation-schema"` |
| Scope boundary explicit | 1.0 | Body states model never sees this schema; pipeline-only |
| Coercion rules for auto_fix | 0.5 | `on_failure: auto_fix` fields document the exact coercion |
Sum of weights: 8.0. `soft_score = sum(weight * gate_score) / 8.0 * 10`
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — archive to pool as canonical validation contract |
| >= 8.0 | PUBLISH — safe to apply in production generation pipelines |
| >= 7.0 | REVIEW — applicable but coercion rules or boundary need clarification |
| < 7.0 | REJECT — do not apply; constraints are ambiguous or on_failure is inconsistent |
## Bypass
| Field | Value |
|-------|-------|
| condition | Target kind is new with no prior instances; schema is a best-effort draft |
| approver | Engineer responsible for the target kind's builder |
| audit_log | Entry in `.claude/bypasses/validation_schema_{date}.md` listing unvalidated fields |
| expiry | 30 days or until 10 instances of the target kind exist |
H01 (frontmatter parses) and H05 (quality is null) cannot be bypassed under any condition.

## Examples

# Examples: validation-schema-builder
## Golden Example
INPUT: "Create validation_schema para knowledge_card output"
OUTPUT:
```yaml
id: p06_vs_knowledge_card
kind: validation_schema
pillar: P06
title: "Validation Schema: Knowledge Card"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
```yaml
id: output_schema
kind: schema
pillar: Schema
format: text
fields_count: 0
on_failure: maybe
quality: 9.0
tags: schema

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
