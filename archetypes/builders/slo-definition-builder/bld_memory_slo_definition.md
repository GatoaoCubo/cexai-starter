---
id: bld_memory_slo_definition
kind: knowledge_card
pillar: P10
title: "Memory: slo_definition Builder Patterns"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: slo_definition
quality: null
tags: [memory, slo_definition, P09]
llm_function: INJECT
tldr: "Recalled patterns and corrections for slo_definition builder sessions."
8f: "F3_inject"
keywords: [slo_definition builder patterns, memory, slo_definition, persistent patterns, common corrections, context injection priority, memory persistence checklist, memory pattern, error budget, user conflates]
density_score: null
related:
  - bld_memory_canary_config
  - bld_memory_data_contract
  - bld_memory_saga
  - bld_manifest_slo_definition
  - bld_memory_default
---
# Memory: slo_definition Builder

## Persistent Patterns
| Pattern | Frequency | Note |
|---------|-----------|------|
| target_percent < 100.0 always | HIGH | Gate H06 |
| Compute error_budget_minutes from formula | HIGH | Never guess |
| Specify both fast-burn (1h) and slow-burn (6h) alerts | HIGH | Google SRE standard |
| error_budget_policy is mandatory | HIGH | Gate H07 |

## Common Corrections
| Mistake | Correction |
|---------|-----------|
| User sets 100% SLO | Reject: explain error budget requires headroom; suggest 99.99% |
| User conflates SLO with SLA | Teach: SLA is contract with penalties; SLO is internal target |
| User omits burn rate thresholds | Add standard 14x/6x burn rates |
| User conflates with quality_gate | Redirect: quality_gate is build-time; slo_definition is runtime |

## Context Injection Priority
1. bld_schema_slo_definition.md
2. bld_knowledge_card_slo_definition.md (error budget math)
3. bld_examples_slo_definition.md
4. bld_quality_gate_slo_definition.md

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
| [[bld_memory_canary_config]] | sibling | 0.43 |
| [[bld_memory_data_contract]] | related | 0.36 |
| [[bld_memory_saga]] | sibling | 0.35 |
| [[bld_manifest_slo_definition]] | upstream | 0.35 |
| [[bld_memory_default]] | related | 0.34 |
