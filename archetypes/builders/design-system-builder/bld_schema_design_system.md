---
id: bld_schema_design_system
kind: schema
pillar: P06
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Schema: design_system"
domain: design_system
quality: null
tags: [design_system, builder, schema, tokens, P06]
tldr: "Single source of truth for a design_system: five token groups, four component recipes, four usage rules, a mandatory leverage block, and the instance frontmatter."
density_score: 0.92
related:
  - bld_model_design_system
  - bld_output_design_system
  - bld_eval_design_system
---

# Schema: design_system
Derivation hierarchy: **SCHEMA (this) > TEMPLATE (bld_output) > CONFIG (bld_config)**.
The defining contract is p06_vs_design_system; this ISO is its builder-facing restatement.

## Frontmatter Fields (required)
| Field | Type | Notes |
|-------|------|-------|
| id | string `p06_ds_{name}` | equals filename stem |
| kind | literal `design_system` | type integrity |
| pillar | literal `P06` | pillar assignment |
| title | string | "Name -- one-line stance" |
| version | semver | start 1.0.0 |
| aesthetic | string | one-line aesthetic stance |
| density | enum `comfortable\|compact` | selects active space band |
| leverage | block | feeds_kinds, inject_hook, brand_config_relation, composes_with, binds_8f |
| quality | null | never self-score |
| tags | list >=3 | includes `design-system` |

## Token groups (all five mandatory)
| Group | Required slots |
|-------|----------------|
| color | canvas, panel, ink, ink_soft, edge, signal, signal_ink, affirm, alert |
| type | face.{display,text,mono}, scale.ratio, scale.steps (t_1..t6), weight.{reg,med,bold}, leading.{tight,normal,loose} |
| space | unit (base px), scale s0..s7 (unit multipliers) |
| motion | dur.{instant,quick,calm}, ease.{linear,standard,emphatic}, move.{enter,exit,shift} |
| form | radius.{none,soft,full}, edge.width, shadow.{flat,raised,float} |

## Component recipes (four mandatory)
`surface`, `control`, `field`, `marker` -- token compositions only, never raw CSS literals.

## Usage rules (four mandatory)
1. Contrast floor: ink-on-canvas and signal_ink-on-signal >= 4.5:1 (WCAG AA).
2. Reduce-motion: every move collapses to dur.instant.
3. Single signal: exactly one accent role.
4. Density mode: declare comfortable|compact; it selects the active space band.

## Leverage block (mandatory)
`feeds_kinds` (>=1 registered kind) + `inject_hook` + `brand_config_relation` + `composes_with` + `binds_8f`. Missing -> FAIL: a passive token dump is not a design_system.

## Constraints
- max_bytes: 5120 (body); naming `p06_ds_{name}.md`; machine_format yaml.
- id == filename stem; quality: null always; clean-room (original values, no copied system).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p06_vs_design_system | upstream | 0.6 |
| [[bld_output_design_system]] | downstream | 0.5 |
| [[bld_eval_design_system]] | downstream | 0.48 |
| bld_model_design_system | sibling | 0.4 |
| [[kc_design_system]] | related | 0.4 |
