---
id: p03_pt_brand_voice_templates
kind: prompt_template
8f: F6_produce
pillar: P03
title: Brand Voice Templates — Tone & Messaging Calibration
version: 1.0.0
created: 2026-07-20
author: n02_marketing
domain: brand_voice_copywriting
quality: null
tags: [prompt_template, brand_voice, tone, messaging, audience, forbidden-words, N02]
tldr: Brand voice calibration templates for different audiences and channels -- includes a forbidden-word list per audience segment so copy avoids management-speak and empty superlatives. Ensures consistent brand personality without flattening different readers into one tone.
voice_dimensions: [tone, formality, personality, energy, perspective]
keywords: [brand voice, tone calibration, personality, energy level, audience-specific adaptations, b2b professional, b2c consumer, forbidden words]
density_score: 0.9
related:
  - p09_env_brand_override_n02
  - kc_marketing_vocabulary
  - p06_vs_content_spec_n02
---

# Brand Voice Templates — Tone & Messaging Calibration

## Purpose

Copy that "sounds like the brand" is not a vibe -- it is a set of dials you can
set explicitly and check mechanically. This template exposes the dials as
`{{open_vars}}` so any brand can calibrate voice without rewriting the
generation logic underneath.

## 1. Voice Dimension Framework

```yaml
brand_voice_config:
  tone:
    scale: "professional <-> conversational <-> casual"
    position: "{{BRAND_TONE_POSITION | default: '60% conversational'}}"

  formality:
    scale: "formal <-> semi-formal <-> informal"
    position: "{{BRAND_FORMALITY | default: '70% semi-formal'}}"

  personality:
    primary: "{{BRAND_PERSONALITY_PRIMARY | default: 'confident'}}"    # confident | humble | bold | thoughtful
    secondary: "{{BRAND_PERSONALITY_SECONDARY | default: 'helpful'}}"  # helpful | witty | authoritative | friendly

  energy:
    level: "{{BRAND_ENERGY_LEVEL | default: 'moderate'}}"        # calm | moderate | energetic | high-intensity
    expression: "{{BRAND_ENERGY_EXPRESSION | default: 'steady'}}" # steady | bursts | building | varied

  perspective:
    person: "{{BRAND_PERSON | default: '2nd_person'}}"           # 1st (we) | 2nd (you) | 3rd (customers)
    relationship: "{{BRAND_RELATIONSHIP | default: 'peer'}}"     # expert | peer | guide | coach
```

## 2. Audience-Specific Voice Adaptations

### B2B Professional Audience
```yaml
b2b_professional_voice:
  tone_adjustment: "+20% professional, +10% authoritative"
  language_preferences:
    vocabulary: "Industry terminology acceptable, avoid overly casual"
    sentence_structure: "Slightly longer sentences, complex ideas welcome"
    examples: "Business case studies, ROI-focused, data-driven"

  messaging_framework:
    opening_style: "Industry insight or business challenge"
    benefit_focus: "Efficiency, cost savings, competitive advantage"
    proof_format: "Case studies, statistics, testimonials from similar businesses"
    cta_style: "Professional action-oriented (Schedule demo, Get proposal)"

  template_example: |
    "For [INDUSTRY] leaders managing [CHALLENGE], [SOLUTION] delivers [SPECIFIC_OUTCOME].

    Companies like [CUSTOMER_EXAMPLE] have seen [QUANTIFIED_RESULT] in just [TIMEFRAME].

    [CTA: Get your custom ROI analysis]"
```

### B2C Consumer Audience
```yaml
b2c_consumer_voice:
  tone_adjustment: "+30% conversational, +20% relatable"
  language_preferences:
    vocabulary: "Simple, everyday language, emotional resonance"
    sentence_structure: "Shorter sentences, easy scanning"
    examples: "Personal stories, lifestyle benefits, transformation"

  messaging_framework:
    opening_style: "Personal question or relatable scenario"
    benefit_focus: "Lifestyle improvement, emotional satisfaction, convenience"
    proof_format: "Customer stories, before/after, social proof"
    cta_style: "Benefit-focused (Start feeling better today, Get instant access)"

  template_example: |
    "Tired of [RELATABLE_PROBLEM]? You're not alone.

    [CUSTOMER_NAME] felt the same way until they discovered [SOLUTION].

    Now they're [POSITIVE_OUTCOME] and couldn't be happier.

    [CTA: Start your transformation today]"
```

## 3. Channel-Specific Voice Calibration

### Email Marketing Voice
```yaml
email_voice_settings:
  subject_lines:
    tone: "{{BRAND_EMAIL_SUBJECT_TONE | default: 'curiosity-driven'}}"  # benefit-focused | curiosity-driven | direct
    length: "{{BRAND_EMAIL_SUBJECT_LENGTH | default: '30-50_chars'}}"
    personalization: "{{BRAND_EMAIL_PERSONALIZATION | default: 'first_name'}}"

  body_copy:
    greeting: "{{BRAND_EMAIL_GREETING | default: 'Hi [FIRST_NAME]'}}"
    tone_shift: "+10% personal, +15% conversational"
    paragraph_length: "2-4 sentences maximum"
    closing: "{{BRAND_EMAIL_CLOSING | default: 'Best'}}"
```

### Social Media Voice
```yaml
social_media_voice:
  platform_adaptations:
    linkedin:
      tone_adjustment: "+20% professional, +10% thought-leadership"
      hashtag_strategy: "{{BRAND_LINKEDIN_HASHTAGS | default: '3-5_industry_specific'}}"

    instagram:
      tone_adjustment: "+40% visual-storytelling, +30% lifestyle"
      hashtag_strategy: "{{BRAND_INSTAGRAM_HASHTAGS | default: '10-15_mixed'}}"

    twitter_x:
      tone_adjustment: "+50% conversational, +20% timely"
      hashtag_strategy: "{{BRAND_TWITTER_HASHTAGS | default: '1-3_trending'}}"

  universal_guidelines:
    response_time: "Within 2 hours during business hours"
    engagement_style: "{{BRAND_SOCIAL_ENGAGEMENT | default: 'helpful_and_genuine'}}"
    controversy_handling: "{{BRAND_CONTROVERSY_APPROACH | default: 'acknowledge_and_redirect'}}"
```

## 4. Voice Quality Assurance

```yaml
consistency_audit:
  tone_alignment:
    - "Does copy match brand tone position on scale?"
    - "Is formality level appropriate for audience?"
    - "Does personality come through in word choice?"

  audience_appropriateness:
    - "Language complexity matches audience sophistication?"
    - "Examples and references resonate with target?"
    - "Cultural sensitivity and inclusivity maintained?"

  channel_optimization:
    - "Format optimized for channel constraints?"
    - "Engagement style matches platform norms?"
    - "CTA strength appropriate for channel context?"
```

## 5. Forbidden-Word List (per audience segment)

Words that score "professional" in a tone audit but read as filler to the
actual reader. Strip them before delivery.

### Founder / solo operator
| Forbidden | Why | Replace with |
|-----------|-----|--------------|
| "leverage" (verb) | management-speak filler | "use", "apply", "turn into" |
| "scale" (intransitive) | undefined what is scaling | "grow revenue 3x", "double customers" |
| "synergy" | meeting jargon | drop entirely or name the specific overlap |
| "stakeholders" | hides who actually decides | "investors", "your co-founders", "the customer" |
| "ecosystem" | vague | "5 tools you already use", "your stack" |

### Marketer / operator (campaign owner)
| Forbidden | Why | Replace with |
|-----------|-----|--------------|
| "engagement" | unmeasurable noun phrase | CTR, save rate, reply rate, named metric |
| "optimize" (vague) | hides which lever | "raise CTR by", "cut bounce by" |
| "audience-first" | tautology | name the segment |
| "content strategy" | category, not action | the actual deliverable (cadence, formats, channels) |
| "next-level" | empty escalator | the specific metric and delta |

This brand voice template system ensures consistent, audience-appropriate
messaging across marketing touchpoints while keeping the flexibility to
optimize per channel and objective. Fill every `{{BRAND_*}}` variable once
per brand -- generation prompts downstream read these values, not hardcoded
defaults.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p09_env_brand_override_n02]] | downstream | 0.35 |
| [[kc_marketing_vocabulary]] | upstream | 0.27 |
| [[p06_vs_content_spec_n02]] | downstream | 0.19 |
