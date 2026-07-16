---
kind: quality_gate
id: p11_qg_audio_tool
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of audio_tool artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: audio_tool"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, audio-tool, P04, speech, stt, tts, direction, formats, languages]
tldr: "Pass/fail gate for audio_tool artifacts: direction declaration, model validity, format enum compliance, BCP-47 language codes, streaming declaration."
domain: "audio processing tool — STT, TTS, and audio analysis with declared direction, models, formats, and language coverage"
created: "2026-03-28"
updated: "2026-03-28"
8f: "F7_govern"
keywords: [audio processing tool, and language coverage, direction declaration, model validity, format enum compliance, language codes, streaming declaration]
density_score: 0.91
related:
  - bld_schema_audio_tool
  - audio-tool-builder
---
## Quality Gate

# Gate: audio_tool
## Definition
| Field | Value |
|---|---|
| metric | audio_tool artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: audio_tool` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p04_audio_[a-z][a-z0-9_]+$` | ID has hyphens, uppercase, missing prefix, or wrong namespace |
| H03 | ID equals filename stem | `id: p04_audio_stt` but file is `p04_audio_transcription.md` |
| H04 | Kind equals literal `audio_tool` | `kind: tool`, `kind: cli_tool`, or any non-audio_tool value |
| H05 | Quality field is null | `quality: 8.5` or any non-null value |
| H06 | All required fields present | Missing any of: direction, models, formats, languages, name, tldr |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Direction clarity | 1.0 | Direction declared + processing flow described in ## Direction section |
| Model documentation | 1.0 | Each model has provider, accuracy tier, latency class, cost tier in ## Models table |
| Format compatibility | 1.0 | ## Formats section shows input/output matrix; formats match frontmatter list |
| Language coverage | 1.0 | ## Languages section lists BCP-47 codes with quality tier per model |
| Streaming declaration | 0.5 | streaming: true/false declared; if true, streaming protocol described |
| Sample rate specificity | 0.5 | sample_rate declared with Hz value apownte to direction |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Internal prototype tool used only during provider evaluation, never shipped |
| approver | Author self-certification with comment explaining prototype-only scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d — prototype tools must be promoted to >= 7.0 or removed from repo |
| never_bypass | H01 (unparseable YAML), H05 (self-scored quality), H07 (invalid direction) |

## Examples

# Examples: audio-tool-builder
## Golden Example
INPUT: "Create a speech-to-text tool using Whisper and Deepgram for transcription"
OUTPUT:
```yaml
id: p04_audio_speech_transcription
kind: audio_tool
pillar: P04
version: "1.0.0"
created: "2026-03-28"
updated: "2026-03-28"
author: "builder_agent"
name: "Speech Transcription Tool"
```
## Overview
Transcribes audio input to text using Whisper large-v3 (OpenAI) or Deepgram Nova-2.
Used by voice interfaces, meeting recorders, and content pipelines requiring accurate multilingual transcription.
## Direction
Input (STT): audio bytes received -> format detected -> model selected -> transcription returned as text with optional word-level timestamps.
Streaming mode: audio chunks pushed in real-time, partial transcripts emitted as SSE events.
## Models
| Model | Provider | Accuracy | Latency | Cost |
|-------|----------|----------|---------|------|
| whisper_large_v3 | OpenAI | high | medium (2-8s) | $0.006/min |
| deepgram_nova_2 | Deepgram | high | low (<1s) | $0.0043/min |
## Formats
| Format | Input | Output | Notes |
|--------|-------|--------|-------|
| mp3 | yes | - | lossy, common upload format |
| wav | yes | - | lossless PCM, highest accuracy |
| ogg | yes | - | open format, good for web |
| flac | yes | - | lossless compressed |
| webm | yes | - | browser MediaRecorder default |
| m4a | yes | - | Apple ecosystem format |
## Languages
| Code | Language | Whisper | Deepgram |
|------|----------|---------|---------|
| en | English | high | high |
| pt-BR | Portuguese (Brazil) | high | medium |
| es | Spanish | high | medium |
| fr | French | high | medium |
| de | German | high | medium |
| ja | Japanese | medium | low |
| zh | Chinese (Mandarin) | medium | low |
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p04_audio_ pattern (H02 pass)
- kind: audio_tool (H04 pass)
- direction: input — valid enum (H06 pass)
## Anti-Example
INPUT: "Create audio tool for text to speech"
BAD OUTPUT:
```yaml
id: tts-tool
kind: tool
pillar: tools
name: TTS
models: [GPT-4o]
quality: 9.0
tags: [tts]
```
Converts text to audio.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
