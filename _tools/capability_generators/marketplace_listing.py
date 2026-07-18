#!/usr/bin/env python3
# -*- coding: ascii -*-
"""marketplace_listing -- N06 CAPGEN G2: G1 product -> Mercado Livre listing (dual-output).

KIND = "marketplace_listing" (capability slug = kind; auto-registered by @register).
Input  = a G1 catalog row (the tenant's products entity) + marketplace=mercado_livre.
Output = a StructuredOutput holding the ML listing in ML's ACTUAL API schema (title,
         category_id, price, condition, pictures[], attributes[], ...) -- ready to POST to
         POST /items (Mercado Livre) or render via cex_dual_output.to_dual_output.

G1->G2 field mapping (canonical; tested in test_entities_config._G2_MAPPING):
  titulo_ml   -> title           (ML listing title, <=60 chars preferred)
  descricao   -> description     (listing body -> description.plain_text)
  categoria_ml-> category_id     (ML official category id, e.g. "MLB1055")
  marca       -> BRAND attribute (injected into attributes[] if not already there)
  condicao    -> condition       (novo->new, usado->used, recondicionado->refurbished)
  preco       -> price           (listing price, float, R$)
  estoque     -> available_quantity (integer, >= 0)
  fotos       -> pictures[]      (comma-sep URL string or JSON array -> [{url:...}])
  atributos   -> attributes[]    (JSON {"key":"value"} -> [{id:key, value_name:value}])
  sku         -> seller_custom_field + SELLER_SKU attribute

MEDIA (for cex_dual_output.to_dual_output):
  listing_media_requests(inputs) -> media_requests arg: one image slot per foto URL
    + a video slot (always declared; empty/upload-fallback by default).
  listing_produced_media(inputs) -> produced_media arg: maps foto_N slots to real src
    when a URL is present; video_demo is NEVER auto-produced (never-fabricate).

NEVER-FABRICATE: a missing field stays an honest empty/default; no fake ML field names.
DEGRADE-NEVER: missing optional input defaults from the contract; never raises.
ASCII-only per .claude/rules/ascii-code-rule.md.
Multi-tenant-safe: no tenant-specific hardcoded data; reads from inputs only.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional, Tuple

from ._base import (
    brand_frame_note,
    brand_name_of,
    effective_kind,
    fields_section,
    list_section,
    register,
    structured_output,
    table_section,
)

KIND = "marketplace_listing"
CONTRACT_VERSION = "1.0.0"

# ML Brazil constant (the official ISO-4217 currency for all ML Brazil listings).
_ML_CURRENCY_ID = "BRL"
# Default listing type for ML Brazil standard catalog listings.
_ML_LISTING_TYPE_DEFAULT = "gold_special"
# ML preferred title length ceiling (ML allows up to 60 for most categories).
_ML_TITLE_MAX_LEN = 60

# G1 condicao -> ML condition (REAL ML values: "new", "used", "refurbished").
_CONDITION_MAP: Dict[str, str] = {
    "novo": "new",
    "new": "new",
    "usado": "used",
    "used": "used",
    "recondicionado": "refurbished",
    "refurbished": "refurbished",
}

# Required ML fields (gates in F7; all must be non-empty/non-zero to publish).
_ML_REQUIRED_KEYS = {
    "title", "category_id", "price", "currency_id",
    "available_quantity", "condition", "listing_type_id",
}

# The ONLY marketplace this generator targets today (unlike ads.py's multi-platform
# _PLATFORM_LIMITS, this generator has no Shopee/Amazon/Magalu code path). Applied when
# the G1 row omits inputs['marketplace'].
_DEFAULT_MARKETPLACE = "mercado_livre"

# Deterministic example shown in the "Atributos" section when the G1 row supplies none --
# a worked FORMAT SAMPLE (never a fabricated product attribute) guiding the seller on the
# expected atributos JSON shape.
_ATRIBUTOS_EXAMPLE_SCAFFOLD = '{"Material": "sisal", "Peso_kg": "1.5"}'

# Deterministic fallback for the internal product label in the "Payload ML" section when
# the G1 row has neither nome/name nor titulo_ml.
_DEFAULT_NOME_INTERNO = "Produto"


# --------------------------------------------------------------------------- #
# Helpers -- pure parsers (TOTAL: never raise, never fabricate).
# --------------------------------------------------------------------------- #

def _parse_fotos(fotos_raw: Any) -> List[str]:
    """Parse the G1 'fotos' field (comma-sep URL string OR JSON array) into a list of
    URL strings. A blank/missing value -> []. NEVER fabricates a URL."""
    raw = str(fotos_raw or "").strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(u).strip() for u in parsed if str(u).strip()]
        except Exception:
            pass
    return [u.strip() for u in raw.split(",") if u.strip()]


def _parse_atributos(atributos_raw: Any) -> List[Tuple[str, str]]:
    """Parse the G1 'atributos' field (JSON {"key":"value"} dict) into a list of
    (id, value_name) tuples for the ML attributes[] array. Missing/invalid JSON -> [].
    NEVER fabricates an attribute value."""
    raw = str(atributos_raw or "").strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return []
        return [
            (str(k).strip(), str(v).strip())
            for k, v in data.items()
            if k and v is not None and str(k).strip() and str(v).strip()
        ]
    except Exception:
        return []


def _condition_for_ml(condicao: str) -> str:
    """Map a G1 condicao value to the ML condition value. Unknown -> 'new' (safe default)."""
    return _CONDITION_MAP.get(str(condicao or "").strip().lower(), "new")


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Coerce val to a float; NaN/Inf -> default. TOTAL."""
    try:
        v = float(val)
        return v if v == v and abs(v) != float("inf") else default
    except Exception:
        return default


def _safe_int(val: Any, default: int = 0) -> int:
    """Coerce val to an int; missing -> default. TOTAL."""
    try:
        return max(0, int(float(val)))
    except Exception:
        return default


# --------------------------------------------------------------------------- #
# Media helpers (public -- called by tests and the edge runtime).
# --------------------------------------------------------------------------- #

def listing_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Build the media_requests list for cex_dual_output.to_dual_output from a G1 input row.

    Each foto URL declared in inputs['fotos'] gets its own image slot (key=foto_N,
    kind=image, section='Fotos'). When no fotos are present, ONE empty hero image slot is
    still declared (the upload-fallback affordance). A video slot (key=video_demo,
    kind=video) is ALWAYS declared -- it starts empty/upload-fallback; the media pipeline
    fills it if it produces a video. NEVER fabricates a slot key or src."""
    picture_urls = _parse_fotos(inputs.get("fotos") or inputs.get("pictures") or "")
    requests: List[Dict[str, Any]] = []
    if picture_urls:
        for i in range(len(picture_urls)):
            requests.append({
                "key": "foto_%d" % i,
                "kind": "image",
                "section": "Fotos",
                "label": "Foto %d" % (i + 1),
            })
    else:
        requests.append({
            "key": "foto_0",
            "kind": "image",
            "section": "Fotos",
            "label": "Imagem principal",
        })
    # Always declare the video slot (upload-fallback until the pipeline produces it).
    requests.append({
        "key": "video_demo",
        "kind": "video",
        "section": None,
        "label": "Video do produto (opcional)",
    })
    return requests


def listing_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Build the produced_media dict for cex_dual_output.to_dual_output from a G1 input row.

    A foto URL that IS present in inputs['fotos'] -> a generated slot (src=url, status='generated').
    The video_demo slot is NEVER produced here (the media pipeline fills it; we never fabricate).
    A missing/blank URL -> that slot stays empty (upload-fallback). PURE + TOTAL."""
    picture_urls = _parse_fotos(inputs.get("fotos") or inputs.get("pictures") or "")
    produced: Dict[str, Any] = {}
    for i, url in enumerate(picture_urls):
        url = url.strip()
        if url:
            produced["foto_%d" % i] = {"src": url, "alt": "Foto %d" % (i + 1)}
    # video_demo: intentionally omitted (NEVER produced here -- never-fabricate rule).
    return produced


# --------------------------------------------------------------------------- #
# The generator (auto-registered as KIND = "marketplace_listing").
# --------------------------------------------------------------------------- #

@register(KIND)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> dict:
    """Build a Mercado Livre listing StructuredOutput from a G1 catalog row.

    Parses G1 fields (titulo_ml / descricao / categoria_ml / marca / condicao /
    preco / estoque / fotos / atributos / sku) into the ML API listing schema and emits
    6 output_sections (Listagem ML / Preco e Estoque / Fotos / Atributos / Descricao /
    Payload ML). The artifact carries the full ml_listing JSON (POST /items payload).

    Designed for cex_dual_output.to_dual_output: call
      to_dual_output("marketplace_listing", struct,
                     media_requests=listing_media_requests(inputs),
                     produced_media=listing_produced_media(inputs))
    to get the HUMAN HTML audiovisual listing + MACHINE .md+YAML (both faces).

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND.
    """
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # F1 CONSTRAIN -- parse G1 inputs (no crash on missing optional fields).
    marketplace = str(inputs.get("marketplace") or _DEFAULT_MARKETPLACE).strip().lower()
    titulo_ml = str(inputs.get("titulo_ml") or inputs.get("title") or "").strip()
    descricao = str(inputs.get("descricao") or inputs.get("description") or "").strip()
    categoria_ml = str(inputs.get("categoria_ml") or inputs.get("category_id") or "").strip()
    marca = str(inputs.get("marca") or inputs.get("brand") or "").strip()
    condicao_raw = str(inputs.get("condicao") or inputs.get("condition") or "novo").strip()
    condicao_ml = _condition_for_ml(condicao_raw)
    preco = _safe_float(inputs.get("preco") or inputs.get("price"), 0.0)
    estoque = _safe_int(inputs.get("estoque") or inputs.get("available_quantity"), 0)
    sku = str(inputs.get("sku") or inputs.get("seller_sku") or "").strip()
    fotos_raw = inputs.get("fotos") or inputs.get("pictures") or ""
    atributos_raw = inputs.get("atributos") or inputs.get("attributes") or ""
    listing_type = str(inputs.get("listing_type_id") or _ML_LISTING_TYPE_DEFAULT).strip()
    nome_interno = str(
        inputs.get("nome") or inputs.get("name") or titulo_ml or _DEFAULT_NOME_INTERNO
    ).strip()

    # F3 INJECT -- derive ML schema fields from the G1 row.
    picture_urls = _parse_fotos(fotos_raw)
    attributes_pairs: List[Tuple[str, str]] = _parse_atributos(atributos_raw)

    # Inject BRAND attribute when marca is present but not already in atributos
    # (ML requires BRAND for most categories; inject it as the first attribute).
    attr_ids_lower = {k.lower() for k, _ in attributes_pairs}
    if marca and "brand" not in attr_ids_lower and "marca" not in attr_ids_lower:
        attributes_pairs = [("BRAND", marca)] + list(attributes_pairs)
        notes.append("BRAND attribute injected from marca (not present in atributos)")

    # Inject SELLER_SKU attribute when sku is present and not already in atributos.
    if sku and "seller_sku" not in attr_ids_lower:
        attributes_pairs = list(attributes_pairs) + [("SELLER_SKU", sku)]
        notes.append("SELLER_SKU attribute injected from sku")

    # Build the publishable ML listing payload (the machine artifact).
    ml_listing: Dict[str, Any] = {
        "title": titulo_ml,
        "category_id": categoria_ml,
        "price": preco,
        "currency_id": _ML_CURRENCY_ID,
        "available_quantity": estoque,
        "condition": condicao_ml,
        "listing_type_id": listing_type,
        "description": {"plain_text": descricao} if descricao else {},
        "pictures": [{"url": u} for u in picture_urls],
        "attributes": [{"id": k, "value_name": v} for k, v in attributes_pairs],
        "seller_custom_field": sku or None,
    }

    # BRAND_MUSTACHE: frame the listing for THIS tenant (the SELLER) from the brand context the
    # run path injected. ``marca`` is the PRODUCT brand attribute (an input -> ML BRAND attr);
    # the brand context is the TENANT seller identity -- distinct. The 6-section shape + every
    # row stays STABLE (tests assert "Listagem ML" + machine_md); the brand rides an ADDITIVE
    # clause on the EXISTING "Marketplace" row VALUE + a note on the "Listagem ML" section.
    # Un-branded -> neutral value, no note delta (degrade-never). NEVER hardcodes the brand.
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)
    _marketplace_val = marketplace
    if brand_name:
        _marketplace_val = "%s (vendedor: %s)" % (marketplace, brand_name)
    _listagem_note = ("Campos principais do anuncio ML. Titulo: max %d chars preferencial."
                      % _ML_TITLE_MAX_LEN)
    if _bnote:
        _listagem_note = "%s %s" % (_listagem_note, _bnote)

    # F6 PRODUCE -- output sections (ML listing shape, human-readable in the dashboard).
    sec1 = fields_section(
        "Listagem ML",
        [
            ("Titulo", titulo_ml or "(sem titulo_ml -- obrigatorio)"),
            ("Marketplace", _marketplace_val),
            ("Categoria ID", categoria_ml or "(sem categoria_ml -- obrigatorio)"),
            ("Condicao ML", condicao_ml),
            ("Tipo de anuncio", listing_type),
            ("Moeda", _ML_CURRENCY_ID),
        ],
        note=_listagem_note,
        contract_version=CONTRACT_VERSION,
    )

    sec2 = fields_section(
        "Preco e Estoque",
        [
            ("Preco (R$)", ("%.2f" % preco) if preco > 0 else "(sem preco -- obrigatorio)"),
            ("Estoque", str(estoque)),
            ("SKU do vendedor", sku or "(sem sku)"),
            ("Marca", marca or "(sem marca -- obrigatorio pelo ML)"),
        ],
        note="Campos financeiros + identidade. preco = preco publico do anuncio.",
        contract_version=CONTRACT_VERSION,
    )

    if picture_urls:
        sec3 = list_section(
            "Fotos",
            picture_urls,
            note="%d foto(s) mapeada(s). Cada URL = pictures[].url no payload ML." % len(picture_urls),
        )
    else:
        sec3 = list_section(
            "Fotos",
            ["(sem fotos -- adicione URLs em fotos ou envie via upload no slot abaixo)"],
            note="Nenhuma foto mapeada. ML exige ao menos 1 imagem para publicar o anuncio.",
        )
        notes.append("[WARN] no photos -- ML requires at least 1 picture to publish")

    if attributes_pairs:
        sec4 = table_section(
            "Atributos",
            ["Atributo (id)", "Valor"],
            [[k, v] for k, v in attributes_pairs],
            column_types=["string", "string"],
            key_col_index=0,
            note="Specs tecnicas + atributos obrigatorios (BRAND, SELLER_SKU) mapeados de G1.",
            contract_version=CONTRACT_VERSION,
        )
    else:
        sec4 = table_section(
            "Atributos",
            ["Atributo (id)", "Valor"],
            [["(sem atributos)", "Adicione em atributos: %s" % _ATRIBUTOS_EXAMPLE_SCAFFOLD]],
            note="Nenhum atributo mapeado. ML pode exigir atributos especificos por categoria.",
        )

    sec5 = fields_section(
        "Descricao",
        [("Descricao completa", descricao or "(sem descricao -- recomendado)")],
        note="Corpo do anuncio. G2 envia como description.plain_text para a API ML.",
        contract_version=CONTRACT_VERSION,
    )

    payload_json = json.dumps(ml_listing, ensure_ascii=True, separators=(",", ":"))
    payload_preview = payload_json[:900] + ("..." if len(payload_json) > 900 else "")
    sec6 = fields_section(
        "Payload ML (pronto para publicar)",
        [
            ("Produto interno", nome_interno),
            ("Fotos mapeadas", str(len(picture_urls))),
            ("Atributos mapeados", str(len(attributes_pairs))),
            ("JSON do anuncio", payload_preview),
        ],
        note="POST este JSON em POST /items para publicar no ML. Preencha titulo_ml e categoria_ml antes.",
        contract_version=CONTRACT_VERSION,
    )

    sections = [sec1, sec2, sec3, sec4, sec5, sec6]

    # F7 GOVERN -- gate: required ML fields must be non-empty.
    score = 1.0
    missing_required: List[str] = []

    if not titulo_ml:
        score -= 0.20
        missing_required.append("titulo_ml->title")
        notes.append("[FAIL] titulo_ml is missing -- required for ML listing")
    elif len(titulo_ml) > _ML_TITLE_MAX_LEN:
        score -= 0.05
        notes.append("[WARN] titulo_ml exceeds %d chars" % _ML_TITLE_MAX_LEN)

    if not categoria_ml:
        score -= 0.15
        missing_required.append("categoria_ml->category_id")
        notes.append("[FAIL] categoria_ml is missing -- required for ML listing")

    if preco <= 0.0:
        score -= 0.15
        missing_required.append("preco->price")
        notes.append("[FAIL] preco is 0 or missing -- required for ML listing")

    if not descricao:
        score -= 0.05
        notes.append("[WARN] descricao missing -- strongly recommended for ML listing")

    if not picture_urls:
        score -= 0.10
        notes.append("[WARN] no photos -- ML requires at least 1 picture to publish")

    if not marca:
        score -= 0.05
        notes.append("[WARN] marca missing -- required by ML for most categories")

    score = max(0.0, score)
    passed = (not bool(missing_required)) and score >= 0.70

    artifact_dict: Dict[str, Any] = {
        "kind": _kind,
        "contract_version": CONTRACT_VERSION,
        "marketplace": marketplace,
        "ml_listing": ml_listing,
        "missing_required": missing_required,
        "photos_count": len(picture_urls),
        "attributes_count": len(attributes_pairs),
    }

    return structured_output(
        KIND,
        sections,
        passed=passed,
        score=score,
        artifact=json.dumps(artifact_dict, ensure_ascii=True),
        real=True,
        notes=notes,
    )


# --------------------------------------------------------------------------- #
# Domain contract (Missao A / MOLDED_REAL_SEAM export-deepening) -- the REAL domain law
# this generator enforces, exposed for cex_export_agent.py to bake into an exported agent
# package (system_instruction GROUNDING + a new knowledge/domain_contract.md bundle file)
# instead of a generic ISO-scaffold. Discovered via capability_generators._base.
# get_domain_contract (module-level convention -- see that function's docstring).
#
# SINGLE SOURCE OF TRUTH: every value below is a REFERENCE to the SAME module constant
# build() reads above -- never a re-typed literal -- so an exported bundle can never drift
# from what build() actually enforces at runtime. _DEFAULT_MARKETPLACE /
# _ATRIBUTOS_EXAMPLE_SCAFFOLD / _DEFAULT_NOME_INTERNO were PROMOTED from inline literals to
# module constants (this same change) specifically so build() and domain_contract() share
# one definition each -- zero behavior change (build()'s output is byte-identical).
#
# HONEST FRAMING (marketplace_listing.py is Mercado-Livre-only -- read before extending):
# this generator has NO Shopee/Amazon/Magalu code path, unlike the 4-marketplace matrix
# documented in env_config_marketplace_specs_anuncio.md (N02's anuncio pipeline -- a
# DIFFERENT generator). Inventing those marketplaces' limits here would be fabrication --
# absent means absent, not "not yet found". _ML_REQUIRED_KEYS is the module's OWN declared
# "ML needs these 7 fields to publish" claim (real Mercado Livre API law); tracing build()'s
# F7 GOVERN block shows it currently hard-blocks ``passed`` on only 3 of the 7 (title,
# category_id, price) -- the other 4 (currency_id, available_quantity, condition,
# listing_type_id) always resolve to a safe default (BRL / 0 / 'new' /
# default_listing_type_id) so they can never independently register as "missing" at gate
# time. Exposed by reference AS DECLARED, with that nuance stated plainly in
# ``required_fields_note`` rather than silently implied.
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law marketplace_listing.py enforces on every generated Mercado Livre
    listing (Missao A). Returns a structured, JSON-serialisable dict -- never {} for THIS
    generator (marketplace_listing DOES declare domain law: the ML currency + title-length
    limit, the condicao->condition vocabulary, the declared required-to-publish field set,
    plus this generator's own deterministic default/scaffold content -- default
    marketplace, default listing type, default product label, and the atributos example
    format; {} is only the _base.py no-op default for a generator with none)."""
    return {
        "contract_version": CONTRACT_VERSION,
        "marketplace_law": {
            "currency_id": _ML_CURRENCY_ID,
            "title_max_len": _ML_TITLE_MAX_LEN,
        },
        "condition_vocabulary": dict(_CONDITION_MAP),
        "required_fields_to_publish": sorted(_ML_REQUIRED_KEYS),
        "required_fields_note": (
            "Mercado Livre's real POST /items payload needs all 7 keys above "
            "non-empty/non-zero to publish. This generator's F7 gate hard-blocks 3 of "
            "them when absent (title, category_id, price); the other 4 (currency_id, "
            "available_quantity, condition, listing_type_id) always resolve to a safe "
            "default so they are never independently missing at gate time."
        ),
        "defaults": {
            "default_marketplace": _DEFAULT_MARKETPLACE,
            "default_listing_type_id": _ML_LISTING_TYPE_DEFAULT,
            "default_nome_interno_when_unspecified": _DEFAULT_NOME_INTERNO,
        },
        "atributos_example_scaffold": _ATRIBUTOS_EXAMPLE_SCAFFOLD,
        "scope_note": (
            "This generator targets Mercado Livre ONLY. It has no Shopee/Amazon/Magalu "
            "code path -- see env_config_marketplace_specs_anuncio.md for those "
            "marketplaces' rules (owned by a different generator, N02's anuncio pipeline)."
        ),
    }


__all__ = [
    "KIND",
    "CONTRACT_VERSION",
    "build",
    "listing_media_requests",
    "listing_produced_media",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
