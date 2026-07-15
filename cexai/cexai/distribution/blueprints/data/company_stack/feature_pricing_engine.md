---
kind: feature_template
feature_name: pricing_engine
vertical: 16_company_stack
round_added: 22
pillars: [P11, P06]
adr_019_packages: [foundation/, governance/]
feature_dependencies: [feature_catalog]
brand_niche_constraints: null
open_vars:
  - name: brand_name
    type: str
    description: "Brand name used in displayed pricing context."
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
    description: "Drives pricing model selection (subscription vs unit vs project)."
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
    description: "B2B vs B2C influences which prices are exposed where."
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
    description: "Default language for displayed pricing labels."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: pricing_model
    type: enum
    description: "Overall pricing approach."
    filler_role: n06
    filler_stage: F3_INJECT
    allowed_values: ["unit_with_tiers", "subscription", "project_based", "usage_based", "freemium", "marketplace_takerate"]
    context_hints: [brand_config.pricing_model]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: false
  - name: tier_multipliers
    type: dict
    description: "For unit_with_tiers model: map of tier name to cost multiplier (e.g., {'b2b': 1.51, 'b2c': 1.85})."
    filler_role: n06
    filler_stage: F3_INJECT
    context_hints: [brand_config.tier_multipliers]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: {"b2c": 2.0}
    rebind_allowed: true
  - name: fixed_kit_prices
    type: dict
    description: "Named fixed-price bundles (e.g., {'starter_kit': 374.90, 'pro_kit': 999.00}). Overrides per-unit pricing for the named bundle."
    filler_role: n06
    filler_stage: F3_INJECT
    context_hints: [brand_config.fixed_kit_prices]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: {}
    rebind_allowed: true
---

# Feature Template: Pricing Engine

**Purpose**: derive displayable prices from internal `cost_price` per product, per audience tier, and per pricing model. Supports per-unit multipliers, subscription tiers, fixed bundle prices, and rendering rules.

---

## Pricing models

The deployer chooses ONE model per deployment (cannot mix at deployment level; but a single deployment may have BOTH `unit_with_tiers` products AND `fixed_kit_prices` bundles -- they are complementary).

| Model | Derivation |
|-------|-----------|
| `unit_with_tiers` | `displayed_price = cost_price * tier_multipliers[tier]`. Renders different prices on B2B vs B2C surfaces. |
| `subscription` | `displayed_price = subscription_plan.monthly_amount`. No multiplier on cost; price is published in plan table. |
| `project_based` | No catalog price; price quoted per project. Pricing engine returns "quote on request" for public pages. |
| `usage_based` | `displayed_price = base_fee + (usage_units * per_unit_rate)`. Computed at billing time, not display time. |
| `freemium` | Two tiers: free (price = 0) + paid (price per `tier_multipliers`). |
| `marketplace_takerate` | `displayed_price = product_price`. Platform takes a percentage cut at transaction time. |

---

## Tier multipliers (for `unit_with_tiers`)

Stored in `tier_multipliers` open_var as a dict mapping tier name -> multiplier.

Example (B2B + B2C):
```yaml
tier_multipliers:
  b2b: 1.51
  b2c: 1.85
```

Derivation:
- Catalog stores `cost_price` only.
- B2B page renders `cost_price * 1.51`.
- B2C page renders `cost_price * 1.85`.
- NEVER display `cost_price` publicly.

Deployer with more tiers extends: `b2b_distributor: 1.35`, `b2b_retailer: 1.51`, `b2c: 1.85`, `b2c_premium: 2.25`.

---

## Fixed kit prices

For bundle deals that override per-unit math:

```yaml
fixed_kit_prices:
  starter_kit_15_items: 374.90
  growth_kit_50_items: 1199.00
```

Display logic: bundle page shows `fixed_kit_prices[bundle_id]`, NOT `sum(item.b2b_price for item in bundle)`. The fixed price is typically BELOW the sum-of-units-at-b2b-rate to incentivize the bundle.

---

## Trust + data hygiene

| Concern | Pattern |
|---------|---------|
| `cost_price` accuracy | Deployer maintains. Validation: `cost_price > 0` + `cost_price < displayed_price`. |
| Inverted-cost data drift | Some legacy SKUs may have `price < cost_price` (data error). Pricing engine emits `PricingDataIntegrityWarning` on render if detected; recommend admin review. |
| Currency consistency | All prices in catalog use `pricing_currency` open_var (from `feature_catalog.md`). Multi-currency pricing is OUT of v1 scope; deferred to R23. |

---

## Rendering rules

| Surface | Tier displayed |
|---------|---------------|
| Public B2B page (`/b2b`, `/b2b/*`) | `tier_multipliers.b2b` |
| Public B2C page (`/`, `/b2c`, `/catalogo`) | `tier_multipliers.b2c` |
| Admin catalog | All tiers (table with columns per tier) |
| Marketplace listings (`feature_marketplace_integration.md`) | Per `pricing_strategy` open_var |
| ERP push (`feature_erp_integration.md`) | `cost_price` + `b2b` typically |
| Public bundle landing (e.g., `/b2b/starter-kit`) | `fixed_kit_prices[kit_slug]` (overrides per-unit) |

---

## Integration contracts

- Consumes from: `feature_catalog.md` (cost_price + currency).
- Provides to: `feature_frontend.md` (rendered prices on public pages), `feature_admin_console.md` (admin tables), `feature_marketplace_integration.md` (marketplace prices), `feature_erp_integration.md` (ERP push values).
- Receives audience context from session (B2B vs B2C inferred from auth state + URL path).

---

## Out of scope

- Dynamic pricing (price varies by demand) -- deferred R23.
- Promotions / coupons -- deferred R23 `feature_promotions.md`.
- Tax computation (deployer integrates a tax service or handles in ERP).
- Currency conversion (single-currency deployment in v1).
- Per-customer custom pricing (deferred R23; would extend `tier_multipliers` per `customer_segment`).
