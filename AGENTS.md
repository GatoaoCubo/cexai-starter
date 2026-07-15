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

Once booted (or in any Claude Code session opened at this repo's root), six slash
commands are available (`.claude/commands/`):

| Command | Does |
|---|---|
| `/run` | Boot the 3 local apps (storefront, admin, API) |
| `/build <intent>` | Run the 8F pipeline in-session, produce one typed artifact |
| `/guide [goal]` | Co-pilot mode -- ask the subjective decisions before building |
| `/validate` | Repo-wide health check (`cex_doctor`) |
| `/mentor [explain\|quiz] <concept>` | Teach a concept in this brain, hands-on |
| `/simplify [path]` | Three-lens audit of a diff or path (reuse / quality / efficiency) |

Underneath these, `.claude/rules/` (10 files) and `.claude/skills/` (28 lazy-loaded files)
carry the actual behavioral contract -- the 8F pipeline, GDP (guided decisions), the
ASCII-code rule, dispatch-before-build discipline, and more. `.claude/agents/` ships 121
builder sub-agent definitions (one per typed kind, plus nucleus identities) that Claude
Code can invoke as in-session Task-tool agents.

## Track 2 -- any other agent (GPT, Gemini, Ollama-backed, custom loops)

There is no dedicated per-runtime boot script in this tenant (no `boot/*_codex.ps1`, no
`GEMINI.md`, no `OLLAMA.md` -- unlike CEXAI's own engine repo, this fabrication shipped
lean). Two real options:

1. **Point your agent at `CLAUDE.md` directly.** It is plain markdown; tell your agent
   "read `CLAUDE.md` first, then follow its pointers" and it has the same map a Claude
   Code session gets automatically. From there it can read
   `.claude/rules/8f-reasoning.md`, the nucleus rule files (`N0X_*/rules/n0X-*.md`), and
   `.cex/kinds_meta.json` the same way.
2. **Keep the native `claude` CLI, swap the backend model.** This repo includes the "any
   model" seam: `boot/cex_anymodel.ps1` wires `ANTHROPIC_BASE_URL` to a local LiteLLM
   proxy (`boot/litellm_proxy.ps1`, config at `.cex/config/litellm_config.yaml`) that can
   route to Anthropic, a **free local Ollama model**, Groq, Cerebras, DeepSeek, or 100+
   other providers -- the native `claude` CLI, TUI, and tools stay unchanged; only the
   transport moves. Full walkthrough: [`docs/RUNTIME_ANY_MODEL.md`](docs/RUNTIME_ANY_MODEL.md).

## Who am I? (nucleus identity)

`CLAUDE.md` resolves identity from the `CEX_NUCLEUS` environment variable. `boot/cex.sh` /
`boot/cex.ps1` always set it to `N07` (the orchestrator) -- this is the only nucleus with a
dedicated boot script in this tenant. To have an agent act as a **different** department
(say, N02 Marketing) inside a plain Claude Code session, set `CEX_NUCLEUS=N02` yourself, or
simply ask the agent to "act as N02" -- it self-loads `N02_marketing/rules/n02-marketing.md`
the same way N07 loads its own. Every one of the 8 nuclei has a `rules/n0X-*.md` file; none
needs a dedicated boot script to be read.

## This is a solo-operator brain, not a multi-nucleus dispatch grid

CEXAI's own engine repo runs N07 as an orchestrator that **dispatches** work to parallel
nuclei (`grid`, `swarm`, crews). This tenant fabrication is leaner by design: `/build` runs
the 8F pipeline **in-session**, one operator at a time -- "there is no nucleus dispatch and
no grid" here (see `.claude/commands/build.md`). If you came from the engine repo expecting
`_spawn/dispatch.sh`, it is not part of this fabrication. The 8 nuclei directories are still
real, typed, 12-pillar knowledge departments -- you can read them, build from them, and
address them by name -- you just do it yourself, in one session, rather than fanning work
out to parallel processes.

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
