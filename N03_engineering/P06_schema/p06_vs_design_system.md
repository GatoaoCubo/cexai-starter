---
id: p06_vs_design_system
kind: validation_schema
pillar: P06
nucleus: N03
title: "Design-System Contract -- the shape every CEXAI design_system must satisfy"
version: 1.1.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
quality: null
status: active
validates_kind: design_system
leverage_required: true
tags: [design-system, tokens, contract, schema, brand, leverage]
tldr: "Original CEXAI contract for a selectable brand design system: five required token groups (color/type/space/motion/form), four component recipes, four usage rules, a mandatory CEXAI leverage declaration, and the instance frontmatter. The generator binds to this; instances supply concrete values."
density_score: 0.9
related:
  - p06_ds_ferro
  - p06_ds_sereno
---

# Design-System Contract

A `design_system` is one selectable brand visual language, expressed as typed tokens
plus component recipes plus usage rules -- the contract a design or frontend generator
binds to under F1 CONSTRAIN. This schema is the GOVERN gate: an instance is valid only
if it supplies every required group below, in the declared shape. Concrete values live
in the instance, never here.

## Required token groups (all five mandatory)

| Group | Required slots | Value format |
|-------|----------------|--------------|
| `color` | `canvas` `panel` `ink` `ink_soft` `edge` `signal` `signal_ink` `affirm` `alert` | `#RRGGBB` or `#RRGGBBAA` |
| `type` | `face.display` `face.text` `face.mono`; `scale.ratio`; `scale.steps` (t_1..t6 -> rem); `weight.{reg,med,bold}`; `leading.{tight,normal,loose}` | font stack string; ratio float; rem; int; unitless |
| `space` | `unit` (base px); `scale` (s0..s7 as unit multipliers) | int px; float multipliers |
| `motion` | `dur.{instant,quick,calm}` (ms); `ease.{linear,standard,emphatic}` (cubic-bezier); `move.{enter,exit,shift}` (dur+ease recipe) | int ms; `cubic-bezier(a,b,c,d)`; recipe ref |
| `form` | `radius.{none,soft,full}` (px/%); `edge.width` (px); `shadow.{flat,raised,float}` (elevation recipe) | px or %; px; shadow string |

## Component recipes (all four mandatory -- token compositions, NOT CSS)

| Component | Composed from |
|-----------|---------------|
| `surface` | `color.panel` + `form.radius` + `form.shadow` + `space.scale` padding |
| `control` | `color.signal` + `color.signal_ink` + `form.radius` + `type.text` + `motion.move.shift` on press |
| `field` | `color.panel` + `color.edge` + `color.ink` + `form.radius.soft` + `space` padding |
| `marker` | `color.signal` (tint) + `type.mono` + `form.radius.full` |

## Usage rules (all four mandatory)

1. **Contrast floor**: `ink` on `canvas` >= 4.5:1 and `signal_ink` on `signal` >= 4.5:1 (WCAG AA text).
2. **Reduce-motion**: every `motion.move` MUST collapse to `dur.instant` under `prefers-reduced-motion`.
3. **Single signal**: exactly one `signal` role -- no competing primary accents in one system.
4. **Density mode**: declare `density: comfortable | compact`; it selects the active `space.scale` band.

## CEXAI leverage declaration (mandatory)

A `design_system` is an ACTIVE composable asset, not a passive token dump: every instance
MUST declare a `leverage:` block stating how CEXAI binds it. Missing or empty -> FAIL.

| Field | Meaning | Shape |
|-------|---------|-------|
| `feeds_kinds` | Registered kinds that consume this system at F3 INJECT | list, len >= 1 -- e.g. `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck` |
| `inject_hook` | One line: how a builder binds the tokens at F3 INJECT | string |
| `brand_config_relation` | How it realizes the global `brand_config` identity into bindable tokens | string |
| `composes_with` | CEXAI primitives it plugs into | list -- e.g. `variant_shotgun_taste_loop`, `user_model`, `gdp` |
| `binds_8f` | 8F steps where the system acts | list -- `F1_constrain`, `F3_inject` |

## Instance frontmatter contract

`id` (`p06_ds_{{name}}`), `kind: design_system`, `pillar: P06`, `title`, `version`,
`aesthetic` (one-line stance), `density` (comfortable|compact), the mandatory `leverage:`
block (above), `quality: null`, plus standard `created`/`author`/`tags`/`tldr`/`related`.

## Validation rules (GOVERN -- fail closed)

- Missing any required group/slot -> FAIL (incomplete contract).
- Missing or empty `leverage:` block (no `feeds_kinds`) -> FAIL (passive token dump, not an active asset).
- Any contrast pair below 4.5:1 -> FAIL (a11y floor breached).
- More than one `signal` role -> FAIL (single-signal rule).
- A `motion.move` with no reduce-motion fallback -> FAIL.
- Raw values where a slot reference is required (e.g. a CSS literal in a component) -> WARN.

### How to use

```text
You are the design/frontend generator acting under F1 CONSTRAIN.
- Load exactly one design_system instance; bind its tokens as your only palette/scale source.
- Compose components from the recipes above; never improvise off-token values.
- Honor every usage rule (contrast, reduce-motion, single-signal, density) at emit time.
```
