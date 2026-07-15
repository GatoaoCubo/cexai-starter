// MIRRORS apps/dashboard_web/lib/brandTheme.ts -- keep in sync.
//
// brandTheme.ts -- brand-theming layer (BRANDBOOK W1, Cell D), lifted verbatim
// for the L2 public site. The /public/tenant-info "brand" object maps 1:1 to
// BrandTheme (name/tagline/logo + the 24 moldgen tokens).
//
// Maps the tenant brand (the 24 moldgen white_label tokens + visual fields) to CSS
// custom properties applied to the page. Mirrors the storefront's
// applyBrandTheme() token contract so the surfaces share one vocabulary.
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

/** Minimal brand theme consumed by the public page chrome and the export wrapper.
 *  ALL fields optional -- a partial or absent theme degrades to the neutral look. */
export interface BrandTheme {
  /** brand display name shown in the chrome and export header. */
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
// UTILS
// ---------------------------------------------------------------------------

/** True when a src is safe to embed as a logo URL. Logos are always images -- a more
 *  restrictive subset of isSafeMediaSrc. Permits THREE shapes, all incapable of XSS or
 *  cross-origin exfiltration:
 *    1. ``https://...``            -- a remote image over TLS,
 *    2. ``data:image/...``         -- an inline image data URI,
 *    3. a same-origin ROOT-RELATIVE ``/path`` (e.g. "/images/tenants/x/logo.png") --
 *       a first-party committed asset on OUR OWN origin. A protocol-relative "//host"
 *       (cross-origin) is explicitly rejected (the second char must NOT be "/"), so a
 *       root-relative path can only ever resolve against the public site's own origin.
 *  Everything else (http:, javascript:, data:text/html, file:, a bare relative path) is
 *  dropped. Total -- never throws. */
export function isSafeLogoSrc(src: string): boolean {
  const s = (src ?? "").trim();
  if (/^https:\/\//i.test(s)) return true;
  if (/^data:image\//i.test(s)) return true;
  // same-origin root-relative path: starts with a single "/" and NOT "//" (protocol-
  // relative / cross-origin). Also forbid "/\" which some parsers treat as "//".
  if (/^\/[^/\\]/.test(s)) return true;
  return false;
}

// ---------------------------------------------------------------------------
// RENDER-BOUNDARY TOKEN GUARD (defense-in-depth)
// ---------------------------------------------------------------------------
//
// The public site is the UNAUTHENTICATED surface: it consumes the tenant brand
// from /public/tenant-info, which the backend forwards from the write path. The
// write path (cex_moldgen_emit.validate_spec) ALREADY shape-validates the 24
// tokens -- but the verifier flagged that the public render must NOT blindly
// trust that. So buildCssVars RE-VALIDATES every token value at the render
// boundary and DROPS any malformed one, mirroring the Python validators
// (is_hsl_triplet / is_css_length) byte-for-byte. A token that fails the shape
// check is never emitted into :root{} -- the fallback (the neutral / static
// default) wins for that var instead of a hostile or broken value.
//
// This is a DROP-the-bad-one policy (degrade-never), NOT a fail-closed reject:
// one malformed token must never blank the whole brand. ASCII-only. TOTAL.

/** Mirror of cex_moldgen_emit._HSL_RE: an "H S% L%" triplet. */
const HSL_TRIPLET_RE = /^\s*(\d{1,3})\s+(\d{1,3})%\s+(\d{1,3})%\s*$/;
/** Mirror of cex_moldgen_emit._RADIUS_RE: a CSS length usable for --radius. */
const CSS_LENGTH_RE = /^(0|\d*\.?\d+(px|rem|em|%))$/;

/** True iff value is a valid "H S% L%" triplet (H<=360, S/L<=100). Mirrors
 *  cex_moldgen_emit.is_hsl_triplet. Total. */
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
 *  cex_moldgen_emit.is_css_length. Total. */
export function isCssLength(value: unknown): boolean {
  return typeof value === "string" && CSS_LENGTH_RE.test(value.trim());
}

/** The one token whose value is a CSS length (every other token is an HSL triplet). */
const RADIUS_TOKEN: keyof BrandTokens = "radius";

/** True iff a token value is a SHAPE-VALID value for that token key (the render-boundary
 *  guard). radius -> CSS length; every other token -> HSL triplet. A value that also
 *  smuggles a raw CSS var ref ("--x") is rejected (mirrors the write-path value guard). */
function isValidTokenValue(key: keyof BrandTokens, value: unknown): boolean {
  if (typeof value !== "string") return false;
  if (value.includes("--")) return false; // no raw var refs (matches validate_spec)
  return key === RADIUS_TOKEN ? isCssLength(value) : isHslTriplet(value);
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
// CSS VAR BUILDER
// ---------------------------------------------------------------------------

/** A font-family value is render-safe when it carries no CSS-control / injection chars
 *  ({ } ; < > and a raw var ref). It is a free-text identifier, not a shape, so we only
 *  reject the characters that could break out of the declaration. Total. */
function isSafeFontFamily(value: string): boolean {
  if (/[{}<>;]/.test(value)) return false;
  if (value.includes("--")) return false;
  return true;
}

/** Build a CSS :root{} block string from the brand tokens and optional fontFamily.
 *
 *  RENDER-BOUNDARY GUARD (defense-in-depth): every token value is RE-VALIDATED here
 *  against the same shape the write path enforces (is_hsl_triplet / is_css_length).
 *  A token whose value FAILS the shape check is DROPPED -- it is never emitted into
 *  :root{}, so the static fallback wins for that var instead of a hostile / malformed
 *  value reaching the unauthenticated public surface. Dropping one bad token never
 *  blanks the rest (degrade-never).
 *
 *  Empty string when the theme carries no VALID tokens (degrade-never -> neutral look).
 *  Total -- never throws. */
export function buildCssVars(theme: BrandTheme): string {
  const decls: string[] = [];
  const t = theme.tokens ?? {};
  for (const [key, cssVar] of TOKEN_TO_CSSVAR) {
    const val = t[key];
    // render-boundary guard: only a SHAPE-VALID token value is emitted.
    if (isValidTokenValue(key, val)) {
      decls.push(cssVar + ":" + (val as string).trim());
    }
  }
  if (
    theme.fontFamily &&
    typeof theme.fontFamily === "string" &&
    theme.fontFamily.trim() &&
    isSafeFontFamily(theme.fontFamily.trim())
  ) {
    decls.push("--font-family-base:" + theme.fontFamily.trim());
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
