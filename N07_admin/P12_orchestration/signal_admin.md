---
id: p12_sig_admin_orchestration
kind: signal
pillar: P12
title: "Signal Protocol: Admin Orchestration"
version: "1.0.0"
quality: null
tags: [signal, orchestration, complete, error, progress]
8f: F8_collaborate
nucleus: n07
domain: orchestration
created: "2026-07-20"
tldr: "Signal protocol an orchestrator nucleus reads: complete/error/progress payloads with quality score, written to .cex/runtime/signals/."
related:
  - p12_ho_n07
  - p12_wf_admin_orchestration
  - signal-builder
---

# Signal Protocol: Admin Orchestration

## Required Fields

| Field | Type | Description |
|---|---|---|
| agent_group | string | Emitting nucleus slug (e.g. `n03`, `n07`) |
| status | string | `complete`, `error`, or `progress` |
| quality_score | float or null | 0.0-10.0, or null if not yet scored |
| timestamp | string | ISO 8601 datetime |

## Optional Fields

| Field | Type | Description |
|---|---|---|
| task | string | Short label of the related task |
| artifacts | array | Paths to produced artifacts |
| commit_hash | string | Git commit hash |
| error_code | string | Short error classifier |
| message | string | Brief context |
| progress_pct | integer | 0-100 |

## Emission

```bash
python -c "from _tools.signal_writer import write_signal; write_signal('{{nucleus}}', '{{status}}', {{score}}, '{{mission}}')"
```

## Example: Complete Signal

```json
{
  "agent_group": "{{nucleus}}",
  "status": "complete",
  "quality_score": 9.0,
  "timestamp": "{{iso_datetime}}",
  "task": "{{task_label}}",
  "artifacts": ["{{path_1}}", "{{path_2}}"],
  "commit_hash": "{{short_hash}}"
}
```

## Status Vocabulary

| Status | Meaning | Terminal | Quality Required |
|---|---|---|---|
| complete | Task finished | YES | YES (>= 8.0) |
| error | Task failed, needs intervention | YES | NO (null) |
| progress | Ongoing, partial update | NO | NO (null) |

## Consumer Contract

- MUST handle `agent_group`, `status`, `quality_score`, `timestamp`.
- MAY process optional fields; ignore any that are absent.
- MUST NOT assume the signal carries routing or execution instructions.
- MUST treat `quality_score: null` as "not yet evaluated."

## File Location

`.cex/runtime/signals/{{nucleus}}_{{status}}_{{timestamp}}.json`

## Related Artifacts

| Artifact | Relationship |
|----------|---------------|
| [[p12_ho_n07]] | upstream -- the handoff whose completion this signal reports |
| [[p12_wf_admin_orchestration]] | upstream -- the workflow step that polls for this signal |
| [[signal-builder]] | related -- builder agent for this kind |
