---
id: schedule_n02
kind: schedule
8f: F8_collaborate
nucleus: n02
pillar: P12
title: "Campaign Calendar -- Pre-Launch, Launch, Nurture Cadence"
overrides:
 tone: conversion-oriented
 voice: second-person direct / brand-first
 required_fields:
 - brand_voice_anchor
 - emotional_tone
 - cta_intent
 - campaign_phase
 - cadence_type
 quality_threshold: 9.0
 density_target: 0.85
 example_corpus: 3+ examples with brand voice samples
nl_spec: "campaign calendar with pre-launch, launch, and nurture phases"
version: 1.0.0
quality: null
tags: [n02, marketing, campaign_calendar, cadence, P12]
tldr: "N02 campaign schedule: pre-launch heat, launch surge, and nurture cadence orchestrated as conversion arcs"
created: "2026-07-20"
updated: "2026-07-20"
author: n02_marketing
keywords: [campaign cadence arcs, phase-specific tone shifts, cron-based recurring tasks, conversion events, teaser, objection handler, scarcity signal, soft cta, hard cta]
density_score: 1.0
related:
 - p01_kc_campaign
 - p04_mg_n02
---

## Campaign Calendar

A generic `schedule` kind covers cron-based recurring tasks. Marketing
campaigns need more: **campaign cadence arcs** -- time-sequenced conversion
events with phase-specific tone shifts.

## Campaign Phases

| Phase | Duration | Goal | Dominant Register | Frequency |
|-------|----------|------|------------------|-----------|
| Pre-launch | T-14 to T-3 | Build desire + FOMO | Warm | 3x/week |
| Launch | T-0 to T+3 | Convert NOW | Bold | Daily + urgency bursts |
| Nurture | T+4 to T+30 | Retain + upsell | Warm | 2x/week |
| Re-engagement | T+31+ | Win back lapsed | Bold or Playful | 1x/week |

## Cadence Templates

### Pre-Launch (14 days)
```yaml
T-14: Teaser -- "Something is coming. You'll want to be first."
T-10: Pain reveal -- Lead with the problem being solved
T-7: Social proof -- Early testimonial or waitlist count
T-3: Final warning -- "Doors open in 72 hours. Are you in?"
```

### Launch (4 days)
```yaml
T+0: Open -- Full offer reveal, bold register, hard CTA
T+1: Objection handler -- FAQ framed as desire amplifiers
T+2: Scarcity signal -- Honest urgency (spots, deadline, bonus)
T+3: Last call -- "This closes at midnight."
```

### Nurture (ongoing)
```yaml
cron: "{{NURTURE_CRON | default: '0 10 * * 2,4'}}"  # e.g. Tue + Thu 10am brand timezone
format: value-first email -> soft CTA
goal: next-tier conversion or referral activation
```

## Fill Before Use

```yaml
schedule_config:
  brand_voice_anchor: "{{BRAND_VOICE_ANCHOR}}"
  emotional_tone: "{{EMOTIONAL_TONE}}"
  cta_intent: "{{CTA_INTENT}}"
  campaign_phase: "pre_launch | launch | nurture | re_engagement"
  cadence_type: "{{CADENCE_TYPE | default: 'weekly'}}"
  timezone: "{{BRAND_TIMEZONE}}"
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_campaign]] | upstream | 0.26 |
| [[p04_mg_n02]] | upstream | 0.24 |
