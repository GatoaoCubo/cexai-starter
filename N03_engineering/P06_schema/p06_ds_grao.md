---
id: p06_ds_grao
kind: design_system
pillar: P06
nucleus: N03
title: "Grao -- cozy-roastery, warm-humanist, light-first design system"
version: 1.0.0
created: "2026-06-15"
author: design-system-builder
domain: coffee-cafe
aesthetic: "Cream canvas, espresso ink, caramel warmth, soft corners and breathing motion -- a system that feels handcrafted, not printed."
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
  inject_hook: "F3 INJECT: bind Grao tokens as the sole palette/scale/motion source; compose only from the four recipes; breathe on enter, collapse to instant under reduced-motion."
  brand_config_relation: "Realizes a specialty-coffee/artisanal-roastery brand_config identity into bindable warm-light tokens; brand_config selects Grao as the active system."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, warm, humanist, coffee, artisanal, leverage]
tldr: "Warm light-mode system for specialty coffee: soft cream canvas, espresso-dark ink, caramel signal, humanist sans display on a 1.25 scale, rounded 8px corners, and gentle breathing motion. Conforms to p06_vs_design_system."
density_score: 0.9
status: DRAFT
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Grao

Conforms to [[p06_vs_design_system]]. Grao dresses specialty-coffee and artisanal
roastery surfaces: a cream canvas that evokes unbleached parchment, espresso-brown
ink as deep and grounded as a ristretto, one caramel signal that warms without
shouting. Corners yield softly; motion breathes rather than snaps.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F9F3EA` | `signal` | `#B5622E` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FFF5EC` |
| `ink` | `#2C1A0E` | `affirm` | `#4A7C59` |
| `ink_soft` | `#7A5C44` | `alert` | `#B03A2A` |
| `edge` | `#E4D5C1` | | |

## type

- `face.display`: `'Nunito', 'Trebuchet MS', sans-serif`
- `face.text`: `'Lato', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Fira Mono', ui-monospace, monospace`
- `scale.ratio`: `1.25` (major second -- warm, readable)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 600 | bold 700`
- `leading`: `tight 1.25 | normal 1.6 | loose 1.85`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 4 | s7 6` (multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 140ms | calm 280ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.4,0,0.2,1) | emphatic cubic-bezier(0.34,1.4,0.64,1)`
- `move`: `enter = calm+emphatic (gentle breath in) | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 8px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px rgba(44,26,14,0.07), 0 4px 10px rgba(44,26,14,0.05) | float 0 10px 28px rgba(44,26,14,0.11)`

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 8px` + `shadow.raised` + `s5` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding |
| `marker` | `signal` @ 14% tint + `type.mono/t_1` + `radius.full` (pill) |

## usage

1. **Contrast**: `ink #2C1A0E` on `canvas #F9F3EA` ~=14.8:1; `signal_ink #FFF5EC` on `signal #B5622E` ~=5.5:1 -- both clear WCAG AA (text and large/UI).
2. **Reduce-motion**: collapse every `move` (including the emphatic `enter` breath) to `dur.instant`; never spring under reduced-motion.
3. **Single signal**: caramel `#B5622E` only -- `affirm`/`alert` are status, never accent.
4. **Density**: `comfortable` -- the active band is `s2..s7`; `s0/s1` are hairline insets only.

## CEXAI Leverage

Grao is an ACTIVE asset, not a token dump. A builder loads exactly one design_system
at F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`,
  `pitch_deck` -- any specialty-coffee, roastery, or cafe-menu surface renders in
  Grao's tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only
  from the four recipes; gentle breath on `enter`, collapse every `move` to
  `dur.instant` under reduced-motion.
- **brand_config**: realizes an artisanal/specialty-coffee brand identity into bindable
  warm-light tokens; the global `brand_config` selects Grao as the active system for
  that identity.
- **Composes with**: the variant-shotgun + taste loop (Grao anchors the
  warm/soft/light/humanist/artisanal corner), `user_model` (founder taste), and GDP
  (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.
