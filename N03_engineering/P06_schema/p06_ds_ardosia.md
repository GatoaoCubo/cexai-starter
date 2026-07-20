---
id: p06_ds_ardosia
kind: design_system
pillar: P06
nucleus: N03
title: "Ardosia -- neutral, civic, compact, stark serif-mono design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Slate-mineral dark canvas, civic-neutral palette, serif display with mono data track, one desaturated sage signal, and motion that resolves without ceremony -- a system built for legislative tables, public records, and government dashboards."
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
  inject_hook: "F3 INJECT: bind Ardosia tokens as the sole palette/scale/motion source; compose only from the four recipes; motion resolves quickly, collapses to dur.instant under reduced-motion."
  brand_config_relation: "Realizes a civic/government/public-data brand_config identity into bindable neutral-dark tokens; brand_config selects Ardosia as the active system for institutional and regulatory surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, dark, neutral, compact, serif, civic, government, dataviz, leverage]
tldr: "Neutral dark civic system: slate-mineral canvas, sage-citrine signal, serif display paired with mono data track, hairline 1px edges, compact 4px grid, and resolving motion without theatrics. Conforms to p06_vs_design_system."
density_score: 0.91
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_vigil
---

# Ardosia

Conforms to [[p06_vs_design_system]]. Named for the grey-green slate of courthouse facades and legislative blackboards.
Institutional neutral: no decoration, only legibility and authority. Dresses
civic portals, public-data dashboards, and government-grade surfaces.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#131815` | `signal` | `#A8C56A` |
| `panel` | `#1E2421` | `signal_ink` | `#0A140C` |
| `ink` | `#D8DED9` | `affirm` | `#6EC98A` |
| `ink_soft` | `#7D8C82` | `alert` | `#E07B6A` |
| `edge` | `#2E3830` | | |

Signal: desaturated sage-citrine -- authoritative, temperature-neutral.
Affirm/alert are status only; never accent.

## type

- `face.display`: `'Playfair Display', 'Georgia', ui-serif, serif`
- `face.text`: `'Source Serif 4', 'Georgia', ui-serif, serif`
- `face.mono`: `'IBM Plex Mono', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.2` (minor third -- tight for legislative data)
- `scale.steps`: `t_1 0.833 | t1 1.0 | t2 1.2 | t3 1.44 | t4 1.728 | t5 2.074 | t6 2.488` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.15 | normal 1.5 | loose 1.75`

Display serif headings; text serif for briefs; mono for codes and identifiers.

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12` (-> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 100ms | calm 200ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0,0,1) | emphatic cubic-bezier(0.35,0,0,1)`
- `move`: `enter = quick+standard | exit = quick+linear | shift = quick+standard`

## form

- `radius`: `none 0 | soft 2px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 0 0 1px #2E3830 | float 0 6px 20px #00000088`

Near-square (2px). Hairlines as elevation. Full radius for marker pills only.

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft` + `shadow.raised` + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s3` padding |
| `marker` | `signal` @ 18% tint + `type.mono/t_1` + `radius.full` |

## usage

1. **Contrast**: `ink #D8DED9` on `canvas #131815` ~= 13:1; `signal_ink #0A140C` on `signal #A8C56A` ~= 9.8:1 -- both clear WCAG AA.
2. **Reduce-motion**: collapse every `move` to `dur.instant` under `prefers-reduced-motion`.
3. **Single signal**: sage-citrine `#A8C56A` only -- `affirm`/`alert` are status, never accent.
4. **Density**: `compact` -- active band `s0..s5`; tables use `s2/s3` cell padding; `s6/s7` gutters.

## CEXAI Leverage

Ardosia is an ACTIVE asset, not a token dump. A builder loads it at F3 INJECT as the
sole visual source:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- civic portals, public-data dashboards, regulatory filings, institutional surfaces.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose from the four
  recipes only; motion collapses to `dur.instant` under reduced-motion.
- **brand_config**: realizes a civic/institutional identity into neutral-dark tokens;
  selected for surfaces demanding legibility and authority over expressiveness.
- **Composes with**: variant-shotgun + taste loop (neutral/compact/stark/dark/serif+mono corner),
  `user_model` (density/reading prefs), GDP (institutional gate). Binds F1 CONSTRAIN + F3 INJECT.
