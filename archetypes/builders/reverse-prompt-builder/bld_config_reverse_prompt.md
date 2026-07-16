---
id: config_reverse_prompt_builder
kind: config
pillar: P09
llm_function: CONSTRAIN
domain: reverse_prompt
version: 1.0.0
created: "2026-07-03"
updated: "2026-07-03"
author: builder
tags: [config, reverse-prompt, P03, naming, constraints]
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
title: "Config Reverse Prompt"
tldr: "Naming convention, the two-path distinction (pool draft vs synthesizer runtime), size limits, and open-var rules for reverse_prompt."
8f: "F1_constrain"
keywords: [config reverse prompt, config, reverse-prompt, naming, constraints, "p03_rp_{topic_slug}.md", tree_sha, "records/pool/prompts", two paths]
density_score: 0.90
related:
  - p03_ins_reverse_prompt
  - bld_memory_reverse_prompt
  - bld_schema_reverse_prompt
  - reverse-prompt-builder
  - bld_collaboration_reverse_prompt
---
# Config -- reverse-prompt-builder
## Naming Convention
**Pattern**: `p03_rp_{topic_slug}.md` (kinds_meta naming field, verbatim)
| Component | Rule |
|---|---|
| `p03` | Pillar prefix -- always P03 for prompt layer |
| `rp` | Kind abbreviation -- always `rp` for `reverse_prompt` |
| `{topic_slug}` | Lowercase, underscored; recommend `{owner}_{repo}` or `{owner}_{repo}_{tree_sha_short}` |
| `.md` | Always markdown |
**Valid examples**: `p03_rp_vercel_labs_skills_a1b2c3d.md`, `p03_rp_gitreverse_dry_run.md`
**Invalid examples**: `reverse_prompt_vercel.md` (missing pillar prefix), `p03_vercel_skills.md` (missing `rp` abbreviation)
## The Two Paths (do not confuse)
| Path | Written by | Keyed by | Determinism |
|---|---|---|---|
| `.cex/runtime/artifacts/reverse_prompts/<tree_sha>.md` | `GitReverseSynthesizer._write_artifact` | tree_sha (cache key, FR-006) | Byte-identical guarantee |
| `records/pool/prompts/p03_rp_{{name}}.md` | reverse-prompt-builder (this) | topic_slug (human-legible) | NO determinism guarantee -- self-disclose in `## Provenance` |
## Size Limits
| Limit | Value | Scope |
|---|---|---|
| max_bytes | 8192 | Per artifact (kinds_meta.max_bytes) |
| max_open_vars | 3 (fixed) | target_audience, target_runtime, complexity_level -- no more, no fewer |
| max_entry_files_cited | 10 | Mirrors `GitReverseSynthesizer._MAX_ENTRY_FILES` |
| file_tree_budget | 5000 paths | Mirrors `_FILE_TREE_BUDGET`; beyond this, mark `truncated: true` |
## Open Var Rules
### target_audience (string, `rebind_allowed: true`)
Free text; default filler `"general software engineer"` when unresolved (mirrors `_DEFAULT_FILLERS`).
### target_runtime (enum, `rebind_allowed: false`)
`claude-code` \| `codex` \| `gemini` \| `ollama`. A runtime change is a NEW synthesis, not a rebind (FR-014) -- mirror this even in hand-authored drafts: never "rebind" a runtime in place, produce a new instance instead.
### complexity_level (enum, `rebind_allowed: true`)
`introductory` \| `intermediate` \| `advanced`. Default `intermediate`.
## Version Increment Rules
| Change type | Version bump |
|---|---|
| Repair a truncation/typo (mode=repair) | patch (1.0.0 -> 1.0.1) |
| Re-calibrate open_vars (new audience/complexity) | minor (1.0.0 -> 1.1.0) |
| Change `target_runtime` | NEW artifact (separate id), not a version bump |
| Fix frontmatter formatting only | patch |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_ins_reverse_prompt]] | upstream | 0.40 |
| [[bld_memory_reverse_prompt]] | downstream | 0.40 |
| [[bld_schema_reverse_prompt]] | upstream | 0.38 |
| [[reverse-prompt-builder]] | upstream | 0.36 |
| [[bld_collaboration_reverse_prompt]] | upstream | 0.36 |
