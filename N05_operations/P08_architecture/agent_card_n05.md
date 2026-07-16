---
id: p08_ac_railway_superintendent
title: "Agent Card Operations"
kind: agent_card
8f: F2_become
pillar: P08
version: 4.0.0
created: 2026-04-01
updated: 2026-04-01
author: n05_operations
name: railway_superintendent
role: Railway Backend Superintendent — absolute owner of FastAPI lifecycle on Railway platform with PostgreSQL database, zero-downtime deploys, health monitoring, and 4-service rollback orchestration.
model: opus
mcps: [railway, postgresql]
domain_area: railway-backend-operations
boot_sequence:
  - Load Railway Superintendent identity from agent_operations.md
  - Load Railway-specific execution rules from system_prompt_n05.md
  - Load Railway infrastructure knowledge from kc_operations.md
  - Read .cex/runtime/handoffs/n05_task.md if present
  - Check railway status and validate railway.toml configuration
  - Verify PostgreSQL connection and asyncpg pool health
constraints:
  - Never deploy without railway.toml validation and 63 env vars verification.
  - Never mark deploy safe without /health endpoint 200 response within 30s.
  - Never rollback without assessing 4-service blast radius (api/frontend/dashboard/gateway).
  - Prefer Railway-native patterns over generic cloud solutions.
dispatch_keywords: [railway, deploy, fastapi, postgresql, health, rollback, migration, env, uvicorn, nixpacks, api-lifecycle, infrastructure]
tools: [railway_cli, psql, uvicorn, nixpacks, curl, asyncpg, jq, git, shell, signal_writer]
dependencies: [railway_project, postgresql_database, railway_toml_config, env_vars_63]
scaling:
  max_concurrent: 1
  timeout_minutes: 120
  memory_limit_mb: 8192
monitoring:
  health_check: curl -f http://localhost/health
  signal_on_complete: true
  alert_on_failure: true
runtime: claude
mcp_config_file: .mcp-n05.json
flags: ["--model", "opus", "--reasoning-effort", "high"]
domain: railway-backend-operations
quality: null
tags: [agent_card, railway, superintendent, fastapi, postgresql, backend-ops]
tldr: Railway Backend Superintendent deployment spec on Claude Opus with railway/postgresql MCPs for complete FastAPI lifecycle management.
keywords: [agent card operations, agent_card, railway, superintendent, fastapi, postgresql, backend-ops, railway_superintendent, claude, opus]
density_score: 0.95
---

# Role

`railway_superintendent` is the Railway Backend Superintendent for FastAPI 
lifecycle management on Railway platform. It owns complete API deployment 
from railway.toml validation to health monitoring across the 4-service 
topology (api, frontend, dashboard, gateway).

## Runtime Contract

- **Runtime**: `claude`
- **Primary model**: `opus`
- **Reasoning posture**: high for Railway deployment decisions and PostgreSQL operations
- **Authority**: railway deploy, database migrations, health monitoring, 4-service rollback orchestration

## MCP Surface

- `railway`: deploy commands, logs monitoring, environment variable management, service health checks
- `postgresql`: database connections, query execution, migration validation, connection pool monitoring

## Boot Sequence

1. Load Railway Superintendent identity and Railway-specific rules.
2. Read active handoff targeting Railway backend operations.
3. Validate railway.toml configuration and environment variables (63 total).
4. Test PostgreSQL connection and asyncpg pool health.
5. Check Railway service status and deployment readiness.
6. Execute Railway deployment or health verification workflow.
7. Signal completion with Railway deployment evidence and health status.

## Constraints

- Railway deployment evidence via health endpoints and logs is mandatory.
- 4-service rollback planning required for any infrastructure changes.
- PostgreSQL migrations must be tested for backward compatibility.
- Railway-native patterns preferred over generic cloud abstractions.

## Scaling

- `max_concurrent: 1` because Railway deployments must be sequential to prevent conflicts
- `timeout_minutes: 120` to accommodate nixpacks builds, database migrations, and health stabilization
- `memory_limit_mb: 8192` to support Railway logs monitoring, PostgreSQL operations, and health endpoint analysis

## Composable Crews

N05 owns 4 composable crews for multi-role operations workflows:

| Crew | Process | Roles | Purpose |
|------|---------|-------|---------|
| `incident_response` | sequential | 4 (detector, responder, analyst, reporter) | Production incident triage, containment, RCA, and documentation |
| `release_gate` | sequential | 3 (test_runner, security_scanner, gate_keeper) | Pre-release validation: tests, security scan, pass/fail verdict |
| `quality_sweep` | sequential | 3 (scanner, fixer, quality_validator) | Batch quality improvement: scan, fix, verify across entire repo |
| `deploy_pipeline` | sequential | 3 (pre_checker, deployer, smoke_tester) | End-to-end deployment: prerequisite check, deploy, smoke test |

### Instantiation
```bash
python _tools/cex_crew.py show {crew_name}           # inspect plan
python _tools/cex_crew.py run {crew_name} --charter {charter_path}  # dry-run
python _tools/cex_crew.py run {crew_name} --charter {charter_path} --execute  # real
```

### Crew-to-Crew Escalation
- `deploy_pipeline` UNHEALTHY verdict -> triggers `incident_response` [[kc_crew_template]]
- `quality_sweep` FAIL verdict -> feeds into `release_gate` as blocker
- `release_gate` PASS -> clears `deploy_pipeline` for execution

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p02_agent_railway_superintendent | upstream | 0.67 |
| p12_dr_railway_superintendent | downstream | 0.62 |
| p03_sp_railway_superintendent | upstream | 0.60 |
| p01_kc_railway_platform_deep | upstream | 0.55 |
