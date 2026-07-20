---
id: p04_fn_content_monetization_n06
title: "Content Monetization Function Definition"
kind: function_def
pillar: P04
nucleus: n06
version: 1.0.0
quality: null
tags: [function_def, monetization, billing, checkout, courses, credits, n06]
tldr: "LLM-callable tool for a 9-step content monetization pipeline -- pricing resolution, credit gating, checkout, course generation, ad validation, email dispatch."
name: monetize_content
description: "Execute the full content monetization pipeline: resolve pricing, configure credits, setup checkout, generate course content, validate ads, and send email sequences."
parameters:
  type: object
  properties:
    product:
      type: object
      description: "Product descriptor with name, category, and audience"
    pricing_tier:
      type: string
      enum: [free, pro, enterprise]
    payment_provider:
      type: string
      enum: [stripe, paypal, mercadopago, digistore24, mock]
    pipeline_steps:
      type: array
      items:
        type: string
        enum: [PARSE, PRICING, CREDITS, CHECKOUT, COURSES, ADS, EMAILS, VALIDATE, DEPLOY]
    currency:
      type: string
      enum: [USD, EUR, BRL]
    dry_run:
      type: boolean
  required: [product, pricing_tier, payment_provider]
returns:
  type: object
  description: "Monetization configuration with checkout URL, credit balance, course artifacts, and deployment status"
provider_compat: [openai, anthropic, gemini]
strict: false
domain: content-monetization
density_score: 0.9
related:
  - p06_is_checkout_n06
  - p06_enum_pricing_tiers_n06
updated: "2026-07-20"
---

# Content Monetization Function Definition

## Purpose

`monetize_content` is the single entry point an LLM agent calls to run N06's
9-step content monetization pipeline: billing, credit consumption, checkout
session creation, LLM-driven course generation, ad content validation, email
sequence dispatch, and deployment of the final monetization config.

## Schema (OpenAI / Anthropic tool-use format)

```json
{
  "name": "monetize_content",
  "description": "Execute the full content monetization pipeline: resolve pricing, configure credits, setup checkout, generate course content, validate ads, and send email sequences.",
  "parameters": {
    "type": "object",
    "properties": {
      "product": {
        "type": "object",
        "description": "Product descriptor: {name, category: 'course'|'ebook'|'saas'|'ecommerce', audience}",
        "required": ["name", "category", "audience"]
      },
      "pricing_tier": {
        "type": "string",
        "description": "Tier determines credit allowance and checkout flow",
        "enum": ["free", "pro", "enterprise"]
      },
      "payment_provider": {
        "type": "string",
        "description": "Provider for checkout session; use 'mock' for dev/CI",
        "enum": ["stripe", "paypal", "mercadopago", "digistore24", "mock"]
      },
      "pipeline_steps": {
        "type": "array",
        "description": "Subset of pipeline steps to execute (default: all 9)",
        "items": {
          "type": "string",
          "enum": ["PARSE", "PRICING", "CREDITS", "CHECKOUT", "COURSES", "ADS", "EMAILS", "VALIDATE", "DEPLOY"]
        }
      },
      "currency": {
        "type": "string",
        "enum": ["USD", "EUR", "BRL"],
        "default": "USD"
      },
      "dry_run": {
        "type": "boolean",
        "description": "Validate config and estimate costs without side effects",
        "default": false
      }
    },
    "required": ["product", "pricing_tier", "payment_provider"]
  }
}
```

## Parameter Reference

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| product | object | yes | -- | `{name, category, audience}` -- drives course outline and ad content |
| pricing_tier | string | yes | -- | `free` (no checkout), `pro` (standard pack), `enterprise` (custom) |
| payment_provider | string | yes | -- | pick per market/rail; `mock` for CI |
| pipeline_steps | array | no | all 9 | Subset execution -- useful for a partial rerun after step failure |
| currency | string | no | USD | ISO currency, cents-integer representation |
| dry_run | boolean | no | false | Returns estimated costs and config preview without side effects |

## Pipeline Steps

| Step | Action | Output |
|------|--------|--------|
| PARSE | Extract product, audience, monetization goal | parsed_intent |
| PRICING | Resolve tier, estimate credit cost | pricing_config |
| CREDITS | check_sufficient -> lock credits | credit_lock |
| CHECKOUT | Create payment session | checkout_url |
| COURSES | LLM chain: outline -> module -> sales_page -> emails | course_artifacts |
| ADS | Validate ad content, confidence_score >= 0.7 | validated_ads |
| EMAILS | Render templates, queue dispatch | email_queue |
| VALIDATE | Gates: margin floor, mock exists, webhook idempotent | validation_report |
| DEPLOY | Save monetization_config, signal complete | config_id |

## Error Contract

| Error | Condition | Response |
|-------|-----------|----------|
| insufficient_credits | Balance < pipeline cost for the operation | `{"status": "error", "error": "insufficient_credits", "checkout_url": "..."}` |
| payment_provider_unavailable | API timeout or 5xx after 3 retries | `{"status": "error", "error": "payment_provider_unavailable"}` |
| course_generation_failed | LLM quota exceeded, no mock fallback | `{"status": "partial", "steps_failed": ["COURSES"]}` |
| ad_validation_failed | confidence_score < 0.7 after 2 retries | `{"status": "partial", "steps_failed": ["ADS"], "ad_validation_score": 0.4}` |

## Usage Examples

```python
# Full pipeline
result = await monetize_content(
    product={"name": "{{PRODUCT_NAME}}", "category": "course", "audience": "{{TARGET_AUDIENCE}}"},
    pricing_tier="pro",
    payment_provider="stripe",
)
# Returns: {"status": "success", "checkout_url": "https://payments.example/checkout/...",
#           "credits_consumed": 200, "course_outline_id": "outline_v1", ...}

# Dry run -- estimate costs before charging
result = await monetize_content(
    product={"name": "{{PRODUCT_NAME}}", "category": "ebook", "audience": "{{TARGET_AUDIENCE}}"},
    pricing_tier="free",
    payment_provider="mock",
    dry_run=True,
)

# Partial pipeline -- only ads + emails after the course already exists
result = await monetize_content(
    product={"name": "{{PRODUCT_NAME}}", "category": "course", "audience": "{{TARGET_AUDIENCE}}"},
    pricing_tier="pro",
    payment_provider="paypal",
    pipeline_steps=["ADS", "EMAILS", "DEPLOY"],
)
```

## Quality Gate

- [x] Description <= 2 sentences (LLM context budget)
- [x] All required parameters listed with types and enums
- [x] Return type documented with all fields
- [x] Error contract covers: insufficient_credits, provider_unavailable, generation_failed, validation_failed
- [x] provider_compat covers openai + anthropic + gemini
- [x] mock mode available for every payment path

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p06_is_checkout_n06]] | downstream (CHECKOUT step validates against this contract) |
| [[p06_enum_pricing_tiers_n06]] | related (pricing_tier enum origin) |
