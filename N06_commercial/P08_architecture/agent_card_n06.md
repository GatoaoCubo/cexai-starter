---
id: p08_ac_commercial_nucleus
title: "Agent Card Commercial"
kind: agent_card
8f: F2_become
pillar: P08
version: 4.1.1
created: 2026-03-30
updated: 2026-07-05
author: n06_commercial
name: brand_architect
role: "Brand Architect & Revenue Engineer — discovers brand identity, codifies brand_config.yaml, propagates to all nuclei, then monetizes via pricing/courses/funnels."
model: claude-sonnet-4-6
mcps: [fetch, canva, notebooklm]
mcps_planned: [stripe_mcp, hotmart_mcp]
domain_area: brand-identity-monetization
quality: null
tags: [agent_card, commercial, N06, brand, monetization, brand-architect]
tldr: "N06 agent card: dual-role Brand Architect + Revenue Engineer. Boot sequence loads 10 KCs, system prompt, dispatch rule. Sonnet default, Opus escalation for brand-from-scratch."
keywords: [agent card commercial, anthropic max subscription, brand discovery, brand book, courses -- all brand-aligned, agent_card, commercial, brand, identity, monetization]
density_score: 0.94
linked_artifacts:
  primary: p02_agent_commercial_nucleus
  related: [p03_sp_commercial_nucleus, p12_dr_commercial, p11_qg_commercial_n06]
boot_sequence:
  - "Check if .cex/brand/brand_config.yaml exists"
  - "Load N06_commercial/P02_model/agent_commercial.md (dual-role identity)"
  - "Load N06_commercial/P01_knowledge/kc_brand_*.md (10 brand KCs, 180KB)"
  - "Load N06_commercial/P03_prompt/system_prompt_n06.md (16 rules)"
  - "Load N06_commercial/P12_orchestration/dispatch_rule_n06.md (routing)"
  - "Load N06_commercial/P06_schema/brand_config_schema.md (41 variable validation)"
  - "If NO brand_config: enter Brand Discovery mode"
  - "If YES brand_config: enter Revenue Engineer mode"
  - "Initialize MCPs (fetch only; stripe_mcp/hotmart_mcp NOT CONFIGURED -- no server entry exists in .mcp.json or .mcp-n06.json anywhere in the repo, R-039)"
  - "Ready for dispatch"
constraints:
  - "FIRST nucleus on new instance — brand_config.yaml must exist before other nuclei produce branded output."
  - "Never hardcode brand values — all output uses {{BRAND_*}} mustache variables."
  - "Never write production code — advisory and specification only."
  - "Never execute financial transactions — model revenue, never process payments."
  - "Brand consistency score must be >= 0.85 before handoff to other nuclei."
dispatch_keywords: [brand, marca, identidade, brand-book, persona, arquetipo, voz, naming, tagline, posicionamento, UVP, ICP, design-tokens, paleta, pricing, precificar, curso, course, funnel, funil, monetizar, monetize, receita, revenue, upsell, downsell, checkout, conversao, conversion, LTV, MRR, assinatura]
tools: [brand_inject, brand_validate, brand_propagate, brand_audit, pricing_calculator, funnel_mapper, conversion_tracker, revenue_forecaster]
dependencies: [fetch]
dependencies_planned: [stripe_mcp, hotmart_mcp]
scaling:
  max_concurrent: 3
  timeout_minutes: 45
  memory_limit_mb: 2048
monitoring:
  health_check: "brand_validate.py --check .cex/brand/brand_config.yaml"
  signal_on_complete: true
  alert_on_failure: true
runtime: claude
subscription: anthropic_max
flags: []
domain: brand-identity-monetization
tags: [agent_card, commercial, N06, brand, identity, monetization, sonnet]
tldr: "brand_architect: Sonnet 4.6 model (Opus for brand-from-scratch escalation), Anthropic Max subscription. Phase 1 = Brand Discovery (12-15 Qs -> brand book -> brand_config.yaml -> propagate). Phase 2 = Revenue (pricing, funnels, courses -- all brand-aligned)."
density_score: 0.94
---

## Role

The `brand_architect` agent card defines the deployment spec for N06 Brand Architect & Revenue Engineer.
It handles brand identity discovery and codification (Phase 1) and revenue-facing artifacts (Phase 2).

## Model & Subscription

- **Model**: `claude-sonnet-4-6` (1M context) -- Sonnet default per model-economy.md 2026-07-01
- **Subscription**: Anthropic Max (zero API cost, subscription-based)
- **Runtime**: Claude Code native (git clone + Claude Code, no wrapper)

## MCPs

| MCP | Purpose | Status |
|-----|---------|--------|
| fetch | Web research for competitor analysis, market data | active |
| stripe_mcp | Subscription analytics, churn rate, payment data | planned -- NOT CONFIGURED |
| hotmart_mcp | Course sales data, affiliate commissions, products | planned -- NOT CONFIGURED |

**Status note (R-039, resolved 2026-07-05):** `stripe_mcp` and `hotmart_mcp` are names
in this file's `mcps_planned:` frontmatter list only -- neither has a server entry in
the root `.mcp.json` nor in the N06 overlay `.mcp-n06.json` (confirmed empty:
`{"mcpServers":{}}`). That is a stronger gap than "needs credentials": unlike
`firecrawl` / `canva` / `notebooklm` / `postgres` in the root config, which exist as
real `disabled: true` stub entries pending env vars, stripe_mcp and hotmart_mcp have
no stub at all anywhere in the repo. "Require env credentials -- BLOCKED until
configured" was the prior (inaccurate) framing; the honest status is NOT CONFIGURED.
Wiring either one first requires selecting a real MCP server package for that
provider and adding a config entry -- a build decision, not a credentials fix.

## Boot Sequence

1. Check `.cex/brand/brand_config.yaml` existence → determines Phase 1 or Phase 2
2. Load `agent_commercial.md` — establish dual-role identity
3. Load all `kc_brand_*.md` KCs (10 files, ~180KB brand knowledge)
4. Load `system_prompt_n06.md` — activate 16 ALWAYS/NEVER rules
5. Load brand schemas for validation
6. Initialize MCPs (fetch active; stripe_mcp/hotmart_mcp NOT CONFIGURED -- no server entry exists anywhere, see MCPs section above)
7. Ready for dispatch

## Dispatch

- **Keywords**: brand, marca, identidade, brand-book, persona, arquétipo, voz, naming, tagline, posicionamento, UVP, ICP, design-tokens, paleta, pricing, curso, funil, monetizar, receita, upsell, checkout
- **Priority**: 10 (highest — brand discovery blocks all other branded output)
- **Fallback**: N01 Research (market data) or N03 Builder (artifact construction)

## Brand Propagation Architecture

```
N06 generates .cex/brand/brand_config.yaml
  │
  ├──→ N01: BRAND_ICP, BRAND_COMPETITORS, BRAND_CATEGORY
  ├──→ N02: BRAND_VOICE, BRAND_COLORS, BRAND_FONTS, BRAND_VALUES
  ├──→ N03: BRAND_COLORS, BRAND_FONTS, BRAND_STYLE
  ├──→ N04: BRAND_NAME, BRAND_CATEGORY, BRAND_CONTENT_PILLARS
  ├──→ N05: BRAND_NAME, BRAND_LOGO_URL (env vars, service labels)
  ├──→ N07: BRAND_NAME (commit messages, logging)
  └──→ boot/*.cmd: BRAND_NAME (window titles)
```

## Scaling & Monitoring

- Max 3 concurrent instances (brand audit + pricing + funnel can parallelize)
- 45-minute timeout (brand discovery interview can be long)
- Health check via `brand_validate.py --check`
- Signal on complete: `.cex/runtime/signals/n06_complete.json`
- Alert on failure: `.cex/runtime/signals/n06_error.json`

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p12_dr_commercial | downstream | 0.55 |
| p02_agent_commercial_nucleus | upstream | 0.53 |
| p08_ac_brand_nucleus | sibling | 0.52 |
| p03_sp_brand_nucleus | upstream | 0.46 |
