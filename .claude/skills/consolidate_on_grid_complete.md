---
name: consolidate-on-grid-complete
description: Run the Task tool stop and cex_score apply when all wave nuclei have signaled completion so VRAM frees and quality scores propagate without manual prodding.
kind: skill
pillar: P04
nucleus: n07
quality: null
version: 1.1.0
promoted: "2026-07-03"
related:
  - cross_wave_cleanup
  - n07-orchestrator
---

# Consolidate on Grid Complete

## When this fires

All wave nuclei have signaled completion (`.cex/runtime/signals/signal_{nucleus}_*.json`
present for every dispatched nucleus, or the Mode-W `grid` workflow returned its
structured per-cell results).

## What to do

Run the Consolidate Protocol (`.claude/rules/n07-orchestrator.md` Consolidate Protocol,
or `.claude/commands/consolidate.md` for the step-by-step form):

1. VERIFY -- deliverable files exist; read each nucleus's report.
2. GOVERN -- `python _tools/cex_doctor.py` (0 FAIL); `python _tools/cex_score.py --apply`
   if present.
3. STOP -- `bash _spawn/dispatch.sh stop` (kills only THIS session's idle nuclei; frees
   the resources the finished processes were holding).
4. COMMIT -- stage + commit the wave's work with an attributed message.
5. REPORT -- summarize what landed.

This stub stays in place so the autofire trigger path keeps resolving.
