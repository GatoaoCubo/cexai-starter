---
kind: feature_template
feature_name: self_serve_onboarding
vertical: 17_saas_stack
round_added: 25
pillars: [P05, P12]
adr_019_packages: [tools/web/, governance/]
feature_dependencies: [feature_subscription_lifecycle, feature_crm]
brand_niche_constraints:
  - allow: [saas, freemium, b2b_saas, b2c_saas]
  - warn: [agency, services, ecommerce_one_time]
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in onboarding flow."
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
    description: "Drives onboarding steps selection."
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
    description: "Drives onboarding tone + length."
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
    description: "Onboarding UI language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: activation_steps
    type: list[str]
    description: "Ordered onboarding milestones (e.g., ['signup', 'verify_email', 'create_workspace', 'invite_team', 'first_api_call'])."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.activation_steps]
    constraints: {min_items: 1, max_items: 12}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: activation_definition
    type: str
    description: "Definition of 'activated' user (e.g., 'completed 3 of 5 activation_steps within 7 days')."
    filler_role: n06
    filler_stage: F3_INJECT
    context_hints: [brand_config.activation_definition]
    constraints: {min_length: 5, max_length: 200}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: trial_to_paid_target_rate
    type: float
    description: "Target % of trial users who convert to paid (for analytics dashboards)."
    filler_role: n06
    filler_stage: F3_INJECT
    context_hints: [brand_config.trial_to_paid_target_rate]
    constraints: {minimum: 0.0, maximum: 1.0}
    default_filler_strategy: use_default_value
    required: false
    default_value: 0.15
    rebind_allowed: true
---

# Feature Template: Self-Serve Onboarding

**Purpose**: turn signups into activated users without sales-team touch. The trial-to-paid funnel: signup -> activation milestones -> qualified trial -> conversion to paid.

---

## Architecture

```
visitor lands on /signup
  -> account creation (email + password OR OAuth)
  -> activation flow starts (per activation_steps open_var)
  -> milestones tracked in users.activation_progress
  -> trigger feature_subscription_lifecycle (state: trialing)
  -> drip via feature_messaging.md (email sequence)
  -> at activation_definition met: feature_analytics emits "trial_activated"
  -> at trial_end_at: convert OR cancel
```

---

## Activation step semantics

Each `activation_steps` entry is a discrete milestone. Recommended set:

| Step | Verifiable by |
|------|---------------|
| `signup` | User row exists + email_verified flag |
| `verify_email` | email_verified_at set |
| `create_workspace` | workspaces table has row owned by user |
| `invite_team` | team_invites table has at least 1 invite sent |
| `first_api_call` | usage_events has at least 1 event for this user |
| `first_paid_action` | usage that requires a paid feature (e.g., advanced report generation) |
| `connect_integration` | integrations table has at least 1 connected integration |
| `complete_setup` | setup_completed flag set in user_profile |

Deployer chooses which steps belong to THEIR product. Order matters -- they should be sequenced from easiest (signup) to most engagement-revealing (paid action).

---

## Activation definition

`activation_definition` is a deployer-defined threshold. Examples:

| Definition | When met |
|-----------|----------|
| "completed 3 of 5 activation_steps within 7 days" | 3 milestones done in first week |
| "made first API call within 14 days" | first_api_call timestamp <= 14d post-signup |
| "invited at least 1 team member" | invite_team milestone reached |

When met, user is classified `activated`. This is the leading indicator of trial-to-paid conversion.

---

## Email drip sequence

Default trial flow (deployer customizes per `target_audience`):

| Day | Email | Trigger |
|-----|-------|---------|
| 0 | Welcome + first action | On signup |
| 1 | Quick tip 1 (relevant to brand_niche) | Scheduled |
| 3 | "Have you tried X?" -- nudge to next activation step | If activation_steps not progressing |
| 7 | Trial midpoint -- showcase paid features | Scheduled |
| 10 | Activation reminder | If activation_definition not met |
| 12 | Trial-end approaching | Scheduled (2 days before trial_end_at) |
| 14 | Trial ended | At trial_end_at; CTA to add payment method |

Implemented via `feature_messaging.md` templates + `feature_subscription_lifecycle.md` trigger points.

---

## Conversion gates

The trial-to-paid conversion happens automatically per `feature_subscription_lifecycle.md`:
- If payment method on file at `trial_end_at`: auto-charge + transition to `active` + tier chosen during onboarding.
- If no payment method: prompt during last 3 days of trial; show in-app banner.
- If still no payment method at `trial_end_at`: transition to `cancelled` (not `paused` -- cancelled is permanent for trials).

---

## Tier selection during signup

Two patterns:

| Pattern | Behavior |
|---------|----------|
| **Self-select** | User picks tier at signup; trial starts on that tier; no charge until trial_end_at |
| **Discover** | User starts on free tier; nudges to upgrade emerge as they hit free-tier limits |

Deployer choice. Self-select common for B2B (customer pre-qualifies); Discover common for B2C (lower friction).

---

## Analytics events

| Event | When |
|-------|------|
| `signup_initiated` | Form submission |
| `signup_completed` | User row created |
| `email_verified` | email_verified_at set |
| `activation_step_completed` | Each step hit (with step name in metadata) |
| `trial_activated` | activation_definition met |
| `trial_to_paid_converted` | At trial_end_at, billing succeeds |
| `trial_cancelled` | At trial_end_at, no payment method or explicit cancel |

These feed `feature_analytics.md` SaaS override (which uses PostHog for this funnel).

---

## Integration contracts

- Provides to: `feature_subscription_lifecycle.md` (signal trial start, milestone completion).
- Provides to: `feature_crm.md` SaaS-override (lifecycle stage transitions: trial_signup -> trial_active -> paid_active).
- Consumes from: `feature_messaging.md` (drip sequence templates).
- Provides to: `feature_analytics.md` (funnel events).
- Audit via `kc_audit_event.md` (signup events are PII-relevant; long retention).

---

## Out of scope

- A/B testing onboarding variants -- deferred R26+ `feature_experiments.md`.
- In-app product tour (tooltips, hotspots) -- deployer extension; component-specific.
- White-glove sales-assisted onboarding -- belongs to `feature_crm.md` enterprise track.
- Free trial extensions for VIPs -- admin action (subscription_lifecycle `trial_extended`); not part of self-serve.
