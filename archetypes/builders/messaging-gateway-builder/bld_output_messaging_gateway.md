---
kind: output_template
id: bld_output_template_messaging_gateway
pillar: P05
llm_function: PRODUCE
purpose: Canonical output shape for messaging_gateway artifacts
pattern: Fill {{vars}} to produce a valid messaging_gateway artifact
quality: null
title: "Output Template: messaging_gateway"
version: "1.0.0"
author: n03_builder
tags: [messaging_gateway, builder, output_template, p05, hermes_origin]
tldr: "Fill-in-the-blanks template for messaging_gateway: 7 required sections, platform matrix, security table, slash commands, stub notice."
domain: "messaging gateway construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F6_produce"
keywords: [messaging gateway construction, output template, fill-in-the-blanks template for messaging_gateway, required sections, platform matrix, security table, slash commands, stub notice, messaging_gateway, builder]
density_score: 0.90
related:
  - bld_architecture_messaging_gateway
  - messaging-gateway-builder
  - p04_mg_{{platform}}
---
# Output Template: messaging_gateway

## Frontmatter Template
```yaml
---
id: p04_mg_{{PLATFORM_SLUG}}
kind: messaging_gateway
pillar: P04
nucleus: n05
title: "Messaging Gateway: {{PLATFORM_DISPLAY_NAME}}"
version: 1.0.0
quality: null
created: "{{DATE_YYYY_MM_DD}}"
updated: "{{DATE_YYYY_MM_DD}}"
author: "{{AUTHOR_ID}}"
platforms_supported: [telegram, discord, slack, whatsapp, signal, email]
active_platforms: [{{ACTIVE_PLATFORMS_CSV}}]
transport:
  protocol: {{TRANSPORT_PROTOCOL}}
  auth_type: {{AUTH_TYPE}}
security:
  dm_pairing: {{DM_PAIRING_BOOL}}
  command_approval_list: [{{APPROVAL_COMMANDS_CSV}}]
  allowed_user_ids: [{{ALLOWED_USERS_CSV}}]
  rate_limit_per_user_per_min: {{RATE_LIMIT_INT}}
features:
  voice_memo_transcription: {{VOICE_BOOL}}
  cross_platform_continuity: true
  shared_slash_commands: true
tags: [messaging_gateway, {{PLATFORM_SLUG}}, hermes_origin, stub, p04]
tldr: "{{TLDR_MAX_160CH}}"
---
```

## Body Template

### Section 1: Overview (required)
```
## Overview
{{PLATFORM_DISPLAY_NAME}} gateway stub for the multi-platform messaging architecture.
{{ONE_SENTENCE_DEPLOYMENT_CONTEXT}}.
Part of a unified gateway routing all platforms to the same agent and memory layer.
```

### Section 2: Platform Configuration (required)
```
## Platform Configuration
| Platform | Status | Transport | Auth |
|----------|--------|-----------|------|
| {{PLATFORM_1}} | active | {{PROTOCOL_1}} | {{AUTH_1}} |
| {{PLATFORM_2}} | standby | -- | -- |
```

### Section 3: Security (required)
```
## Security
| Control | Value | Notes |
|---------|-------|-------|
| dm_pairing | {{DM_PAIRING_BOOL}} | {{DM_PAIRING_REASON}} |
| allowed_user_ids | {{ALLOWED_COUNT}} IDs | {{ALLOWED_NOTE}} |
| rate_limit | {{RATE_LIMIT_INT}}/min/user | {{RATE_LIMIT_NOTE}} |
| command_approval_list | {{APPROVAL_COUNT}} commands | {{APPROVAL_NOTE}} |
```

### Section 4: Features (required)
```
## Features
| Feature | Status | Dependency |
|---------|--------|------------|
| cross_platform_continuity | enabled | peer_id consistent across platforms |
| shared_slash_commands | enabled | All active platforms share /cmd set |
| voice_memo_transcription | {{VOICE_STATUS}} | {{VOICE_DEPENDENCY}} |
```

### Section 5: Shared Slash Commands (required)
```
## Shared Slash Commands
| Command | Description |
|---------|-------------|
| /help | List available commands |
| /status | Agent status and memory summary |
| /reset | Clear current session context |
{{ADDITIONAL_COMMANDS}}
```

### Section 6: Integration Points (required)
```
## Integration Points
- `user_model` (P10): peer_id linked to gateway user identity -- populated on every turn
- `session_state` (P10): ephemeral conversation snapshot per turn
{{IF_VOICE}}- `stt_provider` (P04): voice memo transcription (voice_memo_transcription: true){{/IF_VOICE}}
- `agent_profile` (P08): {{AGENT_PROFILE_ID}} -- the agent this gateway routes to
```

### Section 7: Stub Notice (required)
```
## Stub Notice
This is a stub specification. No live platform connections are implemented here.
To activate: configure platform credentials in `.cex/config/gateway_{{PLATFORM_SLUG}}.yaml`
and run `messaging gateway setup` then `messaging gateway start`.
```

## Variable Reference
| Variable | Description | Example |
|----------|-------------|---------|
| `{{PLATFORM_SLUG}}` | Primary platform, lowercase | telegram |
| `{{PLATFORM_DISPLAY_NAME}}` | Human-readable platform name | Telegram |
| `{{ACTIVE_PLATFORMS_CSV}}` | Comma-separated active platforms | telegram, discord |
| `{{TRANSPORT_PROTOCOL}}` | websocket, webhook, or polling | webhook |
| `{{AUTH_TYPE}}` | bot_token, oauth, or app_password | bot_token |
| `{{DM_PAIRING_BOOL}}` | true or false | true |
| `{{RATE_LIMIT_INT}}` | Integer requests/min/user | 30 |
| `{{VOICE_BOOL}}` | true or false | false |
| `{{DATE_YYYY_MM_DD}}` | ISO date | 2026-04-18 |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_messaging_gateway]] | downstream | 0.54 |
| [[messaging-gateway-builder]] | upstream | 0.53 |
| [\[p04_mg_`{{platform}}`\]] | upstream | 0.53 |
