---
id: batch
kind: instruction
pillar: P12
description: "Run many tasks in parallel worktrees. Usage: /batch <intents-file> [--workers N]"
quality: 9.1
title: "Batch"
version: "1.0.0"
author: n03_builder
tags: [instruction, command, parallel, worktree, boris_merge]
tldr: "Fan out N independent tasks across isolated worktrees via dispatch.sh swarm."
domain: "CEX system"
created: "2026-04-15"
updated: "2026-04-15"
density_score: 0.88
related:
  - p01_kc_git_worktree_isolation
  - dispatch
  - p06_ar_infra_apis
  - p01_kc_orchestration
---

# /batch — Parallel Worktree Execution

> Replaces the old `--tmux` stub with real `dispatch.sh swarm` + worktree isolation.

## Usage

| Form | Action |
|------|--------|
| `/batch intents.txt` | One line per task, default 3 workers |
| `/batch intents.txt --workers 6` | 6 concurrent worktrees |
| `/batch --swarm n03 5 "scaffold a landing page"` | 5 parallel n03 instances, same task |
| `/batch --kind landing_page 4` | 4 n03 instances building landing_page variants |

## Input Format

`intents.txt` -- one intent per line, blank lines ignored, `#` comment:

```
build a pricing page for SaaS
scaffold an onboarding flow for edtech
write 3 ad variants for black-friday
# skip: old intent, already shipped
research competitor pricing in legal-tech
```

## Execution Model

Each intent gets its own **git worktree** (isolation: worktree):

```
.cex/worktrees/batch_<timestamp>/
  cell_01/  (branch: batch/20260415-160000/cell_01)
  cell_02/
  cell_03/
  ...
```

One nucleus per cell, fully isolated. Merge strategy determined after wave.

## Invocation

Delegates to `dispatch.sh` (Mode X). For a same-runtime single-session batch, the
mode-resolving `/grid` (R-008) can run the heterogenous form as Mode W instead:
`Workflow({name: "grid", args: {mission: "BATCH_<id>", worktrees: true}})`.

```bash
bash _spawn/dispatch.sh swarm <kind> <N>         # N of same kind
bash _spawn/dispatch.sh grid BATCH_<id> -w       # heterogenous from intents
```

For heterogenous batches, /batch writes handoffs to
`.cex/runtime/handoffs/BATCH_<id>_cell_NN.md` then dispatches grid mode.

## Concurrency Guardrails

1. `--workers` clamps to `[1, 6]` (Claude Code) or `[1, 20]` (Ollama local)
2. Rate-limit-aware (opt-in, advisory): `_spawn/dispatch.sh` reads `CEX_RATELIMIT_GUARD=1` to enable a preflight guard -- unset (default) is a pure no-op; the guard tool itself (`cex_ratelimit_guard.py`) is Central-only and not shipped here
3. Auto-degrades: Sonnet -> Haiku if pool near cap (N01-N04 eligible)
4. Worktree count never exceeds `git worktree list` max (default 100)

## Merge Modes

| Mode | Semantics |
|------|-----------|
| `--merge-best` | Consolidator scores all cells, keeps highest quality |
| `--merge-all` | Every successful cell merged to main (check conflicts) |
| `--merge-none` | Leave worktrees for manual review |

Default: `--merge-best` for `--kind` batches, `--merge-all` for heterogenous.

## Cross-runtime

| Runtime | Swarm primitive |
|---------|-----------------|
| Claude Code | Task tool (subagent), or `_spawn/dispatch.sh swarm` / `grid -w` (git worktree) |
| Codex / Gemini / Ollama | `bash boot/cex_nucleus.sh n0X --cli {codex\|gemini\|ollama}` -- self-contained, no per-nucleus-per-CLI boot file needed (N07 also has dedicated `boot/cex_codex.ps1` / `boot/cex_gemini.ps1`) |
| Ollama (headless, no CLI) | `python _tools/cex_8f_runner.py --worktree` |

## Example

```
/batch intents.txt --workers 4 --merge-best
-> 12 intents, 4 worktrees, rolling pool
-> cell_01 done (quality=9.2, kept)
-> cell_02 done (quality=8.7, discarded)
-> ...
-> final: 5 artifacts merged, 7 discarded, 0 conflicts
```

## When NOT to use

- Single task -- use `/dispatch` directly.
- Tasks with dependencies -- use `/mission` (respects wave order).
- Shared-file edits -- use `.proposal` pattern, not parallel worktrees.


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_git_worktree_isolation]] | upstream | 0.38 |
| [[dispatch]] | sibling | 0.28 |
| [[p06_ar_infra_apis]] | upstream | 0.27 |
| [[p01_kc_orchestration]] | upstream | 0.25 |
