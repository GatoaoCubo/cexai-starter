---
id: p06_ds_crisma
kind: design_system
pillar: P06
nucleus: N03
title: "Crisma -- warm, compact, serif, light-mode print-heritage design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Cream vellum surface, Old-Style serif display, sepia ink, amber-gold signal, tightly leaded columns -- the visual grammar of a letterpress editorial house."
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
  inject_hook: "F3 INJECT: bind Crisma tokens as the sole palette/scale/motion source; compose only from the four recipes; snap transitions, collapse to dur.instant under prefers-reduced-motion."
  brand_config_relation: "Realizes a publishing, heritage, or scholarly brand_config identity into bindable warm-compact tokens; brand_config selects Crisma as the active system for print-heritage surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, warm, compact, serif, editorial, print-heritage, leverage]
tldr: "Warm compact light-mode system: cream-vellum canvas, Old-Style serif display over a tight 1.25 scale, amber-gold signal, squared-soft corners, snap motion with print-heritage restraint. Conforms to p06_vs_design_system."
density_score: 0.91
related:
  - p06_vs_design_system
  - p06_ds_sereno
  - p06_ds_vespera
---

# Crisma

Conforms to [[p06_vs_design_system]]. Warm/compact/soft/light/serif -- distinct from
[[p06_ds_sereno]] (airy), [[p06_ds_vespera]] (dark), and all cold-side siblings.
The grammar of a letterpress editorial house: cream vellum, anointed amber, columns
that breathe only as much as the measure demands.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F5EFE0` | `signal` | `#8B5E19` |
| `panel` | `#FBF7EE` | `signal_ink` | `#FFFAF0` |
| `ink` | `#261E14` | `affirm` | `#3D6B42` |
| `ink_soft` | `#5C4A35` | `alert` | `#9B2B2B` |
| `edge` | `#D9CEBC` | | |

## type

- `face.display`: `'Cormorant Garamond', 'Palatino Linotype', 'Book Antiqua', serif`
- `face.text`: `'Libre Baskerville', 'Georgia', serif`
- `face.mono`: `'Courier Prime', 'Courier New', monospace`
- `scale.ratio`: `1.25` (major second -- editorial compact; tight column hierarchy)
- `scale.steps`: `t_1 0.80 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 600 | bold 700`
- `leading`: `tight 1.25 | normal 1.5 | loose 1.7`

## space

- `unit`: `6px`
- `scale`: `s0 0 | s1 0.667 | s2 1.333 | s3 2 | s4 2.667 | s5 4 | s6 5.333 | s7 8` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 120ms | calm 240ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.4,0,0.2,1) | emphatic cubic-bezier(0.2,0,0,1)`
- `move`: `enter = calm+emphatic (clean snap in) | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 4px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px rgba(38,30,20,0.08), 0 3px 8px rgba(38,30,20,0.06) | float 0 8px 24px rgba(38,30,20,0.13)` (warm ink-tinted elevation)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 4px` + `shadow.raised` + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s3` padding |
| `marker` | `signal` @ 14% tint + `type.mono/t_1` + `radius.full` (pill tag) |

## usage

1. **Contrast**: `ink #261E14` on `canvas #F5EFE0` ~= 14.5:1; `signal_ink #FFFAF0` on `signal #8B5E19` ~= 5.5:1 -- both clear WCAG AA (>= 4.5:1).
2. **Reduce-motion**: collapse every `move` to `dur.instant` under `prefers-reduced-motion`; no spring or emphatic easing under that flag.
3. **Single signal**: amber-gold `#8B5E19` only -- `affirm`/`alert` are status roles, never accent competitors.
4. **Density**: `compact` -- active band is `s2..s6`; `s7` is reserved for section-level breathing; `s0/s1` are hairline insets only.

## CEXAI Leverage

Crisma is an ACTIVE asset. A builder loads exactly one design_system at F3 INJECT and
binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `pitch_deck`, `product_tour`, `onboarding_flow`, `interactive_demo`
  -- any publishing or heritage-brand surface renders in Crisma's tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the
  four recipes; snap on `enter`, collapse every `move` to `dur.instant` under reduced-motion.
- **brand_config**: realizes a publishing or heritage brand identity into bindable warm-compact
  tokens; `brand_config` selects Crisma as the active system for that identity.
- **Composes with**: variant-shotgun + taste loop (anchors warm/compact/soft/light/serif corner),
  `user_model`, and GDP. Binds at F1 CONSTRAIN + F3 INJECT.
