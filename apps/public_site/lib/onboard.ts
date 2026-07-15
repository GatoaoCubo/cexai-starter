// ----------------------------------------------------------------------------
// onboard -- the PURE, testable core of the DEV-ONLY /onboard flow (inc3 URL-first
// onboarding). The route (app/api/onboard/route.ts) owns the spawn ORCHESTRATION
// (child_process -> python bootstrap + the loader); everything that can be reasoned
// about without spawning a process lives HERE so it can be unit-tested in isolation:
//
//   * isOnboardEnabled(env) -- the HARD DEV GATE. true ONLY when NODE_ENV=="development"
//     AND the server-only opt-in CEXAI_ONBOARD_ENABLED=="1". This is the prod-refusal:
//     in any prod/deployed build NODE_ENV!=="development" so the gate is false and the
//     route can NEVER spawn a process. (The route checks process.env server-side.)
//   * validateUrlScheme(url) -- accept http(s) ONLY; reject file:/ftp:/data:/javascript:.
//     The SSRF note: the operator is dev-trusted, so we validate the SCHEME (+ the route
//     passes a spawn timeout) rather than an allowlist (this is a dev tool).
//   * deriveSlugFromUrl(url) -- the URL hostname -> a slug (lowercase, strip non [a-z0-9],
//     truncate 63). The result MUST pass isValidSlug (lib/slug.ts) or we return null --
//     never force a transform that could path-escape.
//   * parseManifest(stdout) -- parse the bootstrap's --json manifest off stdout. TOTAL:
//     a valid manifest (ok OR error) returns the object; non-JSON returns a typed error.
//
// PURE + TOTAL: none of these throw, none touch the filesystem or the network. ASCII-only
// + diacritic-free (house style).
// ----------------------------------------------------------------------------

import { isValidSlug } from "@/lib/slug";

/** The env subset the dev gate reads. A plain record so it is trivially testable
 *  (the route passes process.env). */
export interface OnboardEnv {
  NODE_ENV?: string;
  CEXAI_ONBOARD_ENABLED?: string;
}

/** The booted-manifest shape cex_tenant_bootstrap.py emits with --json. Every field is
 *  optional + defensively read -- the route never assumes a key is present. (The python
 *  side always emits the full shape, but typing it loose keeps parseManifest TOTAL.) */
export interface OnboardManifest {
  ok?: boolean;
  tenant_id?: string;
  tenant_root?: string;
  tenant_config_path?: string;
  tenant_config_persisted?: boolean;
  brand?: {
    name?: string;
    tagline?: string;
    domain?: string;
    tokens?: Record<string, string>;
  } | null;
  business_shape?: Record<string, unknown> | null;
  next_steps?: string[];
  errors?: string[];
  [key: string]: unknown;
}

/** The JSON the route returns to the page -- a HONEST projection of the manifest + the
 *  resolved preview path. Shared so the page renders the exact contract. */
export interface OnboardApiResponse {
  ok: boolean;
  tenant_id?: string;
  tenant_config_path?: string;
  tenant_config_persisted?: boolean;
  brand?: OnboardManifest["brand"];
  business_shape?: Record<string, unknown> | null;
  errors?: string[];
  next_steps?: string[];
  previewPath?: string | null;
}

/** The HARD DEV GATE. true ONLY in a local dev build that has EXPLICITLY opted in.
 *
 *  Both conditions are required and are checked server-side by the route:
 *    1. NODE_ENV === "development"  -- never true in a prod/deployed build.
 *    2. CEXAI_ONBOARD_ENABLED === "1"  -- a SERVER-ONLY env (NOT a NEXT_PUBLIC_ var, so it
 *       can never be inlined into the client bundle / toggled from the browser).
 *  This is the prod-refusal: when false the route returns 403 BEFORE any spawn. TOTAL. */
export function isOnboardEnabled(env: OnboardEnv | undefined | null): boolean {
  if (!env) return false;
  return env.NODE_ENV === "development" && env.CEXAI_ONBOARD_ENABLED === "1";
}

/** True iff ``rawUrl`` parses AND its scheme is http(s). Rejects file:/ftp:/data:/
 *  javascript: and anything unparseable. The route calls this BEFORE spawning so a
 *  non-http(s) URL never reaches the bootstrap. PURE + TOTAL (never throws). */
export function validateUrlScheme(rawUrl: unknown): boolean {
  if (typeof rawUrl !== "string") return false;
  try {
    const u = new URL(rawUrl.trim());
    return u.protocol === "http:" || u.protocol === "https:";
  } catch {
    return false;
  }
}

/** Derive a tenant slug from a site URL's hostname:
 *    https://MyBrand.com.br  ->  "mybrand"   (first host label, lowercased)
 *    https://www.acme.io      ->  "acme"      (a leading www. is stripped)
 *
 *  Algorithm: parse -> hostname -> drop a leading "www." -> take the FIRST label (before
 *  the first dot) -> lowercase -> strip every char that is not [a-z0-9] -> truncate 63.
 *  The result MUST pass isValidSlug (the SAME allowlist the route enforces before spawn,
 *  ^[a-z0-9][a-z0-9_-]{0,63}$); otherwise we return null rather than force a transform
 *  that could path-escape. PURE + TOTAL: a bad/empty/unparseable URL returns null. */
export function deriveSlugFromUrl(rawUrl: unknown): string | null {
  if (typeof rawUrl !== "string") return null;
  let host: string;
  try {
    host = new URL(rawUrl.trim()).hostname; // URL already lowercases the host
  } catch {
    return null;
  }
  if (!host) return null;
  host = host.replace(/^www\./i, "");
  const firstLabel = host.split(".")[0] || "";
  const cleaned = firstLabel.toLowerCase().replace(/[^a-z0-9]/g, "");
  const slug = cleaned.slice(0, 63);
  // Defence-in-depth: the value we will pass to the spawned bootstrap MUST be a valid
  // slug (the bootstrap's own _safe_tenant_id is the fail-closed secondary).
  return isValidSlug(slug) ? slug : null;
}

/** Parse the bootstrap's --json manifest off captured stdout. TOTAL -- never throws:
 *    * valid JSON object (ok:true OR ok:false-with-errors) -> { manifest, error:null }
 *    * empty / non-JSON / a JSON non-object (array, number) -> { manifest:null, error }
 *  Defensive: if the whole string is not valid JSON it retries on the outermost
 *  { ... } slice, so a stray log line leaked onto stdout still yields the manifest. */
export function parseManifest(
  stdout: unknown,
):
  | { manifest: OnboardManifest; error: null }
  | { manifest: null; error: string } {
  const text = typeof stdout === "string" ? stdout.trim() : "";
  if (!text) return { manifest: null, error: "empty bootstrap output" };

  const direct = tryParseObject(text);
  if (direct) return { manifest: direct, error: null };

  // Fallback: extract the outermost JSON object (defensive against a stray prefix/suffix).
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start >= 0 && end > start) {
    const sliced = tryParseObject(text.slice(start, end + 1));
    if (sliced) return { manifest: sliced, error: null };
  }
  return { manifest: null, error: "bootstrap stdout was not a JSON object" };
}

/** JSON.parse that returns a plain object or null (never throws, rejects arrays/scalars). */
function tryParseObject(s: string): OnboardManifest | null {
  try {
    const value = JSON.parse(s);
    if (value && typeof value === "object" && !Array.isArray(value)) {
      return value as OnboardManifest;
    }
    return null;
  } catch {
    return null;
  }
}
