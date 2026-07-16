---
kind: knowledge_card
id: bld_knowledge_card_kind_manifest
pillar: P01
llm_function: INJECT
purpose: "Domain knowledge for kind_manifest production -- the R-310 re-typing, the 294-instance corpus, and the fixed-filename naming axis"
sources: "This repo's own N00_genesis/*/kind_{{kind}}/kind_manifest_n00.md corpus (294 real instances), .cex/kinds_meta.json's kind_manifest entry (R-310), archetypes/builders/kind-manifest-builder/bld_schema_kind_manifest.md"
quality: null
title: "Knowledge Card Kind Manifest"
version: "1.0.0"
author: n03_builder
tags: [kind_manifest, builder, examples]
tldr: "Golden and anti-examples for kind_manifest construction: the R-310 re-typing from knowledge_card, the 294-instance clean corpus, and the fixed-filename/varying-directory naming axis."
domain: "kind_manifest construction"
created: "2026-07-10"
updated: "2026-07-10"
8f: "F3_inject"
keywords: [r-310 re-typing, per-kind identity document, kind manifest construction, knowledge card kind manifest, kind_manifest, builder, examples, domain knowledge, fixed filename axis, related artifacts]
density_score: 0.88
related:
  - bld_instruction_kind_manifest
  - p10_lr_kind_manifest_builder
  - kind-manifest-builder
  - p11_qg_kind_manifest
  - bld_schema_kind_manifest
---
# Domain Knowledge: kind_manifest
## Executive Summary
`kind_manifest` is the per-KIND identity document: one manifest per registered kind in CEX's taxonomy, always at `N00_genesis/P0X_*/kind_{{kind}}/kind_manifest_n00.md`, carrying `id: n00_{{kind}}_manifest`. It is the "what is this kind, and where does its builder live" reference an LLM injects at F3 before authoring a new instance of that kind. Until register row R-310 (2026-07-10, the same day as this scaffold), all 294 real instances mis-typed themselves internally as `knowledge_card` -- a reflexive sub-population the earlier R-307 id-drift measurement flagged EXEMPT-BY-PRECEDENT pending an explicit register decision. The founder's DP4 approved registering `kind_manifest` as its own kind; R-310 re-typed all 294 `kind:` fields (ids, filenames, and the closed `related:` cross-reference web stayed BYTE-UNCHANGED -- load-bearing) and authored ONE ISO (`bld_schema_kind_manifest.md`). This builder completes the other 11.
## Spec Table
| Property | Value |
|----------|-------|
| Pillar | P01 (knowledge) |
| Naming | `kind_{{kind}}/kind_manifest_n00.md` -- directory + id vary, filename invariant |
| Id pattern | `^n00_[a-z][a-z0-9_]+_manifest$` -- 294/294 real instances match, ZERO exceptions |
| max_bytes | 8192 (whole file); real corpus 3,256-6,352B (p95 4,635B) |
| depends_on | `[]` (fixed empty -- a manifest may reference any kind, but declares no dependency edge) |
| core | false (per kinds_meta.json) |
| nucleus (kinds_meta.json, owning) | N03 -- distinct from `nucleus: n00` inside every real instance's OWN frontmatter |
| Reference instances | `n00_knowledge_card_manifest.md` (the R-310 poster child), `n00_output_template_manifest.md` (same resolution shape precedent, R-298/299), `n00_agent_manifest.md` |
## Patterns
| Source | Concept | Application |
|--------|---------|-------------|
| This repo's own R-298/R-299 (output_template) | Register the kind first, scaffold the 12-ISO builder as a disclosed follow-up | R-310 repeats the SAME two-step shape for kind_manifest: register today, build the family today as this hotfix |
| Software "manifest" files (package.json, Cargo.toml) | A fixed-shape declaration of identity for one unit | Every `kind_manifest_n00.md` plays the same role for one KIND in this taxonomy |
| Wikipedia-style "disambiguation page" | One term, several distinct senses, each pointed at its own real target | `kind_manifest` (this kind), a builder-package's informal "ISO 1", and independently-registered `*_manifest` kinds are 3 distinct senses of "manifest" here |
- **The R-310 re-typing was byte-scoped, not a rewrite**: only the `kind:` field flipped from `knowledge_card` to `kind_manifest` across 294 files -- ids, filenames, and the mutual `related:` cross-reference web were left untouched, because renaming any of those would have rewritten ~294 files' worth of inbound wikilinks at once (the exact trap a prior register row, R-289, named and avoided for a different corpus).
- **This corpus has NO id-naming drift** -- unlike `output_template` (3 conventions, 0/18 matching canonical) or `field_manifest`, `kind_manifest`'s 294/294 real instances already match `^n00_[a-z][a-z0-9_]+_manifest$` exactly. The only thing that was ever wrong was the `kind:` field, never the `id:`.
- **No dedicated code generator exists** -- a repo-wide search of `_tools/*.py`/`*.sh`/`*.ps1` found only 3 hits referencing the path, none of them writers: `cex_kind_index_gen.py` (mentions the path in generated prose), `cex_naming_validator.py` (classifies/skips the filename), `cex_stats.py` (counts the parent directories). Every real instance was hand-authored, pattern-first -- the same admission R-298 made for `output_template`.
## Anti-Patterns
| Anti-Pattern | Why it fails |
|-------------|-------------|
| Renaming the fixed `kind_manifest_n00.md` filename, or moving the `kind_{{kind}}/` directory | Breaks `cex_naming_validator.py`'s explicit skip-list and `cex_stats.py`'s per-pillar directory count in one move |
| Treating "294" as a permanent constant | A newly-registered kind changes the count the moment its manifest is authored -- always re-verify, never cite a stale number as current |
| Fabricating a builder pointer when none exists | The honest "Builder -- honest status (register row R-XXX, OPEN)" callout is correct -- exactly what this kind's own manifest ecosystem already models (`n00_output_template_manifest.md` did this for `output_template` until R-299 closed it) |
| Confusing this kind with `knowledge_card` | `knowledge_card` is a topic/fact card about the WORLD; `kind_manifest` documents a registered KIND in this taxonomy -- distinct subjects, and this kind's own former mis-type |
| Confusing this kind with `output_template` | `output_template` is a kind-builder's F6 PRODUCE artifact shape (with `{{vars}}`); `kind_manifest` is an F3 INJECT reference document, no fill-in-the-blank body |
## Application
1. Identify the target kind needing documentation; read its `kinds_meta.json` entry in full
2. Check for an existing builder at `archetypes/builders/{{kind}}-builder/`; if absent, plan the honest OPEN callout
3. Mirror the 10-section body structure from SCHEMA.md exactly -- do not invent a new shape
4. Verify any corpus statistic (instance count, id-match rate) against a fresh read, not a prior investigation's citation
5. Keep `depends_on: []`, `nucleus: n00`, `8f: F3_inject`, `quality: null`
## References
- This repo: `archetypes/builders/kind-manifest-builder/bld_schema_kind_manifest.md` (R-310, the schema this knowledge card supports)
- This repo: `n00_knowledge_card_manifest.md`, `n00_output_template_manifest.md`, `n00_agent_manifest.md` (3 real instances read in full for this scaffold)
- This repo: `.cex/kind_tool_supplement.json`'s `kind_manifest` bucket (5 tools: cex_retriever.py, cex_memory_select.py, cex_query.py, cex_fts5_search.py, cex_compile.py)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_kind_manifest]] | downstream | 0.48 |
| [[p10_lr_kind_manifest_builder]] | downstream | 0.42 |
| [[kind-manifest-builder]] | downstream | 0.40 |
| [[p11_qg_kind_manifest]] | downstream | 0.36 |
| [[bld_schema_kind_manifest]] | downstream | 0.34 |
