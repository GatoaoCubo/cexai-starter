---
kind: quality_gate
id: p11_qg_retry_policy
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of retry_policy artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: retry_policy"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, retry-policy, P09, backoff, jitter]
tldr: "Pass/fail gate for retry_policy: id pattern, max_attempts range, jitter not NONE, no 4xx in retryable_errors, all 3 sections."
domain: "retry policy -- backoff and jitter config for retrying failed operations"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F7_govern"
keywords: [fail gate for retry_policy, id pattern, max_attempts range, jitter not none, xx in retryable_errors, quality-gate, retry-policy]
density_score: 0.90
related:
  - bld_output_template_retry_policy
  - bld_schema_retry_policy
  - bld_architecture_retry_policy
  - bld_config_retry_policy
  - bld_knowledge_card_retry_policy
---
## Quality Gate

# Gate: retry_policy

## Definition

| Field | Value |
|---|---|
| metric | retry_policy artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: retry_policy` |

## HARD Gates

All must pass (AND logic). Any single failure = REJECT.

| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p09_rtp_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, or missing prefix |
| H03 | ID equals filename stem | id: p09_rtp_foo but file is p09_rtp_bar.md |
| H04 | Kind equals literal `retry_policy` | kind: retry or any other value |
| H05 | Quality field is null | quality: 8.0 or any non-null value |
| H06 | max_attempts is positive integer | 0, -1, "many", absent |
| H07 | initial_interval is positive integer (ms) | 0, -100, "1s", absent |
| H08 | max_interval is positive integer >= initial_interval | max_interval < initial_interval |
| H09 | retryable_errors does NOT include 400/401/403 | Client errors in retry list |
| H10 | Body has all 3 required sections | Missing Retry Behavior, Backoff Calculation, or Error Classification |

## SOFT Scoring

| Dimension | Weight | Criteria |
|---|---|---|
| Jitter configuration | 1.0 | jitter is FULL or DECORRELATED (not NONE) |
| max_attempts in safe range | 1.0 | max_attempts in [3, 10] |
| Backoff calculation table | 1.0 | Per-attempt delays calculated and shown |
| Error classification completeness | 1.0 | Both retryable and non-retryable defined |
| retry_budget declared | 1.0 | Prevents retry storm |
| backoff_strategy explained | 0.5 | Rationale for chosen strategy |
| Boundary clarity | 1.0 | Explicitly NOT circuit_breaker, NOT rate_limit_config |
| tldr quality | 0.5 | tldr <= 160ch, includes operation, max_attempts, jitter |

## Actions

| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |

## Examples

# Examples: retry-policy-builder

## Golden Example

INPUT: "Create retry policy for Anthropic API calls"

WHY THIS IS GOLDEN:
- id matches `^p09_rtp_[a-z][a-z0-9_]+$` -- H02 pass
- max_attempts positive integer -- H03 pass
- initial_interval positive integer (ms) -- H04 pass
- max_interval declared -- H05 pass

```yaml
id: p09_rtp_anthropic_api
kind: retry_policy
pillar: P09
version: "1.0.0"
created: "2026-04-17"
updated: "2026-04-17"
author: "builder_agent"
operation: "anthropic_api_call"
max_attempts: 4
initial_interval: 1000
backoff_strategy: "exponential"
backoff_multiplier: 2.0
max_interval: 30000
jitter: "FULL"
retry_budget: 10
retryable_errors: [HTTP_429, HTTP_503, HTTP_529, ConnectionError, TimeoutError]
non_retryable_errors: [HTTP_400, HTTP_401, HTTP_403, HTTP_404, InvalidRequestError]
quality: null
tags: [retry_policy, anthropic_api, llm_resilience]
tldr: "Anthropic API retry: 4 attempts, exponential 1s->2s->4s->8s capped 30s, FULL jitter, retries 429/503/529."
```

## Retry Behavior

| Parameter | Value | Notes |
|-----------|-------|-------|
| max_attempts | 4 | 1 initial + 3 retries |
| initial_interval | 1000ms | 1 second before first retry |
| backoff_strategy | exponential | Doubles each attempt |
| backoff_multiplier | 2.0 | 1s -> 2s -> 4s -> 8s |
| max_interval | 30000ms | Capped at 30 seconds |
| jitter | FULL | rand(0, base_delay) -- thundering herd prevention |
| retry_budget | 10 | Max 10 concurrent retries in flight |

## Backoff Calculation

| Attempt | Base Delay | With FULL Jitter | Max Wait |
|---------|------------|-----------------|----------|
| 1 | 1000ms | rand(0-1000ms) | 1.0s |
| 2 | 2000ms | rand(0-2000ms) | 2.0s |
| 3 | 4000ms | rand(0-4000ms) | 4.0s |
| 4 | 8000ms | rand(0-8000ms) | 8.0s |

Total max wait: ~15 seconds before final failure.

## Error Classification

| Error | Action | Reason |
|-------|--------|--------|
| HTTP_429 (Too Many Requests) | RETRY | Rate limited -- temporary |
| HTTP_503 (Service Unavailable) | RETRY | Transient outage |
| HTTP_529 (Anthropic overloaded) | RETRY | Anthropic-specific transient |
| ConnectionError | RETRY | Network transient |
| TimeoutError | RETRY | Request timed out -- retry |
| HTTP_400 (Bad Request) | FAIL | Client error -- won't succeed |
| HTTP_401 (Unauthorized) | FAIL | Auth error -- fix credentials |
| HTTP_403 (Forbidden) | FAIL | Permission error -- won't succeed |
| InvalidRequestError | FAIL | Malformed request -- fix the request |

---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
