---
kind: output_template
id: bld_output_template_prompt_package
pillar: P05
quality: null
title: "Output Template Prompt Package"
version: "1.0.0"
author: builder
tags: [prompt_package, builder, decompose, mode-b, examples]
tldr: "The exact frontmatter + 4-section body scaffold a prompt_package must fill, mirrored from the real tpl_prompt_package.md and the real cex_8f_runner.py writer."
domain: "prompt package construction"
created: "2026-07-03"
updated: "2026-07-03"
density_score: 0.90
llm_function: PRODUCE
8f: "F6_produce"
related:
  - p03_ins_prompt_package
  - bld_output_template_prompt_template
  - schema_prompt_package_builder
  - bld_architecture_prompt_package
  - prompt-package-builder
---
id: `pp_{{target_kind}}_{{task_id}}`
kind: prompt_package
pillar: P03
package_type: f6_prompt_package
task_id: `{{task_id}}`
target_kind: `{{target_kind}}`
target_pillar: `{{target_pillar}}`
target_nucleus: `{{target_nucleus}}`
target_path: `{{target_path}}`
builder_isos_loaded: `{{builder_isos_loaded}}`
context_sources: `{{context_sources}}`
density_target: `{{density_target}}`
max_bytes: `{{max_bytes}}`
stage: 1
stage_2_model_hint: `{{stage_2_model_hint}}`
mode: B
title: "`{{title}}`"
version: "1.0.0"
quality: null
tags: [`{{tags}}`]
---

# `{{title}}`

## IDENTITY (from F2 BECOME)

You are a `{{target_kind}}`-builder. Your role is to produce a structured `{{target_kind}}`
artifact that `{{purpose}}`.
Sin lens: `{{sin}}` -- `{{tagline}}`.

Builder contract: frontmatter with id/kind/title/version/quality:null/tags, body with
>= `{{min_sections}}` sections, at least `{{min_tables}}` table, at least `{{min_wikilinks}}`
wikilinks, density >= `{{density_target}}`.

## CONTEXT (from F3 INJECT)

### Domain knowledge:
- `{{fact_1}}`
- `{{fact_2}}`

### Related artifacts in this codebase:
- `{{artifact_1}}` -- `{{description_1}}`
- `{{artifact_2}}` -- `{{description_2}}`

## PLAN (from F4 REASON)

Sections: [`{{section_list}}`]
Approach: `{{template|hybrid|fresh}}`
Density target: `{{density_target}}`
Estimated output: ~`{{bytes}}` bytes, `{{n}}` sections

## TEMPLATE (generate this artifact)

```markdown
---
id: `{{id}}`
kind: `{{target_kind}}`
pillar: `{{target_pillar}}`
title: "`{{title}}`"
version: 1.0.0
quality: null
tags: [`{{tags}}`]
---

# `{{title}}`

## Section 1
`{{content}}`

## Section 2
`{{content}}`

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| `{{ref}}` | related | `{{score}}` |
```

## Quality Gates

| Gate | Status | Notes |
|---|---|---|
| H01 package_type literal | `{{h01_status}}` | `{{h01_notes}}` |
| H02 target_kind resolves | `{{h02_status}}` | `{{h02_notes}}` |
| H03 4 body sections present | `{{h03_status}}` | `{{h03_notes}}` |
| H04 fill-marker present in TEMPLATE | `{{h04_status}}` | `{{h04_notes}}` |
| H05 size <= registered max_bytes | `{{h05_status}}` | `{{h05_notes}}` |
| H06 quality is null | `{{h06_status}}` | `{{h06_notes}}` |

## Examples

### Filled Example (real, from `.cex/runtime/packages/`)
**Frontmatter (observed convention -- no `p03_pp_` prefix):**
```yaml
task_id: N04_auto_1780985482
target_kind: knowledge_card
target_pillar: P01
target_nucleus: N01
mode: B
```
**Filename**: `pp_knowledge_card_N01_auto_1780985482.md`

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_ins_prompt_package]] | related | 0.29 |
| [[bld_output_template_prompt_template]] | sibling | 0.25 |
| [[schema_prompt_package_builder]] | related | 0.24 |
| [[bld_architecture_prompt_package]] | sibling | 0.23 |
| [[prompt-package-builder]] | related | 0.21 |
