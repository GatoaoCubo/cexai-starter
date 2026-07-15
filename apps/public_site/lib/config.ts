// ----------------------------------------------------------------------------
// Runtime configuration for the L2 PUBLIC SITE, read once from NEXT_PUBLIC_* env.
// Centralized so no component reads process.env directly.
//
// MIRRORS apps/dashboard_web/lib/config.ts but DROPS every auth bit (authMode /
// supabase / management) -- the public site is UNAUTHENTICATED. The only knobs are
// the backend base URL and the fixtures flag.
// ----------------------------------------------------------------------------

function readBool(value: string | undefined): boolean {
  if (!value) return false;
  const v = value.trim().toLowerCase();
  return v === "1" || v === "true" || v === "yes" || v === "on";
}

/** Matches ONLY a loopback-origin plain-http URL: http://localhost or http://127.0.0.1, an
 *  optional :port, and an optional /path (host match is case-insensitive). Anchored full-string
 *  so a lookalike host ("localhost.evil.com", "127.0.0.10", "http://localhost:evil") can never
 *  slip through -- the host must be EXACTLY "localhost" or "127.0.0.1", nothing appended. Declared
 *  BEFORE `config` (which calls normalizeAdminUrl at module-evaluation time) -- a `const` used by a
 *  function invoked during that same top-level evaluation must already be initialized (TDZ). */
const LOOPBACK_HTTP_RE = /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/.*)?$/i;

const _fixtures = readBool(process.env.NEXT_PUBLIC_FIXTURES);

export const config = {
  /** When true, the whole app runs on in-memory fixtures (no backend). The
   *  DATA-LAYER flag (lib/publicApi.ts). */
  fixtures: _fixtures,

  /** FastAPI backend base URL (apps/dashboard_api -- the /public/* routes). The
   *  client only ever appends /public/tenant-info or /public/catalog to this. */
  apiUrl: (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/+$/, ""),

  /** The ADMIN (dashboard) URL the header "Admin" link points at. A trusted, build-time
   *  constant -- NEVER a tenant value. Defaults to "/admin" (a same-origin path) when the
   *  env is unset; an operator can point it at the deployed dashboard origin. We only ever
   *  accept an https: absolute URL, a same-origin "/path", or a LOOPBACK-only plain-http URL
   *  (http://localhost[:port] / http://127.0.0.1[:port] -- R-368, local dev admin servers) --
   *  any other shape degrades to the default (no javascript:/data:/remote-http link can ever
   *  be injected here). */
  adminUrl: normalizeAdminUrl(process.env.NEXT_PUBLIC_ADMIN_URL),
} as const;

/**
 * Accept an https: absolute URL, a same-origin "/path", or a LOOPBACK-only plain-http URL;
 * else the safe default.
 *
 * R-368: the distill engine emits `.env.local` with `NEXT_PUBLIC_ADMIN_URL=http://localhost:3001`
 * for a freshly-emitted tenant's local dev admin server. Plain http: was previously rejected
 * outright (correct for any REMOTE host -- an operator-misconfigured `http://some-host` must never
 * become a clickable insecure link), which silently downgraded that value to the "/admin" default
 * and 404'd the storefront's "Admin" link. The fix narrowly re-admits ONLY the two addresses that
 * can ever resolve to "this machine" (localhost / 127.0.0.1): they can never point at a third-party
 * origin, so trusting plain http for them carries none of the MITM/downgrade risk that motivated
 * rejecting http: in the first place. Every OTHER http: host is still dropped exactly as before,
 * as are javascript:, data:, and protocol-relative "//host" -- this is an ADDITIVE exception, not a
 * relaxation of the general rule.
 */
function normalizeAdminUrl(raw: string | undefined): string {
  const s = (raw || "").trim();
  if (/^https:\/\//i.test(s)) return s;
  if (/^\/[^/]/.test(s) || s === "/") return s; // same-origin path (not "//host")
  if (LOOPBACK_HTTP_RE.test(s)) return s; // R-368: loopback-only plain http (local dev admin)
  return "/admin";
}

/**
 * Build the ADMIN deep-link for a tenant: ``config.adminUrl`` with a ``?tenant=<slug>``
 * query appended, so the public site "Admin" link lands in THAT tenant's admin.
 *
 * SECURITY: the ``?tenant`` param drives the admin THEME + preview label at RUNTIME ONLY --
 * it NEVER selects, widens, or overrides data access. In the dashboard the DATA tenant stays
 * bound to the auth/RLS session (the Supabase JWT app_metadata.tenant_id), never the URL.
 *
 * Handles all adminUrl shapes: a same-origin "/path" ("/admin" -> "/admin?tenant=x"), an
 * absolute https URL ("https://dash.example.com/" -> ".../?tenant=x"), or a loopback http URL
 * ("http://localhost:3001" -> ".../?tenant=x" -- R-368). When the adminUrl already carries a
 * query, the slug is appended with "&". The slug is URL-encoded, and config.adminUrl is already
 * normalized (https: absolute, same-origin "/path", or loopback-only http: -- see
 * normalizeAdminUrl), so no javascript:/data: scheme can ever be produced here. An empty slug ->
 * the bare adminUrl (degrade-never). TOTAL -- never throws. ASCII-only.
 */
export function adminUrlForTenant(slug: string): string {
  const base = config.adminUrl;
  const tenant = encodeURIComponent((slug ?? "").trim());
  if (!tenant) return base;
  const sep = base.includes("?") ? "&" : "?";
  return `${base}${sep}tenant=${tenant}`;
}
