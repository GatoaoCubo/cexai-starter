---
kind: architecture
id: bld_architecture_approval_request
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of approval_request -- inventory, dependencies, and architectural position
quality: null
title: "Architecture Approval Request"
version: "1.0.0"
author: n03_builder
tags: [approval_request, builder, architecture, P11]
tldr: "Component map for approval_request: request_id + operation + requester + expires_at + status + M-of-N context; governance layer P11; runtime-emitted primary path, builder-authored secondary path."
domain: "approval_request construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [and architectural position, approval_request construction, architecture approval request, component map for approval_request, governance layer p, runtime-emitted, builder-authored]
density_score: 0.90
related:
  - approval-request-builder
---
## Component Inventory
| Name | Role | Owner | Status |
|------|------|-------|--------|
| request_id | Unique id of this request instance (runtime format `appr-{12hex}`) | FileApprovalGate (runtime) / approval-request-builder (fixture/audit) | required |
| operation | The gated action string (e.g. `publish_to_social_media`) | Emitting `hitl_config` + requester | required |
| requester | The nucleus/agent/system that attempted the operation | Caller of `ApprovalGate.request()` | required |
| expires_at | ISO-8601 decision deadline | FileApprovalGate (24h production default) | required |
| status | pending / approved / denied / timeout | FileApprovalGate resolution (`resolve_verdicts`) | required |
| emitting_policy | Which `hitl_config` id would emit/emitted this instance | approval-request-builder (artifact-level; not a runtime dataclass field) | recommended |
| approvers_required / approvers_total | M-of-N policy | `ApprovalPolicy` dataclass | optional (default 1-of-1) |
| approvers_roster | Allowlist restricting which approver identities count toward M | `FileApprovalGate` (R-202) | optional |
| scope | fixture / audit_transcription -- declares this artifact's authoring purpose | approval-request-builder | required (unique HARD gate for this kind) |
## Dependency Graph
```
hitl_config (policy, P11)  --[review_trigger fires]-->  ApprovalGate.request(operation, requester)
                                                                    |
                                                        [ApprovalRequest emitted, status=pending]
                                                                    |
                                              FileApprovalGate writes .cexai/approvals/{request_id}.json
                                                                    |
                                    +-------------------------------+-------------------------------+
                                    |                                |                                |
                          [human/approver calls               [deadline passes,               [approval-request-builder
                           record_verdict()]                   no verdict]                     TRANSCRIBES the resolved
                                    |                                |                          file into a CEX artifact,
                          [resolve_verdicts() tallies]        status=timeout                    scope=audit_transcription]
                                    |                                |                                |
                     status=approved | status=denied         approval_timeout                 P11_feedback/examples/
                                    |                                                          p11_ar_{name}.md
                          operation proceeds | denied_by_human
```
| From | To | Type | Data |
|------|----|------|------|
| hitl_config (P11) | approval_request | upstream (emits) | `depends_on: [hitl_config]` -- the ONLY dependency |
| ApprovalGate.request() | approval_request | produces (runtime) | The frozen `ApprovalRequest` dataclass instance |
| approval_request | audit_log (P11) | downstream (consumed_by) | Resolved requests feed SOC2-style audit trails |
| approval_request | incident_report (P11) | downstream (consumed_by) | A `denied` or `timeout` outcome may trigger a post-mortem |
| approval-request-builder | approval_request (CEX artifact) | produces (fixture/audit only) | `.md`/`.yaml` documentation, NEVER the live watch file |
## Boundary Table
| approval_request IS | approval_request IS NOT |
|---------------|-------------------|
| A runtime human-approval REQUEST INSTANCE (one event) | A `hitl_config` (P11) -- the durable POLICY; one per workflow, emits MANY requests |
| Emitted by `ApprovalGate.request()` at the moment a HITL-tagged op is reached | A `permission` (P09) -- a standing capability grant, not asked-and-resolved per event |
| Carries request_id/operation/requester/expires_at/status | An `incident_report` (P11) -- written AFTER an intervention, not the live pending decision |
| PRIMARILY runtime-emitted; this builder covers the SECONDARY fixture/audit flow only | The live runtime watch file at `.cexai/approvals/{request_id}.json` (Python-owned, never builder-written) |
## Layer Map
| Layer | Components | Purpose |
|-------|------------|---------|
| Emission | request_id, operation, requester, expires_at | Created the instant a HITL-tagged operation pauses |
| Resolution | status, approvers_required/total, approvers_roster, verdicts | How the request reaches a terminal state |
| Documentation (this builder) | emitting_policy, scope | Fixture/audit-only CEX artifact layer, orthogonal to the live runtime path |
| Downstream | audit_log, incident_report, learning_record | What consumes a resolved request after the fact |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[approval-request-builder]] | downstream | 0.66 |
