---
id: user_journey_n02
kind: user_journey
8f: F4_reason
pillar: P05
nucleus: n02
title: "Funnel-Stage Content Mapping -- User Journey"
version: 1.0.0
quality: null
tags: [user_journey, funnel_mapping, content_strategy, TOFU_MOFU_BOFU, P05, n02_marketing]
domain: content-strategy
status: active
keywords: [funnel model, top of funnel, middle of funnel, bottom of funnel, customer journey, content mapping, call to action, pain point education]
density_score: 1.0
related:
  - kc_marketing_vocabulary
  - p01_kc_campaign
  - p03_ap_copy_generation_n02
---

# User Journey -- Funnel-Stage Content Mapping

## Purpose

Every piece of content exists at a specific moment in the user's journey.
Wrong content at the wrong moment wastes budget and confuses the audience.
This map ensures content meets the audience WHERE THEY ARE, not where the
brand wants them to be.

## The Funnel Model

```
AWARENESS (TOFU) -- Top of Funnel
Problem-aware, not solution-aware. Seeking understanding.
    |
    v
CONSIDERATION (MOFU) -- Middle of Funnel
Solution-aware, evaluating options. Seeking proof.
    |
    v
DECISION (BOFU) -- Bottom of Funnel
Vendor-aware, ready to commit. Seeking confidence.
    |
    v
RETENTION
Customer. Seeking value realization. Risk: churn.
    |
    v
ADVOCACY
Delighted customer. Potential amplifier. Seeking recognition.
```

## Stage-by-Stage Content Map

### TOFU -- Awareness

| Element | Specification |
|---------|--------------|
| **Goal** | Generate awareness; build brand familiarity |
| **Audience State** | Experiencing a pain; not yet seeking solutions |
| **Primary Metric** | Impressions, reach, engagement rate, saves |
| **Hook Type** | pain, curiosity (never authority -- not earned yet) |
| **CTA Type** | Soft -- "See how", "Learn more", "Discover" |
| **Urgency** | None or very light |
| **Formats** | Reels, carousels, short posts, educational threads |
| **Tone** | Conversational, empathetic; meet them where they are |

**TOFU Content Types:** pain-point education posts, industry insight,
aspirational storytelling, surface-level how-to content, trending-topic
commentary with a brand perspective.

### MOFU -- Consideration

| Element | Specification |
|---------|--------------|
| **Goal** | Build trust; differentiate from alternatives |
| **Audience State** | Aware of solutions; evaluating you vs. others |
| **Primary Metric** | Link clicks, profile visits, email sign-ups, downloads |
| **Hook Type** | social_proof, data, authority |
| **CTA Type** | Resource -- "Get the guide", "Watch the demo", "Read the case study" |
| **Urgency** | Moderate -- deadline for resource, limited cohort size |
| **Formats** | Carousels, long posts, email sequences, webinars, case studies |
| **Tone** | Professional + proof-heavy; let results speak |

**MOFU Content Types:** customer case studies with named, specific results;
comparison content; data-backed insights; behind-the-scenes process content;
expert interviews; gated tools/templates/calculators.

### BOFU -- Decision

| Element | Specification |
|---------|--------------|
| **Goal** | Convert -- trial, demo, purchase, sign-up |
| **Audience State** | Ready to decide; needs final confidence to act |
| **Primary Metric** | Conversion rate, cost per acquisition, demo book rate |
| **Hook Type** | Urgency + social_proof + authority |
| **CTA Type** | Direct -- "Start free trial", "Book your demo", "Claim offer" |
| **Urgency** | High -- scarcity, deadline, bonus |
| **Formats** | Direct-response ads, retargeting, email drip, landing page |
| **Tone** | Bold, confident, urgency-forward |

**BOFU Content Types:** limited-time offers, risk-reversal content ("Try
free for 14 days, cancel anytime"), final objection handling, retargeting
copy, side-by-side feature comparison, ROI calculator copy.

### RETENTION

| Element | Specification |
|---------|--------------|
| **Goal** | Reduce churn; increase LTV |
| **Audience State** | Paying customer; evaluating ongoing value |
| **Primary Metric** | Renewal rate, NPS score, feature adoption, support tickets |
| **CTA Type** | Engagement -- "Unlock feature", "Access your [report]", "Upgrade" |
| **Tone** | Warm, personal, progress-acknowledging |

### ADVOCACY

| Element | Specification |
|---------|--------------|
| **Goal** | Convert happy customers into amplifiers |
| **Audience State** | Delighted; NPS 9-10 promoter |
| **CTA Type** | Community -- "Share your story", "Refer a friend", "Join our community" |
| **Tone** | Celebratory, inclusive, grateful |

## Content Calendar Logic

```yaml
content_calendar_rule:
  tofu_mofu_bofu_ratio:
    default: "60:30:10"          # most brands need more awareness
    product_launch: "40:40:20"
    growth_phase: "50:35:15"
    mature_product: "30:40:30"

  posting_cadence:
    instagram: "{{CADENCE_INSTAGRAM | default: '4-5x per week'}}"
    linkedin: "{{CADENCE_LINKEDIN | default: '3-4x per week'}}"
    x: "{{CADENCE_X | default: '5-7x per week'}}"
    email: "{{CADENCE_EMAIL | default: '1-2x per week'}}"

  stage_rotation:
    rule: "No more than 2 consecutive BOFU posts on any platform"
    reason: audience fatigue + algorithmic suppression of sales-heavy content
```

## Journey Analytics

```yaml
journey_metric:
  cohort_id: string
  entry_stage: TOFU|MOFU|BOFU|RETENTION|ADVOCACY
  current_stage: string
  stages_touched: array[string]
  days_in_journey: integer
  conversion_event: string (nullable)
  churn_event: string (nullable)
  journey_velocity: float  # stages per week
```

## Integration

- Feeds: `p03_ap_copy_generation_n02.md` (funnel_stage injection)
- Cross-references: audience segment + journey stage combo (see your own
  `customer_segment` artifact once defined)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_marketing_vocabulary]] | upstream | 0.31 |
| [[p01_kc_campaign]] | upstream | 0.29 |
| [[p03_ap_copy_generation_n02]] | upstream | 0.28 |
