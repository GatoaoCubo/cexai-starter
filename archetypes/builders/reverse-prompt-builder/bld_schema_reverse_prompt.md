---
id: schema_reverse_prompt_builder
kind: type_def
pillar: P06
llm_function: CONSTRAIN
domain: reverse_prompt
version: 1.0.0
created: "2026-07-03"
updated: "2026-07-03"
author: builder
tags:
  - "schema"
  - "reverse-prompt"
  - "P03"
  - "source-of-truth"
quality: null
title: "Schema Reverse Prompt"
tldr: "Field-level source of truth for reverse_prompt: ID pattern, frontmatter fields, the two-path naming discrepancy (p03_rp_ slug vs tree_sha filename), and enum values."
8f: "F1_constrain"
keywords:
  - "schema reverse prompt"
  - "schema"
  - "reverse-prompt"
  - "source-of-truth"
  - "^p03_rp_[a-z][a-z0-9_]+$"
  - "tree_sha"
  - "open_vars"
  - "frontmatter fields"
  - "two paths"
density_score: 0.90
related:
  - bld_config_reverse_prompt
  - bld_eval_reverse_prompt
  - reverse-prompt-builder
---

# Schema -- reverse-prompt-builder
> SOURCE OF TRUTH. All fields here MUST appear in `bld_output_template_reverse_prompt.md`. Zero drift permitted.
## ID Pattern
```
^p03_rp_[a-z][a-z0-9_]+$
```
Examples: `p03_rp_vercel_labs_skills_a1b2c3d`, `p03_rp_gitreverse_dry_run_example`
## The Naming Discrepancy (grounded, read before building)
`kinds_meta.json`'s `naming` field is `p03_rp_{{name}}.md` (the frontmatter `id` convention). The REAL synthesizer (`GitReverseSynthesizer._write_artifact`, `synthesizer.py:349-356`) writes its canonical runtime file as `<tree_sha>.md` under `.cex/runtime/artifacts/reverse_prompts/` -- the FILE BASENAME is the tree_sha, not the `p03_rp_` slug. This builder's drafts follow the `p03_rp_{{name}}.md` convention under `records/pool/prompts/`; a real synthesizer emission's frontmatter `id` may still carry a `p03_rp_`-style id even though its file basename is the tree_sha. Do NOT "fix" the tree_sha filenames to match this pattern -- that IS the cache/determinism key (FR-006).
## Frontmatter Fields
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| id | string | YES | -- | `p03_rp_{slug}`, unique |
| kind | enum | YES | -- | Fixed value: `reverse_prompt` |
| pillar | enum | YES | -- | Fixed value: `P03` |
| title | string | YES | -- | e.g. "Reverse Prompt: owner/repo" |
| version | string | YES | `"1.0.0"` | Semver |
| created / updated | string | YES | -- | ISO date |
| author | string | YES | -- | Agent/human id |
| source_url | string | YES | -- | Normalized `https://{github\|gitlab\|bitbucket}.com/<owner>/<repo>` |
| tree_sha | string | YES | -- | Real sha (repair/document of a live run) OR an explicit non-sha marker for `dry_run`/`calibration_pair` |
| open_vars | list | YES | 3-tuple | Always `[target_audience, target_runtime, complexity_level]` |
| filled_vars | map | YES | -- | Resolved `name -> value` |
| quality | float or null | YES | `null` | Gate score; null until validation |
| tags | list[string] | YES | `[]` | Include `reverse_prompt` |
| tldr | string | YES | -- | One sentence |
| keywords | list[string] | REC | `[]` | Search keywords |
| density_score | float | REC | `null` | Content density |
## Enum Values
### target_runtime
`claude-code` \| `codex` \| `gemini` \| `ollama` (matches `GitReverseSynthesizer._VALID_RUNTIMES`; `rebind_allowed: false` -- a runtime change is a fresh synthesis, FR-014)
### complexity_level
`introductory` \| `intermediate` \| `advanced` (matches `_VALID_COMPLEXITY`; `rebind_allowed: true`)
## Constraints
| Constraint | Rule |
|---|---|
| max_bytes | 8192 bytes per file (`kinds_meta.max_bytes`) |
| depends_on | `[prompt_template]` -- the fixed synthesis template this kind fills |
| kind lock | `kind` MUST be `reverse_prompt` -- never overridden |
| quality null | `quality: null` until an independent gate scores it |
| write path | `records/pool/prompts/p03_rp_{{name}}.md` for builder drafts; NEVER `.cex/runtime/artifacts/reverse_prompts/` (synthesizer-reserved) |
| license disclosure | `upstream_license` OR `derived_from_unlicensed_source: true` whenever `source_url` names a real repo |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_reverse_prompt]] | related | 0.55 |
| [[bld_eval_reverse_prompt]] | related | 0.54 |
| [[reverse-prompt-builder]] | upstream | 0.53 |
