---
kind: quality_gate
id: p11_qg_feature_flag
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of feature_flag artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: feature_flag"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, feature-flag, toggle, rollout, P11]
tldr: "Validates feature_flag artifacts: toggle semantics, rollout strategy completeness, and kill switch safety."
domain: "feature_flag — on/off toggles with rollout percentage, cohort targeting, and kill switch behavior"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [cohort targeting, and kill switch behavior, validates feature_flag artifacts, toggle semantics, rollout strategy completeness, and kill switch safety, quality-gate]
density_score: 0.91
related:
  - feature-flag-builder
  - bld_schema_feature_flag
  - bld_architecture_feature_flag
---
## Quality Gate

# Gate: feature_flag
## Definition
| Field     | Value |
|-----------|-------|
| metric    | composite score across SOFT dimensions |
| threshold | >= 7.0 to publish; >= 9.5 for golden |
| operator  | weighted average after all HARD gates pass |
| scope     | all artifacts where `kind: feature_flag` |
All HARD gates are AND-logic: one failure rejects the artifact regardless of SOFT score.
## HARD Gates
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Any YAML syntax error |
| H02 | ID matches `^p09_ff_[a-z][a-z0-9_]+$` | Wrong format or namespace |
| H03 | ID equals filename stem (no extension) | Mismatch between id field and file name |
| H04 | Kind equals literal `feature_flag` | Any other value |
| H05 | `quality` field is null | Any non-null value |
| H06 | Required fields present: id, kind, pillar, version, created, updated, author, flag_name, default_state, category, rollout_percentage, quality, tags, tldr | Any missing field |
## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| S01 | `tldr` <= 160 chars, names flag and toggle behavior | 0.10 | Accurate=1.0, vague=0.4, absent=0.0 |
| S02 | Tags list len >= 3, includes `feature_flag` | 0.05 | Met=1.0, partial=0.5 |
| S03 | `flag_name` is snake_case and descriptive | 0.07 | Snake_case+descriptive=1.0, generic=0.3 |
| S04 | Rollout strategy has stages with explicit percentages | 0.12 | All stages=1.0, partial=0.5, absent=0.0 |
| S05 | Kill switch behavior documented | 0.10 | Explicit=1.0, implied=0.4, absent=0.0 |
| S06 | Cohort targeting rules defined when `rollout_percentage` < 100 | 0.10 | Defined=1.0, missing when needed=0.0, N/A=1.0 |
**Weight sum: 1.00**
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — reference artifact for feature_flag calibration |
| >= 8.0 | PUBLISH — pool-eligible; rollout strategy and kill switch documented |
| >= 7.0 | REVIEW — usable but missing sunset date or observability hook |
| < 7.0  | REJECT — redo; likely missing rollback procedure or cohort rules |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Hotfix rollout only; flag controls an active incident mitigation with no time to complete all gates |
| approver | Product owner or on-call engineer |
| audit trail | Required: incident ticket, timestamp, approver handle |
| expiry | 24 hours; must be replaced with compliant artifact |
| never bypass | H01 (corrupt YAML), H05 (self-scored quality is invalid), H08 (boolean semantics must be exact for runtime evaluation) |

## Examples

# Examples: feature-flag-builder
## Golden Example
INPUT: "Create a feature flag for the new search algorithm with gradual rollout"
OUTPUT:
```yaml
id: p09_ff_enable_vector_search
kind: feature_flag
pillar: P09
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
flag_name: "enable_vector_search"
```
## Flag Specification
Enables vector-based semantic search to replace legacy keyword search.
Default OFF — legacy keyword search serves all users until flag ramps.
Kill switch: set rollout_percentage to 0 to instantly revert to keyword search.
## Rollout Strategy
| Stage | Percentage | Duration | Criteria |
|-------|-----------|----------|----------|
| canary | 5% | 3 days | error rate < 0.1%, latency < 200ms |
| early | 25% | 4 days | no regressions, user feedback positive |
| broad | 50% | 3 days | metrics stable, no support tickets |
| full | 100% | permanent | retire flag after 2 weeks stable |
## Lifecycle
- Created: 2026-03-26 (flag defined, code deployed behind flag)
- Test: internal QA with flag ON in staging
- Ramp: canary 5% -> early 25% -> broad 50% -> full 100%
- Retire: 2026-05-01 (remove flag, vector search becomes default)
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p09_ff_ pattern (H02 pass)
- kind: feature_flag (H04 pass)
- 19 required+recommended fields present (H06 pass)
## Anti-Example
INPUT: "Add a feature flag for dark mode"
BAD OUTPUT:
```yaml
id: dark-mode
kind: flag
pillar: config
flag_name: Dark Mode Toggle
default_state: maybe
rollout_percentage: half
quality: 9.0
tags: [ui]
```
Turn on dark mode for users.
FAILURES:
1. id: "dark-mode" uses hyphens, no `p09_ff_` prefix -> H02 FAIL
2. kind: "flag" not "feature_flag" -> H04 FAIL
3. pillar: "config" not "P09" -> H06 FAIL
4. default_state: "maybe" not in enum [on, off] -> H08 FAIL
5. rollout_percentage: "half" not integer 0-100 -> H09 FAIL
6. quality: 9.0 (not null) -> H05 FAIL
7. Missing fields: version, created, updated, author, category, tldr -> H06 FAIL
8. tags: only 1 item, missing "feature_flag" -> S02 FAIL
9. Body missing ## Flag Specification, ## Rollout Strategy, ## Lifecycle -> H07 FAIL
10. flag_name uses spaces and uppercase (should be snake_case slug) -> S04 FAIL
11. No rollout strategy or lifecycle plan defined -> S05 FAIL

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
