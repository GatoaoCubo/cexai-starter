---
id: tools_prompt_package_builder
kind: tools
pillar: P04
llm_function: CALL
domain: prompt_package
version: 1.0.0
created: "2026-07-03"
updated: "2026-07-03"
author: builder
tags:
  - "tools"
  - "prompt-package"
  - "P03"
  - "decompose"
quality: null
title: "Tools Prompt Package"
tldr: "Real tool registry for prompt_package production -- the decompose orchestrator, the F1-F4 harvester, and the generic tool bucket registered in kind_tool_supplement.json."
8f: "F5_call"
keywords:
  - "tools prompt package"
  - "cex_decompose.py"
  - "cex_8f_runner.py"
  - "prompt_package"
  - "mode b"
  - "stage 1"
  - "stage 2"
density_score: 0.90
related:
  - bld_tools_prompt_template
  - bld_architecture_prompt_package
  - prompt-package-builder
  - bld_config_prompt_package
  - bld_orchestration_prompt_package
---

# Tools -- prompt-package-builder

## Tool Registry

| Tool | Status | Tag | Purpose |
|---|---|---|---|
| `_tools/cex_decompose.py` | ACTIVE | [CLI] | 3-stage dispatch orchestrator: Stage 1 (write package) -> Stage 2 (consume + F6) -> Stage 3 (gate + validate + commit + signal) |
| `_tools/cex_8f_runner.py` | ACTIVE | [CLI] | `--stage 1 --mode B` writes the package (`_write_prompt_package`); `--stage 2 --prompt-package <path> --execute` consumes it (`_run_mode_b_generate`) |
| Read | ACTIVE | [FS] | Read `tpl_prompt_package.md`, `p06_if_prompt_package.md`, sibling `pp_*.md` examples |
| Glob | ACTIVE | [FS] | `_find_latest_package` equivalent: `glob("pp_*.md")` under `.cex/runtime/packages/`, sorted by mtime |
| Grep | ACTIVE | [FS] | Search for `package_type: f6_prompt_package` or `target_kind:` collisions across the pool |
| Write | ACTIVE | [FS] | Produce the final `prompt_package` artifact under `.cex/runtime/packages/` |
| Edit | ACTIVE | [FS] | Patch `target_path`/`stage_2_model_hint` during VALIDATE phase without a full rewrite |
| `cex_wikilink_gate.py` | CONDITIONAL | [CLI] | Stage-3 W2 hard gate on the DOWNSTREAM artifact (not the package itself) -- `gate(path)` / `repair_file(path, fabricated)` |
| `cex_mentor_swarm.py` | CONDITIONAL | [CLI] | `load_escalation_ladder(model)` -- backs the A3 quality-floor climb when `CEX_DECOMPOSE_ESCALATE=1` |
| `cex_score_python.py` | CONDITIONAL | [CLI] | `score_fast(path)` -- zero-LLM structural score used by the A3 escalation check |

## Tool Descriptions

### `_tools/cex_decompose.py` [CLI] -- ACTIVE

The real 3-stage subprocess orchestrator. Invoke as:
```
python _tools/cex_decompose.py --nucleus n0X --task "<intent>" [--dry-run]
python _tools/cex_decompose.py --nucleus n0X --task "<intent>" --guard-on-factual warn
```
Resolves Stage 1/2 models via `tiers.decompose` in `.cex/config/nucleus_models.yaml`, precedence
CLI flag > env var > YAML tier > sensible default (resolved through `cex_model_resolver`).

### `_tools/cex_8f_runner.py` [CLI] -- ACTIVE

The ACTUAL package writer/reader. `_write_prompt_package` (lines 2001-2101) assembles frontmatter
(`package_type`, `task_id`, `target_kind`, `target_pillar`, `target_nucleus`, `target_path`,
`builder_isos_loaded`, `context_sources`, `density_target`, `max_bytes`, `stage`,
`stage_2_model_hint`, `mode`) plus the 4 body sections, then writes to
`pkg_dir / ("pp_%s_%s.md" % (kind, session_id))` under `.cex/runtime/packages/`.
`_run_mode_b_generate` (line ~2105) reads that same file back for Stage 2.

### Read / Glob / Grep / Write / Edit [FS] -- ACTIVE

Standard filesystem tools for manual/example authoring (the builder path, as opposed to the
auto-generated runtime path). Read the schema + interface docs before composing; Glob the
`.cex/runtime/packages/` pool (gitignored -- 121 real instances observed on disk this session,
`pp_*_auto_*.md` naming) and `N00_genesis/P03_prompt/examples/stress_decompose_packages/` (9
tracked examples, T01-T09) for style reference before assigning a new `task_id`.

### `cex_wikilink_gate.py` [CLI] -- CONDITIONAL

Only relevant to Stage 3, and only gates the DOWNSTREAM artifact Stage 2 produces -- never the
`prompt_package` itself. Included here because a prompt-package-builder invoked manually should
know the artifact it hands off will be gated before F8, per `cex_decompose.py` lines 260-289.

## Data Sources

| Source | Content | When to use |
|---|---|---|
| `N00_genesis/P06_schema/p06_if_prompt_package.md` | Bilateral contract: required fields, required sections, validation rules | Every production run |
| `N00_genesis/P03_prompt/tpl_prompt_package.md` | Frontmatter + body structure to follow | Every production run |
| `N00_genesis/P03_prompt/examples/stress_decompose_packages/` | 9 real examples (T01-T09); 3 use current `kind: prompt_package` frontmatter, 6 use the earlier `package_type` + `target_kind` variant | Style/format reference |
| `.cex/runtime/packages/` (gitignored) | Live auto-generated instances from real Stage-1 runs | Understand the REAL naming convention in production |
| `.cex/kind_tool_supplement.json` | Generic `kind_to_tools["prompt_package"]` bucket (see below) | Cross-check registered tooling |

## Registered Generic Tool Bucket (honesty note)

`.cex/kind_tool_supplement.json`'s `kind_to_tools["prompt_package"]` currently lists:
`cex_prompt_cache.py`, `cex_prompt_optimizer.py`, `cex_prompt_layers.py`, `cex_skill_loader.py`,
`cex_crew_runner.py`. Per the triage decision doc's Sec 3.2 correction, these are SHARED
boilerplate buckets (~33 generic tool-list groups across all 125 kinds), not prompt_package-
specific dispatch wiring -- the REAL, kind-specific mechanism is `cex_decompose.py` +
`cex_8f_runner.py`, neither of which appears in that generic bucket.

## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | live MCP / browser tools inside a package body | Defeats the Stage-2 no-live-tools contract |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_tools_prompt_template | sibling | 0.58 |
| [[bld_architecture_prompt_package]] | related | 0.55 |
| [[prompt-package-builder]] | related | 0.50 |
| bld_config_prompt_package | sibling | 0.47 |
| [[bld_orchestration_prompt_package]] | related | 0.44 |
