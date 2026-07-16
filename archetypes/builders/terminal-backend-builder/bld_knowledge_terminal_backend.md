---
kind: knowledge_card
id: bld_kc_terminal_backend
pillar: P01
llm_function: INJECT
purpose: Linked KC reference for terminal_backend builder
quality: null
title: "Knowledge Card Link: Terminal Backend"
version: "1.0.0"
author: n03_engineering
tags: [terminal_backend, builder, knowledge_card]
tldr: "Pointer to kc_terminal_backend.md -- Honcho-adjacent execution backend abstraction "
domain: "terminal_backend construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F3_inject"
keywords: [terminal_backend construction, knowledge card link, terminal backend, pointer to kc_terminal_backend, terminal_backend, builder, knowledge_card, environments/, serverless: true, hibernation_capable: true]
density_score: 0.88
related:
 - terminal-backend-builder
 - bld_architecture_terminal_backend
---

## Primary KC
`N00_genesis/P01_knowledge/library/kind/kc_terminal_backend.md`

## Key Facts for Builder
- 6 supported backends: local, docker, ssh, daytona, modal, singularity
- Origin: multi-agent `environments/` directory
- No code changes required to switch backends -- YAML only
- `serverless: true` is ONLY valid for modal and daytona
- `hibernation_capable: true` is ONLY valid for daytona
- Boundary: terminal_backend = WHERE; sandbox_config = HOW isolated; env_config = WHAT vars

## Related KCs

| KC | Pillar | Relationship |
|----|--------|-------------|
| `kc_sandbox_config` | P09 | Security isolation wrapping terminal session |
| `kc_env_config` | P09 | Env vars injected into terminal session |
| `kc_secret_config` | P09 | Credentials for auth.secret_ref |
| `kc_runtime_rule` | P09 | Timeout/retry rules applied to session |

## Upstream Sources
- multi-agent: `environments/` directory, 6 backend definitions
- design spec: "Six Supported Backends: Local / Docker / SSH / Daytona / Singularity / Modal"

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[terminal-backend-builder]] | downstream | 0.41 |
| [[bld_architecture_terminal_backend]] | downstream | 0.30 |
