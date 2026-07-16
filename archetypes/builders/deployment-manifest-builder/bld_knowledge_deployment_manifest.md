---
quality: null
quality: null
id: bld_knowledge_card_deployment_manifest
kind: knowledge_card
pillar: P01
title: "Knowledge Card: deployment_manifest"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: deployment_manifest
tags: [knowledge_card, deployment_manifest, P09]
llm_function: INJECT
tldr: "Domain knowledge for building deployment_manifest artifacts: patterns, anti-patterns, and decision rules."
8f: "F3_inject"
keywords: [knowledge card, and decision rules, knowledge_card, deployment_manifest, what it is, key patterns, why it fails, related artifacts, sibling, environment]
density_score: null
related:
  - kc_deployment_manifest
  - bld_manifest_deployment_manifest
  - bld_instruction_deployment_manifest
  - bld_quality_gate_deployment_manifest
  - bld_memory_deployment_manifest
---
# Knowledge Card: deployment_manifest

## What It Is
A deployment_manifest specifies WHAT artifacts to deploy, WHERE (environment/target), and HOW (configuration overrides, secrets, rollback). Industry analogs: Kubernetes manifest, Helm values.yaml, AWS CloudFormation template.

## When to Use
- Deploying one or more versioned artifacts to a known environment
- Encoding deployment configuration that differs from defaults
- Specifying rollback plan before triggering a deployment pipeline
- Documenting what was deployed (post-deploy audit trail)

## When NOT to Use
- Defining runtime environment variables in isolation -> use env_config
- Configuring a test/ephemeral environment -> use sandbox_spec
- Splitting traffic between versions -> use canary_config
- Defining contractual SLA with external parties -> use enterprise_sla

## Key Patterns
| Pattern | When | Notes |
|---------|------|-------|
| Blue-green | Zero-downtime swap | Two identical envs; switch traffic atomically |
| Rolling update | Gradual pod replacement | Reduces risk; slower than blue-green |
| Recreate | Simple stateless services | Downtime acceptable; simplest manifest |
| Pin versions | Always | Never use "latest" in production manifests |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Inline secrets | Security leak in version control | Reference secrets by vault path or k8s secret name |
| Missing rollback_to | No recovery path | Always specify prior revision or known-good version |
| "latest" tag | Non-reproducible deployments | Always pin exact version or SHA |
| No health check | Cannot detect failed deploy | Always specify health_check_endpoint |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_deployment_manifest]] | sibling | 0.45 |
| [[bld_manifest_deployment_manifest]] | downstream | 0.43 |
| [[bld_instruction_deployment_manifest]] | downstream | 0.32 |
| [[bld_quality_gate_deployment_manifest]] | downstream | 0.29 |
| [[bld_memory_deployment_manifest]] | sibling | 0.29 |
