---
id: p07_sr_copy_gates
kind: scoring_rubric
8f: F7_govern
pillar: P07
nucleus: n02
title: "Rubric: Marketing Copy Gates (G1-G7)"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n02_marketing
framework: "Copy Gates (G1-G7)"
target_kinds: [landing_page, prompt_template, action_prompt]
dimensions_count: 7
total_weight: 100
threshold_golden: 9.5
threshold_publish: 8.0
threshold_review: 7.0
automation_status: semi-automated
domain: marketing_copy
quality: null
tags: [scoring_rubric, marketing, copy, n02, P07, quality-gate]
tldr: "A weighted 0-10 scoring rubric for marketing copy deliverables -- 7 dimensions (hook, register, anti-pattern, CTA, A/B coverage, length, brand voice), each with explicit PUBLISH/REVIEW/REJECT calibration."
when_to_use: "Load at F7 GOVERN when scoring any copy deliverable (tagline, ad/social/email copy, landing-page copy, campaign prompt artifact)."
keywords: [hook strength, register match, anti-pattern blocklist, cta specificity, ab variant coverage, platform character limit, brand voice anchor]
density_score: 0.92
calibration_set: []
calibration_set_note: "No calibration examples exist on disk yet. Do not backfill a fabricated calibration_set -- add real refs only after the first GOLDEN-tier artifact is scored and archived."
inter_rater_agreement: null
inter_rater_agreement_note: "No calibration study has been run. Do not fabricate an agreement figure."
appeals_process: "Submit to the orchestrating nucleus with the competing score and which gate's evidence is disputed."
related:
  - p06_vs_content_spec_n02
  - p03_ap_copy_generation_n02
---

# Rubric: Marketing Copy Gates (G1-G7)

## Framework Overview

Most copy quality bars start as an informal checklist in someone's head.
This rubric formalizes that checklist into 7 weighted dimensions with
explicit scales and tier thresholds, so two different reviewers (or an LLM
judge and a human) converge on the same verdict for the same artifact.

Applies to: taglines, ad/social/email copy, landing-page copy blocks,
campaign prompt artifacts -- any artifact whose primary payload is
persuasive copy rather than markup or code.

## Dimensions

| # | Dimension | Weight | Scale | Score 10 | Score 5 | Score 0 |
|---|-----------|--------|-------|----------|---------|---------|
| G1 | Hook | 20% | 0-10 | First sentence creates genuine tension/curiosity; reader cannot stop | Hook present but predictable, mild interest | No hook -- opens with "We are..." or the product name |
| G2 | Register | 15% | 0-10 | Matches the context-triggered register exactly (e.g. warm for nurture, bold for launch, playful for social) | Register present but mismatched to context | No discernible register -- generic corporate tone |
| G3 | Anti-pattern | 15% | 0-10 | Zero hits against the brand's forbidden-phrase blocklist | 1 hit, otherwise clean | 2+ hits, or an unsubstantiated health/financial claim present |
| G4 | CTA | 20% | 0-10 | Exactly one CTA, action-verb-first, <= 5 words, not a generic fallback ("click here"/"learn more"/"submit"/"buy now") | CTA present but generic, or 2 CTAs (decision fatigue) | 0 CTAs in conversion-focused copy, or an unproven superlative used as the CTA |
| G5 | A/B | 10% | 0-10 | Variant A (desire-led) + Variant B (pain-led) both present, B built via a deliberate hook-adjacency swap, not a random second draft | 2 variants present but barely differentiated (near-synonyms) | Single version, no variants |
| G6 | Length | 10% | 0-10 | Within the exact per-platform limit for every asset field (headline/body/CTA/hashtags) | Within limit but no margin (>= 95% of cap) | Exceeds any platform's hard limit |
| G7 | Brand Voice | 10% | 0-10 | Matches the brand's declared voice anchor (tone/formality/personality/energy) | Neutral, on-brand-adjacent but not distinctly branded | Off-brand: wrong formality, wrong energy, or a blocked phrase |

Weights sum to 100% (20 + 15 + 15 + 20 + 10 + 10 + 10).

```
soft_score = SUM(dimension_score * weight) on a 0-10 scale
final_score = ALL 7 dimensions evaluated ? soft_score : incomplete
```

## Thresholds

| Tier | Score | Action |
|------|-------|--------|
| GOLDEN | >= 9.5 | Save as canonical copy example |
| PUBLISH | >= 8.0 | Deliver to client / activate in campaign |
| REVIEW | >= 7.0 | Return to F6 with the lowest-scoring gate named explicitly; one revision cycle |
| REJECT | < 7.0 | Full rewrite from a new hook formula, not a patch |

## Calibration

- **GOLDEN**: every gate at Score 10 simultaneously -- rare by design (G1 and
  G4 carry the most weight; a genuinely irresistible hook AND a
  zero-friction CTA together is the actual bar, not just an average).
- **PUBLISH**: G1/G4 (the 40%-weight pair) both >= 7, no gate at 0, G3 clean.
- **REVIEW**: one of the seven gates is weak but the rest clear PUBLISH --
  targeted revision, not a wholesale rewrite.
- **REJECT**: G1 or G4 at or near 0 -- copy with no hook or no CTA has no
  persuasion mechanism regardless of how the other five gates score.

No calibration examples exist yet (see `calibration_set_note`) -- this
section states the reasoning, not measured anchors, until a first batch of
scored artifacts is archived.

## Automation

| Dimension | Status | Method |
|-----------|--------|----------------|
| G1 Hook | Manual | LLM self-critique against the brand's tone examples -- no automated hook-scorer required |
| G2 Register | Manual | Human/LLM judgment -- context-to-register mapping is not currently pattern-matchable |
| G3 Anti-pattern | Automatable | Literal string match against the brand's forbidden-phrase blocklist -- a plain-text list, no tool build required |
| G4 CTA | Semi-automated | Pattern match against a generic-CTA fail-list is mechanical; full grading needs human or LLM judgment |
| G5 A/B | Automatable | Count `Variant A` / `Variant B` labels -- no tool needed |
| G6 Length | Automatable | Character count vs. `p06_vs_content_spec_n02.md`'s platform limit table -- no tool needed |
| G7 Brand Voice | Manual | Compare against the brand voice config (`p03_pt_brand_voice_templates.md` / `p09_env_brand_override_n02.md`) |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_vs_content_spec_n02]] | upstream | 0.42 |
| [[p03_ap_copy_generation_n02]] | related | 0.35 |
