---
id: p06_iface_engineering_nucleus_n03
kind: interface
8f: F1_constrain
pillar: P06
title: Interface -- Builder Nucleus
version: 2.0.0
created: 2026-03-30
updated: 2026-03-30
author: builder_agent
domain: meta-construction
quality: null
tags: [interface, builder, N03]
tldr: "N03 public API: 9 CLI commands (motor, runner, compile, doctor, forge, index, kind_register, nucleus_builder, feedback), Python-importable via cex_sdk, strict I/O contracts per tool."
keywords: [cex_agent, parse_intent, classify_kind, compile_artifact, run_health_check, score_artifact, kinds_meta.json, stdout, stderr]
density_score: 0.88
related:
  - p04_fn_builder_toolkit_n03
  - p04_cli_n03_build
  - p06_vs_artifact_output
  - bld_schema_interface
---

# Interface: Builder Nucleus

## CLI Commands

| Command | Purpose |
|---------|---------|
| cex_8f_motor.py --intent ... | Parse intent to kind |
| cex_8f_runner.py --kind X | Build single artifact |
| cex_doctor.py | Health check |
| cex_compile.py PATH | Compile .md to .yaml |
| cex_index.py | Rebuild index |
| cex_kind_register.py --kind X | Register new kind |
| cex_nucleus_builder.py --nucleus N0x | Build nucleus |
| cex_forge.py | Batch build |
| cex_feedback.py | Apply feedback |

## Input Contract

Minimum: intent string OR explicit kind name.
Maximum: intent + kind + pillar + context + domain + output_dir + model + dry_run.

## Output Contract

Success: file path + compiled path + quality score + signal JSON.
Failure: error signal with step number and reason.

## Python Import Surface

```python
from cex_sdk.build import CEXAgent, build
from cex_sdk.motor import parse_intent, classify_kind
from cex_sdk.compile import compile_artifact, compile_all
from cex_sdk.doctor import run_health_check
from cex_sdk.score import score_artifact, ScoreResult
```

## Exit Code Contract

All CLI tools follow the same exit code protocol:

| Code | Meaning | Consumer Action |
|------|---------|-----------------|
| 0 | Success | Read stdout for result |
| 1 | Validation failure | Parse stderr for issue list |
| 2 | Missing dependency | Install/configure and retry |
| 3 | Kind not found | Check kinds_meta.json |
| 4 | Quality below floor | Read score from stdout, decide retry |

## Backward Compatibility Rules

- Adding optional frontmatter fields: non-breaking (minor version bump)
- Removing a required field: breaking (major version bump + migration script)
- Changing field type (string to list): breaking
- Adding a new CLI flag: non-breaking if default preserves old behavior

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p04_fn_builder_toolkit_n03]] | upstream | 0.31 |
| [[p04_cli_n03_build]] | upstream | 0.30 |
| [[p06_vs_artifact_output]] | sibling | 0.27 |
| [[bld_schema_interface]] | related | 0.24 |
