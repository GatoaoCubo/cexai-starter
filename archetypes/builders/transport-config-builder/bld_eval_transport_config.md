---
kind: quality_gate
id: p09_qg_transport_config
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for transport_config
quality: null
title: "Quality Gate Transport Config"
version: "1.1.0"
author: n04_hybrid_review2
tags:
  - "transport_config"
  - "builder"
  - "quality_gate"
tldr: "Quality gate with HARD and SOFT scoring for transport_config"
domain: "transport_config construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords:
  - "transport_config construction"
  - "quality gate transport config"
  - "transport_config"
  - "builder"
  - "quality_gate"
  - "^p09_tc_[a-z0-9_]+$"
  - "quality gate"
density_score: 0.90
related:
  - bld_output_template_transport_config
  - bld_schema_transport_config
  - transport-config-builder
  - n00_transport_config_manifest
  - bld_architecture_transport_config
---
## Quality Gate
## Definition
| Metric | Threshold | Operator | Scope |
|--------|-----------|----------|-------|
| TLS version | >= 1.2 | >= | All encrypted transports |
| WebRTC TURN server | >= 1 | >= | WebRTC configs |
| Keepalive / heartbeat | defined | present | WebSocket, gRPC, SSE |
| Message size limit | defined | present | WebSocket, gRPC |
| QoS markings | defined | present | Latency-sensitive configs |

## HARD Gates
| ID | Check | Fail Condition |
|----|-------|----------------|
| H01 | YAML valid | Invalid YAML syntax |
| H02 | ID matches pattern | ID does not match `^p09_tc_[a-z0-9_]+$` |
| H03 | kind matches | kind != "transport_config" |
| H04 | TLS version | TLS/DTLS version < 1.2 |
| H05 | Transport type declared | transport_type field missing or empty |
| H06 | WebRTC: TURN present | WebRTC config has no TURN server (STUN-only blocked) |
| H07 | Mandatory protocol fields | Missing required fields for declared transport_type |

## SOFT Scoring (5D)
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|--------------|
| D1 | Protocol completeness | 0.30 | All mandatory fields for transport_type: 1.0; partial: 0.5; minimal: 0.2 |
| D2 | Security configuration | 0.25 | TLS 1.3 + proper certs + DTLS-SRTP: 1.0; TLS 1.2: 0.7; no TLS: 0.0 |
| D3 | Resilience / reconnection | 0.20 | Keepalive + retry policy + timeout defined: 1.0; partial: 0.5; none: 0.0 |
| D4 | QoS and performance | 0.15 | DSCP + limits + congestion control: 1.0; partial: 0.5; none: 0.2 |
| D5 | Documentation quality | 0.10 | tldr + notes + inline comments: 1.0; tldr only: 0.5; none: 0.0 |

## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN: auto-approve, add to examples library |
| >= 8.0 | PUBLISH: deploy to production |
| >= 7.0 | REVIEW: manual check before deploy |
| < 7.0 | REJECT: rework required |

## Bypass
| Condition | Approver | Audit Trail |
|-----------|----------|------------|
| Emergency fix with known risk | Senior Engineer | Log reason, timestamp, PID |
| Legacy system lacking TLS support | Architecture Lead | Log reason + migration ticket |
| Third-party API constraint | Tech Lead | Log reason + external ticket ref |

## Examples
## Golden Example 1: WebRTC Media Transport
```yaml
---
id: p09_tc_webrtc_media
kind: transport_config
pillar: P09
title: "WebRTC Media Transport - Production"
version: "1.0.0"
transport_type: webrtc
protocol: dtls-srtp
```

## Golden Example 2: WebSocket Event Stream
```yaml
---
id: p09_tc_ws_events
kind: transport_config
pillar: P09
title: "WebSocket Event Transport"
version: "1.0.0"
transport_type: websocket
protocol: rfc6455
```

## Anti-Example 1: WebRTC Without TURN
```yaml
---
id: p09_tc_stun_only
kind: transport_config
transport_type: webrtc
---
ice_servers:
  - urls: ["stun:stun.l.google.com:19302"]
```

**Why it fails:**
STUN-only configuration fails behind symmetric NAT (~15% of enterprise users). Without TURN
relay servers, connectivity checks will fail silently. H06 HARD gate REJECTS this config.
Always pair STUN with at least one TURN server.

## Anti-Example 2: WebSocket Without Message Size Limit
```yaml
---
id: p09_tc_ws_no_limit
kind: transport_config
transport_type: websocket
---
endpoint: "wss://api.example.com/stream"
keepalive:
  ping_interval_ms: 30000
```

**Why it fails:**
Missing `max_message_size_bytes`. A single WebSocket frame can be up to 2^63 bytes by protocol
spec. Without a server-side limit, a malicious client can OOM the server with one message.
Also missing reconnect policy -- if the WSS connection drops, the client has no guidance on
retry behavior.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
