---
kind: quality_gate
id: p11_qg_model_provider
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of model_provider artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Model Provider"
version: "1.0.0"
author: builder_agent
tags: [quality-gate, model-provider, llm-routing, P02, fallback]
tldr: "Quality gate for model_provider artifacts: enforces tiered models, rate limits, fallback chain, and provider authentication fields."
domain: model_provider
created: "2026-04-06"
updated: "2026-04-06"
8f: "F7_govern"
density_score: 0.87
related:
  - model-provider-builder
---
## Quality Gate

# Gate: Model Provider
## Definition
A `model_provider` is a connection and routing configuration for an LLM API: provider, tiered models (fast/balanced/quality), rate limits (RPM/TPM), fallback chain, and authentication. Infrastructure artifact only — not a tutorial. Gates ensure model IDs are current, rate limits are documented, and fallback chains are complete.
## HARD Gates
All HARD gates must pass. Any single failure sets score to 0 and blocks publish.
| ID  | Check | Failure consequence |
|-----|-------|---------------------|
| H01 | YAML frontmatter parses without error | Artifact unparseable by tooling |
| H02 | `id` matches `^p02_mp_[a-z][a-z0-9_]+$` | Namespace violation — not discoverable |
| H03 | `id` equals filename stem exactly | Brain search failure — id/file mismatch |
| H04 | `kind` == literal string `"model_provider"` | Type integrity failure |
| H05 | `quality` == `null` | Self-scoring violation — pool metric corruption |
| H06 | Required fields present: `id`, `kind`, `pillar`, `version`, `created`, `updated`, `author`, `provider`, `models`, `api_key_env`, `rate_limit_rpm`, `tags`, `tldr` | Incomplete artifact |
## SOFT Scoring
Weights sum to 100%. Each dimension scores 0 or its full weight.
| ID  | Dimension | Weight | Criteria |
|-----|-----------|--------|----------|
| S01 | tldr quality | 1.0 | `tldr` <= 160 chars, names provider + model tier range |
| S02 | Rate limits documented | 1.0 | Both `rate_limit_rpm` and `rate_limit_tpm` present with source |
| S03 | Fallback configured | 1.0 | `fallback` field present with a valid provider name |
| S04 | All three tiers populated | 1.0 | `models.fast`, `models.balanced`, `models.quality` all present |
| S05 | Pricing per tier documented | 1.0 | Body Model Tiers table includes $/1M input and output per model |
| S06 | Retry strategy documented | 1.0 | `max_retries` present; body describes backoff algorithm |
| S07 | Capability matrix (optional) | 1.0 | BONUS, non-blocking: if a `capabilities:` block is present it uses ONLY canonical keys (tool_calling/structured_output/vision/streaming/json_mode/parallel_tool_calls/context_window/max_output_tokens) and declares only verifiable facts. Absent -> neutral, no penalty (degrade-never). Never a HARD gate. |
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool + record in memory |
| >= 8.0 | PUBLISH | Commit to pool |
| >= 7.0 | REVIEW | Acceptable with documented improvement items |
| < 7.0 | REJECT | Revise and resubmit — do not publish |
| 0 (HARD fail) | REJECTED | Fix failing HARD gate(s) first |
## Bypass
Bypasses are logged and expire automatically.
| Field | Value |
|-------|-------|

## Examples

# Examples: model-provider-builder
## Golden Example
INPUT: "Configure Anthropic provider for CEX with Max subscription"
OUTPUT:
```yaml
id: p02_mp_anthropic
kind: model_provider
pillar: P02
version: "1.0.0"
created: "2026-04-06"
updated: "2026-04-06"
author: "builder_agent"
provider: "anthropic"
api_key_env: "ANTHROPIC_API_KEY"
api_base_url: null
auth_method: "api-key"
models:
  fast: "claude-haiku-3.5"
  balanced: "claude-sonnet-4-6"
  quality: "claude-opus-4-7"
rate_limit_rpm: 4000
rate_limit_tpm: 400000
max_retries: 3
timeout_seconds: 120
fallback: "openai"
health_check_interval: 60
cost_aware: true
nucleus_assignment: [N02, N03, N06, N07]
domain: llm_routing
quality: null
tags: [model-provider, anthropic, claude, multi-tier]
tldr: "Anthropic — claude-haiku/sonnet/opus tiers, 4K RPM (Max), fallback to OpenAI, cost-aware routing"
keywords: [anthropic, claude, llm-routing, fallback]
linked_artifacts:
  primary: null
  related: [p02_mp_openai, p02_mp_google]
data_source: "https://docs.anthropic.com/en/api/rate-limits"
## Boundary
model_provider IS: connection and routing config for Anthropic API (models, rate limits, fallback).
model_provider IS NOT: model_card, embedder_provider, agent, boot_config.
## Provider Matrix
| Parameter | Value | Source |
|-----------|-------|--------|
| Provider | anthropic | https://docs.anthropic.com/en/api |
| API Base | https://api.anthropic.com | https://docs.anthropic.com/en/api |
| Auth Method | api-key (x-api-key header) | https://docs.anthropic.com/en/api/getting-started |
| RPM (Max tier) | 4000 | https://docs.anthropic.com/en/api/rate-limits |
| TPM (Max tier) | 400000 | https://docs.anthropic.com/en/api/rate-limits |
| Timeout | 120s | CEX convention |
## Model Tiers
| Tier | Model ID | Context | $/1M In | $/1M Out | Use Case |
|------|----------|---------|---------|----------|----------|
| fast | claude-haiku-3.5 | 200K | $0.80 | $4.00 | Classification, formatting, simple Q&A |
| balanced | claude-sonnet-4-6 | 200K | $3.00 | $15.00 | Research, analysis, general coding |
| quality | claude-opus-4-7 | 200K | $15.00 | $75.00 | Complex architecture, multi-file refactors |
## Fallback Chain
1. Primary: anthropic (claude-sonnet-4-6)
2. Fallback 1: openai (gpt-4o) — trigger: anthropic 429 or 5xx for > 30s
3. Fallback 2: google (gemini-2.5-pro) — trigger: both anthropic and openai unavailable
4. Circuit breaker: open after 3 consecutive failures, half-open after 60s
## Rate Limit Strategy
- Algorithm: exponential backoff with jitter (base=1s, max=60s)
- Retry: max 3 attempts, then fallback to next provider
- RPM tracking: sliding window per provider
- TPM tracking: token count per response, rolling 60s window

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
