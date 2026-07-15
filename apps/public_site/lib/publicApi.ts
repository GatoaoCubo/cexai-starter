// ----------------------------------------------------------------------------
// PublicApiClient -- the ONE module the public pages talk to. UNAUTHENTICATED.
//
// MIRRORS apps/dashboard_web/lib/api.ts's private req() wrapper + ApiClientError +
// the { error: { type, reason, detail } } envelope parsing, with these KEY
// DIFFERENCES (this is the security keystone):
//   * UNAUTHENTICATED: it NEVER sends an Authorization header and NEVER sends a
//     tenant_id. Only slug + kind (+ limit/offset) ever reach the API. The backend
//     resolves the tenant from the slug (public_read-gated) -- the client carries no
//     identity at all.
//   * GET-only: the public surface is read-only; there is no POST/PATCH/DELETE.
//   * Two modes: FIXTURES (config.fixtures -> lib/fixtures, no network) vs REAL
//     (fetch GET against NEXT_PUBLIC_API_URL + /public/*).
//
// NO-LEAK 404 HANDLING: the backend returns 404 { error: { type:"public_not_found"
// ... } } for an unknown OR a non-public slug (indistinguishable). The client maps
// that 404 to NULL (not a thrown error) -- the page renders <NotFound/>, the SAME
// view for every miss, so it never discloses whether a tenant exists. Any OTHER
// non-ok status throws an ApiClientError the page can surface.
//
// ASCII-only + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { config } from "@/lib/config";
import { fxGetCatalog, fxGetTenantInfo } from "@/lib/fixtures";
import { isValidKind, isValidSlug } from "@/lib/slug";
import type {
  ApiError,
  PublicCatalogResponse,
  PublicTenantInfo,
} from "@/lib/types";

/** The single error type the public pages handle. Mirrors lib/api.ApiClientError. */
export class ApiClientError extends Error implements ApiError {
  status: number;
  reason?: string;
  constructor(status: number, message: string, reason?: string) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.reason = reason;
  }
}

/** The backend's no-leak 404 error type. A 404 carrying this -> NULL (NotFound),
 *  never a thrown error. */
const PUBLIC_NOT_FOUND = "public_not_found";

/**
 * The unauthenticated, GET-only public client. There is NO constructor identity
 * (no token, no tenant) -- the public path carries none. A module-level singleton
 * is exported below for convenience.
 */
export class PublicApiClient {
  /**
   * GET against the public API. UNAUTHENTICATED: no Authorization header, no
   * tenant_id, no cookies. Mirrors lib/api.req()'s envelope parsing.
   *
   * Returns the parsed body on 200. Returns NULL when the response is a no-leak
   * 404 (error.type === "public_not_found") -- the caller renders <NotFound/>. Any
   * OTHER non-ok status throws an ApiClientError.
   */
  private async getOrNull<T>(path: string): Promise<T | null> {
    if (config.apiUrl === "") {
      throw new ApiClientError(
        0,
        "NEXT_PUBLIC_API_URL is not set. Set it, or run with NEXT_PUBLIC_FIXTURES=1.",
      );
    }
    let res: Response;
    try {
      res = await fetch(`${config.apiUrl}${path}`, {
        method: "GET",
        // NO Authorization header. NO tenant_id. The public path carries no
        // identity -- the backend resolves the tenant from the slug in the query.
        headers: { accept: "application/json" },
        // Never attach cookies/credentials to the cross-origin public read.
        credentials: "omit",
        cache: "no-store",
      });
    } catch {
      throw new ApiClientError(
        0,
        `Cannot reach the backend at ${config.apiUrl}. Is it running?`,
      );
    }

    if (!res.ok) {
      let reason: string | undefined;
      let type: string | undefined;
      let message = `Request failed (${res.status}).`;
      try {
        const data = (await res.json()) as Record<string, unknown>;
        // The backend wraps every failure as { error: { type, reason, detail } }.
        const envelope = data.error;
        if (envelope && typeof envelope === "object") {
          const e = envelope as Record<string, unknown>;
          if (typeof e.type === "string") type = e.type;
          if (typeof e.reason === "string") reason = e.reason;
          if (typeof e.detail === "string" && e.detail) message = e.detail;
          else if (typeof e.reason === "string") message = e.reason;
        } else {
          // Defensive: tolerate a flat {detail|message|reason} body too.
          if (typeof data.detail === "string") message = data.detail;
          else if (typeof data.message === "string") message = data.message;
          if (typeof data.reason === "string") reason = data.reason;
        }
      } catch {
        // non-JSON error body; keep the default message
      }
      // The no-leak miss: a 404 public_not_found is NOT an error to surface -- it is
      // "no such public tenant". Return null so the page renders <NotFound/>.
      if (res.status === 404 && type === PUBLIC_NOT_FOUND) return null;
      throw new ApiClientError(res.status, message, reason);
    }

    if (res.status === 204) return null;
    return (await res.json()) as T;
  }

  /**
   * GET /public/tenant-info?slug=<slug> -> the tenant's public brand shell, or NULL
   * for an unknown/non-public slug (no-leak). Validates the slug client-side FIRST
   * (defence-in-depth): a malformed slug never reaches the API -> returns null.
   */
  async getTenantInfo(slug: string): Promise<PublicTenantInfo | null> {
    if (!isValidSlug(slug)) return null; // defence-in-depth: never fetch a bad slug
    const s = slug.trim();
    if (config.fixtures) return fxGetTenantInfo(s);
    const qs = `?slug=${encodeURIComponent(s)}`;
    return this.getOrNull<PublicTenantInfo>(`/public/tenant-info${qs}`);
  }

  /**
   * GET /public/catalog?slug=&kind=&limit=&offset= -> the published rows of ``kind``
   * for the tenant behind ``slug``, or NULL for an unknown/non-public slug (no-leak).
   * Validates BOTH slug and kind client-side FIRST: a malformed slug -> null
   * (NotFound); a malformed kind -> null (no such catalog). Only slug + kind +
   * limit/offset ever reach the API -- never a tenant_id, never an auth header.
   */
  async getCatalog(
    slug: string,
    kind: string,
    limit?: number,
    offset?: number,
  ): Promise<PublicCatalogResponse | null> {
    if (!isValidSlug(slug)) return null; // defence-in-depth
    if (!isValidKind(kind)) return null; // a bad kind is "no such catalog"
    const s = slug.trim();
    const k = kind.trim();
    if (config.fixtures) return fxGetCatalog(s, k, limit ?? 50, offset ?? 0);
    const params = new URLSearchParams();
    params.set("slug", s);
    params.set("kind", k);
    if (typeof limit === "number" && Number.isFinite(limit) && limit > 0) {
      params.set("limit", String(Math.floor(limit)));
    }
    if (typeof offset === "number" && Number.isFinite(offset) && offset >= 0) {
      params.set("offset", String(Math.floor(offset)));
    }
    return this.getOrNull<PublicCatalogResponse>(`/public/catalog?${params.toString()}`);
  }
}

/** The module-level singleton the pages import (no per-request identity to bind). */
export const publicApi = new PublicApiClient();
