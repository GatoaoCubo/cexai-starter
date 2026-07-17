---
id: schema_prompt_template_builder
kind: type_def
pillar: P06
llm_function: CONSTRAIN
domain: prompt_template
version: 1.0.0
created: "2026-03-26"
updated: "2026-07-04"
author: builder
tags:
  - "schema"
  - "prompt-template"
  - "P03"
  - "source-of-truth"
quality: null
title: "Schema Prompt Template"
tldr: "Golden and anti-examples for prompt template construction, demonstrating ideal structure and common pitfalls."
8f: "F1_constrain"
keywords:
  - "schema prompt template"
  - "schema"
  - "prompt-template"
  - "source-of-truth"
  - "^p03_pt_[a-z][a-z0-9_]+$"
  - "examples:"
  - "| | pillar | enum | yes | — | fixed value:"
  - "frontmatter fields"
  - "variable object"
  - "variable object each"
density_score: 0.90
related:
  - bld_schema_reranker_config
  - bld_schema_benchmark_suite
  - bld_schema_integration_guide
  - bld_schema_sandbox_spec
  - bld_schema_dataset_card
---

# Schema — prompt-template-builder
> SOURCE OF TRUTH. All fields in this file MUST appear in OUTPUT_TEMPLATE.md. Zero drift permitted.
## ID Pattern
Regex: `^p03_pt_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem.
Examples: `p03_pt_knowledge_card`, `p03_pt_research_synthesis`, `p03_pt_code_review`

> **Status: LIVE-ENFORCED for new 8F builds (corrected 2026-07-04 -- judge-refuted
> the dormant claim by execution, N07-reproduced).** H02 in `_tools/cex_8f_runner.py`
> extracts the backtick-labeled Regex line in this section (extraction at ~503-511)
> and fires on every 8F run of this kind. The `_schema.yaml` id_pattern lane stays
> dormant -- two lanes, only this one is live. CONSEQUENCE: binds every NEW build;
> the pre-2026-07-04 corpus was ~55% non-compliant (worst of the 3 reviewed kinds --
> benchmark 33%, guardrail 50%) -- register R-263's id-rename sweep closed that gap.
> Evidence: `.claude/rules/8f-reasoning.md` H02 note; SPEC_R259 Section 1 + 8.

> **Exemption: cybersec-derived corpus.** 81 prompt_template files (`N05_operations/
> cybersec/` 77 + `cybersec_distilled/` 4) are externally-derived research with their
> own naming -- same precedent as hydration accounting (`N05_CYBERSEC_EXEMPT_PREFIXES`,
> `docs/HYDRATION_MAP.md` Sec 2). Never rebuilt via 8F, so H02 never fires on them.
> R-263 keeps them EXEMPT-DOCUMENTED, not renamed -- the sweep covered the
> hand-authored/genesis CORE corpus only (59 files, minus 6 held for a kind-correction
> decision on the `bld_output_*` builder-ISO cluster).

## Frontmatter Fields
> Tiering (R-262 sub-lane a, 2026-07-04, method = R-259): population >= 85% across 150
> confirmed on-disk `prompt_template` artifacts -> YES/enforced (wired into `_schema.yaml`
> `frontmatter_required`); < 85% -> REC, unless a grep-proven consumer overrides. (n=150, not
> 139 -- naive greps miss `.cex/` (hidden-dir) + `_courses/` (gitignored, 11 force-tracked
> files); `git ls-files` is authoritative -- same blind-spot class as R-259's CRLF-anchor and
> R-260's uncommitted-file gotchas.) `title`/`variables` were previously YES, demoted to REC
> at 50.0% / 11.3% population. See `docs/PROJECT_BACKLOG.md` R-262 (sub-lane a) +
> `docs/SPEC_R259_SCHEMA_PRACTICE_RECONCILIATION_2026_07_04.md`.
| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| id | string | YES | — | Unique identifier. Must match ID pattern above |
| kind | enum | YES | — | Fixed value: `prompt_template` |
| pillar | enum | YES | — | Fixed value: `P03` |
| version | string | YES | `"1.0.0"` | Semver string |
| created | string | YES | — | ISO date: YYYY-MM-DD |
| quality | float or null | YES | `null` | Gate score 0.0-1.0; null until first validation |
| tags | list[string] | YES | `[]` | Searchability tags |
| tldr | string | YES | — | One-sentence summary for discovery |
| title | string | REC | — | Human-readable name of the template (50.0% population; 98.4% among hand-authored/course/genesis artifacts (CORE, n=62) -- low overall population is concentrated in one cybersec-derived generator batch of 77 files, see R-262 (sub-lane a) dissent) |
| updated | string | REC | — | ISO date: YYYY-MM-DD, updated on every change (48.7% population; 95.2% CORE) |
| author | string | REC | — | Agent_group or human author ID (44.0% population; 96.8% CORE) |
| variables | list[object] | REC | — | List of variable definitions (see Variable Object below) (11.3% population; 27.4% CORE -- low even among hand-authored artifacts) |
| variable_syntax | enum | REC | `"mustache"` | `"mustache"` or `"bracket"` (11.3% population; 27.4% CORE) |
| composable | boolean | REC | `false` | True if template is designed for embedding in larger templates (12.7% population; 30.6% CORE) |
| domain | string | REC | — | Semantic domain: research, marketing, knowledge, code, etc. (39.3% population; 82.3% CORE -- just under the 85% bar even excluding the cybersec cluster; consumer evidence also weak/indirect, same ambiguity R-259 found for benchmark's `domain`) |
| keywords | list[string] | REC | `[]` | Search keywords distinct from tags |
| density_score | float | REC | `null` | Content density 0.0-1.0; null until measured |
## Variable Object
Each item in the `variables` list MUST contain:
| Field | Type | Required | Description |
|---|---|---|---|
| name | string | YES | Variable name matching the slot in the template body |
| type | enum | YES | `string`, `list`, `integer`, `boolean`, `object` |
| required | boolean | YES | Whether the variable must be supplied at render time |
| default | any or null | YES | Default value; null for required variables |
| description | string | YES | One sentence describing the variable's purpose |
## Body Structure
Every `prompt_template` artifact MUST contain these 5 sections in order:
1. `## Purpose` — one paragraph describing what the template produces and its reuse scope
2. `## Variables Table` — markdown table listing all variables with all 5 object fields
3. `## Template Body` — the parameterized prompt text in a fenced code block
4. `## Quality Gates` — table showing H01-H08 gate status for this artifact
5. `## Examples` — at least one filled example with variable values and rendered output
## Constraints
| Constraint | Rule |
|---|---|
| max_bytes | 8192 bytes per file |
| variable_syntax | `mustache` is tier-1 (`{{var}}`); `bracket` is tier-2 (`[VAR]`) — use bracket only when Mustache conflicts with target system |
| body completeness | Every `{{var}}` in the body MUST be declared in `variables`. Every declared variable MUST appear in the body at least once. |
| id uniqueness | No two prompt_template artifacts may share the same id |
| kind lock | The `kind` field MUST be `prompt_template` — never overridden |
| quality null | `quality: null` is valid for draft artifacts; must be a float before pool submission |
## Enum Values
### variable_syntax
- `mustache` — `{{variable}}` syntax (Mustache, Handlebars, Anthropic-compatible)
- `bracket` — `[VARIABLE]` syntax (fallback for systems where `{{}}` is reserved)
### variable.type
- `string` — plain text
- `list` — array of items
- `integer` — whole number
- `boolean` — true/false
- `object` — structured key-value data

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_schema_reranker_config | related | 0.56 |
| bld_schema_benchmark_suite | related | 0.55 |
| bld_schema_integration_guide | related | 0.54 |
| bld_schema_sandbox_spec | related | 0.53 |
| [[bld_schema_dataset_card]] | related | 0.53 |
