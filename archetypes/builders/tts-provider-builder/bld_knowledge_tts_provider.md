---
kind: knowledge_card
id: bld_knowledge_card_tts_provider
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for tts_provider production
quality: null
title: "Knowledge Card Tts Provider"
version: "1.0.0"
author: wave1_builder_gen
tags: [tts_provider, builder, knowledge_card]
tldr: "Domain knowledge for tts_provider production"
domain: "tts_provider construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F3_inject"
keywords: [tts_provider construction, knowledge card tts provider, tts_provider, builder, knowledge_card, domain overview  
text, google cloud, azure cognitive services, custom neural voice, amazon polly]
density_score: 0.85
related:
  - tts-provider-builder
  - voice-pipeline-builder
---
## Domain Overview  
Text-to-speech (TTS) provider integration converts text into spoken audio via third-party APIs or self-hosted models. The market has bifurcated into cloud APIs (high quality, instant availability) and generative open-source models (voice cloning, zero-shot synthesis).

**Cloud APIs -- commercial**:
- **ElevenLabs**: State-of-the-art voice quality. Turbo v2.5 model, ~300ms TTFB, voice cloning from 1min sample. $0.30/1K chars (Starter), $0.18/1K (Creator). 29 languages. MOS ~4.7/5. Streaming via WebSocket.
- **OpenAI TTS**: 6 voices (alloy/echo/fable/onyx/nova/shimmer), streaming via HTTP chunks. $0.015/1K chars (tts-1), $0.030/1K (tts-1-hd). Simple REST API, no SSML.
- **Cartesia**: Ultra-low-latency TTS (<80ms TTFB). Sonic model with voice cloning (3sec sample). $0.065/1K chars (Sonic). Streaming via WebSocket. Optimized for real-time conversational AI. 15 languages.
- **Google Cloud TTS**: 380+ voices, 50+ languages. Neural2 (MOS ~4.5), Studio (MOS ~4.7). $4/1M (Standard), $16/1M (Neural2), $160/1M (Studio).

**Open-source / self-hosted**:
- **Coqui TTS (XTTS v2)**: Multi-speaker, voice cloning, 17 languages, runs on consumer GPU (4GB VRAM). Apache 2.0.
- **Bark** (Suno AI): Generative audio model, supports non-verbal sounds, music. Not real-time (2-30s generation). MIT.
- **Tortoise-TTS**: High quality but slow (30-120s). Best for offline quality.
- **Piper TTS**: Fast, lightweight, ONNX-based. <100ms on CPU. Ideal for embedded/edge.

Integration focuses on API compatibility, latency optimization, and SSML support. MOS (Mean Opinion Score) is the standard quality benchmark (4.0+ = good, 4.5+ = excellent, 4.7+ = near-human).  

## Key Concepts  
| Concept          | Definition                                                                 | Source                          |  
|------------------|----------------------------------------------------------------------------|---------------------------------|  
| TTS API          | Interface for requesting speech synthesis from a provider                   | AWS Polly, Google Cloud TTS     |  
| Voice Model      | Pretrained speaker profile (e.g., gender, age, accent)                    | Azure Cognitive Services        |  
| Latency          | Time between text input and audio delivery                                | ISO/IEC 24612                   |  
| Language Support | Provider’s list of supported languages and locales                        | Google Cloud TTS Documentation  |  
| SSML             | Speech Synthesis Markup Language for text formatting                      | W3C SSML Specification          |  
| Audio Format     | Output encoding (e.g., 16kHz PCM, MP3)                                    | RTP Protocol                    |  

## Vendor Benchmark Matrix (2024-2025)

| Provider | MOS Score | Latency (TTFB) | Price (USD) | Voice Cloning | Languages |
|---|---|---|---|---|---|
| ElevenLabs Turbo v2.5 | ~4.7/5 | ~300ms | $0.30/1K chars | Yes (1min sample) | 29 |
| Cartesia Sonic | ~4.6/5 | <80ms | $0.065/1K chars | Yes (3sec sample) | 15 |
| OpenAI TTS-1-HD | ~4.5/5 | ~400ms | $0.030/1K chars | No | 57 |
| Google Neural2 | ~4.5/5 | ~200ms | $0.016/1K chars | No | 50+ |
| Azure Neural | ~4.4/5 | ~200ms | $0.016/1K chars | Yes (Custom) | 140+ |
| Deepgram Aura-2 | ~4.3/5 | <250ms | $0.015/1K chars | No | 1 (EN) |

**Cartesia** (recommended for real-time conversational AI): Sonic model, sub-80ms TTFB is market-leading for streaming voice agents. WebSocket streaming. Best for LiveKit/Daily.co pipelines.

**Deepgram Aura** (recommended for cost-sensitive English voice bots): Aura-2 model, $0.015/1K chars, <250ms TTFB, designed for high-volume conversational AI. Pairs naturally with Deepgram STT.

## Industry Standards  
- SSML (W3C)  
- ISO/IEC 24612: Speech Synthesis Metadata  
- RTP (Real-time Transport Protocol)  
- Web Speech API (W3C)  

## Common Patterns  
1. Use SSML for advanced text formatting and pronunciation control.  
2. Implement asynchronous processing for long or complex text inputs.  
3. Design fallback mechanisms for unsupported languages or API failures.  
4. Apply rate limiting to avoid provider quota overruns.  
5. Cache frequently used audio clips to reduce redundant API calls.  
6. Align audio sampling rates with provider and platform requirements.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[tts-provider-builder]] | downstream | 0.56 |
| [[voice-pipeline-builder]] | downstream | 0.36 |
