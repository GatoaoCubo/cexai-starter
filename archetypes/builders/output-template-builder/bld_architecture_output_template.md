---
kind: architecture
id: bld_architecture_output_template
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of output_template -- inventory, dependencies, and architectural position
quality: null
title: "Architecture Output Template"
version: "1.0.0"
author: n03_builder
tags: [output_template, builder, examples]
tldr: "Golden and anti-examples for output_template construction, demonstrating the reflexive-vs-broader usage split and the 3-way naming drift resolution."
domain: "output_template construction"
created: "2026-07-07"
updated: "2026-07-07"
8f: "F1_constrain"
keywords: [component map of output_template, and architectural position, output_template construction, architecture output template, output_template, builder, examples, component inventory, dependency graph, boundary table]
density_score: 0.88
related:
  - bld_architecture_kind
  - bld_architecture_prompt_template
  - output-template-builder
---
## Component Inventory
| Name | Role | Owner | Status |
|------|------|-------|--------|
| usage_declaration | Explicit statement: reflexive (ISO#9) or broader (recurring output document) | author | required |
| template_body | Fenced fill-in-the-blank block (reflexive/blank) OR narrative report body (broader/completed) | author | required |
| id | Frontmatter identifier -- canonical `bld_output_template_{{kind}}` for new reflexive work; one of 3 documented drift conventions, disclosed, for broader work | author | required |
| depends_on | Fixed EMPTY list per kinds_meta.json | kinds_meta.json | required (immutable) |
| pillar | Fixed `P05` per kinds_meta.json (1/18 real instances drifted to P12 -- not repeated) | kinds_meta.json | required |
| naming_convention_disclosure | Which of Convention A/B/C this instance's id follows (broader usage only) | author | recommended |
| related_artifacts | Wikilinks with relationship + score, all resolving to REAL artifacts | author | required |
## Dependency Graph
```
kind-builder                --reflexive_source--> output_template (ISO#9 self-typing, 317x)
prompt_template              --sibling_contrast--> output_template
response_format               --sibling_contrast--> output_template
formatter                      --sibling_contrast--> output_template
output_template.{reflexive}  --typed_by--> every kind-builder's own bld_output_{{kind}}.md
output_template.{broader}    --scaffolds--> a nucleus's recurring document (README section, brand_config.yaml, audit report)
```
| From | To | Type | Data |
|------|----|------|------|
| kind-builder | output_template | reflexive_source | The meta-builder-of-builders convention that makes every kind-builder's ISO#9 file a `kind: output_template` instance |
| prompt_template | output_template | sibling_contrast | output_template's own boundary text names prompt_template as "a template for an LLM-facing PROMPT, not the target artifact" |
| response_format | output_template | sibling_contrast | boundary text names response_format as "an abstract CONSTRAIN-time spec of a live response's structure" |
| formatter | output_template | sibling_contrast | boundary text names formatter as "a GOVERN-time runtime transform of already-produced content, not an authored content template" |
| output_template (reflexive) | every kind-builder's ISO#9 | typed_by | `bld_output_{{kind}}.md` carries `id: bld_output_template_{{kind}}` internally, confirmed across all 317 kind-builders |
| output_template (broader) | a nucleus's recurring document | scaffolds | e.g. `output_brand_config.md` scaffolds `.cex/brand/brand_config.yaml`; `output_readme_hero.md` scaffolds the README hero section |
## Boundary Table
| output_template IS | output_template IS NOT |
|-----------------|---------------------|
| The reflexive typing of a kind-builder's OWN F6 PRODUCE shape (ISO#9) | A template for an LLM-facing PROMPT (that is prompt_template) |
| A reusable scaffold for a recurring OUTPUT document (README section, config template, report shell) | An abstract CONSTRAIN-time spec of a live response's structure with no fill-in-the-blank body (that is response_format) |
| Sometimes a genuine BLANK template (`{{var}}` markers, empty defaults) | Always a blank template -- roughly half the real corpus (e.g. `output_orchestration_audit.md`) is a COMPLETED report, not blank |
| A kind with `depends_on: []` -- depends on nothing upstream | A kind that inherits validation from a sibling schema (no `depends_on` entries exist) |
| Governed by a CANONICAL id pattern (`bld_output_template_{{kind}}`) for NEW production | A kind whose 18 real instances already match that pattern (0/18 do -- 3 drift conventions instead) |
## Layer Map
| Layer | Components | Purpose |
|-------|------------|---------|
| Usage resolution | usage_declaration (reflexive vs broader) | Decide which of the two real shapes this instance takes BEFORE composing |
| Contract declaration | template_body, id, pillar | Define the frontmatter + body shape per SCHEMA.md |
| Naming resolution | Convention A/B/C disclosure (broader) OR canonical pattern (reflexive) | Resolve the 3-way drift honestly, never silently pick one |
| Consumers | The kind-builder itself (reflexive) OR the producing nucleus (broader, e.g. N06 filling `output_brand_config.md` into a real `brand_config.yaml`) | Wire the template to its real filler |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_output_template]] | upstream | 0.40 |
| bld_architecture_kind | sibling (reflexive-case source) | 0.39 |
| [[bld_architecture_prompt_template]] | sibling (contrast) | 0.36 |
| [[output-template-builder]] | upstream | 0.34 |
| [[bld_prompt_output_template]] | upstream | 0.32 |
