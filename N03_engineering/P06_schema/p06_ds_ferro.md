---
id: p06_ds_ferro
kind: design_system
pillar: P06
nucleus: N03
title: "Ferro -- engineered, sovereign, terminal-grade design system"
version: 1.1.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Monochrome canvas, hairline edges, one cold signal, motion that snaps -- a system that looks built, not decorated."
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
  inject_hook: "F3 INJECT: bind Ferro tokens as the sole palette/scale/motion source; compose only from the four recipes; snap, never spring."
  brand_config_relation: "Realizes a sovereign/developer-infra brand_config identity into bindable terminal-grade tokens; brand_config selects Ferro as the active system."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, dark, monochrome, engineered, leverage]
tldr: "Stark dark-mode system: near-black canvas, hairline borders as elevation, a single teal signal, mono-forward type on a tight 1.2 scale, and snap-fast linear motion. Conforms to p06_vs_design_system."
density_score: 0.89
related:
  - p06_vs_design_system
  - p06_ds_sereno
---

# Ferro

Conforms to [[p06_vs_design_system]]. Ferro refuses ornament: elevation is a hairline,
not a glow; corners are near-square; motion arrives and leaves without easing theatre.
It dresses developer-infrastructure and sovereign-tooling surfaces.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#0B0D0E` | `signal` | `#2DD4BF` |
| `panel` | `#16191B` | `signal_ink` | `#062925` |
| `ink` | `#E8EBED` | `affirm` | `#34D399` |
| `ink_soft` | `#8A9398` | `alert` | `#F87171` |
| `edge` | `#2A2F33` | | |

## type

- `face.display`: `'Space Grotesk', 'Arial Narrow', sans-serif`
- `face.text`: `'Inter', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'JetBrains Mono', ui-monospace, 'Cascadia Code', monospace`
- `scale.ratio`: `1.2` (minor third -- tight, utilitarian)
- `scale.steps`: `t_1 0.833 | t1 1.0 | t2 1.2 | t3 1.44 | t4 1.728 | t5 2.074 | t6 2.488` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.1 | normal 1.45 | loose 1.7`

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 90ms | calm 180ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.2,0,0,1) | emphatic cubic-bezier(0.3,0,0,1)`
- `move`: `enter = quick+standard | exit = instant+linear | shift = quick+standard`

## form

- `radius`: `none 0 | soft 2px | full 2px` (Ferro rejects pills; even markers stay near-square)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 0 0 1px var(edge) | float 0 8px 24px rgba(0,0,0,0.5)` (hairline elevation, blur only at top layer)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft` + `shadow.raised` (hairline) + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s3` padding |
| `marker` | `signal` @ 16% tint + `type.mono/t_1` + `radius.full` |

## usage

1. **Contrast**: `ink #E8EBED` on `canvas #0B0D0E` ~= 15:1; `signal_ink #062925` on `signal #2DD4BF` ~= 7.2:1 -- both clear WCAG AA.
2. **Reduce-motion**: collapse every `move` to `dur.instant` (Ferro is already near-instant; the fallback is invisible).
3. **Single signal**: teal `#2DD4BF` only -- `affirm`/`alert` are status, never accent.
4. **Density**: `compact` -- the active band is `s0..s5`; reserve `s6/s7` for page gutters.

## CEXAI Leverage

Ferro is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- any developer-infrastructure or sovereign-tooling surface renders in Ferro's tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the
  four recipes; motion snaps (never springs) and collapses to `dur.instant` under reduced-motion.
- **brand_config**: realizes a sovereign/terminal brand identity into bindable tokens; the global
  `brand_config` selects Ferro as the active system for that identity.
- **Composes with**: the variant-shotgun + taste loop (Ferro anchors the cold/compact/stark/dark/mono
  corner), `user_model` (founder taste), and GDP (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.
