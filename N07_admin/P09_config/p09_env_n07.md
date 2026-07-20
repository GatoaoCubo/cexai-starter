---
id: p09_env_n07
kind: env_config
pillar: P09
title: "Orchestrator Env Contract"
version: "1.0.0"
quality: null
tags: [config, env, orchestration, dispatch, session]
8f: F1_constrain
nucleus: n07
domain: orchestration
created: "2026-07-20"
tldr: "The environment variables an orchestrator nucleus requires for session bootstrap, dispatch, wave planning, and mission control -- fail closed on identity/path/credential vars, warn only on budget vars."
related:
  - bld_schema_env_config
  - p12_wf_admin_orchestration
---

# Orchestrator Env Contract

## Purpose

Defines the environment variables required for orchestration, dispatch, wave
planning, and mission control. Sloth lens: minimal required config, maximum
leverage -- every variable earns its place by preventing a class of failure.
Fail closed on missing identity/path vars; warn only on budget vars.

## Values

| Variable | Type | Required | Sensitive | Default | Action On Failure |
|---|---|---|---|---|---|
| CEX_NUCLEUS | string | yes | no | `n07` | Abort: wrong nucleus booted |
| CEX_SESSION_ID | string | yes | no | auto-generated | Abort: session cannot be tracked |
| CEX_DISPATCH_MODE | string | yes | no | `solo` | Abort: unknown topology (`solo\|grid\|crew\|swarm`) |
| CEX_MAX_CONCURRENT | integer | yes | no | `6` | Cap at 6; do not abort |
| CEX_WAVE_TIMEOUT_SEC | integer | yes | no | `1800` | Use default; warn operator |
| CEX_MISSION_BUDGET_TOKENS | integer | no | no | `500000` | Warn only; do not block dispatch |
| CEX_HANDOFF_DIR | string | yes | no | `.cex/runtime/handoffs/` | Abort: handoffs cannot be written |
| CEX_SIGNAL_DIR | string | yes | no | `.cex/runtime/signals/` | Abort: completion signals unreadable |
| ANTHROPIC_API_KEY | string | yes | YES | none | Abort: no provider credential available |

## Precedence

1. Runtime environment variable (shell export, container env, CI secret injection) -- highest
2. `.env` file at repo root -- mid; loaded by bootstrap, never committed with secrets
3. Compiled default in this artifact -- lowest; never overrides explicit operator input

Required vars with no default MUST be supplied at tier 1 or 2. Absence at boot
time is an immediate abort, not a warning.

## Resolution Rules

| Rule | Sloth Effect |
|---|---|
| Identity first | Validate nucleus + session vars before any dispatch call |
| Path pre-flight | Check all path vars exist and are writable before writing a handoff |
| Concurrency cap | Over-limit silently caps to 6 and logs a warning |
| Secret masking | The provider credential is redacted in all logs, signals, and handoffs |
| Budget soft gate | Approaching budget triggers a warn-only log; dispatch continues |

## Example

```env
CEX_NUCLEUS=n07
CEX_SESSION_ID={{nucleus}}-{{iso_date}}-{{seq}}
CEX_DISPATCH_MODE=grid
CEX_MAX_CONCURRENT=6
CEX_WAVE_TIMEOUT_SEC=1800
CEX_HANDOFF_DIR=.cex/runtime/handoffs/
CEX_SIGNAL_DIR=.cex/runtime/signals/
```

## Related Artifacts

| Artifact | Relationship |
|----------|---------------|
| [[bld_schema_env_config]] | upstream -- the kind schema this contract instantiates |
| [[p12_wf_admin_orchestration]] | downstream -- the workflow this config gates at boot |
