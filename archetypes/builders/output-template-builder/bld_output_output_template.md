---
kind: output_template
id: bld_output_template_output_template
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce an output_template artifact (the reflexive, self-typing case)
pattern: every field here exists in SCHEMA.md -- template derives, never invents
quality: null
title: "Output Template Output Template"
version: "1.0.0"
author: n03_builder
tags:
  - "output_template"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for output_template construction: the reflexive self-typing shape plus the broader recurring-document shape, side by side."
domain: "output template construction"
created: "2026-07-07"
updated: "2026-07-07"
8f: "F6_produce"
keywords:
  - "template with"
  - "output template construction"
  - "output template output template"
  - "output_template"
  - "builder"
  - "examples"
  - "## reflexive shape"
  - "## broader shape"
  - "{{slug}}"
density_score: 0.88
related:
  - bld_schema_output_template
  - bld_output_template_field_manifest
  - p10_lr_output_template_builder
  - bld_instruction_output_template
  - bld_output_template_prompt_template
---
# Output Template: output_template
This kind is REFLEXIVE: the shape below is itself an `output_template` instance,
demonstrating BOTH real usages side by side (see `bld_schema_output_template.md`
"Two Coexisting Usages"). Choose the block matching your intent -- do not merge them.

## Reflexive Shape (a NEW kind-builder's own ISO#9 -- `bld_output_{{kind}}.md`)
Frontmatter of the ISO#9 file being produced:
```yaml
id: bld_output_template_{{kind}}
kind: output_template
pillar: P05
llm_function: PRODUCE
purpose: "Template with {{vars}} that the LLM fills to produce a {{kind}} artifact"
pattern: "every field here exists in SCHEMA.md -- template derives, never invents"
quality: null
title: "Output Template {{Kind Title Case}}"
version: "1.0.0"
author: "{{who_produced}}"
domain: "{{kind}} construction"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
tags: [{{kind}}, builder, examples]
tldr: "{{dense_summary_max_160ch}}"
density_score: {{0.80_to_1.00}}
```
Body of the SAME ISO#9 file (a nested example of the TARGET kind's own future artifact,
rendered here as a plain block -- an inner fenced ```yaml block is what a real ISO file
contains, omitted here one level to avoid unrenderable nested triple-backticks):
```text
# Output Template: {{kind}}

  id: {{canonical_or_registered_id_pattern}}
  kind: {{kind}}
  pillar: {{target_pillar}}
  version: "1.0.0"
  created: "{{YYYY-MM-DD}}"
  updated: "{{YYYY-MM-DD}}"
  depends_on: [{{fixed_deps_per_kinds_meta}}]
  quality: null
  tags: [{{tag_1}}, {{tag_2}}]
  tldr: "{{one_line_summary}}"

## {{Section 1}}
{{content matching the target kind's own bld_schema Body Structure}}
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| {{ref}} | related | {{score}} |
```

## Broader Shape (a recurring output document -- README section, config template, report shell)
Frontmatter of the new instance:
```yaml
id: "{{one_of_3_documented_conventions -- disclosed, e.g. p05_out_{{slug}} or {{nucleus}}_output_{{slug}}}}"
kind: output_template
pillar: P05
title: "{{Human Title}} -- {{what it scaffolds}}"
version: 1.0.0
created: "{{YYYY-MM-DD}}"
author: "{{nucleus}}_{{domain}}"
domain: "{{domain}}"
quality: null
updated: "{{YYYY-MM-DD}}"
tags: [output, {{domain}}, {{format}}, {{nucleus}}]
tldr: "{{dense_summary_max_160ch}}"
depends_on: []
```
Body of the same instance:
```text
# {{Title}}

## Instructions (or "## Summary" for a completed-report-shaped instance)
1. {{step_1 -- e.g. run the upstream generator}}
2. {{step_2 -- e.g. validate with a real tool}}

## Template (fenced block matching the real target format -- yaml/markdown/text)
  # {{real_target_path_this_scaffolds, e.g. .cex/brand/brand_config.yaml}}
  {{SECTION_1}}:
    {{VAR_1}}: ""   # {{constraint_or_required_note}}
    {{VAR_2}}: ""   # {{constraint_or_required_note}}

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| {{ref}} | related | {{score}} |
```

## Choosing Between the Two Shapes
| Signal | Use Reflexive Shape | Use Broader Shape |
|--------|---------------------|--------------------|
| A brand-new kind-builder is being scaffolded (12 ISOs, 1:1 with pillars) | YES | no |
| A nucleus needs a reusable scaffold for a document it writes repeatedly | no | YES |
| The consumer is another kind-builder's own F6 PRODUCE step | YES | no |
| The consumer is a human/nucleus filling `{{var}}` markers into a real config/report | no | YES |
| id should follow the canonical `bld_output_template_{{kind}}` pattern | YES (this is the ONE sub-case where corpus and canonical already agree) | RARE (0/18 real instances do; disclose the convention chosen instead) |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_output_template]] | upstream | 0.42 |
| bld_output_template_field_manifest | sibling (reflexive-case example) | 0.36 |
| [[p10_lr_output_template_builder]] | downstream | 0.33 |
| [[bld_instruction_output_template]] | upstream | 0.30 |
| [[bld_output_template_prompt_template]] | sibling (contrast) | 0.28 |
