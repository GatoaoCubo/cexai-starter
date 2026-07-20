---
id: p06_ds_estrato
kind: design_system
pillar: P06
nucleus: N03
title: "Estrato -- cold-neutral dark geometric-mono dataviz design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Charcoal-neutral canvas, balanced density, geometric monospace stack, single amber-gold data signal, measured decelerate motion -- a system calibrated for reading numbers, not admiring chrome."
density: comfortable
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
quality: null
leverage:
  feeds_kinds: [landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck]
  inject_hook: "F3 INJECT: bind Estrato tokens as sole palette/scale/motion source; compose from the four recipes only; decelerate enter, cut exit, collapse to dur.instant under reduced-motion."
  brand_config_relation: "Realizes a dataviz/analytics-platform brand_config identity into cold-neutral dark tokens; brand_config selects Estrato for data-dense or instrument-grade surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, dark, cold-neutral, geometric, mono, dataviz, analytics, leverage]
tldr: "Cold-neutral dark dataviz system: charcoal canvas, amber-gold data signal, geometric mono-forward type on 1.25 scale, 4px corners, comfortable density, decelerate-cut motion. Conforms to p06_vs_design_system."
density_score: 0.91
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_vigil
  - p06_ds_neblina
---

# Estrato

Conforms to [[p06_vs_design_system]]. Estrato (geological stratum) dresses analytics
dashboards, reporting tools, and observability surfaces. Cold-neutral dark keeps the
eye on numbers; amber-gold marks the one datum that demands attention.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#111416` | `signal` | `#E0A32E` |
| `panel` | `#1C2025` | `signal_ink` | `#0F1214` |
| `ink` | `#D9DCE0` | `affirm` | `#4CAF82` |
| `ink_soft` | `#7A8491` | `alert` | `#E05858` |
| `edge` | `#2C3138` | | |

## type

- `face.display`: `'DM Mono', 'Fira Mono', ui-monospace, monospace`
- `face.text`: `'Inter', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'DM Mono', ui-monospace, 'Cascadia Mono', monospace`
- `scale.ratio`: `1.25` (major second, compact for label-dense layouts)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 500 | bold 600`
- `leading`: `tight 1.15 | normal 1.5 | loose 1.7`

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12` (multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 100ms | calm 220ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0,0,0.2,1) | emphatic cubic-bezier(0,0,0,1)`
- `move`: `enter = calm+standard (decelerate) | exit = quick+linear (cut) | shift = quick+standard`

## form

- `radius`: `none 0 | soft 4px | full 9999px` (geometric; pills for badge markers only)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 0 1px #2C3138 | float 0 8px 28px rgba(0,0,0,0.48)` (border-tone at layer; deep blur at float)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 4px` + `shadow.raised` + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s3` padding |
| `marker` | `signal` @ 18% tint + `type.mono/t_1` + `radius.full` (pill badge) |

## usage

1. **Contrast**: `ink #D9DCE0` on `canvas #111416` ~= 10.8:1; `signal_ink #0F1214` on `signal #E0A32E` ~= 10.2:1 -- both clear WCAG AA 4.5:1.
2. **Reduce-motion**: collapse every `move` to `dur.instant`; never animate data transitions under reduced-motion.
3. **Single signal**: amber-gold `#E0A32E` only; `affirm`/`alert` carry status meaning, never accent role.
4. **Density**: `comfortable` -- active band `s2..s7`; `s0/s1` for hairline insets; dataviz surfaces may shift to `compact` by stepping down one band.

## CEXAI Leverage

Estrato is an ACTIVE asset, not a token dump. A builder loads one design_system at F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- analytics dashboards, observability tools, and data-dense reporting surfaces.
- **Inject hook**: bind tokens as sole palette/scale/motion source; four recipes only;
  decelerate `enter`, cut `exit`, collapse to `dur.instant` under reduced-motion;
  mono display face keeps numeric columns aligned.
- **brand_config**: realizes a dataviz/analytics-platform brand identity into cold-neutral
  dark bindable tokens; `brand_config` selects Estrato for instrument-grade surfaces.
- **Composes with**: variant-shotgun + taste loop (Estrato holds the cold-neutral/dark/balanced/geometric/mono dataviz corner), `user_model` (analyst taste), GDP (data-literacy gate). Binds at F1 CONSTRAIN + F3 INJECT.
