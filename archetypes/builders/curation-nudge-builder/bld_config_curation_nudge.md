---
id: p11_config_curation_nudge
kind: env_config
pillar: P11
llm_function: CONSTRAIN
purpose: P09 config knobs for curation_nudge builder
quality: null
title: "Config: Curation Nudge Builder"
version: "1.0.0"
author: n03_builder
tags: [config, curation_nudge, builder, p11, memory]
domain: "curation_nudge construction"
created: "2026-04-18"
updated: "2026-04-18"
tldr: "P09 config knobs for curation_nudge builder"
8f: "F1_constrain"
keywords: [curation_nudge construction, curation nudge builder, config, curation_nudge, builder, memory, cn_trigger_type, turn_count, cn_threshold]
density_score: 0.87
related:
 - curation-nudge-builder
---
## Builder Configuration

### Runtime Defaults

| Config Key | Default | Description |
|------------|---------|-------------|
| `CN_TRIGGER_TYPE` | `turn_count` | Default trigger mechanism |
| `CN_THRESHOLD` | `10` | Default count to fire nudge |
| `CN_MIN_INTERVAL_TURNS` | `5` | Anti-spam: min turns between nudges |
| `CN_MAX_PER_SESSION` | `3` | Hard cap on nudges per session |
| `CN_DESTINATION` | `MEMORY.md` | Default memory write destination |
| `CN_AUTO_WRITE` | `true` | Persist immediately on agent confirmation |

### Environment Variables

```bash
# Override defaults for all new curation_nudge artifacts
export CN_TRIGGER_TYPE=turn_count
export CN_THRESHOLD=10
export CN_DESTINATION=MEMORY.md

# Research-heavy session: lower threshold, use entity_memory
export CN_TRIGGER_TYPE=density_threshold
export CN_THRESHOLD=5
export CN_DESTINATION=entity_memory

# Headless pipeline: disable nudge (set max_per_session=0 in config)
export CN_MAX_PER_SESSION=0
```

### Per-Trigger-Type Defaults

| Trigger Type | Default Threshold | Rationale |
|-------------|-----------------|-----------|
| `turn_count` | 10 | General sessions; fire roughly every 10 exchanges |
| `density_threshold` | 5 | Fire when 5 new facts observed; research sessions |
| `tool_call_count` | 15 | Agentic sessions; tool calls accumulate fast |
| `user_correction` | 1 | Fire on every correction (high signal value) |

### Quality Thresholds (CEX standards)

| Threshold | Value | When |
|-----------|-------|------|
| Minimum trigger | 5 | Below this threshold, nudge spam degrades session |
| Session cap | 3 | CEX default max_per_session (prevents context saturation) |
| Min interval | 5 | Anti-spam gap between consecutive nudges |

### Builder Execution Config

```yaml
builder_config:
 kind: curation_nudge
 pillar: P11
 max_bytes: 2048
 naming: "p11_cn_{{trigger_type}}.yaml"
 compile_target: yaml
 validate_on_produce: true
 hard_gate_count: 6
 soft_gate_count: 4
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[curation-nudge-builder]] | related | 0.37 |
