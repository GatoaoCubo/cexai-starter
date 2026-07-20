---
id: schedule_n07
kind: schedule
pillar: P12
title: "Schedule: Orchestrator Consolidation Sweep"
version: "1.0.0"
quality: null
tags: [schedule, orchestration, cron, consolidation]
nucleus: n07
created: "2026-07-20"
cron: "0 */2 * * *"
action: "bash _spawn/dispatch.sh status && python _tools/cex_doctor.py"
timezone: "{{tenant_timezone}}"
enabled: true
related:
  - p12_wf_admin_orchestration
---

# Schedule: Orchestrator Consolidation Sweep

| Field | Value |
|---|---|
| Trigger | `{{cron}}` (every 2h; adjust to mission cadence) |
| Action | Poll dispatch status + run doctor health check |
| On FAIL | Halt next dispatch wave; alert operator |
| On PASS | Log clean; proceed |
| Owner | n07 (orchestrator) |

Use for any recurring orchestration check -- signal sweep, stale-handoff
cleanup, doctor health -- that should run without a human triggering it.

## Related Artifacts

| Artifact | Relationship |
|----------|---------------|
| [[p12_wf_admin_orchestration]] | upstream -- the workflow this schedule triggers |
