---
id: kc_tenant_voice_profile
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P03
title: "Tenant Voice Profile — Deep Knowledge for tenant_voice_profile"
version: 1.0.0
created: 2026-07-20
updated: 2026-07-20
author: knowledge_agent
domain: tenant_voice_profile
quality: null
tags: [tenant_voice_profile, P03, CONSTRAIN, kind-kc]
tldr: "The brand-voice mold a tenant fills once -- identity, register, lexicon -- that a grounded copy engine loads on every generation."
when_to_use: "Building, reviewing, or reasoning about tenant_voice_profile artifacts"
keywords: [brand voice, tenant voice profile, grounding contract, tone of voice, voice knob]
feeds_kinds: [tenant_voice_profile]
density_score: null
aliases: ["brand voice profile", "tone of voice mold", "voice knob", "brand voice guide"]
user_says: ["define our brand voice", "make copy sound like us", "set up a tone of voice guide", "give the copy engine our brand personality"]
long_tails: ["I want every generated ad to sound like our brand, not generic AI copy", "define our tone once so every writer or model uses the same voice", "make sure the copy engine never invents facts, only shapes how we say them", "keep our brand voice separate from any one AI agent's personality"]
cross_provider:
  frontify: "Brand guideline platform -- centralizes tone/voice rules teams reference before writing copy"
  mailchimp: "Brand Kit -- tone + style settings that feed into content generation"
  jasper: "Brand Voice -- a trained profile that constrains AI-generated copy to one register"
related:
  - kc_system_prompt
  - kc_guardrail
  - system-prompt-builder
  - guardrail-builder
---

# Tenant Voice Profile

## Spec
```yaml
kind: tenant_voice_profile
pillar: P03
llm_function: CONSTRAIN
max_bytes: 8192
naming: p03_tvp_{{tenant}}.md
id_pattern: "^p03_tvp_[a-z][a-z0-9_]*$"
core: false
```

## What It Is
A `tenant_voice_profile` is the brand-voice mold a tenant fills ONCE, that a grounded copy engine
loads on every generation. It has three blocks: Block A is a fixed skeleton identical across
every tenant; Block B is an INHERITED grounding contract (facts-only rules, referenced by name,
never restated loosely); Block C is this ONE tenant's distilled fill (brand name, essence,
archetype, tone, voice samples, color roles, imagery mood, forbidden elements, per-channel
platform specifics, and sources). It is NOT `personality` (an agent's own persona, hot-swappable
per agent) and NOT `system_prompt` (the LLM's identity and task rules, read first by the model).
A tenant_voice_profile is BRAND voice, not AGENT identity, with no task instructions of its own.

## Cross-Framework Map
| Framework/Provider | Class/Concept | Notes |
|---|---|---|
| Frontify / Brandfolder | Brand guideline platform | Centralized tone/voice rules, not a single-agent persona |
| Mailchimp Brand Kit | Tone + style settings | Feeds copy generation tools across channels |
| Jasper / Copy.ai brand voice | Trained brand-voice profile | Constrains AI-generated copy toward one brand's register |

## Key Fields
| Field | Type | Required | Notes |
|---|---|---|---|
| brand_name, essence, archetype | string | yes | Block C identity fields |
| tone | object | yes | `{primary, secondary, anti_tone}` -- what the voice IS and explicitly is NOT |
| voice_samples | object | yes | Per-channel list; 3+ real samples per channel recommended |
| color_roles | object | yes | `{primary_action, accent, urgency}` -- visual register, not the voice itself |
| imagery_mood | string | yes | Descriptive tone for visual selection |
| forbidden_elements | list | yes | Words, claims, or motifs the voice must never use |
| platform_specifics | object | yes | Per-channel `{max_chars, hashtag_style, cta_style, emoji_ok}` |
| sources | list | yes | Non-empty -- every non-obvious Block C field must trace to a cited source |

## Patterns
| Pattern | When to Use | Example |
|---|---|---|
| 3-block body | Any per-tenant mold that shares a skeleton but varies in content | Block A (skeleton) -> Block B (inherited contract) -> Block C (tenant fill) |
| Distillation, not invention | Filling brand voice from real source material | Every non-obvious field cites a real source; unsupported fields are marked unfilled, never guessed |
| Reference, don't restate | Reusing a shared contract across many tenant instances | Block B points at the grounding contract by name instead of re-deriving it per tenant |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Fabricated voice sample | Breaks the no-fabrication invariant the whole profile depends on | Only include samples pulled from real tenant material |
| Empty `sources` list | A voice profile with no provenance is a guess, not a distillation | Require at least one cited source; treat empty as a hard gate failure |
| Voice touching a fact, dimension, or price | Violates the inherited grounding contract | Facts and quantitative claims stay with the product/fact data, never the voice profile |
| Confusing with `personality` | personality is an agent's own persona and is hot-swappable per agent | tenant_voice_profile is per-TENANT brand voice, shared across every agent writing for that tenant |

## Integration Graph
```
[system_prompt: skeleton pattern] --> [tenant_voice_profile] <-- [guardrail: grounding contract]
                                              |
                                    [grounded copy engine reads it per generation]
```

## Decision Tree
- IF you need to bound HOW a tenant's copy sounds (register, tone, lexicon) THEN tenant_voice_profile
- IF you need an agent's own persona, independent of any one tenant THEN personality
- IF you need the LLM's identity and task rules THEN system_prompt
- IF you need the underlying facts a generation may state THEN a product/fact data kind, not this one
- DEFAULT: tenant_voice_profile for any per-tenant voice knob a copy engine loads before writing

## Quality Criteria
- GOOD: All three blocks present; Block C fields cite sources; `sources` non-empty
- GREAT: Voice samples cover every active channel; platform_specifics calibrated from real per-channel limits; forbidden_elements explicit
- FAIL: Any Block C field invented without a source; voice profile states a fact, price, or claim; Block A keys renamed or missing

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_system_prompt]] | upstream (skeleton lineage) | 0.50 |
| [[kc_guardrail]] | upstream (grounding contract lineage) | 0.50 |
| [[system-prompt-builder]] | related | 0.40 |
| [[guardrail-builder]] | related | 0.40 |
