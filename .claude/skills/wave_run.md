---
name: wave_run
description: In-session multi-wave mission loop -- dispatch grid per wave, Monitor, run the mechanical between-waves gate, advance only on GREEN. N07-facing; reuses Monitor + the cex_wave_state engine.
kind: skill
pillar: P12
nucleus: n07
quality: null
version: 1.0.0
created: 2026-06-24
related:
  - monitor
  - cex_wave_state
  - n07-orchestrator
  - p01_kc_orchestration_best_practices
  - p01_kc_cex_orchestration_architecture
---

> **[DISTILL ANNOTATION -- updated]** `cex_wave_state.py` is now shipped in this tenant (multi-orchestration carry). `cex_team_charter` remains Central-only; its one call below still carries an inline `[NOT SHIPPED in this tenant -- Central-only tool]` marker.

# wave_run -- The In-Session Multi-Wave Mission Loop

> **Mechanism**: N07 drives the live grid + the `Monitor` tool; the mechanical between-waves
> gate is `python _tools/cex_wave_state.py gate` (the testable engine). One governed multi-wave
> mission instead of hand-driving each boundary + re-deriving the gate from memory.

> **Mode note (R-008, 2026-07-02)**: this loop as written below is the MODE-X wave pattern
> (`_spawn/dispatch.sh` + Monitor + signals). For a Mode-W wave, dispatch via `Workflow({name: "grid",
> args: {mission}})` instead -- no Monitor needed (harness notifications + structured returns
> replace steps 3-4); the between-waves QUALITY gate (doctor + floor) still applies before the
> next wave. Mode resolution table: `.claude/commands/grid.md`.

This is the P3 mission loop. The user (or a plan) gives N07 a multi-wave mission; N07 runs each
wave as a grid, monitors with the Monitor primitive, and **never advances past a red gate**. The
gate is mechanical and fail-closed (see `cex_wave_state.py`): N07 does NOT re-derive it from
memory each time.

## When this fires

- A `/mission` or `/grid` whose plan has 2+ waves (`## Wave 1`, `## Wave 2`, ...).
- Any time N07 would otherwise hand-drive: dispatch -> monitor -> manual consolidate ->
  manually compose the next wave. Use this loop instead.

For a SINGLE wave, the plain Monitor + `/consolidate` is enough -- this loop's value is the
governed wave-to-wave advance.

## Step 0 -- Print the wave table (always first)

Resolve and SHOW the wave plan before dispatching anything:

```bash
python _tools/cex_wave_state.py plan --plan <plan.md>
```

This prints every wave + its unique nuclei (empty waves are DROPPED by the parser -- never
fabricated) and the HARD RULE: the between-waves gate must be GREEN before a wave advances.
Decide `-w` per wave using the `n07-orchestrator.md` rule (>= 3 cells AND multi-commit/long-running
-> add `-w`; same-file cells -> never `-w`).

## The loop (per wave)

```
for each wave W in the plan:
  1. WRITE handoffs            .cex/runtime/handoffs/{MISSION}_{n0X}.md  (+ copy to {n0X}_task.md)
  2. ARCHIVE stale signals     mv .cex/runtime/signals/signal_n0*.json .cex/runtime/signals/archive/
  3. DISPATCH the grid         bash _spawn/dispatch.sh grid <MISSION> [-w]
  4. MONITOR (persistent)      the Monitor loop below -- N07 keeps working between notifications
  5. on ALL-COMPLETE -> GATE   python _tools/cex_wave_state.py gate --mission <MISSION> --wave W [--worktree]
       rc 0 (PASS) -> consolidate this wave, ADVANCE to W+1
       rc 2 (FAIL) -> append the gate feedback to the FAILING nuclei's handoffs,
                      re-dispatch ONLY those, re-MONITOR, re-GATE (bounded retries, default 1)
       retries exhausted -> HALT + escalate to the user (NEVER advance past a red gate)
final: one consolidate + a one-line report
```

> **The gate is the keystone.** It AGGREGATES (a) verify [`-w` only] + (b) doctor + (c) quality
> floor -- all three run, so the feedback names EVERY failing check -- then (d) `merge-all
> --cleanup` ONLY if a/b/c are all green (`-w` only). It is fail-closed + never-fabricate: a
> subprocess that could not run / an unexpected rc / a sub-floor score is a FAIL, never a
> pass. The ONLY honest skips are the worktree-only checks (verify, merge) on a non-`-w` grid.

> **Charter-bound teams (spec 06 P7, optional).** When the grid was dispatched with
> `--charter <path>`, the between-waves gate MAY ALSO consult the team envelope:
> `python _tools/cex_team_charter.py check --charter <path> --elapsed <s> --cells <committed>`  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
> (rc 0 within / 2 breach; action = ok | escalate | halt). A breach fires ONLY on a REAL
> over-ceiling (a missing ceiling is UNBOUNDED, never a fake breach) -- escalate to the user on
> `escalate`, HALT on `halt`. This is additive to the (a)-(d) gate above, not a replacement.

### Step 3 -- Dispatch (mirror n07-orchestrator)

```bash
bash _spawn/dispatch.sh grid <MISSION>       # plain grid
bash _spawn/dispatch.sh grid <MISSION> -w    # per-cell worktrees (race-free)
```

NEVER timeout/kill `bash _spawn/dispatch.sh grid` (killing the spawn manager orphans the cells). Use the
Monitor (a `run_in_background` watcher) instead.

### Step 4 -- Monitor (reused verbatim from `monitor.md`)

Start a persistent Monitor; N07 keeps working between notifications. The loop checks commits +
signals + PID liveness every 60s and exits when all wave nuclei complete or all PIDs die.

```bash
NUCLEI="n03 n04"   # <-- this wave's dispatched nuclei
PIDS="<pids>"
DONE_COUNT=0
TOTAL=$(echo $NUCLEI | wc -w)
while true; do
  for nuc in $NUCLEI; do
    NUC_UPPER=$(echo $nuc | tr 'a-z' 'A-Z')
    COMMITS=$(git log --oneline --since="90 seconds ago" --all 2>/dev/null | grep -c "\[$NUC_UPPER\]" || true)
    if [ "$COMMITS" -gt 0 ]; then
      MSG=$(git log --oneline --since="90 seconds ago" --all 2>/dev/null | grep "\[$NUC_UPPER\]" | head -1)
      echo "[MONITOR] $NUC_UPPER committed: $MSG"
    fi
    SIG=$(ls .cex/runtime/signals/signal_${nuc}_*.json 2>/dev/null | wc -l || true)
    if [ "$SIG" -gt 0 ]; then
      echo "[MONITOR] $NUC_UPPER COMPLETE (signal found)"
      DONE_COUNT=$((DONE_COUNT + 1))
    fi
  done
  for pid in $PIDS; do
    if ! powershell -Command "Get-Process -Id $pid -EA SilentlyContinue" >/dev/null 2>&1; then
      echo "[MONITOR] PID $pid DEAD"
    fi
  done
  if [ "$DONE_COUNT" -ge "$TOTAL" ]; then
    echo "[MONITOR] ALL $TOTAL NUCLEI COMPLETE -- ready to GATE"
    break
  fi
  sleep 60
done
```

**N07 keeps working** between notifications: write the next wave's handoffs, audit artifacts,
update memory/specs/plans, run doctor checks. N07 NEVER goes idle.

### Step 5 -- Gate, then advance OR retry

On the Monitor's `ALL ... COMPLETE` notification, run the gate. The MissionState (waves +
per-nucleus quality) is the gate's source of truth; record each wave's quality into MissionState
during consolidate so (c) has real scores to read.

```bash
python _tools/cex_wave_state.py gate --mission <MISSION> --wave W [--worktree]
echo "rc=$?"   # 0 PASS -> advance ; 2 FAIL -> retry the failing nuclei
```

- **rc 0 (PASS)**: consolidate this wave (the gate already ran doctor; on `-w` it also merged the
  worktrees). Advance to wave W+1.
- **rc 2 (FAIL)**: the gate's `feedback` names EVERY failing check (and the sub-floor nuclei).
  Append it to ONLY the failing nuclei's handoffs, re-dispatch ONLY those, re-Monitor, re-gate.
  Bounded retries (default 1).
- **retries exhausted**: HALT + escalate to the user with the gate feedback. **Never advance
  past a red gate.** (A red gate that re-gates clean is fine; a red gate that stays red stops the
  mission -- that is the contract.)

The gate's verdict is recorded to the side ledger `.cex/runtime/wave_state.json` for the audit
trail. `python _tools/cex_wave_state.py status --mission <MISSION>` shows the MissionState
summary + every recorded gate verdict.

## Anti-patterns (from `monitor.md` -- the gate adds two more)

| Wrong | Right |
|-------|-------|
| `cex_signal_watch.py` (blocks N07) | the Monitor tool (async notifications) |
| Repeated Bash calls every 60s | a single persistent Monitor with the while-loop |
| Trusting signals alone | check commits + PID liveness too |
| Re-deriving the between-waves gate from memory | run `cex_wave_state.py gate` (mechanical) |
| Advancing a wave on a partial / unverified result | advance ONLY on a GREEN gate (rc 0) |
| `merge-all` on a red tree | the gate withholds merge until verify+doctor+quality are green |

## Decision authority (mirror n07-orchestrator)

- N07 decides: wave order, `-w` per wave, when to dispatch, when to consolidate, killing idle
  PIDs after a signal -- all autonomous.
- N07 asks the user: GDP decisions BEFORE the first dispatch; a gate that stays red after the
  bounded retries (re-dispatch or accept?); a nucleus stuck > 45min (wait or kill?).

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| monitor | sibling | 0.80 |
| cex_wave_state | engine | 0.75 |
| n07-orchestrator | upstream | 0.60 |
| p01_kc_orchestration_best_practices | related | 0.40 |
| p01_kc_cex_orchestration_architecture | related | 0.35 |
