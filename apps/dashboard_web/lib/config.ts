// ----------------------------------------------------------------------------
// Runtime configuration, read once from NEXT_PUBLIC_* env.
// Centralized so no component reads process.env directly.
// ----------------------------------------------------------------------------

function readBool(value: string | undefined): boolean {
  if (!value) return false;
  const v = value.trim().toLowerCase();
  return v === "1" || v === "true" || v === "yes" || v === "on";
}

/**
 * How the app authenticates a session. The SINGLE explicit selector (mission ADDAY1B,
 * the dev-login-revert done right -- a config flip, not a code rewrite):
 *   - "supabase" -> REAL Supabase Auth (tenant logins; the JWT app_metadata.tenant_id
 *                   claim is the ONLY identity gate -> backend verify -> RLS).
 *   - "dev"      -> the local dev-login STUB (any credentials pass, FIXTURE_TENANT
 *                   session). The LOCAL default; never for a real deploy.
 */
export type AuthMode = "dev" | "supabase";

/**
 * Resolve the auth mode from NEXT_PUBLIC_CEXAI_AUTH, with a LEGACY fallback so every
 * existing NEXT_PUBLIC_FIXTURES setup keeps working byte-for-byte:
 *   explicit "supabase" | "dev"      -> that mode (the production flag-flip path);
 *   unset + fixtures                 -> "dev"  (the offline-mocks local default);
 *   unset + Supabase url/key present -> "supabase" (the prior LIVE behavior);
 *   unset + nothing configured       -> "dev"  (degrade to the safe local stub).
 */
function resolveAuthMode(
  raw: string | undefined,
  fixtures: boolean,
  supabaseUrl: string,
  supabaseAnonKey: string,
): AuthMode {
  const explicit = (raw || "").trim().toLowerCase();
  if (explicit === "supabase") return "supabase";
  if (explicit === "dev") return "dev";
  if (fixtures) return "dev";
  return supabaseUrl && supabaseAnonKey ? "supabase" : "dev";
}

const _fixtures = readBool(process.env.NEXT_PUBLIC_FIXTURES);
const _supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const _supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

export const config = {
  /** When true, the whole app runs on in-memory fixtures (no backend, no DB). The
   *  DATA-LAYER flag (lib/api.ts); independent of authMode (lib/auth.tsx). */
  fixtures: _fixtures,

  /** Which auth path is active: "dev" stub vs real "supabase" (mission ADDAY1B). */
  authMode: resolveAuthMode(
    process.env.NEXT_PUBLIC_CEXAI_AUTH,
    _fixtures,
    _supabaseUrl,
    _supabaseAnonKey,
  ),

  /** FastAPI backend base URL (apps/dashboard_api). */
  apiUrl: (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/+$/, ""),

  /** Supabase project (Auth / PLANE 1). */
  supabaseUrl: _supabaseUrl,
  supabaseAnonKey: _supabaseAnonKey,

  /** Brand label shown in chrome. */
  brandName: process.env.NEXT_PUBLIC_BRAND_NAME || "CEXAI",

  /**
   * The ACTIVE tenant whose brand personalises the admin (dark-lab) shell -- the
   * single accent + header logo + name (lib/adminTheme.ts). A known tenant id ->
   * that tenant's reskin (accent + logo); unset / "default" / "cexai" -> the
   * default CEXAI cyan dark-lab, byte-identical. NEVER changes auth or data.
   */
  activeTenant: (process.env.NEXT_PUBLIC_TENANT || "").trim(),

  /**
   * Whether the management/CRUD half of the dashboard is exposed for this
   * tenant. Overlay-driven: a tenant whose overlay declares no manageable
   * entities hides the "Data" nav entirely. Defaults ON so the mold ships its
   * full surface; a deployment can set NEXT_PUBLIC_ENABLE_MANAGEMENT=0 to hide.
   */
  enableManagement: process.env.NEXT_PUBLIC_ENABLE_MANAGEMENT
    ? readBool(process.env.NEXT_PUBLIC_ENABLE_MANAGEMENT)
    : true,

  /**
   * The tenant's BUSINESS SHAPE vertical -- "retail" | "services" (register R-012).
   * Mirrors the backend cex_business_shape / the frozen TenantShape.vertical
   * contract (apps/public_site/lib/tenantConfig.ts). Drives lib/fixtureFlavor's
   * FIXTURES-mode demo vocabulary so a services tenant no longer previews a
   * pet-retail catalog. Unset / unrecognised -> "" -> fixtureFlavor.resolveFlavor
   * degrades to the neutral generic-commerce flavor (never pet by accident).
   */
  businessShape: (process.env.NEXT_PUBLIC_BUSINESS_SHAPE || "").trim().toLowerCase(),
} as const;

/** True when real Supabase Auth is the active mode AND its url/key are configured.
 *  The real client (lib/supabase.getSupabase) is created ONLY when this holds; in
 *  "dev" mode it stays null and lib/auth.tsx serves the local stub session. */
export function hasSupabase(): boolean {
  return config.authMode === "supabase" && Boolean(config.supabaseUrl && config.supabaseAnonKey);
}
