---
kind: output_template
id: bld_output_template_reverse_prompt
pillar: P00
quality: null
title: "Output Template Reverse Prompt"
version: "1.0.0"
author: n03_builder
tags: [reverse_prompt, builder, examples]
tldr: "Frontmatter + body shape for a builder-authored reverse_prompt draft: Purpose, Provenance, Repo Extract Summary, Open Vars Table, Reconstruction Prompt Body, Quality Gates, Examples."
domain: "reverse prompt construction"
created: "2026-07-03"
updated: "2026-07-03"
density_score: 0.90
llm_function: PRODUCE
related:
  - bld_eval_reverse_prompt
  - bld_architecture_reverse_prompt
---
id: p03_rp_`{{slug}}`
kind: reverse_prompt
pillar: P03
title: "`{{title}}`"
version: "`{{version}}`"
created: "`{{created}}`"
updated: "`{{updated}}`"
author: "`{{author}}`"
source_url: "`{{source_url}}`"
tree_sha: "`{{tree_sha_or_mode_marker}}`"
open_vars: [target_audience, target_runtime, complexity_level]
filled_vars:
  target_audience: "`{{target_audience}}`"
  target_runtime: "`{{target_runtime}}`"
  complexity_level: "`{{complexity_level}}`"
domain: "`{{domain}}`"
quality: `{{quality}}`
tags: [`{{tags}}`]
tldr: "`{{tldr}}`"
keywords: [`{{keywords}}`]
density_score: `{{density_score}}`
---

# `{{title}}`
## Purpose
`{{purpose_paragraph}}`
## Provenance
| Field | Value |
|---|---|
| mode | `{{mode}}` (document \| dry_run \| repair \| calibration_pair) |
| byte-deterministic? | `{{deterministic_flag}}` (true ONLY if mode=repair preserving a real tree_sha) |
| upstream_license | `{{upstream_license}}` |
| derived_from_unlicensed_source | `{{derived_from_unlicensed_source}}` |
## Repo Extract Summary
| Field | Value |
|---|---|
| primary_language | `{{primary_language}}` |
| description | `{{description}}` |
| default_branch | `{{default_branch}}` |
| truncated | `{{truncated}}` |
| entry_files_cited | `{{entry_files_cited}}` |
## Open Vars Table
| Open Var | Type | Resolved Value |
|---|---|---|
| target_audience | string | `{{target_audience}}` |
| target_runtime | enum | `{{target_runtime}}` |
| complexity_level | enum | `{{complexity_level}}` |
## Reconstruction Prompt Body
```
{{reconstruction_prompt_body}}
```
## Quality Gates
| Gate | Status | Notes |
|---|---|---|
| H01 frontmatter parses | `{{h01_status}}` | `{{h01_notes}}` |
| H02 id pattern | `{{h02_status}}` | `{{h02_notes}}` |
| H03 kind literal | `{{h03_status}}` | `{{h03_notes}}` |
| H04 quality null | `{{h04_status}}` | `{{h04_notes}}` |
| H05 open_vars complete | `{{h05_status}}` | `{{h05_notes}}` |
| H06 enum validity | `{{h06_status}}` | `{{h06_notes}}` |
| H07 source_url normalized | `{{h07_status}}` | `{{h07_notes}}` |
| H08 license disclosed | `{{h08_status}}` | `{{h08_notes}}` |
| H09 provenance present | `{{h09_status}}` | `{{h09_notes}}` |
| H10 size + path | `{{h10_status}}` | `{{h10_notes}}` |
## Examples
### Filled Example
**Variables:**
```yaml
{{example_variables}}
```
**Rendered Excerpt:**
```
{{example_rendered_output}}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_reverse_prompt]] | related | 0.25 |
| [[bld_architecture_reverse_prompt]] | sibling | 0.21 |
