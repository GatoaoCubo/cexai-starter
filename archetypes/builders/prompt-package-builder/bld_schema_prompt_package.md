---
id: schema_prompt_package_builder
kind: type_def
pillar: P06
llm_function: CONSTRAIN
domain: prompt_package
version: 1.0.0
created: "2026-07-03"
updated: "2026-07-03"
author: builder
tags:
  - "schema"
  - "prompt-package"
  - "P03"
  - "source-of-truth"
quality: null
title: "Schema Prompt Package"
tldr: "Field-by-field schema for prompt_package, reconciling .cex/kinds_meta.json against the real interface contract and the real generator code."
8f: "F1_constrain"
keywords:
  - "schema prompt package"
  - "p06_if_prompt_package"
  - "f6_prompt_package"
  - "target_kind"
  - "max_bytes"
  - "16384"
density_score: 0.90
related:
  - bld_schema_prompt_template
  - prompt-package-builder
  - bld_architecture_prompt_package
  - bld_config_prompt_package
---

# Schema -- prompt-package-builder

> SOURCE OF TRUTH for the artifact this builder produces. Cross-checked against
> `.cex/kinds_meta.json`, `N00_genesis/P06_schema/p06_if_prompt_package.md`, and the real
> writer `_tools/cex_8f_runner.py::_write_prompt_package`.

## ID Pattern

```
Registered (.cex/kinds_meta.json "naming"):  p03_pp_{{task_id}}.md
Observed real (cex_8f_runner.py line ~2088): pp_{target_kind}_{session_id}.md
```
Neither `.cex/runtime/packages/` (121 live files, gitignored) nor
`N00_genesis/P03_prompt/examples/stress_decompose_packages/` (9 tracked examples) contain a
single `p03_pp_`-prefixed filename. This builder follows the OBSERVED convention
(`pp_{target_kind}_{id}.md`) because `cex_decompose.py::_find_latest_package` globs `pp_*.md` --
a `p03_pp_`-prefixed file would still match that glob, but would NOT match any file a human
searching the pool by the real examples' naming would expect. Report the mismatch; do not
silently "fix" the registry from inside a builder ISO.

## Frontmatter Fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| id | string | YES | -- | Unique identifier; see ID Pattern above for the 2 conventions |
| kind | enum | YES | -- | Fixed value: `prompt_package` |
| pillar | enum | YES | -- | Fixed value: `P03` |
| package_type | literal | YES | `f6_prompt_package` | Identifies the file as a prompt package (interface field 1/8) |
| task_id | string | YES | -- | Session/task identifier (interface field, real writer uses `self.session_id`) |
| target_kind | string | YES | -- | The kind Stage 2 must produce; MUST resolve in `.cex/kinds_meta.json` |
| target_pillar | enum P01-P12 | YES | -- | Pillar of the TARGET kind (not necessarily P03) |
| target_nucleus | string | YES | -- | Owning nucleus, e.g. `N03`; real writer defaults to `os.environ["CEX_NUCLEUS"]` or `n07` |
| target_path | string (file path) | YES | -- | Where Stage 2 writes the produced artifact |
| builder_isos_loaded | integer | YES | -- | Count of builder ISOs loaded by Stage 1 |
| context_sources | integer | YES | -- | Count of knowledge sources injected |
| density_target | float 0.80-1.00 | YES | 0.85 | Minimum density Stage 2 must achieve |
| max_bytes | integer | YES | -- | Hard byte cap; <= 32768 (interface) AND <= 16384 (this kind's own registered cap) |
| stage | literal | YES | 1 | Always `1` for a prompt_package output (it IS the Stage-1 artifact) |
| stage_2_model_hint | string | REC | `claude-haiku-4-5-20251001` | Soft preference; `cex_decompose.py` resolution precedence overrides it |
| mode | literal | YES | `B` | Marks the decomposed (Mode B) pipeline |
| quality | float or null | YES | `null` | Gate score; null until Stage 3 scores it |
| tags | list[string] | YES | `[]` | Searchability tags |

## Body Structure

Every `prompt_package` artifact MUST contain these 4 sections in order (per
`p06_if_prompt_package.md`'s Required Body Sections table):
1. `## IDENTITY (from F2 BECOME)` -- builder persona + sin lens + rules for Stage 2
2. `## CONTEXT (from F3 INJECT)` -- pre-compiled knowledge: existing artifacts, KCs, examples
3. `## PLAN (from F4 REASON)` -- section list, approach, density target, template match score
4. `## TEMPLATE (generate this artifact)` -- frontmatter skeleton + section headers with fill
   markers Stage 2 must resolve

## Constraints

| Constraint | Rule |
|---|---|
| max_bytes | 16384 per `.cex/kinds_meta.json` (this kind's registered cap); interface hard ceiling is 32768 -- the TIGHTER of the two always wins |
| `package_type` | MUST equal literal `f6_prompt_package` -- any other value is INVALID (Stage 2 must not consume) |
| `target_kind` | MUST resolve in `.cex/kinds_meta.json` -- an unregistered kind is INVALID |
| fill-marker | TEMPLATE section MUST contain >= 1 fill marker; `{{...}}` (real template + real writer) OR `[FILL: ...]` (interface doc) -- both attested, accept either |
| `quality` null | Valid at authoring AND at Stage-2 consumption time -- Stage 3 tools score, never the model |
| kind lock | `kind` field MUST be `prompt_package` -- never overridden by the embedded TEMPLATE's own `kind:` (that one is the TARGET artifact's kind) |
| no live tools in body | `## CONTEXT` MUST carry pre-resolved results, never an unexecuted MCP/retrieval call |

## Validation Rules (from p06_if_prompt_package.md, verbatim)

A package is **valid** iff ALL hold: frontmatter parses; all 8 required fields present + typed;
all 4 body sections present; `## TEMPLATE` has >= 1 fill marker; `target_path` is writable under
a nucleus directory; `density_target` in [0.80, 1.00]; `max_bytes` positive integer <= 32768.

A package is **invalid** (Stage 2 MUST NOT consume) if ANY hold: `package_type !=
f6_prompt_package`; missing `## TEMPLATE`; `target_kind` not in `.cex/kinds_meta.json`;
`max_bytes` exceeds the target kind's own hard cap.

## Enum Values

### mode
- `B` -- decomposed (Mode B); the only value this kind's packages carry today

### stage
- `1` -- always 1; a prompt_package IS the Stage-1 output, it never represents Stage 2 or 3

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_schema_prompt_template | sibling | 0.56 |
| [[prompt-package-builder]] | related | 0.53 |
| [[bld_architecture_prompt_package]] | related | 0.50 |
| bld_config_prompt_package | sibling | 0.48 |
