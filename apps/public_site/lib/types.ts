// ----------------------------------------------------------------------------
// Wire types for the L2 PUBLIC SITE -- they mirror the unauthenticated public API
// contract (apps/dashboard_api/public_routes.py). The BACKEND is the source of
// truth; these types match its response shapes 1:1.
//
//   GET /public/tenant-info?slug=<slug>
//     200 -> PublicTenantInfo { tenant_id, slug, brand, published_at }
//     404 -> { error: ApiError }   // unknown OR non-public slug (indistinguishable)
//   GET /public/catalog?slug=<slug>&kind=<kind>&limit=&offset=
//     200 -> PublicCatalogResponse { tenant_id, slug, kind, items, limit, offset }
//     404 -> { error: ApiError }
//
// The "brand" object maps 1:1 to BrandTheme (lib/brandTheme). Each catalog item is
// the published payload FLATTENED + id/kind/published_at + an optional human_html.
// There is NO get-by-id endpoint and NO list-kinds endpoint.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import type { BrandTheme } from "@/lib/brandTheme";

/** The error contract every failure carries. Mirrors the backend envelope
 *  { error: { type, reason, detail } } and the dashboard's ApiError shape. The
 *  ApiClientError (lib/publicApi) implements this so callers handle ONE type. */
export interface ApiError {
  /** the HTTP status (0 when the request never reached the backend). */
  status: number;
  /** the backend error reason code (e.g. "public_not_found"'s reason), when present. */
  reason?: string;
}

/**
 * GET /public/tenant-info 200 body. The tenant's PUBLIC brand shell.
 * ``brand`` maps 1:1 to BrandTheme (name / tagline / logo + the 24 tokens).
 * ``published_at`` is null on the tenant shell (it is a per-row concept -- the
 * catalog rows carry their own), kept in the contract for the page shell.
 */
export interface PublicTenantInfo {
  /** the slug-resolved tenant id (never a client value). */
  tenant_id: string;
  /** the public slug (the backend echoes the resolved one). */
  slug: string;
  /** the tenant's public brand -- maps 1:1 to BrandTheme. */
  brand: BrandTheme;
  /** null on the tenant shell (per the contract). */
  published_at: string | null;
}

/**
 * ONE published catalog item: the published payload FLATTENED + the explicit
 * envelope keys (id / kind / published_at) + an optional human_html. The payload
 * fields are open (capability/tenant-extensible), so this is an index signature
 * over the known keys. ``human_html`` is tenant-authored -- treated as an EXPORT
 * STRING (rendered only inside a sandboxed iframe, never injected into the live DOM).
 */
export interface PublicCatalogItem {
  /** the published tenant_data row id. */
  id: string;
  /** the tenant_data kind (echoes the requested kind). */
  kind: string;
  /** the row's go-live time, or null. */
  published_at: string | null;
  /** the tenant-authored human face HTML (export string), when present. */
  human_html?: string;
  /** the flattened published payload fields (open). */
  [key: string]: unknown;
}

/** GET /public/catalog 200 body. */
export interface PublicCatalogResponse {
  /** the slug-resolved tenant id. */
  tenant_id: string;
  /** the public slug. */
  slug: string;
  /** the requested kind. */
  kind: string;
  /** the published rows of ``kind`` for this tenant (newest first). */
  items: PublicCatalogItem[];
  /** the page size the backend applied. */
  limit: number;
  /** the page offset the backend applied. */
  offset: number;
}
