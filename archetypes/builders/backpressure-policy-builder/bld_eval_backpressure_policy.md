---
kind: quality_gate
id: p11_qg_backpressure_policy
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of backpressure_policy artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: backpressure_policy"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, backpressure-policy, P09, reactive-streams, flow-control]
tldr: "Pass/fail gate for backpressure_policy: overflow strategy enum, buffer positivity, shed threshold range, watermark consistency."
domain: "backpressure policy -- reactive streams flow control for producer-consumer pipelines"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F7_govern"
keywords: [fail gate for backpressure_policy, overflow strategy enum, buffer positivity, shed threshold range, watermark consistency, quality-gate, backpressure-policy]
density_score: 0.90
related:
  - bld_schema_backpressure_policy
  - bld_architecture_backpressure_policy
---
## Quality Gate

# Gate: backpressure_policy

## Definition
| Field | Value |
|---|---|
| metric | backpressure_policy artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: backpressure_policy` |

## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p09_bp_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, or missing prefix |
| H03 | ID equals filename stem | id: p09_bp_foo but file is p09_bp_bar.md |
| H04 | Kind equals literal `backpressure_policy` | kind: flow-policy or any other value |
| H05 | Quality field is null | quality: 8.0 or any non-null value |
| H06 | All required fields present | Missing overflow_strategy, buffer_size, or shed_threshold |
| H07 | overflow_strategy is valid enum | Not one of: DROP_LATEST, DROP_OLDEST, BUFFER, THROTTLE, ERROR |
| H08 | buffer_size is positive integer | -1, 0, "big", absent |
| H09 | shed_threshold is float in [0.0, 1.0] | 1.5, -0.1, "high", absent |
| H10 | Body has all 4 required sections | Missing ## Overview, ## Strategy, ## Thresholds, or ## Flow |

## SOFT Scoring
| Dimension | Weight | Criteria |
|---|---|---|
| Strategy rationale | 1.0 | overflow_strategy choice justified with use case reasoning |
| Threshold coherence | 1.0 | high_watermark <= buffer_size AND low_watermark < high_watermark |
| Watermark presence | 1.0 | Both high_watermark and low_watermark declared |
| Queue identification | 1.0 | monitored_queue names specific queue/channel/topic |
| Batch sizing | 0.5 | request_batch_size tuned to consumer capacity |
| Data loss acknowledgment | 1.0 | DROP strategies explicitly document data loss risk |
| Consumer lag SLA | 0.5 | Acceptable lag documented |
| Boundary clarity | 1.0 | Explicitly NOT circuit_breaker, NOT rate_limit_config |
| tldr quality | 1.0 | tldr <= 160ch, includes strategy + key thresholds |

## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |

## Examples

# Examples: backpressure-policy-builder

## Golden Example
INPUT: "Create backpressure policy for LLM job queue"
OUTPUT:
```yaml
id: p09_bp_llm_job_queue
kind: backpressure_policy
pillar: P09
version: "1.0.0"
created: "2026-04-17"
updated: "2026-04-17"
author: "builder_agent"
overflow_strategy: "DROP_LATEST"
buffer_size: 100
shed_threshold: 0.8
high_watermark: 80
low_watermark: 40
request_batch_size: 5
monitored_queue: "llm_job_queue"
quality: null
tags: [backpressure_policy, llm_job_queue, reactive_streams]
tldr: "LLM job queue: DROP_LATEST at 80% capacity; 5-item batches; resume at 40 items"
```

## Overview
Controls flow for the async LLM job processing queue. When the consumer (LLM processor)
lags behind the producer (API ingest), drops newest requests to protect queue stability.

## Strategy
**Overflow strategy**: DROP_LATEST
Rationale: LLM jobs are user requests; newest duplicates are more likely to be retried
by the client than oldest queued items. Dropping newest preserves in-flight work.

| Strategy | Behavior | Data loss risk |
|----------|----------|---------------|
| DROP_LATEST | New jobs rejected when buffer >= 80% | Medium -- new requests rejected |

## Thresholds
- Buffer capacity: 100 items
- Shedding begins at: 80% (80 items)
- Active backpressure (high watermark): 80 items
- Normal flow resumes (low watermark): 40 items

## Flow
- Demand signal batch size: 5 items per request
- Protocol: Reactive Streams
- Queue monitored: llm_job_queue
- Consumer lag SLA: < 30 seconds per job

WHY THIS IS GOLDEN:
- overflow_strategy: DROP_LATEST (valid enum value) -- H07 pass
- buffer_size: 100 (positive integer) -- H08 pass
- shed_threshold: 0.8 (float in [0.0, 1.0]) -- H09 pass
- All 4 body sections present -- H10 pass

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
