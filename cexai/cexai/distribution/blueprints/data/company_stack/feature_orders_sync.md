---
kind: feature_template
feature_name: orders_sync
vertical: 16_company_stack
round_added: 23
pillars: [P04, P09]
adr_019_packages: [tools/, foundation/]
feature_dependencies: [feature_catalog, feature_erp_integration]
brand_niche_constraints:
  - allow: [e-commerce, retail, b2b_distribution, marketplace, subscription_box]
  - warn: [saas, agency, creator, services]
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in order audit logs."
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
    description: "Drives fulfillment workflow defaults."
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
    description: "Drives shipping/fulfillment SLA defaults."
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
    description: "Order notifications language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: order_sources
    type: list[str]
    description: "Where orders originate (e.g., ['direct_checkout', 'marketplace_mercadolivre', 'erp_bling', 'b2b_dealer'])."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.order_sources]
    constraints: {min_items: 1}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: order_lifecycle_stages
    type: list[str]
    description: "Ordered lifecycle stages."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.order_lifecycle_stages]
    constraints: {min_items: 2, max_items: 12}
    default_filler_strategy: use_default_value
    required: false
    default_value: ["pending", "paid", "fulfilling", "shipped", "delivered", "completed", "cancelled", "refunded"]
    rebind_allowed: true
  - name: fulfillment_provider
    type: enum
    description: "Shipping/logistics integration."
    filler_role: n05
    filler_stage: F3_INJECT
    allowed_values: ["correios", "melhor_envio", "shippo", "shipstation", "easyship", "manual", "marketplace_managed"]
    context_hints: [brand_config.fulfillment_provider]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "manual"
    rebind_allowed: true
---

# Feature Template: Orders Sync

**Purpose**: unified orders lifecycle layer that pulls orders from multiple sources (direct checkout, marketplaces, ERP, B2B dealer flow) into a single source of truth + drives fulfillment.

---

## Architecture

```
Order sources (parallel):
  - direct_checkout (from feature_billing.md webhook on payment success)
  - marketplace orders (from feature_marketplace_integration.md pull_orders)
  - erp orders (from feature_erp_integration.md if ERP is order-of-record)
  - b2b_dealer orders (from CRM negotiations converted)
  -> unified orders table (one row per order, source tagged)
  -> lifecycle state machine (order_lifecycle_stages)
  -> fulfillment dispatch (fulfillment_provider)
  -> notifications (CRM contact via feature_messaging.md)
  -> downstream sync (ERP receives the order; marketplace gets status updates)
```

---

## Unified order schema

```yaml
table: orders   # extends feature_billing.md orders table
columns:
  - id (uuid)
  - source (enum from order_sources)
  - external_id (per-source identifier; e.g., marketplace order ID)
  - customer_id (FK to crm_contacts; may be null for marketplace orders without CRM record)
  - line_items (jsonb: [{product_id, quantity, unit_price, total}, ...])
  - subtotal / tax / shipping / total
  - currency
  - status (enum from order_lifecycle_stages)
  - shipping_address (jsonb)
  - billing_address (jsonb; may be same as shipping)
  - tracking_number (nullable)
  - fulfillment_provider_used (nullable; defaults to feature_orders_sync open_var)
  - fulfillment_started_at / shipped_at / delivered_at (iso_datetime)
  - cancellation_reason (nullable)
  - refund_reason (nullable)
  - notes (markdown)
  - created_at / updated_at
```

---

## Lifecycle state machine

| From | To | Trigger |
|------|-----|---------|
| `pending` | `paid` | feature_billing.md webhook: payment_succeeded |
| `pending` | `cancelled` | timeout (default 24h) OR explicit customer cancellation |
| `paid` | `fulfilling` | operator marks fulfillment started OR auto on payment if drop-ship |
| `fulfilling` | `shipped` | fulfillment_provider returns tracking_number |
| `shipped` | `delivered` | fulfillment_provider delivery confirmation OR manual marking |
| `delivered` | `completed` | manual close OR auto after N days post-delivery |
| `paid` -> | `refunded` | feature_billing.md refund event |
| any pre-shipped | `cancelled` | customer/admin cancellation |

Backward transitions: NOT permitted (e.g., `shipped` -> `paid` is invalid). Re-shipment requires a new related order.

---

## Source-specific behaviors

### `direct_checkout`
- Originates from `feature_billing.md` webhook.
- customer_id auto-resolved from billing event.
- Highest data quality (deployer controls the flow).

### `marketplace_*`
- Originates from `feature_marketplace_integration.md` pull_orders cron.
- customer_id may be null (some marketplaces don't expose customer email/phone).
- Polling interval: default 30min via cron; configurable.
- DEDUP via (marketplace, external_id) tuple -- same order pulled twice is idempotent.

### `erp_*`
- Originates from `feature_erp_integration.md`.
- Useful when ERP is the order-of-record (e.g., distributor whose orders enter via salesperson).
- Sync direction is configurable (push CEXAI->ERP or pull ERP->CEXAI).

### `b2b_dealer`
- Originates from CRM negotiation converted to order (`feature_crm.md` lifecycle stage `won` triggers).
- Typically large quantity; pricing uses `b2b` tier from `feature_pricing_engine.md`.

---

## Fulfillment dispatch

| Provider | Integration |
|----------|-------------|
| `correios` (Brazil postal) | Correios API or via `melhor_envio`/`shippo` aggregator |
| `melhor_envio` | Brazilian shipping aggregator (multi-carrier) |
| `shippo` | International shipping aggregator |
| `shipstation` | E-commerce shipping platform |
| `easyship` | International, automated label creation |
| `manual` | No API integration; operator manually labels + ships |
| `marketplace_managed` | Marketplace handles fulfillment (Mercado Envios, FBA) |

Selection per-order: deployer config OR per-source rule (e.g., marketplace orders use `marketplace_managed`; direct_checkout uses `melhor_envio`).

---

## Notifications

Lifecycle transitions notify the customer via `feature_messaging.md`:

| Transition | Notification |
|-----------|--------------|
| `paid` | Order confirmation (email/whatsapp) |
| `shipped` | Tracking number + ETA |
| `delivered` | Delivery confirmation + review request |
| `cancelled` | Cancellation notice + refund info if applicable |
| `refunded` | Refund confirmation + ETA on credit |

Template + channel selection deployer-configurable per stage.

---

## Audit pattern

Every state transition emits `audit_event`:
- `event_type: order_*` (specific: `order_created`, `order_paid`, `order_fulfilling_started`, `order_shipped`, `order_delivered`, `order_cancelled`, `order_refunded`)
- `retention_class: long_3y` (commercial transaction records)

---

## Cross-source dedup

When an order MAY arrive from multiple sources (e.g., direct_checkout creates the order, ERP echoes it back as `erp_*`), the system dedups via:
1. External_id matching when available.
2. Composite (customer_id, line_items_hash, time_window) matching.
3. Operator manual merge UI for ambiguous cases.

Dedup is critical -- duplicate orders cause double-shipping + double-revenue-counting.

---

## Niche-mismatch handling

| Niche | Compatibility |
|-------|--------------|
| saas, agency, creator, services | WARN -- non-physical-goods niches typically don't have orders in the e-commerce sense; SaaS uses subscriptions (`feature_billing.md`), not orders. |

---

## Integration contracts

- Consumes from: `feature_billing.md` (direct_checkout source), `feature_marketplace_integration.md` (marketplace source), `feature_erp_integration.md` (erp source), `feature_crm.md` (b2b_dealer source via won-stage transitions).
- Provides notifications via: `feature_messaging.md`.
- Provides fulfillment dispatch via: chosen `fulfillment_provider`.
- Provides revenue + lifecycle events to: `feature_analytics.md`.
- Audit via: `kc_audit_event.md` with `retention_class: long_3y`.

---

## Out of scope

- Returns merchandise authorization (RMA) workflow -- deferred R24+ `feature_returns.md`.
- Inventory reservation during checkout -- deferred R24+ `feature_inventory.md`.
- Multi-warehouse routing -- deferred R24+.
- Bulk order import via CSV -- deployer extension if needed.
- Order splitting (multiple shipments for one order) -- deferred R24+.
