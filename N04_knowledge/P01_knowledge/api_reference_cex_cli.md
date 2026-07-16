---
id: p06_ar_cex_cli
kind: api_reference
pillar: P06
title: "CEXAI CLI Tool Reference -- cex_install, cex_run, cex_8f_runner, cex_doctor, cex_compile"
version: "1.0.0"
created: "2026-06-09"
updated: "2026-06-09"
author: N04_knowledge
domain: developer_reference
quality: null
tags: [api_reference, cli, developer, tools, cex_install, cex_run, cex_8f_runner, cex_doctor, cex_compile, cex_setup_validator, dispatch]
tldr: "Reference for the 7 user-facing CEXAI CLI tools. All flags are real -- verified against --help. No invented options."
keywords:
  - "cex_install.py"
  - "cex_run.py"
  - "cex_8f_runner.py"
  - "cex_doctor.py"
  - "cex_compile.py"
  - "cex_setup_validator.py"
  - "the Task tool"
  - "CLI flags"
  - "developer reference"
density_score: 0.95
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_install, cex_run, cex_setup_validator. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

## Overview

CEXAI ships 216 Python tools in `_tools/`. This reference covers the primary user-facing
tools an operator interacts with directly -- turnkey install (`cex_install`), build
(`cex_run`, `cex_8f_runner`), validation (`cex_doctor`, `cex_setup_validator`), compilation
(`cex_compile`), and nucleus dispatch (`Task tool: dispatch`). All flags documented here are
verified against `--help` output from the current codebase.

**Run any tool help:**
```bash
python _tools/<tool>.py --help
```

---

## 1. cex_run.py -- Unified Entry Point

**Purpose:** Highest-level entry point. Takes a natural-language intent, discovers the
right builder, plans the execution, and optionally runs the full 8F pipeline end-to-end.

**Usage:**
```bash
python _tools/cex_run.py [intent] [flags]  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```

**Key flags:**

| Flag | Type | Description |
|------|------|-------------|
| `intent` | positional | Natural language goal (e.g. "create a knowledge card about RAG") |
| `--execute` / `-x` | bool | Execute via `claude` CLI (requires Claude Code subscription auth) |
| `--dry-run` | bool | Plan without saving prompt or calling LLM |
| `--quality` / `-q` | float | Quality target, default `9.0` |
| `--verbose` / `-v` | bool | Show step-by-step pipeline progress |
| `--status` | bool | Print system status (builders, kinds, last commit) |
| `--discover QUERY` | str | Find builders matching a query (no artifact produced) |
| `--plan INTENT` | str | Generate execution plan only (no LLM call) |
| `--json` | bool | Output plan as JSON |
| `--bare` | bool | Skip config search and heavy context load; 10x faster for hot-loop dispatch |
| `--mode {A,B,auto}` | str | 8F execution mode: A=monolithic, B=decomposed, auto=detect from model tier |
| `--model MODEL` | str | Model override (e.g. `haiku`, `gemini-flash`) |

**Example invocations:**

```bash
# Discover which builder handles a topic (no execution)
python _tools/cex_run.py --discover "payment processing"  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

# Plan only (show what would run, no LLM call)
python _tools/cex_run.py --plan "create a knowledge card about RAG" --json  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

# Full autonomous: compose -> claude CLI -> validate -> save
python _tools/cex_run.py "create a knowledge card about RAG" --execute  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

# Dry run (plan without saving)
python _tools/cex_run.py "build webhook handler" --dry-run  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

# System status
python _tools/cex_run.py --status  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```

**Output:** by default, prints the composed prompt. With `--execute`, prints the 8F trace
and the saved file path. With `--json`, outputs a JSON plan object.

---

## 2. cex_8f_runner.py -- 8F Stateful Artifact Pipeline

**Purpose:** Runs the complete 8F pipeline (F1 CONSTRAIN through F8 COLLABORATE) for a
single artifact. Supports both monolithic (Mode A) and decomposed (Mode B) execution.
More fine-grained control than `cex_run.py`.

**Usage:**
```bash
python _tools/cex_8f_runner.py [intent] [flags]
```

**Key flags:**

| Flag | Type | Description |
|------|------|-------------|
| `intent` | positional | Natural language intent |
| `--kind KIND` | str | Override kind classification (skip Motor F1 auto-detection) |
| `--dry-run` | bool | Preview prompt without LLM call (default behavior) |
| `--execute` | bool | Call LLM to produce artifact |
| `--list-kinds` | bool | Print all available kind names |
| `--verbose` | bool | Show per-F (per-function) trace details |
| `--step N` | int | Stop after function N (1-8); useful for debugging a specific stage |
| `--output-dir DIR` | str | Save outputs to this directory instead of default pillar path |
| `--nucleus N0X` | str | Target nucleus (e.g. `N01`, `N05`) |
| `--context TEXT` | str | Inject domain context string |
| `--context-file FILE` | str | Read domain context from file (safer for untrusted content) |
| `--model MODEL` | str | Model override (e.g. `ollama/qwen3:8b`, `claude-sonnet-4-6`) |
| `--update FILE` | str | Diff-aware update: read existing artifact, produce delta merge preserving human edits |
| `--force` | bool | Allow >60% rewrite in `--update` mode (bypass rewrite guard) |
| `--mode {auto,A,B}` | str | A=monolithic F1-F8, B=decomposed (F6 from prompt_package), auto=detect from model tier |
| `--prompt-package FILE` | str | Path to pre-compiled prompt_package for Mode B Stage 2 |
| `--stage {1,2,3}` | int | Decomposed stage: 1=write prompt_package, 2=consume it (F6), 3=F7+F8 only |

**Example invocations:**

```bash
# List all supported kinds
python _tools/cex_8f_runner.py --list-kinds

# Dry-run with explicit kind (no LLM call)
python _tools/cex_8f_runner.py --kind knowledge_card --dry-run

# Execute: produce and save an artifact
python _tools/cex_8f_runner.py "create knowledge card about RAG patterns" --execute --nucleus n04

# Debug: stop after F4 REASON to inspect the plan
python _tools/cex_8f_runner.py "create agent" --step 4 --verbose

# Update an existing artifact without overwriting human edits
python _tools/cex_8f_runner.py "improve density" --update N04_knowledge/P01_knowledge/kc_rag.md

# Mode B Stage 1: write prompt_package only (cheap model does Stage 2)
python _tools/cex_8f_runner.py "create knowledge card" --mode B --stage 1

# Mode auto: detect from model tier
python _tools/cex_8f_runner.py "create prompt template" --execute --mode auto --model haiku
```

**Output:** prints the 8F trace. With `--execute`, saves file to the correct pillar directory
and prints the saved path. Exit code 0 = success; 1 = validation failure.

---

## 3. cex_doctor.py -- Quality Diagnostics

**Purpose:** Runs 118+ checks across all builders and artifacts. The quality gate for CI
and pre-publish validation. Checks frontmatter, ISO completeness, density, naming, non-ASCII,
and compilation.

**Usage:**
```bash
python _tools/cex_doctor.py [subcommand] [flags]
```

**Subcommands:**

| Subcommand | Description |
|-----------|-------------|
| (none) | Default check: diagnose only, no changes |
| `check` | Explicit check subcommand (same as default) |
| `summary` | Condensed summary output |
| `fix` | Diagnose + auto-fix naming issues |

**Key flags:**

| Flag | Type | Description |
|------|------|-------------|
| `--fix` | bool | Diagnose and auto-fix naming issues |
| `--signals` | bool | Check that every `complete` signal has a matching deliverable |
| `--vocab` | bool | Validate per-nucleus vocabulary KC presence (standalone check) |
| `--open-vars` | bool | Validate Article XIX open variables mandate for typed artifacts |
| `--wikilinks [PATH ...]` | path(s) | Check wikilink integrity for staged-only files (or given paths) |

**Example invocations:**

```bash
# Standard health check (run before every commit)
python _tools/cex_doctor.py

# Summary only
python _tools/cex_doctor.py summary

# Auto-fix naming issues
python _tools/cex_doctor.py --fix

# Check signal integrity (did all nuclei deliver what they signaled?)
python _tools/cex_doctor.py --signals

# Vocabulary KC presence check
python _tools/cex_doctor.py --vocab
```

**Output format:**
```
Result: 302 PASS | 0 FAIL | 3 WARN
```
Exit code 0 = PASS (0 FAIL); exit code 1 = FAIL (any FAIL present).

**Common failures and fixes:**

| FAIL message | Cause | Fix |
|-------------|-------|-----|
| `missing frontmatter field: quality` | `quality: null` absent | Add `quality: null` to frontmatter |
| `non-ASCII in code file` | Emoji/accented char in `.py` or `.ps1` | `python _tools/cex_sanitize.py --fix` |
| `density below 0.80` | Too much prose, not enough tables/bullets | Replace prose with tables |
| `missing ISO: bld_schema_{kind}.md` | Builder directory incomplete | Add the missing ISO file |

---

## 4. cex_compile.py -- Artifact Compiler

**Purpose:** Compiles `.md` artifacts to `.yaml` (forward) or renders compiled YAML back
to target formats (reverse). Every artifact must compile without errors to be publishable.
F8 COLLABORATE calls this automatically; use it manually to verify a single file.

**Usage:**
```bash
python _tools/cex_compile.py [file | --all | --lp LP] [flags]
```

**Key flags:**

| Flag | Type | Description |
|------|------|-------------|
| `file` | positional | Single `.md` file to compile |
| `--all` | bool | Compile all examples in all LPs (pillar directories) |
| `--lp LP` | str | Compile all examples in a specific LP (e.g., `P03`) |
| `--target {claude-md,cursorrules,customgpt,mcp}` | str | Reverse compile: render to target format |
| `--output` / `-o OUTPUT` | str | Output path for `--target` reverse compile |

**Example invocations:**

```bash
# Compile a single file (most common use)
python _tools/cex_compile.py N04_knowledge/P01_knowledge/kc_onboarding_concepts.md

# Compile all artifacts in P01
python _tools/cex_compile.py --lp P01

# Compile everything (slow; use before a major commit)
python _tools/cex_compile.py --all

# Reverse compile: render to CLAUDE.md format
python _tools/cex_compile.py --target claude-md --output docs/CLAUDE_export.md

# Reverse compile: render to CustomGPT instructions
python _tools/cex_compile.py --target customgpt --output docs/customgpt_instructions.txt
```

**Output:** prints `[OK] compiled: <path>` per file, or `[FAIL] <path>: <error>` on failure.
Exit code 0 = all compile; exit code 1 = any failure.

---

## 5. cex_install.py -- One-Command Turnkey Installer

**Purpose:** Gets CEXAI running on a clean machine in one command. Reads the frozen dependency
manifest (`.cex/config/dependency_manifest.yaml`), detects what is present vs missing, and -- by
default -- AUTO-INSTALLS the missing dependencies, then re-validates. Manifest-only (never runs a
command not declared in the manifest) and idempotent (skips anything already present).

**Usage:**
```bash
python _tools/cex_install.py [flags]  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```

**Key flags:**

| Flag | Type | Description |
|------|------|-------------|
| (none) | default | AUTO-INSTALL: detect -> plan -> install missing (required + recommended) -> re-validate |
| `--dry-run` | bool | Preview the matrix + plan + what WOULD install; change NOTHING |
| `--plan-only` | bool | Detect + plan + validate; install nothing (the safe check-only mode) |
| `--fix` | bool | Apply ONLY safe local fixes (create runtime dirs + write `.env` template); no system installs |
| `--include-optional` | bool | Also install OPTIONAL items (default scope: required + recommended) |
| `--profile {adaptive,mixed,free,premium}` | str | Budget profile for conditional deps (default: `adaptive`) |
| `--json` | bool | Machine-readable output |
| `--validate-only` | bool | Only run the validator delegation, then exit |
| `--no-validate` | bool | Skip the final validator cross-check (faster) |

**Example invocations:**

```bash
# Preview what would be installed (safe -- installs nothing)
python _tools/cex_install.py --dry-run  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

# Turnkey: auto-install every missing required + recommended dependency
python _tools/cex_install.py  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

# Check + plan only, no install (good for CI gating)
python _tools/cex_install.py --plan-only  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

# Auto-install including optional providers (gemini/codex/etc.)
python _tools/cex_install.py --include-optional  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```

**Output:** a present/missing dependency matrix, a PLAN (exact install command per missing item),
the install log (commands actually run), and a final `Verdict: READY` / `NOT-READY` with the count
of required items still missing. Exit code 0 = ready; non-zero = a required item is still missing.

---

## 6. cex_setup_validator.py -- Environment Validator

**Purpose:** Verifies the local environment across ten categories (runtime, packages,
MCP servers, env vars, structure, git hooks, system, Ollama, podcast, manifest).
`cex_install` delegates to this for its post-install cross-check; run it standalone to
diagnose a single category.

**Usage:**
```bash
python _tools/cex_setup_validator.py [flags]  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```

**Key flags:**

| Flag | Type | Description |
|------|------|-------------|
| `--category CATEGORY` | str | Check one category only: `runtime`, `packages`, `mcp_servers`, `env_vars`, `structure`, `git_hooks`, `system`, `ollama`, `podcast`, `manifest` |
| `--fix` | bool | Attempt auto-fix for FAIL items |
| `--json` | bool | Machine-readable JSON output |

**Example invocations:**

```bash
# Full environment validation
python _tools/cex_setup_validator.py  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

# Validate one category only
python _tools/cex_setup_validator.py --category packages  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

# Attempt auto-fix of failing items
python _tools/cex_setup_validator.py --fix  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```

**Output:** per-category `PASS` / `WARN` / `FAIL` lines plus a summary. Exit code 0 when all
checks pass.

---

## 7. the Task tool -- Nucleus Dispatch

**Purpose:** The operator entry point for delegating work to a nucleus (builder). Wraps the
per-runtime boot scripts; runs one nucleus (`solo`), up to six in parallel (`grid`), or N
parallel worktree builders (`swarm`), and also monitors and stops running nuclei. Cross-platform
(Mac/Linux/WSL/Git-Bash).

**Usage:**
```bash
# in-session dispatch (Task tool): <mode> [args]
```

**Key modes:**

| Mode | Form | Description |
|------|------|-------------|
| `solo` | `solo n0X "task"` | Dispatch one nucleus (N01-N07) on a task |
| `grid` | `grid MISSION` | Dispatch up to 6 parallel nuclei from handoffs in `.cex/runtime/handoffs/` |
| `swarm` | `swarm <kind> <N> "task"` | N parallel builders of one kind in isolated worktrees |
| `status` | `status` | Monitor running nuclei |
| `stop` | `stop` / `stop n0X` / `stop --all` | Stop your session's nuclei / one nucleus / all (DANGEROUS) |

**Key flags:**

| Flag | Description |
|------|-------------|
| `-m MODEL` | Model override (e.g. `-m sonnet`) |
| `-cli {claude,gemini,codex}` | Per-cell runtime override (boots `n0X_<cli>.ps1`) |
| `-w [id]` | Run in an isolated git worktree (grid: one per cell) |
| `--dry-run` | Show routing, spawn nothing |

**Example invocations:**

```bash
# Dispatch N03 on a build task
# in-session dispatch (Task tool): solo n03 "create a knowledge card about RAG"

# Dispatch a multi-nucleus grid from prepared handoffs
# in-session dispatch (Task tool): grid BRAND_LAUNCH

# Show routing without spawning anything
# in-session dispatch (Task tool): solo n04 -cli gemini --dry-run

# Monitor, then stop your session's nuclei
# in-session dispatch (Task tool): status
# in-session dispatch (Task tool): stop
```

**Output:** prints routing/dispatch info and spawns nucleus processes; with `--dry-run`,
prints the resolved boot target only.

---

## Tool Quick Reference

| Tool | Primary use | When to run |
|------|-------------|-------------|
| `cex_install.py` | One-command install of all dependencies | First run on a clean machine |
| `cex_setup_validator.py` | Validate the local environment | After install, or when something breaks |
| `cex_run.py --status` | Check system health | Start of any session |
| `cex_run.py "intent" --execute` | Build an artifact (easiest entry) | When you have a goal |
| `cex_8f_runner.py "intent" --execute` | Build with fine-grained control | When you need --kind/--nucleus/--step |
| `cex_doctor.py` | Validate all artifacts | Before every commit |
| `cex_compile.py <file>` | Compile a specific artifact | After editing a `.md` artifact |
| `cex_compile.py --all` | Compile everything | Before a release |
| `Task tool: dispatch solo n0X "task"` | Dispatch one nucleus | To delegate a build |
| `Task tool: dispatch grid MISSION` | Dispatch up to 6 nuclei | To run a multi-nucleus mission |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_faq_cexai_user | sibling | 0.55 |
