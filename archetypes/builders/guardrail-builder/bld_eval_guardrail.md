---
kind: quality_gate
id: p11_qg_guardrail
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of guardrail artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: guardrail"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, guardrail, safety, enforcement, security-boundary, P11]
tldr: "Validates guardrail artifacts: enforcement mode specificity, concrete violation examples, severity classification, and bypass policy."
domain: "guardrail — safety boundaries and enforcement policies applied to agents and artifacts"
created: "2026-03-27"
updated: "2026-07-04"
8f: "F7_govern"
keywords: [validates guardrail artifacts, enforcement mode specificity, concrete violation examples, severity classification, and bypass policy, quality-gate, guardrail]
density_score: 0.94
related:
  - bld_instruction_guardrail
  - p10_lr_guardrail_builder
  - p11_qg_quality_gate
  - guardrail-builder
  - bld_architecture_guardrail
---
## Quality Gate

# Gate: guardrail
## Definition
| Field     | Value |
|-----------|-------|
| metric    | composite score across SOFT dimensions |
| threshold | >= 7.0 to publish; >= 9.5 for golden |
| operator  | weighted average after all HARD gates pass |
| scope     | all artifacts where `kind: guardrail` |
All HARD gates are AND-logic: one failure rejects the artifact regardless of SOFT score.
Numbering matches `.claude/rules/8f-reasoning.md` (canonical) and `cex_8f_runner.py` (code)
exactly — renumbered 2026-07-04 (R-259) to fold the id/filename-stem check into H02 (both
are id-validity concerns) instead of inserting it as an extra gate that shifted everything
else out of sync with the canonical list.
## HARD Gates
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Any YAML syntax error |
| H02 | ID matches `^p11_gr_[a-z][a-z0-9_]+$` AND ID equals filename stem (no extension) | Wrong format/namespace, or mismatch between id field and file name |
| H03 | Kind equals literal `guardrail` | Any other value |
| H04 | `quality` field is null | Any non-null value |
| H05 | Required fields present: id, kind, pillar, title, version, created, updated, quality, tags, tldr | Any missing field |
| H06 | Body <= 4096 bytes (max_bytes) | Oversized body |
## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| S01 | `tldr` <= 160 chars, names protected boundary and enforcement mode | 0.09 | Named=1.0, vague=0.3 |
| S02 | Tags list len >= 3, includes severity level keyword | 0.05 | Met=1.0, partial=0.5 |
| S03 | Violations section has >= 2 specific, concrete examples | 0.13 | 2+=1.0, 1=0.5, 0=0.0 |
| S04 | Enforcement action describes exact system response (not just "block") | 0.12 | Precise=1.0, generic "block"=0.3 |
| S05 | Detection method specified (pattern match, LLM judge, static rule, regex) | 0.11 | Specified=1.0, absent=0.0 |
| S06 | Severity classification justified with written rationale | 0.09 | Justified=1.0, bare label=0.2 |
**Weight sum: 1.00**
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — reference artifact for guardrail calibration |
| >= 8.0 | PUBLISH — pool-eligible; enforcement, detection, and bypass documented |
| >= 7.0 | REVIEW — usable but detection method or false-positive risk missing |
| < 7.0  | REJECT — redo; likely no concrete violation examples or missing enforcement spec |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Severity is `low` or `medium` only AND guardrail blocks a critical production hotfix path |
| approver | Security lead; written sign-off required before bypass activates |
| audit trail | Required: security lead name, incident ID, timestamp, expected re-enable date |

## Examples

# Examples: guardrail-builder
## Golden Example
INPUT: "Create guardrail para prevenir que agents executem comandos destrutivos no filesystem"
OUTPUT:
```yaml
id: p11_gr_destructive_commands
kind: guardrail
pillar: P11
title: "Guardrail: Destructive Commands"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
```yaml
id: safety_guardrail
kind: guardrail
title: "Be Safe"
quality: 8.0
severity: "important"
enforcement: "stop"
## Rules
- Be careful with commands
- Don't do bad things
- Think before acting
## Bypass
Contact admin if needed.
```
FAILURES:
1. id: no p11_gr_ prefix -> H02 FAIL
2. pillar: missing -> H05 FAIL
3. quality: self-scored 8.0 instead of null -> H06 FAIL
4. severity: "important" not valid enum (must be critical/high/medium/low) -> H07 FAIL
5. enforcement: "stop" not valid enum (must be block/warn/log) -> H09 FAIL

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
