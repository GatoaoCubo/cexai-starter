---
kind: config
id: bld_config_content_factory
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints for content_factory
pattern: CONFIG restricts SCHEMA, never contradicts it
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Content Factory"
version: "1.0.0"
author: n03_builder
tags: [content_factory, builder, content-fabric]
tldr: "Golden and anti-examples for content_factory construction, demonstrating the brief -> N-row fan-out and common pitfalls."
domain: "content factory construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, content factory construction, config content factory, content_factory, builder, content-fabric, "p04_content_factory_{{name}}.md", hashtag caps, requires_external_context]
density_score: 0.90
related:
  - bld_config_social_publisher
  - bld_config_content_library
  - bld_config_kind
  - p01_kc_content_factory
  - bld_schema_content_factory
---
# Config: content_factory Production Rules

## Naming Convention (per `.cex/kinds_meta.json`)
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact | `p04_content_factory_{{name}}.md` | `p04_content_factory_petlux_launch.md` |
| Template | `tpl_content_factory.md` | P04_tools/templates/ |
| Examples | `ex_content_factory_{niche}.md` | `ex_content_factory_pet_shop.md` |
| Compiled | `content_factory_{slug}.yaml` | P04_tools/compiled/ |
| Instance | `content_factory_brief.md` | `_instances/{tenant}/N02_marketing/` |
| Frontmatter id | `p04_content_factory_{slug}` | `p04_content_factory_petlux` |

## Size Limits
| Artifact | Max Size | Rationale |
|----------|---------|-----------|
| content_factory artifact | 8192 bytes | This kind's own `max_bytes` in kinds_meta.json |
| Template | 8192 bytes | Builder ISO limit |
| Example | 8192 bytes | Builder ISO limit |
| bld_prompt ISO | 10240 bytes | Reasoning-trace headroom (doctor's prompt-file exception) |

## Operational Constraints (real, code-enforced)
| Rule | Value | Rationale |
|------|-------|-----------|
| Hashtag cap: instagram | 5 | `cex_channel_publisher.HASHTAG_CAPS` |
| Hashtag cap: tiktok | 30 | `cex_channel_publisher.HASHTAG_CAPS` |
| Hashtag cap: linkedin | 8 | `cex_channel_publisher.HASHTAG_CAPS` |
| Hashtag cap: twitter | 3 | `cex_channel_publisher.HASHTAG_CAPS` |
| Hashtag cap: facebook | 30 | `cex_channel_publisher.HASHTAG_CAPS` |
| Hashtag cap: pinterest | 20 | `cex_channel_publisher.HASHTAG_CAPS` |
| Hashtag cap: threads | 5 | `cex_channel_publisher.HASHTAG_CAPS` |
| Hashtag cap: unknown platform | 30 (default) | `_DEFAULT_HASHTAG_CAP` |
| requires_external_context | true | ACR preflight pre-gathers web context (the only builder-less kind flagged this way) |
| requires_live_tools | false | The producer performs no live network I/O |
| core | false | Not a foundational/protected kind |

## File Placement Rules
| Artifact Type | Directory | Pillar |
|--------------|-----------|--------|
| Template | P04_tools/templates/ | P04 |
| Examples | P04_tools/examples/ | P04 |
| Compiled | P04_tools/compiled/ | P04 |
| Nucleus tool | N02_marketing/P04_tools/ | P04 |
| Nucleus KC | N02_marketing/P01_knowledge/ | P01 |
| Tenant brief | `_instances/{tenant}/N02_marketing/` | instance |

## Security Rules
1. Publisher API keys: NEVER in plaintext -- always ENV_VAR reference (this kind's own
   seam has NO provider wired at all; a future arm still follows this rule)
2. Voice-profile paths: reference via config, never hardcode a tenant's file path
3. Canonical product identifiers: reference by id, never embed full PII/pricing inline
4. No real publish credentials belong in a content_factory artifact -- the seam is
   provider-less by design (founder decision 2026-06-23)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_social_publisher]] | sibling | 0.38 |
| [[bld_config_content_library]] | sibling | 0.30 |
| [[bld_config_kind]] | sibling | 0.28 |
| [[p01_kc_content_factory]] | upstream | 0.27 |
| [[bld_schema_content_factory]] | downstream | 0.25 |
