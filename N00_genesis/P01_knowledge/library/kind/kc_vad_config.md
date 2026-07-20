---
id: kc_vad_config
kind: knowledge_card
8f: F3_inject
title: Voice Activity Detection (VAD) Configuration
version: 1.0.0
quality: null
pillar: P01
tldr: "Voice activity detection parameters -- sensitivity, energy threshold, silence detection, profiles"
when_to_use: "When configuring speech detection in audio pipelines to distinguish voice from background noise"
keywords: [voice activity detection, sensitivity level, time constant, energy threshold, silence detection, noise suppression, echo cancellation, audio normalization, speech recognition]
density_score: 0.97
related:
  - vad-config-builder
  - bld_knowledge_card_vad_config
  - n00_vad_config_manifest
  - bld_collaboration_vad_config
  - kc_voice_pipeline
---

# Voice Activity Detection (VAD) Configuration

Voice Activity Detection (VAD) is a critical component in audio processing systems that identifies segments of speech in an audio signal. Proper configuration of VAD parameters ensures accurate detection of voice activity while minimizing false positives and negatives.

## How to use

You are a vad-config-builder at **F1 CONSTRAIN**. Set the five parameters to the
acoustic environment; start from a profile, then calibrate.

1. Pick a **Configuration Profile** (Basic, Noisy, Quiet) as the baseline.
2. Tune sensitivity + energy threshold to the ambient noise floor.
3. Set silence detection duration for the use case (call center vs. dictation).
4. Enable noise suppression / echo cancellation; monitor false-detection rate live.

## Core Configuration Parameters

### 1. Sensitivity Level
Controls the threshold for detecting voice activity. Higher values increase sensitivity to subtle speech patterns, while lower values reduce false triggers.

### 2. Time Constant (τ)
Determines the duration over which voice activity is analyzed. A longer time constant improves accuracy in noisy environments but may delay response to sudden speech changes.

### 3. Energy Threshold
Minimum energy level required to classify a segment as voice activity. Adjusts based on ambient noise levels and speaker volume.

### 4. Silence Detection
Configures the minimum duration of silence required to trigger a silence detection event. Critical for applications like call centers and automated attendants.

### 5. Audio Processing Settings
Includes parameters for noise suppression, echo cancellation, and audio normalization. These settings optimize the input signal before VAD analysis.

## Recommended Configuration Profiles

| Profile | Use Case | Key Parameters |
|--------|---------|----------------|
| Basic | General voice detection | Sensitivity: 0.7, Time Constant: 0.2s |
| Noisy | Industrial environments | Sensitivity: 0.9, Time Constant: 0.5s |
| Quiet | Library settings | Sensitivity: 0.5, Time Constant: 0.1s |

## Implementation Considerations

- Always calibrate VAD parameters to the specific acoustic environment
- Use adaptive algorithms for dynamic environments
- Monitor false detection rates during deployment
- Combine with speech recognition systems for enhanced accuracy

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[vad-config-builder]] | downstream | 0.49 |
| [[bld_knowledge_card_vad_config]] | sibling | 0.45 |
| [[bld_collaboration_vad_config]] | downstream | 0.35 |
| [[kc_voice_pipeline]] | sibling | 0.31 |
