// ----------------------------------------------------------------------------
// OFFLINE FIXTURES for the L2 PUBLIC SITE (NEXT_PUBLIC_FIXTURES=1).
//
// HONEST BY CONSTRUCTION: this serves a clearly-flagged SAMPLE catalog -- it is NEVER
// claimed to be a real tenant's published data. Every item carries ``real: false``
// and the brand tagline + the sample slug name say "amostra". The fixtures path
// mirrors the LIVE contract (apps/dashboard_api/public_routes.py) shape-for-shape
// so the pages + tests run with no backend and no DB.
//
// SOURCE OF TRUTH: the per-tenant BRAND + CATALOG moved to lib/tenantConfig. The old
// TENANTS registry is GONE -- fxGetTenantInfo / fxGetCatalog now DERIVE the brand + catalog
// from tenantConfigFor(slug), and use isRegisteredTenant(slug) to honour the no-leak
// contract (a registered fixture tenant vs an unknown slug). The synthetic fixtures
// tenant_id (a fixtures-runtime detail, never a secret, not part of the tenant_config
// contract) is derived from the slug.
//
// The fixtures model the no-leak contract:
//   * fxGetTenantInfo(slug): a REGISTERED tenant -> the brand shell; ANY other slug
//     -> null (the page renders <NotFound/>, exactly like a live 404). There is no
//     way to tell an unknown slug from a non-public one (no-leak).
//   * fxGetCatalog(slug, kind): a registered slug + a kind WITH sample rows -> those rows;
//     a registered slug + an unknown kind -> an empty list (the branded empty shell); an
//     unknown slug -> null (NotFound).
//
// ASCII-only + diacritic-free (house style). PURE DATA + PURE FUNCTIONS.
// ----------------------------------------------------------------------------

import {
  tenantConfigFor,
  isRegisteredTenant,
  SAMPLE_SLUG,
  ORBIT_SLUG,
} from "@/lib/tenantConfig";
import type {
  PublicCatalogItem,
  PublicCatalogResponse,
  PublicTenantInfo,
} from "@/lib/types";

// Re-export the registered tenant slugs (they live in tenantConfig now) so existing import
// sites + tests -- import { SAMPLE_SLUG, ORBIT_SLUG } from "@/lib/fixtures" -- are
// unchanged.
export { SAMPLE_SLUG, ORBIT_SLUG };

/** The synthetic fixtures tenant id for a registered slug (never a secret -- a fixtures
 *  runtime detail; the live backend resolves the real id from the DB). Derived from the
 *  slug so no parallel id map is needed: "demo-acme" -> "tenant_sample_demo_acme",
 *  "example-co" -> "tenant_sample_example_co". */
function fixtureTenantId(slug: string): string {
  return "tenant_sample_" + slug.replace(/-/g, "_");
}

// --- the fixtures API (mirrors the live contract shape) ----------------------

/** GET /public/tenant-info (fixtures). A REGISTERED tenant -> the brand shell (brand DERIVED
 *  from tenantConfig); ANY other slug -> null (NotFound). No-leak: unknown vs non-public are
 *  indistinguishable. */
export function fxGetTenantInfo(slug: string): PublicTenantInfo | null {
  if (!isRegisteredTenant(slug)) return null;
  return {
    tenant_id: fixtureTenantId(slug),
    slug,
    brand: tenantConfigFor(slug).brand,
    published_at: null,
  };
}

/** GET /public/catalog (fixtures). A registered slug + a kind with rows -> a paged
 *  response (catalog DERIVED from tenantConfig); a registered slug + an unknown kind -> an
 *  empty list; an unknown slug -> null (NotFound). Honours limit/offset so pagination tests
 *  behave. */
export function fxGetCatalog(
  slug: string,
  kind: string,
  limit = 50,
  offset = 0,
): PublicCatalogResponse | null {
  if (!isRegisteredTenant(slug)) return null;
  const all: PublicCatalogItem[] = tenantConfigFor(slug).catalog[kind] ?? [];
  const lim = Number.isFinite(limit) && limit > 0 ? Math.floor(limit) : 50;
  const off = Number.isFinite(offset) && offset > 0 ? Math.floor(offset) : 0;
  const items = all.slice(off, off + lim);
  return {
    tenant_id: fixtureTenantId(slug),
    slug,
    kind,
    items,
    limit: lim,
    offset: off,
  };
}
