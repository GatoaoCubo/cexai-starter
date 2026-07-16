---
kind: instruction
id: bld_instruction_kind_manifest
pillar: P03
llm_function: REASON
purpose: "Step-by-step production process for kind_manifest"
pattern: "3-phase pipeline (research -> compose -> validate)"
quality: null
title: "Instruction Kind Manifest"
version: "1.0.0"
author: n03_builder
tags:
  - "kind_manifest"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for kind_manifest construction: identify the target kind, mirror its kinds_meta.json entry into the 10-section body, and never fabricate a builder pointer."
domain: "kind_manifest construction"
created: "2026-07-10"
updated: "2026-07-10"
8f: "F4_reason"
keywords:
  - "kind_manifest construction"
  - "instruction kind manifest"
  - "per-kind identity document"
  - "n00_[a-z][a-z0-9_]+_manifest"
  - "kind_manifest"
  - "builder"
  - "examples"
  - "naming discrepancy"
  - "related artifacts"
density_score: 0.88
related:
  - bld_schema_kind_manifest
---
# Instructions: How to Produce a kind_manifest
## Phase 1: RESEARCH
1. Identify the TARGET kind this instance will document -- read its entry in `.cex/kinds_meta.json` (`boundary`, `pillar`, `naming`, `max_bytes`, `depends_on`, `llm_function`, `nucleus`, `core`) in full before writing anything
2. Check whether `archetypes/builders/{{kind}}-builder/` already exists -- if yes, cite its real path; if no, plan an honest "Builder -- honest status (register row R-XXX, OPEN)" callout instead of inventing a path
3. Search for a sibling `kind_manifest_n00.md` in an adjacent pillar directory (Grep `kind: kind_manifest` under `N00_genesis/P0X_*/`) to confirm the current body-structure convention has not drifted since SCHEMA.md was last read
4. Confirm the target kind is not already documented (Glob `N00_genesis/P0X_*/kind_{{kind}}/kind_manifest_n00.md`) -- avoid duplicating an existing manifest
5. Verify any corpus-wide statistic (e.g. "294 real instances") against a fresh count rather than citing a prior investigation's number -- a newly-registered kind changes the count immediately
6. Confirm `depends_on` stays `[]` -- fixed empty per kinds_meta.json, never add a dependency
## Phase 2: COMPOSE
1. Read SCHEMA.md (`bld_schema_kind_manifest.md`) -- source of truth for the id pattern, the fixed-filename/varying-directory naming axis, and the 10 required body sections
2. Read OUTPUT_TEMPLATE.md (`bld_output_kind_manifest.md`) -- fill the shape following SCHEMA constraints exactly
3. Fill frontmatter: `id: n00_{{kind}}_manifest`, `kind: kind_manifest`, `8f: F3_inject`, `pillar` (the DOCUMENTED kind's own pillar), `nucleus: n00`, `title: "{{Kind Title}} -- Canonical Manifest"`, `version: 1.0`, `quality: null`, `tags`, `density_score: 1.0`, `related` (non-empty)
4. Write the body in the fixed 10-section order: `<!-- 8F: ... -->` trace comment, Purpose, Pillar, Schema (key fields), When to use, Builder, Template variables (optional), Example (minimal), Related kinds, Related Artifacts
5. Write the Builder section honestly: a real `archetypes/builders/{{kind}}-builder/` path + `cex_8f_runner.py` invocation example, OR the OPEN-status callout naming the real register row if no builder exists
6. Write the Related Artifacts section: at least 3 wikilinks resolving to REAL existing artifacts (siblings in this pillar, the kind-builder family, or another kind_manifest instance)
7. Verify the whole file is within 8192 bytes (per `kinds_meta.json` `max_bytes`)
## Phase 3: VALIDATE
1. Check QUALITY_GATES.md (`bld_eval_kind_manifest.md`) -- apply each gate manually
2. HARD gates (all must pass):
   - YAML frontmatter parses without errors
   - `kind` == `kind_manifest`, `8f` == `F3_inject`, `nucleus` == `n00`
   - `id` matches `^n00_[a-z][a-z0-9_]+_manifest$`
   - `depends_on` stays `[]` (never add without a kinds_meta.json edit -- out of scope)
   - `quality` == `null`
   - filename == `kind_manifest_n00.md` (never renamed) and directory == `kind_{{kind}}/`
3. SOFT gates (score each against QUALITY_GATES.md):
   - all 10 body sections present, in order, none merged or skipped
   - the Builder section states a REAL path or an honest OPEN callout -- never a fabricated path
   - the Schema table reflects the DOCUMENTED kind's own real fields, not kind_manifest's own fields
   - at least one Related Artifacts wikilink resolves to a REAL existing artifact
4. Cross-check scope boundaries:
   - is this truly `kind_manifest`, not a `knowledge_card` (the R-310 former mis-type)?
   - not an `output_template` (a different F6 PRODUCE artifact shape)?
   - not a `nucleus_def` (documents a NUCLEUS, not a kind)?
5. If score < 8.0: revise in the same pass before outputting

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_kind_manifest]] | downstream | 0.38 |
