---
kind: quality_gate
id: p11_qg_env_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of env_config artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: env_config"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, env-config, environment-variables, secrets, configuration, P11]
tldr: "Gates for env_config artifacts: validates variable catalog completeness, sensitive masking, default correctness, override precedence, and scope acc..."
domain: "env_config — environment variable specifications with scope, validation rules, and sensitive var handling"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords: [validation rules, and sensitive var handling, gates for env_config artifacts, validates variable catalog completeness, sensitive masking, default correctness, override precedence]
density_score: 0.92
related:
  - env-config-builder
  - bld_schema_env_config
---
## Quality Gate

# Gate: env_config
## Definition
| Field     | Value |
|-----------|-------|
| metric    | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator  | AND (all HARD) + weighted_sum (SOFT) |
| scope     | All artifacts where `kind: env_config` |
## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID  | Check | Failure message |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p09_env_[a-z][a-z0-9_]+$` | "ID fails env_config namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"env_config"` | "Kind is not 'env_config'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, domain, scope, variables, override_precedence, version, created, author, tags | "Missing required field(s)" |
## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Validation rules completeness | 1.0 | Each variable has regex, enum, or range validation defined |
| Sensitive variable masking | 1.0 | All sensitive vars have masking_rule (partial/full redaction) specified |
| Default value quality | 1.0 | Non-sensitive defaults are safe, functional, and documented |
| Scope accuracy | 1.0 | Scope (global/agent_group/service) correctly categorizes all variables |
| Type specificity | 0.5 | Types beyond string used where apownte (int, bool, url, path) |
| Boundary clarity | 0.5 | Explicitly not boot_config (provider startup), feature_flag (toggle), path_config |
Weight sum: 1.0+1.0+1.0+1.0+0.5+0.5+1.0+1.0+0.5+1.0+1.0+0.5 = 10.0 (100%)
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool as golden exemplar |
| >= 8.0 | PUBLISH | Publish to pool |
| >= 7.0 | REVIEW | Flag for human review before publish |
| < 7.0  | REJECT | Return to author with failure report |
## Bypass
| Field | Value |
|-------|-------|
| conditions | New service bootstrapping where full variable catalog is not yet known |
| approver | Security/infra owner approval required (written); sensitive vars never bypassed |

## Examples

# Examples: env-config-builder
## Golden Example
INPUT: "Define environment variables for the API service scope"
OUTPUT:
```yaml
id: p09_env_api_service
kind: env_config
pillar: P09
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
scope: "api_service"
variables:
  - DATABASE_URL
  - API_PORT
  - LOG_LEVEL
  - JWT_SECRET_KEY
quality: 8.9
tags: [env_config, api, service, P09, configuration]
tldr: "API service env: 8 vars (2 sensitive), port 8000, structured logging, JWT auth"
description: "Environment variables for the API service including database, auth, logging, and cache config"
environment: all
sensitive_count: 2
override: "env var > .env file > default"
validation: "type check + format validation per variable"
```
## Overview
Environment variables for the API service covering database, authentication, logging, and cache.
Consumed by FastAPI application at startup; missing required vars block boot.
## Variable Catalog
| Variable | Type | Required | Default | Sensitive | Validation |
|----------|------|----------|---------|-----------|------------|
| DATABASE_URL | url | yes | - | yes | postgresql:// prefix |
| API_PORT | integer | no | 8000 | no | range 1024-65535 |
| LOG_LEVEL | string | no | INFO | no | enum: DEBUG, INFO, WARNING, ERROR |
| JWT_SECRET_KEY | secret | yes | - | yes | min 32 chars, alphanumeric |
| CORS_ORIGINS | string | no | "*" | no | comma-separated URLs or "*" |
| MAX_CONNECTIONS | integer | no | 20 | no | range 1-100 |
## Override Precedence
Standard 3-tier override for all variables:
1. Environment variable set in shell/container (highest priority)
2. Value in .env file (loaded by python-dotenv)
3. Default value from this spec (lowest priority)
Required variables with no default MUST be set via tier 1 or 2; missing = startup failure.
## Sensitive Variables
- DATABASE_URL: mask after `://` in logs — store in secrets manager or encrypted .env
- JWT_SECRET_KEY: never log, never commit — generate with `openssl rand -hex 32`
All sensitive vars: excluded from debug output, masked in error reports, rotatable without restart.
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p09_env_ pattern (H02 pass)
- kind: env_config (H04 pass)
- 19 required+recommended fields present (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
