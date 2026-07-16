---
kind: output_template
id: bld_output_template_visual_workflow
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for visual_workflow production
quality: null
title: "Output Template Visual Workflow"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [visual_workflow, builder, output_template]
tldr: "Output template for visual workflow: frontmatter field guide, required body sections, filled example, and quality gate checklist for gui-based workflow editor configuration."
domain: "visual_workflow construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [visual_workflow construction, output template visual workflow, frontmatter field guide, required body sections, filled example, visual_workflow, builder, output_template, markdown, quality gate checklist]
density_score: 0.85
related:
  - bld_output_template_dataset_card
  - bld_output_template_collaboration_pattern
  - bld_config_visual_workflow
  - bld_output_query_optimizer
  - bld_output_template_thinking_config
---
```markdown
```yaml
---
id: p12_vw_{{name}}.md <!-- ^p12_vw_[a-z][a-z0-9_]+.md$ -->
title: `{{title}}` <!-- Workflow title -->
description: `{{description}}` <!-- Brief purpose -->
author: `{{author}}` <!-- Owner -->
version: `{{version}}` <!-- vX.X -->
quality: null <!-- Must be null -->
created: `{{created}}` <!-- YYYY-MM-DD -->
updated: `{{updated}}` <!-- YYYY-MM-DD -->
---
```

| Step | Action | Responsible |
|------|--------|-------------|
| 1    | Start  | {{user}}    |
| 2    | Review | {{team}}    |

```python
# Example script
def workflow_step():
    print("`{{step_name}}` executed by `{{role}}`")
```
```

## Quality Gate Checklist

| Gate | Check | Pass Condition |
|------|-------|---------------|
| H01 | Frontmatter complete | All required fields present with valid types |
| H02 | ID matches filename | id field equals filename stem |
| H03 | Naming convention | Follows p12_vw_{{name}}.md pattern |
| H04 | Body sections present | All required sections non-empty |
| H05 | Size within limits | Total <= 5120 bytes |
| H06 | No placeholder text | No `{{var}}` unreplaced |
| H07 | quality: null | Never self-scored |

## Properties

| Property | Value |
|----------|-------|
| Kind | `output` |
| Pillar | P05 |
| Domain | visual workflow construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_dataset_card]] | sibling | 0.33 |
| [[bld_output_template_collaboration_pattern]] | sibling | 0.33 |
| [[bld_config_visual_workflow]] | downstream | 0.31 |
| [[bld_output_query_optimizer]] | sibling | 0.31 |
| [[bld_output_template_thinking_config]] | sibling | 0.31 |
