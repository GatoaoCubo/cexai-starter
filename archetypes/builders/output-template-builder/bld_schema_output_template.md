---
kind: schema
id: bld_schema_output_template
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for output_template
pattern: TEMPLATE (bld_output) derives from this. CONFIG (bld_config) restricts this.
quality: null
title: "Schema Output Template"
version: "1.0.0"
author: n03_builder
tags:
  - "output_template"
  - "builder"
  - "schema"
  - "P05"
tldr: "Field-level source of truth for output_template: the reflexive ISO#9 usage vs the broader 18-instance recurring-output-document usage, and the 3-way id naming drift resolved (not silently blessed) via kinds_meta's registered pattern."
domain: "output_template construction"
created: "2026-07-07"
updated: "2026-07-07"
8f: "F1_constrain"
keywords:
  - "output_template construction"
  - "schema output template"
  - "bld_output_template_[a-z][a-z0-9_]+"
  - "id pattern"
  - "naming discrepancy"
  - "output_template"
  - "builder"
  - "schema"
  - "reflexive iso"
  - "18 real instances"
density_score: 0.90
related:
  - bld_model_output_template
  - bld_schema_prompt_template
  - bld_schema_kind
---

# Schema: output_template
## Two Coexisting Usages (read before authoring anything)
1. **Reflexive (ISO#9)** -- the kind-builder's own F6 PRODUCE template, one per kind
   (`bld_output_{{kind}}.md`, ISO #9 of every 12-file builder set). All 317 kind-builders'
   own ISO#9 file declares `kind: output_template` internally -- the ORIGINAL, narrowest
   sense per `.cex/kinds_meta.json`'s `boundary` field.
2. **Broader (recurring output document)** -- a reusable, fill-in-the-blank template for
   an OUTPUT document a nucleus produces repeatedly (README sections, `brand_config.yaml`,
   monetization/audit report shells). This is the corpus's ACTUAL majority usage: 18/18
   real canonical-pillar instances are this kind, zero are the reflexive case (ISO#9 files
   live under `archetypes/builders/*/`, outside the corpus the R-298 manifest counted).
Both usages are real; this schema governs both.
## Frontmatter Fields
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string | YES | -- | See ID Pattern -- CANONICAL differs from ALL 18 observed real instances (drift documented, not retroactively enforced) |
| kind | literal "output_template" | YES | -- | Type integrity |
| pillar | literal "P05" | YES | -- | Per kinds_meta.json; 1/18 real instances (`n07_output_orchestration_audit`) drifts to `pillar: P12` (matches its DOMAIN) -- noted, not enforced |
| version | semver string | YES | "1.0.0" | Artifact versioning |
| created / updated | date YYYY-MM-DD | YES | -- | Creation / last-update date |
| author | string | YES | -- | Real corpus uses `n0X_marketing`/`n0X_commercial`-style nucleus tags |
| title | string | YES | -- | Human-readable name |
| domain | string | REC | -- | Free-text domain tag (e.g. `content_factory`, `brand-config`) |
| primary_8f / 8f | literal | YES | "F6_produce" | Both real instances read carry this |
| quality | float\|null | YES | null | Peer-review score (never self-scored) |
| tags | list[string], len >= 3 | YES | -- | Must include an output/template-identifying term |
| tldr | string <= 160ch | REC | -- | Dense one-line summary |
| when_to_use | string | OPT | -- | Present in 2/2 N02 instances read in full; recommended |
| depends_on | list[string] | N/A | [] | Fixed EMPTY per kinds_meta.json |
## ID Pattern
Regex: `^bld_output_template_[a-z][a-z0-9_]+$`
Rule: CANONICAL -- derived directly from `.cex/kinds_meta.json`'s REGISTERED `naming`
field (`bld_output_template_{{kind}}.md`), per the explicit resolution mandate (register
row R-299). NOT a description of the real corpus (see Naming Discrepancy below). New
output_template artifacts authored BY THIS BUILDER should follow it; the gate is
FORWARD-ONLY -- it governs new production and does not retroactively invalidate the 18
pre-existing hand-authored instances (R-298's own admission: "instances of this kind are
authored directly against the schema... not from a builder ISO that does not yet exist").
## Naming Discrepancy (3 conventions, resolved not blessed)
`kinds_meta.json`'s registered naming exactly matches the reflexive ISO#9 case: every one
of the 317 kind-builders' own `bld_output_{{kind}}.md` carries `id: bld_output_template_
{{kind}}` internally (e.g. `bld_output_template_field_manifest` -- confirmed by direct
read). The 18 real canonical-pillar instances (BROADER usage) instead split across THREE
conventions, and ZERO match the canonical pattern:
| Convention | Count | Example | Real file |
|---|---|---|---|
| A: `p05_out_{name}` (pillar-prefixed) | 1/18 | `p05_out_cf_actions_and_distribution` | `N02_marketing/P05_output/output_cf_actions_and_distribution.md` |
| B: `{nucleus}_output_{name}` | 13/18 | `n06_output_brand_config` | `N06_commercial/P05_output/output_brand_config.md` |
| C: `{nucleus}_{name}` (NO "output" marker) | 4/18 | `n02_readme_hero` | `N02_marketing/P05_output/output_readme_hero.md` |
Convention C is an ADDITIONAL finding beyond the two the R-298 manifest names explicitly
(`kind_manifest_n00.md` documents A and B only; this schema adds C from a direct
full-corpus read -- all 4 are `*_readme_*`-titled: `n02_readme_hero`, `n03_readme_
technical`, `n04_readme_curriculum`, `n05_readme_install`). None of the 3 is retroactively
"fixed" here -- out of scope; a rename/reconciliation sweep is a separate register row,
mirroring `reverse_prompt`'s own precedent (`bld_schema_reverse_prompt.md`: "Do NOT 'fix'
the tree_sha filenames... that IS the cache/determinism key").
## Filename vs id (a 4th, orthogonal drift axis)
Unlike `field_manifest`/`approval_request` (which enforce "id MUST equal filename stem"),
output_template does NOT: **0/18** real instances satisfy it. All 18 filenames are
uniformly `output_{{slug}}.md` (no nucleus/pillar prefix), while every id ADDS a prefix
(Convention A/B) or reorders tokens (Convention C: `output_readme_hero.md` ->
`n02_readme_hero`, not `n02_output_readme_hero`). A 100%-consistent FILENAME convention
paired with a 3-way-inconsistent ID convention. `id == filename stem` is therefore NOT a
hard constraint here (it would fail 18/18 times, not a meaningful signal) -- a deliberate,
evidence-based deviation from the field_manifest/approval_request precedent.
## Body Structure (required sections)
1. `## Summary` or `## Instructions` -- what this template produces and how to fill it (both real instances read use one or the other, not both)
2. `## Template` (fenced code block, yaml/markdown/text) -- the actual fill-in-the-blank shape, OR a "How to use" ROLE/ACT block for the reflexive/report-shaped instances
3. Domain-specific body (varies -- a Component table, an Executive Summary, a Flow diagram; the 18 real instances are NOT structurally uniform beyond frontmatter + a template/summary block)
4. `## Related Artifacts` -- wikilinks with relationship + score
## Constraints
- max_bytes: 8192 (body only) -- per `kinds_meta.json`
- naming (kinds_meta.json, reflexive-derived): `bld_output_template_{{kind}}.md`
- naming (real corpus, broader usage, NOT gate-enforced): `output_{{slug}}.md`
- machine_format: markdown authored; compiled via `cex_compile.py`
- depends_on: [] (fixed EMPTY -- no kinds_meta.json edit, out of scope for a builder)
- core: true (the most-produced kind in the R-298 investigation's set)
- quality: null always; pillar P05 always in NEW output (1/18 real drifted to P12)
- NOT `prompt_template` (P03, template for an LLM-facing PROMPT, not the target artifact)
- NOT `response_format` (P05, abstract CONSTRAIN-time spec of a response's structure)
- NOT `formatter` (P05, GOVERN-time runtime transform of already-produced content)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_model_output_template | sibling | 0.44 |
| n00_output_template_manifest | upstream | 0.42 |
| bld_schema_prompt_template | sibling (contrast) | 0.34 |
| bld_schema_kind | related (reflexive-case source) | 0.30 |
