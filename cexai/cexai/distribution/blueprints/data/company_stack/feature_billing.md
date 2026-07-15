---
kind: feature_template
feature_name: billing
vertical: 16_company_stack
round_added: 23
pillars: [P11, P09]
adr_019_packages: [tools/, governance/]
feature_dependencies: [feature_pricing_engine]
brand_niche_constraints:
  - allow: [e-commerce, saas, subscription_box, marketplace, retail, creator]
  - warn: [agency, services]
open_vars:
  - name: brand_name
    type: str
    description: "Brand display on checkout pages + invoices."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    context_hints: [brand_config.brand_name]
    constraints: {min_length: 1, max_length: 80}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: brand_niche
    type: str
    description: "Drives default billing model + checkout copy."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    context_hints: [brand_config.brand_niche]
    constraints: {min_length: 1, max_length: 200}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: target_audience
    type: str
    description: "Drives checkout UX tone."
    filler_role: n02
    filler_stage: F3_INJECT
    context_hints: [brand_config.target_audience]
    constraints: {min_length: 3, max_length: 150}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: primary_language
    type: enum
    description: "Checkout UI language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: billing_provider
    type: enum
    description: "Payment processing backend."
    filler_role: n06
    filler_stage: F3_INJECT
    allowed_values: ["stripe", "mercadopago", "pagarme", "iugu", "asaas", "paddle", "lemon_squeezy", "ko_fi", "razorpay", "custom"]
    context_hints: [brand_config.billing_provider]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: false
  - name: billing_model
    type: enum
    description: "Billing model."
    filler_role: n06
    filler_stage: F3_INJECT
    allowed_values: ["one_time", "subscription_recurring", "usage_metered", "freemium", "donation", "marketplace_takerate"]
    context_hints: [brand_config.billing_model]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: false
  - name: currency
    type: enum
    description: "Billing currency (ISO 4217)."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["BRL", "USD", "EUR", "GBP", "JPY", "CNY", "MXN", "ARS", "INR", "ZAR"]
    context_hints: [brand_config.pricing_currency, brand_config.currency]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "USD"
    rebind_allowed: false
  - name: webhook_signing_required
    type: bool
    description: "Whether webhook payloads from the billing provider must be signature-verified before processing."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.webhook_signing_required]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: true
    rebind_allowed: false
---

# Feature Template: Billing

**Purpose**: payment processing + invoicing + subscription lifecycle. Provider-agnostic adapter pattern (Stripe, MercadoPago, Paddle, Lemon Squeezy, etc.). Bridges `feature_pricing_engine.md` (price determination) and the customer's payment.

---

## Architecture

```
checkout flow:
  -> customer selects product/plan
  -> price resolved via feature_pricing_engine.md (renders displayed_price)
  -> checkout session created with billing_provider (Stripe Checkout, MP Preference, etc.)
  -> customer redirected to provider's hosted checkout
  -> provider posts webhook on success/failure
  -> webhook handler verifies signature (if webhook_signing_required)
  -> updates internal subscription/order state
  -> emits audit_event
  -> triggers downstream (fulfillment, marketplace_orders, CRM lifecycle update)
```

---

## Billing models

| Model | Provider typical setup | Internal state |
|-------|------------------------|----------------|
| `one_time` | Provider Checkout, single payment intent | `orders` table |
| `subscription_recurring` | Provider subscription product + plan | `subscriptions` table + recurring invoices |
| `usage_metered` | Provider's usage records API (Stripe, Paddle) | `usage_records` + `subscriptions` |
| `freemium` | Provider subscription with free tier + paid tier | `subscriptions` with tier=free initially |
| `donation` | Provider Checkout (one-time variable amount) | `donations` table |
| `marketplace_takerate` | Provider Connect/Express + transfers | `transfers` + per-payment commission split |

---

## Data schema (recommended)

```yaml
# Orders (for one_time + marketplace_takerate models)
table: orders
columns:
  - id (uuid)
  - external_payment_id (provider's payment ID)
  - customer_id (FK to crm_contacts)
  - line_items (jsonb)
  - subtotal / tax / shipping / total
  - currency
  - status (pending | paid | refunded | cancelled | disputed)
  - paid_at / refunded_at
  - provider_metadata (jsonb)

# Subscriptions
table: subscriptions
columns:
  - id (uuid)
  - external_subscription_id
  - customer_id (FK)
  - plan_id (deployer-managed mapping)
  - tier (free | basic | pro | enterprise | ...)
  - status (active | past_due | cancelled | trialing | paused)
  - current_period_start / current_period_end
  - cancel_at_period_end (bool)
  - trial_end (nullable iso_datetime)

# Webhooks log
table: billing_webhooks
columns:
  - id
  - provider (matches billing_provider)
  - event_type (provider's event type string)
  - external_event_id (provider's idempotency key)
  - payload (jsonb)
  - signature_verified (bool)
  - processed_at
  - processing_result (success | failed | duplicate)
```

---

## Webhook security

`webhook_signing_required: true` (default) -- every incoming webhook MUST verify signature against the provider's signing secret (stored in `feature_secrets.md` vault).

Unverified webhooks: log + drop. NEVER process. This is the critical security gate -- an attacker injecting fake "payment succeeded" webhooks would otherwise unlock paid features.

Idempotency: providers retry webhooks. Use `external_event_id` as idempotency key. Already-processed events: skip + record duplicate.

---

## Subscription lifecycle hooks

Subscription state transitions trigger CRM lifecycle stage updates:

| Billing event | CRM stage transition |
|---------------|---------------------|
| Trial started | `crm_contacts.status: trial` |
| First payment | `status: active` |
| Failed payment | `status: at_risk` |
| Cancellation requested | `status: at_risk` (still has remaining period) |
| Period ended (cancelled) | `status: churned` |
| Re-activation | `status: reactivated` |

This is the bridge between billing and `feature_crm.md`. SaaS deployers use it; e-commerce one-time skips it.

---

## Invoicing

Default: provider's hosted invoices (Stripe Invoice, MP Boleto, etc.).

Custom invoice rendering (PDF generated by deployer): deferred. Pattern is documented; v1 uses provider invoices.

Invoice metadata stored in `orders.provider_metadata.invoice_url`.

---

## Tax + compliance

| Concern | Pattern |
|---------|---------|
| VAT/sales tax computation | Provider's tax service (Stripe Tax, Paddle handles automatically) OR external service (TaxJar, Avalara) |
| Multi-jurisdiction tax | Deployer's tax service responsibility |
| Refund policy | Deployer policy; provider-supported |
| Chargeback handling | Provider-supported; CEXAI logs dispute via `disputes` table (R24+) |

---

## Audit pattern

Every billing event emits `audit_event`:
- `event_type: billing_*` (specific: `billing_checkout_created`, `billing_payment_succeeded`, `billing_payment_failed`, `billing_subscription_cancelled`, `billing_refund_issued`, `billing_webhook_received`)
- `retention_class: long_3y` (financial events; compliance-sensitive)

Required for fraud investigation, tax audits, chargeback disputes.

---

## Niche-mismatch handling

| Niche | Compatibility |
|-------|--------------|
| agency, services | WARN -- agencies typically invoice externally (not point-of-sale billing); use this template only for productized services |

---

## Integration contracts

- Consumes from: `feature_pricing_engine.md` (price determination).
- Consumes secrets via: `feature_secrets.md` (provider API keys + webhook signing secret).
- Provides events to: `feature_crm.md` (subscription lifecycle hooks).
- Provides revenue feed to: `feature_analytics.md` (purchase / MRR / churn events).
- Audit via `kc_audit_event.md` with `retention_class: long_3y`.

---

## Out of scope

- Custom checkout UI (use provider's hosted checkout in v1; custom UI deferred to R24+).
- Multi-currency conversion at checkout (provider handles; CEXAI uses single currency per deployment).
- Affiliate commission splits (deferred R24+).
- Dunning email sequences (separate `feature_dunning.md` deferred; some providers handle natively).
- Invoice PDF customization beyond provider templates.
- Crypto / on-chain payments (deferred indefinitely).
