---
kind: feature_template
feature_name: frontend
vertical: 16_company_stack
round_added: 22
pillars: [P05, P09]
adr_019_packages: [tools/web/]
feature_dependencies: []
brand_niche_constraints: null
open_vars:
  - name: brand_name
    type: str
    description: "Brand display name shown in headers, page titles, OG tags."
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
    description: "Brand vertical / niche; drives copy templates and SEO keywords."
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
    description: "Primary audience descriptor; drives tone in SEOHead component."
    filler_role: n02
    filler_stage: F3_INJECT
    context_hints: [brand_config.target_audience, session_state.recent_audience]
    constraints: {min_length: 3, max_length: 150}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: primary_language
    type: enum
    description: "Primary language for all public-facing copy."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: primary_domain
    type: url
    description: "Production domain for the public site (used in canonical URLs, OG, sitemap)."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    context_hints: [brand_config.primary_domain]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: false
---

# Feature Template: Frontend

**Purpose**: a deployer-ready web frontend that loads quickly, lazy-loads per route, and ships SEO-clean + auth-gated by default.

---

## Architecture

| Layer | Pattern | Notes |
|-------|---------|-------|
| Framework | React 18+ with Vite OR Next.js (App Router) | Deployer chooses; both supported via this template's variants. Default in v1: React + Vite. |
| Language | TypeScript (strict mode) | Mandatory; non-negotiable. |
| Styling | Tailwind CSS + shadcn/ui (or equivalent component library) | Component library choice is open (Headless UI, Radix, Mantine acceptable). |
| Routing | `react-router-dom` v6 + `BrowserRouter` OR Next.js file-based routing | Per framework choice. |
| State/data | `@tanstack/react-query` for server state; React Context or Zustand for UI state | Avoid Redux unless app complexity demands. |
| Auth gate | `ProtectedRoute` component called inside layout wrappers | Authentication backend = configurable via `feature_admin_console.md` integration. |
| SEO | `<SEOHead>` component with props `title`, `description`, `canonical`, `keywords[]`, `breadcrumbs[]`, `noindex` | One component, used on every route. |
| Hosting | Hosted commerce platform with auto-deploy on push (e.g., Lovable, Vercel, Netlify, Cloudflare Pages) | Deployer choice. |

---

## Required route structure (minimum viable)

| Route | Layout | Purpose |
|-------|--------|---------|
| `/` | public/landing | Brand homepage + primary CTA |
| `/sobre` | public | About / brand story |
| `/blog` `/blog/:slug` | public | Content marketing surface |
| `/login` | public | Auth entry |
| `/admin/*` | admin (protected) | See `feature_admin_console.md` |

The deployer extends per their niche (e.g., e-commerce adds `/catalogo`, `/produtos/:slug`; SaaS adds `/dashboard`, `/billing`).

---

## Critical lazy-loading rule

Every route MUST be `lazy(() => import(...))`. Forgetting either the lazy import OR the `<Route>` entry yields a runtime crash or 404.

```tsx
// pattern (not actual code -- spec only)
const HomePage = lazy(() => import("./pages/HomePage"));
const AdminLayout = lazy(() => import("./components/admin/AdminLayout"));
// ...
<Routes>
  <Route path="/" element={<HomePage />} />
  <Route path="/admin/*" element={<AdminLayout />} />
</Routes>
```

---

## Layout wrappers

Two minimum layouts: `PublicLayout` (Header variant `"b2c"` or `"b2b"`, footer, breadcrumbs) and `AdminLayout` (sidebar nav, admin breadcrumbs, protected route gate).

Deployers with multiple audience modes (B2C + B2B) declare a `Header` component with `variant` prop.

---

## Broken-chunk recovery

Hosted SPA platforms cache `index.html` references to hashed chunk filenames. If any chunk 404s, the route shows infinite loading. Recovery: push an empty / no-op commit to force a clean rebuild. Document this in the deployer's runbook.

---

## Integration contracts

- Receives auth context from `feature_admin_console.md` (the `ProtectedRoute` component reads from there).
- Receives brand config from filled `open_vars` -> rendered in headers/footers/SEO.
- Receives product/CRM/content data via API contracts defined in `feature_catalog.md`, `feature_crm.md`, etc.

---

## Out of scope for this template

- Mobile app shell (out-of-vertical-16 scope).
- Native PWA install flows.
- Server-side rendering tuning (deployer's hosting concern).
- Detailed performance budgets (deployer KPIs).
