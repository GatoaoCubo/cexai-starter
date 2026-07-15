---
kind: collaboration
id: bld_collaboration_output_template
pillar: P12
llm_function: COLLABORATE
purpose: How output-template-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Output Template"
version: "1.0.0"
author: n03_builder
tags: [output_template, builder, examples]
tldr: "Golden and anti-examples for output_template construction, demonstrating the reflexive-vs-broader usage split and the 3-way naming drift resolution."
domain: "output_template construction"
created: "2026-07-07"
updated: "2026-07-07"
8f: "F8_collaborate"
keywords: [output_template construction, collaboration output template, output_template, builder, examples, "### crew: kind scaffolding stack", my role, crew compositions, reflexive iso9, broader recurring document]
density_score: 0.87
related:
  - bld_collaboration_kind
  - bld_collaboration_prompt_template
  - bld_collaboration_response_format
  - bld_collaboration_formatter
  - bld_collaboration_field_manifest
---
# Collaboration: output-template-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question, in one of two registers: "what does this
kind-builder's own F6 PRODUCE shape look like?" (reflexive) OR "what does this recurring
output document look like before it is filled in?" (broader). I do not write LLM-facing
prompts (prompt_template). I do not define abstract, unrendered response shapes
(response_format). I do not transform already-produced content post-hoc (formatter).
I do not fill my own templates with real content -- that is the consuming kind-builder's
or nucleus's own F6 PRODUCE step.
## Crew Compositions
### Crew: "Kind Scaffolding Stack" (reflexive usage)
```
  1. kind-builder -> "the meta-builder that scaffolds a NEW kind's 12 ISOs end to end"
  2. output-template-builder -> "produces ISO#9 (bld_output_{{kind}}.md), the F6 PRODUCE shape"
  3. schema-builder-equivalent (bld_schema_{{kind}}.md, authored alongside) -> "the schema ISO#9 derives from"
```
### Crew: "P05 Output Contract Stack" (adjacent to prompt-template-builder's own crew)
```
  1. output-template-builder -> "reusable scaffold for a produced ARTIFACT (this kind)"
  2. prompt-template-builder -> "reusable {{var}} template for an LLM-facing PROMPT"
  3. response-format-builder -> "abstract CONSTRAIN-time spec of a live response's structure"
  4. formatter-builder -> "GOVERN-time runtime transform of already-produced content"
```
## Handoff Protocol
### I Receive
- seeds: which usage (reflexive/broader), the target kind's own `bld_schema_{{kind}}.md`
  (reflexive) OR the recurring document's real shape from a sibling instance (broader)
- optional: which of the 3 naming-drift conventions to disclose (broader usage only)
### I Produce
- output_template artifact (.md + YAML frontmatter)
- committed to: `archetypes/builders/{{kind}}-builder/bld_output_{{kind}}.md` (reflexive)
  OR `N0X_{{nucleus}}/P05_output/output_{{slug}}.md` (broader)
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
| Builder | Why |
|---------|-----|
| kind-builder | The meta-builder that scaffolds a NEW kind's schema, which my reflexive-usage template must mirror field-for-field |
| (none for broader usage) | `depends_on: []` per kinds_meta.json -- output_template depends on nothing upstream by design |
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| Every one of the 317 kind-builders (reflexive) | Each carries its OWN `bld_output_{{kind}}.md`, an `output_template` instance this builder's schema/model/eval ISOs govern |
| N02/N03/N04/N05/N06/N07 (broader, informal) | Each nucleus authors its own recurring output documents under this kind; no formal `depends_on` registration exists (kinds_meta.json's `depends_on` list stays `[]` for output_template itself -- this is a DOWNSTREAM consumption pattern, not a formal dependency edge) |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_collaboration_kind | sibling (reflexive-case source) | 0.48 |
| [[bld_collaboration_prompt_template]] | sibling (contrast) | 0.44 |
| [[bld_collaboration_response_format]] | related (contrast) | 0.36 |
| [[bld_collaboration_formatter]] | related (contrast) | 0.32 |
| bld_collaboration_field_manifest | sibling | 0.30 |
