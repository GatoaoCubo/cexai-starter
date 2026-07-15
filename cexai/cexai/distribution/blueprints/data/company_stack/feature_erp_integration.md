---
kind: feature_template
feature_name: erp_integration
vertical: 16_company_stack
round_added: 22
pillars: [P04, P09]
adr_019_packages: [tools/]
feature_dependencies: [feature_catalog]
brand_niche_constraints:
  - allow: [e-commerce, retail, b2b_distribution, marketplace]
  - warn: [saas, agency, creator, services]
open_vars:
  - name: brand_name
    type: str
    description: "Brand display in ERP records."
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
    description: "ERP type often depends on niche (Bling for BR retail, NetSuite for enterprise, etc.)."
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
    description: "Drives currency + locale defaults."
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
    description: "Product description language in ERP sync."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: erp_provider
    type: enum
    description: "ERP backend."
    filler_role: n05
    filler_stage: F3_INJECT
    allowed_values: ["bling", "omie", "tiny", "conta_azul", "netsuite", "sap_business_one", "quickbooks", "xero", "none"]
    context_hints: [brand_config.erp_provider]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: false
  - name: sync_direction
    type: enum
    description: "Direction of product sync between catalog and ERP."
    filler_role: n05
    filler_stage: F3_INJECT
    allowed_values: ["push_to_erp", "pull_from_erp", "bidirectional"]
    context_hints: [brand_config.sync_direction]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "push_to_erp"
    rebind_allowed: true
---

# Feature Template: ERP Integration

**Purpose**: a one-way or bidirectional product sync between the catalog (`feature_catalog.md`) and an external ERP system (Bling, Omie, Tiny, Conta Azul, NetSuite, etc.). Handles SKU, price, image, stock-level data flow.

---

## Adapter pattern

Each ERP provider has its own API surface. This template defines the ADAPTER INTERFACE; deployers implement per-provider adapters.

```yaml
# Adapter interface (Python typing)
class ERPAdapter(ABC):
    @abstractmethod
    def push_product(self, product: ProductDict) -> ERPSyncResult: ...
    @abstractmethod
    def pull_product(self, erp_id: str) -> ProductDict: ...
    @abstractmethod
    def list_drift(self) -> List[DriftRow]: ...
    @abstractmethod
    def audit(self) -> AuditReport: ...
```

Deployer implements `BlingAdapter`, `OmieAdapter`, etc. Each adapter knows its provider's API.

---

## Edge functions

| Function | Purpose |
|----------|---------|
| `sync_product` | Push or pull a single product. Body: `{ operation: 'update' \| 'create', product_id, erp_id? }` |
| `fix_skus` | Backfill SKU/price/title from CEX to ERP. Batch operation. |
| `audit` | Diff CEX vs ERP; report drift to `drift_report` table. |

---

## Drift handling

| Drift type | Default action |
|-----------|----------------|
| Catalog has product, ERP does not | Auto-create in ERP (if sync_direction permits push). |
| ERP has product, catalog does not | Manual review (admin decides import or ignore). |
| Same SKU, different name | Flag in drift report; admin resolves. |
| Same SKU, different price | Flag; depending on `pricing_source_of_truth` config, one side wins. |
| ERP product is `inactive`, catalog `active` | Sync inactivation to catalog. |

`pricing_source_of_truth` open_var (extension): which side wins on price disagreement. Default: catalog (CEXAI-side).

---

## Schema extensions

Catalog table (`products`) carries `erp_*` extension fields per provider:

```yaml
extra_columns:
  - bling_id        # for Bling
  - bling_synced_at # last sync timestamp
  - omie_id         # for Omie
  - omie_synced_at
  - <provider>_id   # generic pattern
  - <provider>_synced_at
```

Deployer extends per chosen `erp_provider`.

---

## Auth + secrets

ERP API keys stored in BaaS secret vault. Edge function reads via vault.decrypted_secrets (Supabase pattern) or equivalent.

NEVER store keys in environment variables on a hosted SPA platform. NEVER commit keys to source control.

---

## Niche-mismatch handling

For non-physical-goods niches (SaaS, agency, creator):
- `FeatureNotApplicableWarning` emitted.
- Deployer may still wire this template if they sync SaaS products (e.g., subscription tiers) to an ERP, but the typical e-commerce semantics don't apply.

---

## Integration contracts

- Consumes from: `feature_catalog.md` (product data + image URLs).
- Provides to: ERP system via provider adapter.
- Provides to: `feature_admin_console.md` (drift report renders in `/admin/integracoes`).
- Optionally consumes from: `feature_pricing_engine.md` (derived B2B prices for push to ERP).

---

## Out of scope

- Order sync (orders flow ERP -> CEXAI separately; deferred to `feature_orders_sync.md` R23).
- Inventory/stock-level real-time sync (deployer extends; v1 syncs only on `fix_skus` runs).
- Multi-ERP sync (one ERP at a time per deployment).
- Invoicing / tax calculation (ERP handles natively).
