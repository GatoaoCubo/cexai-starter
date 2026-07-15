// ----------------------------------------------------------------------------
// PUBLIC_KINDS -- the configured set of tenant_data kinds the public LANDING page
// links to, DERIVED from the single source-of-truth (lib/tenantConfig).
//
// WHY A CONSTANT (not a fetch): the public API has NO list-kinds endpoint (see
// apps/dashboard_api/public_routes.py -- only /public/tenant-info and
// /public/catalog exist). So the landing page cannot discover which kinds a tenant
// published; it links to this DOCUMENTED, curated set. Each link lands on the
// catalog page for that kind; a kind the tenant has NOT published renders the
// branded empty shell ("nada publicado ainda") -- honest, never a fabricated list.
//
// The per-slug map is GONE: the kinds now live in each tenant's ``shape.public_kinds``
// in tenantConfig. PUBLIC_KINDS (the built-in retail default) is re-exported from there so
// existing import sites + tests are unchanged. To surface a new public kind, edit the
// tenant's shape in tenantConfig.
// ASCII-only.
// ----------------------------------------------------------------------------

import { tenantConfigFor } from "@/lib/tenantConfig";

/** One linkable public kind: the tenant_data ``kind`` + a human label/blurb. */
export interface PublicKind {
  /** the tenant_data.kind value (matches the catalog ``kind`` query param). */
  kind: string;
  /** the nav/section label shown on the landing page. */
  label: string;
  /** a one-line blurb under the label. */
  blurb: string;
}

/** The curated public catalog kinds -- the DEFAULT set (the built-in product-retail vertical).
 *  Re-exported from tenantConfig (the single source of truth); an unknown slug + demo-acme
 *  resolve to THIS array by reference (tests assert `toBe(PUBLIC_KINDS)`). */
export { PUBLIC_KINDS } from "@/lib/tenantConfig";

/** Resolve the public kinds a tenant SLUG offers, from its ``shape.public_kinds``. A
 *  registered tenant -> its kinds; any other slug -> the default PUBLIC_KINDS by reference
 *  (zero-regression). TOTAL. ASCII-only. */
export function publicKindsFor(slug: string): readonly PublicKind[] {
  return tenantConfigFor(slug).shape.public_kinds;
}
