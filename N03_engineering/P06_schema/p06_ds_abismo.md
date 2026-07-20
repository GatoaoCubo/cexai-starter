---
id: p06_ds_abismo
kind: design_system
pillar: P06
title: "Abismo -- cold, dark, airy, geometric void design system"
version: 1.1.0
created: "2026-06-15"
updated: "2026-06-24"
author: n03_builder
domain: design-systems
aesthetic: "Charcoal-blue abyss, maximum negative space, hard geometric grotesque, single electric-indigo signal, motion that glides then stops -- a system measured in silence and cuts."
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
  inject_hook: "F3 INJECT: bind Abismo tokens as the sole palette/scale/motion source; compose only from the four recipes; glide in from void, cut to nothing on exit, collapse every move to dur.instant under prefers-reduced-motion."
  brand_config_relation: "Realizes a deep-tech/spatial/observatory brand_config identity into bindable dark-geometric tokens; brand_config selects Abismo as the active system for that identity."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, dark, geometric, airy, minimal, leverage]
tldr: "Cold dark airy void: charcoal-blue canvas, 12px grid, geometric grotesque on 1.414 scale, hard zero-radius edges, single electric-indigo signal, glide-cut motion. WCAG-AA on all pairs. Conforms to p06_vs_design_system."
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_vacuo
---

# Abismo

Conforms to [[p06_vs_design_system]]. Abismo is the abyss held open by space: a deep
charcoal-blue canvas with maximum negative space enforced on a 12px baseline grid,
zero radius everywhere, and elevation through luminance shift only. Dresses deep-tech,
spatial-computing, observatory, and data-platform surfaces. Distinct from Ferro
(dark/compact/mono/terminal) -- Abismo is airy, geometric, type-forward. Distinct from
Vacuo (light/white-void) -- Abismo is its dark mirror, charcoal-blue with inverted
luminance hierarchy.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#0D1117` | `signal` | `#4060F0` |
| `panel` | `#161B26` | `signal_ink` | `#FFFFFF` |
| `ink` | `#E8EAF0` | `affirm` | `#2ECC8A` |
| `ink_soft` | `#7A8099` | `alert` | `#E05550` |
| `edge` | `#232A3B` | | |

## type

- `face.display`: `'Geist', 'Inter', 'Helvetica Neue', Arial, sans-serif`
- `face.text`: `'Geist', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Geist Mono', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.414` (augmented fourth -- wide astronomical intervals)
- `scale.steps`: `t_1 0.707 | t1 1.0 | t2 1.414 | t3 2.0 | t4 2.828 | t5 4.0 | t6 5.656` (rem)
- `weight`: `reg 300 | med 400 | bold 600`
- `leading`: `tight 1.1 | normal 1.6 | loose 1.9`

## space

- `unit`: `12px`
- `scale`: `s0 0 | s1 0.333 | s2 0.667 | s3 1 | s4 1.667 | s5 2.667 | s6 4 | s7 6.667` (unit multipliers -> 0/4/8/12/20/32/48/80px)

## motion

- `dur`: `instant 0ms | quick 140ms | calm 300ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.4,0,0.2,1) | emphatic cubic-bezier(0.0,0,0.2,1)`
- `move`: `enter = calm+emphatic (glide in from void) | exit = quick+linear (cut to nothing) | shift = quick+standard`

## form

- `radius`: `none 0 | soft 0 | full 0` (Abismo rejects curves; every edge is a ruled line)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 0 0 1px #232A3B | float 0 0 0 1px #4060F022` (luminance-line only; no blur)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.none` + `shadow.raised` (edge-line) + `s5` padding |
| `control` | `signal` bg + `signal_ink` + `radius.none` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.none` + `s3` padding |
| `marker` | `signal` @ 12% tint + `type.mono/t_1` + `radius.none` (hard-edge label) |

## usage

1. **Contrast**: `ink #E8EAF0` on `canvas #0D1117` ~= 6.9:1; `signal_ink #FFFFFF` on `signal #4060F0` ~= 5.0:1 -- both exceed WCAG AA 4.5:1 floor.
2. **Reduce-motion**: collapse every `move` to `dur.instant`; the hard-cut exit already reads silent, so the fallback is perceptually invisible.
3. **Single signal**: electric-indigo `#4060F0` only -- `affirm`/`alert` are status roles, never accent.
4. **Density**: `comfortable` -- active band is `s3..s7`; `s0/s1/s2` are hairline insets only. All paddings and margins are exact multiples of the `12px` unit.

## CEXAI Leverage

Abismo is an ACTIVE asset, not a token dump. Builders load it at F3 INJECT as the sole
visual source for the surface generated:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck` -- deep-tech, spatial-computing, observatory, and data-platform surfaces.
- **Inject hook**: bind tokens as sole palette/scale/motion source; compose only from the four recipes; enter glides from the void (calm+emphatic), exit cuts to nothing (quick+linear), every move collapses to `dur.instant` under reduced-motion.
- **brand_config**: realizes a deep-tech/spatial/observatory brand identity into bindable dark geometric tokens; `brand_config` selects Abismo as the active system.
- **Composes with**: variant-shotgun + taste loop (Abismo anchors cold/airy/stark/dark/geometric corner), `user_model` (founder taste), GDP (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_vs_design_system]] | upstream | 0.60 |
| [[p06_ds_ferro]] | sibling | 0.45 |
| [[p06_ds_vacuo]] | sibling | 0.45 |
