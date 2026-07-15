---
kind: feature_template
feature_name: usage_metering
vertical: 17_saas_stack
round_added: 25
pillars: [P11, P10]
adr_019_packages: [governance/, memory/]
feature_dependencies: [feature_subscription_lifecycle, feature_analytics]
brand_niche_constraints:
  - allow: [saas, usage_based, api_platform, dev_tools]
  - warn: [agency, services, ecommerce_one_time]
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in usage dashboards."
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
    description: "Drives metering granularity defaults."
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
    description: "Drives quota copy + warning UX."
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
    description: "Quota notification language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: metered_units
    type: list[str]
    description: "What's metered (e.g., ['api_call', 'storage_gb', 'compute_seconds', 'team_member', 'workspace'])."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.metered_units]
    constraints: {min_items: 1}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: aggregation_window
    type: enum
    description: "How often usage is aggregated for quota enforcement."
    filler_role: n05
    filler_stage: F3_INJECT
    allowed_values: ["realtime", "5min", "hourly", "daily", "monthly"]
    context_hints: [brand_config.aggregation_window]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "hourly"
    rebind_allowed: true
  - name: overage_policy
    type: enum
    description: "What happens when quota is exceeded."
    filler_role: n06
    filler_stage: F3_INJECT
    allowed_values: ["block", "soft_block_with_grace", "billable_overage", "throttle", "warn_only"]
    context_hints: [brand_config.overage_policy]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
---

# Feature Template: Usage Metering

**Purpose**: track and enforce per-subscription usage of metered units (API calls, storage, compute, seats). Drives billable usage records (for `feature_billing.md` usage_based model) and quota enforcement.

---

## Architecture

```
application code emits usage events
  -> usage events queue (in-memory + persist async)
  -> aggregator (per aggregation_window: 5min/hourly/daily)
  -> usage_records table (per subscription + unit + period)
  -> quota check: usage vs tier limits (from feature_tier_gating.md)
  -> overage handler (overage_policy: block | soft_block | billable | throttle | warn_only)
  -> emit audit_event + feature_analytics event (usage_recorded)
```

---

## Data schema

```yaml
table: usage_events
columns:
  - id (uuid)
  - subscription_id (FK)
  - unit (from metered_units open_var; e.g., "api_call")
  - amount (numeric)
  - resource_id (str; the API key / workspace / endpoint that originated the event)
  - occurred_at (iso_datetime; high precision)
  - metadata (jsonb)

table: usage_aggregates
columns:
  - id (uuid)
  - subscription_id (FK)
  - unit
  - period_start / period_end (iso_datetime)
  - amount_aggregated (numeric)
  - aggregated_at (iso_datetime)

table: usage_quotas
columns:
  - id (uuid)
  - subscription_id (FK)
  - unit
  - quota_amount (numeric; per period)
  - period_type (matches aggregation_window: hourly/daily/monthly)
  - overage_policy (enum from open_var)
  - resets_at (iso_datetime; next period boundary)
```

---

## Aggregation pipeline

Usage events flood in at high frequency (e.g., one per API call). Aggregation reduces them to per-period buckets:

| aggregation_window | Aggregation cadence | Use case |
|--------------------|---------------------|----------|
| `realtime` | Per event | Hard quotas (e.g., max 100 concurrent connections) |
| `5min` | Every 5 minutes | Near-realtime dashboards |
| `hourly` | Every hour at HH:00 | Default for most metering |
| `daily` | Every day at 00:00 UTC | Cost-sensitive metrics (compute_hours) |
| `monthly` | Once per period boundary | Billable usage records |

Deployer chooses per metered_unit. Multiple units can have different windows.

---

## Quota enforcement (overage policies)

When usage exceeds quota:

| Policy | Behavior |
|--------|----------|
| `block` | Reject new requests with HTTP 429 + clear error message. Usage cannot exceed quota. |
| `soft_block_with_grace` | Allow N% over quota (e.g., 110%) before blocking. Useful for burst tolerance. |
| `billable_overage` | Allow unlimited; charge per-unit overage rate at next billing period. |
| `throttle` | Slow responses (e.g., add latency / lower rate limit) instead of blocking. |
| `warn_only` | Track + notify but don't block. Useful for monitoring before enforcing. |

Deployer chooses per (tier, metered_unit). Free tier typically `block`; pro tier `billable_overage`; enterprise tier `warn_only` or custom contract.

---

## Per-tier limits (cross-feature integration)

Per-tier quotas defined in `feature_tier_gating.md` -- the tier_gating template owns "what features + limits each tier gets"; usage_metering owns "how to enforce them".

Example (from `feature_tier_gating.md` perspective, cross-ref):
```yaml
tier_limits:
  free:
    api_calls_monthly: 1000
    workspaces: 1
  starter:
    api_calls_monthly: 10000
    workspaces: 3
  pro:
    api_calls_monthly: 100000
    workspaces: unlimited
```

Usage_metering reads these limits at quota-check time.

---

## Billable usage records (for usage_based billing model)

When `feature_billing.md billing_model: usage_metered`, the aggregator emits records to the billing provider's usage API (Stripe Subscriptions usage records, Paddle Subscriptions usage, etc.) at period boundary.

```yaml
# Pseudo (spec only)
def emit_billable_usage(subscription_id, unit, amount, period_start, period_end):
    billing_provider.create_usage_record(
        subscription_item_id=lookup_subscription_item(subscription_id, unit),
        quantity=amount,
        timestamp=period_end,
        action="set"  # or "increment"
    )
```

---

## Audit pattern

- Every overage event emits `audit_event` (`event_type: usage_quota_exceeded`).
- Every aggregation run emits `audit_event` (`event_type: usage_aggregation_complete`) at debug verbosity.
- Sampled, NOT every usage event (would spam audit; high frequency).

---

## Integration contracts

- Consumes from: application code (raw usage events).
- Consumes tier limits from: `feature_tier_gating.md`.
- Provides billable records to: `feature_billing.md` (usage_metered model).
- Provides analytics events to: `feature_analytics.md` (`usage_recorded`, `usage_quota_exceeded`).
- Provides notifications to: `feature_messaging.md` (overage warnings).
- Audit via `kc_audit_event.md`.

---

## Out of scope

- Per-customer rate-limiting at HTTP layer (deployer uses CDN / API gateway / Cloudflare for this).
- Cost calculation (cost-per-unit) -- belongs to pricing engine + billing.
- Real-time per-user metering UI -- deployer extends.
- Historical drill-down analytics on usage patterns -- belongs to `feature_analytics.md`.
