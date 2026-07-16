---
quality: null
quality: null
kind: schema
id: bld_schema_terminal_backend
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for terminal_backend
title: "Schema Terminal Backend"
version: "1.0.0"
author: n03_engineering
tags: [terminal_backend, builder, schema]
tldr: "Formal schema for terminal_backend: 6 backend types, auth model, resource limits, cost model"
domain: "terminal_backend construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F1_constrain"
keywords: [terminal_backend construction, schema terminal backend, formal schema for terminal_backend, backend types, auth model, resource limits, cost model, terminal_backend, builder, schema]
density_score: 0.90
related:
  - bld_schema_sandbox_config
  - n00_terminal_backend_manifest
  - p09_qg_terminal_backend
  - bld_schema_reranker_config
  - bld_schema_sandbox_spec
---

## Frontmatter Fields

### Required
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string | Yes | - | Must match naming pattern |
| kind | string | Yes | - | Always "terminal_backend" |
| pillar | string | Yes | - | Always "P09" |
| title | string | Yes | - | Human-readable backend name |
| backend_type | enum | Yes | - | local \| docker \| ssh \| daytona \| modal \| singularity |
| serverless | bool | Yes | false | True only for modal, daytona |
| hibernation_capable | bool | Yes | false | True only for daytona |
| auth.method | enum | Yes | none | none \| ssh_key \| api_token \| oauth |
| auth.secret_ref | string | No | null | Points to secret_config id if auth.method != none |
| limits.timeout_seconds | integer | Yes | 3600 | Max session lifetime; cannot be null |
| cost_model.billing | enum | Yes | free | free \| per_second \| per_task \| subscription |
| version | string | Yes | "1.0.0" | Semantic versioning |
| quality | float\|null | Yes | null | Peer-review score; null until reviewed |
| tags | list | Yes | [] | Lowercase keywords |

### Optional
| Field | Type | Notes |
|-------|------|-------|
| limits.cpu_cores | integer | null = provider default |
| limits.memory_gb | float | null = provider default |
| cost_model.estimated_usd_per_hour | float | null if free or unknown |

## ID Pattern
`^p09_tb_[a-z0-9_-]+$`

## Backend-Specific Validation

| backend_type | auth.method allowed | serverless | hibernation_capable |
|--------------|---------------------|------------|---------------------|
| local | none | false | false |
| docker | none | false | false |
| ssh | ssh_key | false | false |
| daytona | api_token, oauth | true | true |
| modal | api_token | true | false |
| singularity | none, ssh_key | false | false |

## Body Structure
1. **Backend Overview** -- type, purpose, nucleus owner
2. **Connection** -- backend-specific connection config block
3. **Resource Limits** -- cpu, memory, timeout table
4. **Authentication** -- method and secret reference
5. **Cost Model** -- billing mode and estimated cost

## Constraints
- Max file size: 3072 bytes
- ID must match regex pattern
- `limits.timeout_seconds` is required and must be a positive integer
- `backend_type` must be one of the 6 supported values exactly
- `serverless: true` is only valid for modal and daytona
- Tags must be lowercase and unique

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_sandbox_config]] | sibling | 0.51 |
| [[n00_terminal_backend_manifest]] | downstream | 0.48 |
| [[p09_qg_terminal_backend]] | downstream | 0.48 |
| [[bld_schema_reranker_config]] | sibling | 0.47 |
| [[bld_schema_sandbox_spec]] | sibling | 0.46 |
