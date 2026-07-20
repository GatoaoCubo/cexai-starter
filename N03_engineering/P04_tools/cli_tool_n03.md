---
id: p04_cli_n03_build
kind: cli_tool
8f: F5_call
pillar: P04
title: "CLI Tool -- N03 Build Interface"
version: 1.0.0
created: 2026-04-17
author: n03_engineering
domain: artifact-construction
quality: null
tags: [cli-tool, N03, build, interface, 8F, dispatch]
tldr: "CLI interface contract for the nucleus's primary build entry point. Documents all flags, subcommands, exit codes, and integration with the 8F pipeline. Used by the orchestrator dispatch and direct human invocation."
keywords: [8f pipeline, govern, compile step, signal writer, nucleus id, intent, kind, pillar]
density_score: 0.91
updated: "2026-04-17"
related:
  - p06_is_build_contract
  - p01_fse_n07_dispatch
---

# CLI Tool: N03 Build Interface

## Overview

The build CLI is N03's primary interface. It accepts a build contract, executes the full
8F pipeline, and outputs a structured result. All orchestrator dispatches to N03 route through
this interface.

## Base Command

```bash
python _tools/cex_8f_runner.py [OPTIONS]
```

## Subcommands

| Subcommand | Purpose |
|-----------|---------|
| `build` | Execute full 8F pipeline (default) |
| `validate` | Run F7 GOVERN only (no F6, no F8) |
| `dry-run` | Execute F1-F5, print plan, stop before F6 |
| `improve` | Run self-improvement loop on target artifact |
| `batch` | Process list of intents from file |

## Options (build subcommand)

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--intent` | `-i` | string | required* | Natural language build request |
| `--kind` | `-k` | string | resolved | Explicit kind override |
| `--pillar` | `-p` | string | derived | Pillar override |
| `--verb` | `-v` | enum | CREATE | Build action verb |
| `--quality-target` | `-q` | float | 9.0 | Minimum quality score |
| `--domain` | `-d` | string | null | Domain for context injection |
| `--output-dir` | `-o` | path | derived | Override output directory |
| `--model` | `-m` | enum | mid-tier | Model tier override |
| `--dry-run` | | bool | false | Simulate; print plan only |
| `--no-compile` | | bool | false | Skip compile step after save |
| `--no-signal` | | bool | false | Skip completion signal |
| `--force` | `-f` | bool | false | Overwrite existing artifact |
| `--nucleus` | `-n` | enum | n03 | Executing nucleus ID |

*`--intent` OR `--kind` required; both may be specified.

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Build complete; all gates passed | Orchestrator proceeds to next wave |
| 1 | Build failed; artifact not saved | Orchestrator checks failure signal |
| 2 | Validation error; bad input contract | Orchestrator corrects dispatch params |
| 3 | Compile error; artifact saved but invalid YAML | Orchestrator triggers a fix loop |
| 4 | Quality gate failed after 2 retries | Orchestrator escalation required |
| 5 | Token budget exhausted | Orchestrator pauses dispatch |

## Usage Examples

### Minimal build
```bash
python _tools/cex_8f_runner.py -i "create a system prompt for the research agent"
```

### Explicit kind + quality target
```bash
python _tools/cex_8f_runner.py \
  --kind knowledge_card \
  --verb CREATE \
  --domain "embedding strategies" \
  --quality-target 9.5 \
  --nucleus n03
```

### Validate existing artifact (no write)
```bash
python _tools/cex_8f_runner.py validate \
  --kind scoring_rubric \
  N03_engineering/P07_evals/scoring_rubric_n03.md
```

### Batch build from file
```bash
python _tools/cex_8f_runner.py batch \
  --file .cex/runtime/handoffs/batch_n03_w1.txt \
  --nucleus n03 \
  --quality-target 9.0
```

### Dry run (print plan, no write)
```bash
python _tools/cex_8f_runner.py --dry-run \
  -i "create an input schema for the build contract" \
  --kind input_schema
```

## stdout Format (machine-parseable)

```
=== 8F PIPELINE ===
F1 CONSTRAIN: kind=input_schema, pillar=P06, max=3072B
F2 BECOME: input-schema-builder loaded (12 ISOs, one per pillar)
F3 INJECT: kc_input_schema.md + 2 examples. Match: 72%
F4 REASON: 5 sections, approach=template (adapt from match)
F5 CALL: compile+doctor+index ready. 3 similar found.
F6 PRODUCE: 2,840 bytes, 5 sections, density=0.91
F7 GOVERN: Score pending. Gates: 7/7.
F8 COLLABORATE: saved N03_engineering/P06_schema/input_schema_build_contract.md. Compiled. Committed.
===================
EXIT: 0
```

## Integration with Orchestrator Dispatch

The orchestrator writes a handoff to `.cex/runtime/handoffs/n03_task.md`.
N03 reads the handoff on boot. The handoff contains structured CLI arguments:

```yaml
# Handoff excerpt
cli_args:
  kind: input_schema
  verb: CREATE
  quality_target: 9.0
  nucleus: n03
  compile: true
  signal: true
```

N03's boot script reads the task file, constructs the CLI call, executes it.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_is_build_contract]] | downstream | 0.35 |
| [[p01_fse_n07_dispatch]] | upstream | 0.33 |
