// ----------------------------------------------------------------------------
// brandText -- PURE + TOTAL display helpers for the white-label storefront.
//
// The public pages render an OPEN published payload (PublicCatalogItem: id + kind +
// published_at + the flattened tenant payload). The field NAMES are tenant/capability
// extensible, so the storefront picks well-known display keys DEFENSIVELY -- an absent
// field simply does not render (never throws, never assumes a field exists). This
// module centralizes that picking so the HOME hero, the catalog cards, and the PDP all
// agree on which payload key is "the title", "the price", "the gallery", etc.
//
// SECURITY NOTE: this module returns plain strings + URL CANDIDATES only. It NEVER
// emits markup and NEVER decides a media URL is safe -- the GALLERY URLs it returns are
// still gated by isSafeMediaSrc at the render boundary (MediaGallery). A string field is
// always rendered as text by the caller (never dangerouslySetInnerHTML).
//
// The ABOUT page is built from the tenant brand (BrandTheme: name/tagline/tokens/
// fontFamily) -- the ONLY identity the public /tenant-info contract carries. There is NO
// backend "voice"/"story" field, so the about model is HONEST: it surfaces what the
// brand actually published (name + tagline + palette) and never fabricates a narrative.
//
// ASCII-only + diacritic-free (house style). PURE DATA + PURE FUNCTIONS -- no React.
// ----------------------------------------------------------------------------

import type { BrandTheme } from "@/lib/brandTheme";
import type { PublicCatalogItem } from "@/lib/types";
import { tenantConfigFor } from "@/lib/tenantConfig";

/** Pick the first present, trimmed, non-empty string among ``keys``; '' if none. TOTAL. */
export function firstString(item: PublicCatalogItem, keys: readonly string[]): string {
  for (const k of keys) {
    const v = item[k];
    if (typeof v === "string" && v.trim()) return v.trim();
  }
  return "";
}

/** The item's display title (first of title/name/nome/headline), else its id. TOTAL. */
export function titleOf(item: PublicCatalogItem): string {
  return firstString(item, ["title", "name", "nome", "headline"]) || item.id;
}

/** A one-line summary/description for cards + the hero (first present). '' if none. */
export function summaryOf(item: PublicCatalogItem): string {
  return firstString(item, ["summary", "description", "descricao", "tagline", "subtitle"]);
}

/** The longer body/description for the PDP (prefers description over summary). '' if none. */
export function descriptionOf(item: PublicCatalogItem): string {
  return firstString(item, ["description", "descricao", "summary", "body", "texto"]);
}

/** A short price display: a string ("R$ 199,00") or a finite number coerced. '' if absent. */
export function priceOf(item: PublicCatalogItem): string {
  const v = item.price ?? item.preco ?? item.valor;
  if (typeof v === "string" && v.trim()) return v.trim();
  if (typeof v === "number" && Number.isFinite(v)) return String(v);
  return "";
}

/** The published date as YYYY-MM-DD ('' when null/absent/non-string). TOTAL. */
export function publishedDate(item: PublicCatalogItem): string {
  return typeof item.published_at === "string" ? item.published_at.slice(0, 10) : "";
}

/**
 * Collect GALLERY image-URL CANDIDATES from the open payload, in priority order:
 *   1. an array under ``images`` / ``imagens`` / ``gallery`` / ``photos`` (string entries),
 *   2. a single ``image`` / ``imagem`` / ``thumbnail`` / ``cover`` string.
 * Returns a de-duplicated list of NON-EMPTY string candidates. THESE ARE NOT VALIDATED
 * AS SAFE -- the caller (MediaGallery) gates each with isSafeMediaSrc before rendering.
 * Capped at 12 to bound the DOM. TOTAL.
 */
export function galleryCandidates(item: PublicCatalogItem): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  const push = (v: unknown) => {
    if (typeof v === "string" && v.trim() && !seen.has(v.trim())) {
      seen.add(v.trim());
      out.push(v.trim());
    }
  };
  for (const key of ["images", "imagens", "gallery", "galeria", "photos", "fotos"]) {
    const arr = item[key];
    if (Array.isArray(arr)) arr.forEach(push);
  }
  for (const key of ["image", "imagem", "thumbnail", "thumb", "cover", "capa"]) {
    push(item[key]);
  }
  return out.slice(0, 12);
}

/** One specs row: a label + a display value. */
export interface SpecRow {
  label: string;
  value: string;
}

/**
 * Extract simple SPEC / attribute rows from the open payload for the PDP. Two sources:
 *   1. a ``specs`` / ``attributes`` / ``ficha`` object of scalar values -> label/value
 *      rows (the key is the label; the scalar is the value);
 *   2. a ``specs`` ARRAY of { label/name/key, value } objects.
 * Only SCALAR values (string/number/boolean) are surfaced -- nested objects/arrays are
 * skipped (the structured sections renderer handles rich bodies). De-duplicated by label,
 * capped at 24. TOTAL: a payload without specs -> []. NEVER emits markup.
 */
export function specRows(item: PublicCatalogItem): SpecRow[] {
  const out: SpecRow[] = [];
  const seen = new Set<string>();
  const pushRow = (label: unknown, value: unknown) => {
    const l = String(label ?? "").trim();
    if (!l || seen.has(l.toLowerCase())) return;
    let v = "";
    if (typeof value === "string") v = value.trim();
    else if (typeof value === "number" && Number.isFinite(value)) v = String(value);
    else if (typeof value === "boolean") v = value ? "sim" : "nao";
    else return; // skip nested/complex values
    if (!v) return;
    seen.add(l.toLowerCase());
    out.push({ label: l, value: v });
  };
  for (const key of ["specs", "attributes", "atributos", "ficha", "especificacoes"]) {
    const src = item[key];
    if (Array.isArray(src)) {
      for (const row of src) {
        if (row && typeof row === "object") {
          const o = row as Record<string, unknown>;
          const label = o.label ?? o.name ?? o.nome ?? o.key ?? o.chave;
          pushRow(label, o.value ?? o.valor ?? o.v);
        }
      }
    } else if (src && typeof src === "object") {
      for (const [k, v] of Object.entries(src as Record<string, unknown>)) pushRow(k, v);
    }
  }
  return out.slice(0, 24);
}

/**
 * The HONEST rating/review summary for the PDP. Built ONLY from fields the published
 * payload actually carries -- it NEVER fabricates a star count or a review total. A
 * payload with no rating/review fields yields ``null`` (the PDP renders nothing).
 */
export interface RatingSummary {
  /** the average rating, clamped to [0,5] (the payload may use any 0..5 scale). '' nullable. */
  value: number;
  /** the rating value as a 1-decimal display string ("4.8"). */
  display: string;
  /** the number of reviews/ratings, when the payload carries a count (>=0); null otherwise. */
  count: number | null;
  /** true ONLY when the payload explicitly flags the rating/seller as verified. */
  verified: boolean;
}

/** Coerce a payload value to a finite number in [min,max], or null. TOTAL. */
function clampedNum(v: unknown, min: number, max: number): number | null {
  let n: number | null = null;
  if (typeof v === "number" && Number.isFinite(v)) n = v;
  else if (typeof v === "string" && v.trim()) {
    // accept "4,8" (pt-BR decimal comma) and "4.8".
    const parsed = Number(v.trim().replace(",", "."));
    if (Number.isFinite(parsed)) n = parsed;
  }
  if (n === null) return null;
  return Math.min(max, Math.max(min, n));
}

/**
 * Build the HONEST rating summary from the open payload. It surfaces a rating row ONLY
 * when the payload ACTUALLY carries a rating value (rating / rating_value / avaliacao /
 * nota / stars). The review count comes from a separate count field when present
 * (review_count / reviews / num_reviews / avaliacoes / total_reviews) -- a count alone
 * (no rating) does NOT synthesize a rating. ``verified`` is set only by an explicit
 * truthy flag. Returns null when NO rating field exists -> the PDP renders nothing
 * (honest-empty; never a fabricated review/rating). TOTAL. NEVER emits markup.
 */
export function ratingOf(item: PublicCatalogItem): RatingSummary | null {
  const raw =
    item.rating ??
    item.rating_value ??
    item.avaliacao ??
    item.nota ??
    item.stars ??
    item.estrelas;
  const value = clampedNum(raw, 0, 5);
  if (value === null) return null; // no rating field -> honest-empty (render nothing).

  let count: number | null = null;
  for (const k of [
    "review_count",
    "reviews_count",
    "num_reviews",
    "reviews",
    "avaliacoes",
    "total_reviews",
    "qtd_avaliacoes",
  ]) {
    const c = clampedNum(item[k], 0, Number.MAX_SAFE_INTEGER);
    if (c !== null) {
      count = Math.floor(c);
      break;
    }
  }

  const vf = item.verified ?? item.verificado ?? item.rating_verified;
  const verified = vf === true || vf === "true" || vf === 1;

  return { value, display: value.toFixed(1), count, verified };
}

/** One review entry for the optional reviews band. All strings; media is NOT here
 *  (any review media URL stays gated by isSafeMediaSrc at the render boundary). */
export interface ReviewEntry {
  /** the reviewer display name ('' when absent). */
  author: string;
  /** the per-review rating in [0,5], or null. */
  rating: number | null;
  /** the review body text ('' when absent). */
  body: string;
  /** a SAFE media URL candidate (UNVALIDATED -- gated by isSafeMediaSrc at render). '' otherwise. */
  media: string;
}

/**
 * Collect individual REVIEW entries from the open payload, ONLY from an explicit array
 * under ``reviews_list`` / ``review_items`` / ``customer_reviews`` / ``depoimentos``.
 * (The scalar ``reviews`` key is a COUNT, handled by ratingOf -- never treated as a list.)
 * Each entry surfaces author/rating/body verbatim as TEXT; a per-review media url is
 * returned UNVALIDATED (the caller gates it with isSafeMediaSrc). Capped at 12. TOTAL:
 * no review array -> []. NEVER fabricates a review.
 */
export function reviewsOf(item: PublicCatalogItem): ReviewEntry[] {
  const out: ReviewEntry[] = [];
  for (const key of ["reviews_list", "review_items", "customer_reviews", "depoimentos"]) {
    const arr = item[key];
    if (!Array.isArray(arr)) continue;
    for (const row of arr) {
      if (!row || typeof row !== "object") continue;
      const o = row as Record<string, unknown>;
      const author = typeof o.author === "string" ? o.author.trim()
        : typeof o.name === "string" ? o.name.trim()
        : typeof o.autor === "string" ? o.autor.trim() : "";
      const body = typeof o.body === "string" ? o.body.trim()
        : typeof o.text === "string" ? o.text.trim()
        : typeof o.comment === "string" ? o.comment.trim()
        : typeof o.texto === "string" ? o.texto.trim() : "";
      const rating = clampedNum(o.rating ?? o.nota ?? o.stars, 0, 5);
      const mediaRaw = o.image ?? o.imagem ?? o.media ?? o.photo;
      const media = typeof mediaRaw === "string" ? mediaRaw.trim() : "";
      // skip an entry with nothing to show (no body and no author).
      if (!author && !body) continue;
      out.push({ author, rating, body, media });
      if (out.length >= 12) return out;
    }
  }
  return out;
}

/** One paragraph of the honest brand story. */
export interface AboutParagraph {
  /** a short heading for the block. */
  heading: string;
  /** the body text (always factual: derived from the published brand, never invented). */
  body: string;
}

/** The honest about/brand model the AboutView renders. */
export interface BrandAbout {
  /** the brand display name (or a neutral fallback). */
  name: string;
  /** the brand tagline, when published ('' otherwise). */
  tagline: string;
  /** the honest narrative blocks (built from what the brand actually published). */
  paragraphs: AboutParagraph[];
  /** a small palette of the brand's published token swatches (HSL triplets), for display. */
  swatches: { label: string; hsl: string }[];
}

// ---------------------------------------------------------------------------
// WHITE-LABEL HOME COPY (brand-agnostic by default; brand-aware where useful)
// ---------------------------------------------------------------------------
//
// The HOME hero + value pillars + editorial/CTA copy used to be CAT-SPECIFIC static
// strings ("para o seu gato", "felinos"). On a white-label storefront that is a leak:
// a non-cat tenant must NOT show cat copy. So buildHomeCopy derives the home editorial
// from the tenant brand context (name + tagline) with a NEUTRAL, brand-agnostic
// FALLBACK. The brand name is woven in where it sharpens the copy; nothing here invents
// a vertical (no "gatos"/"felinos") -- the only domain words come from the tenant's own
// published tagline, rendered verbatim as text.
//
// The universal BR-commerce trust row (PIX / parcelamento / troca / Feito no Brasil)
// stays separate (TrustRow + TRUST_SIGNALS) -- it is generic e-commerce trust language,
// not a vertical claim, so it is intentionally NOT re-derived here.

/** One home value pillar (icon key + heading + body). The 3rd-pillar glyph is VERTICAL-AWARE
 *  (resolved in buildHomeCopy): the RETAIL default (demo-acme + unknown slug) uses ``cat``
 *  (zero-regression for the retail vitrine), while a SERVICES tenant uses the brand-NEUTRAL
 *  ``heart`` glyph -- so a non-cat tenant never inherits a cat-face. ``headset`` is the
 *  services "atendimento" glyph used by the vertical-aware 2nd pillar. */
export interface HomePillar {
  icon: "sparkle" | "shield" | "heart" | "headset" | "cat";
  title: string;
  body: string;
}

/** The white-label home editorial copy, derived from the brand (neutral fallback). */
export interface HomeCopy {
  /** the hero eyebrow (small uppercase label above the title). */
  eyebrow: string;
  /** the hero supporting line shown when the brand published NO tagline. */
  heroFallbackTagline: string;
  /** the three value pillars (brand-agnostic copy; brand name woven in). */
  pillars: HomePillar[];
  /** the closing-CTA supporting line. */
  ctaBody: string;
}

/** Options for buildHomeCopy. The copy is VERTICAL-AWARE: a services tenant (no products,
 *  no checkout) must not show a PIX/parcelamento/compra claim. The vertical can be supplied
 *  EITHER explicitly via ``isService`` OR resolved from the tenant ``shape.vertical`` by
 *  passing ``slug`` (the declarative source of truth -- not an ad-hoc kind check). An
 *  explicit ``isService`` wins when both are given. */
export interface HomeCopyOptions {
  /** true for a services-vertical tenant (e.g. an IT-services company). */
  isService?: boolean;
  /** the tenant slug -- when given (and ``isService`` is not), the vertical is read from
   *  tenantConfigFor(slug).shape.vertical (the declarative source of truth). */
  slug?: string;
}

/**
 * Build the white-label HOME copy from the tenant brand. The COPY never names a vertical
 * (no "gatos"/"felinos"), so a non-cat tenant shows neutral premium prose. The ICON of the
 * 3rd pillar is VERTICAL-AWARE: a SERVICES tenant gets the brand-neutral ``heart`` glyph
 * (never a cat-face), while the RETAIL default keeps the ``cat`` glyph (zero-regression for
 * the retail vitrine). The 2nd pillar is VERTICAL-AWARE: a product-retail
 * tenant gets a "Compra segura / PIX, parcelamento" claim; a SERVICES tenant gets a
 * support/atendimento claim instead (a services tenant has no checkout, so a PIX/compra
 * claim would be FALSE). The brand display name is woven in where it helps.
 * TOTAL: an absent/empty brand -> a neutral name + the same neutral copy. ASCII-only.
 */
export function buildHomeCopy(
  brand: BrandTheme | undefined,
  options: HomeCopyOptions = {},
): HomeCopy {
  const b = brand ?? {};
  const name = (b.name ?? "").trim();
  const displayName = name || "esta marca";
  // VERTICAL source: an explicit isService wins (back-compat); otherwise, when a slug is
  // given, read it from the declarative shape.vertical (the source of truth) -- never an
  // ad-hoc kind/slug heuristic. Absent both -> retail (false).
  const isService =
    typeof options.isService === "boolean"
      ? options.isService
      : typeof options.slug === "string" && options.slug.trim() !== ""
        ? tenantConfigFor(options.slug).shape.vertical === "services"
        : false;

  // The 2nd pillar is vertical-aware: a services tenant gets a support/atendimento claim,
  // NOT a PIX/parcelamento/compra checkout claim (which would be false -- no products).
  const trustPillar: HomePillar = isService
    ? {
        icon: "headset",
        title: "Atendimento humanizado",
        body:
          "Suporte rapido e proximo -- a equipe de " +
          displayName +
          " acompanha cada atendimento do inicio ao fim.",
      }
    : {
        icon: "shield",
        title: "Compra segura",
        body: "PIX, parcelamento e troca facil. Transparencia em cada etapa da compra.",
      };

  return {
    eyebrow: "Vitrine publica",
    heroFallbackTagline:
      "Um catalogo publicado, transparente e pronto para explorar -- sem login.",
    pillars: [
      {
        icon: "sparkle",
        title: "Curadoria premium",
        body:
          "Um catalogo enxuto e selecionado -- so o que vale a pena, escolhido a dedo por " +
          displayName +
          ".",
      },
      trustPillar,
      {
        // VERTICAL-AWARE 3rd-pillar glyph: the RETAIL default (demo-acme + unknown slug)
        // restores the ``cat`` glyph (zero-regression -- the retail vitrine has always shown
        // it); a SERVICES tenant gets the brand-NEUTRAL ``heart`` glyph (no cat-face leak).
        icon: isService ? "heart" : "cat",
        title: "Feito com cuidado",
        body:
          "Cada item publicado reflete a identidade de " +
          displayName +
          " -- nada generico, nada de pressa.",
      },
    ],
    ctaBody:
      "Tudo publicado, transparente e pronto para explorar -- sem login e sem cadastro.",
  };
}

/** The token keys (and labels) the About palette surfaces, in display order. */
const ABOUT_SWATCH_KEYS: readonly [keyof NonNullable<BrandTheme["tokens"]>, string][] = [
  ["primary", "Primaria"],
  ["accent", "Destaque"],
  ["brand", "Marca"],
  ["secondary", "Secundaria"],
  ["foreground", "Texto"],
];

/**
 * Build the HONEST about model from the tenant brand. It surfaces ONLY what the public
 * tenant-info actually carries (name + tagline + the published palette) -- there is no
 * backend "story"/"voice" field, so this NEVER fabricates a narrative. The prose blocks
 * describe the published identity factually; absent fields simply do not produce a block.
 * TOTAL: an empty brand -> a single neutral block + a neutral name. ASCII-only.
 */
export function buildBrandAbout(brand: BrandTheme | undefined): BrandAbout {
  const b = brand ?? {};
  const name = (b.name ?? "").trim();
  const tagline = (b.tagline ?? "").trim();
  const displayName = name || "Esta marca";

  const paragraphs: AboutParagraph[] = [];
  if (tagline) {
    paragraphs.push({ heading: "O que move " + displayName, body: tagline });
  }
  paragraphs.push({
    heading: "Sobre este catalogo",
    body:
      displayName +
      " publica aqui o seu catalogo no CEXAI. Somente itens publicados aparecem nesta " +
      "vitrine -- cada pagina reflete a identidade da marca (cores, tipografia e tom).",
  });
  // A single honest paragraph about provenance (the public surface is published-only).
  paragraphs.push({
    heading: "Transparencia",
    body:
      "Esta e uma vitrine publica e sem login. Nenhum dado privado e exibido; os itens " +
      "marcados como amostra usam dados simulados e estao claramente sinalizados.",
  });

  const swatches: { label: string; hsl: string }[] = [];
  const tokens = b.tokens ?? {};
  for (const [key, label] of ABOUT_SWATCH_KEYS) {
    const v = tokens[key];
    if (typeof v === "string" && v.trim()) swatches.push({ label, hsl: v.trim() });
  }

  return { name: displayName, tagline, paragraphs, swatches };
}
