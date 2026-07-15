---
name: loop
description: ON-DEMAND recurring execution -- run a command/prompt on a cadence and STOP on a real condition (stop-file / max / a real quality verdict / error-triple). Fixed-interval drives the cex_loop_bridge engine; the self-paced idle branch uses ScheduleWakeup. Schedules NOTHING (no cron / Task Scheduler).
kind: skill
pillar: P12
nucleus: n07
quality: null
version: 1.0.0
created: 2026-06-24
related:
  - loop
  - monitor
  - wave_run
  - cex_loop_bridge
  - schedule
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_evolve, cex_loop_bridge. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# loop -- ON-DEMAND Recurring Execution

> **Mechanism**: two engines, one honest story. Fixed-interval runs through the testable bridge
> `python _tools/cex_loop_bridge.py run` (the in-session path that works); the idle, open-ended  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
> self-paced branch uses the harness `ScheduleWakeup` per iteration. **ON-DEMAND only** -- it runs
> only when N07/the founder invokes it and schedules NOTHING (no cron, no Windows Task Scheduler,
> no GitHub Action). For a true scheduled job, use `/schedule`.

This is the P5 loop. It closes the feedback wire the assess found missing: a quality verdict
(`cex_quality_monitor.py --below <floor>`) is now a real loop STOP CONDITION. The loop is bounded
(it ALWAYS terminates) and fail-closed + never-fabricating (it never invents "done").

## When this fires

- The user asks to repeat a command/prompt on a cadence ("keep evolving overnight", "run until
  stable", "poll the deploy every 5 min", `/loop 5m <cmd>`, `/loop <prompt>`).
- N07 wants a self-improving loop that STOPS on a real success verdict, not a guess.

For a SINGLE run, just run it once -- this skill's value is the bounded, stop-condition-driven
repeat. For a multi-WAVE mission, use `wave_run` instead (that loop gates between waves).

## Pick the branch (pacing -- reconciled with monitor.md)

| Situation | Branch | How |
|-----------|--------|-----|
| Fixed cadence, ACTIVE in-session (incl. during/around grids) | **bridge** | `cex_loop_bridge.py run --interval S` -- a fixed interval is what works in-session (same reason `monitor.md` uses a fixed `sleep 60`) |
| Idle, open-ended, LLM picks the next wake | **ScheduleWakeup** | the harness `ScheduleWakeup` per iteration -- idle-ONLY |

> This is ONE rule, not a contradiction: fixed-interval (the bridge) is the default; ScheduleWakeup
> is the idle-only branch. `monitor.md`'s "avoid ScheduleWakeup during an active grid" is the same
> rule -- never self-pace with ScheduleWakeup while a grid's Monitor is live (the wake fights it).

## The four stop conditions (the keystone -- checked after each iteration, in order)

1. **STOP-FILE** -- `.cex/runtime/loops/<id>.stop` exists. The kill-switch. `cex_loop_bridge.py
   stop <id>` (or `/loop stop <id>`) writes it; the loop stops at its next iteration boundary.
2. **MAX-ITERS** -- `--max <n>` iterations have run.
3. **SUCCESS** -- a REAL verdict reports done: `cex_quality_monitor.py --below <floor>` reports
   **0** artifacts below the target. NEVER-FABRICATE: a non-zero monitor exit, an unparseable
   count, or no `--floor` is NOT success -- the loop keeps looping. This is the closed feedback wire.
4. **ERROR-TRIPLE** -- 3 CONSECUTIVE non-zero command exits.

Plus a HARD backstop (1000 iterations) so an open-ended loop ALWAYS terminates -- reported
honestly as `stop_reason=hard_backstop`, never a silent cutoff. The loop is never unbounded.

## Branch A -- fixed interval (the bridge)

```bash
# Run a command every 30 min, stop when the quality floor is met (0 below 9.0), 3 errors, or --max.
python _tools/cex_loop_bridge.py run \  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
  --command "python _tools/cex_evolve.py --all" \  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
  --interval 1800 \
  --floor 9.0 \
  --max 20 \
  --id evolve_overnight

# Kill-switch (the STOP-FILE condition) -- stop a running loop on demand:
python _tools/cex_loop_bridge.py stop evolve_overnight  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```

- `--floor F` arms the success-stop (the loop stops the iteration the monitor reports 0 below F).
  OMIT `--floor` to disable the success-stop (then max / stop-file / error-triple bound it).
- `--interval S` paces the loop; OMIT it for a tight loop (still bounded by --max + the backstop).
- Per-loop audit lands in `.cex/runtime/loops/<id>.jsonl` (one record per iteration, ephemeral,
  gitignored). It logs BEFORE each stop check, so an aborted loop still has a complete trail.
- The bridge schedules NOTHING -- it loops in-process and returns. NEVER re-enable
  `.github/workflows/cron_evolve.yml`; NEVER register a host cron / Task Scheduler entry here.

## Branch B -- self-paced idle (ScheduleWakeup)

ONLY for an idle, open-ended loop where the LLM picks the next wake and NO grid Monitor is live.
Each iteration: do the work, evaluate the same stop conditions YOURSELF (run
`cex_quality_monitor.py --below <floor>` and stop when it reports 0), then `ScheduleWakeup` for
the next cadence (default idle 1200-1800s; avoid exactly 300s -- worst cache behavior).

```
iteration:
  1. run the command/prompt
  2. python _tools/cex_quality_monitor.py --below <floor>   # 0 below -> SUCCESS, stop (do NOT wake again)
  3. else ScheduleWakeup(seconds=1200..1800) and repeat     # idle-only; never during an active grid
```

Stop the self-paced branch by simply not scheduling the next wake once a stop condition is met.

## When NOT to use

- One-off tasks -- just run once.
- Work that blocks on user input -- loops must be autonomous.
- A real scheduled/cron job that must run when no session is open -- that is `/schedule`, NOT this
  (this is ON-DEMAND and runs only inside an invocation).
- A multi-wave mission -- use `wave_run` (it gates between waves).

## Anti-patterns

| Wrong | Right |
|-------|-------|
| Registering cron / Task Scheduler / re-enabling `cron_evolve.yml` for `/loop` | ON-DEMAND only -- the bridge loops in-process and schedules nothing |
| Declaring a loop "done" without a verdict | success-stop fires ONLY on a real `cex_quality_monitor --below <floor>` = 0 |
| Treating a monitor error / unparseable output as success | a non-checked verdict is NOT success -- keep looping (never-fabricate) |
| An unbounded `while true` loop | the bridge is bounded -- max / stop-file / error-triple / the hard backstop |
| ScheduleWakeup self-pacing DURING an active grid | fixed-interval bridge during grids; ScheduleWakeup is idle-only |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| loop | command | 0.85 |
| cex_loop_bridge | engine | 0.80 |
| monitor | sibling | 0.55 |
| wave_run | sibling | 0.50 |
| schedule | related | 0.40 |
