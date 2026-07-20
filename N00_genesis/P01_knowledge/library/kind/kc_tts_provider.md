---
id: kc_tts_provider
kind: knowledge_card
8f: F3_inject
title: Text-to-Speech Provider Integration
version: 1.0.0
quality: null
pillar: P01
tldr: "Integration guide for text-to-speech services -- voice selection, rate, platform support, latency"
when_to_use: "When adding speech synthesis capability to agents, accessibility tools, or IVR systems"
keywords: [text-to-speech, api integration, rest api, authentication mechanisms, voice selection, speech rate, latency optimization, bandwidth usage, cross-platform compatibility]
density_score: 0.88
related:
  - kc_stt_provider
  - bld_instruction_tts_provider
  - kc_voice_pipeline
  - tts-provider-builder
  - n00_tts_provider_manifest
---

# Text-to-Speech Provider Integration

This knowledge card explains how to integrate text-to-speech (TTS) providers into applications. It covers:

1. **Supported Platforms**  
   - Web (JavaScript/HTML5)
   - Mobile (iOS/Android)
   - Desktop (Windows/macOS/Linux)
   - Cloud services (AWS Polly, Azure Text to Speech)

2. **API Integration**  
   - REST API endpoints for text synthesis
   - Authentication mechanisms (API keys, OAuth)
   - Rate limiting and quotas

3. **Customization Options**  
   - Voice selection (gender, accent, language)
   - Speech rate and pitch adjustment
   - Background noise suppression

4. **Use Cases**  
   - Accessibility tools for visually impaired users
   - Automated customer service IVRs
   - E-learning content delivery
   - Voice assistants and smart home devices

5. **Implementation Considerations**  
   - Latency optimization techniques
   - Bandwidth usage management
   - Cross-platform compatibility strategies

6. **Popular TTS Providers**  
   - Amazon Polly
   - Google Cloud Text-to-Speech
   - Azure Cognitive Services
   - IBM Watson Text to Speech
   - Amazon Lex (for conversational agents)

7. **Best Practices**  
   - Text normalization before synthesis
   - Error handling for network failures
   - Speech synthesis fallback mechanisms
   - User preference storage for personalized experiences

## How to use

```text
ROLE: you are an integration agent adding speech synthesis to a product.
1. Pick a provider from "Popular TTS Providers" against your platform + latency needs.
2. Wire the REST endpoint + auth (API key / OAuth); honor rate limits and quotas.
3. Set voice, rate, and pitch per the Customization Options.
4. Apply Best Practices: normalize text, handle network failures, define a fallback voice.
Primary 8F verb: INJECT (this card is reference knowledge consumed at F3 when wiring a TTS tool).
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_stt_provider]] | sibling | 0.48 |
| [[bld_instruction_tts_provider]] | downstream | 0.43 |
| [[kc_voice_pipeline]] | sibling | 0.40 |
| [[tts-provider-builder]] | downstream | 0.39 |
