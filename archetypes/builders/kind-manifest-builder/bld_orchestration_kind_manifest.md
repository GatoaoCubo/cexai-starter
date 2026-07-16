---
kind: collaboration
id: bld_collaboration_kind_manifest
pillar: P12
llm_function: COLLABORATE
purpose: "How kind-manifest-builder works in crews with other builders"
pattern: "each builder must know its ROLE in a team, what it RECEIVES and PRODUCES"
quality: null
title: "Collaboration Kind Manifest"
version: "1.0.0"
author: n03_builder
tags: [kind_manifest, builder, collaboration, P12]
tldr: "kind-manifest-builder role in crews: per-kind identity documenter. Receives a newly-registered kind's kinds_meta.json entry. Produces its canonical manifest. Depends on nothing formally."
domain: "kind_manifest construction"
created: "2026-07-10"
updated: "2026-07-10"
8f: "F8_collaborate"
keywords: [kind_manifest construction, collaboration kind manifest, kind_manifest, builder, examples, "### crew: kind scaffolding stack", my role, crew compositions, per-kind identity document, r-310 lineage]
density_score: 0.87
---
# Collaboration: kind-manifest-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what does this kind mean, and where does its builder live?" I do not build artifacts OF the documented kind (that kind's own builder does). I do not scaffold the 12-ISO builder package itself (`kind-builder` does that). I do not write fact/topic cards about the world (`knowledge_card`, this kind's own former mis-type until R-310).
## Crew Compositions
### Crew: "Kind Scaffolding Stack" (a new kind's full registration)
```
  1. kind-builder            -> "scaffolds the NEW kind's 12-ISO builder package"
  2. kind-manifest-builder    -> "documents the SAME kind's identity (this builder)"
  3. the new kind's own builder -> "produces artifacts OF that kind going forward"
```
### Crew: "N00 Genesis Reference Stack" (adjacent to knowledge-card-builder's own crew)
```
  1. kind-manifest-builder     -> "per-kind identity document (purpose/schema/pointer)"
  2. knowledge-card-builder    -> "topic/fact card about the world (this kind's former mis-type)"
  3. output-template-builder   -> "F6 PRODUCE artifact shape with {{vars}}"
```
## Handoff Protocol
### I Receive
- seeds: the target kind's name + its full `.cex/kinds_meta.json` entry
  (boundary, pillar, naming, max_bytes, depends_on, llm_function, nucleus, core)
- optional: whether `archetypes/builders/{{kind}}-builder/` already exists
### I Produce
- kind_manifest artifact (.md + YAML frontmatter)
- committed to: `N00_genesis/P0X_{{pillar_domain}}/kind_{{kind}}/kind_manifest_n00.md`
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
| Builder | Why |
|---------|-----|
| kind-builder | The meta-builder that scaffolds a NEW kind's schema/pillar/naming, which my manifest's Schema table must mirror field-for-field |
| (none for depends_on) | `depends_on: []` per kinds_meta.json -- kind_manifest depends on nothing upstream by design |
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| Every one of the 317 kind-builders (informal) | Each MAY inject its own kind's manifest via F3 INJECT for orientation before F6 PRODUCE -- no formal `depends_on` registration exists (kinds_meta.json's `depends_on` list stays `[]` for kind_manifest itself) |
| N07 (orchestrator, informal) | Reads a target kind's manifest when routing an ambiguous dispatch, per `.claude/rules/n07-input-transmutation.md`'s taxonomy-mapping discipline |
