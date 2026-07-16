---
kind: schema
id: bld_schema_approval_request
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for approval_request
pattern: TEMPLATE derives from this. CONFIG restricts this.
quality: null
title: "Schema Approval Request"
version: "1.0.0"
author: n03_builder
tags:
  - "approval_request"
  - "builder"
  - "schema"
  - "P11"
tldr: "Formal field definitions for approval_request artifacts: request identity, gated operation, expiry, status, and optional M-of-N context."
domain: "approval_request construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords:
  - "approval_request construction"
  - "schema approval request"
  - "request identity"
  - "gated operation"
  - "expiry"
  - "approval_request"
  - "builder"
  - "schema"
  - "^p11_ar_[a-z][a-z0-9_]+$"
  - "## overview"
density_score: 0.90
related:
  - bld_schema_hitl_config
  - bld_schema_permission
  - bld_schema_incident_report
  - bld_config_approval_request
---

# Schema: approval_request
## Frontmatter Fields
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p11_ar_{name}) | YES | - | Namespace compliance; per kinds_meta.json `naming` |
| kind | literal "approval_request" | YES | - | Type integrity |
| pillar | literal "P11" | YES | - | Pillar assignment |
| version | semver string | YES | "1.0.0" | Artifact versioning |
| created | date YYYY-MM-DD | YES | - | Creation date |
| updated | date YYYY-MM-DD | YES | - | Last update |
| author | string | YES | - | Producer identity |
| request_id | string | YES | - | Matches the frozen `ApprovalRequest.request_id`; real runtime format `appr-{12 hex}` |
| operation | string | YES | - | The gated action (e.g. `publish_to_social_media`) |
| requester | string | YES | - | The nucleus/agent/system that attempted the operation |
| expires_at | ISO-8601 string | YES | - | Decision deadline; production default policy 24h |
| status | enum: pending/approved/denied/timeout | YES | pending | `pending` is the only non-terminal state |
| emitting_policy | string (hitl_config id) | REC | - | Which `hitl_config` policy would emit/emitted this instance |
| scope | enum: fixture/audit_transcription | YES | - | Declares this artifact's authoring purpose (never omit) |
| approvers_required | integer | OPT | 1 | M in the M-of-N policy; omit for the 1-of-1 default |
| approvers_total | integer | OPT | 1 | N in the M-of-N policy; omit for the 1-of-1 default |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | - | Must include "approval_request" |
| tldr | string <= 160ch | YES | - | Dense summary |
| description | string <= 200ch | REC | - | What operation this instance gates and why |
## ID Pattern
Regex: `^p11_ar_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem. This is the CEX artifact id -- distinct from the runtime
`request_id` field (which follows the live gate's own `appr-{hex}` convention, per
`cexai/cexai/governance/hitl/file_gate.py:322`).
## Body Structure (required sections)
1. `## Overview` -- which operation is gated, why human judgment was required, who is affected
2. `## Request Detail` -- table: request_id, operation, requester, expires_at, status
3. `## Approval Context` -- emitting policy + M-of-N fields (when non-default) + recorded verdicts
4. `## Lifecycle` -- current state + the 3 terminal transitions and downstream effect
5. `## Scope Disclaimer` -- fixture vs audit_transcription, and confirmation this is NOT the live
   watch file at `.cexai/approvals/{request_id}.json`
## Constraints
- max_bytes: 2048 (body only) -- an instance is small (kinds_meta.json + ADR-recorded rationale)
- naming: `p11_ar_{name}.yaml` (compiled target; author in `.md`, compile via `cex_compile.py`)
- machine_format: yaml (compiled artifact)
- id == filename stem
- status MUST be one of: pending, approved, denied, timeout
- `scope` field MUST be present (fixture | audit_transcription) -- HARD requirement unique to this
  kind, because an authored instance could otherwise be mistaken for a live pending gate
- quality: null always
- depends_on: [hitl_config] -- SHOULD reference the emitting policy via `emitting_policy`
## Boundary Note (do not violate)
This SCHEMA governs the CEX ARTIFACT (a `.md`/`.yaml` documentation/fixture record). It does NOT
govern, replace, or write to the LIVE runtime watch file
(`.cexai/approvals/{request_id}.json`), which is exclusively owned by
`cexai.governance.hitl.file_gate.FileApprovalGate`. The two share a field vocabulary
(`request_id`/`operation`/`requester`/`expires_at`/`status`) by design -- they are NOT the same
file, and this builder never writes under `.cexai/approvals/`.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_hitl_config]] | sibling (emitting-policy schema) | 0.58 |
| [[bld_schema_permission]] | sibling (contrast: standing grant) | 0.45 |
| [[bld_schema_incident_report]] | sibling (contrast: post-mortem) | 0.42 |
| [[bld_config_approval_request]] | downstream | 0.38 |
