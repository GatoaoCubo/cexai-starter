---
id: p01_kc_design_system
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P06
title: "Design System -- Deep Knowledge for design_system"
version: 1.0.0
created: 2026-06-15
updated: 2026-06-15
author: n03_builder
domain: design_system
quality: null
tags: [design_system, P06, INJECT, kind-kc, tokens, leverage]
tldr: "Selectable brand visual language as concrete tokens + component recipes + usage rules + a CEXAI leverage declaration; a generator binds exactly one at F3 INJECT."
when_to_use: "Building, reviewing, or reasoning about design_system artifacts"
keywords: [design tokens, color, type scale, motion, component recipe, brand, leverage, inject]
feeds_kinds: [design_system]
density_score: 0.95
linked_artifacts:
  primary: p06_vs_design_system
  related: []
related:
  - design-system-builder
---

# Design System

## Spec
```yaml
kind: design_system
pillar: P06
llm_function: INJECT
max_bytes: 5120
naming: p06_ds_{{name}}.md
core: false
```

## What It Is
A `design_system` (P06) is one selectable brand visual language expressed as typed, concrete-valued tokens (color/type/space/motion/form) plus four component recipes plus usage rules plus a CEXAI leverage declaration. A design or frontend generator binds EXACTLY ONE instance at F3 INJECT and treats it as the sole palette/scale/motion source. It is an ACTIVE, composable asset -- not a passive token dump. NOT `brand_config` (a single global identity, not a selectable library of many); NOT `validation_schema` (defines the contract SHAPE, not concrete values); NOT `pattern` (P08 architecture semantics). The contract every instance satisfies is p06_vs_design_system.

## Token groups (all five mandatory)
| Group | Holds | Example slots |
|-------|-------|---------------|
| color | palette roles | canvas, panel, ink, edge, signal, signal_ink, affirm, alert |
| type | typography | face.{display,text,mono}, scale.ratio, scale.steps, weight, leading |
| space | spacing system | unit (base px), scale s0..s7 |
| motion | animation | dur.{instant,quick,calm}, ease.{...}, move.{enter,exit,shift} |
| form | shape + elevation | radius.{none,soft,full}, edge.width, shadow.{flat,raised,float} |

## Component recipes (token compositions, NOT CSS)
`surface`, `control`, `field`, `marker` -- each composed only from the token slots above; never raw CSS literals.

## CEXAI Leverage model (what makes it ACTIVE)
Founder constraint: each system carries "its own CEXAI leverage capabilities". Every instance declares a `leverage:` block:
| Field | Role |
|-------|------|
| feeds_kinds | kinds that consume it at F3 INJECT (landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck) |
| inject_hook | how a builder binds the tokens at F3 INJECT |
| brand_config_relation | how it realizes the global brand_config identity into bindable tokens |
| composes_with | variant_shotgun_taste_loop, user_model, gdp |
| binds_8f | F1_constrain + F3_inject |
This is the difference between a token file and an asset: the system declares its own wiring into the 8F pipeline and the kind graph.

## Key parameters
| Parameter | Type | Tradeoff |
|-----------|------|----------|
| density | enum comfortable\|compact | selects the active space.scale band |
| signal | single role | exactly one accent -- no competing primaries |
| reduce_motion | fallback | every move collapses to dur.instant |

## Patterns
| Pattern | Rule |
|---------|------|
| Token-only components | components reference slots, never raw CSS literals |
| Single signal | one accent hue per system; affirm/alert are status, not accent |
| Contrast floor | ink-on-canvas and signal_ink-on-signal >= 4.5:1 (WCAG AA) |
| Aesthetic coordinate | each system owns a distinct corner (temperature/density/form/mode/type-voice) |

## Anti-Patterns
| Anti-Pattern | Why it fails |
|-------------|-------------|
| Passive token dump | no leverage block -> not composable; just a palette |
| Two competing accents | breaks single-signal; visual hierarchy collapses |
| Spring under reduce-motion | accessibility breach; motion must collapse to instant |
| Copying a known system's name/values | clean-room breach; instances are original IP |
| quality set to a score | never self-score; peer review assigns |

## Integration Graph
```
[brand_config] --selects--> [design_system] --F3 INJECT--> [landing_page | interactive_demo | product_tour | ...]
[p06_vs_design_system] --GOVERNs--> [design_system]
[variant_shotgun_taste_loop] --breadth+converge--> [design_system library]
```

## Decision Tree
- IF you need a selectable, concrete-valued brand visual language THEN design_system
- IF you need the SHAPE/contract of such a system THEN validation_schema (p06_vs_design_system)
- IF you need a single global identity (one brand) THEN brand_config
- DEFAULT: design_system for any bindable token + component + usage asset

## Quality Criteria
- GOOD: five token groups complete, four recipes, four usage rules, leverage block present
- GREAT: distinct aesthetic coordinate, contrast verified, original clean-room name/values
- FAIL: missing leverage, >1 signal, contrast < 4.5:1, copied content, quality not null

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p06_vs_design_system | upstream | 0.55 |
| [[design-system-builder]] | downstream | 0.45 |
| p06_ds_ferro | example | 0.42 |
| p06_ds_sereno | example | 0.42 |
| p08_adr_design_system_kind | upstream | 0.38 |
