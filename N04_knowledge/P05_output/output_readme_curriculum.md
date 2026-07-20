---
id: n04_readme_curriculum
kind: output_template
8f: F6_produce
pillar: P05
quality: null
keywords: [output readme curriculum, output_template, knowledge, output, learn, explore, what you build, curriculum overview]
density_score: null
title: "Output Template -- Curriculum README"
version: "1.0.0"
author: N04
tags: [output_template, knowledge, output, P05]
tldr: "Render a learning-path README: tiered tracks, module overview, prerequisites, and quality metrics -- with every domain-specific value left as an open slot."
domain: knowledge
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p06_td_document_types
  - p07_em_n04_knowledge
primary_8f: PRODUCE
slots:
  track_table: "<the tiers/tracks this curriculum offers, with module ranges and prices>"
  module_list: "<the ordered module ids, titles, and deliverables>"
  render_target: "<the destination format -- README.md, landing page section, etc.>"
---

# What You'll Learn

`{{one_line_promise}}` -- a short statement of the transformation this
curriculum delivers, from `{{starting_point}}` to `{{end_state}}`.

## Track Table

| Track | Modules | What You Build | Price |
| :--- | :--- | :--- | :--- |
| `{{tier_1_name}}` | `{{tier_1_module_range}}` | `{{tier_1_deliverable}}` | `{{tier_1_price}}` |
| `{{tier_2_name}}` | `{{tier_2_module_range}}` | `{{tier_2_deliverable}}` | `{{tier_2_price}}` |
| `{{tier_3_name}}` | `{{tier_3_module_range}}` | `{{tier_3_deliverable}}` | `{{tier_3_price}}` |

Illustrative fill-in (not a real offer -- replace every cell above):

| Track | Modules | What You Build | Price |
| :--- | :--- | :--- | :--- |
| Foundations | M01-M03 | Your first typed artifact | Free |
| Builder | M04-M10 | A full working pipeline | `{{tier_2_price}}` |
| Master | M11-M14 | A deployed, tuned system | `{{tier_3_price}}` |

## Curriculum Overview

Each row is `{{module_id}}`: `{{module_title}}` -- `{{module_deliverable}}`.
Keep the deliverable concrete and checkable (a file, a working pipeline, a
passing test) -- never a vague verb like "understand" or "learn about".

- **`{{module_id_1}}`**: `{{module_title_1}}` -- `{{module_deliverable_1}}`
- **`{{module_id_2}}`**: `{{module_title_2}}` -- `{{module_deliverable_2}}`
- **`{{module_id_3}}`**: `{{module_title_3}}` -- `{{module_deliverable_3}}`

## Prerequisites

- `{{prereq_1}}` -- e.g. basic command-line comfort
- `{{prereq_2}}` -- e.g. version control fundamentals (clone, commit, push)
- `{{prereq_3}}` -- e.g. the language/runtime the curriculum builds on

## Quality Metrics

| Metric | Value | Threshold |
|--------|-------|-----------|
| Structural completeness | `{{completeness_rating}}` | >= 8.5 |
| Domain specificity | `{{domain_name}}` | Verified |
| Cross-reference density | `{{xref_count}}` refs | >= 3 refs |
| Actionability | `{{actionability_check}}` | Pass |

### Key Principles

- Every module deliverable is concrete and independently checkable
- Quality gates enforce a minimum threshold before any module is published
- Cross-references use explicit id-based links, not path-based ones
- Version tracking enables rollback to any previous curriculum revision

### How to use

```text
You are the consuming agent that acts on this output_template under F6 PRODUCE.
- Resolve the open slots (track_table, module_list, render_target) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this output_template defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F6 PRODUCE.
2. Bind track_table, module_list, and render_target from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the output_template behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_td_document_types]] | related | 0.25 |
| [[p07_em_n04_knowledge]] | related | 0.22 |
