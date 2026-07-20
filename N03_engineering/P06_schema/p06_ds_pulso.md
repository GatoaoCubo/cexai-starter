---
id: p06_ds_pulso
kind: design_system
pillar: P06
title: "Pulso -- warm, geometric, dark-mode design system for sonic and audio surfaces"
version: 1.0.0
created: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Deep charcoal canvas warmed by amber-coral signal, soft pillbox radius, geometric sans on a 1.25 scale, and fluid motion that breathes like a waveform -- a system tuned, not printed."
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
  inject_hook: "F3 INJECT: bind Pulso tokens as the sole palette/scale/motion source; compose only from the four recipes; motion breathes (enter slow, exit fast); collapse to dur.instant under reduced-motion."
  brand_config_relation: "Realizes a music/audio/podcast brand_config identity into bindable warm-dark geometric tokens; brand_config selects Pulso as the active system for sonic surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, dark, warm, geometric, music, audio, leverage]
tldr: "Warm dark-mode system for music and audio surfaces: deep charcoal canvas, single amber-coral signal, geometric grotesque on a 1.25 scale, soft 12px radius, and waveform-paced fluid motion. Distinct from Ferro (cold/snap), Brasa (mono/brutalist), Abismo (cold/airy). Conforms to p06_vs_design_system."
density_score: null
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Pulso

Conforms to [[p06_vs_design_system]]. Pulso (Latin/PT-BR: *pulse* -- the fundamental
rhythmic unit, the beat that carries time) holds the warm/balanced/soft/dark/geometric
corner of the design-system taxonomy. Where Ferro snaps and Abismo cuts, Pulso breathes.
It dresses music players, podcast interfaces, audio-production dashboards, and
streaming editorial surfaces where rhythm and warmth must coexist with legibility.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#131417` | `signal` | `#E8714A` |
| `panel` | `#1E2025` | `signal_ink` | `#1A0B04` |
| `ink` | `#EAE8E3` | `affirm` | `#4CAF82` |
| `ink_soft` | `#7E7B75` | `alert` | `#E05C5C` |
| `edge` | `#2E3038` | | |

## type

- `face.display`: `'DM Sans', 'Outfit', ui-sans-serif, system-ui, sans-serif`
- `face.text`: `'DM Sans', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'JetBrains Mono', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.25` (major third -- open but not airy; readable at arm's length in dim environments)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.2 | normal 1.5 | loose 1.8`

## space

- `unit`: `6px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12` (unit multipliers -> 0/6/12/18/24/36/48/72px)

## motion

- `dur`: `instant 0ms | quick 110ms | calm 260ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0,0,1) | emphatic cubic-bezier(0.15,0,0,1)`
- `move`: `enter = calm+emphatic | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 12px | full 999px` (Pulso uses pills for controls; cards stay at soft)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 2px 8px rgba(0,0,0,0.45) | float 0 12px 32px rgba(0,0,0,0.60)` (warm-dark elevation via opacity depth)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 12px` + `shadow.raised` + `s5` padding |
| `control` | `signal` bg + `signal_ink` + `radius.full` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding |
| `marker` | `signal` @ 18% tint + `type.mono/t_1` + `radius.full` + `s2` padding |

## usage

1. **Contrast**: `ink #EAE8E3` on `canvas #131417` ~= 13.8:1; `signal_ink #1A0B04` on `signal #E8714A` ~= 5.1:1 -- both clear WCAG AA (>= 4.5:1).
2. **Reduce-motion**: collapse every `move` to `dur.instant`; waveform breathing (calm+emphatic enter) collapses gracefully -- no content is lost, only the timing theatre.
3. **Single signal**: amber-coral `#E8714A` only -- `affirm` and `alert` are state-role colors, not decorative accents; never use them as a secondary brand hue.
4. **Density**: `comfortable` -- active band is `s2..s7`; `s0/s1` are reserved for icon nudges and inset borders only; do not use `s1` for text padding.

## CEXAI Leverage

Pulso is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- any music streaming, podcast app, audio-production tool, or sonic-brand surface renders
  in Pulso's tokens; the warm-dark geometric palette communicates intimacy without distraction.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the
  four recipes; enter breathes (calm+emphatic), exit is fast, motion collapses to `dur.instant`
  under reduced-motion; `radius.full` on controls, `radius.soft` on containers -- never mix.
- **brand_config**: realizes a music/audio/podcast brand identity into warm-dark geometric tokens;
  the global `brand_config` selects Pulso as the active system for that sonic identity.
- **Composes with**: the variant-shotgun + taste loop (Pulso anchors the warm/balanced/soft/dark/
  geometric corner), `user_model` (listener vs creator mode), and GDP (content-owner gate).
  Binds at F1 CONSTRAIN + F3 INJECT.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_vs_design_system]] | upstream | 0.60 |
| [[p06_ds_ferro]] | sibling | 0.42 |
| [[p06_ds_sereno]] | sibling | 0.40 |
| [[p06_ds_abismo]] | sibling | 0.38 |
