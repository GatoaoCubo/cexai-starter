---
name: cross-wave-cleanup
description: Clean up wrapper PID trees and orphan runtime processes between waves of /mission, /grid, /showoff, or /batch so the next wave starts clean.
kind: skill
pillar: P04
nucleus: n07
quality: null
version: 1.1.0
promoted: "2026-07-03"
related:
  - cross_wave_cleanup
  - p01_kc_cex_orchestration_architecture
---

# Cross-Wave Cleanup

## When this fires

Between waves of `/mission`, `/grid`, or `/batch` -- before dispatching the next wave.

## What to do

1. Check `bash _spawn/dispatch.sh status` for any nucleus still marked RUNNING with no
   recent signal or commit (a stuck or orphaned wrapper).
2. Kill idle/orphaned processes: `bash _spawn/dispatch.sh stop` (session-scoped, safe --
   never touches another session's nuclei). Use `bash _spawn/dispatch.sh stop n0X` for a
   single stuck nucleus, or `--dry-run` to preview first.
3. Archive the completed wave's signals so the next wave's Monitor does not read stale
   ones: `mv .cex/runtime/signals/signal_n0*.json .cex/runtime/signals/archive/`.
4. Confirm `.cex/runtime/pids/spawn_pids.txt` no longer lists any PID from the
   just-finished wave before dispatching the next one.

This stub stays in place so the autofire trigger path, plus `n07-orchestrator.md`'s
lazy-skills pointer, keep resolving.
