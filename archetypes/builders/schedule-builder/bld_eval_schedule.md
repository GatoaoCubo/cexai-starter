---
kind: quality_gate
id: p11_qg_schedule
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of schedule artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: schedule"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, schedule, P12, cron, temporal-trigger, workflow-ref]
tldr: "Pass/fail gate for schedule artifacts: cron validity, timezone declaration, workflow_ref resolution, and policy completeness."
domain: "workflow scheduling — temporal trigger definitions that start workflows at declared times"
created: "2026-03-29"
updated: "2026-03-29"
last_reviewed: "2026-04-18"
8f: "F7_govern"
keywords: [workflow scheduling, cron validity, timezone declaration, workflow_ref resolution, and policy completeness, quality-gate, schedule]
density_score: 0.90
related:
  - schedule-builder
  - bld_schema_schedule
---
## Quality Gate

# Gate: schedule
## Definition
| Field | Value |
|---|---|
| metric | schedule artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: schedule` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p12_sc_[a-z][a-z0-9_]+$` | ID has hyphens, uppercase, or wrong prefix |
| H03 | ID equals filename stem | `id: p12_sc_daily` but file is `p12_sched_weekly.md` |
| H04 | Kind equals literal `schedule` | `kind: cron` or `kind: trigger` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `trigger_type`, `cron`, or `workflow_ref` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Cron expression clarity | 1.0 | Plain-English explanation of the cron expression in ## Trigger section |
| Timezone declaration | 1.0 | Explicit IANA timezone; not defaulting silently to UTC |
| Workflow ref traceability | 1.0 | workflow_ref resolves to a known workflow id in the cex corpus |
| Policy completeness | 1.0 | catch_up, max_concurrent, jitter all declared with rationale |
| Enabled status documented | 0.5 | enabled field present; paused schedules explain why |
| Date range documented | 0.5 | start_date and end_date (or null) explicitly declared |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Placeholder schedule created during workflow scaffolding, not yet wired to real workflow |
| approver | Author self-certification with comment noting workflow_ref is pending |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 7d — placeholder schedules must be wired or removed |
| never_bypass | H01 (unparseable YAML), H05 (self-scored gates corrupt metrics), H07 (invalid cron fires at wrong time) |

## Examples

# Examples: schedule-builder
## Golden Example
INPUT: "Create a schedule that runs the daily sales report workflow every weekday at 9 AM Sao Paulo time"
OUTPUT:
```yaml
id: p12_sc_daily_sales_report
kind: schedule
pillar: P12
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "Daily Sales Report Schedule"
```
## Overview
Triggers the daily sales report workflow each weekday morning in Sao Paulo business hours.
Designed to fire after overnight data pipeline complete (~8:30 AM) with 60s jitter buffer.
## Trigger
- Expression: `0 9 * * MON-FRI` — 9:00 AM Monday through Friday
- Timezone: America/Sao_Paulo (UTC-3, UTC-2 during summer time)
- Enabled: true
- Trigger type: cron
## Workflow
- Workflow: `p13_wf_daily_sales_report`
- Expected duration: 8-12 minutes
- Dependencies: overnight ETL must complete before 9 AM; upstream tables: orders, products, costmers
## Policy
- Catch-up: false — missed days are not backfilled; report is generated on next scheduled run
- Max concurrent: 1 — workflow writes to shared reporting tables; parallel runs would corrupt output
- Jitter: 0-60s — staggers start against other 9 AM schedules sharing the same DB cluster
- On failure: alert — notify #data-alerts Slack channel; do not auto-retry (data consistency risk)

WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches `^p12_sc_[a-z][a-z0-9_]+$` (H02 pass)
- kind: schedule (H04 pass)
- cron: valid 5-field expression (H07 pass)

## Anti-Example
INPUT: "Create a schedule for the report workflow"
BAD OUTPUT:
```yaml
id: report-schedule
kind: trigger
pillar: orchestration
cron: every day at 9
workflow_ref: report
quality: 8.5
tags: [schedule]
```
Runs the report every day.
FAILURES:
1. id: "report-schedule" has hyphens and no `p12_sc_` prefix -> H02 FAIL
2. kind: "trigger" not "schedule" -> H04 FAIL
3. pillar: "orchestration" not "P12" -> H06 FAIL
4. cron: "every day at 9" is not a valid cron expression -> H07 FAIL
5. quality: 8.5 (not null) -> H05 FAIL
6. Missing fields: trigger_type, version, created, updated, author, tldr -> H06 FAIL
7. tags: only 1 item, missing "schedule" (needs >= 3) -> SOFT FAIL
8. No timezone declared — DST will shift schedule silently -> SOFT FAIL
9. No Policy section — catch_up, max_concurrent, jitter all absent -> SOFT FAIL
10. workflow_ref: "report" is not a resolvable id -> SOFT FAIL
11. Body missing ## Trigger, ## Workflow, ## Policy sections -> H10 FAIL

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
