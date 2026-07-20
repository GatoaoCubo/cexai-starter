---
id: p01_kc_approval_request
kind: knowledge_card
8f: F3_inject
primary_8f: F3_inject
type: kind
pillar: P01
documents_kind: approval_request
documents_kind_pillar: P11
title: "approval_request: Human-Approval Request Instance"
version: 1.0.0
created: 2026-05-26
updated: 2026-07-03
author: n04
domain: approval_request
quality: null
open_vars: []
tags: [approval_request, p11, GOVERN, kind-kc, hitl]
tldr: "A runtime human-approval REQUEST INSTANCE emitted when a HITL-tagged operation is reached -- carries the gated operation, requester, expiry, and pending/approved/denied/timeout status"
when_to_use: "Building, reviewing, or reasoning about approval_request artifacts emitted by a HITL gate"
keywords: [approval, hitl, human-review, request-instance, pending, timeout, gate]
feeds_kinds: [approval_request]
density_score: null
related:
  - p01_kc_hitl_config
  - p01_kc_permission
  - kc_rbac_policy
  - kc_guardrail
  - kc_incident_report
---

# Approval Request

### How to use this card

```text
ROLE: you are reasoning about a HITL gate (8F: F3 INJECT this card; the kind
itself serves F7 GOVERN). Use the Decision Tree to pick the RIGHT kind first:
- Need a durable policy?  -> author hitl_config, not this.
- Need a standing grant?  -> author permission/rbac_policy (P09), not this.
- A gated op just fired?  -> an approval_request INSTANCE is emitted at runtime.
Then verify the instance against Quality Criteria (request_id + operation +
requester + expires_at + status-in-enum) and link it to its emitting policy +
audit trail. Note: PRIMARILY runtime-emitted by `ApprovalGate.request(...)` --
a 12-ISO builder now exists (`archetypes/builders/approval-request-builder/`,
2026-07-03 scaffold) strictly for the secondary fixture/audit-transcription
flow; it never replaces runtime emission as the canonical production path.
```

## Spec
```yaml
kind: approval_request
pillar: P11
llm_function: GOVERN
primary_8f: F7_govern
max_bytes: 2048
naming: p11_ar_{{name}}.yaml
core: false
depends_on: [hitl_config]
```

## What It Is
An `approval_request` is the runtime ARTIFACT INSTANCE emitted at the moment a
HITL-tagged operation is reached and execution pauses for human judgment. It is
the concrete, human-reviewable record of "the agent wants to do X; a human must
say yes/no before it proceeds". It captures the gated operation, who requested
it, when the decision window closes, and the current verdict state.

It is NOT a policy and NOT a capability. It is the per-event request that a
policy (`hitl_config`) produces and a human resolves. One `hitl_config` policy
emits MANY `approval_request` instances over its lifetime -- one per gated
operation attempt.

Spec provenance: `cexai-specs/05_agno/spec.md` US P2 + FR-004/005/006/010, Key
Entities (ApprovalRequest). Runtime shape: the frozen dataclass
`cexai.governance._shared.types.ApprovalRequest` (request_id, operation,
requester, expires_at, status).

## Boundary (the three-way distinction -- read before building)
| Kind | Pillar | Role | Cardinality | Lifetime |
|------|--------|------|-------------|----------|
| `hitl_config` | P11 | The POLICY: which operations are HITL-tagged, who reviews, timeout, escalation | One per workflow/domain | Durable config artifact |
| `approval_request` | P11 | The INSTANCE: one emitted record per gated operation attempt, awaiting a verdict | Many per policy | Ephemeral runtime event |
| `permission` | P09 | The GRANT: a standing access-permission rule a role/agent holds | One per capability grant | Durable authorization |

In one sentence: `hitl_config` decides *what needs approval*, `approval_request`
*is one such approval being requested right now*, and `permission` is *what an
actor is already allowed to do without asking*.

## Key Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| request_id | string | yes | Unique id of this request instance |
| operation | string | yes | The gated action, e.g. `publish_to_social_media` (US P2 test) |
| requester | string | yes | The nucleus / agent that attempted the operation |
| expires_at | ISO-8601 string | yes | Decision deadline; default policy 24h (US P2 #4) |
| status | enum | yes | `pending` \| `approved` \| `denied` \| `timeout` |

## Lifecycle
```
        emitted (HITL gate reached)
                 |
                 v
            [ pending ]
            /    |     \
   human    human     deadline
   approves  denies    passes
       |       |          |
       v       v          v
  [approved][denied]  [timeout]
   (proceed) (abort:   (abort:
             denied_   approval_
             by_human) timeout)
```
- `pending` is the only non-terminal state; a freshly emitted request always
  carries `pending`.
- `approved` -> the paused operation proceeds.
- `denied` -> the mission marks the step `denied_by_human` and aborts it.
- `timeout` -> the mission marks the step `approval_timeout` and aborts it.

## Cross-Framework Map
| Framework/Provider | Instance Concept | Notes |
|-------------------|------------------|-------|
| agno (source) | approval request at HITL-tagged op | The absorbed vertical 05 surface this kind documents |
| LangGraph | pending `interrupt()` payload | Graph paused at `human_node`; the interrupt value is the request |
| CrewAI | Task awaiting `human_input` | The specific task instance blocked on a human reply |
| AutoGen | pending `HumanProxyAgent` turn | The outstanding proxied request awaiting a human response |
| AWS Step Functions | `.waitForTaskToken` callback | A task token issued, paused until `SendTaskSuccess/Failure` |
| Temporal | Activity awaiting a signal | Human-task pattern: workflow blocks on an external signal |
| ServiceNow / Jira | approval ticket instance | One ticket per decision; approve/reject/SLA-breach states |

## Patterns
| Pattern | When to Use | Example |
|---------|-------------|---------|
| One-shot binary | Single approver, accept/reject | Publish action paused for one reviewer |
| M-of-N quorum | Multiple approvers required (policy FR-010) | 2-of-3 compliance officers must approve |
| Auto-expire abort | Unattended pipelines | 24h deadline -> `timeout` -> safe abort |
| Audit-linked | Regulated domains | Each request + verdict feeds an audit trail (runtime span / `audit_log`) |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Modeling the POLICY as an approval_request | Conflates durable config with an ephemeral event | Author a `hitl_config`; let it emit requests |
| Treating it as a `permission` grant | A request is asked-and-resolved, not a standing capability | Use `permission`/`rbac_policy` for standing grants |
| No `expires_at` | Pipeline blocks forever on an unanswered request | Always set a deadline; default 24h, abort on timeout |
| Mutating `status` away from a terminal state | `approved`/`denied`/`timeout` are final | Emit a NEW request for a re-attempt |

## Integration Graph
```
[hitl_config (policy)] --emits--> [approval_request (instance)]
                                          |
                          +---------------+---------------+
                          |               |               |
                     [approved]       [denied]        [timeout]
                          |               |               |
                   (operation       (step marked   (step marked
                    proceeds)        denied_by_     approval_
                                     human)         timeout)
                          |
                   [audit trail: runtime span / audit_log]
```

## Decision Tree
- IF you are defining WHICH operations need approval and who reviews -> author a
  `hitl_config` (policy), NOT an approval_request.
- IF you are granting a standing capability to a role -> author a `permission`
  (P09) under an `rbac_policy` (P09), NOT an approval_request.
- IF a HITL-tagged operation was just reached and a human must decide -> this is
  an `approval_request` instance (emitted by the gate at runtime).
- DEFAULT: an approval_request is RUNTIME-EMITTED by the HITL gate
  (`ApprovalGate.request(...)`), not builder-authored -- this remains the
  canonical production path (see `cexai/docs/adr_v03_governance_taxonomy.md`,
  which deliberately shipped without a builder for exactly this reason). A
  12-ISO builder was later scaffolded (`archetypes/builders/
  approval-request-builder/`, 2026-07-03, per `docs/
  DECISION_BUILDERLESS_KINDS_2026_07_03.md`) strictly for the secondary
  manual / fixture / test / audit-transcription flow -- use it ONLY when no
  runtime gate is emitting the instance for you.

## Quality Criteria
- GOOD: request_id + operation + requester + expires_at + status present; status
  in the canonical enum.
- GREAT: linked to its emitting `hitl_config`; verdict + actor + timestamp
  recorded to an audit trail; M-of-N quorum honored when the policy requires it.
- FAIL: no expiry; status outside the enum; conflated with policy or permission.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_hitl_config]] | upstream (the policy that emits this) | 0.62 |
| [[p01_kc_permission]] | sibling (capability grant -- contrast) | 0.40 |
| [[kc_rbac_policy]] | related (authorization context) | 0.36 |
| [[kc_guardrail]] | related (automated block vs human gate) | 0.31 |
| [[kc_incident_report]] | downstream (post-mortem after interventions) | 0.28 |
