---
id: bld_memory_alert_rule
kind: entity_memory
pillar: P10
llm_function: INJECT
version: 1.0.0
quality: null
tags: [alert_rule, memory, patterns]
title: "Memory Patterns: alert_rule"
author: builder
tldr: "Alert Rule memory: context persistence, recall triggers, and state management"
8f: "F3_inject"
keywords: [memory patterns, alert rule memory, context persistence, recall triggers, and state management, alert_rule, memory, patterns, common mistakes, kind memory]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - alert-rule-builder
  - bld_architecture_alert_rule
---
# Memory Patterns: alert_rule
## What to Remember
- alert_rule GOVERNS observability (system threshold -> action)
- NOT guardrail (LLM behavior) -- completely different concern
- for_duration prevents flapping: always set >= 1m for warning, can be 0s for critical
- Severity must route to different destinations: critical=page, warning=ticket, info=log
- Every critical alert needs a runbook (link or inline steps)

## Common Mistakes
| Mistake | Correction |
|---------|-----------|
| Missing for_duration | Always set; 0s if instant, 5m typical for warning |
| Vague metric expression ("high traffic") | PromQL expression with numeric threshold |
| Conflating with guardrail | alert_rule = system metric; guardrail = LLM behavior |
| Routing all to same channel | Critical -> PD; Warning -> Slack; Info -> log |
| No runbook | Every critical alert needs remediation path |

## Cross-Kind Memory
- signal: what alert_rule evaluates (alert fires on signal threshold)
- guardrail: LLM behavior constraints (NOT alert_rule)
- quality_gate: artifact scoring gates (NOT alert_rule)
- workflow: alert_rule may trigger auto-remediation workflow

## Reuse Signals
- Check existing alert_rules: grep P09 for ar_ prefix files
- Check if Prometheus/Alertmanager config already has rules to avoid duplication
- Group related alerts by system for inhibition rules

## Memory Persistence Checklist

- Verify memory type matches taxonomy (entity, episodic, procedural, working)
- Validate retention policy aligns with data lifecycle rules
- Cross-reference with memory_scope for boundary correctness
- Check for stale entries that need decay or pruning

## Memory Pattern

```yaml
# Memory lifecycle
type: classified
retention: defined
scope: bounded
decay: configured
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_memory_update.py --check
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[alert-rule-builder]] | upstream | 0.49 |
| [[bld_architecture_alert_rule]] | upstream | 0.41 |
