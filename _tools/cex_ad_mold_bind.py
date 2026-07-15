#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_ad_mold_bind -- bind the `ads` capability output to the product_ad mold (ADWIRE W3).

THE wire between the `ads` structured generator (capability_generators/ads.py) and the
conversion-grade product-ad mold (cex_product_ad_mold.emit_product_ad). W2 built the mold
(the CONTAINER); this module FILLS it from a real ads run so the ads capability's HUMAN
face renders as "a altura de um produto de anuncio" -- the founder's brand-voice ad copy
flowing into the 10-section conversion structure, brand-themed by the tenant's own tokens.

WHAT IT DOES (the mapper):
  ads StructuredOutput (output_sections: Variantes / Teste A/B / Voz / Compliance /
  Keywords / Estrategia de funil)  +  the run inputs (product/...)  +  the dual-output
  resolved media_slots  +  the tenant BRAND tokens
        ->  the emit_product_ad ``data`` shape {brand, product, copy, media, offer, meta}
        ->  ONE self-contained, brand-themed, conversion HTML document.

THE FILL-SOURCES (each resolves independently; degrade-never):
  * COPY  -- the Variantes table carries the brand-voice copy (Hook/Corpo/CTA per variant).
            The Teste A/B "Vencedor previsto" picks the hero variant; the rest become the
            value-prop benefit cards. No variant -> return None (the caller keeps the
            generic dual render). NEVER invents copy.
  * BRAND -- the tenant's minted brand.config.ts overlay, parsed via the EXACT moldgen
            contract (cex_moldgen_emit.parse_overlay_ts) so the ad re-themes from the SAME
            24 tokens every other tenant surface uses. An explicit inputs['brand'] dict
            overrides the file. Absent -> the mold's neutral fallback (still renders).
  * MEDIA -- the dual-output resolved media_slots. A GENERATED image slot (real src) ->
            the mold's hero/gallery; an EMPTY slot -> the mold's own upload dropzone
            (never a fabricated <img>). The ads generator's slots start empty -> dropzones.
  * DATA  -- price/offer/proof/specs are NOT produced by the ads capability itself. When the
            run carries a CATALOG record (inputs['product_record'] -- the
            product_catalog_schema shape from get_product_record / normalize_product), this
            module folds it through ad_data_from_product so the body (description prose),
            features (key_features BULLETS), value (benefits_functional/_emotional), offer
            (price/shipping/warranty), specs (the ficha), and faq sections fill from REAL
            catalog data -- WITHOUT the LLM (ADMAX W2b). THE SEAM survives: bullets -> the
            features key, prose -> description, the frozen facts -> the ficha key -- never
            concatenated (ad_data_from_product maps them to SEPARATE keys). With no record,
            those slots stay the mold's honest "[preencher: ...]" placeholders. The ads
            VARIANTS still drive the hero copy (headline/subheadline/cta) -- the catalog
            never overrides the brand-voice hook. NEVER a fabricated price/rating.

HONESTY (Commandment I): the footer real/sample badge reflects whether the copy was truly
LLM-generated. If the ads run fell back to its deterministic scaffold (a
"generation_pending" note), meta.real is forced False ("amostra -- dados simulados") even
though the ads payload carries real=True -- a scaffold is not a real result.

PURE-ish + TOTAL: ``map_ads_to_ad_data`` is a deterministic projection (no IO).
``resolve_brand`` does ONE best-effort read of the tenant overlay (TOTAL: any failure ->
{}). ``build_ad_human_html`` composes them and NEVER raises -- a None return tells the
run-path to keep today's generic human face (the degrade-never contract). The kill-switch
+ fallback live in the caller (cex_run_capability); this module is the pure mapper.

ASCII-only source per .claude/rules/ascii-code-rule.md. The EMITTED HTML may carry PT-BR
copy with full diacritics (runtime CONTENT from the ads payload) -- this module's own
string constants stay diacritic-free.

Importable API: build_ad_human_html(payload, inputs, media_slots, tenant_id),
map_ads_to_ad_data(payload, inputs, media_slots, brand), resolve_brand(tenant_id, inputs).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

# --------------------------------------------------------------------------- #
# Sibling imports (both live in _tools/). Bootstrap the path whether this runs
# as a script or is imported with _tools already on sys.path.
# --------------------------------------------------------------------------- #
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from cex_product_ad_mold import ad_data_from_product, emit_product_ad  # noqa: E402

# REUSE the grounded-copy engine (W2 P3): re-voice a catalog record's title/bullets/body
# through the G1-G10 grounding gate before they fill the mold. TOTAL: absent -> skip (the
# catalog fields are already grounded-by-construction, so a missing engine is zero-regression).
try:
    from cex_grounded_copy import extract_copy as _grounded_extract_copy  # noqa: E402
    from cex_grounded_copy import source_text_of as _grounded_source_text  # noqa: E402
except Exception:  # pragma: no cover - degrade-never on import path issues
    _grounded_extract_copy = None  # type: ignore[assignment]
    _grounded_source_text = None  # type: ignore[assignment]

# --------------------------------------------------------------------------- #
# Module constants -- no side effects.
# --------------------------------------------------------------------------- #
# The default location the MOLDGEN mint writes a tenant's brand.config.ts overlay to
# (the global runtime moldgen dir, keyed by tenant slug -- e.g. .cex/runtime/moldgen/
# <tid>/brand.config.ts). Overridable via env for tests / alternate layouts.
_DEFAULT_MOLDGEN_ROOT = os.path.join(".cex", "runtime", "moldgen")
_ENV_MOLDGEN_ROOT = "CEX_AD_MOLD_BRAND_ROOT"

# The ads output_sections that carry the copy (titles emitted by ads.py).
_SEC_VARIANTES = "Variantes"
_SEC_AB = "Teste A/B"

# Variantes column headers (ads.py): Plataforma | Hook | Corpo | CTA | Chars | Limite.
_COL_HOOK = "Hook"
_COL_CORPO = "Corpo"
_COL_CTA = "CTA"
_AB_WINNER_LABEL = "Vencedor previsto"

# A note substring that marks the ads copy as a deterministic scaffold (not a real LLM run).
_SCAFFOLD_MARKERS = ("generation_pending", "scaffold")

# env var that disables grounding enforcement (degrade-never: grounding=None -> old behaviour).
_ENV_GROUNDING_DISABLED = "CEX_GROUNDING_DISABLED"


# --------------------------------------------------------------------------- #
# THE composite entry (the run-path calls this).
# --------------------------------------------------------------------------- #
def build_ad_human_html(
    payload: Mapping[str, Any],
    inputs: Optional[Mapping[str, Any]] = None,
    media_slots: Optional[Sequence[Mapping[str, Any]]] = None,
    *,
    tenant_id: str = "",
    moldgen_root: Optional[str] = None,
    voice_profile: Optional[Mapping[str, Any]] = None,
    grounding: Optional[Mapping[str, Any]] = None,
) -> Optional[str]:
    """Map a real ads run into the product_ad mold and emit the conversion HTML.

    Resolves the tenant brand (overlay file or an explicit inputs['brand']), resolves the
    tenant voice profile (explicit arg > inputs['voice_profile'] > built-in > None), maps the
    ads output_sections into the emit_product_ad ``data`` shape, and emits the HTML.

    The ``grounding`` block {approved, approved_by, approved_at, sources, confidence}
    gates the honest badge: grounding.approved=False (or not provided) -> 'amostra';
    grounding.approved=True AND not scaffold -> 'resultado real'.

    Returns the HTML string, or None when the run carries NO usable copy (no Variantes /
    no variant rows) -- the signal to the caller to keep today's generic human face.

    TOTAL: never raises. Any failure (mapping miss, brand-load error, emit surprise) ->
    None -> the caller falls back (degrade-never)."""
    try:
        brand = resolve_brand(tenant_id, inputs, moldgen_root=moldgen_root)
        vp = voice_profile if isinstance(voice_profile, Mapping) else _resolve_voice_profile(tenant_id, inputs)
        data = map_ads_to_ad_data(payload, inputs, media_slots, brand=brand,
                                  voice_profile=vp, grounding=grounding)
        if data is None:
            return None
        html = emit_product_ad(data)
        return html if isinstance(html, str) and html.strip() else None
    except Exception:
        # degrade-never: the caller keeps the generic dual human_html.
        return None


# --------------------------------------------------------------------------- #
# THE mapper (PURE + TOTAL): ads StructuredOutput -> emit_product_ad data.
# --------------------------------------------------------------------------- #
def map_ads_to_ad_data(
    payload: Mapping[str, Any],
    inputs: Optional[Mapping[str, Any]] = None,
    media_slots: Optional[Sequence[Mapping[str, Any]]] = None,
    brand: Optional[Mapping[str, Any]] = None,
    voice_profile: Optional[Mapping[str, Any]] = None,
    grounding: Optional[Mapping[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Project the ads payload into the mold ``data`` dict, or None if there is no copy.

    voice_profile: a TenantVoiceProfile dict (from cex_tenant_voice_profile). When present,
    the ``voice`` key in the returned data carries tone/platform/register context so the mold
    can render copy in the brand's real voice. degrade-never: None -> no voice key.

    grounding: {approved, approved_by, approved_at, sources, confidence}. When present,
    grounding.approved gates the honest badge (meta.real). When None, old behaviour applies.

    PURE + TOTAL: a missing/malformed section degrades to an honest-placeholder slot (the
    mold renders it); the ONLY None case is genuinely-no-copy (no variant Hook/Corpo/CTA),
    where the generic dual render is more honest than an all-placeholder mold."""
    sections = _sections(payload)

    variants = _variants(sections)
    if not variants:
        return None  # no usable copy -> caller keeps the generic render (incomplete fallback)

    winner_idx = _winner_index(sections, len(variants))
    winner = variants[winner_idx]

    inp = inputs if isinstance(inputs, Mapping) else {}
    channel = _s(inp.get("channel"))

    # Resolve voice profile: explicit kwarg > inputs["voice_profile"] > None.
    # inputs-based resolution reads inputs only (no tenant lookup here).
    if voice_profile is None:
        voice_profile = _resolve_voice_profile("", inp)

    # COPY: hero = the predicted-winner variant; benefits = the OTHER variants (each a
    # distinct brand-voice angle re-framed as a value card). Pulled from Variantes per the
    # ADWIRE handoff. Empty fields degrade to the mold's "[preencher: ...]" placeholders.
    benefits: List[Dict[str, str]] = []
    for i, v in enumerate(variants):
        if i == winner_idx:
            continue
        if v["hook"] or v["corpo"]:
            benefits.append({"title": v["hook"], "body": v["corpo"]})

    copy: Dict[str, Any] = {
        "headline": winner["hook"],
        "subheadline": winner["corpo"],
        "cta_label": winner["cta"],
        "benefits": benefits,
    }

    product: Dict[str, Any] = {}
    name = _s(inp.get("product"))
    if name:
        product["name"] = name
    category = _s(inp.get("category"))
    if category:
        product["category"] = category

    media = _map_media(media_slots)

    # GROUNDING: normalize and determine approval state.
    grnd = _normalize_grounding(grounding)

    data: Dict[str, Any] = {
        "brand": dict(brand) if isinstance(brand, Mapping) else {},
        "product": product,
        "copy": copy,
        "media": media,
        # OFFER / PROOF / SPECS are NOT produced by the ads capability -> omit them so the
        # mold renders honest placeholders (NEVER a fabricated price/rating/spec).
        "offer": {},
        # GROUNDING: approval gate. Stored for the mold footer + any downstream consumer.
        "grounding": grnd,
        # META: honest real/sample badge. grounding.approved gates meta.real when present.
        "meta": _meta(payload, grounding=grnd if grounding is not None else None),
    }

    # CATALOG FILL (ADMAX W2b): when the run carries a canonical product record, fold the
    # REAL catalog content into the body/features/value/offer/specs/faq sections WITHOUT the
    # LLM. The ads VARIANTS keep driving the hero (headline/subheadline/cta/benefits); the
    # catalog fills only what ads never produces. THE SEAM is preserved by construction --
    # ad_data_from_product maps features -> key_features (bullets), description -> the prose
    # body, and the frozen facts -> the ficha (SEPARATE keys, never concatenated).
    record = _product_record(inp)
    if record is not None:
        data = _merge_catalog(data, record)
        # GROUNDED COPY (W2 P3): re-voice the catalog title/bullets/body through the G1-G10
        # grounding gate before they fill the mold, and attach the grounding result for the
        # HITL/badge gate. degrade-never: engine absent / failure -> data unchanged. With no
        # llm the deterministic projection is byte-identical to _merge_catalog's catalog fill,
        # plus the grounding proof (zero-regression). An llm rides in via inputs['copy_llm'].
        copy_llm = inp.get("copy_llm")
        data = attach_grounded_copy(
            data, record, voice_profile=voice_profile,
            llm=copy_llm if callable(copy_llm) else None,
        )

    # VOICE: register context from the tenant's voice profile (degrade-never: None -> skip).
    voice_data = _extract_voice_data(voice_profile, channel)
    if voice_data:
        data["voice"] = voice_data

    return data


# --------------------------------------------------------------------------- #
# CATALOG fill (ADMAX W2b): a canonical product record -> the real DATA sections.
# --------------------------------------------------------------------------- #
def _product_record(inputs: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
    """The canonical product record carried in the run inputs, or None. PURE + TOTAL.

    A run that fetched the catalog record (get_product_record by sku) passes it as
    inputs['product_record'] (the product_catalog_schema shape). degrade-never: absent /
    non-mapping / empty -> None (the ads-only data shape is unchanged, byte-for-byte)."""
    rec = inputs.get("product_record")
    if isinstance(rec, Mapping) and rec:
        return rec
    return None


def _merge_catalog(
    data: Dict[str, Any],
    record: Mapping[str, Any],
) -> Dict[str, Any]:
    """Fold a canonical catalog record into the ads ``data`` dict (ADMAX W2b). PURE + TOTAL.

    The catalog provides the DATA sections the ads capability never produces -- the prose
    body (description/long_description/why_it_works), the BULLETS (key_features), the two
    benefit groups (benefits_functional/_emotional), the offer (price/shipping/warranty),
    the ficha (dimensions/weight/materials/colors/identity), and the faq.

    The ads VARIANTS keep ownership of the hero: copy.headline / copy.subheadline /
    copy.cta_label / copy.benefits (the brand-voice creative) are NOT overwritten by the
    catalog. Everything else (the catalog's rich, real content) merges in.

    THE SEAM is preserved because ad_data_from_product already maps the bullets, the prose,
    and the frozen facts to SEPARATE keys; this function never concatenates them. TOTAL: any
    failure -> the original ads-only data unchanged (degrade-never)."""
    try:
        rich = ad_data_from_product(record)
    except Exception:
        return data
    if not isinstance(rich, Mapping):
        return data

    out = dict(data)

    # COPY: keep the ads hero (headline/subheadline/cta_label/benefits); add the catalog's
    # body prose + bullets + benefit groups + faq + listing title underneath. The ads keys
    # take priority on conflict so the brand-voice hook always wins.
    rich_copy = rich.get("copy")
    if isinstance(rich_copy, Mapping):
        merged_copy = dict(rich_copy)
        merged_copy.update(out.get("copy") or {})  # ads hero wins on conflict
        out["copy"] = merged_copy

    # OFFER / FICHA / PRODUCT identity / SPECS: the catalog is the only real source -> adopt
    # it wholesale (the ads path leaves these empty). MEDIA: only adopt the catalog images
    # when the ads media_slots produced NONE (a generated ad creative wins over the catalog).
    for key in ("offer", "ficha"):
        val = rich.get(key)
        if isinstance(val, Mapping) and val:
            out[key] = dict(val)
    specs = rich.get("specs")
    if specs:
        out["specs"] = specs

    rich_product = rich.get("product")
    if isinstance(rich_product, Mapping) and rich_product:
        merged_product = dict(rich_product)
        merged_product.update(out.get("product") or {})  # run-supplied name wins
        out["product"] = merged_product

    if not (isinstance(out.get("media"), Mapping) and out["media"]):
        rich_media = rich.get("media")
        if isinstance(rich_media, Mapping) and rich_media:
            out["media"] = dict(rich_media)

    # META sources: union the catalog provenance into the ads meta (keeps the ads real/badge
    # decision -- the catalog never flips meta.real, only adds a provenance line).
    rich_meta = rich.get("meta")
    if isinstance(rich_meta, Mapping):
        rich_sources = rich_meta.get("sources")
        if isinstance(rich_sources, (list, tuple)) and rich_sources:
            meta = dict(out.get("meta") or {})
            existing = list(meta.get("sources") or [])
            for s in rich_sources:
                if s and s not in existing:
                    existing.append(s)
            if existing:
                meta["sources"] = existing
            out["meta"] = meta

    return out


# --------------------------------------------------------------------------- #
# GROUNDED COPY (W2 P3): re-voice the catalog title/bullets/body through the    #
# G1-G10 grounding gate, and attach the grounding result for HITL / the badge.  #
# --------------------------------------------------------------------------- #
def _record_to_canonical_copy_view(record: Mapping[str, Any]) -> Dict[str, Any]:
    """A canonical-shaped view of a catalog record for the grounded-copy engine. PURE + TOTAL.

    The engine speaks the CanonicalProduct vocabulary (title/key_features/description/...); the
    product_record is the product_catalog_schema shape (name/features/description/...). This
    bridges the few field-name differences AND carries the rich raw fields (materials, dims,
    weight, the raw imported text) so the grounding SOURCE blob is complete. Never fabricates:
    only real record values are mapped through.
    """
    r = record if isinstance(record, Mapping) else {}
    view: Dict[str, Any] = {}
    # title: the listing name (canonical `title`).
    name = r.get("name")
    if isinstance(name, str) and name.strip():
        view["title"] = name.strip()
    tagline = r.get("tagline")
    if isinstance(tagline, str) and tagline.strip():
        view["subtitle"] = tagline.strip()
    # prose set -- verbatim.
    for key in ("description", "long_description", "why_it_works"):
        v = r.get(key)
        if isinstance(v, str) and v.strip():
            view[key] = v.strip()
    # bullets: catalog `features` -> canonical `key_features`.
    feats = r.get("features")
    if isinstance(feats, (list, tuple)):
        kept = [x.strip() for x in feats if isinstance(x, str) and x.strip()]
        if kept:
            view["key_features"] = kept
    # structured fact fields the SOURCE blob needs (materials/colors/audience).
    for key in ("benefits_functional", "benefits_emotional", "colors", "materials", "audience_tags"):
        v = r.get(key)
        if isinstance(v, (list, tuple)):
            kept = [x for x in v if isinstance(x, str) and x.strip()]
            if kept:
                view[key] = kept
    # numeric ficha facts -> the canonical numeric keys (so source_text_of renders them).
    dims = r.get("dimensions")
    if isinstance(dims, Mapping):
        if isinstance(dims.get("largura"), (int, float)):
            view["dim_length_cm"] = dims.get("largura")
        if isinstance(dims.get("altura"), (int, float)):
            view["dim_height_cm"] = dims.get("altura")
        if isinstance(dims.get("profundidade"), (int, float)):
            view["dim_width_cm"] = dims.get("profundidade")
    weight = r.get("weight")
    if isinstance(weight, Mapping) and isinstance(weight.get("grams"), (int, float)):
        view["weight_grams"] = weight.get("grams")
    # identity codes (grounds a brand/model mention).
    for key in ("brand", "model", "mpn", "gtin", "sku"):
        v = r.get(key)
        if isinstance(v, str) and v.strip():
            view[key] = v.strip()
    # the attributes long-tail + the seo block + any raw imported text -> all valid source.
    attrs = r.get("attributes")
    if isinstance(attrs, Mapping) and attrs:
        view["attributes"] = dict(attrs)
    seo = r.get("seo")
    if isinstance(seo, Mapping):
        view["seo"] = dict(seo)
    for key in ("_source_text", "raw_text", "raw_description", "source_text"):
        v = r.get(key)
        if isinstance(v, str) and v.strip():
            view[key] = v.strip()
            break
    return view


def attach_grounded_copy(
    data: Dict[str, Any],
    record: Mapping[str, Any],
    voice_profile: Optional[Mapping[str, Any]] = None,
    llm: Optional[Any] = None,
) -> Dict[str, Any]:
    """Run the grounded-copy engine (W2 P3) over a catalog record and fold the GROUNDED
    title/bullets/body into the mold ``data``, attaching the grounding result. PURE-ish + TOTAL.

    The three SEPARATE grounded payloads map back to the mold's SEAM-separate slots:
      title   -> copy.title         (the listing/SEO title)
      bullets -> copy.key_features  (the BULLETS section -- never the prose)
      body    -> copy.description / long_description / why_it_works (the PROSE -- never bullets)

    The ads VARIANTS keep the hero (copy.headline/subheadline/cta_label/benefits): the grounded
    copy fills the catalog-derived slots only, exactly like _merge_catalog -- the brand-voice
    hook always wins. The grounding result rides under data['grounding_copy'] for the HITL gate
    + the honest badge (a section with a fabricated fact was OMITted, never shipped).

    With NO llm, the engine's deterministic projection re-voices STRICTLY from the record (the
    catalog fields verbatim) -> byte-identical content to _merge_catalog, plus the grounding
    proof. With an llm wired, the LLM copy passes the gate (retry-once-then-OMIT) before it
    fills the mold. degrade-never: engine absent / any failure -> data unchanged.
    """
    if _grounded_extract_copy is None:
        return data
    try:
        view = _record_to_canonical_copy_view(record)
        grounded = _grounded_extract_copy(view, voice_profile=voice_profile, llm=llm)
    except Exception:
        return data
    if not isinstance(grounded, Mapping):
        return data

    out = dict(data)
    copy = dict(out.get("copy") or {})

    # title -> copy.title (only if the ads hero did not already set a listing title).
    title = grounded.get("title")
    if isinstance(title, str) and title.strip() and not copy.get("title"):
        copy["title"] = title.strip()

    # bullets -> copy.key_features (the grounded bullets REPLACE the raw catalog bullets:
    # they are the same facts, gate-checked + spec-label-scrubbed).
    bullets = grounded.get("bullets")
    if isinstance(bullets, (list, tuple)) and bullets:
        copy["key_features"] = [b for b in bullets if isinstance(b, str) and b.strip()]

    # body -> the prose set (grounded; a fabricated/empty field was OMITted by the engine).
    body = grounded.get("body")
    if isinstance(body, Mapping):
        for key in ("description", "long_description", "why_it_works"):
            v = body.get(key)
            if isinstance(v, str) and v.strip():
                copy[key] = v.strip()

    out["copy"] = copy

    # Attach the grounding result (the HITL/badge gate reads this -- proof of no-fabrication).
    grnd = grounded.get("grounding")
    if isinstance(grnd, Mapping):
        out["grounding_copy"] = {
            "ok": bool(grnd.get("ok", True)),
            "blocking": bool(grnd.get("blocking", False)),
            "findings": list(grnd.get("findings") or []),
            "omitted": list((grounded.get("meta") or {}).get("omitted") or []),
            "provider": (grounded.get("meta") or {}).get("provider", "deterministic"),
        }
    return out


# --------------------------------------------------------------------------- #
# BRAND resolution (best-effort; TOTAL): explicit inputs override, else the overlay.
# --------------------------------------------------------------------------- #
def resolve_brand(
    tenant_id: str,
    inputs: Optional[Mapping[str, Any]] = None,
    *,
    moldgen_root: Optional[str] = None,
) -> Dict[str, Any]:
    """Resolve the brand dict for the mold (the mold's {name, tagline, logo, logoAlt,
    tokens{24}, fontFamily, domain} shape). Priority:

      1. an explicit ``inputs['brand']`` dict (mold-shape OR moldgen-spec-shape) -- the
         seam an edge can use to pass brand inline (and the pure unit-test path);
      2. the tenant's minted brand.config.ts overlay parsed via the moldgen contract;
      3. {} -> the mold renders in its neutral fallback (still a valid, themed-ish ad).

    TOTAL: any read/parse failure -> {} (degrade-never). NEVER raises."""
    inp = inputs if isinstance(inputs, Mapping) else {}
    explicit = inp.get("brand")
    if isinstance(explicit, Mapping) and explicit:
        return _normalize_brand(explicit)

    spec = _load_overlay_spec(tenant_id, moldgen_root=moldgen_root)
    if spec:
        return _spec_to_brand(spec)
    return {}


def _load_overlay_spec(
    tenant_id: str,
    *,
    moldgen_root: Optional[str] = None,
) -> Dict[str, Any]:
    """Read + parse the tenant's brand.config.ts overlay into a moldgen spec dict, or {}.

    Reuses cex_moldgen_emit.parse_overlay_ts (the single source of truth for the overlay
    shape). TOTAL: no tenant / no file / parse error / module absent -> {}."""
    tid = (tenant_id or "").strip()
    if not tid:
        return {}
    root = _resolve_moldgen_root(moldgen_root)
    path = _overlay_path(root, tid)
    if path is None:
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return {}
    try:
        from cex_moldgen_emit import parse_overlay_ts  # noqa: E402  (sibling)

        spec = parse_overlay_ts(text)
        return spec if isinstance(spec, dict) else {}
    except Exception:
        return {}


def _resolve_moldgen_root(moldgen_root: Optional[str]) -> Path:
    """The moldgen overlay root: explicit arg > env > repo-relative default. TOTAL."""
    if moldgen_root:
        return Path(moldgen_root)
    env = os.environ.get(_ENV_MOLDGEN_ROOT)
    if env and env.strip():
        return Path(env.strip())
    # Repo root is the parent of _tools/ (this file's dir).
    repo_root = Path(_HERE).resolve().parent
    return repo_root / _DEFAULT_MOLDGEN_ROOT


def _overlay_path(root: Path, tid: str) -> Optional[Path]:
    """The brand.config.ts path for a tenant under ``root``. Tries the tid as-is, then a
    sanitized lowercase slug (the moldgen mint slugs the tenant). First existing wins."""
    candidates = [tid]
    slug = re.sub(r"[^a-z0-9]+", "_", tid.lower()).strip("_")
    if slug and slug != tid:
        candidates.append(slug)
    for cand in candidates:
        try:
            p = root / cand / "brand.config.ts"
            if p.is_file():
                return p
        except Exception:
            continue
    return None


def _spec_to_brand(spec: Mapping[str, Any]) -> Dict[str, Any]:
    """Map a moldgen overlay spec ({name, tagline, logo, logoAlt, domain, font{family},
    tokens{}}) into the mold's brand shape ({..., fontFamily, tokens{}}). TOTAL."""
    brand: Dict[str, Any] = {}
    for key in ("name", "tagline", "logo", "logoAlt", "domain"):
        val = _s(spec.get(key))
        if val:
            brand[key] = val
    font = spec.get("font")
    if isinstance(font, Mapping):
        fam = _s(font.get("family"))
        if fam:
            brand["fontFamily"] = fam
    tokens = spec.get("tokens")
    if isinstance(tokens, Mapping) and tokens:
        brand["tokens"] = dict(tokens)
    return brand


def _normalize_brand(brand: Mapping[str, Any]) -> Dict[str, Any]:
    """Accept a brand dict in EITHER the mold shape (fontFamily) or the moldgen-spec shape
    (font.family) and return the mold shape. Passes tokens through verbatim. TOTAL."""
    out: Dict[str, Any] = dict(brand)
    if "fontFamily" not in out:
        font = out.get("font")
        if isinstance(font, Mapping):
            fam = _s(font.get("family"))
            if fam:
                out["fontFamily"] = fam
    return out


# --------------------------------------------------------------------------- #
# MEDIA mapping: dual-output slots -> the mold's media block (generated only).
# --------------------------------------------------------------------------- #
def _map_media(media_slots: Optional[Sequence[Mapping[str, Any]]]) -> Dict[str, Any]:
    """Map the dual-output resolved media_slots into the mold's {hero, gallery} block.

    ONLY a GENERATED image slot with a real src is forwarded (the first -> hero, the rest
    -> gallery). Empty slots are NOT forwarded -> the mold renders its own honest upload
    dropzones. NEVER fabricates a src. TOTAL."""
    hero: Optional[Dict[str, str]] = None
    gallery: List[Dict[str, str]] = []
    for slot in media_slots or []:
        if not isinstance(slot, Mapping):
            continue
        if str(slot.get("kind") or "").strip().lower() != "image":
            continue
        if str(slot.get("status") or "").strip().lower() != "generated":
            continue
        src = _s(slot.get("src"))
        if not src:
            continue
        entry: Dict[str, str] = {"src": src}
        alt = _s(slot.get("alt")) or _s(slot.get("label"))
        if alt:
            entry["alt"] = alt
        if hero is None:
            hero = entry
        else:
            gallery.append(entry)
    media: Dict[str, Any] = {}
    if hero:
        media["hero"] = hero
    if gallery:
        media["gallery"] = gallery
    return media


# --------------------------------------------------------------------------- #
# META / provenance (honest real vs scaffold + grounding gate).
# --------------------------------------------------------------------------- #
def _meta(
    payload: Mapping[str, Any],
    grounding: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """The mold's provenance meta. real = payload.real AND not scaffold AND (when grounding
    is provided) grounding.approved. Any of these missing -> 'amostra' (honesty first).

    grounding=None preserves the pre-grounding behaviour (backward compat)."""
    notes = payload.get("notes")
    scaffolded = False
    if isinstance(notes, (list, tuple)):
        for n in notes:
            low = str(n).lower()
            if any(m in low for m in _SCAFFOLD_MARKERS):
                scaffolded = True
                break

    payload_real = bool(payload.get("real", False))

    if grounding is not None:
        grounding_approved = bool(grounding.get("approved", False))
        real = payload_real and not scaffolded and grounding_approved
    else:
        real = payload_real and not scaffolded

    meta: Dict[str, Any] = {"real": real}

    # Pass grounding sources to the mold footer (the mold's _section_footer reads meta.sources).
    if grounding:
        sources = grounding.get("sources")
        if isinstance(sources, (list, tuple)):
            srcs = [_s(s) for s in sources if _s(s)]
            if srcs:
                meta["sources"] = srcs
        # approved_by + approved_at -> meta.created (the mold renders this as the provenance line).
        if real:
            approved_by = _s(grounding.get("approved_by"))
            approved_at = _s(grounding.get("approved_at"))
            if approved_by or approved_at:
                parts = [x for x in (approved_at, approved_by) if x]
                meta["created"] = " ".join(parts)

    return meta


# --------------------------------------------------------------------------- #
# VOICE: extract relevant voice context from a TenantVoiceProfile.
# --------------------------------------------------------------------------- #
def _extract_voice_data(
    profile: Optional[Mapping[str, Any]],
    channel: str,
) -> Dict[str, Any]:
    """Extract the voice context relevant to this channel from a TenantVoiceProfile dict.

    Returns a dict with {tone, platform, register} (each optional). An absent profile or
    absent channel yields {}. PURE + TOTAL."""
    if not isinstance(profile, Mapping):
        return {}
    voice: Dict[str, Any] = {}

    tone = profile.get("tone")
    if isinstance(tone, Mapping):
        primary = _s(tone.get("primary"))
        if primary:
            voice["tone"] = primary
        anti = _s(tone.get("anti_tone"))
        if anti:
            voice["anti_tone"] = anti

    # Platform specifics for the current channel (if known).
    ch = channel.strip().lower() if channel else ""
    plat = profile.get("platform_specifics")
    if ch and isinstance(plat, Mapping):
        spec = plat.get(ch)
        if isinstance(spec, Mapping):
            voice["platform"] = dict(spec)

    # Voice register samples for this channel (or the closest generic register).
    samples = profile.get("voice_samples")
    if isinstance(samples, Mapping):
        ch_samples: Optional[Sequence] = None
        if ch and ch in samples:
            ch_samples = samples[ch]
        elif "commercial_direct" in samples:
            ch_samples = samples["commercial_direct"]
        if isinstance(ch_samples, (list, tuple)):
            reg = [_s(s) for s in ch_samples if _s(s)]
            if reg:
                voice["register"] = reg[:3]

    return voice


# --------------------------------------------------------------------------- #
# GROUNDING: normalize the grounding block (default approved=False).
# --------------------------------------------------------------------------- #
def _normalize_grounding(
    grounding: Optional[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Normalize the grounding block to a canonical dict. PURE + TOTAL.

    The grounding dict is the approval gate from the content_schedule workflow (mirrors
    the reference commerce app's ContentLibrary approved toggle). Default approved=False until
    an editor approves."""
    if not isinstance(grounding, Mapping):
        return {
            "approved": False,
            "approved_by": "",
            "approved_at": "",
            "confidence": 0.0,
            "sources": [],
        }
    sources = grounding.get("sources")
    srcs: List[str] = [_s(s) for s in (sources if isinstance(sources, (list, tuple)) else []) if _s(s)]
    conf_raw = grounding.get("confidence", 0.0)
    try:
        conf = float(conf_raw)
        conf = max(0.0, min(1.0, conf))
    except (TypeError, ValueError):
        conf = 0.0
    return {
        "approved": bool(grounding.get("approved", False)),
        "approved_by": _s(grounding.get("approved_by")),
        "approved_at": _s(grounding.get("approved_at")),
        "confidence": conf,
        "sources": srcs,
    }


# --------------------------------------------------------------------------- #
# VOICE PROFILE resolution (safe import -- degrade-never if module absent).
# --------------------------------------------------------------------------- #
def _resolve_voice_profile(
    tenant_id: str,
    inputs: Optional[Mapping[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Resolve the tenant voice profile. Priority:
      1. An explicit inputs['voice_profile'] dict.
      2. cex_tenant_voice_profile.load_voice_profile(tenant_id).
      3. None -- no profile -> callers fall back to today's generic behavior.
    TOTAL: any failure -> None (degrade-never)."""
    inp = inputs if isinstance(inputs, Mapping) else {}
    explicit = inp.get("voice_profile")
    if isinstance(explicit, Mapping) and explicit:
        return dict(explicit)
    if not tenant_id:
        return None
    try:
        from cex_tenant_voice_profile import load_voice_profile  # noqa: E402
        return load_voice_profile(tenant_id)
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Section accessors (PURE + TOTAL).
# --------------------------------------------------------------------------- #
def _sections(payload: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    if not isinstance(payload, Mapping):
        return []
    raw = payload.get("output_sections")
    if isinstance(raw, (list, tuple)):
        return [s for s in raw if isinstance(s, Mapping)]
    return []


def _find_section(sections: Sequence[Mapping[str, Any]], title: str) -> Optional[Mapping[str, Any]]:
    want = title.strip().lower()
    for s in sections:
        if str(s.get("title") or "").strip().lower() == want:
            return s
    return None


def _variants(sections: Sequence[Mapping[str, Any]]) -> List[Dict[str, str]]:
    """Extract the ad variants from the Variantes table as [{hook, corpo, cta}, ...].

    Column indices are resolved by HEADER NAME (robust to reordering), defaulting to the
    ads.py order (Hook=1, Corpo=2, CTA=3). A row with no hook/corpo/cta is dropped."""
    section = _find_section(sections, _SEC_VARIANTES)
    if section is None:
        return []
    cols = [str(c) for c in (section.get("columns") or [])]
    hi = _col_index(cols, _COL_HOOK, 1)
    ci = _col_index(cols, _COL_CORPO, 2)
    ti = _col_index(cols, _COL_CTA, 3)
    out: List[Dict[str, str]] = []
    for row in section.get("table") or []:
        if not isinstance(row, (list, tuple)):
            continue
        hook = _cell(row, hi)
        corpo = _cell(row, ci)
        cta = _cell(row, ti)
        if hook or corpo or cta:
            out.append({"hook": hook, "corpo": corpo, "cta": cta})
    return out


def _winner_index(sections: Sequence[Mapping[str, Any]], n_variants: int) -> int:
    """The predicted-winner variant index from Teste A/B 'Vencedor previsto' (A=0, B=1).

    Defaults to 0 (variant A). Clamped into range. TOTAL."""
    ab = _find_section(sections, _SEC_AB)
    letter = ""
    if ab is not None:
        for r in ab.get("rows") or []:
            if isinstance(r, Mapping) and str(r.get("label") or "").strip().lower() == _AB_WINNER_LABEL.lower():
                letter = _s(r.get("value")).upper()
                break
    idx = 0
    if letter == "B":
        idx = 1
    if idx >= n_variants or idx < 0:
        idx = 0
    return idx


def _col_index(cols: Sequence[str], name: str, default: int) -> int:
    low = [str(c).strip().lower() for c in cols]
    try:
        return low.index(name.strip().lower())
    except ValueError:
        return default


def _cell(row: Sequence[Any], idx: int) -> str:
    if 0 <= idx < len(row):
        return _s(row[idx])
    return ""


def _s(v: Any) -> str:
    """A trimmed string for a scalar value. None/empty -> "". Collapses inner whitespace."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "Sim" if v else "Nao"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return " ".join(str(v).split())


__all__ = [
    "build_ad_human_html",
    "map_ads_to_ad_data",
    "resolve_brand",
    "attach_grounded_copy",
    "_record_to_canonical_copy_view",
    "_extract_voice_data",
    "_normalize_grounding",
    "_resolve_voice_profile",
]
