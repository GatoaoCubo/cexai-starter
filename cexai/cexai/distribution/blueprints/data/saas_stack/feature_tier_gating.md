---
kind: feature_template
feature_name: tier_gating
vertical: 17_saas_stack
round_added: 25
pillars: [P09, P11]
adr_019_packages: [governance/, foundation/]
feature_dependencies: [feature_subscription_lifecycle]
brand_niche_constraints:
  - allow: [saas, freemium, tiered_subscription, api_platform]
  - warn: [one_time_purchase, services, agency]
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in upgrade prompts."
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
    description: "Drives feature-gate categorization."
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
    description: "Drives upgrade-prompt tone (pushy vs gentle)."
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
    description: "Upgrade prompt language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: tier_feature_matrix
    type: dict
    description: "Per-tier feature + limit matrix (e.g., {free: {api_calls_monthly: 1000, workspaces: 1, custom_branding: false}, ...})."
    filler_role: n06
    filler_stage: F3_INJECT
    context_hints: [brand_config.tier_feature_matrix]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: gate_behavior_default
    type: enum
    description: "Default behavior when a tier-gated feature is accessed by an insufficient tier."
    filler_role: n06
    filler_stage: F3_INJECT
    allowed_values: ["hard_block", "soft_block_with_upgrade_cta", "preview_then_upgrade", "trial_unlock"]
    context_hints: [brand_config.gate_behavior_default]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "soft_block_with_upgrade_cta"
    rebind_allowed: true
---

# Feature Template: Tier Gating

**Purpose**: per-tier feature flags + limits. Determines which features each subscription tier can access, and what happens when a user attempts to use a feature beyond their tier.

---

## Architecture

```
user attempts to access feature X
  -> tier_gate.check(user.subscription.tier, feature_id="X")
  -> read tier_feature_matrix
  -> if allowed: proceed
  -> if not allowed: apply gate_behavior (block / soft_block / preview / trial_unlock)
  -> emit analytics event (feature_gated)
```

---

## Tier feature matrix

```yaml
tier_feature_matrix:
  free:
    api_calls_monthly: 1000          # numeric limit
    workspaces: 1
    team_members_per_workspace: 1
    custom_branding: false           # boolean gate
    advanced_analytics: false
    sso: false
    audit_log_retention_days: 30
  starter:
    api_calls_monthly: 10000
    workspaces: 3
    team_members_per_workspace: 5
    custom_branding: false
    advanced_analytics: true
    sso: false
    audit_log_retention_days: 90
  pro:
    api_calls_monthly: 100000
    workspaces: unlimited            # special value -> no limit
    team_members_per_workspace: 25
    custom_branding: true
    advanced_analytics: true
    sso: false
    audit_log_retention_days: 365
  team:
    api_calls_monthly: 500000
    workspaces: unlimited
    team_members_per_workspace: 100
    custom_branding: true
    advanced_analytics: true
    sso: true
    audit_log_retention_days: 1095
  enterprise:
    api_calls_monthly: unlimited
    workspaces: unlimited
    team_members_per_workspace: unlimited
    custom_branding: true
    advanced_analytics: true
    sso: true
    audit_log_retention_days: indefinite  # special value -> no rotation
    custom_integrations: true        # enterprise-only feature
    dedicated_support: true
```

Special values: `unlimited`, `indefinite`. Deployer extends.

---

## Gate types

| Type | Examples | Check pattern |
|------|----------|---------------|
| **numeric limit** | api_calls_monthly, workspaces, team_members | Check current usage from `feature_usage_metering.md` vs limit |
| **boolean gate** | sso, custom_branding, advanced_analytics | True if allowed; False if blocked |
| **categorical** | support_tier (community / email / dedicated) | String matching expected level |

---

## Gate behaviors

When a user attempts to access a gated feature:

| Behavior | UX |
|----------|-----|
| `hard_block` | Feature is invisible to ineligible tiers; no UI mention. Reserved for VERY-specific features that shouldn't tempt. |
| `soft_block_with_upgrade_cta` | Feature visible but disabled; click triggers upgrade modal showing required tier + price. DEFAULT. |
| `preview_then_upgrade` | Feature shows a 7-day preview (e.g., advanced analytics dashboard rendered but watermarked); upgrade CTA replaces watermark. |
| `trial_unlock` | Allow N free uses to taste the feature; on N+1, gate kicks in. Useful for hard-to-evaluate features. |

Deployer chooses default + per-feature overrides.

---

## Implementation pattern (spec only)

```python
# Pseudo-Python
class TierGate:
    def check_numeric(self, subscription_id, feature_id, current_value):
        tier = lookup_tier(subscription_id)
        limit = tier_feature_matrix[tier][feature_id]
        if limit == "unlimited":
            return Decision(allowed=True)
        if current_value >= limit:
            return Decision(allowed=False, reason="quota_exceeded",
                            upgrade_to=next_tier_with(feature_id, current_value + 1))
        return Decision(allowed=True)

    def check_boolean(self, subscription_id, feature_id):
        tier = lookup_tier(subscription_id)
        return Decision(allowed=tier_feature_matrix[tier][feature_id])
```

Decisions emit `audit_event` (sampled at low verbosity) + `feature_gated` analytics event.

---

## Upgrade CTA UX

When gate_behavior triggers an upgrade prompt:

```
Modal:
  "This feature requires the <required_tier> tier."
  [show feature benefits: 3-5 bullets]
  [show price: $<tier_price>/month]
  [CTA: "Upgrade to <required_tier>"] -> billing portal
  [secondary: "Maybe later"] -> dismiss, log impression
```

Tone matches `target_audience` open_var. For dev-tools SaaS: more transparent + technical. For end-consumer SaaS: more aspirational + benefit-focused.

---

## Integration contracts

- Consumes from: `feature_subscription_lifecycle.md` (user's current tier).
- Consumes from: `feature_usage_metering.md` (numeric usage vs limits).
- Provides upgrade CTAs to: `feature_frontend.md` + `feature_admin_console.md`.
- Provides analytics events to: `feature_analytics.md` (`feature_gated`, `upgrade_cta_shown`, `upgrade_cta_clicked`).
- Audit via `kc_audit_event.md` (sampled).

---

## Out of scope

- Custom enterprise contracts (negotiated per-deployment) -- handled outside the matrix; deployer overrides per customer.
- Time-limited trial unlocks beyond tier_unlock behavior -- deferred R26+ `feature_promotions.md`.
- A/B testing upgrade CTAs -- R26+.
- Reverse upgrade prompts ("downgrade to free if you don't use feature X for 60 days") -- deferred.
