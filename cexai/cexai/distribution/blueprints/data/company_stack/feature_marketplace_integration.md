---
kind: feature_template
feature_name: marketplace_integration
vertical: 16_company_stack
round_added: 22
pillars: [P04, P09]
adr_019_packages: [tools/]
feature_dependencies: [feature_catalog, feature_erp_integration]
brand_niche_constraints:
  - allow: [e-commerce, retail, b2b_distribution]
  - warn: [saas, agency, creator, services, subscription_box]
open_vars:
  - name: brand_name
    type: str
    description: "Seller display name in marketplaces."
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
    description: "Drives marketplace category selection."
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
    description: "Drives listing copy."
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
    description: "Listing language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: enabled_marketplaces
    type: list[str]
    description: "Marketplace platforms to sync to (e.g., ['mercado_livre', 'shopify', 'amazon', 'shopee', 'magalu'])."
    filler_role: user
    filler_stage: F4_REASON
    allowed_values: ["mercado_livre", "shopify", "amazon", "shopee", "magalu", "americanas", "magazineluiza", "etsy", "ebay"]
    context_hints: [brand_config.enabled_marketplaces]
    constraints: {min_items: 1}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: pricing_strategy
    type: enum
    description: "How marketplace prices relate to catalog price."
    filler_role: n06
    filler_stage: F3_INJECT
    allowed_values: ["catalog_b2c_price", "catalog_b2c_with_marketplace_markup", "custom_per_marketplace"]
    context_hints: [brand_config.pricing_strategy]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "catalog_b2c_price"
    rebind_allowed: true
  - name: oauth_token_storage
    type: enum
    description: "Where marketplace OAuth refresh tokens are stored."
    filler_role: n05
    filler_stage: F3_INJECT
    allowed_values: ["supabase_vault", "aws_secrets_manager", "hashicorp_vault", "encrypted_db_column"]
    context_hints: [brand_config.oauth_token_storage]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "supabase_vault"
    rebind_allowed: true
---

# Feature Template: Marketplace Integration

**Purpose**: a multi-marketplace sync that publishes products to external marketplaces (Mercado Livre, Shopify, Amazon, Shopee, etc.) and pulls order data back. Per-marketplace adapter pattern.

---

## Adapter pattern

Same shape as `feature_erp_integration.md` -- one adapter per marketplace, sharing a common interface.

```yaml
# Adapter interface
class MarketplaceAdapter(ABC):
    @abstractmethod
    def publish_listing(self, product: ProductDict, marketplace_config: Dict) -> ListingResult: ...
    @abstractmethod
    def pull_orders(self, since: datetime) -> List[OrderDict]: ...
    @abstractmethod
    def update_inventory(self, sku: str, qty: int) -> None: ...
    @abstractmethod
    def refresh_oauth_token(self) -> str: ...
```

---

## Schema extensions

```yaml
# Catalog table extensions (per marketplace)
extra_columns:
  - meli_id            # Mercado Livre listing ID
  - meli_status        # active | paused | closed
  - meli_synced_at
  - shopify_id
  - shopify_status
  - shopify_synced_at
  - amazon_asin
  - amazon_status
  - amazon_synced_at
  - <marketplace>_id   # generic
```

```yaml
# Orders pulled from marketplaces (per marketplace)
table: marketplace_orders
columns:
  - id                 # uuid PK (CEXAI-internal)
  - marketplace        # source marketplace name
  - external_order_id  # marketplace's order ID
  - product_id         # FK to products (resolved via marketplace listing ID)
  - quantity
  - unit_price
  - total
  - currency
  - buyer_info         # jsonb
  - shipping_info      # jsonb
  - status             # pending | paid | shipped | delivered | cancelled
  - created_at_marketplace
  - synced_at
```

---

## OAuth handling

Most marketplace APIs use OAuth 2.0 with refresh tokens. Token lifecycle:

1. Deployer connects via OAuth flow in `/admin/integracoes`.
2. Refresh token stored encrypted in `oauth_token_storage`.
3. Background job refreshes the access token periodically (before expiry).
4. Token rotation logged in audit_event.

NEVER store unencrypted tokens in DB columns or environment variables.

---

## Cross-marketplace dedup

A product may sync to multiple marketplaces simultaneously. The `(product_id, marketplace)` tuple is unique per listing -- no double-listing within the same marketplace, but parallel listings across marketplaces are expected.

---

## Pricing strategy

| Strategy | Behavior |
|----------|----------|
| `catalog_b2c_price` | Marketplace price = catalog B2C price (from `feature_pricing_engine.md`). |
| `catalog_b2c_with_marketplace_markup` | Marketplace price = catalog B2C * (1 + marketplace_markup). Per-marketplace markup config. |
| `custom_per_marketplace` | Deployer sets explicit per-marketplace price (no derivation). |

---

## Niche-mismatch handling

For non-physical-goods niches: `FeatureNotApplicableWarning`. SaaS/agency typically have no marketplaces.

---

## Integration contracts

- Consumes from: `feature_catalog.md` (product data) + `feature_erp_integration.md` (SKU normalization).
- Provides to: `feature_admin_console.md` (`/admin/integracoes` page).
- Provides to: deployer's order-fulfillment workflow (marketplace_orders feed).
- Pulls orders into CEXAI; orders may flow onward to ERP via `feature_erp_integration.md`.

---

## Out of scope

- Listing optimization / SEO (deployer concern; marketplace-specific best practices).
- Returns / refunds workflow (marketplace handles natively).
- Bulk feed uploads (deployer extension if marketplace supports CSV/XML feeds).
- Cross-border tax + shipping (marketplace handles, or deployer integrates a tax service).
