---
quality: null
quality: null
id: bld_schema_deployment_manifest
kind: schema
pillar: P06
llm_function: CONSTRAIN
purpose: "Formal schema -- SINGLE SOURCE OF TRUTH for deployment_manifest"
pattern: "TEMPLATE derives from this. CONFIG restricts this."
title: "Schema: deployment_manifest"
version: "1.0.0"
author: builder
tags:
  - "schema"
  - "deployment_manifest"
  - "P09"
domain: "deployment configuration"
created: "2026-04-17"
updated: "2026-04-17"
tldr: "Formal schema -- SINGLE SOURCE OF TRUTH for deployment_manifest"
8f: "F1_constrain"
keywords:
  - "deployment configuration"
  - "schema"
  - "deployment_manifest"
  - "^p09_dm_[a-z][a-z0-9_]+$"
  - "## artifacts"
  - "## target environment"
  - "## config overrides"
  - "## rollback strategy"
  - "frontmatter fields"
  - "pattern regex"
density_score: null
related:
  - bld_schema_usage_report
  - bld_schema_search_strategy
  - bld_schema_quickstart_guide
  - bld_schema_pitch_deck
  - bld_schema_reranker_config
---

# Schema: deployment_manifest

## Frontmatter Fields
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p09_dm_{name_slug}) | YES | - | Namespace compliance |
| kind | literal "deployment_manifest" | YES | - | Type integrity |
| pillar | literal "P09" | YES | - | Pillar assignment |
| version | semver string | YES | "1.0.0" | Version |
| manifest_name | string | YES | - | Human-readable name |
| target_env | enum: staging, production, preview | YES | - | Deployment target |
| artifacts_count | integer | YES | - | Must match artifact list |
| rollback_to | string | YES | - | Prior revision to revert to |
| domain | string | YES | - | System/service domain |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | - | Must include "deployment_manifest" |
| tldr | string <= 160ch | YES | - | Dense summary |
| created | date YYYY-MM-DD | YES | - | Creation date |
| updated | date YYYY-MM-DD | YES | - | Last update |
| author | string | YES | - | Producer identity |

## ID Pattern
Regex: `^p09_dm_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem.

## Body Structure (required sections)
1. `## Artifacts` -- table: name, version, checksum, source
2. `## Target Environment` -- environment, namespace, region, cluster
3. `## Config Overrides` -- env_vars table, secrets list
4. `## Rollback Strategy` -- rollback_to, trigger condition, health_check

## Constraints
- max_bytes: 4096 (body only)
- naming: p09_dm_{name_slug}.md
- machine_format: yaml (frontmatter) + markdown (body)
- id == filename stem
- artifacts_count MUST match actual artifact entries
- NO inline secret values -- reference only
- NO "latest" version tags
- quality: null always

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_usage_report]] | sibling | 0.61 |
| [[bld_schema_search_strategy]] | sibling | 0.60 |
| [[bld_schema_quickstart_guide]] | sibling | 0.60 |
| [[bld_schema_pitch_deck]] | sibling | 0.59 |
| [[bld_schema_reranker_config]] | sibling | 0.59 |
