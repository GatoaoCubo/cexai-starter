---
id: p04_daemon_ops_maintenance
kind: daemon
8f: F8_collaborate
pillar: P04
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
name: "N05 Operations Maintenance Daemon"
schedule: "continuous; heartbeat 60s, orphan-cleanup 5m/30m, PID-hygiene 10m, compile-verify 15m, lock-rotate 1h, temp-cleanup 24h"
restart_policy: on_failure
signal_handling: "SIGTERM: complete active task, flush heartbeat, delete PID, exit 0"
quality: null
tags: [daemon, n05, operations, P04, system-health]
tldr: "N05 ops daemon: orphan reap, signal archival, PID hygiene, compile-verify, lock rotation, heartbeat 60s."
description: "Persistent background daemon maintaining .cex/runtime/ health: 7 staggered tasks keep processes reaped and .md/.yaml pairs in sync."
health_check: "n05_heartbeat.json every 60s; stale >3min = alert"
pid_file: ".cex/runtime/pids/n05_daemon.pid"
resource_limits: "memory_max: 128MB, cpu_percent: 5, max_open_files: 256"
monitoring: "heartbeat JSON; alert if stale >3min or error_count >3 per 10min"
logging: structured
graceful_shutdown: "finish active task, write heartbeat status=stopping, delete PID, exit 0"
max_restarts: "5 in 30min"
keywords: [ops daemon, orphan reap, signal archival, pid hygiene, lock rotation, daemon, operations, system-health, n05_heartbeat.json]
density_score: 1.0
related:
  - daemon-builder
  - bld_schema_daemon
  - nucleus_def_n05
  - p11_gr_untrusted_ingest
---

## Overview
N05's maintenance daemon keeps `.cex/runtime/` clean without a human watching it. Seven
staggered tasks run on independent intervals: orphan process reap, signal archival, PID
hygiene, temp cleanup, compile-verify, lock rotation, heartbeat. Gating Wrath in daemon
form -- nothing accumulates silently; every stale artifact gets reaped on a schedule.

## Lifecycle
Schedule: heartbeat 60s; orphan 5m/30m; PID-hygiene 10m;
compile-verify 15m; lock-rotate 1h; temp-cleanup 24h.
Startup: verify directories exist, write PID file, enter loop.
Restart: on_failure; backoff 1s -> 4s, cap 30s; max 5 restarts in 30min.
Shutdown: complete the active cycle, flush heartbeat, delete PID, exit 0.

## Signal Handling
| Signal | Response |
|--------|----------|
| SIGTERM | Flush heartbeat, delete PID, exit 0 |
| SIGINT | Same as SIGTERM |
| SIGHUP | Reload interval config, no restart |
| STOP_DAEMON file | Graceful exit on the next cycle |

## Monitoring
Health: `n05_heartbeat.json` written every 60s -- timestamp, last_task, error_count;
stale >3min triggers an orchestrator alert. Metrics tracked: orphans_reaped,
signals_archived, compile_flags, locks_released. Alert threshold: error_count >3 per
10min. Logging: structured JSON, `.cex/runtime/logs/n05_daemon.jsonl`, 7-day retention.

## Task Detail

| Task | Interval | Detection | Action |
|------|----------|-----------|--------|
| Heartbeat | 60s | write `n05_heartbeat.json` | timestamp + last_task + error_count |
| Orphan reap (fast) | 5m | process age > 2h with no signal | terminate + audit log entry |
| Orphan reap (deep) | 30m | walk process tree, match parentless workers | kill + audit log entry |
| Signal archive | 10m | signals dir file count > 50 | move to `.cex/runtime/archive/signals/` |
| PID hygiene | 10m | parse PID registry, verify each PID alive | remove stale lines, log |
| Compile verify | 15m | compare `.md` mtime vs `.yaml` mtime in `compiled/` | run `cex_compile.py` on drifted files |
| Lock rotate | 1h | locks older than 2h | delete stale locks, log |
| Temp cleanup | 24h | files in `.cex/runtime/tmp/` | purge files older than 48h |

## Resource Constraints

| Resource | Limit | Enforcement |
|----------|-------|-------------|
| Memory | 128MB RSS max | process memory cap |
| CPU | 5% sustained | yield between tasks (sleep) |
| Open files | 256 max | close handles after each task cycle |
| Disk writes | append-only JSONL | never overwrite audit logs |
| Error budget | 3 errors per 10min | exceed = pause 5min + alert orchestrator |

## Why a daemon (not a cron job or a hook)
A daemon is the right kind here because the work is **continuous supervision**, not a
single event (that would be a `hook`) or a one-shot run that terminates (that would be a
`cli_tool`). The heartbeat itself is the health signal -- absence of a heartbeat IS the
failure mode a daemon exists to surface.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[daemon-builder]] | upstream | 0.35 |
| [[bld_schema_daemon]] | upstream | 0.30 |
| [[nucleus_def_n05]] | upstream | 0.26 |
| [[p11_gr_untrusted_ingest]] | related | 0.22 |
