---
quality: null
quality: null
kind: config
id: bld_config_context_file
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints for context_file
pattern: CONFIG restricts SCHEMA, never contradicts it
effort: low
max_turns: 15
disallowed_tools: []
fork_context: inline
hooks:
  pre_build: null
  post_build: "python _tools/cex_compile.py {path}"
  on_error: null
  on_quality_fail: null
permission_scope: pillar
title: "Config: context_file Production Rules"
version: "1.0.0"
author: n03_builder
tags: [context_file, builder, config, hermes_origin]
tldr: "Naming, path, byte budget, scope constraints for context_file production."
domain: "workspace instruction auto-injection"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints for context_file, workspace instruction auto-injection, context_file production rules, byte budget, context_file, builder, config]
density_score: 0.90
related:
  - ctx_{{scope}}
  - kc_context_file
  - bld_schema_context_file
---

# Config: context_file Production Rules

## Naming Convention
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | `{{scope_slug}}_context.md` | `cex_workspace_context.md`, `n03_nucleus_context.md` |
| Builder directory | kebab-case | `context-file-builder/` |
| Frontmatter id | `ctx_`{{scope_slug}} | `ctx_cex_workspace`, `ctx_n03_nucleus` |
| scope_slug | snake_case, lowercase | `cex_workspace`, `sprint42_session` |
Rule: id MUST equal filename stem (without .md extension).

## File Paths
| Scope | Output path |
|-------|------------|
| global | project root or `.cex/config/global_context.md` |
| workspace | project root (CLAUDE.md equivalent): `workspace_context.md` or `CLAUDE.md` |
| nucleus | `N0X_{domain}/P03_prompt/ctx_n0X_nucleus.md` |
| session | `.cex/runtime/sessions/ctx_`{{session_id}}`.md` (ephemeral) |
Compiled: `{same_dir}/compiled/ctx_`{{scope_slug}}`.yaml`

## Size Limits (aligned with SCHEMA)
| Scope | Recommended bytes | Max bytes |
|-------|------------------|-----------|
| global | 500-1000 | 8192 |
| workspace | 500-2048 | 8192 |
| nucleus | 200-1024 | 4096 |
| session | 100-512 | 2048 |
Rule: narrower scope = smaller budget (less override surface needed).

## Injection Point Selection
| Use case | Preferred injection_point |
|----------|--------------------------|
| Stable workspace conventions | session_start |
| Per-nucleus build rules | session_start |
| Compliance-critical (must not be missed) | every_turn |
| 8F pipeline-specific overlay | f3_inject |
| Ephemeral sprint context | f3_inject (with session scope) |

## Priority Ordering
| Scope | Recommended priority |
|-------|---------------------|
| global | 0 |
| workspace | 1 |
| nucleus | 2 |
| session | 3 |
Rule: lower number = loads earlier; higher number = overrides on conflict (last write wins).

## Body Requirements
- Sections: at least 1 `##` section heading
- Rules per section: minimum 3 items
- Style: ALWAYS/NEVER pattern preferred; all rules must be actionable and verifiable
- Exclusions: NO facts, NO `{{vars}}`, NO step-by-step procedural recipes
- Duplication: child must NOT copy parent chain rules verbatim

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [\[ctx_`{{scope}}`\]] | upstream | 0.38 |
| [[kc_context_file]] | upstream | 0.37 |
| [[bld_schema_context_file]] | upstream | 0.36 |
| [[bld_knowledge_context_file]] | upstream | 0.36 |
