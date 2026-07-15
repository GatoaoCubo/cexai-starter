---
kind: knowledge_card
id: bld_knowledge_card_output_template
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for output_template production -- the reflexive-vs-broader usage split and the 3-way naming drift
sources: Jinja2/Handlebars/Mustache templating engines, the GoF Template Method pattern, cookiecutter/Yeoman scaffold generators, this repo's own N00_genesis/P05_output/kind_output_template/kind_manifest_n00.md (R-298)
quality: null
title: "Knowledge Card Output Template"
version: "1.0.0"
author: n03_builder
tags: [output_template, builder, examples]
tldr: "Golden and anti-examples for output_template construction, demonstrating the reflexive-vs-broader usage split and the 3-way naming drift, resolved not blessed."
domain: "output_template construction"
created: "2026-07-07"
updated: "2026-07-07"
8f: "F3_inject"
keywords: [reflexive iso9, recurring output document, output template construction, knowledge card output template, output_template, builder, examples, domain knowledge, naming discrepancy, related artifacts]
density_score: 0.88
related:
  - bld_instruction_output_template
  - p10_lr_output_template_builder
  - output-template-builder
  - p11_qg_output_template
  - bld_schema_output_template
---
# Domain Knowledge: output_template
## Executive Summary
`output_template` is a fill-in-the-blank scaffold for an OUTPUT artifact -- the same idea
as a Jinja2/Handlebars/Mustache template (a document with named holes), the GoF Template
Method pattern (fix the skeleton, let the filler vary the steps), and the instinct behind
scaffold generators like cookiecutter or Yeoman. In this repo it carries a rare, DOUBLE
identity: (1) the reflexive typing of every kind-builder's own F6 PRODUCE shape
(`bld_output_{{kind}}.md`, ISO #9 of the 12-file set -- the narrowest, originally-intended
sense per `.cex/kinds_meta.json`), and (2) a reusable scaffold for a recurring OUTPUT
DOCUMENT a nucleus produces repeatedly (README sections, `brand_config.yaml`,
monetization/audit report shells -- the ACTUAL majority usage, 18/18 real instances).
Differs from `prompt_template` (an LLM-facing PROMPT, not the target artifact),
`response_format` (an abstract CONSTRAIN-time spec, no fill-in-the-blank body), and
`formatter` (a GOVERN-time runtime transform of already-produced content).
## Spec Table
| Property | Value |
|----------|-------|
| Pillar | P05 (output) |
| Naming (kinds_meta.json, reflexive-case-derived) | `bld_output_template_{{kind}}.md` |
| Naming (real corpus, broader usage) | `output_{{slug}}.md` (0/18 match id to filename stem) |
| max_bytes | 8192 |
| depends_on | [] (fixed empty -- output_template depends on nothing upstream) |
| core | true (per kinds_meta.json -- the single most-produced builder-less kind found in the R-298 sweep) |
| nucleus (kinds_meta.json) | N03 -- yet real instances are produced by N02/N03/N04/N05/N06/N07 alike; every nucleus authors its own recurring output documents |
| Reference instances | `N06_commercial/P05_output/output_brand_config.md` (genuine blank template, 41 vars, 7 sections), `N07_admin/P05_output/output_orchestration_audit.md` (completed report, not blank) |
## Patterns
- **Reflexive ISO#9 self-typing**: every kind-builder's own `bld_output_{{kind}}.md` file
  declares `kind: output_template` and `id: bld_output_template_{{kind}}` internally --
  confirmed across the 9 most-recently-scaffolded builders. A closed, self-consistent
  loop: the meta-kind typing "what does a produced artifact look like" is itself typed
  the SAME way for every one of the 317 kind-builders.
| Source | Concept | Application |
|--------|---------|-------------|
| Jinja2 / Handlebars / Mustache | `{{var}}` fill-markers in a static document skeleton | The universal placeholder syntax this repo's output_template instances use |
| GoF Template Method | Fix the algorithm's skeleton; subclasses fill specific steps | The reflexive ISO#9 case: the 12-ISO builder skeleton is fixed, each kind fills its own PRODUCE shape |
| cookiecutter / Yeoman | A project scaffold generator with named blanks | The broader recurring-document usage: `output_brand_config.md` scaffolds `brand_config.yaml` the same way a cookiecutter template scaffolds a repo |
| Django ModelForm-adjacent "shell" docs | A pre-structured document awaiting real content | `output_readme_hero.md`, `output_monetization_curriculum.md` -- structural shells for a recurring writing task |
- **The dual-usage split is empirically real, not a design choice this builder invents**:
  reading `output_brand_config.md` (blank, `{{VAR}}`-free but every value is an empty
  string/placeholder default) against `output_orchestration_audit.md` (a completed,
  fully-narrated post-mortem with real dates and real gap numbers) shows the SAME kind
  covering both "here is the shape to fill" and "here is what we produced" -- the R-298
  manifest's own "When to use" section names both explicitly.
- **3-way id-naming drift, resolved not blessed**: Convention A `p05_out_{name}` (1/18),
  Convention B `{nucleus}_output_{name}` (13/18), Convention C `{nucleus}_{name}` with NO
  "output" marker (4/18, all `*_readme_*`). `kinds_meta.json`'s registered naming
  (`bld_output_template_{{kind}}.md`) matches NONE of the 3 -- it describes only the
  reflexive ISO#9 case. This builder adopts the kinds_meta pattern as CANONICAL for new
  work while documenting all 3 drift conventions explicitly (see `bld_schema_output_template.md`).
- **Filename vs id mismatch is 100% (18/18)**: every real instance's on-disk filename is
  `output_{{slug}}.md` with NO nucleus/pillar prefix, while every id ADDS one -- unlike
  `field_manifest`/`approval_request`, which both enforce id == filename stem.
## Anti-Patterns
| Anti-Pattern | Why it fails |
|-------------|-------------|
| Picking one of the 3 drift conventions and presenting it as "the" standard | Silently blesses drift instead of resolving it -- exactly what register row R-299 flags as unacceptable |
| Retroactively renaming the 18 real instances to match the canonical pattern | Out of scope for a builder scaffold; a rename sweep is a separate, deliberate register row (mirrors `reverse_prompt`'s "do not fix the tree_sha filenames" precedent) |
| Treating every output_template as a blank fill-in-the-blank scaffold | `output_orchestration_audit.md` and `output_cf_actions_and_distribution.md` are completed REPORTS, not blank templates -- assuming otherwise misreads the corpus |
| Adding a `depends_on` entry | Fixed empty per kinds_meta.json; output_template depends on nothing upstream by design |
| Confusing this kind with `prompt_template` (LLM-facing prompt) | output_template targets the ARTIFACT a nucleus produces, not a prompt fed to an LLM |
| Confusing this kind with `formatter` | formatter is a GOVERN-time runtime transform of ALREADY-produced content; output_template is authored BEFORE content exists |
## Application
1. Identify scope: reflexive (new kind-builder's ISO#9) or broader (recurring nucleus output document)?
2. For reflexive: read the target kind's `bld_schema_{{kind}}.md` and mirror every field into the template
3. For broader: find a sibling instance in the same nucleus/domain if one exists; do not invent structure from zero
4. State explicitly whether this instance is a blank scaffold or a completed-output report
5. Choose an id: canonical pattern for reflexive; disclose the convention choice (A/B/C) for broader usage
6. Keep `depends_on: []`, `pillar: P05`, `quality: null`
## References
- Jinja2 / Handlebars / Mustache: `{{ }}` variable + logic-less templating
- Gang of Four: Template Method pattern (Design Patterns, 1994)
- cookiecutter / Yeoman: project-template scaffolding
- This repo: `kind_manifest_n00.md` (R-298, the naming-drift investigation this builder resolves)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_prompt_output_template]] | downstream | 0.48 |
| [[p10_lr_output_template_builder]] | downstream | 0.42 |
| [[output-template-builder]] | downstream | 0.40 |
| [[p11_qg_output_template]] | downstream | 0.36 |
| [[bld_schema_output_template]] | downstream | 0.34 |
