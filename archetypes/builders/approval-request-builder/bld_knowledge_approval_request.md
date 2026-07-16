---
kind: knowledge_card
id: bld_knowledge_card_approval_request
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for approval_request production -- human-approval request instance specification
sources: cexai.governance._shared.types.ApprovalRequest (frozen dataclass), cexai.governance.hitl.file_gate.FileApprovalGate, LangGraph interrupt(), CrewAI human_input, AWS Step Functions waitForTaskToken
quality: null
title: "Knowledge Card Approval Request"
version: "1.0.0"
author: n03_builder
tags: [approval_request, builder, knowledge_card, P11]
tldr: "approval_request domain knowledge: request lifecycle, M-of-N resolution, real runtime mechanics (FileApprovalGate), and the fixture/audit-only scope of this builder."
domain: "approval_request construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F3_inject"
keywords: [approval_request construction, knowledge card approval request, request lifecycle, m-of-n resolution, real runtime mechanics, fixture audit scope]
density_score: 0.90
related:
  - approval-request-builder
---
# Domain Knowledge: approval_request
## Executive Summary
An `approval_request` is the runtime ARTIFACT INSTANCE emitted when a HITL-tagged operation is
reached and execution pauses for human judgment. It carries the gated `operation`, the
`requester`, the decision deadline (`expires_at`), and the current `status`. It is NOT a
`hitl_config` (the durable policy that emits MANY of these) and NOT a `permission` (a standing
grant). It is EMITTED, not normally authored -- this builder covers the secondary
fixture/test/audit-authoring flow only (see `adr_v03_governance_taxonomy.md`).
## Spec Table
| Property | Value |
|----------|-------|
| Pillar | P11 (Feedback/Governance) |
| llm_function | GOVERN |
| max_bytes | 2048 (an instance is small -- ADR-recorded) |
| naming | `p11_ar_{{name}}.yaml` (compiled target; author in `.md`) |
| depends_on | `hitl_config` (the emitting policy) |
| Status enum | pending / approved / denied / timeout |
| Terminal states | approved, denied, timeout (pending is the only non-terminal state) |
## Real Runtime Mechanics (the mechanism this artifact documents)
| Component | File | What it does |
|-----------|------|---------------|
| `ApprovalRequest` | `cexai/cexai/governance/_shared/types.py:154-167` | Frozen dataclass: request_id, operation, requester, expires_at, status |
| `ApprovalGate` Protocol | `cexai/cexai/governance/_shared/types.py:234-245` | `.request(op, requester) -> ApprovalRequest`; `.await_decision(request_id) -> str` |
| `FileApprovalGate` | `cexai/cexai/governance/hitl/file_gate.py` | v1 concrete gate: writes `{approvals_dir}/{request_id}.json`, default `.cexai/approvals/` |
| `record_verdict()` | `cexai/cexai/governance/hitl/approver.py` | Appends `{approver, verdict, token?}` to the watch file's `verdicts` list |
| `resolve_verdicts()` | `cexai/cexai/governance/hitl/file_gate.py` | Pure M-of-N resolution: single `deny` = veto -> `denied`; else `approved` once M distinct approvers recorded `approve` |
| `ApprovalDeniedError` / `ApprovalTimeoutError` | `cexai/cexai/governance/_shared/errors.py` | Raised by `await_or_raise()` on non-approval terminal states |
## Request ID Convention (runtime, NOT the CEX artifact id)
`FileApprovalGate.request()` mints `request_id = "appr-" + uuid4().hex[:12]` (e.g.
`appr-a1b2c3d4e5f6`). This is DIFFERENT from the CEX artifact `id` field, which follows the
`p11_ar_{{name}}` naming convention. When fixturing a fresh instance, both may share one slug; when
transcribing a REAL resolved request, `request_id` must match the live watch file's value exactly
while the CEX `id` still follows `p11_ar_{{name}}`.
## M-of-N Approval Policy
| Field | Meaning |
|-------|---------|
| approvers_required (M) | Distinct approvals needed before the action proceeds |
| approvers_total (N) | Size of the eligible approver set |
| approvers_roster | Optional allowlist -- an approve from outside it never counts toward M |
| Single deny | Always a VETO -- aborts to `denied` regardless of approval count |
## Lifecycle
```
        emitted (HITL gate reached)
                 |
            [ pending ]
            /    |     \
   human    human     deadline
   approves  denies    passes
       |       |          |
  [approved][denied]  [timeout]
   (proceed) (abort:   (abort:
             denied_   approval_
             by_human) timeout)
```
## Patterns
| Pattern | When to Use | Example |
|---------|-------------|---------|
| Fresh fixture | Demo tenant or regression test needs a seed instance | Seed `pending` request for a new HITL workflow demo |
| Audit transcription | A real resolved request needs a durable, human-reviewable record | Copy an already-`approved`/`denied`/`timeout` live watch file into a CEX artifact |
| M-of-N documentation | Multi-approver decision needs the tally recorded | 2-of-3 compliance officers approved; record which two |
| One-shot binary | Single approver, accept/reject | `approvers_required: 1, approvers_total: 1` |
## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Modeling the POLICY as an approval_request | Conflates durable config (one per workflow) with an ephemeral event (many per policy) | Author a `hitl_config` instead |
| Claiming this artifact IS the live watch file | The real record lives at `.cexai/approvals/{request_id}.json`, written only by `FileApprovalGate` | Always include the Scope Disclaimer (fixture vs audit) |
| No `expires_at` | Mirrors the live gate's own deadline requirement; a request with no deadline cannot be reasoned about | Always set a deadline, even on a terminal-state audit record |
| Mutating `status` away from a terminal state | `approved`/`denied`/`timeout` are final in the real mechanism | Author a NEW instance for a re-attempt, never edit a terminal one in place |
| Treating M-of-N fields as required | Real gate defaults to 1-of-1; only document the policy block when it is non-default | Omit `approvers_required`/`approvers_total` for the 1-of-1 default case |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[approval-request-builder]] | downstream | 0.39 |
