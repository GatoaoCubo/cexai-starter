---
kind: env_config
id: bld_config_hibernation_policy
pillar: P09
llm_function: CONSTRAIN
purpose: P09 config knobs for hibernation_policy builder
quality: null
title: "Config: hibernation_policy Builder"
version: "1.0.0"
author: n03_engineering
tags: [hibernation_policy, builder, config]
tldr: "P09 config knobs for hibernation_policy builder"
domain: "hibernation_policy construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F1_constrain"
keywords: [hibernation_policy construction, hibernation_policy builder, hibernation_policy, builder, config, default_idle_threshold_seconds, default_wake_latency_sla_seconds, default_cost_savings_estimate_pct, default_checkpoint_cadence_seconds, supported_backends]
density_score: 0.90
related:
  - bld_schema_terminal_backend
---
## hibernation_policy Builder Config Knobs

| Knob | Default | Description |
|------|---------|-------------|
| `default_idle_threshold_seconds` | 900 | Default idle threshold when not specified by user |
| `default_wake_latency_sla_seconds` | 10 | Default wake latency SLA |
| `default_cost_savings_estimate_pct` | 70 | Default cost savings estimate |
| `default_checkpoint_cadence_seconds` | null | Default periodic checkpoint interval |
| `supported_backends` | daytona,modal,singularity,generic | Comma-separated list of supported backends |
| `require_sibling_terminal_backend` | false | Warn if no sibling terminal_backend artifact found |

## Defaults by Backend

| Backend | idle_threshold_seconds | wake_latency_sla_seconds | keep_memory | snapshot_disk |
|---------|------------------------|--------------------------|-------------|---------------|
| modal | 300 | 5 | false | false |
| daytona | 1800 | 10 | true | true |
| singularity | 0 (explicit) | 60 | false | true |
| generic | 900 | 30 | true | false |

## Environment Variables

```bash
CEX_HP_DEFAULT_THRESHOLD=900          # Override default idle threshold
CEX_HP_DEFAULT_WAKE_SLA=10            # Override default wake latency SLA
CEX_HP_REQUIRE_SIBLING_TB=false       # Enforce sibling terminal_backend check
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_terminal_backend]] | upstream | 0.32 |
