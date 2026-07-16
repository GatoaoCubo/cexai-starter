---
kind: instruction
id: bld_instruction_approval_request
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for approval_request
pattern: 3-phase pipeline (research -> compose -> validate)
quality: null
title: "Instruction Approval Request"
version: "1.0.0"
author: n03_builder
tags:
  - "approval_request"
  - "builder"
  - "instruction"
  - "P11"
tldr: "3-phase build process for approval_request: research the emitting policy + resolved state, compose a fixture/audit record, validate all HARD gates."
domain: "approval_request construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F6_produce"
keywords:
  - "approval_request construction"
  - "instruction approval request"
  - "research the emitting policy"
  - "compose a fixture record"
  - "validate all hard gates"
  - "approval_request"
  - "builder"
  - "instruction"
  - "quality: null"
  - "^p11_ar_[a-z][a-z0-9_]+$"
density_score: 0.90
related:
  - bld_knowledge_approval_request
  - bld_schema_approval_request
---
# Instructions: How to Produce an approval_request
## Phase 1: RESEARCH
1. Determine WHY you are authoring this artifact -- there are exactly two legitimate reasons:
   (a) a FRESH FIXTURE/SEED for a workflow with no live instance yet (demo tenant, regression
   test), or (b) an AUDIT TRANSCRIPTION of an ALREADY-RESOLVED real request (read its live watch
   file at `.cexai/approvals/{request_id}.json` if one exists, per `cexai/cexai/governance/hitl/file_gate.py`)
2. Identify the emitting `hitl_config` policy: which `workflow`, which `review_trigger` fired --
   this kind's only `depends_on` entry
3. Confirm this is genuinely an `approval_request` (a live, pending-or-resolved EVENT), not a
   `hitl_config` (the durable POLICY) or a `permission` (a standing grant) -- check the KC's
   Decision Tree (`N00_genesis/P01_knowledge/library/kind/kc_approval_request.md`)
4. Choose `operation`: the exact gated action string (e.g. `publish_to_social_media`) -- must
   match what the emitting policy names
5. Choose `requester`: the nucleus/agent/system that attempted the operation
6. Determine `status`: `pending` (fresh/still open) for a seed, or a TERMINAL value
   (`approved`/`denied`/`timeout`) if transcribing a resolved instance
7. If transcribing a resolved instance, gather the M-of-N context from the real watch file's
   `policy` block: `approvers_required`, `approvers_total`, and (if disclosed) the distinct
   approvers who recorded a verdict (`verdicts` list, per `cexai/cexai/governance/hitl/approver.py`)
8. Check existing approval_request examples in `P11_feedback/examples/` -- do not duplicate an
   existing fixture for the same workflow + operation
## Phase 2: COMPOSE
1. Read SCHEMA.md -- source of truth for all fields
2. Read OUTPUT_TEMPLATE.md -- fill the template following SCHEMA constraints
3. Fill all required frontmatter fields; set `quality: null` -- never self-score
4. Write **Overview** section: which operation is gated, why (link the emitting `hitl_config`
   policy by id), who is the requester
5. Write **Request Detail** section: `request_id`, `operation`, `requester`, `expires_at`,
   `status` -- as a table, matching the frozen `ApprovalRequest` dataclass field set exactly
6. Write **Approval Context** section: M-of-N policy (`approvers_required`/`approvers_total`),
   roster if applicable, and (if terminal) which distinct approvers recorded a verdict and when
7. Write **Lifecycle** section: current state + the 3 terminal transitions and their downstream
   effect (`approved` -> proceeds, `denied` -> `denied_by_human`, `timeout` -> `approval_timeout`)
8. Add **Scope Disclaimer** section: state explicitly whether this is a FIXTURE/SEED or an AUDIT
   TRANSCRIPTION, and confirm it does not shadow or duplicate a live
   `.cexai/approvals/{request_id}.json` file
9. Confirm body <= 2048 bytes (kinds_meta `max_bytes`) -- this is TIGHT for an instance kind; keep
   it terse, tables over prose
## Phase 3: VALIDATE
1. Check QUALITY_GATES.md -- verify each HARD gate manually
2. Confirm YAML frontmatter parses without errors
3. Confirm `id` matches `^p11_ar_[a-z][a-z0-9_]+$`
4. Confirm `status` is one of: `pending`, `approved`, `denied`, `timeout`
5. Confirm `expires_at` is a valid ISO-8601 timestamp
6. Confirm `request_id`, `operation`, `requester` are all non-empty strings
7. Confirm the Scope Disclaimer is present and honest (fixture vs audit-transcription)
8. Confirm `quality` is null
9. Confirm body <= 2048 bytes
10. Cross-check: does this describe ONE specific event, not a general policy? If it describes WHAT
    gets gated across many events, it belongs in `hitl_config`, not here
11. If score < 8.0: revise in the same pass before outputting

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_approval_request]] | upstream | 0.38 |
| [[bld_schema_approval_request]] | sibling | 0.35 |
