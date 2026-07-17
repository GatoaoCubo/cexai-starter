# AGENTS.md -- point your agent at this repo

This repo is meant to be read by an LLM, not just a human. This page is the entry point
for whichever agent you use -- Claude Code, a Codex/GPT-backed tool, Gemini, or a local
Ollama-driven agent.

## The real entry point: `CLAUDE.md`

`CLAUDE.md` (repo root) is a plain markdown file -- runtime-agnostic. It declares this
tenant's identity, the 4 non-negotiable rules, and a pointer table into every rule file.
**Any** agent, regardless of runtime, should read it first. If your tool supports an
"always load this file" convention (Claude Code does, automatically), point it there.

## Track 1 -- Claude Code (first-class, this repo)

This repo ships real Claude Code automation:

```bash
sh boot/cex.sh        # Mac / Linux / WSL
boot/cex.ps1            # Windows (PowerShell)
```

What it does, concretely (read `boot/cex.sh` / `boot/cex.ps1` yourself -- both are short,
self-contained, and exactly what runs):

1. Sets `CEX_NUCLEUS=N07` and `CEX_ROOT` in the environment.
2. Resolves the model: `CEX_MODEL_OVERRIDE` env var, else
   `.cex/config/nucleus_models.yaml` (`n07.model`, only if it is a full `claude-*` id),
   else the hardcoded default `claude-sonnet-4-6`.
3. Merges `N07_admin/P08_architecture/agent_card_n07.md` + a short sin-lens system prompt
   into one file and passes it via `--append-system-prompt-file` (a single merged append --
   never repeated flags, which the underlying CLI resolves last-wins, not additively).
4. Launches `claude --dangerously-skip-permissions --permission-mode bypassPermissions
   --model <resolved> --append-system-prompt-file <merged>`.

Note the permission flags in step 4: this launcher starts Claude Code in a
permissions-bypassed mode by default -- know that before you run it, especially against
directories you have not reviewed.

Needs the `claude` CLI on `PATH`. No other setup.

### What Claude Code can do here out of the box

Once booted (or in any Claude Code session opened at this repo's root), 16 slash
commands are available (`.claude/commands/`):

| Command | Does |
|---|---|
| `/run` | Boot the 3 local apps (storefront, admin, API) |
| `/build <intent>` | Run the 8F pipeline in-session, produce one typed artifact |
| `/guide [goal]` | Co-pilot mode -- ask the subjective decisions before building |
| `/validate` | Repo-wide health check (`cex_doctor`) |
| `/mentor [explain\|quiz] <concept>` | Teach a concept in this brain, hands-on |
| `/simplify [path]` | Three-lens audit of a diff or path (reuse / quality / efficiency) |
| `/spec [plan]` | Turn a plan + decisions into a detailed build blueprint |
| `/monitor` | Watch a dispatched wave without blocking (commits + signals + PID liveness) |
| `/plan <goal>` | Decompose a goal into tasks, nucleus assignments, dependencies |
| `/dispatch <nucleus> <task>` | Write a handoff and spawn ONE nucleus (OS-window) |
| `/grid [spec]` | Dispatch nuclei autonomously -- mode-resolving (in-session or OS-window) |
| `/mission <goal>` | Full lifecycle shortcut: plan + guide + spec + grid + consolidate |
| `/consolidate` | Post-dispatch: verify deliverables, stop idle processes, commit |
| `/status` | System health + running-nucleus dashboard |
| `/crew list\|show\|run <name>` | Composable multi-role teams with handoffs (`cex_crew.py`) |
| `/batch <intents-file>` | N independent tasks fanned out across isolated git worktrees |

Underneath these, `.claude/rules/` (10 files) and `.claude/skills/` (28 lazy-loaded files)
carry the actual behavioral contract -- the 8F pipeline, GDP (guided decisions), the
ASCII-code rule, dispatch-before-build discipline, and more -- including
`.claude/rules/n07-orchestrator.md`, which documents BOTH dispatch transports
(in-session Task tool, and the OS-window `_spawn/dispatch.sh` grid; see "Multi-orchestration"
below). `.claude/agents/` ships 121 builder sub-agent definitions (one per typed kind, plus
nucleus identities) that Claude Code can invoke as in-session Task-tool agents -- the path
`/grid` and `/mission` resolve to when they pick the in-session transport.

## Track 2 -- any other agent (GPT, Gemini, Ollama-backed, custom loops)

Four real options, lightest to most integrated:

1. **Point your agent at `CLAUDE.md` directly.** It is plain markdown; tell your agent
   "read `CLAUDE.md` first, then follow its pointers" and it has the same map a Claude
   Code session gets automatically. From there it can read
   `.claude/rules/8f-reasoning.md`, the nucleus rule files (`N0X_*/rules/n0X-*.md`), and
   `.cex/kinds_meta.json` the same way.
2. **`boot/cex_nucleus.sh`** -- one self-contained, cross-platform (Mac/Linux/WSL) launcher
   that boots ANY of the 7 nuclei via ANY CLI: `bash boot/cex_nucleus.sh n03 --cli gemini`
   (also `--cli codex` / `--cli ollama`). It reads `.cex/config/nucleus_models.yaml` for the
   CLI + model, builds the sin-lens system prompt itself, and reads
   `.cex/runtime/handoffs/<nuc>_task.md` if one is waiting -- no per-nucleus-per-CLI file
   required.
3. **N07 direct multi-runtime boots (Windows)** -- `boot/cex_codex.ps1` and
   `boot/cex_gemini.ps1` boot the ORCHESTRATOR specifically via Codex or Gemini
   (`powershell -File boot/cex_gemini.ps1`). Useful for a non-Claude orchestrator that
   still dispatches Claude-run nuclei underneath it via `_spawn/dispatch.sh`.
4. **Keep the native `claude` CLI, swap the backend model.** This repo includes the "any
   model" seam: `boot/cex_anymodel.ps1` wires `ANTHROPIC_BASE_URL` to a local LiteLLM
   proxy (`boot/litellm_proxy.ps1`, config at `.cex/config/litellm_config.yaml`) that can
   route to Anthropic, a **free local Ollama model**, Groq, Cerebras, DeepSeek, or 100+
   other providers -- the native `claude` CLI, TUI, and tools stay unchanged; only the
   transport moves. Full walkthrough: [`docs/RUNTIME_ANY_MODEL.md`](docs/RUNTIME_ANY_MODEL.md).

## Who am I? (nucleus identity)

`CLAUDE.md` resolves identity from the `CEX_NUCLEUS` environment variable. `boot/cex.sh` /
`boot/cex.ps1` are N07's direct, manual boot (always sets `CEX_NUCLEUS=N07`); every one of
the 7 operational nuclei also has its own dispatch-mechanism boot script
(`boot/n01.ps1` .. `boot/n07.ps1`), each setting its own `CEX_NUCLEUS` and merging that
nucleus's agent card + sin-lens identity before launch -- these are what
`_spawn/dispatch.sh` spawns (see "Multi-orchestration" below). To have an agent act as a
**different** department (say, N02 Marketing) inside a plain Claude Code session without
booting through a script, set `CEX_NUCLEUS=N02` yourself, or simply ask the agent to "act
as N02" -- it self-loads `N02_marketing/rules/n02-marketing.md` the same way N07 loads its
own. Every one of the 8 nuclei has a `rules/n0X-*.md` file; reading it is what actually
establishes identity -- the boot script is a convenience, not a requirement.

## Multi-orchestration: N07 dispatches, in two transports

This repo ships the REAL N07 dispatch mechanism, not just in-session fan-out. `/build`
still runs the 8F pipeline in-session for a single artifact -- but for multi-artifact,
multi-nucleus work, N07 now has two transports, both running the full 8F pipeline per
nucleus, both signaling completion, both ending at `/consolidate`:

1. **In-session (Task tool)** -- N07 spawns subagents inside the current Claude Code
   session. No OS window, no PID file, no `taskkill`. Cheaper, faster, the default for
   the common case (same-runtime, attached, single session).
2. **OS-window spawn (`_spawn/dispatch.sh`)** -- N07 spawns a REAL separate process
   (`claude`, or `codex` / `gemini` via `-cli`) per nucleus, each in its own window,
   tracked by PID in `.cex/runtime/pids/spawn_pids.txt`, killable, resumable across a
   crashed session, and able to outlive this one:

   ```bash
   bash _spawn/dispatch.sh solo n03 "task description"              # 1 nucleus, new window
   bash _spawn/dispatch.sh grid MISSION_NAME                        # up to 6 parallel nuclei
   bash _spawn/dispatch.sh grid MISSION_NAME -w                     # + per-cell git worktrees
   bash _spawn/dispatch.sh swarm agent 5 "scaffold 5 sales agents"  # N builders, same kind
   bash _spawn/dispatch.sh status                                   # monitor
   bash _spawn/dispatch.sh stop                                     # stop MY session's nuclei only
   ```

Which transport to use, and the full protocol for both, is in
`.claude/rules/n07-orchestrator.md` ("Which transport?" decision table). The 8 nuclei
directories are real, typed, 12-pillar knowledge departments either way -- the difference
is WHO runs the work (this session vs. a separate process) and HOW you track it (a
returned result vs. a PID + signal file).

**Composable crews** (`/crew`, `cex_crew.py`) layer a coherent multi-role package
(research -> copy -> design -> QA, with handoffs between roles) on top of either
transport -- see `.claude/rules/composable-crew.md`.

**What's genuinely still Central-only** (absent from this repo; referenced calls degrade
gracefully -- fail open or print a clear error, never silently misfire): the `decompose`
dispatch mode's execution tool (`cex_decompose.py`), the Autonomous Capability Router
preflight (`cex_capability_router.py`), rate-limit / quota guards, team-charter
enforcement, and the gated mentor-swarm batch topology. `cex_mission_runner.py` (fully
headless, unattended overnight orchestration) is NOT shipped -- `cex_mission.py` (the
interactive `/plan` + `/mission` decompose/execute engine) IS. `cex_router_v2.py` (the
cost-tiered AUTOROUTE resolver `dispatch.sh solo` consults by default) WAS ALREADY
shipped in this repo before this carry, and is fully functional.

## The 8F pipeline (what every build follows)

```
F1 CONSTRAIN -> F2 BECOME -> F3 INJECT -> F4 REASON -> F5 CALL -> F6 PRODUCE -> F7 GOVERN -> F8 COLLABORATE
```

Full protocol: [`.claude/rules/8f-reasoning.md`](.claude/rules/8f-reasoning.md).
Every artifact any agent produces here -- via `/build` or `python _tools/cex_8f_runner.py`
directly -- passes through all eight functions and never self-scores (`quality: null`; a
peer review or `cex_score.py` assigns the number).

## Running a business capability (not just a knowledge artifact)

If the intent matches one of this tenant's enabled capabilities (ads, pricing, research,
landing pages, lead gen, and more -- full table in the "Capabilities -- How To Run" section
of [COOKBOOK.md](COOKBOOK.md)), it runs through the same headless runtime the dashboard and
API use:

```python
from cex_run_capability import run_capability, Credential
result = run_capability(tenant_id, "<capability>", "<intent>", credential)
```

## This repo ships unfilled -- your agent should know that too

Point an agent at `CLAUDE.md` here and it will see `Brand: Sua Empresa`, `Tagline:
[preencher]`, `Archetype: [preencher]` in the Brand Identity table. That is not missing
data -- it is the shipped, unfilled state (see [README.md](README.md#every-placeholder-is-yours-to-fill)).
An agent extending this repo should treat every `[preencher]` as a real gap to close via
`python _tools/cex_bootstrap.py`, never as a fact to invent a value for.

## Quick reference

```bash
python _tools/cex_bootstrap.py --check      # confirm you are in THIS tenant's checkout
python _tools/cex_doctor.py                 # repo-wide health check
python _tools/cex_8f_runner.py "<intent>" --dry-run --verbose   # preview a build
python _tools/cex_8f_runner.py "<intent>" --execute --verbose   # real build
python _tools/cex_compile.py <path>         # compile one artifact after building it
python _tools/cex_score.py <path> --dry-run # peer-review score (never self-assigned)
```

See [QUICKSTART.md](QUICKSTART.md) for the numbered walkthrough and [INDEX.md](INDEX.md)
for the full repo map.
