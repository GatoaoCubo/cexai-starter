---
id: config_prompt_package_builder
kind: config
pillar: P09
llm_function: CONSTRAIN
domain: prompt_package
version: 1.0.0
created: "2026-07-03"
updated: "2026-07-03"
author: builder
tags: [config, prompt-package, P03, naming, decompose]
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Prompt Package"
tldr: "Naming, paths, and size limits for prompt_package -- the registered convention vs the real observed convention, reconciled honestly."
8f: "F1_constrain"
keywords: [config prompt package, naming, p03_pp_task_id, pp_target_kind_session_id, cex_decompose.py, max_bytes, 16384]
density_score: 0.90
related:
  - p03_ins_prompt_package
  - bld_memory_prompt_package
  - bld_knowledge_card_prompt_package
  - prompt-package-builder
  - bld_orchestration_prompt_package
---
# Config -- prompt-package-builder

## Naming Convention

**Registered pattern** (`.cex/kinds_meta.json` `naming` field): `p03_pp_{{task_id}}.md`

**Observed real pattern** (`_tools/cex_8f_runner.py` line ~2088,
`pkg_filename = "pp_%s_%s.md" % (self.state.kind, self.session_id)`): `pp_{target_kind}_{session_id}.md`

| Component | Rule (real convention) |
|---|---|
| `pp` | Kind abbreviation -- always `pp` for prompt_package, no pillar prefix in practice |
| `{target_kind}` | The kind Stage 2 must produce, e.g. `knowledge_card`, `agent`, `pipeline_template` |
| `{session_id}` | The Stage-1 session identifier (numeric epoch in auto-generated files; `T01`-`T09` in the tracked example corpus) |
| `.md` | Always markdown |

**Valid examples (all real, found on disk this session)**:
- `pp_T05_pipeline_template.md` (`N00_genesis/P03_prompt/examples/stress_decompose_packages/`)
- `pp_agent_N04_auto_1780977687.md` (`.cex/runtime/packages/`, gitignored)
- `pp_knowledge_card_N01_auto_1780985482.md` (`.cex/runtime/packages/`, gitignored)

**Not observed anywhere on disk** (registered but unused in practice): `p03_pp_{{task_id}}.md`.
Neither the 9-file tracked example corpus nor the 121 live gitignored instances found this
session use the `p03_` prefix. This is a genuine registry-vs-practice gap, reported here rather
than resolved unilaterally.

## File Paths

| Context | Path |
|---|---|
| Live runtime instances (gitignored) | `.cex/runtime/packages/pp_{target_kind}_{session_id}.md` |
| Tracked example corpus | `N00_genesis/P03_prompt/examples/stress_decompose_packages/pp_{T0N}_{slug}.md` |
| Authoring template | `N00_genesis/P03_prompt/tpl_prompt_package.md` |
| Interface contract | `N00_genesis/P06_schema/p06_if_prompt_package.md` |
| Builder reference | `archetypes/builders/prompt-package-builder/` |

## Size Limits

| Limit | Value | Scope |
|---|---|---|
| max_bytes (this kind, `.cex/kinds_meta.json`) | 16384 | Per prompt_package artifact file |
| max_bytes (interface hard ceiling) | 32768 | Upper bound any package's own `max_bytes` field may declare |
| Stage-1 truncation budgets (real, from `_write_prompt_package`) | IDENTITY <= 2000 chars, builder KC <= 1500 chars, per-domain-KC <= 1000 chars (up to 3), injected context <= 1500 chars, PLAN <= 2000 chars, TEMPLATE <= 3000 chars | Per body-section slice inside the real writer |
| density_target | 0.80-1.00, default 0.85 | Minimum density Stage 2 must achieve in the PRODUCED artifact |

## Frontmatter Field Enums

### mode
- `B` -- decomposed (Mode B); this kind's `mode` field is always `B`

### package_type
- `f6_prompt_package` -- the ONLY valid literal; any other value is INVALID per H02

### Real `mode:` field on the embedded TARGET (distinct from the package's own `mode: B`)
- `repair` -- Stage 1 is handing off a broken-artifact fix (T07 real precedent, `target_kind: bugloop`)
- `evolve` -- Stage 1 is handing off a low-quality-artifact improvement (T08 real precedent,
  `target_kind: optimizer`)
- unset -- ordinary fresh-build handoff (the common case)

## Version Increment Rules

| Change type | Version bump |
|---|---|
| Add new optional frontmatter field | patch (1.0.0 -> 1.0.1) |
| Add new required frontmatter field | minor (1.0.0 -> 1.1.0) |
| Remove or rename a required field | major (1.0.0 -> 2.0.0) |
| Change the 4-section body order | minor (1.0.0 -> 1.1.0) |
| Reconcile the naming-pattern gap (registry vs. practice) | major, once decided -- touches every consumer of `.cex/runtime/packages/` |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_ins_prompt_package]] | upstream | 0.40 |
| [[bld_memory_prompt_package]] | downstream | 0.40 |
| [[bld_knowledge_prompt_package]] | upstream | 0.38 |
| [[prompt-package-builder]] | upstream | 0.36 |
| [[bld_orchestration_prompt_package]] | upstream | 0.36 |
