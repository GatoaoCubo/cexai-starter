---
id: rule_system_overview
kind: runtime_rule
pillar: P12
title: "CEX System Overview -- Workflow + Commands + Tools"
version: 1.0.0
created: 2026-04-27
quality: null
density_score: 0.90
tags: [system, overview, workflow, commands, tools]
related:
  - "CLAUDE"
  - "n07-orchestrator"
  - "8f-reasoning"
---

# CEX System Overview

## The Workflow

```
/plan -> /guide -> /spec -> /grid -> /consolidate
  |        |        |       |         |
  |        |        |       |         --> verify + score + clean
  |        |        |       --> dispatch nuclei (autonomous)
  |        |        --> spec blueprint (exact artifacts)
  |        --> decisions with user (co-pilot)
  --> decompose goal into tasks
```

User decides WHAT -> LLM builds HOW -> verify together.

## Commands

| Command | Purpose |
|---------|---------|
| `/init` | **First run**: configure CEX for your brand (~2 min) (Central-only -- not in this lean repo) |
| `/plan <goal>` | Decompose goal -> tasks, nuclei, dependencies (Central-only -- not in this lean repo) |
| `/guide [goal]` | **Co-pilot**: ask me before building -- guided decisions |
| `/spec [plan]` | Create spec blueprint from plan + decisions (Central-only -- not in this lean repo) |
| `/grid [spec]` | Execute spec -- autonomous dispatch to nuclei (Central-only -- not in this lean repo) |
| `/build <intent>` | Build single artifact via 8F pipeline |
| `/validate [file\|all]` | Check artifact quality |
| `/dispatch <nucleus> <task>` | Send task to single nucleus (Central-only -- not in this lean repo) |
| `/mission <goal>` | **Shortcut**: plan+guide+spec+grid+consolidate in one (Central-only -- not in this lean repo) |
| `/status` | System health dashboard (Central-only -- not in this lean repo) |
| `/cex-doctor` | Full diagnostics (separate from Claude Code's native `/doctor`) (Central-only -- not in this lean repo) |
| `/consolidate` | Post-dispatch: verify + score + clean (Central-only -- not in this lean repo) |
| `/evolve [file\|all]` | **AutoResearch**: autonomous artifact improvement loop (Central-only -- not in this lean repo) |
| `/mentor [question]` | **Vocabulary**: 8F + 12P + 257K taxonomy navigator |
| `/crew list\|show\|run <name>` | **Composable crew (WAVE8)**: list/inspect/run multi-role teams (Central-only -- not in this lean repo) |

## Composable Crews (WAVE8)

Crews = multi-role teams with handoffs for coherent deliverables.
CLI: `python _tools/cex_crew.py list|show|run <name>`.
Full protocol + grid-of-crews composition: `.claude/rules/composable-crew.md`.

## Tools (top 10)

Full list: `python _tools/<tool>.py --help`

| Tool | Purpose |
|------|---------|
| `cex_run.py` | Unified entry: intent -> discover -> plan -> compose prompt (Central-only -- not in this lean repo) |
| `cex_8f_runner.py` | Full 8F pipeline (--execute, --mode A\|B\|auto, --model) |
| `cex_mission_runner.py` | Autonomous orchestration: waves -> grid -> poll -> gate -> consolidate (Central-only -- not in this lean repo) |
| `cex_compile.py` | .md -> .yaml compilation (--all) / reverse: --target claude-md,cursorrules,customgpt |
| `cex_doctor.py` | Builder health check (size, density, frontmatter, wiring) |
| `cex_evolve.py` | AutoResearch loop: evolve artifacts autonomously (keep/discard) (Central-only -- not in this lean repo) |
| `cex_bootstrap.py` | First-run: brand setup -> propagate -> audit |
| `cex_score.py` | Peer review scoring (--apply) |
| `cex_retriever.py` | TF-IDF artifact similarity (full-corpus index) |
| `cex_flywheel_audit.py` | Doc vs Practice: 109 checks across 7 layers + 7 wires + 7 cascades (Central-only -- not in this lean repo) |

## Model Tiers (8F Execution Modes)

| Tier | Models | 8F Mode | Capabilities |
|------|--------|---------|-------------|
| `full_8f` | Opus, Sonnet | Mode A (monolithic) | F1-F8 autonomous |
| `f6_generation` | Haiku, Gemini Flash | Mode B (decomposed) | F6 only (needs prompt_package) |
| `preflight_aux` | Gemini Pro, Codex | N/A | Read-only: web_fetch, code_scan |
| `local_f6` | Ollama fine-tuned | Mode B | F6 from trained patterns (DEFERRED) |
| `unsupported` | Ollama raw, Codex grid | N/A | BLOCKED (zero deliverables in STRESS_TEST) |

Config: `.cex/config/nucleus_models.yaml` (tiers section).
Routing: `_tools/cex_router_v2.py` (get_mode, get_tier).

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| CLAUDE | upstream | 1.0 |
| n07-orchestrator | related | 0.90 |
| 8f-reasoning | related | 0.85 |
| composable-crew | related | 0.70 |
| guided-decisions | related | 0.65 |

<!-- cex:lean-surface-note -->
> **Lean tenant note:** this sovereign repo ships a SINGLE in-session N07 orchestrator, not
> the full multi-nucleus Central grid. Only `.claude/commands/{build,guide,mentor,run,
> simplify,validate}.md` are shipped -- `/plan`, `/spec`, `/grid`, `/dispatch`, `/mission`,
> `/status`, `/consolidate`, `/evolve`, `/crew`, `/init`, `/cex-doctor` and the
> dispatch-oriented tools below (`cex_run.py`, `cex_crew.py`, `cex_evolve.py`,
> `cex_mission_runner.py`, `cex_flywheel_audit.py`, `cex_capability_index.py`, `cex_hooks.py`,
> `Task tool: dispatch`) are Central-only and are NOT present in this repo. The tables below describe
> Central's full capability set for reference; treat any command/tool not in the shipped list
> as unavailable here (rows below citing one are marked inline too -- see each row).
<!-- cex:lean-surface-note -->
