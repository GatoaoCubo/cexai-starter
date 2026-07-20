---
id: p06_is_checkout_n06
kind: input_schema
pillar: P06
nucleus: n06
title: "Input Schema -- Checkout and Order Flow Contract"
version: 1.0.0
quality: null
tags: [checkout, order, schema, payment, commercial, contract]
tldr: "Canonical input contract for every checkout and order-creation flow in N06 -- product, customer, payment_method, price -- validated before any payment processing."
when_to_use: "Load when CONSTRAINing a checkout/cart/payment request shape, or before creating a payment session. Consult for 'what fields a valid order must carry and how they are validated'."
keywords: [input schema, checkout contract, order flow, payment validation, json schema, plan tier, billing cycle, validation rules, error codes, commercial contract]
long_tails:
  - "what fields must a valid checkout order contain before payment"
  - "how is a checkout request validated and which error codes fire"
slots:
  plan_tier: "<free | starter | pro | enterprise | custom>"
  billing_cycle: "<monthly | annual | lifetime | one_time>"
  payment_provider: "<stripe | paypal | pix | bank_transfer | crypto>"
  currency: "<ISO-4217 -- 3-letter currency code>"
density_score: 1.0
related:
  - p04_fn_content_monetization_n06
  - p06_enum_pricing_tiers_n06
updated: "2026-07-20"
---

# Input Schema: Checkout and Order Flow Contract

## Purpose

Defines the canonical data contract for all checkout and order-creation flows in N06's commercial pipeline. Every pricing page, cart, and payment handler MUST validate against this schema before processing.

### How to use

```text
You are a checkout/payment handler binding a request against this contract.
This is an input_schema; its 8F verb is CONSTRAIN -- it gates input before money moves.

- Validate the incoming order against Schema Definition before any processing.
- Require product, customer, payment_method, and price; reject if any is absent.
- Apply every row of the Validation Rules table; surface the matching error code.
- Read metadata.utm_* and referral_code for attribution; never trust client price.
```

### Procedure

```text
1. Receive the raw order payload at the pricing page or POST /checkout/create.
2. Validate against the JSON Schema (draft 2020-12) in Schema Definition.
3. Enforce the Validation Rules table; on failure, return the ENNN error code.
4. Recompute price.amount_cents server-side; never trust the client value.
5. On pass, create the payment session and persist metadata for attribution.
```

## Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "checkout_order_flow_v1",
  "title": "Checkout Order Flow",
  "type": "object",
  "required": ["product", "customer", "payment_method", "price"],
  "properties": {
    "product": {
      "type": "object",
      "required": ["id", "name", "plan_tier", "billing_cycle"],
      "properties": {
        "id": { "type": "string", "pattern": "^prod_[A-Za-z0-9]+$" },
        "name": { "type": "string", "minLength": 1, "maxLength": 200 },
        "plan_tier": { "$ref": "#/$defs/plan_tier" },
        "billing_cycle": { "enum": ["monthly", "annual", "lifetime", "one_time"] },
        "quantity": { "type": "integer", "minimum": 1, "default": 1 },
        "addons": {
          "type": "array",
          "items": { "$ref": "#/$defs/addon" }
        }
      }
    },
    "customer": {
      "type": "object",
      "required": ["email"],
      "properties": {
        "id": { "type": "string", "description": "Existing customer ID if returning" },
        "email": { "type": "string", "format": "email" },
        "name": { "type": "string" },
        "company": { "type": "string" },
        "country": { "type": "string", "pattern": "^[A-Z]{2}$" },
        "tax_id": { "type": "string", "description": "VAT/EIN for B2B invoicing" }
      }
    },
    "payment_method": {
      "type": "object",
      "required": ["provider"],
      "properties": {
        "provider": { "enum": ["stripe", "paypal", "pix", "bank_transfer", "crypto"] },
        "token": { "type": "string", "description": "Provider payment token" },
        "save_for_future": { "type": "boolean", "default": false }
      }
    },
    "price": {
      "type": "object",
      "required": ["currency", "amount_cents"],
      "properties": {
        "currency": { "type": "string", "pattern": "^[A-Z]{3}$" },
        "amount_cents": { "type": "integer", "minimum": 0 },
        "discount_code": { "type": "string" },
        "discount_percent": { "type": "number", "minimum": 0, "maximum": 100 },
        "tax_amount_cents": { "type": "integer", "minimum": 0 },
        "trial_days": { "type": "integer", "minimum": 0, "default": 0 }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "utm_source": { "type": "string" },
        "utm_medium": { "type": "string" },
        "utm_campaign": { "type": "string" },
        "referral_code": { "type": "string" },
        "affiliate_id": { "type": "string" }
      }
    }
  },
  "$defs": {
    "plan_tier": { "enum": ["free", "starter", "pro", "enterprise", "custom"] },
    "addon": {
      "type": "object",
      "required": ["id", "name", "price_cents"],
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "price_cents": { "type": "integer", "minimum": 0 }
      }
    }
  }
}
```

## Validation Rules

| Field | Rule | Error Code |
|-------|------|-----------|
| product.id | Must match `prod_*` pattern | E001_INVALID_PRODUCT_ID |
| customer.email | Valid RFC 5321 email | E002_INVALID_EMAIL |
| price.amount_cents | Non-negative integer | E003_INVALID_AMOUNT |
| payment_method.provider | From allowed enum | E004_UNSUPPORTED_PROVIDER |
| price.currency | ISO 4217 3-letter code | E005_INVALID_CURRENCY |
| price.discount_percent | 0-100 range | E006_INVALID_DISCOUNT |

## Integration Points

- **Pricing page** -> validates before payment session creation
- **API endpoint** `POST /checkout/create` -> validates request body
- **Webhook handler** -> validates reconstructed order on event replay
- **Referral system** -> reads `metadata.referral_code` for attribution

## Revenue Intelligence Notes

Track `metadata.utm_*` fields to measure channel ROI. `referral_code` attribution feeds into a referral-program payout calculation. `trial_days > 0` should trigger a churn-prevention playbook activation a few days before trial end.

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p04_fn_content_monetization_n06]] | downstream (consumes this contract at the CHECKOUT step) |
| [[p06_enum_pricing_tiers_n06]] | sibling (defines the plan_tier values this schema references) |
