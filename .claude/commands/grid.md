---
description: "Execute a spec — dispatch nuclei autonomously (mode-resolving: in-session workflow or OS-window grid). Usage: /grid [spec_name]"
quality: null
title: "Grid"
version: "1.1.0"
author: n03_builder
tags: [artifact, builder, examples]
tldr: "Golden and anti-examples for CEX system, demonstrating ideal structure and common pitfalls."
domain: "CEX system"
created: "2026-04-07"
updated: "2026-07-02"
density_score: 0.90
related:
  - p12_wf_admin_orchestration
  - p06_enum_n07
  - skill_catalog_cex
  - component_map_n07
  - p06_ar_infra_apis
---

# /grid — Autonomous Execution

> **Input**: A `/spec` + decision manifest
> **What**: Dispatches nuclei to build everything in the spec
> **Output**: Artifacts built, committed, signaled
> **Next step**: `/consolidate`

## Mode Resolution

`/grid` is **mode-resolving**. It always dispatches nuclei autonomously by wave; what changed
(2026-07-02) is HOW. Two transports exist. Both run the full 8F pipeline per nucleus, both
signal into `.cex/runtime/signals/`, both end at `/consolidate`. Pick by falling through this
table top-to-bottom -- first matching row wins:

| Condition | Resolves to | Why |
|---|---|---|
| Non-Claude runtime needed (gemini / codex / ollama) | **X** | Workflow cells are Claude-Code-only |
| Detached, multi-hour autonomy (must outlive this session) | **X** | Workflow cells die with the session |
| Founder-launched OS windows (manual visibility/monitor) | **X** | OS-window spawn is dispatch.sh's mechanic |
| Sovereign tenant repo | **X** | tenants may run non-Claude runtimes with NO Workflow tool -- degrade-never |
| Unsure, or heavy multi-commit cells (>=3 cells, multi-commit each, or wall-clock >=5min) | **X**, with `-w` | race-window justifies OS-level worktree isolation; when in doubt, X is the safer failure mode. Full `-w` heuristic: `.claude/rules/n07-orchestrator.md` HOW TO DISPATCH |
| None of the above -- same-runtime, single-session | **W** (default) | cheaper + faster, no OS-window overhead |

**Default = Mode W.** Every mission that is (a) Claude-only, (b) bounded to this session's
wall-clock, and (c) not the tenant side runs Mode W unless it also trips the unsure/-w row.

Ratified: R-008 (founder, 2026-07-02). Full dispatch reference (all dispatch types, not just
grid): `.claude/rules/n07-orchestrator.md` HOW TO DISPATCH (same W/X split, sibling
documentation). Rationale in full: see "Why Mode W" below.

## Prerequisites

Before `/grid`, you need:
1. ✅ A plan (`/plan` or mental model)
2. ✅ Decisions made (`/guide` → `decision_manifest.yaml`)
3. ✅ A spec (`/spec` → `_docs/specs/spec_*.md`)

If any is missing, suggest the user run that step first. This gate applies to BOTH modes --
mode resolution happens AFTER prerequisites are satisfied, not instead of them.

---

## Mode W -- workflow-grid (default for same-runtime)

**What it is**: N07 executes the grid as a single **ultracode Workflow** -- a saved, named
workflow (`.claude/workflows/grid.js`) whose cells are in-session Sonnet subagents, one per
handoff. No OS window, no PID file, no `taskkill`. This is not a shortcut through 8F or through
the spec/manifest gate -- it is a transport change only; every cell still runs F1-F8 in full.

### How N07 dispatches Mode W

1. **Load spec + verify manifest.** Identical to Mode X Steps 1-2 below: same
   `_docs/specs/spec_*.md`, same `decision_manifest.yaml` gate. Nothing about mode changes the
   prerequisite check.
2. **Confirm handoffs exist on disk.** Same convention as Mode X: one file per cell at
   `.cex/runtime/handoffs/{MISSION}_{n0x}.md`, produced by `/guide` + `/spec` (or written
   directly). N07 does NOT need to enumerate them by hand -- the workflow's own Discovery phase
   (next step) does that.
3. **Invoke the saved workflow by name**, `grid` (`.claude/workflows/grid.js`):
   ```
   workflow("grid", { mission: "<MISSION_TOKEN>", nuclei: ["n03", "n05"], worktrees: <true|false>, model: "sonnet" })
   ```
   Only `mission` is required (must match `/^[A-Za-z0-9][A-Za-z0-9_-]*$/`, the same safe-token
   shape `dispatch.sh`'s handoff parser assumes). `nuclei` is an optional allow-list -- pass it to
   re-dispatch ONLY specific cells, the Mode W equivalent of Mode X Step 3's gate rule
   ("re-dispatch ONLY the failing nuclei with the gate feedback, then re-gate"). `worktrees`
   defaults `false`. `model` defaults `"sonnet"` (a cost-efficient default for most construction and
   audit work; escalate to `"opus"` per-invocation for money-touching / irreversible /
   keystone-verify work) and applies to every cell in the invocation, not per-cell.
4. **The workflow runs two phases internally** (source: `.claude/workflows/grid.js`):
   - **Discovery** -- one Sonnet agent globs `.cex/runtime/handoffs/{mission}_*.md`, parses each
     match's filename for an `n0[1-7]` token, and skips any file with none (a shared-context file
     like `{MISSION}_COMMON.md` -- a real pattern already on disk, e.g.
     `.cex/runtime/handoffs/CAPGEN_COMMON.md` -- is correctly not a cell). Zero matches is
     reported honestly (a `note` field, empty `cells` array) -- never fabricated.
   - **Execute** -- `parallel()` fans out one `agent()` call per discovered cell. Each cell reads
     ONLY its own handoff and is instructed to run it FULLY per 8F (F1 CONSTRAIN through F8
     COLLABORATE): produce every deliverable, compile it (`python _tools/cex_compile.py <path>`),
     then signal -- but explicitly **do NOT `git commit`** (the live prompt template's own
     words: "N07 consolidates after the whole wave"). This is the design choice that removes the
     concurrent-commit race Mode X's `-w` exists to solve: Mode W cells never touch the git index
     at all; only N07 does, once, after every cell in the wave has returned.
5. **Signal, the same call shape a spawned nucleus uses:**
   ```bash
   python -c "from _tools.signal_writer import write_signal; write_signal('n0X', 'complete', <F7_score>, '<MISSION>')"
   ```
   (the mission positional arg maps onto `signal_writer.write_signal`'s 4th parameter). The
   PRIMARY anti-fabrication guard here is NOT `signal_writer`'s `artifact_path`/`min_bytes` check
   -- the landed prompt template passes neither -- it is the workflow's structured return schema:
   every cell must return `{nucleus, ok, deliverables, summary, issues}`, and the prompt
   explicitly instructs "if the handoff cannot be read or a required gate fails, do not fabricate
   success: skip the complete signal ... and report `ok=false`". N07 still re-verifies
   independently at consolidation (step 8) rather than trusting a cell's self-reported `ok` at
   face value -- the same posture 8F Rule 4 (`quality: null`, never self-score) and the Working
   Discipline in `CLAUDE.md` already require. **Worth hardening, not yet done**: wiring
   `artifact_path`/`min_bytes` into the signal call would close the exact
   "signal-without-deliverable" gap (register row R-009) flags for Ollama grids,
   at near-zero cost -- flagged here as a follow-up, not claimed as already in place.
6. **Worktree isolation (`-w` equivalent) is a harness primitive, not a cell-authored sequence.**
   `worktrees: true` sets `isolation: 'worktree'` on every cell's underlying `agent()` call --
   the workflow engine handles entering/exiting the worktree around the cell; it is not a
   manually sequenced `EnterWorktree`/`ExitWorktree` pair inside the cell's own prompt.
   > **What's still open**: since cells never commit (step 4), per-cell worktree isolation
   > protects concurrent FILE WRITES, not concurrent commits -- and exactly how N07's single
   > post-wave commit reconciles N cells' isolated, uncommitted working-tree changes back into
   > one tree is internal to the workflow engine and not something this doc can verify from
   > outside it. R-008 itself was still `in-flight` at ratification time, marked "done
   > after N07 smoke+commit" -- this exact path is pending its first real verification, not yet a
   > proven mechanism the way Mode X's `-w` is. Smoke-test `worktrees: true` on a small,
   > low-stakes mission before trusting it on anything hydration-class.
7. **N07 receives ONE structured result for the whole wave**, not a per-cell stream:
   `{ mission, cells_ok, cells_total, results: [{nucleus, ok, deliverables, summary, issues}, ...], note? }`.
   There is no per-cell polling and no per-cell notification -- the workflow's `parallel()` call
   awaits every cell before returning once. N07 should still not block its own turn waiting on a
   long wave (same non-blocking posture as any other tool call), but the unit of "did it finish"
   is the WAVE, not the cell -- unlike Mode X, where Step 4's polling checks in on individual
   nuclei mid-flight.
8. **Consolidation is the SAME N07 keystone protocol, with one addition.** Read every
   `results[].ok`/`issues` yourself -- do not take `ok: true` on faith (8F Rule 4) -- then run the
   Consolidate Protocol from `.claude/rules/n07-orchestrator.md`: verify deliverables on disk ->
   `cex_doctor.py` (0 FAIL) -> `cex_score.py --apply` -> **`git add` + ONE `git commit` covering
   the whole wave** (present in Mode W but not Mode X, because Mode W cells never commit
   themselves) -> archive signals -> report. No OS PID to `taskkill`/`stop` -- a Workflow cell's
   process lifetime is the cell itself; nothing survives it to clean up.

### Example: the 3-wave sequence from Mode X Step 3, run as Mode W

```
# Wave 1 (sequential -- must complete first): single-cell workflow invocation
workflow("grid", { mission: "WAVE1_BRAND" })

# Wait for the wave's single structured return (not per-cell, do not poll)...

# Wave 2 (parallel -- can run together): multi-cell workflow invocation
workflow("grid", { mission: "WAVE2", worktrees: true })   # smoke-test worktrees:true first -- see step 6's flag

# Wave 3 (after wave 2 completes)
workflow("grid", { mission: "WAVE3_DEPLOY" })

# Re-dispatch ONLY a failing cell after a red gate (Mode W equivalent of Mode X's
# "re-dispatch ONLY the failing nuclei" gate rule):
workflow("grid", { mission: "WAVE2", nuclei: ["n05"] })
```

### Degraded fallback (Workflow tool unavailable)

If the harness cannot invoke the saved workflow (tool disabled, environment limitation), N07
self-executes the waves sequentially, in-session, with no cells and no parallelism. This is the
ORIGINAL pre-mode-resolution fallback and still applies verbatim -- preserved, not deleted:

> If no spawn/grid infrastructure (single session), execute waves sequentially yourself:
> 1. Wave 1: build artifacts for nucleus A
> 2. Wave 2: build artifacts for nuclei B+C
> 3. Wave 3: build artifacts for nucleus D
> 4. After each wave: compile + doctor + commit

This is a last resort, not Mode W proper -- it has none of Mode W's parallelism, signal
discipline, or worktree isolation. If the Workflow tool is unavailable but `_spawn/dispatch.sh`
still works, prefer Mode X over this fallback.

---

## Mode X -- OS-window spawn (cross-runtime / detached / tenant-side)

> Mode X is NOT deprecated. It remains the only path for cross-runtime, detached-autonomy, and
> tenant-side dispatch (sovereign repos have no Workflow tool -- degrade-never). Everything below
> is unchanged from before mode-resolution existed; NEVER delete or weaken any of it.

### Step 1: Load spec

```bash
# Find the latest spec
ls -t _docs/specs/spec_*.md | head -1

# Or user specifies: /grid spec_n06_brand
```

Read the spec. Extract: waves, artifact list, nucleus assignments, dependencies.

Print the wave table so the plan is explicit before any dispatch:

```bash
python _tools/cex_wave_state.py plan --plan <plan.md>
```

### Step 2: Verify manifest exists

```bash
python _tools/cex_bootstrap.py --check
ls .cex/runtime/decisions/decision_manifest.yaml
```

If no manifest → warn: "No decisions on file. Nuclei will use defaults. Run `/guide` first?"

### Step 3: Dispatch by wave

Follow the spec's wave order. Respect dependencies.

```bash
# Wave 1 (sequential — must complete first)
bash _spawn/dispatch.sh solo n06 "Wave 1: brand identity — see spec"

# Wait for signal...

# Wave 2 (parallel — can run together)
bash _spawn/dispatch.sh grid WAVE2

# Wave 3 (after wave 2 completes)
bash _spawn/dispatch.sh solo n05 "Wave 3: deploy — see spec"
```

> **Mandatory between-waves gate.** A wave does NOT advance until the gate is GREEN:
> consolidate `verify` (only with `-w`) + `cex_doctor.py` (0 FAIL) + the per-nucleus quality
> floor. Run it at every boundary:
> `python _tools/cex_wave_state.py gate --mission <MISSION> --wave <n> [--worktree]`
> (rc 0 = advance; rc 2 = re-dispatch ONLY the failing nuclei with the gate feedback, then
> re-gate). NEVER advance past a red gate. Full loop: `.claude/skills/wave_run.md`.

### Step 4: Monitor

```bash
bash _spawn/dispatch.sh status
git log --oneline -10
ls -lt .cex/runtime/signals/ | head -5
```

### Step 5: Report progress

As each nucleus signals complete:

```
━━━ Grid Progress ━━━
  Wave 1: N06 brand ████████████ DONE (q=9.0)
  Wave 2: N02 frontend ████████░░ 80%
  Wave 2: N01 research ████████████ DONE (q=9.0)
  Wave 3: N05 deploy ░░░░░░░░░░ WAITING
  ━━━ 2/4 nuclei complete ━━━
```

When all waves done → suggest: "All nuclei complete. Type `/consolidate` to verify and clean up."

---

## Why Mode W (R-008)

The founder ratified row **R-008** on 2026-07-02: adopt in-session
dispatch as the default posture for same-runtime, single-session missions, reserving OS-window
spawn for what genuinely needs a separate process. This is not novel to `/grid` -- it is the
synthesis of internal architecture research (Fable-Era Recommendations Tier 2),
independently converged on by 7 of the 8 per-nucleus study cards, and it is what the sovereign
tenant side has ALREADY been running as its ONLY dispatch model since before this rewrite
(`n07-orchestrator.tenant.md` ships no OS-window grid at all -- every `_spawn/dispatch.sh` doc
reference is mechanically rewritten to in-session Task-tool phrasing at distill time, per
`cex_distill.py:4225-4249`). This mission's own execution is the live proof: it is running as an
in-session ultracode Workflow, not a `dispatch.sh grid` call.

**The sovereignty constraint is why Mode X is permanent, not a legacy path being phased out.** A
distilled tenant repo may run on `codex`, `gemini`, or `ollama` with no Workflow tool at all --
degrade-never means Mode X's mechanism, docs, and scripts stay fully functional and fully
documented FOREVER, independent of how rarely Central itself takes that branch. Nothing in this
rewrite deletes, shortens, or defers a single Mode X instruction -- every one moved, none were
removed.

## Grid is AUTONOMOUS

Once dispatched, regardless of mode:
1. Nuclei read the spec + manifest
2. They follow 8F pipeline
3. They do NOT ask the user anything
4. They commit and signal when done
5. N07 monitors but does NOT intervene unless failure

> Bullet 4 has one mode-dependent nuance: in Mode X, each spawned nucleus commits its own work.
> In Mode W, cells signal but deliberately do NOT commit -- N07 commits once for the whole wave
> at consolidation (Mode W step 8 above). Both still "commit and signal when done" from the
> caller's point of view; only WHO performs the commit, and when, differs.

## Properties

| Property | Value |
|----------|-------|
| Kind | `` |
| Pillar |  |
| Domain | CEX system |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_wf_admin_orchestration]] | related | 0.41 |
| [[p06_enum_n07]] | related | 0.41 |
| [[skill_catalog_cex]] | related | 0.39 |
| [[component_map_n07]] | related | 0.39 |
| [[p06_ar_infra_apis]] | related | 0.38 |
