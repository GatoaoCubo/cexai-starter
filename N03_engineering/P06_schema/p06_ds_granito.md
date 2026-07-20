---
id: p06_ds_granito
kind: design_system
pillar: P06
nucleus: N03
title: "Granito -- cold, stark, civic-grade light design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Slate-wash canvas, hard rectangular edges, institutional cobalt signal, geometric-mono type stack, and motion that advances without ceremony -- a system cut from grey stone, not poured from resin."
density: compact
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
quality: null
leverage:
  feeds_kinds: [landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck]
  inject_hook: "F3 INJECT: bind Granito tokens as the sole palette/scale/motion source; compose only from the four recipes; motion advances (never springs), collapses to dur.instant under reduced-motion."
  brand_config_relation: "Realizes a civic/public-sector/institutional brand_config identity into bindable cold-light tokens; brand_config selects Granito as the active system for that identity."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, cold, compact, geometric, civic, dataviz, institutional, leverage]
tldr: "Cold compact light system: slate-wash canvas, zero-radius rectangular forms, institutional cobalt signal, geometric-sans display paired with mono data face, and fast advancing motion. Dresses civic, public-sector, and data-transparency surfaces. Conforms to p06_vs_design_system."
density_score: 0.91
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_vacuo
---

# Granito

Conforms to [[p06_vs_design_system]]. Every edge is a rule drawn with a right angle;
every colour belongs to a civic vocabulary. It dresses public dashboards, transparency
portals, and government-grade light surfaces where trust is earned through legibility,
not charm.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F4F6F9` | `signal` | `#2152A3` |
| `panel` | `#FFFFFF` | `signal_ink` | `#F0F5FF` |
| `ink` | `#1A2333` | `affirm` | `#1B7A4E` |
| `ink_soft` | `#5A6880` | `alert` | `#C0392B` |
| `edge` | `#CBD3DF` | | |

## type

- `face.display`: `'DM Sans', 'Helvetica Neue', Arial, sans-serif`
- `face.text`: `'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'IBM Plex Mono', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.2` (minor third -- compact, data-forward)
- `scale.steps`: `t_1 0.833 | t1 1.0 | t2 1.2 | t3 1.44 | t4 1.728 | t5 2.074 | t6 2.488` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.1 | normal 1.45 | loose 1.65`

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 80ms | calm 160ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0,0.25,1) | emphatic cubic-bezier(0.4,0,0.2,1)`
- `move`: `enter = quick+standard | exit = quick+linear | shift = quick+standard`

## form

- `radius`: `none 0 | soft 0 | full 2px` (fully rectangular; only pill markers deviate)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 0 0 1px var(edge) | float 0 2px 8px rgba(26,35,51,0.12)` (structural, not atmospheric)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.none` + `shadow.raised` (1px rule border) + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.none` + `type.text/med` + `move.shift` on press |
| `field` | `canvas` bg + `edge 1px` + `ink` + `radius.none` + `s3` padding |
| `marker` | `signal` @ 12% tint + `type.mono/t_1` + `radius.full` |

## usage

1. **Contrast**: `ink #1A2333` on `canvas #F4F6F9` ~= 13.1:1; `signal_ink #F0F5FF` on `signal #2152A3` ~= 6.8:1 -- both clear WCAG AA (4.5:1 floor).
2. **Reduce-motion**: collapse every `move` to `dur.instant`; Granito motion is already minimal (80ms); fallback is imperceptible.
3. **Single signal**: institutional cobalt `#2152A3` only -- `affirm`/`alert` are status codes, never decorative accent.
4. **Density**: `compact` -- active band is `s0..s5`; `s6/s7` reserved for page gutters and section breaks only.

## CEXAI Leverage

Granito is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- civic-grade and data-transparency surfaces render in Granito tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the
  four recipes; motion collapses to `dur.instant` under `prefers-reduced-motion`.
- **brand_config**: realizes a civic/institutional brand identity into cold-light tokens;
  `brand_config` selects Granito as the active system for that identity.
- **Composes with**: variant-shotgun + taste loop (Granito anchors the cold/compact/stark/light/geometric
  corner), `user_model`, GDP. Binds at F1 CONSTRAIN + F3 INJECT.
