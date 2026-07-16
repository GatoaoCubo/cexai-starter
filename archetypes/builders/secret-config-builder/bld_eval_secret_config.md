---
kind: quality_gate
id: p11_qg_secret_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of secret_config artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: secret_config"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, secret-config, P09, credentials, rotation, encryption]
tldr: "Pass/fail gate for secret_config artifacts: provider validity, rotation policy completeness, encryption posture, access pattern, and no plaintext s..."
domain: "credential and secret management specification — provider, rotation policy, encryption posture, and access pattern"
created: "2026-03-29"
updated: "2026-03-29"
8f: "F7_govern"
keywords: [rotation policy, encryption posture, and access pattern, provider validity, rotation policy completeness, access pattern, and no plaintext secrets]
density_score: 0.90
---
## Quality Gate

# Gate: secret_config
## Definition
| Field | Value |
|---|---|
| metric | secret_config artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: secret_config` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p09_sec_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, or missing prefix |
| H03 | ID equals filename stem | `id: p09_sec_foo` but file is `p09_sec_bar.md` |
| H04 | Kind equals literal `secret_config` | `kind: config` or `kind: env_config` or any other value |
| H05 | Quality field is null | `quality: 7.5` or any non-null value |
| H06 | All required fields present | Missing `provider`, `rotation_policy`, `encryption`, or `access_pattern` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Rotation policy completeness | 1.0 | frequency, method, trigger, and rollback all defined |
| Encryption specificity | 1.0 | Algorithm named (AES-256-GCM, not just "encrypted") |
| Access pattern documentation | 1.0 | Step-by-step retrieval instructions in body |
| Secret path completeness | 0.5 | All relevant paths listed as placeholders |
| Lease and TTL definition | 0.5 | lease_duration set when access_pattern == dynamic |
| Audit log posture | 1.0 | audit_log declared; justification provided if false |
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
| conditions | Internal development stub only, never used in production agents |
| approver | Author self-certification with comment explaining dev-only scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 7d — secret configs must reach >= 7.0 or be removed (shorter than cli_tool — security risk) |
| never_bypass | H01 (unparseable YAML), H05 (self-scored artifacts), H10 (plaintext secrets — immediate security violation) |

## Examples

# Examples: secret-config-builder
## Golden Example
INPUT: "Create secret config for OpenAI and Anthropic API keys used by research_agent research agent, stored in HashiCorp Vault with daily rotation"
OUTPUT:
```yaml
id: p09_sec_llm_api_keys
kind: secret_config
pillar: P09
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "LLM API Keys — research_agent Research Agent"
provider: vault
rotation_policy:
  frequency: daily
  method: automatic
encryption:
  at_rest: AES-256-GCM
  in_transit: TLS 1.3
access_pattern: dynamic
quality: 8.9
tags: [secret_config, vault, llm-keys, P09]
tldr: "Vault-backed LLM API keys for research_agent with daily auto-rotation and dynamic leases"
description: "Manages OpenAI and Anthropic API keys for research_agent research agent via Vault dynamic secrets"
secret_paths:
  - "secret/data/agents/shaka/openai"
  - "secret/data/agents/shaka/anthropic"
lease_duration: "1h"
audit_log: true
namespaces: ["agents/shaka"]
fallback: "env"
```
## Overview
Manages LLM provider API keys (OpenAI, Anthropic) for the research_agent research agent.
Keys rotate daily via Vault auto-rotation; research_agent retrieves a short-lived lease at task start.
## Provider
Backend: HashiCorp Vault — AppRole auth (role_id + secret_id injected at boot)
Paths:
- `secret/data/agents/shaka/openai` — OpenAI API key (sk-<PLACEHOLDER>)
- `secret/data/agents/shaka/anthropic` — Anthropic API key (sk-ant-<PLACEHOLDER>)
AppRole role: `agents-shaka-reader` (read-only on `secret/data/agents/shaka/*`)
## Rotation Policy
- Frequency: daily (00:00 UTC)
- Method: automatic (Vault rotation Lambda)
- Trigger: schedule + on-breach (PagerDuty webhook)
- Rollback: previous version retained for 2h in Vault KV v2 history
## Access Pattern
Pattern: dynamic — research_agent requests a lease-bound token at task start via AppRole login.
1. Boot: inject role_id + secret_id via K8s init container
2. Task start: `vault write auth/approle/login role_id=<PLACEHOLDER> secret_id=<PLACEHOLDER>`
3. Read: `vault kv get secret/data/agents/shaka/openai`
4. Lease TTL: 1h — renewed if task exceeds TTL
Fallback: env injection (OPENAI_API_KEY env var) if Vault unreachable

WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p09_sec_ pattern (H02 pass)
- kind: secret_config (H04 pass)
- provider is valid enum: vault (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
