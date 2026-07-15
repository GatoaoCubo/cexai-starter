// ----------------------------------------------------------------------------
// adminTheme.ts -- per-tenant ACCENT + brand mark for the admin (dark-lab) shell.
//
// PER-TENANT ADMIN THEME. The admin (apps/dashboard_web) is a dark-lab
// operator console: a FIXED ink/panel/line base with ONE accent -- the "synapse"
// cyan filament. This module makes that ONE accent (and only that accent) read as
// the ACTIVE TENANT's brand, while the dark-lab base stays untouched.
//
// SELECTOR: config.activeTenant (NEXT_PUBLIC_TENANT). A known tenant id -> that
// tenant's brand (accent + logo + name). unset / "default" / "cexai" -> the CEXAI cyan
// dark-lab, BYTE-IDENTICAL (the default --accent is NEVER injected, so the
// tailwind fallback -- the exact current cyan -- is what renders).
//
// LEGIBILITY: a raw dark brand blue (e.g. "231 48% 48%") is too DARK to read as
// an accent on the near-black ink surface (WCAG ~2.8:1 -- fails AA). We DERIVE an
// on-dark variant from the brand HUE (raise sat + lightness) so it lands ~5.4:1 on
// bg-ink -- a crisp, AA-legible accent that is unmistakably the brand's blue.
//
// SECURITY: the only value that reaches the injected <style> is the accent triplet,
// and it is re-validated through the SAME isHslTriplet shape guard the brand
// token cascade uses (buildCssVars). A malformed selector -> no injection (the
// default cyan stands). The logo is a same-origin /tenants/<id>/logo.png path.
//
// DEGRADE-NEVER: every export is TOTAL (never throws). ASCII-only source.

import { config } from "./config";
import {
  isHslTriplet,
  ORBIT_BRAND_SAMPLE,
  warnTokenFallback,
  type BrandTheme,
  type BrandTokens,
} from "./brandTheme";
// R-006 Admin Theming Bridge: the GENERATED per-tenant theme registry. Committed default {}.
// Populated by cex_distill._carry_admin_theme (a distilled repo ships its OWN single entry) or
// by the predev collector scripts/load-generated-admin-themes.mjs (Central dev: collects every
// .cex/tenants/<slug>/admin_theme.json the bootstrap persisted). Statically imported so it
// bundles into BOTH server and client -- never a runtime fs read.
import generatedAdminThemesJson from "./generatedAdminThemes.json";

// ---------------------------------------------------------------------------
// THE DEFAULT (CEXAI cyan dark-lab) ACCENT
// ---------------------------------------------------------------------------

/** The EXACT current synapse accent as an HSL triplet: tailwind synapse.DEFAULT
 *  (#5EEAD4) == hsl(171 77% 64%). This is the fallback baked into the tailwind
 *  ``synapse`` color (hsl(var(--accent, 171 77% 64%) / <alpha-value>)). When NO
 *  active tenant is set this value is NEVER overridden -> the admin renders the
 *  current cyan, unchanged. Exposed so the test can assert the default. */
export const CEXAI_ACCENT_HSL = "171 77% 64%";

// ---------------------------------------------------------------------------
// ON-DARK ACCENT DERIVATION
// ---------------------------------------------------------------------------

/** Parse an "H S% L%" triplet into [h, s, l] numbers. Returns null on any value
 *  that is not a valid triplet (shape-guarded -- mirrors isHslTriplet). Total. */
function parseHsl(triplet: string): [number, number, number] | null {
  if (!isHslTriplet(triplet)) return null;
  const m = /^\s*(\d{1,3})\s+(\d{1,3})%\s+(\d{1,3})%\s*$/.exec(triplet);
  if (!m) return null;
  return [parseInt(m[1], 10), parseInt(m[2], 10), parseInt(m[3], 10)];
}

const clamp = (n: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, n));

/** Derive an ON-DARK accent triplet from a brand colour triplet, keeping the brand
 *  HUE but raising saturation + lightness so the colour reads as a crisp, AA-legible
 *  accent on the near-black ink surface (a dark brand blue like "231 48% 48%" is
 *  invisible at rest). The derivation is HUE-PRESERVING: only S/L move, so the
 *  result is unmistakably the SAME brand colour, just legible on dark.
 *
 *  Floors (chosen so a dark brand blue lands ~5.4:1 contrast on bg-ink, clearing
 *  WCAG AA 4.5 for text): saturation >= 72%, lightness in [62, 72]. A colour that
 *  is ALREADY light/saturated enough is left at/above the floor (idempotent-ish:
 *  re-deriving never darkens). Returns null on a malformed brand triplet (caller
 *  then falls back to the default cyan -- degrade-never). Total. */
export function deriveOnDarkAccent(brandTriplet: string): string | null {
  const parsed = parseHsl(brandTriplet);
  if (!parsed) return null;
  const [h, s, l] = parsed;
  const onS = clamp(Math.max(s, 72), 0, 100);
  // raise lightness toward the legible band but never past it (keep it an accent,
  // not a wash): if the brand is already light, clamp into [62, 72]; if dark, lift to 67.
  const targetL = l < 62 ? 67 : l;
  const onL = clamp(targetL, 62, 72);
  return `${h} ${onS}% ${onL}%`;
}

// ---------------------------------------------------------------------------
// ACTIVE TENANT RESOLUTION
// ---------------------------------------------------------------------------

/** The admin's per-tenant personalisation: the brand sample + the on-dark accent
 *  triplet (already legible on ink) + the same-origin logo path + display name. */
export interface AdminTenantTheme {
  /** the canonical tenant id (e.g. the active tenant slug). */
  tenantId: string;
  /** display name shown in the header wordmark (e.g. the tenant brand name). */
  brandName: string;
  /** the AA-legible on-dark accent triplet injected as --accent (e.g. "231 72% 67%"). */
  accentHsl: string;
  /** same-origin logo path under /public, or null to keep the CEXAI brand mark. */
  logoPath: string | null;
  /** alt text for the logo. */
  logoAlt: string;
  /** inline brand-initials monogram SVG (R-006 D2) or null. Rendered by the Wordmark when the
   *  tenant has NO logo -- a known tenant never falls back to the CEXAI mark, never empty. */
  monogramSvg: string | null;
  /** per-tenant document title ("<brand> -- Capability Console", R-006 D3) or null to keep the
   *  default title untouched. */
  title: string | null;
}

/** The MANUAL registry of admin-themable tenants. Each entry reuses the shared brandTheme
 *  sample (one reskin file, both surfaces) and the logo copied under
 *  public/tenants/<id>/. ADD-ONLY: a new tenant adds a row here; nothing existing
 *  changes. The default ("cexai") is the ABSENCE of an entry (no override).
 *
 *  PRECEDENCE (R-006 D3): a manual row here ALWAYS WINS over a GENERATED entry for the same
 *  slug (generatedAdminThemes.json), which in turn wins over the default. `monogramSvg` /
 *  `title` are optional additive fields a manual row MAY declare; absent -> null (the exact
 *  pre-R-006 behaviour for the existing rows). */
const ADMIN_TENANTS: Record<
  string,
  {
    brand: BrandTheme;
    logoPath: string | null;
    monogramSvg?: string | null;
    title?: string | null;
  }
> = {
  "demo-orbit": {
    brand: ORBIT_BRAND_SAMPLE,
    logoPath: "/tenants/demo-orbit/logo.png",
  },
};

/** Tenant selectors that mean "no override -- the default CEXAI cyan dark-lab". */
const DEFAULT_SELECTORS = new Set(["", "default", "cexai"]);

/** Resolve the admin tenant theme for a SELECTOR. With no argument the selector is the
 *  build-time config.activeTenant (NEXT_PUBLIC_TENANT) -- the EXACT pre-existing behaviour
 *  (every legacy caller passes nothing, so it is byte-identical). An explicit ``selector``
 *  (the validated runtime ?tenant slug -- admin runtime-tenant) takes precedence over the
 *  env. Returns null for the default (no/"default"/"cexai"/unknown id) so the admin renders
 *  the current cyan dark-lab UNCHANGED. A known tenant whose brand primary is a valid triplet
 *  yields its on-dark accent + logo + name. Total (never throws).
 *
 *  HARDENING (runtime-tenant): the lookup is OWN-PROPERTY only -- a user-controlled ?tenant
 *  slug (e.g. "constructor"/"toString") must never resolve to an inherited Object.prototype
 *  member; those are not tenants and are rejected to the default. */
export function resolveAdminTheme(selector?: string): AdminTenantTheme | null {
  const raw = selector !== undefined ? selector : config.activeTenant || "";
  const id = raw.trim().toLowerCase();
  if (DEFAULT_SELECTORS.has(id)) return null;
  // MANUAL row WINS (R-006 D3 precedence: manual > generated > default). This branch keeps the
  // exact pre-R-006 semantics for manual rows, INCLUDING the malformed-brand -> default degrade.
  if (Object.prototype.hasOwnProperty.call(ADMIN_TENANTS, id)) {
    const entry = ADMIN_TENANTS[id];
    const primary = entry.brand?.tokens?.primary;
    const accentHsl = primary ? deriveOnDarkAccent(primary) : null;
    if (!accentHsl) {
      // R-019 disclosure: a MANUAL ADMIN_TENANTS row is expected to carry a real,
      // well-formed brand.tokens.primary -- silently degrading to the default cyan
      // here means the curated row is missing it or it failed the HSL shape guard.
      // Dev-only warn (never prod); the degrade-never fallback itself is unchanged.
      warnTokenFallback(
        'admin tenant "' + id + '" has no usable brand.tokens.primary (' +
        (primary ? "malformed value" : "missing") +
        ') -- falling back to the default CEXAI cyan accent'
      );
      return null; // malformed brand -> degrade to the default cyan.
    }
    return {
      tenantId: id,
      brandName: entry.brand.name || id,
      accentHsl,
      logoPath: entry.logoPath,
      logoAlt: entry.brand.logoAlt || entry.brand.name || id,
      monogramSvg: entry.monogramSvg ?? null,
      title: entry.title ?? null,
    };
  }
  // GENERATED entry (R-006 Admin Theming Bridge): emitted at distill (_carry_admin_theme) or
  // collected at predev (scripts/load-generated-admin-themes.mjs). The accent derives from the
  // brand primary ONLY when the generator attested source === "brand"; a colours-less tenant
  // keeps the EXACT default cyan accent (the mechanic's honest default -- never a fabricated
  // brand colour) while still carrying its name + monogram + title (D2: a known tenant never
  // renders the CEXAI mark). An absent/malformed entry -> null -> the default cyan dark-lab,
  // byte-identical to a tree with no generated registry at all (degrade-never).
  const gen = generatedAdminEntryFor(id);
  if (!gen) return null; // unknown id -> default cyan.
  let accentHsl: string = CEXAI_ACCENT_HSL;
  if (gen.source === "brand") {
    const derived = gen.brand.tokens?.primary
      ? deriveOnDarkAccent(gen.brand.tokens.primary)
      : null;
    if (derived) {
      accentHsl = derived;
    } else {
      // R-019 disclosure: the generator ATTESTED source==="brand" (a real brand colour
      // should be present), yet the primary token is missing/malformed -- that is a
      // genuine mismatch worth a dev-only trace, not the honest "source=default" case
      // (which never warns -- see the comment above this block). Fallback unchanged.
      warnTokenFallback(
        'admin tenant "' + id + '" is attested source="brand" but its primary token is ' +
        (gen.brand.tokens?.primary ? "malformed" : "missing") +
        ' -- falling back to the default CEXAI cyan accent'
      );
    }
    // malformed primary -> keep the default cyan (degrade-never).
  }
  return {
    tenantId: id,
    brandName: gen.brand.name || id,
    accentHsl,
    logoPath: gen.logoPath,
    logoAlt: gen.brand.logoAlt || gen.brand.name || id,
    monogramSvg: gen.monogramSvg,
    title: gen.title,
  };
}

// ---------------------------------------------------------------------------
// RUNTIME ?tenant RESOLUTION (admin runtime-tenant -- THEME + PREVIEW ONLY)
// ---------------------------------------------------------------------------
//
// ONE admin build serves every tenant by URL: the public site's "Admin" link is
// ``<adminUrl>?tenant=<slug>``. This block resolves THAT slug into the admin THEME +
// the preview brand at RUNTIME, replacing build-time NEXT_PUBLIC_TENANT for theming.
//
// SECURITY BOUNDARY (load-bearing): ?tenant reaches ONLY the theme/preview. It is NEVER
// a data selector -- the DATA tenant_id is the auth/RLS identity (the Supabase session
// JWT app_metadata.tenant_id claim, read in lib/supabase.tenantFromSession and bound in
// lib/auth.tsx; dev-mode uses the static FIXTURE_TENANT). Nothing in this module touches
// auth or the data layer, and no fetch reads its output -- a URL param cannot widen or
// override data access.

/** Strict tenant-slug shape guard. MIRRORS the backend public_reader._SLUG_RE and
 *  apps/public_site/lib/slug.isValidSlug -- ``^[a-z0-9][a-z0-9_-]{0,63}$``: the leading
 *  class forbids a leading "-"/"_"/"."; there is no "." anywhere so ".." can never match;
 *  the bound caps the length at 64. DEFENCE-IN-DEPTH: a malformed ?tenant value is rejected
 *  by SHAPE before it is ever used as a theme selector (it can carry no path/SQL/script).
 *  Total (never throws). */
const TENANT_SLUG_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/;

export function isValidTenantSlug(raw: unknown): boolean {
  return typeof raw === "string" && TENANT_SLUG_RE.test(raw.trim());
}

// ---------------------------------------------------------------------------
// GENERATED ADMIN-THEME REGISTRY (R-006 Admin Theming Bridge)
// ---------------------------------------------------------------------------
//
// lib/generatedAdminThemes.json is the machine-written half of the theme registry:
// { <slug>: { brand: {name, logoAlt, tokens}, logoPath, monogramSvg, title, source } }.
// Writers: cex_distill._carry_admin_theme (a distilled repo ships exactly its own entry) and
// scripts/load-generated-admin-themes.mjs (Central predev collector over .cex/tenants/*/
// admin_theme.json). Every value below is RE-VALIDATED at this boundary (degrade-never): a
// malformed entry is DROPPED (that slug then behaves exactly like an unknown tenant), a
// non-same-origin logoPath is nulled, a non-<svg monogram is nulled, and `source` fails toward
// "default" (only an attested "brand" may drive the accent). NOTE (init order): this block sits
// AFTER TENANT_SLUG_RE on purpose -- the registry is sanitized once at module init.

/** One sanitized GENERATED admin-theme registry entry. */
export interface GeneratedAdminThemeEntry {
  brand: BrandTheme;
  logoPath: string | null;
  monogramSvg: string | null;
  title: string | null;
  source: "brand" | "default";
}

/** Same-origin logo path shape: absolute /path, safe chars only, no "..". */
const SAME_ORIGIN_LOGO_RE = /^\/[A-Za-z0-9_\-./]*$/;

/** Sanitize one raw generated entry. Null (dropped) when it carries nothing renderable. Total. */
function sanitizeGeneratedEntry(raw: unknown): GeneratedAdminThemeEntry | null {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const e = raw as Record<string, unknown>;
  const brandRaw = e.brand;
  if (!brandRaw || typeof brandRaw !== "object" || Array.isArray(brandRaw)) return null;
  const b = brandRaw as Record<string, unknown>;
  const name = typeof b.name === "string" ? b.name.trim() : "";
  const tokensRaw = b.tokens;
  const tokens: BrandTokens =
    tokensRaw && typeof tokensRaw === "object" && !Array.isArray(tokensRaw)
      ? (tokensRaw as BrandTokens)
      : {};
  const logoAlt = typeof b.logoAlt === "string" && b.logoAlt.trim() ? b.logoAlt : name;
  const logoPathRaw = e.logoPath;
  const logoPath =
    typeof logoPathRaw === "string" &&
    SAME_ORIGIN_LOGO_RE.test(logoPathRaw) &&
    !logoPathRaw.includes("..")
      ? logoPathRaw
      : null;
  const monogramSvg =
    typeof e.monogramSvg === "string" && e.monogramSvg.trimStart().startsWith("<svg")
      ? e.monogramSvg
      : null;
  const title = typeof e.title === "string" && e.title.trim() ? e.title : null;
  const source: "brand" | "default" = e.source === "brand" ? "brand" : "default";
  // an entry carrying NEITHER a name NOR a monogram has nothing honest to render -> dropped.
  if (!name && !monogramSvg) return null;
  return { brand: { name, logoAlt, tokens }, logoPath, monogramSvg, title, source };
}

/** Build the sanitized registry map (null-prototype: registry keys can never collide with
 *  Object.prototype members). Malformed top-level shapes -> an empty registry. Total. */
function buildGeneratedRegistry(raw: unknown): Record<string, GeneratedAdminThemeEntry> {
  const out: Record<string, GeneratedAdminThemeEntry> = Object.create(null);
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return out;
  for (const key of Object.keys(raw as Record<string, unknown>)) {
    const slug = key.trim().toLowerCase();
    if (!TENANT_SLUG_RE.test(slug) || DEFAULT_SELECTORS.has(slug)) continue;
    const entry = sanitizeGeneratedEntry((raw as Record<string, unknown>)[key]);
    if (entry) out[slug] = entry;
  }
  return out;
}

const GENERATED_ADMIN_TENANTS: Record<string, GeneratedAdminThemeEntry> =
  buildGeneratedRegistry(generatedAdminThemesJson as unknown);

/** Own-property lookup into the sanitized generated registry (hardening symmetric with the
 *  manual-map lookup: a prototype-member slug can never resolve). Total. */
function generatedAdminEntryFor(id: string): GeneratedAdminThemeEntry | null {
  return Object.prototype.hasOwnProperty.call(GENERATED_ADMIN_TENANTS, id)
    ? GENERATED_ADMIN_TENANTS[id]
    : null;
}

/** Inline-SVG -> data: URI for an <img>/<link rel="icon"> src. Rendering the monogram through
 *  an image sink (never raw HTML injection) keeps the generated SVG string inert. Total. */
export function monogramDataUri(svg: string): string {
  return "data:image/svg+xml;utf8," + encodeURIComponent(svg);
}

/** Normalise a Next ``searchParams`` ?tenant value (string | string[] | null | undefined)
 *  to a single candidate string, or null. A repeated ?tenant=a&tenant=b (array) takes the
 *  FIRST entry. Total. */
function firstParam(param: string | string[] | null | undefined): string | null {
  if (Array.isArray(param)) return param.length > 0 ? param[0] : null;
  return typeof param === "string" ? param : null;
}

/** The THEME the ?tenant query param OVERRIDES to, or null when the param does NOT resolve
 *  to a KNOWN admin tenant -- i.e. absent, malformed (fails the slug shape guard), an unknown
 *  slug, or a default selector ("cexai"/"default"). null means "no runtime override -> keep
 *  the build-time / default behaviour". THEME + PREVIEW ONLY -- never auth/data. Total. */
export function resolveAdminThemeParamOverride(
  param: string | string[] | null | undefined,
): AdminTenantTheme | null {
  const candidate = firstParam(param);
  if (!candidate || !isValidTenantSlug(candidate)) return null;
  return resolveAdminTheme(candidate); // known tenant -> theme; unknown/default selector -> null
}

/** The EFFECTIVE admin theme for a request: the ?tenant runtime override when it resolves to
 *  a known tenant, ELSE the build-time / default behaviour (config.activeTenant). Absent /
 *  invalid / unknown ?tenant => EXACT current behaviour (NEXT_PUBLIC_TENANT if set, else the
 *  default CEXAI cyan) -- byte-identical. Total (never throws). */
export function resolveAdminThemeFromParam(
  param: string | string[] | null | undefined,
): AdminTenantTheme | null {
  return resolveAdminThemeParamOverride(param) ?? resolveAdminTheme();
}

// ---------------------------------------------------------------------------
// :root ACCENT STYLE EMITTER
// ---------------------------------------------------------------------------

/** Build the ``:root{--accent: <triplet>}`` style string injected at the root layout
 *  for an active tenant. EMPTY string for the default (no tenant) -> nothing is
 *  injected, the tailwind fallback (the exact current cyan) stands -> byte-identical.
 *
 *  SHAPE GUARD: the accent value is re-validated through isHslTriplet (the same guard
 *  buildCssVars uses) before it reaches the markup, so only a well-formed triplet can
 *  ever be emitted -- no new injection sink. Total. */
export function buildAccentRootStyle(theme: AdminTenantTheme | null): string {
  if (!theme) return "";
  if (!isHslTriplet(theme.accentHsl)) return ""; // defence in depth.
  return `:root{--accent:${theme.accentHsl}}`;
}
