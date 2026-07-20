---
id: kc_stt_provider
kind: knowledge_card
8f: F3_inject
title: Speech-to-Text Provider Integration
version: 1.0.0
quality: null
pillar: P01
tldr: "Integration guide for speech-to-text services -- providers, auth, formats, and quality metrics"
when_to_use: "When adding voice recognition or transcription capability to an agent or pipeline"
keywords: [speech-to-text, api key authentication, language model customization, speaker diarization, word error rate, audio sampling rates, noise suppression algorithms, custom vocabulary training, result formatting options, latency performance]
density_score: 1.0
related:
  - kc_tts_provider
  - stt-provider-builder
  - kc_voice_pipeline
  - bld_knowledge_card_stt_provider
  - p01_kc_audio_tool
---

# Speech-to-Text Provider Integration

Speech-to-text (STT) providers enable voice recognition capabilities by converting spoken language into written text. These services are critical for applications requiring voice interaction, transcription, and accessibility features.

## Key Providers
1. **Google Cloud Speech-to-Text** - High accuracy with 120+ languages
2. **Amazon Transcribe** - Seamless AWS integration with real-time transcription
3. **Azure Speech Services** - Enterprise-grade with custom voice models
4. **IBM Watson Speech to Text** - Advanced speaker diarization capabilities
5. **Deepgram** - Low-latency streaming transcription

## Integration Considerations
- API key authentication mechanisms
- Language model customization options
- Real-time vs batch processing capabilities
- Support for multiple audio formats (WAV, MP3, FLAC)
- Pricing models (pay-per-minute, fixed-rate)
- Error correction and punctuation awareness

## Use Cases
- Virtual assistants
- Call center transcription
- Meeting recordings
- Accessibility tools
- Voice-controlled IoT devices

## Technical Requirements
- Audio sampling rates (8kHz-48kHz)
- Noise suppression algorithms
- Speaker diarization support
- Custom vocabulary training
- Result formatting options (JSON, XML, plain text)

## Quality Factors
- Word error rate (WER) metrics
- Language support breadth
- Latency performance
- Scalability for large volumes
- Compliance with data privacy regulations

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_tts_provider]] | sibling | 0.47 |
| [[stt-provider-builder]] | downstream | 0.46 |
| [[kc_voice_pipeline]] | sibling | 0.44 |
| [[bld_knowledge_card_stt_provider]] | sibling | 0.43 |
| [[p01_kc_audio_tool]] | sibling | 0.34 |
