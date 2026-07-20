---
id: p09_env_brand_override_n02
kind: env_config
8f: F1_constrain
pillar: P09
title: Brand Override Config for N02 Marketing
version: 1.0.0
created: 2026-07-20
author: n02_marketing
domain: brand_configuration
quality: null
tags: [config, brand, marketing, tone, voice, N02]
tldr: Brand-specific overrides for marketing copy generation — tone, voice, terminology, and channel-specific adaptations.
keywords: [brand voice calibration, copy formula, tone adjustment, hashtag strategy, emoji usage, social proof, urgency level, character limits]
density_score: 1.0
related:
  - p03_pt_brand_voice_templates
  - p06_vs_content_spec_n02
---

# Brand Override Config — N02 Marketing

## Brand Voice Calibration

### Base Brand Settings
```yaml
brand:
  name: "{{BRAND_NAME}}"
  tone: "{{BRAND_TONE}}"    # professional | casual | technical | friendly
  voice: "{{BRAND_VOICE}}"  # confident | humble | authoritative | conversational
  energy: "{{BRAND_ENERGY}}"  # calm | energetic | bold | subtle
  person: "{{BRAND_PERSON}}"  # 1st | 2nd | 3rd
```

### Copy Formula Preferences
```yaml
copy_preferences:
  primary_formula: "{{BRAND_COPY_FORMULA | default: 'AIDA'}}"  # AIDA | PAS | BAB | FAB
  headline_style: "{{BRAND_HEADLINE_STYLE | default: 'benefit-first'}}"  # benefit-first | curiosity-gap | specific-result
  cta_style: "{{BRAND_CTA_STYLE | default: 'action-specific'}}"  # action-specific | benefit-focused | urgency-driven
  audience_address: "{{BRAND_AUDIENCE_ADDRESS | default: 'you'}}"  # you | we | customer-name
```

### Channel Adaptations
```yaml
channels:
  email:
    tone_adjustment: "+5% formal"  # relative to base tone
    max_subject_length: 50
    preview_text_required: true

  social_media:
    tone_adjustment: "+10% casual"
    hashtag_strategy: "{{BRAND_HASHTAG_STRATEGY | default: 'minimal'}}"  # minimal | moderate | extensive
    emoji_usage: "{{BRAND_EMOJI_USAGE | default: 'occasional'}}"  # none | occasional | frequent

  ads:
    tone_adjustment: "0% (base)"
    hook_requirement: "curiosity-gap + benefit"
    character_limits:
      facebook: 125
      google: 90
      linkedin: 150

  landing_pages:
    tone_adjustment: "+5% confident"
    social_proof_requirement: true
    urgency_level: "{{BRAND_URGENCY_LEVEL | default: 'moderate'}}"  # low | moderate | high
```

### Terminology & Voice

#### Approved Terms
```yaml
preferred_words:
  - "{{BRAND_PREFERRED_WORDS | default: ['solution', 'results', 'growth', 'success']}}"

power_words:
  - "{{BRAND_POWER_WORDS | default: ['proven', 'effective', 'streamlined', 'optimized']}}"

industry_terms:
  - "{{BRAND_INDUSTRY_TERMS | default: []}}"  # Brand-specific terminology
```

#### Banned Terms
```yaml
avoid_words:
  - "{{BRAND_AVOID_WORDS | default: ['amazing', 'incredible', 'revolutionary', 'game-changer']}}"

overused_phrases:
  - "{{BRAND_OVERUSED_PHRASES | default: ['take your business to the next level', 'cutting-edge', 'world-class']}}"
```

### Quality Standards
```yaml
quality_gates:
  readability:
    flesch_kincaid_min: "{{BRAND_READABILITY_MIN | default: 60}}"  # B2C: 60-70, B2B: 40-60
    max_sentence_length: "{{BRAND_MAX_SENTENCE | default: 20}}"  # words

  specificity:
    stats_preference: "{{BRAND_STATS_PREFERENCE | default: 'specific-with-source'}}"  # vague | specific | specific-with-source
    claim_substantiation: "{{BRAND_CLAIM_SUBSTANTIATION | default: 'required'}}"  # required | optional

  legal:
    disclaimer_requirement: "{{BRAND_DISCLAIMER_REQUIRED | default: false}}"
    claim_approval_needed: "{{BRAND_CLAIM_APPROVAL | default: false}}"
```

## Environment Overrides

### Development
```yaml
development:
  ab_testing: false
  approval_workflow: false
  placeholder_content: true
```

### Staging
```yaml
staging:
  ab_testing: true
  approval_workflow: true
  real_content: true
  performance_tracking: false
```

### Production
```yaml
production:
  ab_testing: true
  approval_workflow: true
  real_content: true
  performance_tracking: true
  legal_review: "{{BRAND_LEGAL_REVIEW_REQUIRED | default: false}}"
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_pt_brand_voice_templates]] | upstream | 0.36 |
| [[p06_vs_content_spec_n02]] | downstream | 0.22 |
