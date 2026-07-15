#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_product_ad_mold -- the product-ad HTML MOLD emitter (BRANDBOOK W2 + RICHEN).

THE conversion-grade STRUCTURE a tenant's ad fills. The founder writes the ad COPY
in parallel; this module builds the CONTAINER that makes the output "a altura de um
produto de anuncio" -- a self-contained, brand-themed, mobile-first HTML ad doc with
the 12 canonical sections in conversion order:

  1 brand header -> 2 hero -> 3 gallery -> 4 body (prose) -> 5 features (bullets) ->
  6 value -> 7 proof -> 8 offer -> 9 specs/ficha -> 10 FAQ -> 11 CTA2 ->
  12 footer (provenance/trust)

THE FULL CANONICAL CONTENT MODEL (RICHEN): the mold renders the full PDP/listing copy
set -- NOT a thin shell. The canonical copy fields (from docs/schema/
product_catalog_schema.yaml + the TUDAO listing mold) are: title (+seo_title),
key_features[] (BULLETS -- a DEDICATED section), description + long_description (the
PROSE body), why_it_works, benefits_functional[] + benefits_emotional[] (two distinct
groups), faq[]; plus the FICHA (frozen facts -- numeric dims, weight, materials[],
colors[], the attributes long-tail) and the IDENTITY (gtin/ean/mpn/sku/brand/model).

THE LOAD-BEARING SEAM (all 4 TUDAO research streams agree): structured attributes/
bullets are stored + rendered SEPARATE from the prose description -- only an adapter
may ever concatenate them. So in this mold the BULLETS (key_features -> section 5) and
the FICHA (-> section 9) render as their OWN sections; they are NEVER folded into the
prose body (section 4). ad_data_from_product() maps a canonical product record into the
mold's rich data while preserving this seam.

Four FILL-SOURCES feed the mold; each slot resolves independently:
  * BRAND -- name/tagline/logo + the 24 white-label tokens. ALWAYS fills (known).
            Reuses the EXACT moldgen token contract (cex_moldgen_emit.TOKEN_TO_CSSVAR,
            the same vars apps/dashboard_web/lib/brandTheme.ts mirrors) -> :root{} CSS
            vars, so the ad is brand-consistent with every other tenant surface.
  * COPY  -- headline/subheadline/benefits/faq/cta. May be empty -> an HONEST editable
            placeholder "[preencher: ...]", NEVER an invented claim.
  * MEDIA -- hero + gallery images. May be empty -> an upload-fallback dropzone (the
            same data-slot-key affordance cex_dual_output uses), NEVER a broken <img>.
  * DATA  -- offer (price/discount/urgency/guarantee), proof (rating/testimonials),
            specs. May be empty -> an honest placeholder, NEVER a fabricated price/rating.

RELATION TO cex_dual_output: cex_dual_output renders the GENERIC dual-surface face for
any capability's output_sections. This module is the SPECIALIZED, conversion-optimized
human_html for the `ads` surface specifically -- the rich mold the ad copy + media +
brand fill. The two are complementary (generic report vs. conversion ad), not duplicative.

ADOPTS THE PROVEN PDP DESIGN-SYSTEM (MERGE A): the emitted ad IS the reference retail catalog
"produto" (PDP) page, improved. It CONSUMES the tenant's 24 brand tokens (the same
cex_moldgen_emit contract the storefront's applyBrandTheme uses) via _resolve_brand_tokens
-> a complete :root{} that the structural CSS reads, so the ad renders in the tenant's
brand. The section order mirrors the proven PDP (gallery -> why-it-works/benefits -> proof
-> offer -> specs -> FAQ), the headings use the design-system type scale (text-display/
h1/h2/h3 with the premium negative tracking), and the <head> ships static SEO (og/twitter/
canonical/JSON-LD Product schema) + an @media print stylesheet for a clean PDF. With NO
tokens the ad degrades to a neutral baseline (unchanged look) -- never a broken theme.

PURE + TOTAL: emit_product_ad(data) is a deterministic projection -- no LLM, no network,
no DB, no file IO, no clock. Given the same data it always yields the same HTML, and a
missing/malformed slot degrades to a valid-but-honest placeholder; it NEVER raises.

ASCII-only source per .claude/rules/ascii-code-rule.md. The EMITTED HTML may carry PT-BR
copy with full diacritics (that is runtime CONTENT supplied by the caller, not code) --
this module's own string constants stay diacritic-free.

Design laws baked in: degrade-never (every slot has an honest fallback), never-fabricate
(no invented price/claim/media), reuse-the-contract (the brand tokens come from the one
moldgen contract -- this module declares NO new token vocabulary), a11y (lang + alt text +
semantic tags + contrast-paired tokens), repeated-CTA, provenance (honest real/sample).

CLI:
  python _tools/cex_product_ad_mold.py --demo full     # full data set -> all 12 sections
  python _tools/cex_product_ad_mold.py --demo sparse    # sparse -> honest placeholders
  python _tools/cex_product_ad_mold.py --demo branded   # full data + a DISTINCT tenant palette
  python _tools/cex_product_ad_mold.py --demo product   # a CANONICAL product record -> rich ad
  python _tools/cex_product_ad_mold.py --demo full --out /tmp/ad.html

Importable API: emit_product_ad(data), demo_data(full=True, branded=False),
demo_product_record(), ad_data_from_product(product, brand=..., real=...),
_resolve_brand_tokens(brand), SECTION_ORDER.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from html import escape as _html_escape
from typing import Any, Dict, List, Mapping, Optional, Sequence

# --------------------------------------------------------------------------- #
# REUSE the moldgen token contract (single source of truth -- do NOT reinvent).
# Both modules live in _tools/; ensure the sibling import resolves whether this
# runs as a script (sys.path[0] == _tools) or is imported with _tools on the path.
# --------------------------------------------------------------------------- #
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from cex_moldgen_emit import (  # noqa: E402  (path bootstrapped just above)
    TOKEN_TO_CSSVAR,
    RADIUS_KEY,
    is_css_length,
    is_hsl_triplet,
)

# THE neutral baseline -- imported from the ONE canonical source (cex_neutral_tokens) so the
# 24-token literal is defined exactly once (council MEDIUM dedup). cex_brand_context +
# cex_brand_writeback re-import _NEUTRAL_TOKENS from THIS module for back-compat; the values
# are byte-identical to the former in-module literal -> zero behavior change.
from cex_neutral_tokens import _NEUTRAL_TOKENS  # noqa: E402

# --------------------------------------------------------------------------- #
# Module constants -- no side effects.
# --------------------------------------------------------------------------- #
SCHEMA_VERSION = "1.0"

# The 12 canonical sections in conversion order (the mold's contract). RICHEN added
# `body` (the prose description) + `features` (the key_features bullets) between the
# gallery and the value-prop, so the full PDP/listing content renders -- not a thin shell.
SECTION_ORDER = (
    "brand_header", "hero", "gallery", "body", "features", "value", "proof",
    "offer", "specs", "faq", "cta2", "footer",
)

# The honest placeholder prefix -- a missing COPY/DATA slot renders this, never a claim.
_PH_OPEN = "[preencher: "
_PH_CLOSE = "]"

# A sensible default CTA when the copy supplies none (still a real, generic call to action).
_DEFAULT_CTA = "Comprar agora"

# _NEUTRAL_TOKENS is imported above from cex_neutral_tokens (the ONE canonical source). It is
# keyed by the SAME 24 moldgen token keys (cex_moldgen_emit.TOKEN_TO_CSSVAR), so neutral and
# branded both flow through ONE contract: _resolve_brand_tokens overlays a tenant's validated
# tokens on top of these and ALWAYS writes a complete :root{}. With no tokens the ad renders in
# this neutral look. This single table REPLACES the former hardcoded css-var _FALLBACK dict
# (the resolver is the front door).

# The structural CSS references brand vars with a NEUTRAL inline fallback
# (hsl(var(--primary, <neutral>))) as belt-and-suspenders. That fallback table is DERIVED
# from _NEUTRAL_TOKENS via the moldgen contract -- so there is no second hand-kept source of
# neutral values. Keyed by css-var-short-name (the '--' stripped), matching the %()s slots.
_FALLBACK_CSS = {cssvar[2:]: _NEUTRAL_TOKENS[key] for key, cssvar in TOKEN_TO_CSSVAR}


# --------------------------------------------------------------------------- #
# THE entry.
# --------------------------------------------------------------------------- #
def emit_product_ad(data: Optional[Mapping[str, Any]] = None) -> str:
    """Project an ad `data` mapping into a self-contained, brand-themed HTML ad doc.

    `data` keys (every one OPTIONAL -- a missing key degrades to honest placeholders):
      brand   -- {name, tagline, logo, logoAlt, tokens{24}, fontFamily, domain}  (BRAND)
      product -- {name, category, brand, sku, gtin, model}                       (identity)
      copy    -- {title, seo_title, seo_description, headline, subheadline,
                  description, long_description, why_it_works, key_features[],
                  benefits_functional[], benefits_emotional[], benefits[], faq[],
                  cta_label, cta_sub}                                            (COPY)
      media   -- {hero: {src,alt}|str, gallery: [{src,alt}|str, ...]}            (MEDIA)
      offer   -- {price, original_price, discount, installments, urgency,
                  guarantee, shipping}                                           (DATA)
      proof   -- {rating, count, testimonials: [{quote, author}, ...]}           (DATA)
      ficha   -- {dimensions, weight, materials[], colors[], attributes,
                  identity{gtin,ean,mpn,sku,brand,model}}                        (DATA -- frozen facts)
      specs   -- [{label, value}, ...]                                           (DATA)
      meta    -- {real: bool, created: ISO-8601 str, sources: [str, ...]}        (provenance)

    THE LOAD-BEARING SEAM: copy.key_features (BULLETS -> the `features` section) and the
    `ficha` (-> the `specs` section) render as their OWN sections; they are NEVER folded
    into the prose copy.description / copy.long_description (-> the `body` section).

    Returns ONE self-contained HTML document (inline CSS, mobile-first, brand-themed,
    a11y, the CTA repeated). PURE + TOTAL: never raises; never fabricates a claim/price/
    media; BRAND always fills (or falls back to a neutral look).
    """
    d = data if isinstance(data, Mapping) else {}
    brand = _as_map(d.get("brand"))
    product = _as_map(d.get("product"))
    copy = _as_map(d.get("copy"))
    media = _as_map(d.get("media"))
    offer = _as_map(d.get("offer"))
    proof = _as_map(d.get("proof"))
    ficha = _as_map(d.get("ficha"))
    specs = d.get("specs")
    meta = _as_map(d.get("meta"))

    title = _doc_title(brand, product, copy)
    head = _head(brand, product, copy, media, offer, proof, meta, title)

    body_parts: List[str] = []
    body_parts.append(_section_brand_header(brand))
    body_parts.append(_section_hero(brand, product, copy, media, offer))
    body_parts.append(_section_gallery(media))
    body_parts.append(_section_body(copy))          # PROSE: description + long_description
    body_parts.append(_section_features(copy))      # BULLETS: key_features (DEDICATED seam)
    body_parts.append(_section_value(copy))         # benefits_functional + _emotional groups
    body_parts.append(_section_proof(proof))
    body_parts.append(_section_offer(offer, copy))
    body_parts.append(_section_specs(specs, product, ficha))  # FICHA: frozen facts (DEDICATED seam)
    body_parts.append(_section_faq(copy))
    body_parts.append(_section_cta2(copy, offer))
    body_parts.append(_section_footer(brand, meta))

    body = "\n".join(p for p in body_parts if p)
    return (
        "<!doctype html>\n"
        '<html lang="pt-BR">\n'
        "<head>\n" + head + "\n</head>\n"
        '<body>\n<main class="ad-doc">\n' + body + "\n</main>\n</body>\n</html>\n"
    )


# --------------------------------------------------------------------------- #
# <head> + brand-themed CSS (REUSES the moldgen token contract).
# --------------------------------------------------------------------------- #
def _head(
    brand: Mapping[str, Any],
    product: Mapping[str, Any],
    copy: Mapping[str, Any],
    media: Mapping[str, Any],
    offer: Mapping[str, Any],
    proof: Mapping[str, Any],
    meta: Mapping[str, Any],
    title: str,
) -> str:
    """The complete static <head>: brand-themed CSS + SEO (og/twitter/canonical/JSON-LD).

    The JSON-LD Product schema, Open Graph + Twitter cards are emitted as STATIC strings
    (no react-helmet / no client JS). A CSP COMMENT documents the header the caller should
    serve (this module does not control HTTP). never-fabricate: any SEO tag whose value is
    absent is OMITTED (no placeholder leaks into a meta/JSON-LD value).
    """
    root = _resolve_brand_tokens(brand)
    css = root + "\n" + _STRUCTURAL_CSS + "\n" + _DESIGN_SYSTEM_CSS
    seo = _seo_head(brand, product, copy, media, offer, proof, meta, title)
    return (
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="robots" content="index, follow">\n'
        "<!-- Content-Security-Policy: serve this doc with a CSP HEADER (not a meta) supplied\n"
        "     by the caller, e.g.  default-src 'self'; img-src https: data:; style-src\n"
        "     'unsafe-inline'; script-src 'none'; base-uri 'none'; form-action 'self'\n"
        "     (this mold ships NO executable script; the JSON-LD below is inert data). -->\n"
        "<title>" + _esc(title) + "</title>\n"
        + (seo + "\n" if seo else "")
        + "<style>\n" + css + "\n</style>"
    )


def _resolve_brand_tokens(brand: Any) -> str:
    """Resolve a tenant's 24 brand tokens into a COMPLETE :root{} CSS block.

    REUSES the moldgen contract (cex_moldgen_emit.TOKEN_TO_CSSVAR) -- the SAME tokens the
    gato storefront's applyBrandTheme pushes to :root -- so an emitted ad is brand-consistent
    with every other tenant surface and adopts the proven PDP design-system.

    Each of the 24 css-vars resolves independently: the tenant's value when present AND valid
    (validated via the moldgen is_hsl_triplet / is_css_length predicates, so a malformed token
    is DROPPED, never a broken color), ELSE the _NEUTRAL_TOKENS baseline. The block is ALWAYS
    complete -> degrade-never: with no tokens every var is the neutral baseline (unchanged
    look); with a full token set the ad renders in the tenant's brand. PURE + TOTAL.
    """
    bm = _as_map(brand)
    tokens = _as_map(bm.get("tokens"))
    decls: List[str] = []
    for key, cssvar in TOKEN_TO_CSSVAR:
        raw = tokens.get(key)
        resolved: Optional[str] = None
        if isinstance(raw, str) and raw.strip():
            v = raw.strip()
            ok = is_css_length(v) if key == RADIUS_KEY else is_hsl_triplet(v)
            if ok:
                resolved = v
        if resolved is None:
            resolved = _NEUTRAL_TOKENS[key]  # degrade-never baseline
        decls.append("%s:%s" % (cssvar, resolved))
    font_family = bm.get("fontFamily")
    if isinstance(font_family, str) and font_family.strip():
        decls.append("--font-family-base:%s" % font_family.strip())
    return ":root{%s}" % ";".join(decls)


# --------------------------------------------------------------------------- #
# Static SEO head (og / twitter / canonical / JSON-LD Product schema).
# never-fabricate: every tag is gated on a real value; absent -> omitted.
# --------------------------------------------------------------------------- #
def _seo_head(
    brand: Mapping[str, Any],
    product: Mapping[str, Any],
    copy: Mapping[str, Any],
    media: Mapping[str, Any],
    offer: Mapping[str, Any],
    proof: Mapping[str, Any],
    meta: Mapping[str, Any],
    title: str,
) -> str:
    name = _s(product.get("name")) or _s(copy.get("headline")) or _s(brand.get("name"))
    desc = _s(copy.get("subheadline")) or _s(copy.get("headline")) or _s(product.get("name"))
    bname = _s(brand.get("name"))
    canonical = _canonical_url(brand, meta)
    hero_src, _hero_alt = _media_src_alt(media.get("hero"))
    img = hero_src if (hero_src and _is_safe_media_src(hero_src)) else ""

    parts: List[str] = []
    if desc:
        parts.append('<meta name="description" content="%s">' % _esc(desc))
    if canonical:
        parts.append('<link rel="canonical" href="%s">' % _esc(canonical))

    # Open Graph (product).
    parts.append('<meta property="og:type" content="product">')
    if title:
        parts.append('<meta property="og:title" content="%s">' % _esc(title))
    if desc:
        parts.append('<meta property="og:description" content="%s">' % _esc(desc))
    if bname:
        parts.append('<meta property="og:site_name" content="%s">' % _esc(bname))
    if canonical:
        parts.append('<meta property="og:url" content="%s">' % _esc(canonical))
    if img:
        parts.append('<meta property="og:image" content="%s">' % _esc(img))

    # Twitter card.
    parts.append('<meta name="twitter:card" content="%s">'
                 % ("summary_large_image" if img else "summary"))
    if title:
        parts.append('<meta name="twitter:title" content="%s">' % _esc(title))
    if desc:
        parts.append('<meta name="twitter:description" content="%s">' % _esc(desc))
    if img:
        parts.append('<meta name="twitter:image" content="%s">' % _esc(img))

    ld = _product_jsonld(name, desc, img, bname, offer, proof)
    if ld:
        parts.append(ld)
    return "\n".join(parts)


def _canonical_url(brand: Mapping[str, Any], meta: Mapping[str, Any]) -> str:
    """A canonical URL: an explicit meta.canonical if absolute, else https://<domain>.
    never-fabricate: no domain and no explicit URL -> "" (the canonical tag is omitted)."""
    explicit = _s(meta.get("canonical"))
    if explicit.startswith("https://") or explicit.startswith("http://"):
        return explicit
    domain = _s(brand.get("domain")).strip().strip("/")
    if not domain:
        return ""
    if not (domain.startswith("https://") or domain.startswith("http://")):
        domain = "https://" + domain
    return domain


def _product_jsonld(
    name: str, desc: str, img: str, bname: str,
    offer: Mapping[str, Any], proof: Mapping[str, Any],
) -> str:
    """A schema.org/Product JSON-LD <script> string. never-fabricate: price/rating are
    included ONLY when the caller supplied a parseable real value. Inert data, no JS.
    Escapes <, >, & so the payload is safe inside <script> and cannot break out."""
    if not name:
        return ""
    obj: Dict[str, Any] = {"@context": "https://schema.org", "@type": "Product", "name": name}
    if desc:
        obj["description"] = desc
    if img:
        obj["image"] = [img]
    if bname:
        obj["brand"] = {"@type": "Brand", "name": bname}

    price = _extract_price_number(_s(offer.get("price")))
    if price:
        obj["offers"] = {
            "@type": "Offer",
            "priceCurrency": "BRL",
            "price": price,
            "availability": "https://schema.org/InStock",
        }

    rating = _rating_number(_s(proof.get("rating")))
    if rating:
        agg: Dict[str, Any] = {"@type": "AggregateRating", "ratingValue": rating}
        count = _digits(_s(proof.get("count")))
        if count:
            agg["reviewCount"] = count
        obj["aggregateRating"] = agg

    payload = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    # Defuse any "</script>" or HTML-active chars inside string values.
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return '<script type="application/ld+json">%s</script>' % payload


def _extract_price_number(raw: str) -> str:
    """Parse a display price ('R$ 199,00', '1.299,90') into a schema number string
    ('199.00', '1299.90'). pt-BR aware. Unparseable -> "" (never fabricate a price)."""
    if not raw:
        return ""
    m = re.search(r"\d[\d.,]*", raw)
    if not m:
        return ""
    num = m.group(0)
    if "," in num:
        # pt-BR: '.' thousands, ',' decimal.
        num = num.replace(".", "").replace(",", ".")
    elif num.count(".") > 1:
        # 1.299 with multiple dots -> thousands separators only.
        num = num.replace(".", "")
    try:
        f = float(num)
    except ValueError:
        return ""
    return ("%.2f" % f) if "." in num else str(int(f))


def _rating_number(raw: str) -> str:
    """A 0-5 rating as a clean number string, else "" (never fabricate a rating)."""
    if not raw:
        return ""
    try:
        r = float(raw.replace(",", "."))
    except ValueError:
        return ""
    if r < 0 or r > 5:
        return ""
    return ("%.1f" % r) if r != int(r) else str(int(r))


def _digits(raw: str) -> str:
    """Just the digits of a value ('2.143' -> '2143'); "" when there are none."""
    d = "".join(ch for ch in raw if ch.isdigit())
    return d


# Structural, mobile-first CSS. References the brand vars with NEUTRAL fallbacks so an
# un-themed ad still looks intentional. Static constant -> no brace-escaping headaches.
_STRUCTURAL_CSS = (
    "*{box-sizing:border-box}"
    "html,body{margin:0;padding:0}"
    "body{background:hsl(var(--background,%(background)s));"
    "color:hsl(var(--foreground,%(foreground)s));"
    "font-family:var(--font-family-base,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,"
    "Helvetica,Arial,sans-serif);line-height:1.55;-webkit-font-smoothing:antialiased}"
    ".ad-doc{max-width:720px;margin:0 auto;padding:0 0 32px}"
    "section{padding:28px 20px;border-bottom:1px solid hsl(var(--border,%(border)s))}"
    "section:last-child{border-bottom:0}"
    "h1,h2,h3{margin:0 0 12px;line-height:1.2}"
    "h1{font-size:1.9rem;letter-spacing:-0.01em}"
    "h2{font-size:1.3rem}"
    "p{margin:0 0 12px}"
    "img{max-width:100%%;height:auto;display:block}"
    # brand header
    ".ad-brandbar{display:flex;align-items:center;gap:12px;padding:14px 20px;"
    "background:hsl(var(--brand,%(brand)s));color:hsl(var(--brand-foreground,%(brand-foreground)s));"
    "position:sticky;top:0;z-index:10}"
    ".ad-brandbar img{height:34px;max-width:160px;object-fit:contain;border-radius:6px}"
    ".ad-brandbar .ad-bname{font-size:1.15rem;font-weight:700;line-height:1.15}"
    ".ad-brandbar .ad-btag{display:block;font-size:.72rem;opacity:.85;margin-top:2px;font-weight:400}"
    # hero
    ".ad-hero{text-align:center}"
    ".ad-hero .ad-sub{font-size:1.05rem;color:hsl(var(--muted-foreground,%(muted-foreground)s));"
    "max-width:46ch;margin:0 auto 18px}"
    ".ad-hero .ad-media{margin:18px 0}"
    ".ad-discount-badge{display:inline-block;background:hsl(var(--highlight,%(highlight)s));"
    "color:hsl(var(--highlight-foreground,%(highlight-foreground)s));font-weight:700;"
    "font-size:.85rem;padding:5px 12px;border-radius:999px;margin-bottom:14px}"
    # CTA button (repeated)
    ".ad-cta{display:inline-block;width:100%%;max-width:360px;text-align:center;"
    "background:hsl(var(--primary,%(primary)s));color:hsl(var(--primary-foreground,%(primary-foreground)s));"
    "font-size:1.1rem;font-weight:700;text-decoration:none;padding:15px 26px;"
    "border-radius:var(--radius,%(radius)s);border:0;cursor:pointer;"
    "box-shadow:0 6px 18px -6px hsl(var(--primary,%(primary)s) / .55)}"
    ".ad-cta:hover{filter:brightness(1.06)}"
    ".ad-cta:focus-visible{outline:3px solid hsl(var(--ring,%(primary)s));outline-offset:3px}"
    ".ad-cta-sub{display:block;font-size:.8rem;color:hsl(var(--muted-foreground,%(muted-foreground)s));"
    "margin-top:8px}"
    # value cards
    ".ad-value-grid{display:grid;grid-template-columns:1fr;gap:14px;margin-top:6px}"
    ".ad-vcard{display:flex;gap:12px;align-items:flex-start;background:hsl(var(--card,%(card)s));"
    "border:1px solid hsl(var(--border,%(border)s));border-radius:var(--radius,%(radius)s);padding:14px 16px}"
    ".ad-vcard .ad-vchk{flex:0 0 auto;width:26px;height:26px;border-radius:999px;"
    "background:hsl(var(--brand,%(brand)s));color:hsl(var(--brand-foreground,%(brand-foreground)s));"
    "display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.9rem}"
    ".ad-vcard .ad-vbody{flex:1}"
    ".ad-vcard .ad-vtitle{font-weight:700;margin:0 0 3px}"
    ".ad-vcard p{margin:0;font-size:.92rem;color:hsl(var(--muted-foreground,%(muted-foreground)s))}"
    # proof
    ".ad-proof{text-align:center;background:hsl(var(--muted,%(card)s))}"
    ".ad-rating{font-size:1.6rem;font-weight:800;letter-spacing:.04em;"
    "color:hsl(var(--highlight-foreground,%(foreground)s))}"
    ".ad-stars{color:hsl(var(--highlight,%(highlight)s));font-size:1.3rem;letter-spacing:.1em}"
    ".ad-testi{display:grid;grid-template-columns:1fr;gap:12px;margin-top:16px;text-align:left}"
    ".ad-quote{background:hsl(var(--card,%(card)s));border-left:4px solid hsl(var(--brand,%(brand)s));"
    "border-radius:8px;padding:12px 14px}"
    ".ad-quote blockquote{margin:0 0 6px;font-style:italic}"
    ".ad-quote cite{font-size:.82rem;color:hsl(var(--muted-foreground,%(muted-foreground)s));font-style:normal}"
    # offer
    ".ad-offer{text-align:center;background:hsl(var(--secondary,%(secondary)s));"
    "color:hsl(var(--secondary-foreground,%(secondary-foreground)s))}"
    ".ad-offer h2{color:inherit}"
    ".ad-price{font-size:2.4rem;font-weight:800;line-height:1}"
    ".ad-price-old{font-size:1.1rem;text-decoration:line-through;opacity:.7;margin-left:8px;font-weight:500}"
    ".ad-install{font-size:.95rem;opacity:.9;margin-top:6px}"
    ".ad-offer-meta{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:16px 0}"
    ".ad-chip{font-size:.82rem;background:hsl(var(--card,%(card)s) / .15);border:1px solid currentColor;"
    "border-radius:999px;padding:5px 12px}"
    ".ad-urgency{font-weight:700;color:hsl(var(--highlight,%(highlight)s));margin-top:6px}"
    # specs
    ".ad-specs table{border-collapse:collapse;width:100%%;font-size:.92rem}"
    ".ad-specs td{padding:9px 10px;border-bottom:1px solid hsl(var(--border,%(border)s));vertical-align:top}"
    ".ad-specs td:first-child{font-weight:600;width:42%%;color:hsl(var(--muted-foreground,%(muted-foreground)s))}"
    # faq
    ".ad-faq details{border:1px solid hsl(var(--border,%(border)s));border-radius:var(--radius,%(radius)s);"
    "padding:2px 14px;margin-bottom:10px;background:hsl(var(--card,%(card)s))}"
    ".ad-faq summary{cursor:pointer;font-weight:600;padding:11px 0;list-style:revert}"
    ".ad-faq details p{margin:0 0 12px;font-size:.92rem;"
    "color:hsl(var(--muted-foreground,%(muted-foreground)s))}"
    # honest placeholders + empty media (never-fabricate markers)
    ".ad-ph{display:inline-block;color:hsl(var(--muted-foreground,%(muted-foreground)s));"
    "background:hsl(var(--muted,%(card)s));border:1px dashed hsl(var(--border,%(border)s));"
    "border-radius:6px;padding:1px 8px;font-style:italic;font-size:.92em}"
    ".ad-slot-empty{border:2px dashed hsl(var(--border,%(border)s));border-radius:var(--radius,%(radius)s);"
    "background:hsl(var(--muted,%(card)s));color:hsl(var(--muted-foreground,%(muted-foreground)s));"
    "text-align:center;padding:30px 18px;margin:0 auto}"
    ".ad-slot-empty strong{display:block;font-size:1rem;margin-bottom:4px}"
    ".ad-slot-empty span{font-size:.82rem}"
    ".ad-gallery{display:grid;grid-template-columns:1fr 1fr;gap:12px}"
    ".ad-gallery figure{margin:0}"
    ".ad-gallery img{border-radius:var(--radius,%(radius)s);border:1px solid hsl(var(--border,%(border)s))}"
    # footer
    ".ad-foot{font:12px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;"
    "color:hsl(var(--muted-foreground,%(muted-foreground)s));text-align:center}"
    ".ad-foot .ad-badge{display:inline-block;border-radius:6px;padding:2px 10px;color:#fff;"
    "margin-bottom:8px;font-size:.78rem}"
    ".ad-foot .ad-badge-real{background:#2e7d32}"
    ".ad-foot .ad-badge-sample{background:#b8860b}"
    ".ad-cta-wrap{margin-top:6px}"
    # responsive: roomier on >=560px
    "@media(min-width:560px){.ad-value-grid{grid-template-columns:1fr 1fr}"
    ".ad-testi{grid-template-columns:1fr 1fr}}"
) % _FALLBACK_CSS


# The DESIGN-SYSTEM layer: the reference retail PDP type scale (text-display/h1/h2/h3 with the premium
# negative tracking from design_system.md S3) + token utility classes + the @media print
# sheet. Static (no %()s interpolation -> literal % is safe). Applied via class names that
# MIRROR the design-system, so the same heading/text utilities render the ad like the PDP.
_DESIGN_SYSTEM_CSS = (
    # type scale (clamp values + tracking + weight straight from the design-system).
    ".text-display{font-size:clamp(2rem,5vw,4rem);line-height:1.2;"
    "letter-spacing:-0.025em;font-weight:800}"
    ".text-h1{font-size:clamp(1.75rem,4vw,3rem);line-height:1.2;"
    "letter-spacing:-0.025em;font-weight:700}"
    ".text-h2{font-size:clamp(1.5rem,3vw,2.25rem);line-height:1.2;"
    "letter-spacing:-0.025em;font-weight:600}"
    ".text-h3{font-size:clamp(1.25rem,2vw,1.75rem);line-height:1.5;font-weight:600}"
    ".text-eyebrow{font-size:.75rem;letter-spacing:.025em;text-transform:uppercase;"
    "font-weight:600;color:hsl(var(--brand))}"
    ".text-muted-foreground{color:hsl(var(--muted-foreground))}"
    ".text-lg{font-size:1.05rem;line-height:1.6}"
    # PDP "why it works" lead paragraph (mirrors the PDP intro prose).
    ".ad-why{max-width:60ch;margin:0 auto 18px;font-size:1.05rem;line-height:1.6;"
    "color:hsl(var(--muted-foreground))}"
    # RICHEN: the prose body (description + long_description) -- readable measure.
    ".ad-body p{max-width:62ch}"
    ".ad-body .ad-body-lead{font-weight:500;color:hsl(var(--foreground))}"
    # RICHEN: the key_features BULLETS (a dedicated, scannable list -- NOT the prose body).
    ".ad-feature-list{margin:6px 0 0;padding:0;list-style:none;display:grid;"
    "grid-template-columns:1fr;gap:10px}"
    ".ad-feature-list li{position:relative;padding-left:30px;line-height:1.5}"
    ".ad-feature-list li::before{content:'+';position:absolute;left:0;top:1px;width:21px;"
    "height:21px;border-radius:999px;background:hsl(var(--brand));"
    "color:hsl(var(--brand-foreground));display:flex;align-items:center;"
    "justify-content:center;font-weight:700;font-size:.8rem}"
    # RICHEN: the benefit-group sub-heading (benefits_functional vs _emotional).
    ".ad-bgroup-title{font-size:1rem;font-weight:700;margin:18px 0 10px;"
    "color:hsl(var(--foreground))}"
    "@media(min-width:560px){.ad-feature-list{grid-template-columns:1fr 1fr}}"
    # footer structure (token-driven; replaces the former bespoke inline styles).
    ".ad-foot-inner{border:0;padding-top:20px}"
    ".ad-foot-sources{margin-top:6px}"
    # @media print: a clean PDF -- hide the CTAs + empty upload slots + sticky bar, keep the
    # specs/copy, scale the imagery down, avoid splitting a section across pages.
    "@media print{"
    "body{background:#fff;color:#000}"
    ".ad-brandbar{position:static;box-shadow:none}"
    ".ad-cta,.ad-cta-wrap,.ad-cta-sub,.ad-slot-empty{display:none !important}"
    ".ad-discount-badge,.ad-urgency{color:#000}"
    "section{border-bottom:1px solid #ccc;break-inside:avoid;page-break-inside:avoid}"
    ".ad-hero .ad-media img,.ad-gallery img{max-width:55%;margin:0 auto}"
    ".ad-gallery{grid-template-columns:1fr 1fr}"
    "@page{margin:1.5cm}"
    "}"
)


# --------------------------------------------------------------------------- #
# 1. BRAND HEADER (BRAND -- always fills).
# --------------------------------------------------------------------------- #
def _section_brand_header(brand: Mapping[str, Any]) -> str:
    name = _s(brand.get("name"))
    tagline = _s(brand.get("tagline"))
    logo = _s(brand.get("logo"))
    logo_alt = _s(brand.get("logoAlt")) or name or "logo"

    inner: List[str] = []
    if logo and _is_safe_media_src(logo):
        inner.append('<img src="%s" alt="%s">' % (_esc(logo), _esc(logo_alt[:80])))
    if name:
        tag = ('<span class="ad-btag">%s</span>' % _esc(tagline)) if tagline else ""
        inner.append('<div><span class="ad-bname">%s</span>%s</div>' % (_esc(name), tag))
    if not inner:
        # BRAND unknown -> an honest, editable brand placeholder (degrade-never).
        inner.append('<div><span class="ad-bname">%s</span></div>' % _ph("nome da marca"))
    return '<header class="ad-brandbar" role="banner">%s</header>' % "".join(inner)


# --------------------------------------------------------------------------- #
# 2. HERO (COPY + MEDIA + primary CTA).
# --------------------------------------------------------------------------- #
def _section_hero(
    brand: Mapping[str, Any],
    product: Mapping[str, Any],
    copy: Mapping[str, Any],
    media: Mapping[str, Any],
    offer: Mapping[str, Any],
) -> str:
    headline = _s(copy.get("headline")) or _s(product.get("name"))
    headline_html = _esc(headline) if headline else _ph("headline do anuncio")
    sub = _s(copy.get("subheadline"))
    sub_html = _esc(sub) if sub else _ph("subheadline -- a promessa principal")

    # Optional eyebrow: the canonical product title (the SEO/listing name), shown small
    # above the marketing headline when it is a distinct, real value (never fabricated).
    title = _s(copy.get("title")) or _s(product.get("name"))
    eyebrow = ('<div class="text-eyebrow">%s</div>' % _esc(title)) if (title and title != headline) else ""

    discount = _s(offer.get("discount"))
    badge = ('<div class="ad-discount-badge">%s</div>' % _esc(discount)) if discount else ""

    hero_media = _media_slot(media.get("hero"), "hero", "image", "Imagem principal do produto")

    cta = _cta_button(copy, offer, slot="hero")

    return (
        '<section class="ad-hero">'
        + badge
        + eyebrow
        + '<h1 class="text-display">' + headline_html + "</h1>"
        + '<p class="ad-sub text-lg">' + sub_html + "</p>"
        + '<div class="ad-media">' + hero_media + "</div>"
        + '<div class="ad-cta-wrap">' + cta + "</div>"
        + "</section>"
    )


# --------------------------------------------------------------------------- #
# 3. GALLERY (MEDIA).
# --------------------------------------------------------------------------- #
def _section_gallery(media: Mapping[str, Any]) -> str:
    gallery = media.get("gallery")
    items: List[str] = []
    if isinstance(gallery, (list, tuple)) and gallery:
        for i, g in enumerate(gallery):
            items.append(
                "<figure>%s</figure>"
                % _media_slot(g, "gallery_%d" % (i + 1), "image", "Foto %d do produto" % (i + 1))
            )
    else:
        # No gallery declared -> ONE honest empty upload slot (never a fabricated image).
        items.append(
            "<figure>%s</figure>"
            % _media_slot(None, "gallery_1", "image", "Foto do produto")
        )
    return (
        '<section class="ad-gallery-sec">'
        '<h2 class="text-h2">Galeria</h2>'
        '<div class="ad-gallery">' + "".join(items) + "</div>"
        "</section>"
    )


# --------------------------------------------------------------------------- #
# 4. BODY (COPY -- the PROSE description. THE LOAD-BEARING SEAM: prose ONLY here;
#    bullets live in section 5, the ficha in section 9 -- never folded into this body).
# --------------------------------------------------------------------------- #
def _section_body(copy: Mapping[str, Any]) -> str:
    desc = _s(copy.get("description"))
    long_desc = _s(copy.get("long_description"))
    paras: List[str] = []
    if desc:
        paras.append('<p class="ad-body-lead text-lg">%s</p>' % _esc(desc))
    if long_desc:
        paras.append("<p>%s</p>" % _esc(long_desc))
    if not paras:
        # Honest editable placeholder -- the founder/pipeline fills the real prose.
        paras.append('<p>%s</p>' % _ph("descricao do produto"))
    return (
        '<section class="ad-body">'
        '<h2 class="text-h2">Sobre o produto</h2>'
        + "".join(paras)
        + "</section>"
    )


# --------------------------------------------------------------------------- #
# 5. FEATURES (COPY -- key_features[] BULLETS. A DEDICATED section, SEPARATE from the
#    prose body: the load-bearing rule -- bullets are stored/rendered apart from prose).
# --------------------------------------------------------------------------- #
def _section_features(copy: Mapping[str, Any]) -> str:
    feats = _normalize_bullets(copy.get("key_features"))
    items: List[str] = []
    if feats:
        for f in feats:
            items.append("<li>%s</li>" % _esc(f))
    else:
        # Honest editable placeholders -- never a fabricated feature.
        for n in range(1, 4):
            items.append("<li>%s</li>" % _ph("caracteristica %d" % n))
    return (
        '<section class="ad-features">'
        '<h2 class="text-h2">Caracteristicas principais</h2>'
        '<ul class="ad-feature-list">' + "".join(items) + "</ul>"
        "</section>"
    )


# --------------------------------------------------------------------------- #
# 6. VALUE (COPY -- benefit-led; benefits_functional[] + benefits_emotional[] render as
#    two DISTINCT groups. A flat `benefits[]` (legacy / ads-path) still renders too).
# --------------------------------------------------------------------------- #
def _section_value(copy: Mapping[str, Any]) -> str:
    func = _normalize_benefits(copy.get("benefits_functional"))
    emo = _normalize_benefits(copy.get("benefits_emotional"))
    flat = _normalize_benefits(copy.get("benefits"))

    groups: List[str] = []
    if func:
        groups.append(_benefit_group("O que entrega", func))
    if emo:
        groups.append(_benefit_group("Por que voce vai amar", emo))
    if flat:
        # legacy / ads-path flat list (no group label) -- still a real benefit grid.
        groups.append('<div class="ad-value-grid">' + _benefit_cards_html(flat) + "</div>")
    if not (func or emo or flat):
        # Honest editable placeholders -- the founder fills the real benefits.
        ph = "".join(
            '<div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span>'
            '<div class="ad-vbody"><div class="ad-vtitle">%s</div></div></div>'
            % _ph("beneficio %d" % n)
            for n in range(1, 4)
        )
        groups.append('<div class="ad-value-grid">' + ph + "</div>")

    # PDP parity: an optional "why it works" lead (the PDP's "Por que funciona" prose).
    why = _s(copy.get("why")) or _s(copy.get("why_it_works"))
    why_html = ('<p class="ad-why">%s</p>' % _esc(why)) if why else ""
    return (
        '<section class="ad-value">'
        '<h2 class="text-h2">Por que escolher</h2>'
        + why_html
        + "".join(groups)
        + "</section>"
    )


def _benefit_group(label: str, norm: Sequence["tuple[str, str]"]) -> str:
    """A labeled benefit group (a sub-heading + the benefit-card grid). PURE."""
    return (
        '<h3 class="ad-bgroup-title">%s</h3>'
        '<div class="ad-value-grid">%s</div>'
        % (_esc(label), _benefit_cards_html(norm))
    )


def _benefit_cards_html(norm: Sequence["tuple[str, str]"]) -> str:
    """Render normalized (title, body) benefits as the shared value-card grid. PURE."""
    cards: List[str] = []
    for title, body in norm:
        t_html = ('<div class="ad-vtitle">%s</div>' % _esc(title)) if title else ""
        b_html = ("<p>%s</p>" % _esc(body)) if body else ""
        cards.append(
            '<div class="ad-vcard"><span class="ad-vchk" aria-hidden="true">+</span>'
            '<div class="ad-vbody">' + t_html + b_html + "</div></div>"
        )
    return "".join(cards)


# --------------------------------------------------------------------------- #
# 7. PROOF (DATA/COPY -- social proof; NEVER a fabricated rating).
# --------------------------------------------------------------------------- #
def _section_proof(proof: Mapping[str, Any]) -> str:
    rating = _s(proof.get("rating"))
    count = _s(proof.get("count"))
    testimonials = _normalize_testimonials(proof.get("testimonials"))

    head_bits: List[str] = []
    if rating:
        stars = _stars_for(rating)
        head_bits.append('<div class="ad-stars" aria-hidden="true">%s</div>' % stars)
        sub = rating + ((" de 5  -  " + count + " avaliacoes") if count else " de 5")
        head_bits.append('<div class="ad-rating">%s</div>' % _esc(sub))
    else:
        head_bits.append('<div class="ad-rating">%s</div>' % _ph("nota media + n de avaliacoes"))

    testi_html = ""
    if testimonials:
        rows = []
        for quote, author in testimonials:
            cite = ("<cite>-- %s</cite>" % _esc(author)) if author else ""
            rows.append(
                '<div class="ad-quote"><blockquote>%s</blockquote>%s</div>'
                % (_esc(quote), cite)
            )
        testi_html = '<div class="ad-testi">' + "".join(rows) + "</div>"
    elif not rating:
        # only show a testimonial placeholder when proof is fully empty (avoid noise).
        testi_html = (
            '<div class="ad-testi"><div class="ad-quote"><blockquote>%s</blockquote></div></div>'
            % _ph("depoimento real de cliente")
        )

    return (
        '<section class="ad-proof">'
        '<h2 class="text-h2">Quem comprou aprova</h2>'
        + "".join(head_bits)
        + testi_html
        + "</section>"
    )


# --------------------------------------------------------------------------- #
# 8. OFFER (DATA -- price/urgency/guarantee; NEVER a fabricated price).
# --------------------------------------------------------------------------- #
def _section_offer(offer: Mapping[str, Any], copy: Mapping[str, Any]) -> str:
    price = _s(offer.get("price"))
    original = _s(offer.get("original_price"))
    installments = _s(offer.get("installments"))
    urgency = _s(offer.get("urgency"))
    guarantee = _s(offer.get("guarantee"))
    shipping = _s(offer.get("shipping"))

    if price:
        old = ('<span class="ad-price-old">%s</span>' % _esc(original)) if original else ""
        price_html = '<div class="ad-price">%s%s</div>' % (_esc(price), old)
    else:
        price_html = '<div class="ad-price">%s</div>' % _ph("preco")
    install_html = ('<div class="ad-install">%s</div>' % _esc(installments)) if installments else ""

    chips: List[str] = []
    if shipping:
        chips.append('<span class="ad-chip">%s</span>' % _esc(shipping))
    if guarantee:
        chips.append('<span class="ad-chip">%s</span>' % _esc(guarantee))
    if not chips:
        chips.append('<span class="ad-chip">%s</span>' % _ph("frete / garantia"))
    chips_html = '<div class="ad-offer-meta">' + "".join(chips) + "</div>"

    urgency_html = ('<div class="ad-urgency">%s</div>' % _esc(urgency)) if urgency else ""

    cta = _cta_button(copy, offer, slot="offer")

    return (
        '<section class="ad-offer">'
        '<h2 class="text-h2">A oferta</h2>'
        + price_html
        + install_html
        + chips_html
        + urgency_html
        + '<div class="ad-cta-wrap">' + cta + "</div>"
        + "</section>"
    )


# --------------------------------------------------------------------------- #
# 9. SPECS / FICHA (DATA -- the frozen facts table. THE LOAD-BEARING SEAM: the ficha
#    (numeric dims, weight, materials[], colors[], identity codes, the attributes
#    long-tail) renders here as its OWN structured section -- NEVER folded into the
#    prose body. The legacy flat `specs[]` still appends below the ficha rows).
# --------------------------------------------------------------------------- #
def _section_specs(specs: Any, product: Mapping[str, Any], ficha: Any = None) -> str:
    rows = _ficha_rows(ficha, product)
    rows.extend(_normalize_specs(specs))  # legacy flat specs append after the ficha
    if rows:
        body = "".join(
            "<tr><td>%s</td><td>%s</td></tr>" % (_esc(label), _esc(value))
            for label, value in rows
        )
    else:
        body = (
            "<tr><td>%s</td><td>%s</td></tr>"
            % (_ph("caracteristica"), _ph("valor"))
        )
    return (
        '<section class="ad-specs">'
        '<h2 class="text-h2">Especificacoes</h2>'
        "<table><tbody>" + body + "</tbody></table>"
        "</section>"
    )


def _ficha_rows(ficha: Any, product: Mapping[str, Any]) -> List["tuple[str, str]"]:
    """Build the ficha (frozen-facts) rows: dimensions, weight, materials, colors, the
    identity codes, then the attributes long-tail. Each row appears ONLY when its value
    is real (never-fabricate). Numeric dims/weight render via the shared formatters so a
    structured {largura,...}/{value,grams} OR a pre-formatted string both work. PURE."""
    f = _as_map(ficha)
    prod = _as_map(product)
    rows: List["tuple[str, str]"] = []

    dims = _fmt_dimensions(f.get("dimensions"))
    if dims:
        rows.append(("Dimensoes", dims))
    weight = _fmt_weight(f.get("weight"))
    if weight:
        rows.append(("Peso", weight))
    materials = _join_list(f.get("materials"))
    if materials:
        rows.append(("Materiais", materials))
    colors = _join_list(f.get("colors"))
    if colors:
        rows.append(("Cores", colors))

    # Identity codes -- ficha.identity first, then the product block (surfaced where real).
    identity = _as_map(f.get("identity"))
    for label, key in (("Marca", "brand"), ("Modelo", "model"), ("SKU", "sku"),
                       ("GTIN", "gtin"), ("EAN", "ean"), ("MPN", "mpn")):
        v = _s(identity.get(key)) or _s(prod.get(key))
        if v:
            rows.append((label, v))

    # The attributes long-tail (the per-category channel-required tail).
    rows.extend(_normalize_attributes(f.get("attributes")))
    return rows


# --------------------------------------------------------------------------- #
# 10. FAQ (COPY -- native details/summary accordion for a11y).
# --------------------------------------------------------------------------- #
def _section_faq(copy: Mapping[str, Any]) -> str:
    faq = _normalize_faq(copy.get("faq"))
    items: List[str] = []
    if faq:
        for q, a in faq:
            a_html = ("<p>%s</p>" % _esc(a)) if a else "<p>%s</p>" % _ph("resposta")
            items.append("<details><summary>%s</summary>%s</details>" % (_esc(q), a_html))
    else:
        for n in range(1, 3):
            items.append(
                "<details><summary>%s</summary><p>%s</p></details>"
                % (_ph("pergunta %d" % n), _ph("resposta %d" % n))
            )
    return (
        '<section class="ad-faq">'
        '<h2 class="text-h2">Perguntas frequentes</h2>'
        + "".join(items)
        + "</section>"
    )


# --------------------------------------------------------------------------- #
# 11. CTA2 (the repeated call to action -- conversion requirement).
# --------------------------------------------------------------------------- #
def _section_cta2(copy: Mapping[str, Any], offer: Mapping[str, Any]) -> str:
    urgency = _s(offer.get("urgency"))
    urgency_html = ('<div class="ad-urgency">%s</div>' % _esc(urgency)) if urgency else ""
    cta = _cta_button(copy, offer, slot="cta2")
    return (
        '<section class="ad-hero ad-cta2">'
        '<h2 class="text-h2">Pronto para comecar?</h2>'
        + urgency_html
        + '<div class="ad-cta-wrap">' + cta + "</div>"
        + "</section>"
    )


# --------------------------------------------------------------------------- #
# 12. FOOTER (provenance / trust -- honest real vs sample + sources + timestamp).
# --------------------------------------------------------------------------- #
def _section_footer(brand: Mapping[str, Any], meta: Mapping[str, Any]) -> str:
    real = bool(meta.get("real", False))
    created = _s(meta.get("created"))
    sources = meta.get("sources")
    domain = _s(brand.get("domain"))
    name = _s(brand.get("name"))

    if real:
        badge = '<span class="ad-badge ad-badge-real">resultado real</span>'
    else:
        badge = '<span class="ad-badge ad-badge-sample">amostra -- dados simulados</span>'

    bits: List[str] = [badge, "<br>"]
    owner = name or domain
    if owner:
        bits.append("Anuncio de " + _esc(owner) + " - ")
    bits.append("CEXAI product_ad mold")
    if created:
        bits.append(" | gerado " + _esc(created[:19].replace("T", " ")))

    src_html = ""
    src_list = [s for s in (sources or []) if _s(s)] if isinstance(sources, (list, tuple)) else []
    if src_list:
        src_html = (
            '<div class="ad-foot-sources">Fontes: '
            + _esc("; ".join(_s(s) for s in src_list))
            + "</div>"
        )
    elif not real:
        src_html = (
            '<div class="ad-foot-sources">Fontes: %s</div>'
            % _ph("citar fontes das afirmacoes antes de publicar")
        )

    return (
        '<footer class="ad-foot" role="contentinfo">'
        '<section class="ad-foot-inner">'
        + "".join(bits)
        + src_html
        + "</section></footer>"
    )


# --------------------------------------------------------------------------- #
# CTA button (shared by hero / offer / cta2 -- the repeated CTA).
# --------------------------------------------------------------------------- #
def _cta_button(copy: Mapping[str, Any], offer: Mapping[str, Any], *, slot: str) -> str:
    label = _s(copy.get("cta_label")) or _DEFAULT_CTA
    sub = _s(copy.get("cta_sub")) or _s(offer.get("guarantee"))
    sub_html = ('<span class="ad-cta-sub">%s</span>' % _esc(sub)) if sub else ""
    return (
        '<a class="ad-cta" href="#comprar" role="button" data-cta-slot="%s">%s</a>%s'
        % (_esc(slot), _esc(label), sub_html)
    )


# --------------------------------------------------------------------------- #
# Media slot: a safe real <img> when produced, else an upload-fallback dropzone.
# Mirrors the cex_dual_output data-slot-key affordance. NEVER a broken/fabricated ref.
# --------------------------------------------------------------------------- #
def _media_slot(produced: Any, key: str, kind: str, label: str) -> str:
    src, alt = _media_src_alt(produced)
    data_attrs = (
        'data-slot-key="%s" data-kind="%s" data-editable="true" data-upload-fallback="true"'
        % (_esc(key), _esc(kind))
    )
    if src and _is_safe_media_src(src):
        a = _esc(alt or label)
        return '<img src="%s" alt="%s" %s>' % (_esc(src), a, data_attrs)
    # EMPTY -> editable upload dropzone (no src, no broken <img>).
    prompt = {"image": "Enviar imagem", "video": "Enviar video", "audio": "Enviar audio"}.get(
        kind, "Enviar midia"
    )
    return (
        '<div class="ad-slot-empty" %s><strong>[ + ] %s</strong>'
        '<span>slot vazio (%s) -- faca upload ou edite</span></div>'
        % (data_attrs, _esc(prompt), _esc(label))
    )


def _media_src_alt(produced: Any) -> "tuple[Optional[str], Optional[str]]":
    """Extract (src, alt) from a produced media entry: a bare src str OR {src, alt?}.
    A blank/whitespace src is treated as ABSENT (the slot stays empty). PURE + TOTAL."""
    if isinstance(produced, str):
        s = produced.strip()
        return (s, None) if s else (None, None)
    if isinstance(produced, Mapping):
        s = _s(produced.get("src"))
        a = _s(produced.get("alt")) or None
        return (s, a) if s else (None, None)
    return (None, None)


def _is_safe_media_src(src: str) -> bool:
    """True when a media src is safe to embed: https: or data:image|video|audio only.
    Mirrors brandTheme.ts isSafeLogoSrc (broadened to the AV kinds). Blocks
    javascript:/http:/file: etc. -- never embeds a hostile or insecure ref. TOTAL."""
    s = (src or "").strip().lower()
    if s.startswith("https://"):
        return True
    if s.startswith("data:image/") or s.startswith("data:video/") or s.startswith("data:audio/"):
        return True
    return False


# --------------------------------------------------------------------------- #
# Normalizers (PURE + TOTAL -- coerce loose caller shapes; never raise).
# --------------------------------------------------------------------------- #
def _normalize_benefits(benefits: Any) -> List["tuple[str, str]"]:
    """A benefit is a str (title only) OR {title, body} / {title, desc}. Drop blanks."""
    out: List["tuple[str, str]"] = []
    if not isinstance(benefits, (list, tuple)):
        return out
    for b in benefits:
        if isinstance(b, str):
            t = b.strip()
            if t:
                out.append((t, ""))
        elif isinstance(b, Mapping):
            t = _s(b.get("title")) or _s(b.get("label"))
            body = _s(b.get("body")) or _s(b.get("desc")) or _s(b.get("description"))
            if t or body:
                out.append((t, body))
    return out


def _normalize_testimonials(testimonials: Any) -> List["tuple[str, str]"]:
    """A testimonial is {quote, author?} / {text, author?} / a bare str. Drop blanks."""
    out: List["tuple[str, str]"] = []
    if not isinstance(testimonials, (list, tuple)):
        return out
    for t in testimonials:
        if isinstance(t, str):
            q = t.strip()
            if q:
                out.append((q, ""))
        elif isinstance(t, Mapping):
            q = _s(t.get("quote")) or _s(t.get("text")) or _s(t.get("body"))
            a = _s(t.get("author")) or _s(t.get("name"))
            if q:
                out.append((q, a))
    return out


def _normalize_specs(specs: Any) -> List["tuple[str, str]"]:
    """A spec is {label, value} / {name, value} / a [label, value] pair. Drop blanks."""
    out: List["tuple[str, str]"] = []
    if not isinstance(specs, (list, tuple)):
        return out
    for s in specs:
        if isinstance(s, Mapping):
            label = _s(s.get("label")) or _s(s.get("name")) or _s(s.get("key"))
            value = _s(s.get("value")) or _s(s.get("val"))
            if label or value:
                out.append((label, value))
        elif isinstance(s, (list, tuple)) and len(s) >= 2:
            label, value = _s(s[0]), _s(s[1])
            if label or value:
                out.append((label, value))
    return out


def _normalize_faq(faq: Any) -> List["tuple[str, str]"]:
    """A FAQ item is {q, a} / {question, answer} / a [q, a] pair. Drop blank questions."""
    out: List["tuple[str, str]"] = []
    if not isinstance(faq, (list, tuple)):
        return out
    for f in faq:
        if isinstance(f, Mapping):
            q = _s(f.get("q")) or _s(f.get("question"))
            a = _s(f.get("a")) or _s(f.get("answer"))
            if q:
                out.append((q, a))
        elif isinstance(f, (list, tuple)) and len(f) >= 2:
            q, a = _s(f[0]), _s(f[1])
            if q:
                out.append((q, a))
    return out


def _normalize_bullets(bullets: Any) -> List[str]:
    """key_features[] -> a clean list of bullet strings. A bullet is a str OR a
    {title, body}/{label,value} dict (rendered 'title: body'). Drops blanks. PURE + TOTAL."""
    out: List[str] = []
    if not isinstance(bullets, (list, tuple)):
        return out
    for b in bullets:
        if isinstance(b, str):
            s = b.strip()
            if s:
                out.append(s)
        elif isinstance(b, Mapping):
            t = _s(b.get("title")) or _s(b.get("label")) or _s(b.get("name"))
            body = _s(b.get("body")) or _s(b.get("desc")) or _s(b.get("value"))
            if t and body:
                out.append(t + ": " + body)
            elif t or body:
                out.append(t or body)
    return out


def _normalize_attributes(attrs: Any) -> List["tuple[str, str]"]:
    """The attributes long-tail -> (label, value) rows. Accepts a {k: v} mapping OR a
    list of {label,value}/{name,value}/[label,value]. Drops blanks. PURE + TOTAL."""
    out: List["tuple[str, str]"] = []
    if isinstance(attrs, Mapping):
        for k, v in attrs.items():
            label, value = _s(k), _s(v)
            if label and value:
                out.append((label, value))
    elif isinstance(attrs, (list, tuple)):
        for a in attrs:
            if isinstance(a, Mapping):
                label = _s(a.get("label")) or _s(a.get("name")) or _s(a.get("key"))
                value = _s(a.get("value")) or _s(a.get("val"))
                if label or value:
                    out.append((label, value))
            elif isinstance(a, (list, tuple)) and len(a) >= 2:
                label, value = _s(a[0]), _s(a[1])
                if label or value:
                    out.append((label, value))
    return out


def _join_list(v: Any) -> str:
    """A list-ish ficha field (materials/colors) -> a comma-joined string. A bare string
    passes through. Drops blanks. PURE + TOTAL."""
    if isinstance(v, str):
        return _s(v)
    if isinstance(v, (list, tuple)):
        return ", ".join(_s(x) for x in v if _s(x))
    return ""


def _stars_for(rating: str) -> str:
    """A 0-5 star bar (filled/empty) from a numeric-ish rating. TOTAL: bad input -> empty bar."""
    try:
        r = float(str(rating).replace(",", "."))
    except (TypeError, ValueError):
        return "-----"
    r = max(0.0, min(5.0, r))
    full = int(round(r))
    return ("*" * full) + ("-" * (5 - full))


# --------------------------------------------------------------------------- #
# Numeric / display formatters for the ficha + the schema mapper (PURE + TOTAL).
# These DISPLAY-FORMAT real values supplied by the caller -- they never invent one.
# --------------------------------------------------------------------------- #
def _num(v: Any) -> str:
    """A number -> a clean pt-BR display string: 40.0 -> '40', 6.5 -> '6,5'. TOTAL."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return ""
    if f == int(f):
        return str(int(f))
    s = ("%.3f" % f).rstrip("0").rstrip(".")
    return s.replace(".", ",")


def _fmt_dimensions(dims: Any) -> str:
    """Format dimensions for the ficha. Accepts a pre-formatted string (passed through)
    OR the canonical structured object {largura, altura, profundidade, unit} ->
    'L x A x P unit' (e.g. '7 x 26 x 7 cm'). Missing numbers are skipped; an empty set
    -> '' (the row is then omitted upstream). NEVER fabricates a measurement. PURE + TOTAL."""
    if isinstance(dims, str):
        return _s(dims)
    if not isinstance(dims, Mapping):
        return ""
    parts = [
        _num(dims.get(k))
        for k in ("largura", "altura", "profundidade")
        if isinstance(dims.get(k), (int, float))
    ]
    parts = [p for p in parts if p]
    if not parts:
        return ""
    unit = _s(dims.get("unit")) or "cm"
    return " x ".join(parts) + " " + unit


def _fmt_weight(weight: Any) -> str:
    """Format weight for the ficha. Accepts a pre-formatted string (passed through) OR the
    canonical structured object {value, unit, grams} -> 'value unit' (e.g. '320 g',
    '1,5 kg'), falling back to '<grams> g'. NEVER fabricates a weight. PURE + TOTAL."""
    if isinstance(weight, str):
        return _s(weight)
    if not isinstance(weight, Mapping):
        return ""
    value = weight.get("value")
    unit = _s(weight.get("unit"))
    if isinstance(value, (int, float)) and unit:
        return _num(value) + " " + unit
    grams = weight.get("grams")
    if isinstance(grams, (int, float)):
        return _num(grams) + " g"
    if isinstance(value, (int, float)):
        return _num(value)
    return ""


def _fmt_price_brl(value: Any) -> str:
    """A numeric price -> a pt-BR display string 'R$ 1.299,90' (dot thousands, comma
    decimal). A non-numeric / negative value -> '' (the offer then shows a placeholder --
    never a fabricated price). PURE + TOTAL."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return ""
    if f < 0:
        return ""
    intpart, dec = ("%.2f" % f).split(".")
    rev = intpart[::-1]
    grouped = ".".join(rev[i:i + 3] for i in range(0, len(rev), 3))[::-1]
    return "R$ %s,%s" % (grouped, dec)


# --------------------------------------------------------------------------- #
# Small coercion helpers (PURE + TOTAL).
# --------------------------------------------------------------------------- #
def _as_map(v: Any) -> Mapping[str, Any]:
    return v if isinstance(v, Mapping) else {}


def _s(v: Any) -> str:
    """A trimmed string for a scalar value. None/empty -> "". Collapses inner whitespace."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "Sim" if v else "Nao"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return " ".join(str(v).split())


def _esc(v: Any) -> str:
    """HTML-escape a value (quotes included). TOTAL."""
    return _html_escape(_s(v), quote=True)


def _ph(field: str) -> str:
    """An honest, editable '[preencher: <field>]' placeholder span. NEVER a claim."""
    return '<span class="ad-ph">%s%s%s</span>' % (_PH_OPEN, _esc(field), _PH_CLOSE)


def _doc_title(
    brand: Mapping[str, Any], product: Mapping[str, Any], copy: Mapping[str, Any]
) -> str:
    name = _s(product.get("name")) or _s(copy.get("headline")) or "Anuncio"
    bname = _s(brand.get("name"))
    return (name + " | " + bname) if bname else name


# --------------------------------------------------------------------------- #
# THE schema mapper: a canonical product record -> the rich emit_product_ad data.
# --------------------------------------------------------------------------- #
def _strlist(v: Any) -> List[str]:
    """A list-ish field -> a clean list[str]. A bare string -> a 1-item list. PURE + TOTAL."""
    if isinstance(v, str):
        s = v.strip()
        return [s] if s else []
    if isinstance(v, (list, tuple)):
        return [_s(x) for x in v if _s(x)]
    return []


def ad_data_from_product(
    product: Optional[Mapping[str, Any]] = None,
    *,
    brand: Optional[Mapping[str, Any]] = None,
    real: bool = False,
) -> Dict[str, Any]:
    """Map a CANONICAL product record into the emit_product_ad ``data`` dict (the FULL rich
    ad). The record is the docs/schema/product_catalog_schema.yaml shape -- e.g. the output
    of cex_product_catalog_adapter.normalize_product (slug/name/tagline/price/images/
    description/long_description/why_it_works/features/benefits_functional/_emotional/faq/
    materials/colors/dimensions/weight/seo/identity-codes/_provenance).

    THE LOAD-BEARING SEAM is preserved by construction: the canonical `features[]` ->
    copy.key_features (the BULLETS section), `description`/`long_description` -> the PROSE
    body, and the frozen facts (dimensions/weight/materials/colors/identity/attributes) ->
    the `ficha` -- the three are mapped to SEPARATE keys and never concatenated.

    degrade-never: a field absent in the record is simply OMITTED (the mold then renders an
    honest placeholder); a value is NEVER fabricated. A numeric price is display-formatted
    (a real value, not invented). `real` defaults False -> the honest 'amostra' footer until
    a human approves the ad; pass real=True only for an approved, sourced ad. An optional
    `brand` dict (the mold's {name,tagline,tokens{24},...} shape) themes the ad.

    PURE + TOTAL: never raises; a non-mapping product -> a minimal all-placeholder data."""
    p = _as_map(product)

    # --- identity / product block (surfaced where real) ---
    name = _s(p.get("name"))
    product_block: Dict[str, Any] = {}
    if name:
        product_block["name"] = name
    for key in ("category", "brand", "model", "sku", "gtin", "ean", "mpn"):
        v = _s(p.get(key))
        if v:
            product_block[key] = v

    # --- copy block (the full canonical copy set) ---
    copy: Dict[str, Any] = {}
    if name:
        copy["title"] = name  # the canonical listing title (hero eyebrow + SEO)
    seo = _as_map(p.get("seo"))
    seo_title = _s(seo.get("title"))
    if seo_title:
        copy["seo_title"] = seo_title
    seo_desc = _s(seo.get("description"))
    if seo_desc:
        copy["seo_description"] = seo_desc
    # hero: the tagline is the marketing hook; the seo_description is the sub-promise.
    headline = _s(p.get("tagline")) or name
    if headline:
        copy["headline"] = headline
    if seo_desc:
        copy["subheadline"] = seo_desc
    # PROSE body (THE SEAM -- prose only; bullets/ficha live elsewhere).
    for src in ("description", "long_description", "why_it_works"):
        v = _s(p.get(src))
        if v:
            copy[src] = v
    # BULLETS (THE SEAM -- the canonical features[] -> the dedicated key_features section).
    feats = _strlist(p.get("features"))
    if feats:
        copy["key_features"] = feats
    # benefit groups (two distinct lists).
    func = _strlist(p.get("benefits_functional"))
    if func:
        copy["benefits_functional"] = func
    emo = _strlist(p.get("benefits_emotional"))
    if emo:
        copy["benefits_emotional"] = emo
    faq = _normalize_faq(p.get("faq"))
    if faq:
        copy["faq"] = [{"question": q, "answer": a} for q, a in faq]

    # --- media: images[0] -> hero, the rest -> gallery (the mold validates src safety) ---
    media: Dict[str, Any] = {}
    images = _strlist(p.get("images"))
    if images:
        media["hero"] = images[0]
        if len(images) > 1:
            media["gallery"] = images[1:7]

    # --- offer (real values only; price display-formatted, NEVER fabricated) ---
    offer: Dict[str, Any] = {}
    price = _fmt_price_brl(p.get("price"))
    if price:
        offer["price"] = price
    warranty = _s(p.get("warranty"))
    if warranty:
        offer["guarantee"] = warranty
    shipping = _s(p.get("shipping_info"))
    if shipping:
        offer["shipping"] = shipping

    # --- ficha (THE SEAM -- the frozen facts as their own structured section) ---
    ficha: Dict[str, Any] = {}
    if p.get("dimensions"):
        ficha["dimensions"] = p.get("dimensions")
    if p.get("weight"):
        ficha["weight"] = p.get("weight")
    materials = _strlist(p.get("materials"))
    if materials:
        ficha["materials"] = materials
    colors = _strlist(p.get("colors"))
    if colors:
        ficha["colors"] = colors
    identity: Dict[str, Any] = {}
    for key in ("gtin", "ean", "mpn", "sku", "brand", "model"):
        v = _s(p.get(key))
        if v:
            identity[key] = v
    if identity:
        ficha["identity"] = identity
    attrs = p.get("attributes")
    if attrs:
        ficha["attributes"] = attrs

    # --- meta (provenance; honest 'amostra' until approved) ---
    meta: Dict[str, Any] = {"real": bool(real)}
    prov = _as_map(p.get("_provenance"))
    src = _s(prov.get("source"))
    if src:
        meta["sources"] = ["catalogo: " + src]

    data: Dict[str, Any] = {
        "product": product_block,
        "copy": copy,
        "media": media,
        "offer": offer,
        "ficha": ficha,
        "meta": meta,
    }
    if isinstance(brand, Mapping) and brand:
        data["brand"] = dict(brand)
    return data


# --------------------------------------------------------------------------- #
# Demo data (ASCII source; PT-BR copy here is unaccented per the ASCII-code rule --
# a real caller passes fully accented runtime strings and they render verbatim).
# --------------------------------------------------------------------------- #
def _branded_demo_brand() -> Dict[str, Any]:
    """A DISTINCT, fully synthetic demo brand (Estrela Pet -- not any real tenant) -- a full,
    valid 24-token set in a violet/amber palette. Deliberately far from the default demo's
    teal so `--demo branded` makes the design-system adoption obvious: swap THIS one token
    block and the whole ad reskins."""
    return {
        "name": "Estrela Pet (exemplo)",
        "tagline": "Conforto premium para o seu pet",
        "logoAlt": "Estrela Pet (exemplo)",
        "domain": "estrelapet-exemplo.com.br",
        "fontFamily": "Poppins, -apple-system, Segoe UI, sans-serif",
        "tokens": {
            "background": "0 0% 100%", "foreground": "263 40% 12%",
            "card": "0 0% 99%", "cardForeground": "263 40% 12%",
            "popover": "0 0% 100%", "popoverForeground": "263 40% 12%",
            "primary": "263 70% 50%", "primaryForeground": "0 0% 100%",
            "secondary": "263 30% 20%", "secondaryForeground": "0 0% 100%",
            "muted": "264 24% 96%", "mutedForeground": "263 14% 42%",
            "accent": "322 75% 52%", "accentForeground": "0 0% 100%",
            "border": "264 22% 88%", "input": "264 22% 88%", "ring": "263 70% 50%",
            "brand": "263 70% 50%", "brandForeground": "0 0% 100%", "brandMuted": "263 40% 95%",
            "highlight": "38 95% 53%", "highlightForeground": "0 0% 10%",
            "highlightMuted": "38 90% 94%", "radius": "1rem",
        },
    }


def demo_data(full: bool = True, branded: bool = False) -> Dict[str, Any]:
    """A sample `data` mapping for the CLI/test. full=True -> all sources filled;
    full=False -> ONLY brand + product (the sparse case that proves honest placeholders).
    branded=True -> the same full data but a DISTINCT synthetic palette (Estrela Pet: violet
    brand + amber highlight) so the design-system adoption is visibly different from the default --
    proves the ad reskins from ONE swapped token set, exactly like the white-label mold."""
    brand = {
        "name": "Exemplo Pet",
        "tagline": "O marketplace do tutor de gato",
        "logoAlt": "Exemplo Pet",
        "domain": "exemplopet.com.br",
        "fontFamily": "Inter, -apple-system, Segoe UI, sans-serif",
        "tokens": {
            "background": "0 0% 100%", "foreground": "213 47% 12%",
            "card": "0 0% 98%", "cardForeground": "213 47% 12%",
            "popover": "0 0% 100%", "popoverForeground": "213 47% 12%",
            "primary": "174 68% 50%", "primaryForeground": "0 0% 100%",
            "secondary": "213 35% 18%", "secondaryForeground": "0 0% 100%",
            "muted": "210 20% 96%", "mutedForeground": "213 15% 45%",
            "accent": "174 68% 50%", "accentForeground": "0 0% 100%",
            "border": "210 20% 88%", "input": "210 20% 88%", "ring": "174 68% 50%",
            "brand": "174 68% 50%", "brandForeground": "0 0% 100%", "brandMuted": "174 30% 92%",
            "highlight": "42 100% 50%", "highlightForeground": "0 0% 10%",
            "highlightMuted": "42 80% 93%", "radius": "0.75rem",
        },
    }
    if branded:
        brand = _branded_demo_brand()
    product = {"name": "Arranhador Torre 1,2m", "category": "Moveis para gato"}
    if not full:
        # Sparse: brand known, everything else empty -> honest placeholders, zero fabrication.
        return {"brand": brand, "product": product, "meta": {"real": False}}

    return {
        "brand": brand,
        "product": product,
        "copy": {
            "title": "Arranhador Torre de Sisal 1,2m para Gatos",
            "headline": "Seu gato para de arranhar o sofa em 7 dias",
            "subheadline": "Torre de sisal natural de 1,2m que aguenta gatos de ate 8kg -- "
                           "testada por tutores em apartamento.",
            "description": "Torre arranhador vertical de sisal natural com 1,2m de altura e "
                           "base firme -- o lugar definitivo para o seu gato afiar as garras.",
            "long_description": "Projetada para apartamento: ocupa pouco chao, integra-se ao "
                                "comodo onde o gato ja vive e oferece sisal na vertical, exatamente "
                                "o que ele procura. A base de MDF de alta densidade mantem a torre "
                                "estavel mesmo com saltos de gatos de ate 8kg, e a plataforma do "
                                "topo vira o ponto de descanso preferido da casa.",
            "why": "Gato arranha por instinto: marca territorio e afia as garras. A torre da "
                   "a ele um lugar MELHOR que o sofa -- sisal natural na vertical, firme, no "
                   "comodo onde ele ja vive. Em uma semana o habito migra.",
            "key_features": [
                "Poste de sisal natural prensado de 1,2m",
                "Base de MDF de alta densidade 40x40cm",
                "Plataforma superior acolchoada",
                "Acompanha chave de montagem",
            ],
            "benefits_functional": [
                {"title": "Sisal natural resistente", "body": "Fibra que dura anos sem soltar -- "
                 "o gato arranha aqui, nao no seu sofa."},
                {"title": "Estavel para gatos grandes", "body": "Base de MDF de alta densidade: "
                 "aguenta saltos de gatos de ate 8kg sem balancar."},
                {"title": "Montagem em 10 minutos", "body": "Chega pronta pra montar, com chave "
                 "inclusa. Sem furadeira."},
            ],
            "benefits_emotional": [
                {"title": "Seu sofa intacto", "body": "O fim da briga diaria pelo estofado -- "
                 "a casa volta a ser sua e do gato."},
                {"title": "Tranquilidade de quem cuida", "body": "Voce da ao seu gato o que ele "
                 "precisa por instinto, sem culpa."},
            ],
            "cta_label": "Quero a torre com desconto",
            "cta_sub": "Frete gratis SP e RJ - 30 dias de garantia",
            "faq": [
                {"q": "Aguenta mais de um gato?", "a": "Sim -- a base suporta ate 8kg; dois gatos "
                 "medios usam a torre sem problema."},
                {"q": "O sisal solta fiapo?", "a": "Nao. E sisal natural prensado, preso na "
                 "estrutura -- nao desfia com o uso normal."},
                {"q": "Qual o prazo de entrega?", "a": "2 dias uteis para SP e RJ; 5 a 7 dias "
                 "uteis para o resto do Brasil."},
            ],
        },
        "media": {
            "hero": {"src": "https://cdn.exemplopet.com.br/torre/hero.jpg",
                     "alt": "Gato usando a torre arranhador de sisal na sala"},
            "gallery": [
                {"src": "https://cdn.exemplopet.com.br/torre/lado.jpg", "alt": "Torre vista de lado"},
                {"src": "https://cdn.exemplopet.com.br/torre/topo.jpg", "alt": "Plataforma do topo"},
            ],
        },
        "offer": {
            "price": "R$ 199,00", "original_price": "R$ 289,00", "discount": "-31% hoje",
            "installments": "ou 6x de R$ 33,17 sem juros",
            "urgency": "Ultimas 12 unidades com esse preco",
            "guarantee": "30 dias de garantia ou seu dinheiro de volta",
            "shipping": "Frete gratis para SP e RJ",
        },
        "proof": {
            "rating": "4.8", "count": "2.143",
            "testimonials": [
                {"quote": "Meu gato adotou a torre no primeiro dia e largou o sofa de vez.",
                 "author": "Marina S., Sao Paulo"},
                {"quote": "Firme de verdade. Tenho um gato de 7kg e nao balanca nada.",
                 "author": "Rafael T., Rio de Janeiro"},
            ],
        },
        # The FICHA -- the frozen facts as STRUCTURED data (numeric dims/weight + lists +
        # identity codes + the attributes long-tail). Renders as its OWN section, separate
        # from the prose body + the bullets (THE LOAD-BEARING SEAM).
        "ficha": {
            "dimensions": {"largura": 40.0, "altura": 120.0, "profundidade": 40.0, "unit": "cm"},
            "weight": {"value": 6.5, "unit": "kg", "grams": 6500},
            "materials": ["Sisal natural", "MDF alta densidade", "Feltro"],
            "colors": ["Bege", "Cinza", "Grafite"],
            "identity": {"brand": "Exemplo Pet", "model": "Torre 120", "sku": "EXPET-ARR-12",
                         "gtin": "7891234567890"},
            "attributes": {"Indicacao de porte": "gatos de ate 8 kg",
                           "Tipo de fixacao": "piso (base livre)"},
        },
        # The legacy flat specs -- the genuinely-EXTRA rows (not in the structured ficha).
        # They append BELOW the ficha rows (backward-compat: a flat specs[] still renders).
        "specs": [
            {"label": "Peso suportado", "value": "ate 8 kg"},
            {"label": "Montagem", "value": "10 min, chave inclusa"},
        ],
        "meta": {
            "real": False,  # demo data -> honest "amostra" badge (never claim a real run).
            "created": "2026-06-22T14:30:00Z",
            "sources": ["catalogo exemplo", "avaliacoes verificadas da loja"],
        },
    }


def demo_product_record() -> Dict[str, Any]:
    """A sample CANONICAL product record -- the docs/schema/product_catalog_schema.yaml
    shape that cex_product_catalog_adapter.normalize_product emits. Feeds
    ad_data_from_product to prove the mold renders the FULL listing content (title, prose
    body, bullets, two benefit groups, faq, the structured ficha) from a real catalog
    record. ASCII source; a real record carries fully-accented runtime strings."""
    return {
        "slug": "arranhador-torre-sisal-12m",
        "sku": "EXPET-ARR-12",
        "name": "Arranhador Torre de Sisal 1,2m para Gatos",
        "tagline": "Seu gato para de arranhar o sofa em 7 dias",
        "brand": "Exemplo Pet",
        "model": "Torre 120",
        "gtin": "7891234567890",
        "price": 199.0,
        "images": [
            "https://cdn.exemplopet.com.br/torre/hero.jpg",
            "https://cdn.exemplopet.com.br/torre/lado.jpg",
            "https://cdn.exemplopet.com.br/torre/topo.jpg",
        ],
        "description": "Torre arranhador de sisal natural de 1,2m que aguenta gatos de ate "
                       "8kg -- testada por tutores em apartamento.",
        "long_description": "Gato arranha por instinto: marca territorio e afia as garras. A "
                            "torre da a ele um lugar melhor que o sofa -- sisal natural na "
                            "vertical, firme, no comodo onde ele ja vive. A base de MDF de alta "
                            "densidade mantem tudo estavel mesmo com gatos grandes, e em uma "
                            "semana o habito migra do estofado para a torre.",
        "why_it_works": "O sisal natural na vertical imita o tronco que o gato procuraria na "
                        "natureza -- por isso ele prefere a torre ao tecido do sofa.",
        "features": [
            "Poste de sisal natural prensado",
            "Base de MDF de alta densidade 40x40cm",
            "Plataforma superior acolchoada",
            "Acompanha chave de montagem",
        ],
        "benefits_functional": [
            "Sisal que dura anos sem soltar fiapo",
            "Estavel para gatos de ate 8kg, nao balanca",
            "Montagem em 10 minutos, sem furadeira",
        ],
        "benefits_emotional": [
            "Seu sofa intacto e seu gato satisfeito",
            "A tranquilidade de quem cuida bem do pet",
        ],
        "faq": [
            {"question": "Aguenta mais de um gato?",
             "answer": "Sim -- a base suporta ate 8kg; dois gatos medios usam sem problema."},
            {"question": "O sisal solta fiapo?",
             "answer": "Nao. E sisal natural prensado, preso na estrutura -- nao desfia."},
        ],
        "materials": ["Sisal natural", "MDF alta densidade", "Feltro"],
        "colors": ["Bege", "Cinza", "Grafite"],
        "dimensions": {"largura": 40.0, "altura": 120.0, "profundidade": 40.0, "unit": "cm"},
        "weight": {"value": 6.5, "unit": "kg", "grams": 6500},
        "warranty": "30 dias de garantia ou seu dinheiro de volta",
        "shipping_info": "Frete gratis para SP e RJ",
        "seo": {
            "title": "Arranhador Torre Sisal 1,2m | Exemplo Pet",
            "description": "Torre de sisal natural 1,2m para gatos de ate 8kg. Seu gato larga "
                           "o sofa em 7 dias. Frete gratis SP e RJ.",
            "keywords": ["arranhador", "torre sisal", "gato"],
        },
        "attributes": {
            "Indicacao de porte": "gatos de ate 8 kg",
            "Tipo de fixacao": "piso (base livre)",
        },
        "status": "published",
        "_provenance": {"source": "exemplo (demo)", "confidence": 0.9,
                        "completeness": 1.0, "flags": []},
    }


# --------------------------------------------------------------------------- #
# CLI.
# --------------------------------------------------------------------------- #
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="product_ad HTML mold emitter")
    ap.add_argument("--demo", choices=["full", "sparse", "branded", "product"], default="full",
                    help="emit a demo ad: 'full' (all sources, sample brand), 'sparse' (honest "
                         "placeholders), 'branded' (full + a DISTINCT tenant palette), or "
                         "'product' (a CANONICAL product record via ad_data_from_product)")
    ap.add_argument("--out", help="write the HTML here (default: stdout)")
    args = ap.parse_args(argv)

    if args.demo == "product":
        data = ad_data_from_product(demo_product_record(), brand=demo_data()["brand"])
    else:
        data = demo_data(full=(args.demo != "sparse"), branded=(args.demo == "branded"))
    html = emit_product_ad(data)

    if args.out:
        # Emitted HTML may carry PT-BR accents (runtime content) -> utf-8.
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html)
        sys.stderr.write("[OK] wrote %s (%d bytes)\n" % (args.out, len(html.encode("utf-8"))))
    else:
        sys.stdout.write(html)
    return 0


__all__ = [
    "emit_product_ad",
    "ad_data_from_product",
    "demo_data",
    "demo_product_record",
    "_resolve_brand_tokens",
    "SECTION_ORDER",
    "SCHEMA_VERSION",
]


if __name__ == "__main__":
    raise SystemExit(main())
