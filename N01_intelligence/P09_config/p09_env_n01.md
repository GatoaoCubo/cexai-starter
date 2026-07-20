---
id: p09_env_n01
kind: env_config
pillar: P09
nucleus: n01
title: N01 Environment Config
version: 1.0
quality: null
tags: [env_config, runtime, research, governance]
keywords: [env config, research runtime, evidence governance, comparative research, triangulated evidence, counter signals, provider api key ref]
density_score: 1.0
related:
  - p09_rl_n01
  - api_reference_research_apis
  - nucleus_def_n01
  - dispatch_rule_n01
  - p04_retr_n01
updated: "2026-07-20"
---

<!-- 8F: F1 constrain=P09/env_config F4 reason=honest split between a proposed evidence-governance config surface and the real env vars that govern N01 boot today F8 collaborate=N01_intelligence/P09_config/p09_env_n01.md -->

## Purpose

| Item | Decision |
|------|----------|
| Scope | N01 research runtime and evidence governance |
| Environment | all |
| Lens | Analytical Envy uses env config to bias research runs toward explicit comparison and source quality |
| Override rule | environment variable > local file > default (design intent for the `N01_*` table below -- see Status Note) |
| Secret policy | sensitive values appear as refs only, never literal secrets |
| Implementation status | **design-intent** for the 12 `N01_*` vars below -- treat as a target shape for a future evidence-governance layer, not a wired one. Real, live-wired vars are documented separately below. |

## Status Note

| Question | Answer |
|----------|--------|
| Are any of the 12 `N01_*` vars below read by code today? | Not by default -- they describe a proposed evidence-governance config surface. Before relying on any of them, grep your own tree for the exact variable name to confirm current wiring status. |
| How does N01 actually pick its provider/model at boot? | `.cex/config/nucleus_models.yaml` `n01:` block (`cli`, `model`, `fallback_chain`), resolved by `boot/_shared/resolve_model.ps1` at boot time -- an entirely different, YAML-driven mechanism with zero `N01_*` env var involvement. |
| So what is the Values table below? | A documented design surface for an env-var-driven evidence-governance layer. Kept as a coherent target (not deleted) in case you choose to wire it -- struck/unwired rows should stay marked as such, not silently implied as live. |
| What DOES actually vary N01's runtime via real env vars? | See "Real Environment Variables" below -- generic `CEX_*` infra vars N01 shares with every nucleus, plus whatever MCP research-tool keys your own deployment wires up. |

## Values (DESIGN-INTENT -- verify wiring before relying on any row)

| Variable | Type | Required | Default | Sensitive | Validation | Wired? |
|---------|------|----------|---------|-----------|------------|--------|
| `N01_DEFAULT_PROVIDER` | string | yes | `anthropic` | no | enum `openai\|anthropic\|router` | verify in your tree |
| `N01_DEFAULT_MODEL` | string | yes | (your provider's current model id) | no | non-empty | verify in your tree |
| `N01_RESEARCH_MODE` | string | yes | `comparative` | no | enum `comparative\|paper\|market\|audit` | verify in your tree |
| `N01_MIN_PRIMARY_SOURCES` | integer | yes | `2` | no | range `1..10` | verify in your tree |
| `N01_EVIDENCE_TARGET` | string | yes | `triangulated` | no | enum from research evidence state | verify in your tree |
| `N01_MAX_RESULTS_PER_SCAN` | integer | no | `12` | no | range `3..50` | verify in your tree |
| `N01_TIME_HORIZON_DAYS` | integer | no | `90` | no | range `1..365` | verify in your tree |
| `N01_BUDGET_TOKENS_DAY` | integer | no | `120000` | no | range `10000..500000` | verify in your tree |
| `N01_ENABLE_COUNTER_SIGNALS` | boolean | no | `true` | no | boolean only | verify in your tree |
| `N01_RUN_CONTEXT_PATH` | string | no | `.cex/runtime` | no | relative path | verify in your tree |
| `N01_PROVIDER_API_KEY_REF` | string | yes | `sec_n01_llm_provider` | yes | `^sec_[a-z0-9_]+$` | verify in your tree |
| `N01_TRACING_ENABLED` | boolean | no | `true` | no | boolean only | verify in your tree |

## Variable Roles

Design intent for each `N01_*` variable above, IF it is wired in your deployment:

| Variable | Runtime Role | Competitive Effect |
|---------|--------------|--------------------|
| `N01_DEFAULT_PROVIDER` | chooses base provider | affects speed and comparative cost |
| `N01_DEFAULT_MODEL` | default model route | affects depth of synthesis |
| `N01_RESEARCH_MODE` | sets task posture | determines whether envy is broad or narrow |
| `N01_MIN_PRIMARY_SOURCES` | proof floor | reduces vanity analysis |
| `N01_EVIDENCE_TARGET` | stopping threshold | keeps output from pretending certainty |
| `N01_MAX_RESULTS_PER_SCAN` | breadth control | balances coverage vs noise |
| `N01_TIME_HORIZON_DAYS` | freshness bound | prevents stale benchmark worship |
| `N01_BUDGET_TOKENS_DAY` | cost cap | stops deep research from becoming waste |
| `N01_ENABLE_COUNTER_SIGNALS` | contradiction search toggle | makes envy rigorous instead of one-sided |
| `N01_RUN_CONTEXT_PATH` | runtime path anchor | keeps tool state predictable |
| `N01_PROVIDER_API_KEY_REF` | secret pointer | clean separation from secret config |
| `N01_TRACING_ENABLED` | audit logging | supports post hoc governance |

## Override Precedence

Design intent only (applies to the unwired `N01_*` table -- not verified as implemented):

| Priority | Source | Why |
|---------|--------|-----|
| 1 | process environment | deploy-time truth |
| 2 | `.env.local` or runner file | developer convenience |
| 3 | frontmatter default in this artifact | documented baseline |

## Sensitive Handling

| Variable | Exposure Rule | Storage Guidance |
|---------|---------------|------------------|
| `N01_PROVIDER_API_KEY_REF` | log pointer only, never the literal secret | resolve via your own secret-config artifact / vault |
| `N01_DEFAULT_PROVIDER` | safe to log | useful for debugging routes |
| `N01_DEFAULT_MODEL` | safe to log | useful for benchmark audits |

## Rationale

Design reasoning for the proposed (unwired) `N01_*` surface -- still a coherent target if it is ever built:

| Design Choice | Why | Analytical Envy Interpretation |
|--------------|-----|--------------------------------|
| Evidence target in env | lets runtime bias all requests upward | environment can institutionalize proof pressure |
| Counter-signal toggle | contradiction search should be a first-class behavior | envy must test itself against rival evidence |
| Model and provider split | route quality and cost independently | lets N01 compare depth and spend cleanly |
| Secret as ref only | keeps config auditable and non-leaky | rigor includes operational hygiene |
| Daily token budget | depth must answer to cost | disciplined envy spends where advantage matters |

## Real Environment Variables (Live, Verified Against This Repo's Boot Scripts)

These are the environment variables that actually affect an N01 run today, a
different namespace from the `N01_*` design table above.

### Generic infra (shared by every nucleus, not N01-specific)

| Variable | Effect | Evidence |
|----------|--------|----------|
| `CEX_NUCLEUS` | identifies the running nucleus for tools, signals, cost-tracking | `boot/n01.ps1` (sets `N01`) |
| `CEX_ROOT` | repo root anchor for all path resolution | `boot/n01.ps1` |
| `CEX_TENANT_ID` | tenant-scoped handoff path (`.cex/tenants/<tid>/runtime/handoffs/` instead of the central path) | `boot/n01_codex.ps1`, `boot/n01_gemini.ps1`, `boot/n01_litellm.ps1`, `boot/n01_ollama.ps1` |
| `CEX_GRID` | skips solo-mode console buffer/size setup (grid dispatch controls sizing instead) | `boot/n01_codex.ps1`, `boot/n01_gemini.ps1` |
| `CEX_MODEL_OVERRIDE` | overrides the YAML-resolved model for a single run | `boot/n01.ps1`, `boot/n01_gemini.ps1` |
| `OLLAMA_MODEL` | overrides the default local model (`qwen3:8b`) on the Ollama runtime variant | `boot/n01_ollama.ps1` |
| `LITELLM_BASE_URL` | overrides the LiteLLM proxy URL (default `http://localhost:4000`) | `boot/n01_litellm.ps1` |

### N01-specific (research MCP stack)

If your deployment wires MCP research tools (web search, academic, github
lookups, etc.) for N01, their API keys follow the same convention as the
generic infra vars above: a repo-root `.env` file (or your process
environment) supplies the value, and the relevant `.mcp*.json` overlay
references it as a `${VAR}` placeholder. This repo does not ship a
pre-wired `.mcp-n01.json` -- add one (gitignored) if your deployment needs
live MCP research tools, and name its keys to match whatever provider you
choose (see `api_reference_research_apis.md` for source categories worth
wiring first).

### Secret handling reality check

The REAL mechanism for every credential in this repo, N01 included, is the
plain `.env` + process-environment + `${VAR}`-placeholder pattern described
in the table above. Do not point `N01_PROVIDER_API_KEY_REF` (or any
`sec_*` ref) at a vault backend unless you have actually built one --
document what exists, not what was once proposed.

## Example (illustrative only -- not consumed by any process; see Status Note)

```env
N01_DEFAULT_PROVIDER=anthropic
N01_DEFAULT_MODEL=claude-sonnet-5
N01_RESEARCH_MODE=comparative
N01_MIN_PRIMARY_SOURCES=3
N01_EVIDENCE_TARGET=benchmark_mapped
N01_MAX_RESULTS_PER_SCAN=10
N01_TIME_HORIZON_DAYS=45
N01_BUDGET_TOKENS_DAY=180000
N01_ENABLE_COUNTER_SIGNALS=true
N01_RUN_CONTEXT_PATH=.cex/runtime
N01_PROVIDER_API_KEY_REF=sec_n01_llm_provider
N01_TRACING_ENABLED=true
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `env_config` |
| Pillar | `P09` |
| Nucleus | `n01` |
| Environment | `all` |
| `N01_*` Variables Documented | `12` |
| `N01_*` Variables Wired | verify against your own tree before relying on any |
| Real Live Vars (different namespace) | `7` generic `CEX_*`/runtime vars, verified against this repo's boot scripts |
| Sensitive Count | `1` (design-intent) |
| Override Model | `env > file > default` (design-intent, unverified for the `N01_*` table) |
| Quality Field | `null` |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p09_rl_n01]] | sibling | 0.32 |
| [[api_reference_research_apis]] | related | 0.31 |
| [[nucleus_def_n01]] | related | 0.28 |
| [[dispatch_rule_n01]] | related | 0.26 |
| [[p04_retr_n01]] | related | 0.25 |
