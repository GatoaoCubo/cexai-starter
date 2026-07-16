---
quality: null
quality: null
id: bld_knowledge_card_canary_config
kind: knowledge_card
pillar: P01
title: "Knowledge Card: canary_config"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: canary_config
tags: [knowledge_card, canary_config, P09]
llm_function: INJECT
tldr: "Domain knowledge for canary_config: traffic stages, rollback triggers, Argo Rollouts, Flagger."
8f: "F3_inject"
keywords: [knowledge card, domain knowledge for canary_config, traffic stages, rollback triggers, argo rollouts, knowledge_card, canary_config, what it is, standard traffic stages, typical pause]
density_score: null
related:
  - kc_canary_config
  - bld_manifest_canary_config
  - bld_instruction_canary_config
  - bld_quality_gate_canary_config
  - bld_tools_canary_config
---
# Knowledge Card: canary_config

## What It Is
A canary_config specifies how to gradually shift traffic from a stable version to a new canary version, with automatic rollback if defined metrics breach thresholds. Named after the "canary in a coal mine" practice: expose a small subset of traffic to the new version first.

## Standard Traffic Stages
| Stage | Canary % | Stable % | Typical Pause |
|-------|---------|---------|---------------|
| Initial | 5% | 95% | 10 min |
| Phase 1 | 25% | 75% | 15 min |
| Phase 2 | 50% | 50% | 20 min |
| Full | 100% | 0% | N/A (complete) |

## Rollback Trigger Metrics
| Metric | Typical Threshold | Notes |
|--------|-----------------|-------|
| error_rate | > 1% | HTTP 5xx / total requests |
| latency_p99_ms | > 500 | 99th percentile response time |
| cpu_utilization | > 80% | Canary pod CPU |
| slo_breach | any | Link to slo_definition |

## Provider Comparison
| Provider | Platform | Key Feature |
|----------|---------|-------------|
| Argo Rollouts | Kubernetes | Native k8s controller; analysis templates |
| Flagger | Kubernetes | Istio/Linkerd mesh integration |
| AWS CodeDeploy | AWS | Lambda + EC2 canary deployments |
| Custom | Any | Manual metric check + rollback script |

## Anti-Patterns
| Anti-Pattern | Fix |
|-------------|-----|
| Jumping to 50% immediately | Start at 5%; risk is proportional to traffic |
| No rollback trigger | Always define at least 1 metric threshold |
| Canary = feature flag | Canary splits traffic; feature flag toggles feature |
| Canary = A/B test | A/B uses statistics; canary uses metric threshold |

## Knowledge Injection Checklist

- Verify domain facts are sourced and citable
- Validate density_score >= 0.85 (no filler content)
- Cross-reference with related KCs for consistency
- Check for outdated facts that need refresh

## Injection Pattern

```yaml
# KC injection at F3
source: verified
density: 0.85+
cross_refs: checked
freshness: current
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_retriever.py --query "{DOMAIN}"
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_canary_config]] | sibling | 0.48 |
| [[bld_manifest_canary_config]] | downstream | 0.45 |
| [[bld_instruction_canary_config]] | downstream | 0.43 |
| [[bld_quality_gate_canary_config]] | downstream | 0.39 |
| [[bld_tools_canary_config]] | sibling | 0.36 |
