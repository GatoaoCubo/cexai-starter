---
id: p06_ds_vacuo
kind: design_system
pillar: P06
nucleus: N03
title: "Vacuo -- geometric, grid-strict, editorial-void design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Near-white void, strict 8px grid, zero-radius hard edges, single cobalt accent, motion that cuts -- a system drawn with a t-square, not a brush."
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
  inject_hook: "F3 INJECT: bind Vacuo tokens as the sole palette/scale/motion source; compose only from the four recipes; cut on enter, instant under reduced-motion."
  brand_config_relation: "Realizes an architectural/editorial/precision-instrument brand_config identity into bindable geometric tokens; brand_config selects Vacuo as the active system."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, geometric, editorial, minimal, leverage]
tldr: "Cold airy light-mode system: near-white canvas, strict 8px baseline grid, geometric grotesque type on a 1.5 scale, zero-radius hard edges, single cobalt-indigo signal, and cut-fast motion. Conforms to p06_vs_design_system."
density_score: 0.91
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Vacuo

Conforms to [[p06_vs_design_system]]. Vacuo is void-as-discipline: generous whitespace
enforced by an 8px baseline grid, no radius anywhere, elevation through edge-line only.
It dresses architectural, editorial, precision-instrument, and institutional surfaces.
Distinct from [[p06_ds_ferro]] (dark/compact/terminal) and [[p06_ds_sereno]] (warm/spring/humanist).

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F5F5F7` | `signal` | `#2952CC` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FFFFFF` |
| `ink` | `#161618` | `affirm` | `#1A7F5A` |
| `ink_soft` | `#6B6B72` | `alert` | `#C0392B` |
| `edge` | `#DCDCE0` | | |

## type

- `face.display`: `'DM Sans', 'Helvetica Neue', Arial, sans-serif`
- `face.text`: `'DM Sans', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'DM Mono', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.5` (perfect fifth -- austere, wide intervals, strong hierarchy)
- `scale.steps`: `t_1 0.667 | t1 1.0 | t2 1.5 | t3 2.25 | t4 3.375 | t5 5.063 | t6 7.594` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.1 | normal 1.5 | loose 1.75`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 4 | s7 6` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 120ms | calm 220ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.2,0,0,1) | emphatic cubic-bezier(0.0,0,0.0,1)`
- `move`: `enter = quick+emphatic (hard cut in) | exit = quick+linear | shift = quick+standard`

## form

- `radius`: `none 0 | soft 0 | full 0` (Vacuo rejects every curve; hard edges everywhere)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 0 0 1px var(edge) | float 0 0 0 1px #2952CC22` (edge-line only; no blur)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.none` + `shadow.raised` (edge-line) + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.none` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.none` + `s3` padding |
| `marker` | `signal` @ 10% tint + `type.mono/t_1` + `radius.none` (hard-edge label) |

## usage

1. **Contrast**: `ink #161618` on `canvas #F5F5F7` ~= 15.4:1; `signal_ink #FFFFFF` on `signal #2952CC` ~= 10.3:1 -- both clear WCAG AA.
2. **Reduce-motion**: collapse every `move` to `dur.instant`; Vacuo's cuts are already near-instant so the fallback is invisible.
3. **Single signal**: cobalt-indigo `#2952CC` only -- `affirm`/`alert` are status roles, never accent.
4. **Density**: `comfortable` -- the active band is `s2..s7`; `s0/s1` are hairline insets only. Grid discipline: all paddings and margins must be exact multiples of the `8px` unit.

## CEXAI Leverage

Vacuo is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- any architectural, editorial, or precision-instrument surface renders in Vacuo's tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the
  four recipes; motion cuts (never springs or snaps to ease-in) and collapses to `dur.instant`
  under reduced-motion.
- **brand_config**: realizes an architectural/editorial brand identity into bindable geometric tokens;
  the global `brand_config` selects Vacuo as the active system for that identity.
- **Composes with**: the variant-shotgun + taste loop (Vacuo anchors the cold/airy/stark/light/geometric
  corner), `user_model` (founder taste), and GDP (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.
