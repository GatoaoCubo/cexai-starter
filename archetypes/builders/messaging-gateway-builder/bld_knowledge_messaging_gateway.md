---
kind: knowledge_card
id: bld_kc_messaging_gateway
pillar: P01
llm_function: INJECT
purpose: Linked KC for messaging_gateway builder -- injected at F3 INJECT
quality: null
title: "KC Link: messaging_gateway"
version: "1.0.0"
author: n03_builder
tags: [messaging_gateway, builder, knowledge_card, p01, hermes_origin]
tldr: "Builder-linked KC: messaging_gateway is the multi-platform transport stub. Boundaries vs webhook/api_client/notifier. Honcho wiring via user_model."
domain: "messaging gateway construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F3_inject"
keywords: [messaging gateway construction, kc link, builder-linked kc, boundaries vs webhook, honcho wiring via user_model, messaging_gateway, builder, knowledge_card, hermes_origin, "p04_mg_{platform}"]
density_score: 0.90
related:
  - messaging-gateway-builder
  - kc_messaging_gateway
  - n00_messaging_gateway_manifest
  - bld_architecture_messaging_gateway
  - p04_mg_{{platform}}
---
# KC Link: messaging_gateway Builder

## What This Builder Produces
`messaging_gateway` artifacts (P04) -- stub specifications for multi-agent multi-platform
messaging transport. Defines the interface by which an agent receives and sends messages
across Telegram, Discord, Slack, WhatsApp, Signal, and Email simultaneously.

## Canonical KC
Full knowledge card: `N00_genesis/P01_knowledge/library/kind/kc_messaging_gateway.md`
Read it at F3 INJECT before producing any messaging_gateway artifact.

## Critical Facts for Builders
1. **DP5 stub contract**: artifact is interface spec -- no live credentials, no connection code
2. **Cross-platform continuity**: same peer_id across all platforms (default, do not disable)
3. **DM pairing required**: security.dm_pairing: true for all production stubs
4. **Platform-Transport matrix**: see schema -- Telegram=webhook, Discord=websocket, Signal=polling
5. **Honcho wiring**: gateway populates user_model (P10) on every turn via session.add_messages

## Boundary Quick-Reference
| If user wants... | Route to... |
|-----------------|-------------|
| Single inbound HTTP event | webhook-builder |
| Outbound REST calls | api-client-builder |
| One-way notifications | notifier-builder |
| Voice processing only | stt-provider-builder |
| User memory across sessions | user-model-builder |
| Multi-platform messaging gateway | messaging-gateway-builder (this builder) |

## Quality Floor
Minimum acceptable messaging_gateway artifact:
- id: `p04_mg_{platform}` (namespace compliance)
- platforms_supported non-empty
- active_platforms non-empty subset
- transport fully declared
- security.dm_pairing declared
- All 7 body sections present
- quality: null
- Score >= 9.0 before commit

## Related KCs
- `kc_webhook.md` -- single HTTP event inbound callback pattern
- `kc_api_client.md` -- outbound REST client pattern
- `kc_user_model.md` -- Honcho peer record populated by gateway turns (P10)
- `kc_session_state.md` -- ephemeral session data from gateway turns (P10)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[messaging-gateway-builder]] | downstream | 0.52 |
| [[kc_messaging_gateway]] | sibling | 0.49 |
| [[n00_messaging_gateway_manifest]] | sibling | 0.43 |
| [[bld_architecture_messaging_gateway]] | downstream | 0.43 |
| [\[p04_mg_`{{platform}}`\]] | downstream | 0.35 |
