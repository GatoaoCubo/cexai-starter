// MIRRORS apps/public_site/lib/brandTheme.ts -- keep in sync.
//
// brandTheme.ts -- brand-theming layer for DualOutputFace (BRANDBOOK W1, Cell D).
//
// Maps the tenant brand (the 24 moldgen white_label tokens + visual fields) to CSS
// custom properties applied to the dual-output HTML face. Mirrors the storefront's
// applyBrandTheme() token contract so the two surfaces share one vocabulary.
//
// DEGRADE-NEVER: absent or empty theme -> neutral look (unchanged). All exports are
// TOTAL (never throw). ASCII-only source.

/** The 24 moldgen brand tokens (camelCase keys, mirrors brand.config.ts BrandTokens).
 *  23 are HSL triplets "H S% L%"; radius is a CSS length (e.g. "0.75rem"). */
export interface BrandTokens {
  background?: string;
  foreground?: string;
  card?: string;
  cardForeground?: string;
  popover?: string;
  popoverForeground?: string;
  primary?: string;
  primaryForeground?: string;
  secondary?: string;
  secondaryForeground?: string;
  muted?: string;
  mutedForeground?: string;
  accent?: string;
  accentForeground?: string;
  border?: string;
  input?: string;
  ring?: string;
  brand?: string;
  brandForeground?: string;
  brandMuted?: string;
  highlight?: string;
  highlightForeground?: string;
  highlightMuted?: string;
  radius?: string;
}

/** Minimal brand theme consumed by DualOutputFace and the export wrapper.
 *  ALL fields optional -- a partial or absent theme degrades to the neutral look. */
export interface BrandTheme {
  /** brand display name shown in the component and export header. */
  name?: string;
  /** short tagline shown under the name in the header. */
  tagline?: string;
  /** logo URL: https:// or data:image/ only (scheme-validated before render). */
  logo?: string;
  /** alt text for the logo image. */
  logoAlt?: string;
  /** The 24 moldgen CSS token values -- mirrors brand.config.ts BrandTokens. */
  tokens?: BrandTokens;
  /** base font-family value (applied to --font-family-base in the export CSS). */
  fontFamily?: string;
}

// ---------------------------------------------------------------------------
// TOKEN CONTRACT -- EXACTLY mirrors cex_moldgen_emit.TOKEN_TO_CSSVAR (Python)
// ---------------------------------------------------------------------------

const TOKEN_TO_CSSVAR: [keyof BrandTokens, string][] = [
  ["background", "--background"],
  ["foreground", "--foreground"],
  ["card", "--card"],
  ["cardForeground", "--card-foreground"],
  ["popover", "--popover"],
  ["popoverForeground", "--popover-foreground"],
  ["primary", "--primary"],
  ["primaryForeground", "--primary-foreground"],
  ["secondary", "--secondary"],
  ["secondaryForeground", "--secondary-foreground"],
  ["muted", "--muted"],
  ["mutedForeground", "--muted-foreground"],
  ["accent", "--accent"],
  ["accentForeground", "--accent-foreground"],
  ["border", "--border"],
  ["input", "--input"],
  ["ring", "--ring"],
  ["brand", "--brand"],
  ["brandForeground", "--brand-foreground"],
  ["brandMuted", "--brand-muted"],
  ["highlight", "--highlight"],
  ["highlightForeground", "--highlight-foreground"],
  ["highlightMuted", "--highlight-muted"],
  ["radius", "--radius"],
];

// ---------------------------------------------------------------------------
// TOKEN-VALUE SHAPE GUARD -- EXACTLY mirrors cex_moldgen_emit.is_hsl_triplet /
// is_css_length (Python). The dashboard and public surfaces re-validate token
// VALUES symmetrically at the render boundary, so a malformed value (a typo, a
// stray injection, a non-string) is DROPPED rather than emitted into the cascade.
// ---------------------------------------------------------------------------

/** The one token whose value is a CSS length (e.g. "0.75rem"); the other 23 are HSL. */
const RADIUS_KEY: keyof BrandTokens = "radius";

// `^\s*(\d{1,3})\s+(\d{1,3})%\s+(\d{1,3})%\s*$` -- mirrors Python _HSL_RE.
const HSL_TRIPLET_RE = /^\s*(\d{1,3})\s+(\d{1,3})%\s+(\d{1,3})%\s*$/;
// `^(0|\d*\.?\d+(px|rem|em|%))$` -- mirrors Python _RADIUS_RE (matched on the trimmed value).
const CSS_LENGTH_RE = /^(0|\d*\.?\d+(px|rem|em|%))$/;

/** True iff value is a valid "H S% L%" triplet with H<=360, S/L<=100. Mirrors
 *  cex_moldgen_emit.is_hsl_triplet exactly (same regex + same bounds). Total. */
export function isHslTriplet(value: unknown): boolean {
  if (typeof value !== "string") return false;
  const m = HSL_TRIPLET_RE.exec(value);
  if (!m) return false;
  const h = parseInt(m[1], 10);
  const s = parseInt(m[2], 10);
  const l = parseInt(m[3], 10);
  return h <= 360 && s <= 100 && l <= 100;
}

/** True iff value is a CSS length usable for --radius (e.g. "0.75rem"). Mirrors
 *  cex_moldgen_emit.is_css_length exactly (regex matched on the trimmed value). Total. */
export function isCssLength(value: unknown): boolean {
  return typeof value === "string" && CSS_LENGTH_RE.test(value.trim());
}

/** Render-boundary guard for a single brand token value: a valid HSL triplet for
 *  every colour token, a valid CSS length for ``radius``. A value that fails its
 *  shape check is DROPPED by buildCssVars (never emitted into the :root cascade).
 *  This makes the dashboard re-validate token VALUES symmetrically with the public
 *  surface and with the Python moldgen validator. Total. */
export function isValidTokenValue(key: keyof BrandTokens, value: unknown): boolean {
  return key === RADIUS_KEY ? isCssLength(value) : isHslTriplet(value);
}

// ---------------------------------------------------------------------------
// UTILS
// ---------------------------------------------------------------------------

/** True when a src is safe to embed as a logo URL (https: or data:image/ only).
 *  Logos are always images -- a more restrictive subset of isSafeMediaSrc. Total. */
export function isSafeLogoSrc(src: string): boolean {
  const s = (src ?? "").trim();
  if (/^https:\/\//i.test(s)) return true;
  if (/^data:image\//i.test(s)) return true;
  return false;
}

/** HTML-escape a value before injecting into markup. Total. */
function esc(v: unknown): string {
  return String(v ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ---------------------------------------------------------------------------
// R-019 DISCLOSURE (audit D1.7 PARTIAL: "default color palette renders silently
// with no disclosure when tenant brand tokens are unmapped"). A dev-only warn
// hook so a token that silently drops to its base/default CSS value leaves a
// TRACE during development -- never in a prod build, never a thrown error.
// ---------------------------------------------------------------------------

/** Dev-only disclosure: logs ``console.warn`` ONLY when ``NODE_ENV==="development"``
 *  (the SAME dev-gate convention as lib/exportAgent.ts / ExportAgentButton.tsx), so a
 *  brand/admin token that is present-but-malformed (or otherwise fails to map) and
 *  therefore silently falls back to a base/default value leaves a trace in local dev
 *  without adding any console noise to a deployed build. Total (never throws -- a
 *  console shim replacement can never break rendering). Exported so adminTheme.ts
 *  (and tests) share ONE disclosure mechanism rather than a second ad hoc check. */
export function warnTokenFallback(message: string): void {
  if (process.env.NODE_ENV !== "development") return;
  try {
    // eslint-disable-next-line no-console -- intentional, dev-gated diagnostic (R-019).
    console.warn("[brandTheme] " + message);
  } catch {
    /* a console shim must never break rendering (degrade-never). */
  }
}

// ---------------------------------------------------------------------------
// CSS VAR BUILDER
// ---------------------------------------------------------------------------

/** A font-family value is render-safe when it carries no CSS-control / injection chars
 *  ({ } ; < > and a raw var ref). It is a free-text identifier, not a shape, so we only
 *  reject the characters that could break out of the declaration. Total.
 *
 *  PARITY: byte-for-byte identical to the public_site mirror -- a hostile fontFamily
 *  such as "Inter; } body{display:none" must be DROPPED on BOTH surfaces, so the
 *  export-document <style> can never receive an injected live CSS rule. */
function isSafeFontFamily(value: string): boolean {
  if (/[{}<>;]/.test(value)) return false;
  if (value.includes("--")) return false;
  return true;
}

/** Build a CSS :root{} block string from the brand tokens and optional fontFamily.
 *  Empty string when the theme carries no tokens (degrade-never). Total.
 *
 *  RENDER-BOUNDARY GUARD: each token VALUE is re-validated against its shape
 *  (isValidTokenValue -- HSL triplet for colours, CSS length for ``radius``).
 *  A malformed value (typo, injection, wrong unit) is DROPPED here rather than
 *  emitted into the cascade, symmetric with the public_site mirror + the Python
 *  moldgen validator. Valid token values pass through unchanged (zero-regression).
 *
 *  R-019 DISCLOSURE: a token that was SUPPLIED (non-empty) but failed its shape
 *  guard -- i.e. the "unmapped -> falls back to the default cascade" case the audit
 *  flagged (D1.7 PARTIAL) -- gets a dev-only warnTokenFallback() call before being
 *  dropped. A token that was simply never supplied (every BrandTokens field is
 *  optional; a partial theme is legitimate) does NOT warn -- only a present-but-
 *  rejected value does, so this stays a real signal, not routine noise.
 *
 *  The fontFamily branch is likewise guarded by isSafeFontFamily (symmetric with
 *  public_site): a hostile font stack carrying CSS-control chars is DROPPED so it
 *  can never inject a live rule into the export-document <style> -- and likewise
 *  discloses when a SUPPLIED fontFamily was the one rejected. */
export function buildCssVars(theme: BrandTheme): string {
  const decls: string[] = [];
  const t = theme.tokens ?? {};
  for (const [key, cssVar] of TOKEN_TO_CSSVAR) {
    const val = t[key];
    if (val && typeof val === "string" && val.trim() && isValidTokenValue(key, val)) {
      decls.push(cssVar + ":" + val.trim());
    } else if (val !== undefined && val !== null && val !== "") {
      warnTokenFallback(
        'token "' + String(key) + '" was supplied but failed its shape check -- dropped; ' +
        cssVar + " falls back to the base/default CSS value"
      );
    }
  }
  if (
    theme.fontFamily &&
    typeof theme.fontFamily === "string" &&
    theme.fontFamily.trim() &&
    isSafeFontFamily(theme.fontFamily.trim())
  ) {
    decls.push("--font-family-base:" + theme.fontFamily.trim());
  } else if (theme.fontFamily) {
    warnTokenFallback(
      "fontFamily was supplied but failed its safety check -- dropped; " +
      "--font-family-base falls back to the base/default CSS value"
    );
  }
  return decls.length > 0 ? ":root{" + decls.join(";") + "}" : "";
}

// ---------------------------------------------------------------------------
// HTML HELPERS (for the exported standalone doc)
// ---------------------------------------------------------------------------

/** Build the brand header HTML fragment for the exported doc (logo + name + tagline).
 *  Uses direct HSL values from the tokens so the header renders without needing
 *  the :root cascade (total: works even when the doc shell is minimal). Empty string
 *  when neither name nor logo is present (degrade-never). Total. */
export function buildBrandHeaderHtml(theme: BrandTheme): string {
  const { name, tagline, logo, logoAlt, tokens } = theme;
  if (!name && !(logo && isSafeLogoSrc(logo))) return "";
  const primaryHsl = tokens?.primary ?? "220 90% 50%";
  const fgHsl = tokens?.primaryForeground ?? "0 0% 100%";
  const rad = tokens?.radius ?? "0.5rem";
  const wrapStyle = [
    "display:flex",
    "align-items:center",
    "gap:12px",
    "padding:14px 20px",
    "margin-bottom:20px",
    "background:hsl(" + primaryHsl + ")",
    "border-radius:" + rad,
    "color:hsl(" + fgHsl + ")",
    "font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif",
  ].join(";");
  let logoHtml = "";
  if (logo && isSafeLogoSrc(logo)) {
    const alt = esc(logoAlt || name || "logo").slice(0, 80);
    logoHtml =
      '<img src="' +
      esc(logo) +
      '" alt="' +
      alt +
      '" style="height:36px;object-fit:contain;max-width:160px;border-radius:4px">';
  }
  let nameHtml = "";
  if (name) {
    nameHtml =
      '<div><span style="font-size:20px;font-weight:700;line-height:1.2">' +
      esc(name) +
      "</span>";
    if (tagline) {
      nameHtml +=
        '<span style="display:block;font-size:12px;opacity:0.85;margin-top:3px">' +
        esc(tagline) +
        "</span>";
    }
    nameHtml += "</div>";
  }
  return '<div style="' + wrapStyle + '">' + logoHtml + nameHtml + "</div>";
}

/** Build the provenance/trust footer HTML for the exported doc.
 *  Always honest: flags real vs amostra, timestamp when available, capability. Total. */
export function buildProvenanceHtml(opts: {
  capability: string;
  real: boolean;
  createdAt?: string;
}): string {
  const { capability, real, createdAt } = opts;
  const label = real ? "resultado real" : "amostra -- dados simulados";
  const ts = createdAt
    ? " | gerado " + String(createdAt).slice(0, 19).replace("T", " ")
    : "";
  const cap = capability ? " | " + esc(capability) : "";
  return (
    '<div style="margin-top:24px;padding-top:12px;border-top:1px solid #dbe2ea;' +
    'color:#64748b;font:12px/1.5 monospace">CEXAI face humana -- ' +
    esc(label) +
    ts +
    cap +
    "</div>"
  );
}

// ---------------------------------------------------------------------------
// FIXTURE BRAND SAMPLE (ADD -- never replaces existing fixture data)
// ---------------------------------------------------------------------------

/** Fictitious default brand sample for DualOutputFace brand-theming proof (P0-A rebrand:
 *  this used to carry the real production brand's name + palette -- now a synthetic teal/navy
 *  palette not tied to any real tenant). Token values are "H S% L%" triplets matching the
 *  moldgen BrandTokens contract. */
export const DEFAULT_BRAND_SAMPLE: BrandTheme = {
  name: "Acme Pet Shop",
  tagline: "O marketplace do tutor de gato (amostra)",
  logoAlt: "Acme Pet Shop",
  tokens: {
    background: "0 0% 100%",
    foreground: "213 47% 12%",
    card: "0 0% 98%",
    cardForeground: "213 47% 12%",
    popover: "0 0% 100%",
    popoverForeground: "213 47% 12%",
    primary: "174 68% 50%",
    primaryForeground: "0 0% 100%",
    secondary: "213 35% 18%",
    secondaryForeground: "0 0% 100%",
    muted: "210 20% 96%",
    mutedForeground: "213 15% 50%",
    accent: "174 68% 50%",
    accentForeground: "0 0% 100%",
    border: "210 20% 88%",
    input: "210 20% 88%",
    ring: "174 68% 50%",
    brand: "174 68% 50%",
    brandForeground: "0 0% 100%",
    brandMuted: "174 30% 92%",
    highlight: "42 100% 50%",
    highlightForeground: "0 0% 10%",
    highlightMuted: "42 80% 93%",
    radius: "0.75rem",
  },
  fontFamily: "Inter, -apple-system, Segoe UI, sans-serif",
};

/** Orbit Tech (fictitious) brand sample for the admin-theme proof (BUILD R2 reskin proof;
 *  P0-A rebrand renamed the tenant from the former real-brand references to the fictitious
 *  "Orbit Tech", an IT-services tenant). The reskin is ROYAL BLUE primary + RED highlight --
 *  a palette distinct from the default sample -- so the same admin dashboard themes to Orbit
 *  Tech's identity, not the default brand sample.
 *
 *  These 24 token values are IDENTICAL to the overlay cex_tenant_bootstrap emitted for
 *  tenant=demo-orbit (brand.config.ts: primary/brand/accent/ring = "231 48% 48%",
 *  highlight = "4 90% 58%"), so the admin theme and the storefront overlay share one
 *  source of truth -- one reskin file, both surfaces. Token values are "H S% L%"
 *  triplets matching the moldgen BrandTokens contract; radius is a CSS length. */
export const ORBIT_BRAND_SAMPLE: BrandTheme = {
  name: "Orbit Tech",
  tagline: "Solucoes em Tecnologia",
  logoAlt: "Orbit Tech - Solucoes em Tecnologia",
  tokens: {
    background: "0 0% 100%",
    foreground: "0 0% 13%",
    card: "0 0% 100%",
    cardForeground: "0 0% 13%",
    popover: "0 0% 100%",
    popoverForeground: "0 0% 13%",
    primary: "231 48% 48%",
    primaryForeground: "0 0% 100%",
    secondary: "210 16% 96%",
    secondaryForeground: "0 0% 13%",
    muted: "210 16% 96%",
    mutedForeground: "215 16% 47%",
    accent: "231 48% 48%",
    accentForeground: "0 0% 100%",
    border: "0 0% 90%",
    input: "0 0% 90%",
    ring: "231 48% 48%",
    brand: "231 48% 48%",
    brandForeground: "0 0% 100%",
    brandMuted: "231 48% 95%",
    highlight: "4 90% 58%",
    highlightForeground: "0 0% 100%",
    highlightMuted: "4 90% 95%",
    radius: "0.625rem",
  },
  fontFamily: "Inter, -apple-system, Segoe UI, sans-serif",
};
