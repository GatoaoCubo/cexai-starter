---
kind: quality_gate
id: p11_qg_approval_request
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of approval_request artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: approval_request"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, approval-request, human-review, hitl, instance, P11]
tldr: "Gates for approval_request: validates the 5 request-detail fields, status enum, terminal-state discipline, and the mandatory fixture/audit scope disclaimer."
domain: "approval_request -- runtime human-approval request INSTANCE with request_id/operation/requester/expires_at/status and a pending->terminal lifecycle"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F7_govern"
keywords: [request-detail fields, status enum, terminal-state discipline, scope disclaimer, gates for approval_request, human-approval request instance]
density_score: 0.92
related:
  - p01_kc_approval_request
  - bld_knowledge_card_approval_request
  - approval-request-builder
  - bld_instruction_approval_request
  - bld_schema_approval_request
---
## Quality Gate

# Gate: approval_request
## Definition
| Field | Value |
|-------|-------|
| metric | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator | AND (all HARD) + weighted_sum (SOFT) |
| scope | All artifacts where `kind: approval_request` |
## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID | Check | Failure message |
|----|-------|----------------|
| H01 | `quality` field is `null` | "Quality must be null at authoring time" |
| H02 | `id` matches `^p11_ar_[a-z][a-z0-9_]+$` | "ID fails approval_request namespace regex" |
| H03 | `kind` equals literal `"approval_request"` | "Kind is not 'approval_request'" |
| H04 | `pillar` equals literal `"P11"` | "Pillar is not 'P11'" |
| H05 | `status` is one of: pending, approved, denied, timeout | "status must be pending, approved, denied, or timeout" |
| H06 | `request_id`, `operation`, `requester`, `expires_at` all present and non-empty | "Missing a required ApprovalRequest field" |
| H07 | `scope` field present, one of: fixture, audit_transcription | "Missing scope disclaimer -- an authored instance must declare fixture vs audit, so it is never mistaken for a live pending gate" |
## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Request-detail completeness | 1.5 | All 5 ApprovalRequest fields present and internally consistent |
| Emitting-policy linkage | 1.5 | `emitting_policy` names a real or plausible `hitl_config` id; workflow named |
| Status/lifecycle correctness | 1.5 | Terminal states never mutated; `pending` used only for genuinely open instances |
| Scope honesty | 1.5 | Fixture vs audit_transcription disclosed and consistent with the rest of the body |
| M-of-N documentation (when non-default) | 1.0 | approvers_required/total present and internally consistent with recorded verdicts |
| expires_at realism | 1.0 | ISO-8601, in the future for `pending`, plausible for the workflow's SLA |
| No live-file impersonation | 1.0 | Never claims to be, or write to, `.cexai/approvals/{request_id}.json` |
| Boundary discipline | 1.0 | Never conflated with hitl_config, permission, or incident_report |
Weight sum: 1.5+1.5+1.5+1.5+1.0+1.0+1.0+1.0 = 10.0 (100%)
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
| conditions | None -- H07 (scope disclaimer) is never bypassed; a mislabeled instance risks being read as a live pending gate |
| approver | N/A -- see conditions |

## Examples

# Examples: approval-request-builder
## Golden Example (audit_transcription, illustrative)
INPUT: "Document the resolved approval for last week's production migration deploy -- 2 of 3
release approvers signed off"
OUTPUT:
```yaml
id: p11_ar_prod_migration_deploy_0091
kind: approval_request
pillar: P11
version: "1.0.0"
created: "2026-07-03"
updated: "2026-07-03"
author: "builder_agent"
request_id: "appr-9f3c7a1b2d4e"
operation: "deploy_production_migration"
requester: "n05_operations"
expires_at: "2026-06-27T18:00:00Z"
status: "approved"
emitting_policy: "p11_hitl_prod_deploy_review"
scope: "audit_transcription"
approvers_required: 2
approvers_total: 3
```
## Overview
A production database migration was HITL-tagged for release-team review before deploy. Human
judgment was required because an irreversible schema change cannot be safely scored by automated
checks alone. The approved verdict released the migration to the deploy pipeline.
## Request Detail
| Field | Value |
|-------|-------|
| request_id | `appr-9f3c7a1b2d4e` |
| operation | `deploy_production_migration` |
| requester | `n05_operations` |
| expires_at | `2026-06-27T18:00:00Z` |
| status | `approved` |
## Approval Context
Emitting policy: `p11_hitl_prod_deploy_review` (workflow: `production_release`).
| Field | Value |
|-------|-------|
| approvers_required (M) | 2 |
| approvers_total (N) | 3 |
| recorded verdicts | release_lead: approve, dba_oncall: approve |
## Lifecycle
Current state: **approved** (terminal). The migration proceeded to the deploy pipeline.
## Scope Disclaimer
This is an **audit_transcription**. It is NOT the live runtime watch file
(`.cexai/approvals/appr-9f3c7a1b2d4e.json`), which is owned by `FileApprovalGate`; fields above
were verified to match it exactly at transcription time.

WHY THIS IS GOLDEN:
- quality: null (H01 pass)
- id matches p11_ar_ pattern (H02 pass)
- kind: approval_request (H03 pass)
- status is a valid terminal enum value (H05 pass)
- all 5 ApprovalRequest fields present (H06 pass)
- scope disclosed as audit_transcription (H07 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
