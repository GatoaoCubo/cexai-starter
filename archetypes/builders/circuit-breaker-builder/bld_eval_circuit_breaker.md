---
kind: quality_gate
id: p11_qg_circuit_breaker
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of circuit_breaker artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: circuit_breaker"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "circuit-breaker"
  - "P09"
  - "resilience"
  - "fault-tolerance"
tldr: "Pass/fail gate for circuit_breaker artifacts: failure threshold validity, cooldown positivity, probe count, state machine completeness."
domain: "circuit breaker -- resilience pattern for dependency fault isolation"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F7_govern"
keywords:
  - "failure threshold validity"
  - "cooldown positivity"
  - "probe count"
  - "state machine completeness"
  - "quality-gate"
  - "circuit-breaker"
  - "resilience"
density_score: 0.90
related:
  - bld_output_template_circuit_breaker
  - bld_architecture_circuit_breaker
  - bld_instruction_circuit_breaker
  - bld_knowledge_card_circuit_breaker
  - p01_kc_circuit_breaker
---
## Quality Gate

# Gate: circuit_breaker

## Definition
| Field | Value |
|---|---|
| metric | circuit_breaker artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: circuit_breaker` |

## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p09_cb_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, or missing prefix |
| H03 | ID equals filename stem | id: p09_cb_foo but file is p09_cb_bar.md |
| H04 | Kind equals literal `circuit_breaker` | kind: breaker or any other value |
| H05 | Quality field is null | quality: 8.0 or any non-null value |
| H06 | All required fields present | Missing service, failure_rate_threshold, cooldown_duration, probe_count |
| H07 | failure_rate_threshold is integer in [1, 100] | 0, -1, "high", 101, absent |
| H08 | cooldown_duration is positive integer | -30, 0, "30s", absent |
| H09 | probe_count is positive integer | 0, -1, "three", absent |
| H10 | Body has all 4 required sections | Missing ## Overview, ## State Machine, ## Cooldown, or ## Fallback |

## SOFT Scoring
| Dimension | Weight | Criteria |
|---|---|---|
| Failure threshold specificity | 1.0 | Threshold is based on real dependency SLA or observed failure rate |
| State machine completeness | 1.0 | All 3 states (CLOSED/OPEN/HALF-OPEN) documented with transitions |
| Cooldown rationale | 1.0 | Cooldown duration justified (e.g. matches service restart time) |
| Probe strategy | 1.0 | probe_count reflects real recovery confidence level |
| Fallback quality | 1.0 | fallback_response is actionable (not just "error") |
| Exception coverage | 1.0 | monitored_exceptions covers all realistic failure modes |
| Slow call detection | 0.5 | slow_call_threshold_ms present when latency is a concern |
| Sliding window tuning | 1.0 | window type and size appropriate for traffic volume |
| Boundary clarity | 1.0 | Explicitly NOT rate_limit_config, NOT fallback_chain, NOT runtime_rule |
| tldr quality | 1.0 | tldr <= 160ch, includes service + thresholds |

## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |

## Examples

# Examples: circuit-breaker-builder

## Golden Example
INPUT: "Create circuit breaker for Anthropic API calls"
OUTPUT:
```yaml
id: p09_cb_anthropic_api
kind: circuit_breaker
pillar: P09
version: "1.0.0"
created: "2026-04-17"
updated: "2026-04-17"
author: "builder_agent"
service: "anthropic_api"
failure_rate_threshold: 50
cooldown_duration: 60
probe_count: 3
sliding_window_type: "COUNT_BASED"
sliding_window_size: 10
minimum_number_of_calls: 5
slow_call_threshold_ms: 30000
fallback_response: "Service temporarily unavailable. Retry after 60 seconds."
monitored_exceptions: [ConnectionError, TimeoutError, HTTP_5xx, HTTP_529]
quality: null
tags: [circuit_breaker, anthropic_api, llm_resilience]
tldr: "Anthropic API circuit breaker: 50% failure rate trips 60s cooldown; 3 probes to recover"
```

## Overview
Protects callers from cascading failure when the Anthropic API is degraded or unavailable.
Trips when 5 of the last 10 calls fail (50%), disabling the integration for 60 seconds.

## State Machine
| State | Condition | Transitions To |
|-------|-----------|---------------|
| CLOSED | Normal operation | OPEN when failure_rate >= 50% over last 10 calls |
| OPEN | API disabled | HALF-OPEN after 60s cooldown |
| HALF-OPEN | Recovery probe | CLOSED if 3 probes succeed; OPEN if any probe fails |

## Cooldown
- Duration: 60 seconds
- Probe calls: 3 requests allowed in HALF-OPEN
- Recovery criteria: 3 consecutive probe successes
- Reset trigger: 3 consecutive successes from half-open state

## Fallback
Response during OPEN state: "Service temporarily unavailable. Retry after 60 seconds."
Error code: 503
SLA impact: Callers receive 503 immediately instead of waiting for timeout

WHY THIS IS GOLDEN:
- failure_rate_threshold: 50 (positive integer, range [1,100]) -- H07 pass
- cooldown_duration: 60 (positive integer seconds) -- H08 pass
- probe_count: 3 (positive integer) -- H09 pass
- All 4 body sections present -- H10 pass

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
