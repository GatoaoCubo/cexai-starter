---
kind: feature_template
feature_name: admin_console
vertical: 16_company_stack
round_added: 22
pillars: [P02, P05, P09]
adr_019_packages: [tools/web/, governance/rbac/]
feature_dependencies: [feature_frontend]
brand_niche_constraints: null
open_vars:
  - name: brand_name
    type: str
    description: "Brand display name in admin header."
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
    description: "Drives which admin pages are visible (e.g., e-commerce shows catalog; SaaS hides it)."
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
    description: "Drives admin terminology (e.g., 'leads' for B2B vs 'subscribers' for SaaS)."
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
    description: "Primary admin UI language."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: admin_role_names
    type: list[str]
    description: "Role names recognized by the auth gate. The 'admin' role is mandatory; deployer may add custom roles."
    filler_role: n05
    filler_stage: F3_INJECT
    context_hints: [brand_config.admin_role_names]
    constraints: {min_items: 1}
    default_filler_strategy: use_default_value
    required: false
    default_value: ["admin"]
    rebind_allowed: true
  - name: enabled_admin_modules
    type: list[str]
    description: "Which admin modules are wired (e.g., ['dashboard', 'catalog', 'crm']). Drives nav sidebar items."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.enabled_admin_modules]
    constraints: {min_items: 1}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
---

# Feature Template: Admin Console

**Purpose**: an admin surface gated by auth + role, with a modular page set that the deployer enables per their niche.

---

## Architecture

| Layer | Pattern |
|-------|---------|
| Auth backend | Supabase Auth, Auth0, Clerk, or equivalent OAuth/email+password provider with role table. |
| Role gate | A `user_roles` table (or equivalent) mapping `user_id -> role`. Admin gate = `role IN admin_role_names` (open_var). |
| Protected route | A `ProtectedRoute` component reading the role from the auth provider; redirects unauthorized to `/login`. |
| Layout wrapper | `AdminLayout` wraps every admin page (sidebar nav + header + breadcrumbs). |
| Module enablement | Sidebar items derived from `enabled_admin_modules` open_var. |

---

## Standard admin page set (modular)

The deployer enables a subset via `enabled_admin_modules`. Each module corresponds to one feature template (when present in the deployment).

| Module | Route | Source template |
|--------|-------|-----------------|
| `dashboard` | `/admin` | This template (KPI cards) |
| `catalog` | `/admin/produtos` (or `/admin/products`) | `feature_catalog.md` |
| `crm` | `/admin/crm` (or `/admin/contacts`) | `feature_crm.md` |
| `content_library` | `/admin/conteudo` (or `/admin/content`) | `feature_content_factory.md` + `feature_publishing.md` |
| `sales` | `/admin/vendas` (or `/admin/sales`) | This template + `feature_crm.md` |
| `integrations` | `/admin/integracoes` (or `/admin/integrations`) | `feature_erp_integration.md` + `feature_marketplace_integration.md` |
| `b2b_orders` | `/admin/b2b-orders` | `feature_pricing_engine.md` + `feature_crm.md` |
| `users_roles` | `/admin/usuarios` | This template (role management) |

A deployer enabling only `dashboard + crm` deploys a leaner surface; modules they don't enable do not render nav items or routes.

---

## Dashboard (KPI cards)

The `/admin` root shows KPI cards. Default v1 set:
- Total contacts (count of `crm_contacts`)
- Active products (count of `products` where `status = 'active'`)
- Messages sent (count of `sales_messages` last 30d)
- Pending publish (count of `content_library` where `approved = true AND publish_status = 'pending'`)
- Recent orders (count of `b2b_orders` last 7d)

Cards link to their respective admin pages. Counts auto-refresh on a 60s interval.

---

## Role enforcement

| Concept | Pattern |
|---------|---------|
| Default role on signup | `null` (no admin access) |
| Admin role grant | Manual DB update by deployer OR self-serve flow per `feature_admin_console.md` `admin_role_grant_flow` extension |
| First-time login lag | Document expected ~1-2s delay while `useIsAdmin()` resolves; `ProtectedRoute` MUST handle loading state without race condition |
| Multi-role | Supported via `admin_role_names` open_var (e.g., `["admin", "editor", "viewer"]`) |

---

## Integration contracts

- Consumes auth context from the deployer's auth provider.
- Provides protected route wrapping to: `feature_catalog.md`, `feature_crm.md`, `feature_content_factory.md`, `feature_publishing.md`, `feature_erp_integration.md`, `feature_marketplace_integration.md`, `feature_pricing_engine.md`.
- Reads brand context from filled `open_vars`.

---

## Out of scope

- Audit logging of admin actions (use `feature_publishing.md` audit_event pattern if needed).
- Multi-tenant admin (one admin console per brand; multi-brand uses separate deployments per E2 in spec).
- Custom role-permission DSL (deployer extends via the auth provider's native ACL).
- 2FA / MFA setup (provider responsibility).
