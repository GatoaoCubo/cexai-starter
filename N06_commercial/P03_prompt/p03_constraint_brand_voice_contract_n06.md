---
id: p03_constraint_brand_voice_contract_n06
kind: constraint_spec
pillar: P03
nucleus: n06
title: "Brand Voice Contract -- 5D Consistency Validation"
version: 1.0.0
quality: null
tags: [schema, brand, voice, contract, consistency, n06]
tldr: "Validates voice consistency across channels. 5D scores within +/-1 tolerance of brand_config. Tone matrix per channel. Do/Don't hard constraints."
density_score: 0.93
axioms:
  - "5D scores must stay within +/-1 of brand_config values -- larger deviation = brand drift."
  - "Do/Don't constraints are HARD -- violating a Don't is an automatic quality failure."
related:
  - p01_kc_brand_voice_systems
  - p03_pt_pricing_strategy_n06
  - nucleus_def_n06
updated: "2026-07-20"
---

# Brand Voice Contract

A `constraint_spec` is a HARD rule set, not a style guide -- every field below is
something a quality gate can mechanically check, not a suggestion an author
can talk themselves out of.

## 5D Voice Dimensions

Each dimension scored 1-5 in your `brand_config.yaml` (or equivalent brand
source of truth):

| Dimension | 1 | 2 | 3 | 4 | 5 |
|-----------|---|---|---|---|---|
| Formality | Casual/slang | Relaxed | Balanced | Professional | Formal/academic |
| Enthusiasm | Deadpan | Measured | Engaged | Energetic | Exuberant |
| Humor | None | Subtle/dry | Occasional | Frequent | Constant/playful |
| Warmth | Cold/clinical | Neutral | Friendly | Warm | Intimate/personal |
| Authority | Peer/equal | Knowledgeable | Expert | Authoritative | Commanding |

## Channel Tolerance Matrix

Voice scores may shift +/-1 per channel from the base brand_config values --
this is what keeps a brand recognizable while letting each channel breathe:

| Channel | Formality | Enthusiasm | Humor | Warmth | Authority |
|---------|-----------|------------|-------|--------|-----------|
| Social media | -1 | +1 | +1 | +1 | -1 |
| Blog/articles | 0 | 0 | 0 | 0 | 0 |
| Documentation | +1 | -1 | -1 | 0 | +1 |
| Email marketing | -1 | +1 | 0 | +1 | 0 |
| Sales pages | 0 | +1 | 0 | +1 | +1 |
| Customer support | -1 | 0 | 0 | +1 | -1 |
| Ads (paid) | -1 | +1 | context | +1 | 0 |

## Validation Rules

### Hard Constraints

1. No dimension may exceed bounds (1-5) after channel adjustment
2. Do's from `BRAND_VOICE_DO` must be present in ALL channel outputs
3. Don'ts from `BRAND_VOICE_DONT` must be absent from ALL channel outputs
4. `BRAND_LANGUAGE` must be consistent (no mixing languages within one artifact)

### Soft Constraints (warnings)

1. Voice shift > +/-1 from base triggers review
2. Humor in formal contexts (docs, legal) triggers warning
3. Low authority (1-2) in sales contexts triggers warning
4. Inconsistent tone across paragraphs within the same artifact

## Example Phrases (Calibration)

A brand book typically ships 8-10 example phrases per voice. These serve as
calibration:
- Every output should SOUND like these phrases
- Copywriters read the phrases before writing
- LLMs receive the phrases as few-shot examples in the prompt

## Voice Injection Snippet

For LLM prompts, inject this block from `brand_config`:

```
Voice: {{BRAND_VOICE_TONE}}
Formality: {{BRAND_VOICE_FORMALITY}}/5
Enthusiasm: {{BRAND_VOICE_ENTHUSIASM}}/5
Humor: {{BRAND_VOICE_HUMOR}}/5
Warmth: {{BRAND_VOICE_WARMTH}}/5
Authority: {{BRAND_VOICE_AUTHORITY}}/5
DO: {{BRAND_VOICE_DO}}
DON'T: {{BRAND_VOICE_DONT}}
```

## Scoring

Voice consistency score = (matching_dimensions / total_dimensions)
- Passing: >= 0.80 (4/5 dimensions within tolerance)
- Excellent: 1.00 (all dimensions within tolerance for the channel)
- Failing: < 0.60 (re-calibrate voice or retrain the copy)

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p01_kc_brand_voice_systems]] | upstream (voice theory this contract enforces) |
| [[p03_pt_pricing_strategy_n06]] | sibling (P03 prompt template that must obey this contract) |
| [[nucleus_def_n06]] | upstream |
