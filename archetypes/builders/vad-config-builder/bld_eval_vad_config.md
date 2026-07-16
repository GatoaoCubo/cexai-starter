---
kind: quality_gate
id: p09_qg_vad_config
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for vad_config
quality: null
title: "Quality Gate Vad Config"
version: "1.0.0"
author: wave1_builder_gen
tags:
  - "vad_config"
  - "builder"
  - "quality_gate"
tldr: "Quality gate with HARD and SOFT scoring for vad_config"
domain: "vad_config construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords:
  - "vad_config construction"
  - "quality gate vad config"
  - "vad_config"
  - "builder"
  - "quality_gate"
  - "p09_vad_[a-za-z0-9_]+"
  - "## anti-example 1: missing required parameters"
  - "## why it fails missing"
  - "quality gate"
  - "fail condition"
density_score: 0.85
related:
  - vad-config-builder
---
## Quality Gate

## Definition  
| metric       | threshold | operator | scope  |  
|--------------|-----------|----------|--------|  
| sensitivity  | 0.7       | >=       | global |  
| threshold    | 0.3       | <=       | per-channel |  
| operator     | valid     | in       | all    |  

## HARD Gates  
| ID   | Check               | Fail Condition                          |  
|------|---------------------|-----------------------------------------|  
| H01  | YAML valid          | Invalid YAML syntax                     |  
| H02  | ID matches pattern  | ID does not match `p09_vad_[a-zA-Z0-9_]+` |  
| H03  | kind matches        | kind != `vad_config`                   |  
| H04  | sensitivity range   | sensitivity < 0.1 or > 1.0            |  
| H05  | aggressiveness range | aggressiveness not in {0,1,2,3}       |  
| H06  | frame_size_ms valid | frame_size_ms not in {10,20,30}        |  
| H07  | noise_floor_db range | noise_floor_db < -70 or > -10 dBFS   |  

## SOFT Scoring  
| Dim | Dimension          | Weight | Scoring Guide                               |  
|-----|--------------------|--------|---------------------------------------------|  
| D1  | YAML structure     | 0.15   | 1.0 if valid, 0.5 if partial, 0 otherwise   |  
| D2  | Sensitivity tuning | 0.15   | 1.0 if env-specific, 0.5 if generic default |  
| D3  | Engine coverage    | 0.10   | 1.0 if engine named (webrtc/silero/kaldi), 0.5 otherwise |  
| D4  | Frame size valid   | 0.10   | 1.0 if in {10,20,30}ms, 0 otherwise         |  
| D5  | Use case docs      | 0.10   | 1.0 if use_case section present, 0.5 otherwise |  
| D6  | ID uniqueness      | 0.10   | 1.0 if ID unique, 0.5 if duplicate          |  
| D7  | Documentation      | 0.10   | 1.0 if comments present, 0.5 if missing     |  
| D8  | HARD gate coverage | 0.20   | 1.0 if meets all H01-H07, 0.5 if partial   |  

## Actions  
| Score     | Action                          |  
|-----------|---------------------------------|  
| GOLDEN    | >=9.5: No action required       |  
| PUBLISH   | >=8.0: Auto-publish             |  
| REVIEW    | >=7.0: Require manual review    |  
| REJECT    | <7.0: Reject and rework         |  

## Bypass  
| conditions                        | approver | audit trail         |  
|----------------------------------|----------|---------------------|  
| Critical production outage       | CTO      | Ticket #VAD-2023-01 |  
| Emergency configuration fix      | CTO      | Ticket #VAD-2023-02 |  
| Approved by QA for A/B testing   | QA Lead  | Ticket #VAD-2023-03 |

## Examples

## Golden Example
```yaml
---
kind: vad_config
version: 1.0
---
sensitivity: 0.75
noise_suppression: true
aggressiveness: 3
min_speech_duration: 0.5
max_speech_gap: 1.2
```

## Anti-Example 1: Missing required parameters
```yaml
---
kind: vad_config
version: 1.0
---
noise_suppression: false
aggressiveness: 5
```
## Why it fails
Missing `sensitivity` and `min_speech_duration` parameters make configuration incomplete. VAD requires these to function reliably, leading to unpredictable detection behavior.

## Anti-Example 2: Mixing VAD with STT parameters
```yaml
---
kind: vad_config
version: 1.0
---
sensitivity: 0.8
transcription_engine: "whisper"
language: "en"
```
## Why it fails
Includes `transcription_engine` and `language` parameters which belong to STT components, not VAD. This violates the boundary constraint and creates configuration conflicts.

### H_RELATED: Cross-Reference Check (HARD)
- [ ] `related:` frontmatter field populated (min 3 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream or sibling reference
- Gate: REJECT if < 3 entries (auto-populated by cex_wikilink.py at F6.5)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
