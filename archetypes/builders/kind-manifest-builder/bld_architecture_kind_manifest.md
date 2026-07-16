---
kind: architecture
id: bld_architecture_kind_manifest
pillar: P08
llm_function: CONSTRAIN
purpose: "Component map of kind_manifest -- inventory, dependencies, and architectural position"
quality: null
title: "Architecture Kind Manifest"
version: "1.0.0"
author: n03_builder
tags: [kind_manifest, builder, examples]
tldr: "Golden and anti-examples for kind_manifest construction: the per-kind identity document's component inventory, its R-310 dependency history, and its boundary against knowledge_card/output_template/nucleus_def."
domain: "kind_manifest construction"
created: "2026-07-10"
updated: "2026-07-10"
8f: "F1_constrain"
keywords: [component map of kind_manifest, and architectural position, kind_manifest construction, architecture kind manifest, kind_manifest, builder, examples, component inventory, dependency graph, boundary table]
density_score: 0.88
related:
  - bld_architecture_kind
  - bld_architecture_knowledge_card
---
## Component Inventory
| Name | Role | Owner | Status |
|------|------|-------|--------|
| purpose_paragraph | 1-paragraph statement of what the documented kind IS | author | required |
| pillar_line | `P0X -- {{pillar_name}}` for the documented kind | author | required |
| schema_table | Key-fields table for the documented kind's OWN schema | author | required |
| when_to_use | 2-4 bullets | author | required |
| builder_pointer | Real path to `archetypes/builders/{{kind}}-builder/`, OR an honest OPEN-status callout | author | required |
| id | `n00_{{kind}}_manifest` -- the ONE part of the frontmatter that varies systematically with the target kind | author | required (pattern-fixed) |
| filename | `kind_manifest_n00.md` -- INVARIANT across all 294 real instances | kinds_meta.json | required (immutable) |
| directory | `kind_{{kind}}/` -- the ONE path segment that varies | author | required |
| related_artifacts | Wikilinks with relationship + score, forming a closed mutual cross-reference web | author | required |
## Dependency Graph
```
kind-builder                  --scaffolds--> a NEW kind's 12-ISO builder package
kind_manifest                 --documents--> that SAME kind's identity (purpose/schema/pointer)
knowledge_card                --former_mistype_of--> kind_manifest (R-310, closed 2026-07-10)
output_template                --sibling_contrast--> kind_manifest
nucleus_def                     --sibling_contrast--> kind_manifest
kind_manifest.{294 instances}  --scaffolded_under--> N00_genesis/P0X_*/kind_{{kind}}/
```
| From | To | Type | Data |
|------|----|------|------|
| kind-builder | kind_manifest | co-scaffolds | Both fire when a NEW kind is registered: kind-builder scaffolds the 12-ISO package, kind_manifest documents the kind's identity |
| knowledge_card | kind_manifest | former_mistype_of | All 294 real instances carried `kind: knowledge_card` until R-310 (2026-07-10) re-typed them in one pass, ids/filenames untouched |
| output_template | kind_manifest | sibling_contrast | output_template is an F6 PRODUCE artifact shape (with `{{vars}}`); kind_manifest is an F3 INJECT reference document, no fill-in-the-blank body |
| nucleus_def | kind_manifest | sibling_contrast | nucleus_def documents a NUCLEUS (N00-N07); kind_manifest documents a registered KIND -- distinct subjects |
| kind_manifest (this kind) | 294 real instances | scaffolded_under | Every registered kind SHOULD have exactly one manifest; 294 currently do |
## Boundary Table
| kind_manifest IS | kind_manifest IS NOT |
|-----------------|---------------------|
| A per-KIND identity document: purpose, schema, builder pointer | A fact/topic card about the world (that is `knowledge_card`, this kind's own former mis-type) |
| An F3 INJECT reference an LLM loads before authoring a new instance of the documented kind | An F6 PRODUCE artifact shape with fill-in-the-blank `{{vars}}` (that is `output_template`) |
| Scoped to exactly ONE documented kind per instance | A document about a NUCLEUS (that is `nucleus_def`) |
| Fixed-filename (`kind_manifest_n00.md`), varying directory + id | A kind whose filename varies with content, like most of the 317-kind taxonomy |
| Governed by a CANONICAL id pattern 294/294 real instances already match | A kind with unresolved id-naming drift (unlike `output_template`'s 3-way drift) |
## Layer Map
| Layer | Components | Purpose |
|-------|------------|---------|
| Identity resolution | purpose_paragraph, pillar_line | State what the documented kind IS, in the taxonomy's own terms |
| Contract declaration | schema_table, builder_pointer | Mirror the documented kind's real fields and real (or honestly-absent) builder |
| Naming resolution | id, filename, directory (fixed-filename/varying-directory axis) | The ONE naming shape this kind uses -- never invent a 2nd |
| Consumers | Any nucleus about to author (F6) or reason about (F1-F4) an instance of the documented kind | Ground that work in the manifest's purpose + schema before producing |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_kind]] | sibling (reflexive-case source) | 0.39 |
| [[bld_architecture_knowledge_card]] | sibling (former mis-type contrast) | 0.36 |
