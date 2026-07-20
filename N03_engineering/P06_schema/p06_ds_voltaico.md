---
id: p06_ds_voltaico
kind: design_system
pillar: P06
nucleus: N03
title: "Voltaico -- high-voltage competitive HUD design system"
version: 1.0.0
created: "2026-06-15"
author: design-system-builder
domain: gaming-esports
aesthetic: "Near-black arena, hairline hard edges, single electric-cyan signal, magenta only for alerts -- a live scoreboard that never softens."
density: compact
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
quality: null
leverage:
  feeds_kinds: [landing_page, interactive_demo, onboarding_flow, pitch_deck, product_tour]
  inject_hook: "F3 INJECT: bind Voltaico tokens as the sole palette/scale/motion source; compose only from the four recipes; motion is instant or quick -- no easing theatre; collapse every move to dur.instant under prefers-reduced-motion."
  brand_config_relation: "Realizes a gaming/esports brand_config identity into bindable HUD-grade tokens; brand_config selects Voltaico as the active system for competitive-play surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
status: DRAFT
tags: [design-system, tokens, dark, gaming, esports, hud, electric, leverage, mono, compact]
tldr: "Cold dark-mode system: near-black canvas, electric-cyan single signal, magenta alert, hard-edge zero-radius form, mono+geometric type on a tight 1.25 scale, and snap-fast linear motion. Conforms to p06_vs_design_system."
density_score: 0.91
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Voltaico

Conforms to [[p06_vs_design_system]]. Built for scoreboards, match HUDs, live-stream
overlays, and tournament dashboards. Every decision serves glance-speed legibility:
hard edges, zero rounding, one cyan signal, magenta reserved for alert only.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#0A0B0F` | `signal` | `#00D9FF` |
| `panel` | `#12151C` | `signal_ink` | `#000F12` |
| `ink` | `#E4EAF0` | `affirm` | `#1AE86B` |
| `ink_soft` | `#6B7685` | `alert` | `#FF2D78` |
| `edge` | `#1E2530` | | |

## type

- `face.display`: `'Barlow Condensed', 'Arial Narrow', sans-serif`
- `face.text`: `'Barlow', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Share Tech Mono', 'Courier New', ui-monospace, monospace`
- `scale.ratio`: `1.25` (major second -- compact, numeric-heavy)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 600 | bold 800`
- `leading`: `tight 1.05 | normal 1.35 | loose 1.6`

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 80ms | calm 150ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.2,0,0,1) | emphatic cubic-bezier(0.4,0,0,1)`
- `move`: `enter = quick+standard | exit = instant+linear | shift = quick+linear`

## form

- `radius`: `none 0 | soft 0 | full 0` (Voltaico refuses rounding -- all surfaces are hard-edged)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 0 0 1px #1E2530 | float 0 0 0 1px #00D9FF, 0 4px 16px rgba(0,217,255,0.15)`

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel #12151C` + `radius.none 0` + `shadow.raised` (border hairline) + `s3` padding; stacks as HUD panel |
| `control` | `signal #00D9FF` bg + `signal_ink #000F12` + `radius.none` + `type.display/bold` + `move.shift` on press |
| `field` | `panel` + `edge 1px #1E2530` + `ink #E4EAF0` + `radius.none` + `s2` x-padding `s1` y-padding; stat input |
| `marker` | `signal #00D9FF` @ 18% opacity tint + `type.mono/t_1/bold` + `radius.none`; ping badge / rank chip |

## usage

1. **Contrast**: `ink #E4EAF0` on `canvas #0A0B0F` ~= 14.2:1; `signal_ink #000F12` on `signal #00D9FF` ~= 16.1:1; `ink_soft #6B7685` on `canvas #0A0B0F` ~= 4.8:1 -- all clear WCAG AA.
2. **Reduce-motion**: collapse every `move` (enter/exit/shift) to `dur.instant 0ms` under `prefers-reduced-motion: reduce`; Voltaico is already near-instant so the fallback is invisible.
3. **Single signal**: electric cyan `#00D9FF` is the sole signal -- `affirm #1AE86B` is kill-feed green (status only), `alert #FF2D78` is magenta (damage/alert status only); neither competes as an accent.
4. **Density**: `compact` -- active band is `s0..s5` (0-24px); `s6/s7` reserved for panel gutters and viewport margins only.

## CEXAI Leverage

Voltaico is an ACTIVE asset, not a token dump:

- **Feeds**: `landing_page`, `interactive_demo`, `onboarding_flow`, `pitch_deck`, `product_tour` -- any esports or live-event surface renders in Voltaico tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the four recipes; snap motion only; collapse every `move` to `dur.instant` under `prefers-reduced-motion`.
- **brand_config**: realizes a gaming/esports brand identity into bindable HUD-grade tokens; `brand_config` selects Voltaico as the active system.
- **Composes with**: variant-shotgun + taste loop (Voltaico anchors cold/compact/stark/dark/mono corner), `user_model`, `gdp`. Binds at F1 CONSTRAIN + F3 INJECT.
