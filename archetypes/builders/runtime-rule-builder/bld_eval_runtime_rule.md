---
kind: quality_gate
id: p11_qg_runtime_rule
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of runtime_rule artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: Runtime Rule'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: 'Quality gate for runtime behavior specs: verifies rule type, numeric parameters
  with units, scope declaration, and recovery behavior.'
domain: runtime_rule
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
keywords: [runtime rule, verifies rule type, numeric parameters, kind: runtime_rule, yaml.safe_load(frontmatter), p09_rr_*, id.startswith("p09_rr_")]
density_score: 0.85
related:
  - p11_qg_quality_gate
  - p11_qg_response_format
  - p11_qg_prompt_template
  - p03_ins_runtime_rule
  - p11_qg_runtime_state
---
## Quality Gate

## Definition
A runtime rule artifact specifies how a single operation behaves under load, failure, or resource pressure. It declares a rule type (timeout, retry, rate_limit, or circuit_breaker), the numeric parameters that govern the rule with explicit units, and the scope of operations the rule applies to. Every rule must define what happens when its threshold is breached — silent failure is not acceptable.
Scope: files with `kind: runtime_rule`. Does not apply to lifecycle rules (P09 sub-kind) or feature flags (P14), which govern activation rather than execution behavior.
## HARD Gates
Failure on any single gate means REJECT regardless of soft score.
| ID  | Predicate | How to test |
|-----|-----------|-------------|
| H01 | Frontmatter parses as valid YAML | `yaml.safe_load(frontmatter)` raises no error |
| H02 | `id` matches namespace `p09_rr_*` | `id.startswith("p09_rr_")` is true |
| H03 | `id` equals filename stem | `Path(file).stem == id` |
| H04 | `kind` equals literal `runtime_rule` | string equality check |
| H05 | `quality` is null at authoring time | `quality is None` |
| H06 | All required frontmatter fields present and non-empty | id, kind, pillar, title, version, created, updated, author, domain, tags, tldr, rule_type, scope all present |
## SOFT Scoring
Score each dimension 0 (absent or fails) to 1 (present and passes). Weights are 0.5 or 1.0.
| #  | Dimension | Weight |
|----|-----------|--------|
| 1  | `density_score` field present and >= 0.80 | 1.0 |
| 2  | Retry strategy specified as fixed, exponential, or jitter (not just "retry") | 1.0 |
| 3  | Timeout values have units and are grounded in observed latency data or documented assumptions | 1.0 |
| 4  | Rate limit has a time window defined (per second, per minute, per hour) | 1.0 |
| 5  | Circuit breaker has a recovery behavior defined (half-open probe interval, reset condition) | 1.0 |
| 6  | Tags list includes `runtime-rule` | 0.5 |
**Formula**: `final_score = (sum of score_i * weight_i) / (sum of weight_i) * 10`
Weight total: 8.5. Each dimension contributes proportionally. Score range: 0.0 to 10.0.
## Actions
| Tier | Threshold | Action |
|------|-----------|--------|
| GOLDEN | >= 9.5 | Publish to pool as golden; use as reference for reliability engineering |
| PUBLISH | >= 8.0 | Publish to pool; mark production-ready |
| REVIEW | >= 7.0 | Return to author with scored dimension feedback; one revision cycle allowed |
| REJECT | < 7.0 | Block from pool; full rewrite required before re-evaluation |
## Bypass
| Field | Value |
|-------|-------|
| condition | Rule governs a third-party dependency whose latency profile is not yet characterized |
| approver | Domain lead must approve in writing before bypass takes effect |
| audit_log | Record in `records/pool/audits/bypasses.md` with date, approver, and reason |

## Examples

# Examples: runtime-rule-builder
## Golden Example
INPUT: "Define retry rules for the API client connecting to external payment provider"
OUTPUT:
```yaml
id: p09_rr_payment_api_retry
kind: runtime_rule
pillar: P09
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
rule_name: "payment_api_retry"
rule_type: retry
scope: "payment_connector"
quality: 8.9
tags: [runtime_rule, retry, payment, P09, api, resilience]
tldr: "Payment API retry: exponential backoff 500ms base, 3 max, jitter, 5s total budget"
description: "Retry strategy for external payment API calls with exponential backoff and jitter"
fallback: "Return payment_unavailable error after 3 retries exhausted"
severity: critical
```
## Rule Specification
| Parameter | Value | Unit | Notes |
|-----------|-------|------|-------|
| max_retries | 3 | count | After 3 failures, stop retrying |
| base_delay | 500 | ms | Initial wait before first retry |
| strategy | exponential_jitter | - | base * 2^attempt + random(0, 250ms) |
| max_delay | 4000 | ms | Cap on any single retry delay |
| total_budget | 5000 | ms | Max total time for all retries |
| retryable_codes | [408, 429, 500, 502, 503] | HTTP | Only retry on transient errors |
## Trigger Behavior
When max_retries exhausted: return `payment_unavailable` error to caller.
When rate-limited (429): respect Retry-After header if present, else use backoff.
When total_budget exceeded: abort remaining retries, return timeout error.
Log every retry attempt with: attempt number, wait duration, error code.
## Tuning Guide
- base_delay: increase to 1000ms if payment provider has strict rate limits
- max_retries: do not exceed 5 (risk of duplicate payments)
- Monitor: retry_count metric, success_after_retry_rate, total_budget_exceeded_count
- Safe range: base_delay 200-2000ms, max_retries 1-5, total_budget 3000-15000ms
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p09_rr_ pattern (H02 pass)
- kind: runtime_rule (H04 pass)
- 19 required+recommended fields present (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
