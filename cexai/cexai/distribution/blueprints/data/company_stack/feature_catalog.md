---
kind: feature_template
feature_name: catalog
vertical: 16_company_stack
round_added: 22
pillars: [P01, P05, P06]
adr_019_packages: [tools/web/, foundation/]
feature_dependencies: [feature_admin_console]
brand_niche_constraints:
  - allow: [e-commerce, retail, marketplace, b2b_distribution, subscription_box]
  - warn: [saas, agency, creator]
open_vars:
  - name: brand_name
    type: str
    description: "Brand display name (appears in product page OG tags)."
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
    description: "Drives product taxonomy + SEO keyword bias."
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
    description: "Drives product description tone + bundle suggestions."
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
    description: "Primary product copy language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: product_taxonomy
    type: dict
    description: "Category tree for the catalog. Keys are slugs, values describe display label + subcategory list."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.product_taxonomy]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: pricing_currency
    type: enum
    description: "Currency code for product prices (ISO 4217)."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["BRL", "USD", "EUR", "GBP", "JPY", "CNY", "MXN", "ARS"]
    context_hints: [brand_config.pricing_currency]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "USD"
    rebind_allowed: false
  - name: media_storage_pattern
    type: enum
    description: "Where product media is stored."
    filler_role: n05
    filler_stage: F3_INJECT
    allowed_values: ["supabase_storage", "s3", "r2", "cloudinary", "local_filesystem"]
    context_hints: [brand_config.media_storage_pattern]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "supabase_storage"
    rebind_allowed: true
---

# Feature Template: Catalog

**Purpose**: a product catalog with admin CRUD, public product pages, and media management. Default schema is e-commerce-shaped (SKUs, prices, images). SaaS/agency deployers receive a warning per `brand_niche_constraints`.

---

## Data schema (recommended)

```yaml
# Product schema (placeholder; deployer adjusts per their BaaS)
table: products
columns:
  - name: id                  # uuid PK
  - name: slug                # unique, URL-safe
  - name: name                # display name
  - name: description         # long-form text/markdown
  - name: status              # enum: draft | active | archived
  - name: price               # numeric, in pricing_currency open_var
  - name: cost_price          # numeric, internal cost; NEVER displayed publicly
  - name: images              # text[] / list of media_storage_pattern URLs
  - name: category_slug       # FK to product_taxonomy
  - name: bling_*             # extension fields for ERP integration (feature_erp_integration.md)
  - name: meli_*              # extension fields for marketplace (feature_marketplace_integration.md)
  - name: media_kit_*         # extension fields for content factory (feature_content_factory.md)
  - name: created_at
  - name: updated_at
```

Deployer adjusts column names per language + niche.

---

## Admin pages

| Route | Component | Purpose |
|-------|-----------|---------|
| `/admin/produtos` (or `/admin/products`) | ProductsAdmin | Catalog CRUD table with filters |
| `/admin/produtos/novo` `/:id/editar` | ProductForm | Single-product form: name, slug, description, price, images, category |

Form integrates with `media_storage_pattern` open_var (uploads land in the chosen storage backend).

---

## Public pages

| Route | Component | Purpose |
|-------|-----------|---------|
| `/catalogo` (or `/catalog`) | CatalogPage | Category browse, filterable grid |
| `/produtos/:slug` (or `/products/:slug`) | ProductDetail | Single product page with SEO + structured data |

Each public product page emits `Product` schema.org JSON-LD with `name`, `description`, `image`, `offers.price`, `offers.priceCurrency` (from `pricing_currency`), `brand.name` (from `brand_name`).

---

## Media management

| Concern | Pattern |
|---------|---------|
| Upload | Admin form uploads to `media_storage_pattern` backend; returns public URL. |
| Public URL prefix | Deployer-config (e.g., Supabase Storage uses `<project>.supabase.co/storage/v1/object/public/`). |
| Multiple images per product | Stored as ordered array. First image is primary. |
| Image optimization | Deployer's CDN responsibility; recommend WebP + responsive srcset on public pages. |

---

## Pricing integration

Catalog stores `price` + `cost_price`. The displayed prices on B2B vs B2C pages are derived via `feature_pricing_engine.md` (multipliers applied at render time, not at storage time). NEVER display `cost_price` on public surfaces.

---

## Integration contracts

- Provides product data to: `feature_content_factory.md` (media kit per product), `feature_publishing.md` (product-feature campaigns), `feature_erp_integration.md` (sync to ERP), `feature_marketplace_integration.md` (sync to marketplaces).
- Consumes from: `feature_admin_console.md` (auth + protected routes), `feature_pricing_engine.md` (price derivation at render time).
- Brand config -> filled open_vars -> rendered in product detail SEO/OG.

---

## Niche-mismatch handling

For `brand_niche` outside the `allow` list (e.g., `"SaaS"`):
- `FeatureNotApplicableWarning` emitted.
- Catalog still deploys but with `status: deprecated_for_niche` flag.
- SaaS deployers typically replace catalog with `feature_pricing_engine.md` standalone + a billing template (R23 deferred).

---

## Out of scope

- Inventory/stock management (deployer extends or integrates with ERP via `feature_erp_integration.md`).
- Product reviews / ratings (deferred to R23 `feature_reviews.md`).
- Variant SKUs (size, color, etc.) -- simple SKUs in v1; variants in R23.
- Cart + checkout (handled by hosted commerce platform or deployer's chosen e-commerce engine).
