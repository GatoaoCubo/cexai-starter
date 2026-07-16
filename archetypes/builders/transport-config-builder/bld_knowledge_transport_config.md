---
kind: knowledge_card
id: bld_knowledge_card_transport_config
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for transport_config production
quality: null
title: "Knowledge Card Transport Config"
version: "1.1.0"
author: n04_hybrid_review2
tags: [transport_config, builder, knowledge_card, webrtc, websocket, sse, grpc]
tldr: "Protocol coverage: WebRTC (SDP/ICE/STUN/TURN), WebSocket (RFC 6455), SSE, gRPC streaming, TCP/UDP/QUIC"
domain: "transport_config construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F3_inject"
keywords: [transport_config construction, knowledge card transport config, protocol coverage, grpc streaming, transport_config, builder, knowledge_card]
density_score: 0.92
related:
  - bld_architecture_transport_config
  - transport-config-builder
  - streaming-config-builder
---
## Domain Overview

Transport configuration defines how data traverses network boundaries — protocol selection,
connection establishment, NAT traversal, security, QoS, and flow control. Covers four primary
real-time transport families: WebRTC (browser-to-browser media), WebSocket (full-duplex
over HTTP), SSE (server-push event streams), and gRPC (HTTP/2 streaming RPC). Each has
distinct connection models, framing formats, and failure modes requiring separate config blocks.

The config_transport artifact governs: protocol-specific parameters (ICE candidates, stream
framing, keep-alive intervals), security (DTLS-SRTP, TLS 1.3), congestion control (QUIC BBR,
TCP CUBIC), QoS marking (DSCP), and NAT traversal (STUN/TURN server lists). Unlike
streaming_config (which governs buffer sizes and chunking) or realtime_session (which governs
connection lifecycle), transport_config owns the raw packet-level transmission parameters.

## WebRTC Transport

| Concept | Definition | RFC/Spec |
|---------|-----------|---------|
| SDP (Session Description Protocol) | Offer/answer negotiation of media codecs, ICE candidates, DTLS fingerprints | RFC 4566 |
| ICE (Interactive Connectivity Establishment) | NAT traversal framework — gathers host, server-reflexive, relay candidates | RFC 8445 |
| STUN | Server-reflexive address discovery for NAT traversal | RFC 5389 |
| TURN | Relay server fallback when direct path unavailable | RFC 5766 |
| DTLS-SRTP | DTLS handshake establishes SRTP keys for encrypted media | RFC 5764 |
| ICE Candidate Types | host (local NIC), srflx (STUN-reflected), relay (TURN) | RFC 8445 |

**Config fields for WebRTC:**
- `ice_servers`: list of STUN/TURN URIs with credentials
- `ice_transport_policy`: "all" or "relay" (force TURN)
- `bundle_policy`: "max-bundle" | "balanced" | "max-compat"
- `rtcp_mux_policy`: "require" | "negotiate"

## WebSocket Transport (RFC 6455)

| Concept | Definition | Source |
|---------|-----------|--------|
| HTTP Upgrade handshake | Sec-WebSocket-Key/Accept header exchange upgrades HTTP to WS | RFC 6455 §4 |
| Masking | Client-to-server frames MUST be masked with 4-byte key | RFC 6455 §5.3 |
| Frame opcodes | 0x1 text, 0x2 binary, 0x8 close, 0x9 ping, 0xA pong | RFC 6455 §5.2 |
| Subprotocols | Sec-WebSocket-Protocol negotiation (e.g., "mqtt", "graphql-ws") | RFC 6455 §1.9 |
| Extensions | Per-message deflate (RFC 7692), per-frame compression | RFC 7692 |
| Keep-alive | Ping/pong frames to detect stale connections | RFC 6455 §5.5 |
| Close handshake | Mutual close with status codes (1000=normal, 1001=going away) | RFC 6455 §7.4 |

**Config fields for WebSocket:**
- `ping_interval_ms`: frequency of ping frames (e.g., 30000)
- `ping_timeout_ms`: max wait for pong before closing
- `max_message_size_bytes`: prevent memory exhaustion
- `subprotocols`: negotiated application protocols

## SSE (Server-Sent Events)

| Concept | Definition | Source |
|---------|-----------|--------|
| Event stream format | `data: ...\n\n` with optional `id:`, `event:`, `retry:` fields | W3C SSE spec |
| Reconnection | Browser auto-reconnects with `Last-Event-ID` header | W3C SSE spec |
| Connection multiplexing | Single HTTP/2 stream per SSE channel | HTTP/2 RFC 9113 |
| Content-Type | Must be `text/event-stream; charset=utf-8` | W3C SSE spec |
| Heartbeat | Empty comment lines (`:\n\n`) keep connection alive through proxies | W3C SSE spec |

**Config fields for SSE:**
- `retry_ms`: client reconnect delay hint
- `heartbeat_interval_ms`: comment frequency (default 15000)
- `max_event_size_bytes`: limit per-event payload
- `buffer_timeout_ms`: server flush interval for event batching

## gRPC Streaming Transport

| Concept | Definition | Source |
|---------|-----------|--------|
| Server streaming | Client sends one request, server streams N responses | gRPC spec |
| Client streaming | Client streams N requests, server sends one response | gRPC spec |
| Bidirectional streaming | Both sides stream independently over single HTTP/2 stream | gRPC spec |
| Flow control | HTTP/2 WINDOW_UPDATE controls per-stream and connection-level | RFC 9113 |
| Keepalive pings | GRPC_ARG_KEEPALIVE_TIME_MS / GRPC_ARG_KEEPALIVE_TIMEOUT_MS | gRPC core |
| Max message size | GRPC_ARG_MAX_RECEIVE/SEND_MESSAGE_LENGTH | gRPC core |

**Config fields for gRPC:**
- `keepalive_time_ms`: interval between keepalive pings
- `keepalive_timeout_ms`: wait before closing unresponsive connection
- `max_receive_message_length`: per-message size cap
- `max_send_message_length`: per-message size cap

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_transport_config]] | downstream | 0.41 |
| [[transport-config-builder]] | downstream | 0.38 |
| [[streaming-config-builder]] | downstream | 0.36 |
