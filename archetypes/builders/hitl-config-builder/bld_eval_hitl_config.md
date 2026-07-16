---
kind: quality_gate
id: p11_qg_hitl_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of hitl_config artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: hitl_config"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, hitl-config, human-review, escalation, approval, P11]
tldr: "Gates for hitl_config: validates review trigger precision, escalation chain completeness, approval flow validity, timeout > 0, and safe fallback."
domain: "hitl_config -- human-in-the-loop approval flow configuration with review triggers, escalation chains, and timeout/fallback behavior"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [escalation chains, and timeout, fallback behavior, gates for hitl_config, validates review trigger precision, escalation chain completeness, approval flow validity]
density_score: 0.92
related:
  - hitl-config-builder
  - bld_schema_hitl_config
---
## Quality Gate

# Gate: hitl_config
## Definition
| Field | Value |
|-------|-------|
| metric | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator | AND (all HARD) + weighted_sum (SOFT) |
| scope | All artifacts where `kind: hitl_config` |
## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID | Check | Failure message |
|----|-------|----------------|
| H01 | `quality` field is `null` | "Quality must be null at authoring time" |
| H02 | `id` matches `^p11_hitl_[a-z][a-z0-9_]+$` | "ID fails hitl_config namespace regex" |
| H03 | `kind` equals literal `"hitl_config"` | "Kind is not 'hitl_config'" |
| H04 | `pillar` equals literal `"P11"` | "Pillar is not 'P11'" |
| H05 | `escalation_chain` list has >= 2 entries | "Escalation chain must have minimum 2 reviewers (single point of failure)" |
| H06 | `approval_flow` is one of: binary, edit, score | "approval_flow must be binary, edit, or score" |
## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Trigger precision | 1.5 | Condition is numeric threshold or enum match, not vague prose |
| Escalation chain completeness | 1.5 | Each level has role, SLA, and channel defined |
| Approval flow clarity | 1.0 | Each reviewer action is defined with downstream effect |
| Timeout sizing | 1.0 | timeout_seconds is realistic for the workflow SLA (not 0, not 999999) |
| Fallback safety | 1.0 | fallback_action is appropriate for the risk level of the workflow |
| Priority routing | 0.5 | High-risk outputs have priority_rules to fast-track to senior reviewers |
Weight sum: 1.5+1.5+1.0+1.0+1.0+0.5+0.5+1.0+0.5+0.5+0.5+0.5 = 10.0 (100%)
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool as golden exemplar |
| >= 8.0 | PUBLISH | Publish to pool |
| >= 7.0 | REVIEW | Flag for human review before publish |
| < 7.0 | REJECT | Return to author with failure report |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Prototype or exploratory workflow where escalation chain is not yet finalized |
| approver | Workflow owner approval required (written); timeout and fallback never bypassed |

## Examples

# Examples: hitl-config-builder
## Golden Example
INPUT: "Configure human review for AI-generated marketing copy before publishing"
OUTPUT:
```yaml
id: p11_hitl_marketing_copy_review
kind: hitl_config
pillar: P11
version: "1.0.0"
created: "2026-04-13"
updated: "2026-04-13"
author: "builder_agent"
workflow: "marketing_copy_generation"
```
## Overview
AI-generated marketing copy requires human review before publication to ensure brand voice consistency,
legal compliance, and accuracy of product claims.
Human judgment is required because brand safety and legal risk cannot be reliably scored by automated
metrics alone; a human reviewer catches edge cases that confidence scores miss.
Approved output is published to CMS; rejected output returns to generation pipeline with reviewer notes.
## Review Trigger
Review fires when model confidence is below threshold OR brand risk score is elevated.
| Trigger | Condition | Data Source | Notes |
|---------|-----------|-------------|-------|
| Low confidence | confidence < 0.85 | model output metadata | Covers uncertain generations |
| Brand risk | brand_risk_score > 0.6 | brand safety classifier | Covers borderline brand claims |
## Escalation Chain
| Level | Role | SLA (min) | Channel | Escalates When |
|-------|------|-----------|---------|---------------|
| L1 | content_reviewer | 60 | Slack #review-queue | No response in 60 min |
| L2 | brand_lead | 60 | Slack DM + email | No response from L1 in 60 min |
| L3 | legal_counsel | 60 | Email urgent | brand_risk_score > 0.8 OR no L2 response |
## Approval Flow
Flow type: **edit** -- reviewers may modify the copy, not just accept/reject.
| Action | Meaning | Downstream Effect |
|--------|---------|-------------------|
| approve | Copy is brand-safe and accurate | Released to CMS publish queue |
| edit + approve | Reviewer corrected copy | Edited version released; diff logged for training |
| reject | Copy fails brand/legal standard | Returned to generation with rejection reason |
## Timeout and Fallback
Timeout: **7200s** (2 hours, applies to each escalation level).
Fallback: **reject** -- unreviewed marketing copy is never auto-published; safety over availability.

WHY THIS IS GOLDEN:
- quality: null (H01 pass)
- id matches p11_hitl_ pattern (H02 pass)
- kind: hitl_config (H03 pass)
- escalation_chain has 3 roles: L1, L2, L3 (H05 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
