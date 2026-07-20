---
id: p04_fn_builder_toolkit_n03
kind: function_def
8f: F6_produce
pillar: P04
title: Function Definitions -- Builder Toolkit
version: 1.0.0
created: 2026-03-30
updated: 2026-03-30
author: builder_agent
domain: meta-construction
quality: null
tags: [function-def, builder, N03, tools]
tldr: "N03 toolkit: 10 Python CLI functions (motor, runner, compiler, doctor, forge, indexer, feedback, kind_register, nucleus_builder, validate) -- all return exit code 0/1, all accept --help, composable via shell or Python import."
keywords: [parse_intent, run_pipeline, compile_artifact, batch_forge, rebuild_index, apply_feedback, register_kind, build_nucleus, validate_registries]
density_score: 0.90
related:
  - p06_iface_engineering_nucleus_n03
  - p04_cli_n03_build
  - p12_wf_builder_8f_pipeline
  - bld_schema_function_def
---

# Builder Toolkit: 10 Functions

| # | Name | Script | Input | Output | Timeout |
|---|------|--------|-------|--------|---------|
| 1 | parse_intent | cex_8f_motor.py | intent (string) | verb, objects, classified_kinds | 10s |
| 2 | run_pipeline | cex_8f_runner.py | kind, context, dry_run | path, quality, compiled | 120s |
| 3 | compile_artifact | cex_compile.py | path | yaml_path, success | 30s |
| 4 | check_health | cex_doctor.py | (none) | pass, warn, fail counts | 60s |
| 5 | batch_forge | cex_forge.py | kinds list, domain | created, failed counts | 300s |
| 6 | rebuild_index | cex_index.py | (none) | total_indexed | 60s |
| 7 | apply_feedback | cex_feedback.py | path, feedback | updated, new_quality | 60s |
| 8 | register_kind | cex_kind_register.py | kind, pillar, function, desc | files_updated | 30s |
| 9 | build_nucleus | cex_nucleus_builder.py | nucleus, name, domain | pass, total | 600s |
| 10 | validate_registries | cex_kind_register.py --validate | (none) | in_sync, gaps | 10s |

## Invocation Pattern

All tools follow: python _tools/{script} [args]
All return exit code 0 on success, non-zero on failure.
All write structured output to stdout (JSON or human-readable).

## Composition

The 8F Runner (F02) internally calls F03-F06-F10 in sequence.
For full artifact creation: F01 > F02 (which runs F1-F8 internally).
For batch: F05 calls F02 in parallel.
For nucleus: F09 calls F02 sequentially for each kind.

## Dependency Graph

```
parse_intent (F01)
    |
    v
run_pipeline (F02) -----> compile_artifact (F03) ----> rebuild_index (F06)
    |                          |
    |                          v
    |                    check_health (F04) -- standalone diagnostic
    |
    +---> batch_forge (F05) -- parallel wrapper around F02
    +---> build_nucleus (F09) -- sequential wrapper around F02
    +---> apply_feedback (F07) -- post-build quality iteration
    +---> register_kind (F08) -- pre-build kind registration
    +---> validate_registries (F10) -- consistency check for F08 outputs
```

## Error Handling Convention

All tools follow the same error output protocol:
- Structured errors to stderr as `[TOOL_NAME] ERROR: {message}`
- Exit code 1 for recoverable errors (retry-safe)
- Exit code 2 for environment errors (missing dependency, no API key)
- Never silently swallow errors -- every failure path logs explicitly

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_iface_engineering_nucleus_n03]] | downstream | 0.29 |
| [[p04_cli_n03_build]] | sibling | 0.27 |
| [[p12_wf_builder_8f_pipeline]] | related | 0.22 |
| [[bld_schema_function_def]] | related | 0.20 |
