---
kind: knowledge_card
id: bld_knowledge_card_prosody_config
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for prosody_config production
quality: null
title: "Knowledge Card Prosody Config"
version: "1.1.0"
author: n03_hybrid_review2
tags: [prosody_config, builder, knowledge_card, ssml, elevenlabs, playht, cartesia]
tldr: "Domain knowledge for prosody_config production -- SSML, emotion/style tags, provider-specific prosody controls"
domain: "prosody_config construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F3_inject"
keywords: [prosody_config construction, knowledge card prosody config, style tags, provider-specific prosody controls, prosody_config, builder, knowledge_card]
density_score: 0.92
related:
  - hybrid_review2_n03
  - p09_qg_prosody_config
  - bld_instruction_prosody_config
  - bld_output_template_prosody_config
  - bld_knowledge_card_tts_provider
---
## Domain Overview
Prosody_config defines voice personality and emotional expression for TTS output -- pitch, rate, volume, emphasis, pauses, and provider-specific emotion/style tags. The config is consumed by tts_provider at inference time. Two emission paths coexist: (1) **SSML** (W3C Speech Synthesis Markup Language 1.1) -- portable tags recognized by Google Cloud TTS, Azure Speech, AWS Polly, IBM Watson; (2) **provider-native controls** -- JSON/param payloads for neural TTS vendors that exceed SSML expressiveness (ElevenLabs v3, PlayHT Play3.0, Cartesia Sonic, Hume Octave).

The circumplex model of affect (valence x arousal) maps cleanly onto the two dominant provider paradigms: `style` + `stability` sliders (ElevenLabs) or explicit emotion tags (PlayHT, Cartesia). Prosody_config MUST stay declarative -- no audio bytes, no model weights, no agent persona logic (that belongs in agent_profile).

## Key Concepts
| Concept              | Definition                                                                     | Source                          |
|----------------------|--------------------------------------------------------------------------------|---------------------------------|
| SSML                 | W3C XML markup for speech synthesis: `<prosody>`, `<break>`, `<emphasis>`     | W3C SSML 1.1 (2010)             |
| Pitch contour        | F0 pattern over time; SSML `pitch` attr: x-low..x-high, Hz, st, %              | W3C SSML 1.1 Sec 3.2.4          |
| Speaking rate        | WPM or SSML `rate`: x-slow..x-fast, %, or numeric                              | W3C SSML 1.1 Sec 3.2.4          |
| Volume               | SSML `volume`: silent, x-soft..x-loud, dB                                      | W3C SSML 1.1 Sec 3.2.4          |
| Break                | SSML `<break time="500ms"/>` or strength=none..x-strong                        | W3C SSML 1.1 Sec 3.2.3          |
| Emphasis             | SSML `<emphasis level="strong">` strong/moderate/reduced                       | W3C SSML 1.1 Sec 3.2.2          |

## Provider Prosody Matrix (2024)
| Provider           | SSML? | Emotion Tags                              | Pitch/Rate/Vol     | Notes                                        |
|--------------------|-------|-------------------------------------------|--------------------|----------------------------------------------|
| Azure Neural TTS   | Yes   | `<mstts:express-as style="cheerful">`     | SSML full          | 14 styles: cheerful, sad, angry, whispering  |
| Google Cloud TTS   | Yes   | SSML only (no custom styles)              | SSML full          | WaveNet/Neural2 voices; no native emotion    |
| AWS Polly          | Yes   | `<amazon:domain name="news">` + SSML      | SSML full          | Neural voices; limited emotion (newscaster)  |
| ElevenLabs v3      | No    | `stability`, `similarity_boost`, `style`  | voice_settings obj | Most expressive; multilingual; 0-1 sliders   |
| PlayHT Play3.0     | Partial| `emotion: male_happy` enum (8 values)     | speed only         | Low-latency streaming; fewer prosody knobs   |
| Cartesia Sonic     | No    | Inline `[emotion]` brackets in text        | speed, language    | ~90ms latency; text-embedded directives      |

## Industry Standards
- W3C SSML 1.1 (Speech Synthesis Markup Language)
- W3C PLS 1.0 (Pronunciation Lexicon Specification)
- ISO/IEC 24612 (Linguistic annotation framework)
- IPA (International Phonetic Alphabet) for phoneme override

## Common Patterns
1. Declare a baseline prosody block (neutral), then define named emotion variants that delta from it.
2. When target provider supports SSML, emit SSML strings; when native, emit provider-specific JSON payload.
3. Map circumplex (valence, arousal) -> provider sliders: high arousal + positive valence = ElevenLabs style=0.6, stability=0.3.
4. Use `<break>` tags at clause boundaries for natural phrasing (200-500ms typical).
5. Keep SSML and native payloads in parallel fields -- do NOT conflate.
6. Test across 3+ providers before shipping; prosody perception is non-portable.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[hybrid_review2_n03]] | downstream | 0.66 |
| [[p09_qg_prosody_config]] | downstream | 0.64 |
| [[bld_instruction_prosody_config]] | downstream | 0.54 |
| [[bld_output_template_prosody_config]] | downstream | 0.43 |
| [[bld_knowledge_card_tts_provider]] | sibling | 0.41 |
