---
kind: quality_gate
id: p11_qg_unit_eval
pillar: P07
llm_function: GOVERN
purpose: Golden and anti-examples of unit_eval artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Unit Eval'
version: 1.0.0
author: builder
tags:
- eval
- P07
- quality_gate
- examples
tldr: 'Validates unit tests for agents and prompts: input, expected output, target
  component, and isolation.'
domain: unit_eval
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
keywords:
  - "unit eval"
  - "expected output"
  - "^p07_ue_[a-z][a-z0-9_]+$"
  - "unit_eval"
  - "quality"
  - "target"
  - "target_kind"
density_score: 0.85
related:
  - unit-eval-builder
  - bld_collaboration_unit_eval
  - bld_memory_unit_eval
  - bld_knowledge_card_unit_eval
  - p11_qg_validator
---
## Quality Gate

## Definition
A unit eval tests a single agent, prompt, or component in isolation. It defines an input, an expected output or assertion, the component under test, and setup and teardown steps. Unit evals must be deterministic, fast, and independent of external services. This gate ensures every unit eval is traceable, executable, and covers meaningful behavior rather than trivial cases.
## HARD Gates
Failure on any HARD gate causes immediate REJECT. No score is computed.
| ID  | Check | Rule |
|-----|-------|------|
| H01 | Frontmatter parses | YAML frontmatter is valid and complete with no syntax errors |
| H02 | ID matches namespace | `id` matches pattern `^p07_ue_[a-z][a-z0-9_]+$` |
| H03 | ID equals filename | `id` slug matches the parent directory or filename stem |
| H04 | Kind matches literal | `kind` is exactly `unit_eval` |
| H05 | Quality is null | `quality` field is `null` (not yet scored) |
| H06 | Required fields present | `target`, `target_kind`, `assertions` all defined and non-empty |
## SOFT Scoring
Score each dimension 0 or 10. Multiply by weight. Divide total by sum of weights, scale to 0-10.
| Dimension | Weight | Pass Condition |
|-----------|--------|----------------|
| Density >= 0.80 | 1.0 | Eval is tight; no filler prose or restatements of the obvious |
| Setup and teardown documented | 0.5 | `setup` and `teardown` steps are present even if empty (explicit null is acceptable) |
| Assertions are deterministic | 1.0 | Each assertion produces the same pass/fail result on every run |
| Coverage mapped to quality gates | 1.0 | Each assertion references at least one gate ID from the target's QUALITY_GATES.md |
| Isolation from external dependencies | 1.0 | No live API calls, file system writes, or database reads in the eval body |
| Tags include unit-eval | 0.5 | `tags` list contains `"unit-eval"` |
Sum of weights: 7.5. `soft_score = sum(weight * gate_score) / 7.5 * 10`
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — archive to pool as reference unit eval |
| >= 8.0 | PUBLISH — safe to run in CI and quality pipelines |
| >= 7.0 | REVIEW — runnable but coverage or isolation needs improvement |
| < 7.0 | REJECT — do not run; assertions are ambiguous or component not isolated |
## Bypass
| Field | Value |
|-------|-------|
| condition | Target component is under active construction and its interface is not yet stable; eval is written speculatively |
| approver | Engineer who owns the target component |
| audit_log | Entry required in `.claude/bypasses/unit_eval_{date}.md` with the expected stabilization date |
| expiry | Until the target component reaches PUBLISH score; eval must be updated and re-gated at that point |
H01 (frontmatter parses) and H05 (quality is null) cannot be bypassed under any condition.

## Examples

# Examples: unit-eval-builder
## Golden Example
INPUT: "Create unit eval for knowledge_card builder testing YAML parse gate"
OUTPUT:
```yaml
id: p07_ue_kc_yaml_parse
kind: unit_eval
pillar: P07
title: "Unit Eval: KC YAML Parse Gate"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
```
WHY THIS IS GOLDEN:
- quality: null (never self-scored)
- id matches p07_ue_ pattern
- kind: unit_eval
- 19 frontmatter fields present (all required + recommended)
## Anti-Example
INPUT: "Test the KC builder"
BAD OUTPUT:
```yaml
id: test_kc
kind: unit_test
quality: 7.5
target: KC

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
