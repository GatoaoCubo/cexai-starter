---
kind: quality_gate
id: p11_qg_streaming_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of streaming_config artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: streaming_config"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, streaming-config, SSE, WebSocket, chunked, P11]
tldr: "Gates for streaming_config: validates protocol enum, buffer positivity, heartbeat presence, lifecycle completeness."
domain: "streaming_config -- SSE, WebSocket, and chunked HTTP transport specifications"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [streaming_config -- sse, gates for streaming_config, validates protocol enum, buffer positivity, heartbeat presence, lifecycle completeness, quality-gate]
density_score: 0.92
related:
  - bld_architecture_streaming_config
  - bld_schema_streaming_config
---
## Quality Gate

# Gate: streaming_config

## Definition

| Field | Value |
|-------|-------|
| metric | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator | AND (all HARD) + weighted_sum (SOFT) |
| scope | All artifacts where `kind: streaming_config` |

## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.

| ID | Check | Failure message |
|----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p05_sc_[a-z][a-z0-9_]+$` | "ID fails streaming_config namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"streaming_config"` | "Kind is not 'streaming_config'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, protocol, version, created, author, tags, tldr | "Missing required field(s)" |

## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.

| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Protocol rationale | 1.0 | Explains why this protocol was chosen over alternatives |
| Buffer sizing justification | 1.0 | buffer_bytes choice is explained relative to expected data rate |
| Backpressure completeness | 1.0 | backpressure_strategy present with overflow rationale |
| Heartbeat tuning | 1.0 | heartbeat_interval_ms below known proxy timeout thresholds |
| Flush interval correctness | 1.0 | flush_interval_ms <= 50ms for token streams; documented rationale |
| Lifecycle completeness | 1.0 | timeout_ms, reconnect_delay_ms, shutdown strategy all present |

Weight sum: 1.0+1.0+1.0+1.0+1.0+1.0+0.5+1.0+1.0+0.5 = 9.5 (normalized to 100%)

## Actions

| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool as golden exemplar |
| >= 8.0 | PUBLISH | Publish to pool |
| >= 7.0 | REVIEW | Flag for human review before publish |
| < 7.0 | REJECT | Return to author with failure report |

## Bypass

| Field | Value |
|-------|-------|
| conditions | New transport integration where full parameter set is not yet known |
| approver | Engineering lead approval required (written); protocol and buffer fields never bypassed |

## Examples

# Examples: streaming-config-builder

## Golden Example 1 -- SSE for LLM Token Delivery

INPUT: "Configure SSE streaming for LLM token delivery"

OUTPUT:
```yaml
id: p05_sc_llm_token_sse
kind: streaming_config
pillar: P05
version: "1.0.0"
created: "2026-04-13"
updated: "2026-04-13"
author: "builder_agent"
protocol: sse
```

## Overview
SSE transport for real-time LLM token delivery from inference server to browser.
Producer: FastAPI inference endpoint. Consumer: browser EventSource API.

## Protocol Settings

| Parameter | Value | Notes |
|-----------|-------|-------|
| protocol | sse | Unidirectional; browser auto-reconnects |
| content_type | text/event-stream | Required MIME for SSE |
| encoding | utf-8 | Text tokens |
| event_id | enabled | Allows reconnect resume from last token |
| event_type | token | Named event; client filters by type |

## Flow Control

| Parameter | Value | Notes |
|-----------|-------|-------|
| buffer_bytes | 4096 | 4KB -- fits ~1000 tokens before flush |
| flush_interval_ms | 50 | 20 flushes/sec -- smooth UX |
| backpressure_strategy | drop | Slow client drops tokens; LLM keeps generating |
| max_connections | 200 | Limit concurrent inferences |

## Lifecycle

| Parameter | Value | Notes |
|-----------|-------|-------|
| heartbeat_interval_ms | 15000 | Comment event every 15s prevents proxy timeout |
| timeout_ms | 60000 | 60s idle terminates stream |
| reconnect_delay_ms | 1000 | 1s before EventSource reconnects |
| max_reconnect_attempts | -1 | Infinite -- client retries until done |
| shutdown | graceful | Send [DONE] sentinel before closing |

WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p05_sc_ pattern (H02 pass)
- kind: streaming_config (H04 pass)
- protocol: sse (valid enum, H06 pass)

## Golden Example 2 -- WebSocket for Chat

INPUT: "Configure WebSocket streaming for bidirectional chat"

OUTPUT (frontmatter only for brevity):
```yaml
id: p05_sc_chat_websocket
kind: streaming_config
pillar: P05
protocol: websocket
buffer_bytes: 8192
heartbeat_interval_ms: 30000
max_connections: 500
backpressure_strategy: block
```

Key differences from SSE: block backpressure (messages must not drop in chat),
larger buffer (binary frames), longer timeout (chat sessions persist).

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
