---
kind: feature_template
feature_name: analytics
vertical: 16_company_stack
round_added: 23
pillars: [P11, P10]
adr_019_packages: [governance/, tools/]
feature_dependencies: []
brand_niche_constraints: null
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in analytics dashboards."
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
    description: "Drives KPI selection defaults."
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
    description: "Drives funnel definitions + segmentation defaults."
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
    description: "Dashboard label language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: analytics_provider
    type: enum
    description: "Telemetry/dashboard backend."
    filler_role: n05
    filler_stage: F3_INJECT
    allowed_values: ["plausible", "umami", "matomo", "posthog", "amplitude", "mixpanel", "ga4", "grafana_loki", "datadog", "custom"]
    context_hints: [brand_config.analytics_provider]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: privacy_mode
    type: enum
    description: "Privacy posture for visitor tracking."
    filler_role: n06
    filler_stage: F3_INJECT
    allowed_values: ["no_cookies", "consent_required", "essential_only", "full_tracking"]
    context_hints: [brand_config.privacy_mode]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "consent_required"
    rebind_allowed: true
  - name: tracked_events
    type: list[str]
    description: "Event names tracked (e.g., ['page_view', 'add_to_cart', 'checkout_start', 'purchase'])."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.tracked_events]
    constraints: {min_items: 1}
    default_filler_strategy: use_default_value
    required: false
    default_value: ["page_view", "session_start", "session_end"]
    rebind_allowed: true
---

# Feature Template: Analytics

**Purpose**: a privacy-aware observability layer for visitor + behavioral telemetry. Provider-agnostic across cookieless (Plausible, Umami) + consent-based (PostHog, GA4) + ops-focused (Grafana, Datadog) backends.

---

## Architecture

```
[public + admin pages]
  -> tracker SDK (provider-specific JS or server-side ingestion)
  -> analytics_provider's collection endpoint
  -> dashboards (provider-hosted OR self-hosted)

[backend events (publishing, orders, etc.)]
  -> emit audit_event AND optionally analytics event
  -> analytics_provider's server-side API
```

Two streams: client-side (visitor behavior) and server-side (ops events). Both flow to the same provider OR different providers per concern.

---

## Provider matrix

| Provider | Cookies | Self-host? | Open-source? | Strong for |
|----------|---------|------------|--------------|-----------|
| `plausible` | No | Optional | Yes | Privacy-first marketing analytics |
| `umami` | No | Yes | Yes | Self-hosted privacy-first |
| `matomo` | Configurable | Yes | Yes | Comprehensive GA-alternative |
| `posthog` | Yes | Yes | Yes | Product analytics + feature flags |
| `amplitude` | Yes | No | No | Product analytics enterprise |
| `mixpanel` | Yes | No | No | Behavioral analytics |
| `ga4` | Yes | No | No | Free + ubiquitous; privacy concerns in EU |
| `grafana_loki` | n/a | Yes | Yes | Ops observability (logs + metrics) |
| `datadog` | n/a | No | No | Ops enterprise (logs + metrics + APM) |
| `custom` | n/a | n/a | n/a | Deployer adapter for proprietary backend |

Deployer choice drives:
- Tracker SDK (per-provider snippet)
- Server-side ingestion adapter
- Consent banner requirement (per `privacy_mode`)

---

## Privacy modes

| Mode | Visitor tracking |
|------|------------------|
| `no_cookies` | Anonymous aggregates only (Plausible-style). No PII. No consent needed (in most jurisdictions). |
| `consent_required` | Tracking after explicit consent banner accept. Pre-consent: anonymous + essential only. |
| `essential_only` | Track only auth-required pages (admin); public visitors not tracked. |
| `full_tracking` | All events tracked; consent depends on jurisdiction. NOT recommended for GDPR/LGPD targets. |

Deployer's legal obligation. The template provides the technical lever; deployer validates with counsel.

---

## Standard event taxonomy

Recommended `tracked_events` core set (deployer extends per niche):

| Event | When fired |
|-------|-----------|
| `page_view` | Public route navigation |
| `session_start` / `session_end` | Visit boundaries |
| `signup_initiated` / `signup_completed` | Auth funnel |
| `login` | Auth event |
| `add_to_cart` | E-commerce funnel (if `feature_catalog.md` enabled) |
| `checkout_start` / `purchase` | E-commerce conversion |
| `content_published` | When publishing pipeline completes |
| `lead_created` | CRM event (linked to `feature_crm.md`) |
| `outreach_sent` | CRM outreach (via `feature_messaging.md`) |
| `error` | Client-side error surface |

Per-niche extensions:
- SaaS: `trial_start`, `subscription_active`, `feature_used`, `churn`
- Agency: `proposal_sent`, `engagement_start`, `delivery_complete`
- Creator: `view`, `subscribe`, `interaction`

---

## KPI defaults

Per `brand_niche`, default KPI cards:

| Niche | Top 5 KPIs |
|-------|------------|
| e-commerce | revenue_30d, conversion_rate, avg_order_value, returning_customer_pct, cart_abandonment |
| saas | MRR, ARR, churn_rate, active_users_30d, NPS |
| agency | active_projects, billable_hours, pipeline_value, client_satisfaction, on_time_delivery |
| creator | followers_growth, engagement_rate, content_velocity, top_post_views, revenue_per_post |

Deployer adjusts via dashboard config.

---

## Integration contracts

- Consumes events from: `feature_frontend.md` (client tracker), `feature_publishing.md` (publish events), `feature_crm.md` (CRM events), `feature_catalog.md` (e-commerce funnel events).
- Provides KPI feed to: `feature_admin_console.md` dashboard module.
- Server-side events MAY also emit `audit_event` (analytics is observability; audit is governance; both can coexist).
- Cross-references `kc_audit_event.md`.

---

## Out of scope

- A/B testing infrastructure -- deferred R24+ `feature_experiments.md`.
- Heatmaps / session replay -- deployer extension (provider-specific).
- Attribution modeling (last-click vs multi-touch) -- deferred.
- Real-time alerting on event anomalies -- belongs to ops layer; deferred.
- Customer Data Platform (CDP) features -- deferred R25+.
