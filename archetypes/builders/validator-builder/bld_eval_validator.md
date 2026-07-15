---
kind: quality_gate
id: p11_qg_validator
pillar: P06
llm_function: GOVERN
purpose: Golden and anti-examples of validator artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Validator'
version: 1.0.0
author: builder
tags:
- eval
- P06
- quality_gate
- examples
tldr: 'Validates technical pass/fail rules for artifact checking: condition structure,
  severity, and target kind.'
domain: validator
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
keywords:
  - "validates technical pass"
  - "condition structure"
  - "^p06_val_[a-z][a-z0-9_]+$"
  - "validator"
  - "quality"
  - "target_kind"
  - "conditions"
density_score: 0.85
related:
  - validator-builder
  - bld_output_template_validator
  - bld_schema_validator
  - bld_knowledge_card_validator
  - p03_ins_validator
---
## Quality Gate

## Definition
A validator defines one or more pass/fail rules applied to an artifact. Each rule has a condition (field, operator, value), a severity (error, warning, or info), and a target artifact kind. Validators do not score — they pass or fail. This gate ensures every validator is structurally sound, has actionable error messages, and is safe to run automatically.
## HARD Gates
Failure on any HARD gate causes immediate REJECT. No score is computed.
| ID  | Check | Rule |
|-----|-------|------|
| H01 | Frontmatter parses | YAML frontmatter is valid and complete with no syntax errors |
| H02 | ID matches namespace | `id` matches pattern `^p06_val_[a-z][a-z0-9_]+$` |
| H03 | ID equals filename | `id` slug matches the parent directory or filename stem |
| H04 | Kind matches literal | `kind` is exactly `validator` |
| H05 | Quality is null | `quality` field is `null` (not yet scored) |
| H06 | Required fields present | `target_kind`, `conditions`, `severity` all defined and non-empty |
## SOFT Scoring
Score each dimension 0 or 10. Multiply by weight. Divide total by sum of weights, scale to 0-10.
| Dimension | Weight | Pass Condition |
|-----------|--------|----------------|
| Density >= 0.80 | 1.0 | No prose restating what the condition table shows |
| Standard operators only | 1.0 | Operators from: `eq`, `neq`, `gt`, `lt`, `gte`, `lte`, `regex`, `in`, `not_in` |
| Severity justification present | 0.5 | Each severity level has a brief reason |
| Auto_fix feasibility noted | 0.5 | `auto_fix: true` conditions describe what the fix does |
| Bypass policy present | 0.5 | Body includes a bypass section, even if `bypass: null` |
| Tags include validator | 0.5 | `tags` contains `"validator"` |
Sum of weights: 7.5. `soft_score = sum(weight * gate_score) / 7.5 * 10`
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — archive to pool as reference validator |
| >= 8.0 | PUBLISH — safe to run in automated pipelines |
| >= 7.0 | REVIEW — runnable but error messages or pipeline placement needs clarification |
| < 7.0 | REJECT — do not run; conditions are ambiguous or severity is unjustified |
## Bypass
| Field | Value |
|-------|-------|
| condition | Validator targets a new artifact kind whose field structure is still being finalized; conditions may be temporarily incomplete |
| approver | Engineer who owns the target artifact kind |
| audit_log | Entry required in `.claude/bypasses/validator_{date}.md` listing which conditions are not yet enforced |
| expiry | Until target kind's QUALITY_GATES.md reaches PUBLISH score; validator must be updated at that point |
H01 (frontmatter parses) and H05 (quality is null) cannot be bypassed under any condition.

## Examples

# Examples: validator-builder
## Golden Example
INPUT: "Create um validator que garante que todo knowledge_card tem quality null"
OUTPUT:
```yaml
id: p06_val_kc_quality_null
kind: validator
pillar: P06
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
rule: "Knowledge card quality must be null"
conditions:
  - field: "quality"
    operator: "eq"
    value: null
    target: "frontmatter"
  - field: "kind"
    operator: "eq"
    value: "knowledge_card"
    target: "frontmatter"
error_message: "quality must be null — never self-score. Remove the numeric value and set quality: null."
severity: "error"
auto_fix: true
pre_commit: true
threshold: null
bypass:
  conditions: ["calibration run with known golden artifacts"]
  approver: "p06-chief"
  audit: true
logging: true
domain: "knowledge_card"
quality: 8.7
tags: [validator, knowledge-card, quality-null, pre-commit]
tldr: "Blocks knowledge_cards with non-null quality — self-scoring is forbidden."
density_score: 0.92
```
## Rule Definition
Every knowledge_card artifact MUST have `quality: null` in frontmatter.
Self-assigned quality scores corrupt the evaluation pipeline.
## Conditions
| # | Field | Operator | Value | Target |
|---|-------|----------|-------|--------|
| 1 | quality | eq | null | frontmatter |
| 2 | kind | eq | knowledge_card | frontmatter |
## Error Handling
- **Message**: quality must be null — never self-score. Remove the numeric value and set quality: null.
- **Severity**: error (blocks commit)
- **Auto-fix**: yes — set quality: null
- **Remediation**: Open file, find `quality:` line, replace value with `null`
## Bypass Policy
- **Conditions**: calibration run with known golden artifacts
- **Approver**: p06-chief
- **Audit**: always logged
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p06_val_ pattern (H02 pass)
- kind: validator (H04 pass)
- 22 required fields present (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
