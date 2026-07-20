---
id: p06_ds_vespera
kind: design_system
pillar: P06
nucleus: N03
title: "Vespera -- candle-lit editorial dark design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Aged-parchment-shadow canvas, cream ink, amber signal, soft organic radii, and motion that drifts and settles -- a system that reads like a book by candlelight."
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
  inject_hook: "F3 INJECT: bind Vespera tokens as the sole palette/scale/motion source; compose only from the four recipes; drift on enter, exhale on exit, collapse to dur.instant under reduced-motion."
  brand_config_relation: "Realizes a literary/luxury/editorial-dark brand_config into bindable warm-dark tokens; brand_config selects Vespera as the active system."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, dark, warm, humanist, serif, editorial, luxury, leverage]
tldr: "Warm dark editorial system: aged-parchment-shadow canvas, cream ink, amber signal, generous serif display on a perfect-fourth scale, soft organic corners, and slow drifting motion. Conforms to p06_vs_design_system."
density_score: null
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Vespera

Conforms to [[p06_vs_design_system]]. Vespera occupies the warm-dark-airy-serif corner -- distinct from [[p06_ds_ferro]]
(cold/stark/mono/compact) and [[p06_ds_sereno]] (warm/airy/light/humanist). It dresses
literary, luxury, and long-form editorial surfaces: generous, unhurried, glowing softly.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#1C1710` | `signal` | `#D4882A` |
| `panel` | `#26200F` | `signal_ink` | `#1A0F00` |
| `ink` | `#EDE5D2` | `affirm` | `#6BAF74` |
| `ink_soft` | `#9C9080` | `alert` | `#C45E5E` |
| `edge` | `#3A3020` | | |

## type

- `face.display`: `'Cormorant Garamond', 'Garamond', 'Georgia', serif`
- `face.text`: `'Lora', 'Palatino Linotype', 'Book Antiqua', serif`
- `face.mono`: `'Fira Code', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.333` (perfect fourth -- generous, editorial)
- `scale.steps`: `t_1 0.75 | t1 1.0 | t2 1.333 | t3 1.777 | t4 2.369 | t5 3.157 | t6 4.209` (rem)
- `weight`: `reg 300 | med 500 | bold 700`
- `leading`: `tight 1.3 | normal 1.75 | loose 2.0`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 2 | s4 3 | s5 4 | s6 6 | s7 9` (unit multipliers -> 0/4/8/16/24/32/48/72px)

## motion

- `dur`: `instant 0ms | quick 200ms | calm 420ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0.1,0.25,1) | emphatic cubic-bezier(0.16,1,0.3,1)`
- `move`: `enter = calm+emphatic (drift in, settle) | exit = quick+standard (exhale out) | shift = quick+standard`

## form

- `radius`: `none 0 | soft 14px | full 9999px` (soft organic curves; panels breathe)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 2px 8px rgba(10,6,0,0.45), 0 1px 3px rgba(10,6,0,0.3) | float 0 16px 48px rgba(10,6,0,0.65)` (deep warm lift; amber ghost in ambient)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 14px` + `shadow.raised` + `s5` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding |
| `marker` | `signal` @ 14% tint + `type.mono/t_1` + `radius.full` (pill) |

## usage

1. **Contrast**: `ink #EDE5D2` on `canvas #1C1710` ~= 11.6:1; `signal_ink #1A0F00` on `signal #D4882A` ~= 7.8:1 -- both clear WCAG AA (>= 4.5:1).
2. **Reduce-motion**: collapse every `move` (including the drift `enter`) to `dur.instant`; never animate under `prefers-reduced-motion`.
3. **Single signal**: amber `#D4882A` only -- `affirm`/`alert` are status roles, never accent.
4. **Density**: `comfortable` -- the active reading band is `s3..s7`; generous measure (60-75ch line length); `s0/s1` for tight insets only.

## CEXAI Leverage

Vespera is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- any literary, luxury, or editorial-dark surface renders in Vespera's tokens.
- **Inject hook**: bind tokens as sole palette/scale/motion source; compose from the four recipes;
  drift on `enter`, exhale on `exit`, collapse every `move` to `dur.instant` under reduced-motion.
- **brand_config**: realizes a literary/luxury/editorial-dark brand identity into warm-dark tokens;
  `brand_config` selects Vespera as the active system for that identity.
- **Composes with**: the variant-shotgun + taste loop (Vespera anchors the warm/airy/dark/soft/serif
  corner), `user_model` (founder taste), and GDP (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.
