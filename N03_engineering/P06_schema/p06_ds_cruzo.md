---
id: p06_ds_cruzo
kind: design_system
pillar: P06
nucleus: N03
title: "Cruzo -- warm compact stark light grotesque design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Parchment canvas, dense condensed grotesque at poster scale, zero-radius hard edges, one tomato-brick signal, snap motion -- drawn with a poster-printer's rule, conversion-first."
density: compact
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
quality: null
leverage:
  feeds_kinds: [landing_page, pitch_deck, product_tour, onboarding_flow, interactive_demo]
  inject_hook: "F3 INJECT: bind Cruzo tokens as sole palette/scale/motion source; four recipes only; tomato signal only; snap enter; instant under reduced-motion."
  brand_config_relation: "Realizes a poster/performance-marketing brand_config identity into bindable warm-light grotesque tokens; brand_config selects Cruzo as the active system."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, warm, compact, stark, grotesque, poster, leverage]
tldr: "Warm compact light-mode: parchment canvas, condensed grotesque on 1.333 scale, zero-radius hard edges, tomato-brick signal at 5.6:1, 4px unit, snap motion. Conforms to p06_vs_design_system."
density_score: 0.91
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_brasa
  - p06_ds_vacuo
---

# Cruzo

Conforms to [[p06_vs_design_system]]. Poster energy as system: parchment canvas,
condensed grotesque for headline-scale action, zero radius, one tomato-brick signal,
snap motion. Distinct from [[p06_ds_brasa]] (dark/mono), [[p06_ds_vacuo]] (cold/airy),
[[p06_ds_sereno]] (warm/soft/humanist). Coordinate: warm/compact/stark/light/grotesque.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F2EDE3` | `signal` | `#B83400` |
| `panel` | `#FDFAF5` | `signal_ink` | `#FFFFFF` |
| `ink` | `#1C1612` | `affirm` | `#2A7A44` |
| `ink_soft` | `#6B5E52` | `alert` | `#B5200F` |
| `edge` | `#D4CABC` | | |

## type

- `face.display`: `'Barlow Condensed', 'Franklin Gothic Medium Cond', 'Impact', sans-serif`
- `face.text`: `'Barlow', 'Helvetica Neue', Arial, sans-serif`
- `face.mono`: `'JetBrains Mono', 'Consolas', ui-monospace, monospace`
- `scale.ratio`: `1.333` (perfect fourth -- punchy poster steps, controlled range)
- `scale.steps`: `t_1 0.75 | t1 1.0 | t2 1.333 | t3 1.777 | t4 2.369 | t5 3.157 | t6 4.209` (rem)
- `weight`: `reg 400 | med 600 | bold 800`
- `leading`: `tight 1.05 | normal 1.35 | loose 1.6`

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 90ms | calm 180ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.2,0,0,1) | emphatic cubic-bezier(0.0,0.8,0.0,1)`
- `move`: `enter = quick+emphatic (poster snap) | exit = instant+linear | shift = quick+standard`

## form

- `radius`: `none 0 | soft 0 | full 0` (Cruzo rejects all curves; poster corners are square)
- `edge.width`: `2px` (heavier rule for poster register)
- `shadow`: `flat none | raised 0 0 0 2px var(edge) | float 2px 4px 0 rgba(28,22,18,0.18)` (offset rule; no blur)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.none` + `shadow.raised` (2px rule) + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.none` + `type.display/bold` + `move.shift` on press |
| `field` | `panel` + `edge 2px` + `ink` + `radius.none` + `s3` padding |
| `marker` | `signal` @ 12% tint + `type.mono/t_1/bold` + `radius.none` |

## usage

1. **Contrast**: `ink #1C1612` on `canvas #F2EDE3` ~= 15.2:1; `signal_ink #FFFFFF` on `signal #B83400` ~= 5.6:1 -- both clear WCAG AA (floor 4.5:1).
2. **Reduce-motion**: collapse every `move` to `dur.instant` under `prefers-reduced-motion`; Cruzo already snaps, so the fallback is invisible.
3. **Single signal**: tomato-brick `#B83400` only -- `affirm`/`alert` are status roles, never accent.
4. **Density**: `compact` -- active band is `s0..s5`; `s6/s7` reserved for page-level gutters and section breaks only.

## CEXAI Leverage

Cruzo is ACTIVE, not a token dump. A builder binds exactly one design_system at F3 INJECT
as the sole visual source:

- **Feeds**: `landing_page`, `pitch_deck`, `product_tour`, `onboarding_flow`, `interactive_demo`
  -- conversion-focused and poster-register surfaces render in Cruzo's tokens.
- **Inject hook**: bind as sole palette/scale/motion source; four recipes only; tomato `signal`
  is the single accent; every `move` collapses to `dur.instant` under reduced-motion;
  display weight at bold/800 for headline impact.
- **brand_config**: realizes a performance-marketing brand identity into warm-light grotesque
  tokens; `brand_config` selects Cruzo when conversion pressure outranks editorial calm.
- **Composes with**: variant-shotgun + taste loop (anchors warm/compact/stark/light/grotesque
  corner vs Brasa dark and Vacuo cold), `user_model`, GDP. Binds F1_constrain + F3_inject.
