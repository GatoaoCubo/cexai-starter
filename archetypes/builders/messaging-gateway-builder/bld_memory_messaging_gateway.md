---
kind: memory
id: bld_memory_messaging_gateway
pillar: P10
llm_function: INJECT
purpose: P10 memory hooks for messaging_gateway builder -- what to remember across sessions
quality: null
title: "Memory Hooks: messaging_gateway"
version: "1.0.0"
author: n03_builder
tags: [messaging_gateway, builder, memory, p10, hermes_origin]
tldr: "Memory hooks: track active platforms, security posture decisions, DP5 stub status, and Honcho wiring per deployment."
domain: "messaging gateway construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F3_inject"
keywords: [messaging gateway construction, memory hooks, track active platforms, security posture decisions, stub status, messaging_gateway, builder, memory, hermes_origin, . actual session state belongs to]
density_score: 0.89
related:
  - bld_architecture_messaging_gateway
---
# Memory Hooks: messaging_gateway Builder

## What to Remember Across Sessions
When a messaging_gateway artifact is produced, record these facts in session memory:

### Deployment-Level Facts
| Fact | Memory Kind | Why |
|------|-------------|-----|
| active_platforms at build time | entity_memory | Avoid redundant re-configuration |
| security.allowed_user_ids decisions | entity_memory | User-specific access policy |
| command_approval_list decisions | entity_memory | Privileged command surface |
| voice_memo_transcription toggle | entity_memory | stt_provider dependency tracking |
| Primary gateway id (p04_mg_X) | entity_memory | Cross-reference in handoffs |

### Builder-Level Facts
| Fact | Memory Kind | Why |
|------|-------------|-----|
| GDP decisions (DP5 confirmed) | learning_record | Never re-ask this decision |
| Platform transport choices | learning_record | Reuse in future gateway builds |
| Deployment context (dev vs prod) | entity_memory | Security posture calibration |

## Integration with P10
The messaging_gateway spec is stateless between turns. All durable state lives in P10:

```
messaging_gateway artifact
  |
  +-> user_model (P10, user-model-builder)
  |     peer_id, collections, dialectic loop config
  |
  +-> session_state (P10, session-state-builder)
        ephemeral conversation snapshot per turn
```

The gateway ARTIFACT does not store user data. It only specifies the interface.
Actual user memory belongs to `user_model`. Actual session state belongs to `session_state`.

## Memory Anti-Patterns (NEVER store in messaging_gateway)
- Bot tokens or platform credentials -> these go in .cex/config/
- User messages or conversation history -> these go in session_state (P10)
- Derived user facts -> these go in user_model (P10) Collections
- Active platform connection state -> this is runtime, not spec

## Compaction Trigger
If a session produces multiple messaging_gateway builds (multi-platform deployment),
compact into one entity_memory record:
```
entity: p10_em_gateway_deployment_{workspace}
attributes:
  active_platforms: [telegram, discord]
  security_posture: production (dm_pairing + allowlist)
  voice_enabled: false
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_messaging_gateway]] | upstream | 0.41 |
