---
kind: quality_gate
id: p11_qg_rate_limit_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of rate_limit_config artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: rate_limit_config"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, rate-limit-config, P09, rpm, tpm, budget, tier]
tldr: "Pass/fail gate for rate_limit_config artifacts: numeric limit completeness, tier validity, budget cap presence, and provider identification."
domain: "rate limiting configuration — RPM, TPM, budget, and tier management for LLM API providers"
created: "2026-03-29"
updated: "2026-03-29"
8f: "F7_govern"
keywords: [rate limiting configuration, numeric limit completeness, tier validity, budget cap presence, and provider identification, quality-gate, rate-limit-config]
density_score: 0.90
related:
  - rate-limit-config-builder
---
## Quality Gate

# Gate: rate_limit_config

This ISO encodes a rate limit policy -- throttle bounds, quota windows, and backoff behavior.
## Definition
| Field | Value |
|---|---|
| metric | rate_limit_config artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: rate_limit_config` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p09_rl_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, or missing prefix |
| H03 | ID equals filename stem | `id: p09_rl_foo` but file is `p09_rl_bar.md` |
| H04 | Kind equals literal `rate_limit_config` | `kind: config` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `provider`, `rpm`, `tpm`, `tier`, or `tags` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Limit completeness | 1.0 | RPM, TPM, RPD, and concurrent all documented |
| Tier description | 1.0 | Tier named, described, and upgrade path provided |
| Budget cap | 1.0 | budget_usd present with alert_threshold and overage policy |
| Model overrides | 0.5 | Per-model rpm/tpm overrides present when provider supports them |
| Retry policy | 0.5 | retry_after documented for 429 handling |
| Provider accuracy | 1.0 | Limits match known provider documentation for stated tier |
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
| conditions | Internal placeholder used only during development with fictional limits |
| approver | Author self-certification noting placeholder status |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 7d — placeholder configs must be replaced with real limits or removed |
| never_bypass | H01 (unparseable YAML), H05 (self-scored gates corrupt quality metrics), H07/H08 (zero/negative limits break all consumers) |

## Examples

# Examples: rate-limit-config-builder

This ISO encodes a rate limit policy -- throttle bounds, quota windows, and backoff behavior.
## Golden Example
INPUT: "Create rate limit config for Anthropic Build tier"
OUTPUT:
```yaml
id: p09_rl_anthropic_build
kind: rate_limit_config
pillar: P09
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "Anthropic Build Tier Rate Limits"
```
## Overview
Declares rate limits for the Anthropic API Build tier — the default production tier
activated after $5 cumulative spend. Used by all Claude API integrations at this tier.
## Limits
| Dimension | Limit | Notes |
|-----------|-------|-------|
| RPM | 50 | Requests per minute, all models |
| TPM | 80,000 | Tokens per minute, all models |
| RPD | 1,000 | Requests per day hard cap |
| Concurrent | 10 | Max parallel in-flight requests |
## Tier
**Tier**: build
Standard production tier. Requires $5 cumulative API spend to activate.
Includes all Claude models. Upgrade to Scale tier requires costm agreement with Anthropic sales.
## Budget
Monthly cap: $100.00
Alert threshold: 80% — trigger notification at $80 spend
Overage policy: Requests blocked when budget_usd exceeded; reset at billing cycle start.
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches ^p09_rl_ pattern (H02 pass)
- kind: rate_limit_config (H04 pass)
- rpm: 50 and tpm: 80000 are positive integers (H07+H08 pass)
## Anti-Example
INPUT: "Create rate limit config for OpenAI"
BAD OUTPUT:
```yaml
id: openai-limits
kind: config
provider: openai
rpm: unlimited
tpm: lots
quality: 9.5
tags: [openai]
```
Rate limits for OpenAI. Use when calling GPT.
FAILURES:
1. id: "openai-limits" has hyphens and no `p09_rl_` prefix -> H02 FAIL
2. kind: "config" not "rate_limit_config" -> H04 FAIL
3. quality: 9.5 (not null) -> H05 FAIL
4. rpm: "unlimited" is not a positive integer -> H07 FAIL
5. tpm: "lots" is not a positive integer -> H08 FAIL
6. tags: only 1 item, missing "rate_limit_config" -> H09 FAIL
7. Missing required fields: pillar, version, created, updated, author, name, tier, tldr -> H06 FAIL
8. Body missing ## Overview, ## Limits, ## Tier, ## Budget sections -> H10 FAIL
9. No tier specified — cannot verify limits against provider docs -> SOFT FAIL
10. No budget_usd or alert_threshold — cost unbounded -> SOFT FAIL

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
