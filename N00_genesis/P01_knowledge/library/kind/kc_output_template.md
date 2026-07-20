---
id: kc_output_template
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P01
title: "Output Template -- Deep Knowledge for output_template"
version: 1.0.0
created: 2026-07-20
updated: 2026-07-20
author: n03_builder
domain: output_template
quality: null
tags: [output_template, P05, PRODUCE, kind-kc, scaffold, reflexive-iso, fill-in-the-blank]
tldr: "Fill-in-the-blank scaffold with a double identity: the reflexive ISO#9 of every kind-builder's own F6 PRODUCE shape, and a reusable template for a recurring output document a nucleus produces repeatedly."
when_to_use: "When scaffolding a new kind-builder's own ISO#9 (bld_output_{{kind}}.md), or when authoring a reusable template for a document (README section, config shell, report shell) a nucleus produces repeatedly."
keywords: [output template, reflexive iso9, recurring output document, fill-in-the-blank, scaffold, naming drift, template method]
density_score: null
related:
  - output-template-builder
  - bld_schema_output_template
  - p01_kc_prompt_template
  - p01_kc_response_format
  - p01_kc_formatter
---

# Output Template

## Definition
An `output_template` is a fill-in-the-blank scaffold for an OUTPUT artifact -- the same idea as a Jinja2/Handlebars/Mustache template or the GoF Template Method pattern. Registered `pillar: P05`, owning `nucleus: N03`, `llm_function: PRODUCE`, `primary_8f: F6_produce`, `core: true`, `depends_on: []` (`.cex/kinds_meta.json`). It carries a rare DOUBLE identity: (1) the reflexive typing of every kind-builder's own F6 PRODUCE shape (`bld_output_{{kind}}.md`, ISO #9 of the 12-file builder set -- the narrowest, originally-registered sense), and (2) a reusable scaffold for a recurring OUTPUT DOCUMENT a nucleus produces repeatedly (README sections, `brand_config.yaml`, monetization/audit report shells) -- empirically the ACTUAL majority usage in the real canonical-pillar corpus (18/18 instances read, zero reflexive-case).

## Boundaries
**What it is:** a document with named `{{var}}` holes (or, for report-shaped instances, a completed example of what filling those holes produces).

**What it is NOT:**
- NOT `prompt_template` (P03) -- an LLM-facing PROMPT, not the target artifact a nucleus produces.
- NOT `response_format` (P05) -- an abstract CONSTRAIN-time spec of how a live agent response is structured, with no fill-in-the-blank body.
- NOT `formatter` (P05) -- a GOVERN-time runtime transform of ALREADY-produced content; `output_template` is authored BEFORE content exists.

## Naming Convention
| Property | Value |
|---|---|
| Naming (kinds_meta.json, reflexive-derived) | `bld_output_template_{{kind}}.md` |
| ID regex (bld_schema, CANONICAL forward-only) | `^bld_output_template_[a-z][a-z0-9_]+$` |
| Naming (real corpus, broader usage, NOT gate-enforced) | `output_{{slug}}.md` -- 0/18 real instances match id to filename stem |
| max_bytes | 8192 (body) |
| depends_on | `[]` -- fixed empty by design |

**Naming drift, resolved not blessed:** the 18 real canonical-pillar instances split across three id conventions, none matching the canonical pattern -- `p05_out_{name}` (1/18), `{nucleus}_output_{name}` (13/18), `{nucleus}_{name}` with no "output" marker (4/18, all `*_readme_*`). New work should follow the kinds_meta-registered pattern; the drift is disclosed, not retroactively renamed (a separate reconciliation sweep would be required).

## Key Fields
| Field | Type | Required | Notes |
|---|---|---|---|
| kind | literal `output_template` | YES | -- |
| pillar | literal `P05` | YES | 1/18 real instances drift to `P12`; do not repeat |
| primary_8f / 8f | literal `F6_produce` | YES | -- |
| tags | list, len >= 3 | YES | must include an output/template-identifying term |
| depends_on | `[]` | N/A | fixed empty |

## When to Use
- Reflexive: scaffolding ISO#9 for a brand-new kind-builder being built -- the template-with-`{{vars}}` shape that kind's own artifacts must fill.
- Broader: authoring a recurring output document (README section, `brand_config.yaml`-style config, an audit/report shell) for any nucleus.
- State explicitly, at the top of any new instance, WHICH usage is intended -- a blank scaffold and a completed report are structurally different and have different consumers.

## Related Kinds
- [[p01_kc_prompt_template]] -- the LLM-facing sibling this kind is most often confused with; targets a PROMPT, not the produced artifact.
- [[p01_kc_response_format]] -- an abstract response-shape spec with no fill-in-the-blank body.
- [[p01_kc_formatter]] -- a post-hoc runtime transform of content that already exists.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[output-template-builder]] | downstream (builder identity) | 0.55 |
| [[bld_schema_output_template]] | downstream (schema, source of truth) | 0.52 |
| [[p01_kc_prompt_template]] | sibling (contrast) | 0.38 |
| [[p01_kc_response_format]] | sibling (contrast) | 0.35 |
| [[p01_kc_formatter]] | sibling (contrast) | 0.33 |
