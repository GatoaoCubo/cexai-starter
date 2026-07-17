# Composable Crew Protocol

**The 5th wiring rule.** Alongside 8F (how to think), GDP (who decides), dispatch-depth (how deep), and shared-file-proposal (how to merge), composable-crew is how CEX assembles **multi-role teams** for work that single builders cannot cover.

## When to use a crew (vs. solo builder vs. grid)

| Scenario | Use | Why |
|----------|-----|-----|
| Produce 1 artifact of 1 kind | **solo builder** | 8F pipeline is enough |
| Produce N artifacts in parallel, independent | **grid dispatch** | Nuclei handle their own scopes |
| Produce 1 coherent deliverable that requires N roles with handoffs | **crew** | Roles depend on each other; process matters |

Crews are the right tool when the **output is a package** (e.g. launch kit, RFP response, incident postmortem) that requires multiple specialties in a defined topology.

## The 5 WAVE8 primitives

| Kind | Pillar | Function | Purpose |
|------|--------|----------|---------|
| `crew_template` | P12 | CALL | Reusable recipe -- roles table + process topology + handoff protocol |
| `role_assignment` | P02 | CONSTRAIN | Binds a role_name to an agent_id with goal/backstory/tools |
| `capability_registry` | P08 | CONSTRAIN | Index of all spawnable agents (282 today); crew planner queries it |
| `nucleus_def` | P02 | CONSTRAIN | Machine-readable nucleus identity + capabilities (1 per nucleus) |
| `team_charter` | P12 | GOVERN | Mission contract per crew instance (budget, deadline, gate) |

## Topology (process types)

| Process | Semantics | When |
|---------|-----------|------|
| `sequential` | Role N waits for Role N-1's artifact | When each step strictly depends on the prior |
| `hierarchical` | Manager role coordinates workers; may delegate | When coordination overhead is worth it (>= 5 roles) |
| `consensus` | All roles work in parallel, vote on final | When diverse perspectives reduce risk (review / audit) |

`process:` remains REQUIRED, still exactly these 3 values -- unchanged by the
extensions below. It is also still what `_charter_gate` reads to decide
whether the package passed (weakest-link for sequential/hierarchical, mean +
divergence for consensus).

## Process Topology Extensions (R-172): composable termination + named speaker-selection

kc_oss_autogen.md (clean-room mechanics from microsoft/autogen's MIT-licensed
`autogen-agentchat` package) documents that AutoGen's own group-chat substrate
splits "who speaks next" from "when do we stop" into two independently
swappable pieces: a composable (AND/OR) `TerminationCondition` family, and a
pluggable per-Team speaker-selection strategy. `crew_template` gains the same
split via **two new OPTIONAL frontmatter blocks**. Neither is required, and
neither changes the meaning of `process:` above.

```yaml
# OPTIONAL -- names the strategy explicitly. Absent -> derived from `process`
# via the legacy mapping table below (byte-identical to today's behavior).
speaker_selection:
  strategy: round_robin   # round_robin | manager_delegates | vote

# OPTIONAL -- a composable AND/OR condition tree, checked BETWEEN ROUNDS of
# the round_robin strategy. Absent -> no early exit; the strategy's natural
# fixed shape governs completion (unchanged).
termination:
  any_of:                       # OR -- fires when ANY child is true
    - type: max_rounds
      rounds: 6
    - type: quality_gate_passed
      threshold: 9.0
  all_of:                       # AND -- fires only when ALL children are true
    - type: artifact_produced
    - type: budget_exhausted
      tokens: 50000
```

**Named strategies** (`speaker_selection.strategy`) map onto the 3 existing
processes, with room for future names to be added without growing the
`process:` enum:

| Strategy | Legacy `process:` equivalent | What it runs |
|----------|------------------------------|--------------|
| `round_robin` | `sequential` | Rotates through roles by index; role N receives role N-1's artifact (the handoff protocol) |
| `manager_delegates` | `hierarchical` | Manager runs first (coordinator context), workers run with the manager's artifact as handoff, manager re-plans once over the workers' artifacts |
| `vote` | `consensus` | All roles run independently (no handoff), merged into a mean-score + divergence verdict |

An explicit `speaker_selection.strategy` naming a known strategy WINS over the
`process`-derived default (an author can decouple execution topology from
gate-scoring shape intentionally -- see the scoped limit below). An absent,
unrecognized, or non-dict `speaker_selection` block falls back to the legacy
`process -> strategy` mapping, so a crew_template that does not declare this
block always resolves to the exact strategy it always has.

**Composable termination** (`termination`) is a recursive AND/OR tree, mirroring
AutoGen's `TerminationCondition.__or__`/`__and__` operator overloads as data
instead of Python operators. Each node is either:
- `{any_of: [<node>, ...]}` -- OR: true iff ANY child evaluates true (nestable, arbitrary depth)
- `{all_of: [<node>, ...]}` -- AND: true iff ALL children evaluate true (an EMPTY `all_of` is a safe `False`, never a vacuous `True`)
- `{type: <name>, ...params}` -- a LEAF condition, dispatched by name

4 named leaf condition types ship today:

| Type | Params | Fires when |
|------|--------|------------|
| `max_rounds` | `rounds` (or `value`) | The round counter reaches `rounds` |
| `artifact_produced` | `role` (optional) | The relevant turn's artifact is non-empty (defaults to the just-completed turn; `role` scopes to a specific role name) |
| `quality_gate_passed` | `threshold` (optional, defaults to the crew's own `charter_gate`) | The just-completed turn's score clears `threshold` |
| `budget_exhausted` | `tokens` | A cumulative char/4 token estimate reaches `tokens` (same convention as the crew's own cost-tracking fallback) |

**Degrade-never / absent-blocks contract (zero-regression guarantee).**
`CrewRunner.load_from_crew_template` only writes `crew_meta["speaker_selection"]`
/ `crew_meta["termination"]` into the resolved plan when the frontmatter
ACTUALLY has a dict-shaped block for that key -- never a `None` placeholder.
Every crew_template on disk today (including `p12_ct_product_launch.md`) has
neither block, so its resolved plan, its `CrewControlPlaneRunner.run()`
outcome, and `cex_crew.py show`/`list` output are all **byte-identical** to
before R-172. This is proved by an A/B harness
(`_tools/tests/test_crew_r172_topology.py`) that loads git HEAD's pre-R-172
`_tools/cex_crew_runner.py` as an isolated module and diffs its output against
the current module for the real on-disk `product_launch.md`, mirroring the
R-189 `ACTION_TABLE` precedent in `_tools/cex_capability_router.py`.

**Scoped limit (documented, not silently generalized).** Only the
`round_robin` strategy consumes `termination` today -- it is the one strategy
with a natural per-turn loop (AutoGen's own `RoundRobinGroupChat` +
`TerminationCondition` pairing). `manager_delegates`/`vote` keep their
existing fixed-shape run (a `termination` block on a hierarchical/consensus
crew_template is parsed and rendered by `show`, but not yet consumed by the
runner). A hard safety cap (`len(roles) * 3` rounds) guarantees the
`round_robin` loop can never spin forever even if `termination` is malformed
or never fires -- hitting the cap is recorded as a run warning, never an
exception. `_charter_gate` is UNCHANGED: it still keys off `process:`, not the
resolved strategy -- so an explicit `speaker_selection.strategy` that
diverges from what `process:` implies (e.g. `process: sequential` +
`speaker_selection: {strategy: manager_delegates}`) changes WHO RUNS but not
how the package is SCORED. Keep the two aligned unless you deliberately want
that decoupling.

Implementation: `_tools/cex_crew_runner.py` -- `CONDITION_TABLE` (leaf
dispatch) + `_evaluate_termination` (the recursive AND/OR evaluator) +
`STRATEGY_TABLE` + `PROCESS_TO_STRATEGY` (the strategy dispatch, replacing the
old `process ==` if/elif ladder -- see the R-172 module comment just above
`CrewControlPlaneRunner`). Register row: R-172.
Source KC: `N01_intelligence/P01_knowledge/kc_oss_autogen.md`.

## How to instantiate a crew (end-to-end)

```bash
# 1. Discover available crews
python _tools/cex_crew.py list

# 2. Inspect the plan (dry)
python _tools/cex_crew.py show product_launch

# 3. Dry-run (generates prompts under .cex/runtime/crews/{name}/)
python _tools/cex_crew.py run product_launch \
    --charter N02_marketing/P12_orchestration/team_charter_launch_demo.md

# 4. Real execution (LLM calls + artifacts)
python _tools/cex_crew.py run product_launch \
    --charter N02_marketing/P12_orchestration/team_charter_launch_demo.md \
    --execute
```

## Authoring a new crew

1. **Pick an agent set** -- query `capability_registry.json` for candidates:
   ```bash
   python _tools/cex_capability_index.py --query "research"
   ```
2. **Write role_assignments** (one per role) in `N0x/crews/p02_ra_{role}.md`.
   Each binds `role_name -> agent_id` with goal/backstory/P04_tools/delegation.
3. **Write crew_template** in `N0x/crews/p12_ct_{name}.md` with the Roles
   table referencing your role_assignments and a `process:` topology.
4. **Write team_charter** (instance-specific) with mission/budget/deadline/gate.
5. **Validate** -- `python _tools/cex_crew.py show {name}` prints the resolved plan.

## Integration with 8F

A crew run is a specialization of F6 PRODUCE that expands into N sub-F6 runs,
one per role. Each role still executes F1..F8 internally (it's a full builder).
The crew layer adds:
- **F3 INJECT augmentation**: each role receives the upstream role's artifact
- **F7 GOVERN coordination**: a charter-level quality gate runs after all roles complete
- **F8 COLLABORATE coordination**: role handoffs go through a2a Task signals

## Grid + Crew composition

The three dispatch modes stack:

| Layer | What it runs | Parallelism |
|-------|--------------|-------------|
| **solo** | One builder, one artifact | none |
| **crew** | N roles with handoffs (sequential / hierarchical / consensus) | intra-crew only |
| **grid** | N solo builders OR N crew instances | full cross-cell |
| **grid of crews** | N parallel crew instances, each with its own charter | crews run in parallel; roles inside each crew follow their topology |

Example -- ship 3 product launches on the same day:

```
N07 dispatches a grid with 3 cells:
  cell_1: cex_crew.py run product_launch --charter charter_prod_A.md --execute
  cell_2: cex_crew.py run product_launch --charter charter_prod_B.md --execute
  cell_3: cex_crew.py run product_launch --charter charter_prod_C.md --execute

Each cell runs the same 4-role sequential crew (research -> copy -> design -> QA)
but grounded on a different charter (different product, deadline, budget).

Total concurrency: 3 crews x (1 active role at a time each) = 3 LLM calls in flight.
If you switch the crew to `process: consensus`, concurrency becomes 3 x 4 = 12.
```

Grid+crew is the highest-leverage composition CEX offers: you parallelize
entire packages, not just individual artifacts, while keeping coherence
within each package via the crew's handoff protocol.

## Swarm mode (BORIS_MERGE D5)

When you need **N parallel builders of the same kind** (not N different roles,
not a full crew with handoffs), use swarm instead of crew. Swarm trades
coherence for breadth:

```bash
bash _spawn/dispatch.sh swarm agent 5 "scaffold 5 niche sales agents"
# Spawns 5 agent-builders in parallel worktrees, each produces one artifact.
```

Contrast:
- **crew** -- 4 roles, 1 coherent deliverable, handoffs between roles
- **swarm** -- N builders, N independent deliverables of same kind, isolated worktrees
- **grid** -- heterogeneous nuclei, arbitrary handoffs, mission-scoped

Swarm is the right tool when the goal is **coverage** (explore a kind-space by
generating variants) rather than **integration** (roles depend on each other).

**Two-phase reality (register vs. fan-out), verified on disk 2026-07-07 (R-058).**
The `swarm` example above is honest about the OUTCOME but silent on the
MECHANIC: `bash _spawn/dispatch.sh swarm` does not itself launch any builder process. Its
`swarm)` case (`_spawn/dispatch.sh:507-516`) does exactly one thing --
delegate to `bash _spawn/spawn_swarm.sh "$KIND" "$N" "$TASK"` -- and that
script is two phases, only the first of which is automatic:

1. **Register** (automatic -- all `spawn_swarm.sh` actually does): create N
   git worktrees (`.cex/worktrees/swarm_<ts>/cell_NN/`, one branch per cell),
   write N handoff files (`.cex/runtime/handoffs/SWARM_<ts>_cell_NN.md`), and
   print the cell list (`spawn_swarm.sh:51-102`). Zero builders are running
   when this step finishes.
2. **Fan-out** (manual -- the operator must run it): `spawn_swarm.sh` prints,
   but never executes, the real dispatch commands -- either one cell at a
   time (`bash _spawn/dispatch.sh solo {nucleus} "Read {handoff} and execute"
   -w {swarm_id}`, `spawn_swarm.sh:105-106`) or a copy-paste "auto-fan-out"
   loop that backgrounds one `bash _spawn/dispatch.sh solo ... &` per cell followed by
   `wait` (`spawn_swarm.sh:108-113`).

So `bash _spawn/dispatch.sh swarm agent 5 "..."` really does create 5
worktrees + 5 handoffs in one call, but nothing is *building* until the
operator runs (or copy-pastes) the fan-out step it prints. Treat swarm as
register-then-fan-out, not a single self-contained dispatch.

## When crews are NOT the answer

- **1 artifact, 1 kind** -> solo builder, not a crew
- **Independent parallel production** -> grid dispatch, not a crew
- **Pure research** -> N01 alone; the crew pattern adds no value
- **No handoffs needed** -> if roles never consume each other's output, grid is cheaper

<!-- cex:lean-surface-note -->
> **Multi-orchestration note (updated):** this repo now ships the REAL dispatch mechanism
> alongside the in-session Task-tool path -- both are available; pick per the cost/detachment
> tie-breaker in `.claude/rules/n07-orchestrator.md`. Shipped: `.claude/commands/{batch,build,
> consolidate,crew,dispatch,grid,guide,mentor,mission,monitor,plan,run,simplify,spec,status,
> validate}.md`, `_spawn/dispatch.sh` (+ spawn_grid/spawn_solo/spawn_stop/spawn_monitor/
> spawn_swarm.sh/grid_safe_launch/grid_watchdog), `.claude/workflows/grid.js` (Mode W),
> `boot/n01.ps1..n07.ps1` + `boot/cex_codex.ps1` + `boot/cex_gemini.ps1` + `boot/cex_nucleus.sh`
> (multi-runtime boot targets), and `_tools/{cex_mission,cex_wave_state,cex_evolve,
> cex_system_test,cex_crew,cex_crew_runner}.py`. Still NOT present in this repo (genuinely
> Central-only): `cex_run.py`, `cex_mission_runner.py`, `cex_flywheel_audit.py`,
> `cex_capability_index.py`, `cex_hooks.py`, `cex_team_charter.py`, `cex_capability_router.py`
> (ACR preflight), and the improvement register. Any command/tool not in the shipped list above
> is unavailable here; a row below citing one is marked inline too.
<!-- cex:lean-surface-note -->
