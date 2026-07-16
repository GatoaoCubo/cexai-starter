---
quality: null
quality: null
id: bld_memory_deployment_manifest
kind: knowledge_card
pillar: P10
title: "Memory: deployment_manifest Builder Patterns"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: deployment_manifest
tags: [memory, deployment_manifest, P09]
llm_function: INJECT
tldr: "Recalled patterns and corrections for deployment_manifest builder sessions."
8f: "F3_inject"
keywords: [deployment_manifest builder patterns, memory, deployment_manifest, persistent patterns, common corrections, context injection priority, related artifacts, user conflates, upstream, reference]
density_score: null
related:
  - bld_rules_deployment_manifest
  - bld_manifest_deployment_manifest
  - kc_deployment_manifest
  - bld_knowledge_card_deployment_manifest
  - bld_architecture_deployment_manifest
---
# Memory: deployment_manifest Builder

## Persistent Patterns
| Pattern | Frequency | Source |
|---------|-----------|--------|
| Always pin versions (never latest) | HIGH | Security + reproducibility requirement |
| Rollback_to must reference a known-good revision | HIGH | Recovery path mandatory |
| Secrets via reference, never inline | HIGH | Security gate H04 |
| artifacts_count must match list length | HIGH | Gate H06 |
| health_check_endpoint always required for services | MED | Gate H07 |

## Common Corrections
| Mistake | Correction |
|---------|-----------|
| User says "deploy latest" | Pin to current HEAD SHA or explicit semver |
| User omits rollback | Ask for prior stable version; default to N-1 |
| User writes secret value inline | Replace with vault path reference |
| User conflates with env_config | Redirect: env_config for runtime vars; deployment_manifest for what to deploy |
| User conflates with canary_config | Redirect: canary_config for traffic split; deployment_manifest for artifact spec |

## Context Injection Priority
1. bld_schema_deployment_manifest.md (always)
2. bld_examples_deployment_manifest.md (golden reference)
3. env_config KC (for config override context)
4. slo_definition KC (for post-deploy success criteria)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_rules_deployment_manifest]] | sibling | 0.37 |
| [[bld_manifest_deployment_manifest]] | upstream | 0.33 |
| [[kc_deployment_manifest]] | sibling | 0.30 |
| [[bld_knowledge_card_deployment_manifest]] | sibling | 0.30 |
| [[bld_architecture_deployment_manifest]] | sibling | 0.29 |
