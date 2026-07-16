---
kind: instruction
id: bld_instruction_messaging_gateway
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for messaging_gateway
pattern: 3-phase pipeline (configure -> compose -> validate)
quality: null
title: "Instruction: messaging_gateway"
version: "1.0.0"
author: n03_builder
tags: [messaging_gateway, builder, instruction, p04, hermes_origin]
tldr: "3-phase build: identify active platforms + configure transport + set security posture. Stub only (DP5). Max 4096 bytes."
domain: "messaging gateway construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F6_produce"
keywords: [messaging gateway construction, phase build, identify active platforms, configure transport, set security posture, stub only, messaging_gateway, builder, instruction, hermes_origin]
density_score: 0.90
related:
 - bld_schema_messaging_gateway
 - bld_output_template_messaging_gateway
 - messaging-gateway-builder
 - n00_messaging_gateway_manifest
 - bld_architecture_messaging_gateway
---
# Instructions: How to Produce a messaging_gateway

## Phase 1: CONFIGURE
1. Identify the deployment context: which platforms will this gateway serve?
2. Determine active_platforms (subset to configure now) vs platforms_supported (full enum)
3. Choose transport.protocol per platform: websocket (Discord), webhook (Telegram/Slack), polling (Signal/Email)
4. Choose transport.auth_type per platform: bot_token (Telegram/Discord), oauth (Slack), app_password (WhatsApp/Signal/Email)
5. Set security posture:
 - dm_pairing: always true for production
 - allowed_user_ids: empty for dev, populated for production
 - rate_limit_per_user_per_min: 30 default
 - command_approval_list: list any /commands requiring explicit operator approval
6. Declare feature flags:
 - cross_platform_continuity: true (default -- same peer_id across platforms)
 - shared_slash_commands: true (default -- same /commands on all platforms)
 - voice_memo_transcription: false unless stt_provider is configured
7. Confirm this is a STUB (DP5) -- no live platform code in the artifact
8. Confirm id slug: p04_mg_{platform} (primary platform slug, lowercase, underscores)

## Phase 2: COMPOSE
1. Read SCHEMA.md -- source of truth for all fields
2. Read OUTPUT_TEMPLATE.md -- fill template variables following SCHEMA constraints
3. Fill frontmatter: all required fields (quality: null -- never self-score)
5. Write active_platforms: only the platforms with credentials ready
6. Write transport block: protocol + auth_type
7. Write security block: dm_pairing + command_approval_list + allowed_user_ids + rate_limit
8. Write features block: voice_memo_transcription + cross_platform_continuity + shared_slash_commands
9. Write Overview section: 2 sentences -- what platforms this gateway covers and why
10. Write Platform Configuration section: table with Platform | Status | Transport | Auth
11. Write Security section: table with Control | Value | Notes
12. Write Features section: table with Feature | Status | Dependency
13. Write Shared Slash Commands section: table with Command | Description
14. Write Integration Points section: link to user_model, session_state, stt_provider, agent_profile
15. Write Stub Notice: explain DP5 and how to activate
16. Verify body <= 4096 bytes
17. Verify id matches `^p04_mg_[a-z][a-z0-9_]+$`

## Phase 3: VALIDATE
1. Check QUALITY_GATES.md -- verify each HARD gate manually
2. Confirm YAML frontmatter parses without errors
3. Confirm id matches `p04_mg_` prefix
4. Confirm kind == messaging_gateway
5. Confirm platforms_supported is non-empty and subset of [telegram, discord, slack, whatsapp, signal, email]
6. Confirm active_platforms is a subset of platforms_supported
7. Confirm transport.protocol is one of: websocket, webhook, polling
8. Confirm transport.auth_type is one of: bot_token, oauth, app_password
9. Confirm security.dm_pairing is boolean (true for production)
10. HARD gates: frontmatter valid, id pattern matches, platforms_supported non-empty, transport declared
11. SOFT gates: score against QUALITY_GATES.md -- target >= 9.0
12. Cross-check kind boundaries: no live platform code (that is impl, not spec)? No session data (that is session_state)? Not a single-event callback (that is webhook)?
13. Revise if score < 9.0 -- most common fix: add slash commands table or security rationale

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_messaging_gateway]] | downstream | 0.53 |
| [[bld_output_template_messaging_gateway]] | downstream | 0.46 |
| [[messaging-gateway-builder]] | downstream | 0.45 |
| [[n00_messaging_gateway_manifest]] | downstream | 0.42 |
| [[bld_architecture_messaging_gateway]] | downstream | 0.41 |
