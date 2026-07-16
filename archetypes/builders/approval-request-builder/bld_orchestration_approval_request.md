---
kind: collaboration
id: bld_collaboration_approval_request
pillar: P12
llm_function: COLLABORATE
purpose: How approval-request-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Approval Request"
version: "1.0.0"
author: n03_builder
tags: [approval_request, builder, collaboration, P12]
tldr: "approval-request-builder role in crews: fixture/audit instance documenter. Receives an emitting hitl_config + resolved (or seed) state. Produces a documented request instance. Depends on hitl_config."
domain: "approval_request construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F8_collaborate"
keywords: [approval_request construction, collaboration approval request, approval-request-builder role in crews, fixture audit instance documenter, receives emitting hitl_config, produces documented request instance, depends on hitl_config, approval_request, builder]
density_score: 0.90
related:
  - hitl-config-builder
  - bld_architecture_approval_request
---
# Collaboration: approval-request-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what does one specific human-approval event look like
-- the gated operation, the requester, the deadline, and the current verdict?"
I do NOT define the policy (that is `hitl_config`). I do NOT grant standing capabilities (that is
`permission`). I do NOT write the live runtime record (that is `FileApprovalGate`, Python code). I
document/fixture/audit-transcribe ONE instance of the SAME shape for test, demo, and audit-trail
purposes.
## Crew Compositions
### Crew: "AI Output Governance"
```
  1. hitl-config-builder       -> "the durable policy: which operations are HITL-tagged"
  2. approval-request-builder  -> "a fixture/audit instance of one such gated event"
  3. incident-report-builder   -> "post-mortem if the resolved instance was denied/timed out"
  4. learning-record-builder   -> "capture the audit trail as a training signal"
```
### Crew: "HITL Test Fixture Suite"
```
  1. hitl-config-builder       -> "the policy under test"
  2. approval-request-builder  -> "seed instances covering pending/approved/denied/timeout"
  3. scoring-rubric-builder    -> "criteria for whether the test suite exercises every status"
```
### Crew: "Governance Audit Trail"
```
  1. approval-request-builder  -> "audit_transcription of a resolved live request"
  2. audit-log-builder         -> "the durable SOC2-style log entry referencing it"
  3. incident-report-builder   -> "post-mortem for any denied/timeout outcome"
```
## Handoff Protocol
### I Receive
- seeds: the emitting `hitl_config` id/workflow, the gated `operation`, the `requester`, and
  whether this is a FRESH FIXTURE or an AUDIT TRANSCRIPTION of a real resolved instance
- optional: the live watch file's exact fields (`request_id`, `expires_at`, `status`, `policy`,
  `verdicts`) when transcribing a real request -- read-only, from `.cexai/approvals/{request_id}.json`
- optional: M-of-N context (approvers_required/total, roster) when non-default
### I Produce
- approval_request artifact (.md + .yaml frontmatter)
- committed to: `P11_feedback/examples/p11_ar_{name}.md`
- NEVER written to: `.cexai/approvals/**` (the live runtime path)
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons listed
- if a `hitl_config` cannot be identified as the emitting policy: signal a GDP flag (this may
  actually belong to a different kind -- re-check the Decision Tree)
## Builders I Depend On
| Builder | Why |
|---------|-----|
| hitl-config-builder | The emitting policy; my ONLY `depends_on` in kinds_meta.json |
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| incident-report-builder | A denied/timeout outcome may source a post-mortem from my record |
| learning-record-builder | Resolved requests feed training/improvement signals |
| audit-log-builder | A durable audit trail references the resolved instance |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[hitl-config-builder]] | upstream (emitting policy) | 0.40 |
| [[bld_architecture_approval_request]] | upstream | 0.34 |
