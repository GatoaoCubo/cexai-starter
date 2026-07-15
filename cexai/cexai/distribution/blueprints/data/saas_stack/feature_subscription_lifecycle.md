---
kind: feature_template
feature_name: subscription_lifecycle
vertical: 17_saas_stack
round_added: 25
pillars: [P11, P12]
adr_019_packages: [governance/, foundation/]
feature_dependencies: [feature_billing, feature_crm]
brand_niche_constraints:
  - allow: [saas, subscription_box, freemium, subscription_recurring]
  - warn: [ecommerce_one_time, agency, services]
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in subscription notifications."
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
    description: "SaaS sub-niche (B2B / B2C / dev tools)."
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
    description: "Drives trial-end notification tone."
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
    description: "Notification + dashboard language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: subscription_tiers
    type: list[str]
    description: "Ordered list of subscription tier names from free to enterprise."
    filler_role: n06
    filler_stage: F3_INJECT
    context_hints: [brand_config.subscription_tiers]
    constraints: {min_items: 1, max_items: 8}
    default_filler_strategy: use_default_value
    required: false
    default_value: ["free", "starter", "pro", "team", "enterprise"]
    rebind_allowed: true
  - name: trial_duration_days
    type: int
    description: "Default trial length in days. Per-tier overrides via context_hints."
    filler_role: n06
    filler_stage: F3_INJECT
    context_hints: [brand_config.trial_duration_days]
    constraints: {minimum: 1, maximum: 90}
    default_filler_strategy: use_default_value
    required: false
    default_value: 14
    rebind_allowed: true
  - name: grace_period_days
    type: int
    description: "Days after payment failure before subscription enters 'cancelled' state."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.grace_period_days]
    constraints: {minimum: 0, maximum: 30}
    default_filler_strategy: use_default_value
    required: false
    default_value: 7
    rebind_allowed: true
---

# Feature Template: Subscription Lifecycle

**Purpose**: a SaaS-specific state machine tracking subscriptions from trial through paid through churn through reactivation. Sits ABOVE `feature_billing.md` (which handles payment events) and feeds the CRM lifecycle (via `feature_crm.md` SaaS override).

---

## Architecture

```
billing_provider (Stripe Connect, Paddle, etc.) webhook events
  -> feature_billing.md webhook handler
  -> feature_subscription_lifecycle state transitions
  -> update subscriptions table + emit audit_event
  -> trigger feature_crm.md lifecycle stage transitions
  -> trigger notifications via feature_messaging.md
```

---

## State machine

```
            new_signup
                |
                v
          +-> trialing
          |     |     |
          |     |     +-> trial_extended (admin grants extra days)
          |     v          |
          |   converted_to_paid <----+
          |     |
          |     v
          |   active
          |     |
          |     +-> upgraded (tier change up)
          |     +-> downgraded (tier change down)
          |     +-> paused (admin/user pause)
          |     +-> payment_failed
          |              |
          |              v
          |          grace_period (grace_period_days countdown)
          |              |
          |     +--------+--------+
          |     v                 v
          |   recovered      cancelled
          |     |                 |
          |     +-> active        v
          |                    churned
          |                       |
          |     +-----------------+
          |     v
          +-- reactivated (re-subscribe via self-serve)
                |
                v
              active
```

Transitions are EVENT-DRIVEN. Each event maps to a billing webhook OR an admin action.

---

## Data schema (recommended)

```yaml
table: subscriptions
columns:
  - id (uuid)
  - external_subscription_id (provider's ID)
  - customer_id (FK to crm_contacts)
  - tier (from subscription_tiers open_var)
  - state (enum: trialing | trial_extended | active | upgraded | downgraded | paused | payment_failed | grace_period | recovered | cancelled | churned | reactivated)
  - trial_end_at (iso_datetime; nullable for non-trial states)
  - grace_period_end_at (iso_datetime; nullable; set when payment_failed)
  - current_period_start / current_period_end
  - cancel_at_period_end (bool)
  - created_at / updated_at

table: subscription_events
columns:
  - id (uuid)
  - subscription_id (FK)
  - event_type (transition name; e.g., "trial_to_paid_converted")
  - from_state
  - to_state
  - triggered_by (str; "billing_webhook" | "admin_action" | "scheduled_cron")
  - external_event_id (provider's webhook event ID; for dedup)
  - occurred_at (iso_datetime)
  - metadata (jsonb)
```

---

## Trial behavior

When a customer signs up:
1. Create subscription row with `state: trialing`, `tier: <free or designated trial tier>`, `trial_end_at: now() + trial_duration_days`.
2. Schedule notifications at `trial_end_at - 7d`, `trial_end_at - 1d`, `trial_end_at`.
3. At `trial_end_at`:
   - If payment method on file AND auto-charge enabled: transition to `active` + `tier: <chosen paid tier>`.
   - If no payment method: transition to `cancelled` (no grace period for trial expiry).

`trial_extended` is admin-initiated -- adds N days to `trial_end_at`. Logged in subscription_events.

---

## Payment failure handling

When billing webhook reports payment failure:
1. Transition state: `active -> payment_failed`.
2. Set `grace_period_end_at: now() + grace_period_days`.
3. Notify customer (via `feature_messaging.md`); CTA: update payment method.
4. During grace_period: attempt payment retry per provider's dunning policy.
5. If retry succeeds: `payment_failed -> recovered -> active`.
6. If `grace_period_end_at` reached without success: `grace_period -> cancelled`.

---

## CRM lifecycle wiring (cross-feature integration)

Each subscription state transition triggers a CRM lifecycle update per the SaaS override in `feature_overrides.yaml`:

| Subscription event | CRM crm_lifecycle_stages transition |
|--------------------|--------------------------------------|
| Trial started | `trial_signup -> trial_active` |
| Trial converted to paid | `trial_active -> paid_active` |
| Payment failed | `paid_active -> at_risk` |
| Grace period -> cancelled | `at_risk -> churned` |
| Reactivated | `churned -> reactivated` |
| Tier upgrade | `paid_active -> paid_active` (with metadata: previous_tier, new_tier) |

This bidirectional wiring keeps billing + CRM in sync without separate event chains.

---

## Audit pattern

Every state transition emits `audit_event`:
- `event_type: subscription_<transition_name>`
- `retention_class: long_3y` (subscription history is compliance-relevant)
- `subject.subscription_id: <id>`
- `subject.from_state` + `subject.to_state`

---

## Integration contracts

- Consumes from: `feature_billing.md` (webhook events).
- Provides to: `feature_crm.md` SaaS-override (lifecycle stage transitions).
- Provides to: `feature_messaging.md` (trial-end notifications, payment-failure notifications).
- Provides to: `feature_analytics.md` SaaS-override (events: trial_start, trial_to_paid_converted, churn, reactivation).
- Audit via `kc_audit_event.md` with `retention_class: long_3y`.

---

## Out of scope

- Per-tier feature gating logic -- belongs to `feature_tier_gating.md`.
- Usage-based billing rules -- belongs to `feature_usage_metering.md`.
- Self-serve trial signup UX -- belongs to `feature_self_serve_onboarding.md`.
- Dunning email templates -- generic templates in `feature_messaging.md`; per-deployer customization.
- Annual vs monthly billing toggle -- handled by provider (Stripe / Paddle); subscription_lifecycle is provider-agnostic.
