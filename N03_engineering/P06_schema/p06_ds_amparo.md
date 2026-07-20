---
id: p06_ds_amparo
kind: design_system
pillar: P06
nucleus: N03
title: "Amparo -- calm clinical, soft-teal telehealth design system"
version: 1.0.0
created: "2026-06-15"
author: design-system-builder
domain: telehealth
aesthetic: "Warm-white canvas, deep-teal signal, humanist type, motion that settles -- built to lower patient anxiety."
density: comfortable
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
quality: null
status: DRAFT
leverage:
  feeds_kinds: [landing_page, patient_portal, onboarding_flow, interactive_demo, product_tour]
  inject_hook: "F3 INJECT: bind Amparo tokens as sole palette/scale/motion source; compose only from four recipes; motion settles (no springs); collapse all moves to dur.instant under prefers-reduced-motion."
  brand_config_relation: "Realizes a telehealth/patient-care brand_config into bindable calm-clinical tokens; brand_config selects Amparo for patient-facing surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, telehealth, calm, humanist, teal, accessible, leverage]
tldr: "Accessible-first light-mode telehealth system: warm-white canvas, deep-teal signal, humanist sans on 1.25 scale, airy 8px spacing, soft 12px corners, calm settling motion with mandatory reduce-motion fallback."
density_score: 0.89
related:
  - p06_vs_design_system
  - p06_ds_sereno
---

# Amparo

Conforms to [[p06_vs_design_system]]. Patient-facing telehealth: virtual visits,
patient portals, medication and symptom trackers. Every token answers one question --
does this lower or raise patient anxiety? Occupies the cold/airy/soft/light/humanist
aesthetic corner.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F5F8FA` | `signal` | `#226878` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FFFFFF` |
| `ink` | `#1C2B36` | `affirm` | `#1F6B4A` |
| `ink_soft` | `#4A6070` | `alert` | `#B5341E` |
| `edge` | `#C8D8E4` | | |

## type

- `face.display`: `'Nunito', 'Trebuchet MS', ui-sans-serif, sans-serif`
- `face.text`: `'Nunito', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Roboto Mono', ui-monospace, monospace`
- `scale.ratio`: `1.25` (major second -- calm, legible)
- `scale.steps`: `t_1 0.80 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 600 | bold 700`
- `leading`: `tight 1.35 | normal 1.65 | loose 1.9`

## space

- `unit`: `8px`
- `scale`: `s0 0|s1 0.5|s2 1|s3 1.5|s4 2|s5 3|s6 4|s7 6` (unit multipliers)

## motion

- `dur`: `instant 0ms | quick 140ms | calm 300ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0,0.1,1) | emphatic cubic-bezier(0.25,0,0,1)`
- `move`: `enter = calm+emphatic (settle in) | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 12px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px rgba(28,43,54,0.07), 0 4px 14px rgba(28,43,54,0.05) | float 0 10px 28px rgba(28,43,54,0.11)`

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 12px` + `shadow.raised` + `s5` padding; `shadow.float` for appointment/vitals modals |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press; `affirm` variant for confirm-action (mark taken, join visit) |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding; `alert` border on invalid state + icon label (never color-alone) |
| `marker` | `signal` @ 14% tint + `type.mono/t_1` + `radius.full`; `affirm` tint for resolved/normal; `alert` tint for critical/overdue |

## usage

1. **Contrast (a11y-critical)**: `ink #1C2B36` on `canvas #F5F8FA` ~= 13.0:1 (AAA); `signal_ink #FFFFFF` on `signal #226878` ~= 6.3:1 (AA+); `ink_soft #4A6070` on canvas ~= 6.0:1 (AA). Error states use `alert` color AND icon/label -- never color alone.
2. **Reduce-motion**: collapse every `move` to `dur.instant` under `prefers-reduced-motion: reduce`; no settling curves. Session-timeout and appointment alerts skip enter animation regardless of motion preference.
3. **Single signal**: deep teal `#226878` only -- `affirm`/`alert` are clinical status, never accent. All primary CTAs, active states, and navigation resolve to `signal`.
4. **Density**: `comfortable` -- active band `s2..s7`; `s0/s1` for internal insets only. Forms use `s5` vertical rhythm between fields; vital cards use `s6` between sections.

## CEXAI Leverage

Active asset -- not a token dump. A builder loads exactly one design_system at F3 INJECT:

| Field | Value |
|-------|-------|
| **Feeds** | `landing_page`, `patient_portal`, `onboarding_flow`, `interactive_demo`, `product_tour` |
| **Inject hook** | bind as sole palette/scale/motion source; four recipes only; enter settles; all moves -> `dur.instant` under reduced-motion |
| **brand_config** | realizes telehealth brand identity into calm-clinical tokens for patient-facing surfaces |
| **Composes with** | variant-shotgun + taste loop, `user_model` (a11y prefs), GDP (clinical UX gates) |
| **Binds 8F** | F1 CONSTRAIN + F3 INJECT |
