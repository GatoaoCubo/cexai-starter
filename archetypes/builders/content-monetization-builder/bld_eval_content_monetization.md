---
kind: quality_gate
id: p11_qg_content_monetization
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of content monetization configs
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: content_monetization"
version: 1.0.0
author: n03_engineering
tags: [quality-gate, content-monetization, P11, pricing, billing, credits, governance]
tldr: "Gates for monetization artifacts — margin enforcement, webhook idempotency, credit tracking, mock-first development, checkout security."
domain: content_monetization
created: 2026-03-31
updated: 2026-03-31
8f: "F7_govern"
keywords: [gates for monetization artifacts, margin enforcement, webhook idempotency, credit tracking, mock-first development, checkout security, quality-gate]
density_score: 1.0
related:
  - content-monetization-builder
  - bld_schema_content_monetization
---
## Quality Gate

# Gate: content_monetization

## Definition
| Field | Value |
|-------|-------|
| Kind | content_monetization (cli_tool/workflow instances) |
| Pillar | P04 (tools) |
| Function | CALL (monetization automation) |
| Threshold | 8.0 minimum |

## HARD Gates (fail = reject)
| # | Gate | Check |
|---|------|-------|
| H1 | 9-stage complete | All 9 stages documented (PARSE through DEPLOY) |
| H2 | Margin enforcement | floor_margin_pct >= 0.30 and explicitly set |
| H3 | Integer pricing | All prices in centavos/cents, no floats |
| H4 | Zero secrets | No API keys/webhook secrets in plaintext — only ENV_VAR |
| H5 | Webhook idempotent | idempotency: true and dedup mechanism described |
| H6 | Mock mode default | mock_mode: true in all non-production configs |

## SOFT Gates (warn, don't reject)
| # | Gate | Check | Weight |
|---|------|-------|--------|
| S1 | Multi-tier | At least 2 pricing tiers defined | 0.8 |
| S2 | Credit packs | Pay-as-you-go packs available for non-subscribers | 0.7 |
| S3 | Behavioral emails | Email sequences use behavioral triggers, not time-only | 0.8 |
| S4 | Annual discount | Yearly pricing with discount available | 0.5 |
| S5 | Fallback provider | Alternative checkout provider documented | 0.6 |
| S6 | Course structure | If courses enabled: modules + lessons + drip defined | 0.7 |

## Margin Validation Gate (per-tier, at config time)
| Tier Type | Min Margin | Rationale |
|-----------|-----------|-----------|
| Free | N/A | No revenue, but must cap credit usage |
| Starter/Basic | 30% | Minimum viable after pipeline costs |
| Pro/Growth | 40% | Should fund scaling |
| Enterprise | 50% | Custom support costs absorb margin |
| Credit Pack | 35% | Per-unit must cover operation + overhead |

## Scoring Formula
```
score = (HARD_pass / 8) * 6.0 + (SOFT_weighted / max_weight) * 4.0
```

## Quality Tiers
| Tier | Score | Meaning |
|------|-------|---------|
| REJECT | < 8.0 | Missing stages, no margin check, or security violation |
| PUBLISH | 8.0-8.9 | Pipeline complete, margins enforced, webhooks idempotent |
| EXEMPLARY | 9.0+ | Full funnel (ads→checkout→course→email), multi-provider, behavioral triggers |

## Bypass
| Field | Value |
|-------|-------|
| conditions | Critical revenue stream requiring immediate launch |
| approver | n06-chief |
| audit_trail | Log in records/audits/ with justification and timestamp |
| expiry | 48h — full gate pass required before expiry |
| never_bypass | H3 (integer pricing), H4 (zero secrets), H5 (webhook idempotency) |

## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish as exemplar |
| >= 8.0 | PUBLISH | Ready for runtime |
| >= 7.0 | REVIEW | Flag for review |
| < 7.0  | REJECT | Rework required |

## Examples

# Examples: content-monetization-builder

## Golden — SaaS (Stripe, BR)
INPUT: "Monetization config for AI research platform, BR"
```yaml
identity: { empresa: "CODEXA", domain: ai_tools, currency: BRL, currency_unit: centavos, country: BR }
pricing:
  strategy: hybrid
  floor_margin_pct: 0.35
  tiers:
    - { name: free, price_monthly: 0, credits_monthly: 50, features: [basic_search] }
    - { name: pro, price_monthly: 9990, credits_monthly: 1000, features: [research, publish] }
credits: { pipeline_costs: { research: 50, publish: 10 }, overdraft_policy: notify_then_block }
checkout: { provider: stripe, webhook_secret_env: STRIPE_WEBHOOK_SECRET, idempotency: true, mock_mode: true }
validation: { margin_check: true, webhook_test: true, mock_before_live: true }
```
WHY GOOD: Hybrid pricing, centavos, ENV_VAR secrets, idempotent, mock on.

## Golden — Course (Hotmart, BR)
INPUT: "Pet care course, Hotmart, BR"
```yaml
identity: { empresa: "PetVida", domain: pet_education, currency: BRL, currency_unit: centavos, country: BR }
pricing: { strategy: tiered, floor_margin_pct: 0.70, tiers: [{ name: basico, price_monthly: 4990 }, { name: complete, price_monthly: 9990 }] }
checkout: { provider: hotmart, webhook_secret_env: HOTMART_HOTTOK, signature: sha256_hmac, format: json, idempotency: true, mock_mode: true }
courses: { enabled: true, modules: [{ title: "Nutrição", drip_days: 0 }, { title: "Saúde", drip_days: 7 }], certification: true }
validation: { margin_check: true, webhook_test: true, mock_before_live: true }
```
WHY GOOD: Course-focused, Hotmart webhook (JSON/sha256), drip, 70% margins.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
