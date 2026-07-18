#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI dual-output renderer -- cex_output_contract (mission CAPABILITY_LAYER, Wave 1).

THE dual emitter (plan section 3 + n01 S3, n03 S2, n04 S3). ONE canonical structured
result -> TWO projections that read the SAME object:
  * MD  (the AI view, CANONICAL): YAML frontmatter (the structured fields, safe-dumped)
        + a body of code-fenced sections. This is what the NEXT capability (ads, images)
        reads. Emitted via yaml.safe_dump(..., allow_unicode=False) -- NEVER hand-concat
        (a value containing ':' breaks naive concat; n03 S2.2 flagged the unsafe
        formatter.format_markdown). allow_unicode=False keeps the .md ASCII-safe so it
        survives a cp1252 terminal round-trip (the ascii-only code rule's sibling concern).
  * HTML (the human view, ALWAYS DERIVATIVE): a self-contained report -- tables for the
        price band / competitors / benchmark, provenance badges from `data_sources`, a
        confidence badge + a ready_for_ads banner. HTML is never the source of truth; the
        MD is (n04 S3.1 canonical-source principle).

PURE: NO LLM, NO network, NO DB, NO file IO. ``render(structured_result, contract)`` is a
deterministic projection -- given the same inputs it always yields the same two strings.
Fully type-hinted. ASCII-only per .claude/rules/ascii-code-rule.md.

THE CONTRACT (the ordered field schema -- iterate ONCE, never hardcode per vertical):
  ``contract`` describes which fields exist, their label, type, section, and html widget.
  ``render`` walks the contract's ordered field list EXACTLY ONCE; it has ZERO per-vertical
  branching (no ``if vertical == 'pesquisa_produto'``). A new vertical = a new contract
  dict, not a code edit. The contract shape:
    {
      "schema_id": "<contract id>",          # stamped into frontmatter (schema_version too)
      "title_field": "product_name",         # which field titles the HTML card (optional)
      "summary_field": "recommended_positioning",  # which field is the HTML summary (optional)
      "sections": [ {"id": "pricing", "label": "Pricing"}, ... ],  # ordered section list
      "fields": [
        {"name": "price_band_min", "label": "Preco Minimo R$", "type": "number",
         "section": "pricing", "html_widget": "table_row"},
        ...
      ],
    }
  A field whose ``name`` is absent from ``structured_result`` renders as a blank/omitted
  cell (TOTAL: never raises on a missing field). Extra keys in ``structured_result`` that
  the contract does not mention are still emitted into the frontmatter (so nothing the
  producer computed is silently dropped), but only contract fields drive the HTML widgets.

THE anuncio_open_vars ADAPTER (plan C3 -- the single most important contract reconciliation):
  N01's product-research fields (opportunities / differentiation_angle / gaps) and N02's
  expected ads inputs (usps / competitor_gaps / social_insights) DIFFER. ``render`` bakes a
  stable ``anuncio_open_vars`` block into the frontmatter so the ads agent reads ONE shape
  regardless of which verticals ran (plan S3.3 + C3):
    usps            := merge(opportunities, differentiation_angle)   (dedup, order-preserving)
    competitor_gaps := gaps
    social_insights := the lead_b2c output if present, else {} (V1-only run -> empty -> ads
                       simply emits fewer PAIN_POINT bullets; never fabricated).
  ``build_anuncio_open_vars(structured_result)`` is the public adapter (cex_run_pipeline
  feeds it to the ads capability); ``render`` also embeds it so the persisted MD carries it.

Spec: plan_capability_layer_FINAL_2026-06-18.md (S3 output contract, S3.3 chain mapping,
C3 adapter). Consumed by: _tools/cex_run_pipeline.py (the research->ads driver) +
apps/dashboard_api/main.py (the ?render_format=md|html projection).
"""

from __future__ import annotations

from html import escape as _html_escape
from typing import Any, Dict, List, Mapping, Optional, Sequence

# --------------------------------------------------------------------------- #
# Module constants.
# --------------------------------------------------------------------------- #
SCHEMA_VERSION = "1.0"

# The keys the MD frontmatter MUST always carry (plan S3.1 "Mandatory keys" + the
# anti-hallucination contract: mock:false is checked at 3 redundant layers, n05 S6.3).
# ``render`` guarantees these are present in the frontmatter even if the producer omitted
# them (mock defaults False; confidence_score/ready_for_ads default to a safe floor).
_MANDATORY_FRONTMATTER = ("schema_version", "mock", "confidence_score", "ready_for_ads")

# The UNIVERSAL F7 identity keys the artifact frontmatter MUST carry so the H01/H03 gates
# (cex_sdk.schema.validator) PASS on the RENDERED artifact string -- H01 wants {id, kind,
# title}, H03 wants a description >=10 chars. ``render`` GUARANTEES these in the frontmatter
# (the renderer is the place the frontmatter STRING is assembled, so the guarantee lives HERE
# rather than upstream in any single engine -- so EVERY rendered artifact is gate-clean, not
# just the STORM path). They are METADATA about the artifact (derived from the product name /
# schema_id / kind), NEVER a marketplace claim -- no data is fabricated. A producer-supplied
# value ALWAYS wins (idempotent); these are only the degrade-never fallback.
_IDENTITY_FRONTMATTER = ("id", "kind", "title", "description")


# --------------------------------------------------------------------------- #
# The V1 product-research contract (plan S3.1 -- the 30 fields, grouped). This is an
# INSTANCE of the contract shape, not special-cased code: render() treats it like any
# other contract. A second vertical ships its OWN dict; render() is unchanged.
# --------------------------------------------------------------------------- #
def _f(name: str, label: str, ftype: str, section: str, widget: str) -> Dict[str, str]:
    """Build one ordered contract field descriptor (terse helper, pure)."""
    return {
        "name": name,
        "label": label,
        "type": ftype,
        "section": section,
        "html_widget": widget,
    }


PESQUISA_PRODUTO_CONTRACT: Dict[str, Any] = {
    "schema_id": "pesquisa_produto",
    "title_field": "product_name",
    "summary_field": "recommended_positioning",
    "sections": [
        {"id": "identity", "label": "Identidade e Proveniencia"},
        {"id": "gate", "label": "Portao (ready_for_ads)"},
        {"id": "pricing", "label": "Preco de Mercado"},
        {"id": "competitive", "label": "Inteligencia Competitiva"},
        {"id": "keywords", "label": "Palavras-Chave"},
        {"id": "filing", "label": "Categorias por Marketplace"},
        # Pass 2 (CATALOG/detail) -- spec_extraction_depth_v1 S5. APPEND-ONLY: two new sections
        # join the existing six. The renderer walks the contract once with zero per-vertical
        # branching, so a new section/field is data, not code -- the existing 30 fields + their
        # render output are byte-preserved.
        {"id": "catalog", "label": "Catalogo / Ficha"},
        {"id": "longitudinal", "label": "Serie Temporal"},
    ],
    "fields": [
        # Identity / provenance (9).
        _f("tenant_id", "ID do Tenant", "string", "identity", "kv"),
        _f("run_id", "ID da Pesquisa", "string", "identity", "kv"),
        _f("product_id", "ID do Produto", "string", "identity", "kv"),
        _f("product_name", "Nome do Produto", "string", "identity", "kv"),
        _f("run_timestamp", "Data/Hora", "string", "identity", "kv"),
        _f("data_freshness", "Dado Mais Antigo", "string", "identity", "kv"),
        _f("marketplaces_queried", "Marketplaces Consultados", "list", "identity", "chips"),
        _f("marketplaces_failed", "Marketplaces sem Dado", "list", "identity", "chips"),
        _f("data_sources", "Origem dos Dados", "object", "identity", "provenance"),
        # Gate (2).
        _f("confidence_score", "Pontuacao de Confianca", "number", "gate", "badge"),
        _f("ready_for_ads", "Pronto para Anuncio?", "bool", "gate", "banner"),
        # Pricing (4).
        _f("price_band_min", "Preco Minimo R$", "number", "pricing", "table_row"),
        _f("price_band_max", "Preco Maximo R$", "number", "pricing", "table_row"),
        _f("price_avg", "Preco Medio R$", "number", "pricing", "table_row"),
        _f("sweet_spot_price", "Preco Recomendado R$", "number", "pricing", "table_row"),
        # Competitive (8).
        _f("top_competitor_name", "Principal Concorrente", "string", "competitive", "table_row"),
        _f("top_competitor_rating", "Avaliacao do Lider", "number", "competitive", "table_row"),
        _f("top_competitor_reviews", "Reviews do Lider", "number", "competitive", "table_row"),
        _f("competitors_count", "Concorrentes Mapeados", "number", "competitive", "table_row"),
        _f("gaps", "Lacunas do Mercado", "list", "competitive", "bullets"),
        _f("opportunities", "Oportunidades", "list", "competitive", "bullets"),
        _f("differentiation_angle", "Angulo de Diferenciacao", "string", "competitive", "kv"),
        _f("recommended_positioning", "Posicionamento", "string", "competitive", "kv"),
        # Keywords (6).
        _f("head_terms", "Palavras-Chave Principais", "list", "keywords", "chips"),
        _f("longtails", "Termos de Cauda Longa", "list", "keywords", "chips"),
        _f("synonyms", "Sinonimos", "list", "keywords", "chips"),
        _f("seo_inbound", "Keywords Inbound", "list", "keywords", "chips"),
        _f("seo_outbound", "Keywords para Ads", "list", "keywords", "chips"),
        _f("negative_keywords", "Palavras Negativas", "list", "keywords", "chips"),
        # Filing (1).
        _f("category_paths", "Categorias por Marketplace", "object", "filing", "provenance"),
        # --- Pass 2 CATALOG/detail (spec S5). APPEND-ONLY -- the 30 fields above are untouched. ---
        # Catalog / ficha (W1 + W2): buy-box, sellers, sold, listing age, logistic, variations,
        # attributes, seller reputation. Each is honest-null when the ML lane could not capture it.
        _f("catalog_product_id", "ID de Catalogo", "string", "catalog", "kv"),
        _f("buy_box_winner", "Vencedor da Buy-Box", "string", "catalog", "kv"),
        _f("buy_box_status", "Status na Buy-Box", "string", "catalog", "kv"),
        _f("num_sellers", "No. de Vendedores", "number", "catalog", "table_row"),
        _f("sold_exact", "Vendidos (exato)", "number", "catalog", "table_row"),
        _f("sold_bucket", "Vendidos (faixa)", "string", "catalog", "table_row"),
        _f("available_quantity", "Estoque (faixa)", "string", "catalog", "table_row"),
        _f("date_created", "Data de Criacao do Anuncio", "string", "catalog", "kv"),
        _f("listing_age_days", "Idade do Anuncio (dias)", "number", "catalog", "table_row"),
        _f("logistic_type", "Logistica (FULL/flex)", "string", "catalog", "kv"),
        _f("variations_count", "Variacoes (qtd)", "number", "catalog", "table_row"),
        _f("variations", "Variacoes (cor/tam/SKU)", "list", "catalog", "bullets"),
        _f("attributes_count", "Itens da Ficha Tecnica", "number", "catalog", "table_row"),
        _f("attributes", "Ficha Tecnica", "object", "catalog", "provenance"),
        _f("seller_reputation", "Reputacao do Vendedor", "string", "catalog", "kv"),
        _f("seller_power_status", "MercadoLider", "string", "catalog", "kv"),
        _f("seller_sales_total", "Vendas do Vendedor", "number", "catalog", "table_row"),
        # Pricing precision (W2) -- de/por + discount + parcelas join the EXISTING pricing section.
        _f("price_original", "Preco \"de\" R$", "number", "pricing", "table_row"),
        _f("discount_pct", "Desconto %", "number", "pricing", "table_row"),
        _f("installments", "Parcelas", "string", "pricing", "kv"),
        # --- Pass 3 DEMAND (spec S5 + W3). APPEND-ONLY -- the rows above are untouched. The demand
        # signal is RELATIVE / ranked (top-searched terms), NEVER absolute search volume: the
        # demand_relative marker field renders that qualifier honestly in BOTH projections, and
        # the field label itself says "(relativo)". Populated from cex_meli_trends.fetch_demand;
        # honest-null (empty list) when the category is unknown or /trends is unauthorized.
        _f("demand_trends", "Tendencias de Demanda (relativo)", "list", "longitudinal", "bullets"),
        _f("demand_relative", "Sinal Relativo (nao e volume absoluto)", "bool", "longitudinal", "kv"),
        # Read-time longitudinal metrics (W4 store; honest-null below 2 captures). Declared here so
        # the section renders them once the time-series exists; absent now -> blank (never invented).
        _f("sales_velocity", "Velocidade de Vendas (un/dia)", "number", "longitudinal", "table_row"),
        _f("price_history", "Historico de Preco", "list", "longitudinal", "bullets"),
    ],
}


# --------------------------------------------------------------------------- #
# The ready_for_ads gate (plan S3.1 -- the canonical gate expression). PURE.
# --------------------------------------------------------------------------- #
def compute_ready_for_ads(structured_result: Mapping[str, Any]) -> bool:
    """Evaluate the canonical ready_for_ads gate (plan S3.1):

        confidence_score >= 7.5 AND competitors_count >= 1
        AND price_band_min > 0 AND len(head_terms) >= 1

    PURE + TOTAL: a missing/non-numeric field is treated as failing its clause (fail-closed
    -- a gate can never PASS on absent data). If the producer already set an explicit
    ``ready_for_ads`` bool it is HONORED (the producer's CRITIC may have set it); this
    function is the fallback the renderer uses when the field is absent.
    """
    explicit = structured_result.get("ready_for_ads")
    if isinstance(explicit, bool):
        return explicit
    conf = _as_number(structured_result.get("confidence_score"))
    competitors = _as_number(structured_result.get("competitors_count"))
    price_min = _as_number(structured_result.get("price_band_min"))
    head = structured_result.get("head_terms")
    head_n = len(head) if isinstance(head, (list, tuple)) else 0
    return bool(
        conf is not None and conf >= 7.5
        and competitors is not None and competitors >= 1
        and price_min is not None and price_min > 0
        and head_n >= 1
    )


# --------------------------------------------------------------------------- #
# The anuncio_open_vars adapter (plan C3 -- decouple N01 producer from N02 consumer).
# --------------------------------------------------------------------------- #
def build_anuncio_open_vars(structured_result: Mapping[str, Any]) -> Dict[str, Any]:
    """Map whatever verticals ran into the STABLE shape the ads capability expects (plan C3).

    The ads agent reads THIS block, never the raw vertical fields, so a V1-only run still
    produces valid ads input. Mapping (plan S3.3 + C3):
      usps            := merge(opportunities, differentiation_angle)  (dedup, order-preserving)
      competitor_gaps := gaps
      social_insights := lead_b2c output if present (``social_insights`` already on the
                         result), else {} (V1-only -> empty -> ads emits fewer PAIN_POINT
                         bullets; NEVER fabricated).
      head_terms / longtails / sweet_spot_price / top_competitor_name pass through verbatim
      (they share a name across producer + consumer; n02 S1.3 mapping table).

    PURE + TOTAL: never raises; an absent field becomes an empty list / None.
    """
    opportunities = _as_str_list(structured_result.get("opportunities"))
    angle = structured_result.get("differentiation_angle")
    usps: List[str] = list(opportunities)
    if isinstance(angle, str) and angle.strip():
        usps.append(angle.strip())

    social = structured_result.get("social_insights")
    if isinstance(social, Mapping) and social:
        social_insights: Dict[str, Any] = dict(social)
    else:
        # V1-only (no lead_b2c vertical): an EMPTY object, never fabricated complaints.
        social_insights = {"top_complaints": [], "top_praises": []}

    return {
        "usps": _dedup_preserve(usps),
        "competitor_gaps": _as_str_list(structured_result.get("gaps")),
        "social_insights": social_insights,
        "head_terms": _as_str_list(structured_result.get("head_terms")),
        "longtails": _as_str_list(structured_result.get("longtails")),
        "sweet_spot_price": _as_number(structured_result.get("sweet_spot_price")),
        "top_competitor_name": _as_opt_str(structured_result.get("top_competitor_name")),
    }


# --------------------------------------------------------------------------- #
# THE entry (the dual renderer).
# --------------------------------------------------------------------------- #
def render(
    structured_result: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> Dict[str, str]:
    """Render ONE structured result into {"md": <str>, "html": <str>} (the dual emitter).

    PURE: no LLM, no network, no IO. Walks ``contract['fields']`` EXACTLY ONCE (no
    per-vertical branching). Returns a dict with two keys:
      "md"   -- YAML frontmatter (yaml.safe_dump, allow_unicode=False) + code-fenced
                sections; the AI/canonical projection. Carries the mandatory keys
                (schema_version, mock, confidence_score, ready_for_ads) + anuncio_open_vars.
      "html" -- a self-contained human report (tables + provenance badges + a confidence
                badge + a ready_for_ads banner); always derivative.

    TOTAL: a missing field renders blank; a malformed contract degrades to an empty-but-
    valid pair (never raises on shape).
    """
    if not isinstance(structured_result, Mapping):
        structured_result = {}
    if not isinstance(contract, Mapping):
        contract = {}

    md = _render_md(structured_result, contract)
    html = _render_html(structured_result, contract)
    return {"md": md, "html": html}


# --------------------------------------------------------------------------- #
# MD projection (canonical: safe-YAML frontmatter + code-fenced body).
# --------------------------------------------------------------------------- #
def _render_md(
    structured_result: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> str:
    """The MD projection: yaml.safe_dump frontmatter + a body of code-fenced sections."""
    frontmatter = _build_frontmatter(structured_result, contract)
    fm_text = _safe_yaml_dump(frontmatter)

    parts: List[str] = ["---", fm_text.rstrip("\n"), "---", ""]
    title = _resolve_title(structured_result, contract)
    parts.append("# %s" % (title or contract.get("schema_id") or "Capability Result"))
    parts.append("")

    # One code-fenced block per declared section, in contract order. Code fences keep the
    # body machine-parseable + render verbatim (no markdown surprises in values).
    fields_by_section = _group_fields_by_section(contract)
    for section in _sections(contract):
        sid = section.get("id")
        slabel = section.get("label") or sid
        section_fields = fields_by_section.get(sid, [])
        if not section_fields:
            continue
        parts.append("## %s" % slabel)
        parts.append("")
        parts.append("```")
        for field in section_fields:
            name = field.get("name")
            value = structured_result.get(name)
            parts.append("%s: %s" % (name, _scalar_for_fence(value)))
        parts.append("```")
        parts.append("")
    return "\n".join(parts).rstrip("\n") + "\n"


def _build_frontmatter(
    structured_result: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> Dict[str, Any]:
    """Assemble the frontmatter mapping (the structured fields + mandatory keys + open_vars).

    Order: mandatory keys first (stable, machine-locatable), then every contract field in
    order, then any EXTRA producer keys the contract did not mention (so nothing computed is
    dropped), then the anuncio_open_vars adapter block. yaml.safe_dump sorts deterministically
    when keys() ordering is not preserved; we still build in a sensible order for readability.
    """
    fm: Dict[str, Any] = {}

    # Mandatory keys (plan S3.1) -- always present, safe defaults.
    fm["schema_version"] = str(
        structured_result.get("schema_version") or contract.get("schema_version") or SCHEMA_VERSION
    )
    mock = structured_result.get("mock")
    fm["mock"] = bool(mock) if isinstance(mock, bool) else False
    conf = _as_number(structured_result.get("confidence_score"))
    fm["confidence_score"] = conf if conf is not None else 0.0
    fm["ready_for_ads"] = compute_ready_for_ads(structured_result)
    fm["schema_id"] = str(contract.get("schema_id") or "")

    # Every contract field, in order, coerced to a yaml-safe scalar/list/dict.
    contract_names = set()
    for field in _fields(contract):
        name = field.get("name")
        if not name or name in _MANDATORY_FRONTMATTER:
            continue
        contract_names.add(name)
        fm[name] = _yaml_safe_value(structured_result.get(name))

    # Extra producer keys not in the contract (never silently drop computed data). Skip the
    # adapter/mandatory keys we manage ourselves.
    reserved = contract_names | set(_MANDATORY_FRONTMATTER) | {"schema_id", "anuncio_open_vars"}
    for key, value in structured_result.items():
        k = str(key)
        if k in reserved or k in fm:
            continue
        fm[k] = _yaml_safe_value(value)

    # The downstream adapter (plan C3) -- baked into the canonical MD so the ads capability
    # reads a stable shape from the persisted artifact.
    fm["anuncio_open_vars"] = _yaml_safe_value(build_anuncio_open_vars(structured_result))

    # The UNIVERSAL F7 identity guarantee (H01 {id,kind,title} + H03 description>=10). The
    # renderer is where the frontmatter STRING is assembled, so the guarantee lives HERE -- the
    # gate parses THIS rendered frontmatter, so stamping it here makes EVERY rendered artifact
    # gate-clean (not just the engine path that remembered to stamp the structured dict). A
    # producer/CRITIC-supplied value always wins; this is the degrade-never fallback. No
    # marketplace data is fabricated -- these are metadata about the artifact.
    _ensure_artifact_identity(fm, structured_result, contract)
    return fm


def _ensure_artifact_identity(
    fm: Dict[str, Any],
    structured_result: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> None:
    """Guarantee the H01/H03 frontmatter identity (id, kind, title, description) IN PLACE.

    H01 (cex_sdk.schema.validator) requires {id, kind, title}; H03 requires a description of
    >=10 chars. The renderer assembles the frontmatter the gate parses, so this is the correct
    boundary for the guarantee (the prior fix stamped the structured DICT inside one engine, but
    a render of a dict that lacked these keys -- e.g. another caller, or a path that bypassed the
    stamp -- still produced an H01/H03-failing artifact; the LIVE smoke hit exactly that).

    PURE + TOTAL + idempotent: a value already in ``fm`` (the producer/CRITIC view OR a contract
    field already copied over) is NEVER overwritten. The fallbacks are honest METADATA derived
    from fields already present (the product/title field, the schema_id, the kind) -- no
    marketplace number is invented. ASCII-safe (the slug is ascii-folded; the title/description
    keep the raw label which safe_dump(allow_unicode=False) renders ASCII-only anyway).
    """
    # The human label for this artifact: the contract's title_field value, else product_name.
    title_field = contract.get("title_field") if isinstance(contract, Mapping) else None
    label = ""
    if isinstance(title_field, str):
        label = _as_opt_str(structured_result.get(title_field)) or ""
    if not label:
        label = _as_opt_str(structured_result.get("product_name")) or ""

    schema_id = str(contract.get("schema_id") or "") if isinstance(contract, Mapping) else ""

    # id: an existing id wins; else slug(label) [+ short run_id when present] / the schema_id.
    if not _is_nonempty_str(fm.get("id")):
        slug = _identity_slug(label) or _identity_slug(schema_id) or "artifact"
        run_id = _as_opt_str(structured_result.get("run_id")) or ""
        short = run_id.replace("-", "")[:8]
        fm["id"] = ("%s_%s" % (slug, short)).strip("_") if short else slug

    # kind: an existing kind (producer / contract field) wins; else the schema_id.
    if not _is_nonempty_str(fm.get("kind")):
        kind = _as_opt_str(structured_result.get("kind")) or schema_id or "artifact"
        fm["kind"] = kind

    # title: an existing title wins; else a label-derived title (>=1 char guaranteed).
    if not _is_nonempty_str(fm.get("title")):
        fm["title"] = label or (schema_id.replace("_", " ").title() if schema_id else "Artifact")

    # description: an existing >=10-char description wins; else a fixed descriptive sentence
    # (>=10 chars guaranteed by the fixed prefix); never asserts a price/competitor number.
    if len(_as_opt_str(fm.get("description")) or "") < 10:
        what = label or (schema_id.replace("_", " ") if schema_id else "artefato")
        fm["description"] = "Artefato gerado por CEXAI: %s." % what


# --------------------------------------------------------------------------- #
# HTML projection (derivative: self-contained human report).
# --------------------------------------------------------------------------- #
def _render_html(
    structured_result: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> str:
    """The HTML projection: a self-contained report (inline style, tables, badges)."""
    title = _resolve_title(structured_result, contract)
    summary = _resolve_summary(structured_result, contract)
    conf = _as_number(structured_result.get("confidence_score"))
    ready = compute_ready_for_ads(structured_result)

    out: List[str] = []
    out.append("<section class=\"cex-card\" style=\"font-family:system-ui,Arial,sans-serif;"
               "max-width:880px;margin:0 auto;color:#1a1a1a;\">")
    out.append("<header style=\"border-bottom:2px solid #eee;padding-bottom:8px;\">")
    out.append("<h1 style=\"margin:0;font-size:1.4rem;\">%s</h1>"
               % _html_escape(title or str(contract.get("schema_id") or "Capability Result")))
    out.append("%s" % _confidence_badge_html(conf))
    out.append("%s" % _ready_banner_html(ready))
    out.append("</header>")
    if summary:
        out.append("<p class=\"cex-summary\" style=\"font-size:1rem;color:#333;\">%s</p>"
                   % _html_escape(summary))

    # One block per section, in contract order, dispatching on the field's html_widget.
    fields_by_section = _group_fields_by_section(contract)
    for section in _sections(contract):
        sid = section.get("id")
        section_fields = fields_by_section.get(sid, [])
        if not section_fields:
            continue
        rendered = _render_html_section(section, section_fields, structured_result)
        if rendered:
            out.append(rendered)

    out.append("<footer style=\"margin-top:16px;border-top:1px solid #eee;padding-top:8px;"
               "font-size:.8rem;color:#888;\">Gerado por CEXAI -- relatorio derivado do "
               "artefato canonico (MD). %s</footer>" % _mock_note_html(structured_result))
    out.append("</section>")
    return "\n".join(out)


def _render_html_section(
    section: Mapping[str, Any],
    fields: Sequence[Mapping[str, Any]],
    structured_result: Mapping[str, Any],
) -> str:
    """Render one HTML section block, dispatching each field on its html_widget."""
    out: List[str] = []
    out.append("<div class=\"cex-section\" style=\"margin-top:14px;\">")
    out.append("<h2 style=\"font-size:1.05rem;border-bottom:1px solid #f0f0f0;\">%s</h2>"
               % _html_escape(str(section.get("label") or section.get("id") or "")))

    # Group table_row widgets into ONE table; render other widgets inline.
    table_rows: List[Mapping[str, Any]] = [f for f in fields if f.get("html_widget") == "table_row"]
    if table_rows:
        out.append("<table style=\"border-collapse:collapse;width:100%;font-size:.92rem;\">")
        for field in table_rows:
            label = _html_escape(str(field.get("label") or field.get("name") or ""))
            value = _html_escape(_scalar_for_html(structured_result.get(field.get("name"))))
            out.append("<tr><td style=\"padding:4px 8px;border:1px solid #eee;"
                       "font-weight:600;width:45%%;\">%s</td>"
                       "<td style=\"padding:4px 8px;border:1px solid #eee;\">%s</td></tr>"
                       % (label, value))
        out.append("</table>")

    for field in fields:
        widget = field.get("html_widget")
        if widget == "table_row":
            continue  # already rendered in the grouped table
        rendered = _render_html_widget(field, structured_result)
        if rendered:
            out.append(rendered)
    out.append("</div>")
    return "\n".join(out)


def _render_html_widget(
    field: Mapping[str, Any],
    structured_result: Mapping[str, Any],
) -> str:
    """Render ONE non-table field by its html_widget. PURE + TOTAL (blank on missing)."""
    name = field.get("name")
    label = str(field.get("label") or name or "")
    value = structured_result.get(name)
    widget = field.get("html_widget")

    if widget in ("badge", "banner"):
        return ""  # rendered in the header (confidence badge / ready banner)
    if widget == "kv":
        if value in (None, "", [], {}):
            return ""
        return ("<p style=\"margin:4px 0;\"><strong>%s:</strong> %s</p>"
                % (_html_escape(label), _html_escape(_scalar_for_html(value))))
    if widget == "chips":
        items = _as_str_list(value)
        if not items:
            return ""
        chips = "".join(
            "<span style=\"display:inline-block;background:#eef;border-radius:10px;"
            "padding:2px 8px;margin:2px;font-size:.82rem;\">%s</span>" % _html_escape(i)
            for i in items
        )
        return "<p style=\"margin:4px 0;\"><strong>%s:</strong> %s</p>" % (_html_escape(label), chips)
    if widget == "bullets":
        items = _as_str_list(value)
        if not items:
            return ""
        lis = "".join("<li>%s</li>" % _html_escape(i) for i in items)
        return ("<p style=\"margin:4px 0;\"><strong>%s:</strong></p><ul>%s</ul>"
                % (_html_escape(label), lis))
    if widget == "provenance":
        return _provenance_html(label, value)
    # Default widget: a labeled key/value line.
    if value in (None, "", [], {}):
        return ""
    return ("<p style=\"margin:4px 0;\"><strong>%s:</strong> %s</p>"
            % (_html_escape(label), _html_escape(_scalar_for_html(value))))


def _provenance_html(label: str, value: Any) -> str:
    """Render a per-field provenance/origin object as small badges (n01 S3.1 data_sources)."""
    if not isinstance(value, Mapping) or not value:
        return ""
    badges: List[str] = []
    for k, v in value.items():
        badges.append(
            "<span style=\"display:inline-block;background:#efe;border:1px solid #cdc;"
            "border-radius:6px;padding:1px 6px;margin:2px;font-size:.78rem;\">"
            "%s = %s</span>" % (_html_escape(str(k)), _html_escape(_scalar_for_html(v)))
        )
    return ("<p style=\"margin:4px 0;\"><strong>%s:</strong> %s</p>"
            % (_html_escape(label), "".join(badges)))


def _confidence_badge_html(conf: Optional[float]) -> str:
    """A colored confidence badge (green >=7.5, amber 5-7.4, red <5 / unknown)."""
    if conf is None:
        color, text = "#999", "Confianca: n/d"
    elif conf >= 7.5:
        color, text = "#2e7d32", "Confianca: %.1f/10" % conf
    elif conf >= 5.0:
        color, text = "#b8860b", "Confianca: %.1f/10" % conf
    else:
        color, text = "#c62828", "Confianca: %.1f/10" % conf
    return ("<span style=\"display:inline-block;background:%s;color:#fff;border-radius:6px;"
            "padding:2px 10px;margin-left:8px;font-size:.85rem;\">%s</span>"
            % (color, _html_escape(text)))


def _ready_banner_html(ready: bool) -> str:
    """The ready_for_ads banner (green PASS / amber INCOMPLETE)."""
    if ready:
        return ("<div style=\"background:#e8f5e9;border-left:4px solid #2e7d32;padding:6px 10px;"
                "margin-top:8px;font-size:.9rem;\">Pronto para anuncio.</div>")
    return ("<div style=\"background:#fff8e1;border-left:4px solid #b8860b;padding:6px 10px;"
            "margin-top:8px;font-size:.9rem;\">Pesquisa incompleta -- anuncio bloqueado.</div>")


def _mock_note_html(structured_result: Mapping[str, Any]) -> str:
    """Surface the mock flag honestly (anti-hallucination -- n05 S6.2)."""
    mock = structured_result.get("mock")
    if isinstance(mock, bool) and mock:
        return "<strong style=\"color:#c62828;\">DADOS SIMULADOS (mock=true).</strong>"
    return "Dados reais (mock=false)."


# --------------------------------------------------------------------------- #
# Contract accessors (TOTAL -- always return a usable shape).
# --------------------------------------------------------------------------- #
def _fields(contract: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    fields = contract.get("fields")
    if isinstance(fields, (list, tuple)):
        return [f for f in fields if isinstance(f, Mapping) and f.get("name")]
    return []


def _sections(contract: Mapping[str, Any]) -> List[Mapping[str, Any]]:
    sections = contract.get("sections")
    if isinstance(sections, (list, tuple)) and sections:
        return [s for s in sections if isinstance(s, Mapping) and s.get("id")]
    # No sections declared -> one implicit catch-all so fields still render.
    return [{"id": None, "label": "Fields"}]


def _group_fields_by_section(contract: Mapping[str, Any]) -> Dict[Any, List[Mapping[str, Any]]]:
    grouped: Dict[Any, List[Mapping[str, Any]]] = {}
    for field in _fields(contract):
        grouped.setdefault(field.get("section"), []).append(field)
    return grouped


def _resolve_title(structured_result: Mapping[str, Any], contract: Mapping[str, Any]) -> str:
    name = contract.get("title_field")
    if isinstance(name, str):
        v = structured_result.get(name)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _resolve_summary(structured_result: Mapping[str, Any], contract: Mapping[str, Any]) -> str:
    name = contract.get("summary_field")
    if isinstance(name, str):
        v = structured_result.get(name)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


# --------------------------------------------------------------------------- #
# Value coercion helpers (PURE + TOTAL).
# --------------------------------------------------------------------------- #
def _as_number(value: Any) -> Optional[float]:
    """Coerce to float, or None. A bool is NOT a number here."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip().replace(",", ".")
        try:
            return float(s)
        except ValueError:
            return None
    return None


def _as_str_list(value: Any) -> List[str]:
    """Coerce to a list of non-empty strings ([] otherwise)."""
    if isinstance(value, (list, tuple)):
        out: List[str] = []
        for item in value:
            s = str(item).strip()
            if s:
                out.append(s)
        return out
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _as_opt_str(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _is_nonempty_str(value: Any) -> bool:
    """True iff ``value`` is a non-empty/non-whitespace string (used by the H01 identity
    guarantee to decide whether a producer already supplied id/kind/title)."""
    return isinstance(value, str) and bool(value.strip())


def _identity_slug(text: Any) -> str:
    """An ASCII-only, lowercase, hyphenated slug for the artifact id (H01). TOTAL: a non-string /
    empty / all-non-ascii input -> ''. Mirrors the engine's _slug so ids stay consistent."""
    import re as _re

    s = str(text or "").encode("ascii", "ignore").decode("ascii").lower().strip()
    s = _re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def _dedup_preserve(items: Sequence[str]) -> List[str]:
    """Order-preserving dedup of a string list."""
    seen: set = set()
    out: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _yaml_safe_value(value: Any) -> Any:
    """Project a value into a yaml.safe_dump-able primitive tree (str/num/bool/None/list/dict).

    Lists become lists of safe values; mappings become dicts of safe values; anything exotic
    becomes its str(). PURE + TOTAL -- never raises (so safe_dump never chokes on a custom type).
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_yaml_safe_value(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _yaml_safe_value(v) for k, v in value.items()}
    return str(value)


def _safe_yaml_dump(data: Mapping[str, Any]) -> str:
    """yaml.safe_dump with allow_unicode=False (ASCII-safe) + block style.

    DEGRADE-NEVER: if PyYAML is unavailable, fall back to a minimal, safe, hand-rolled
    key: value emitter (quotes every string) so the renderer still produces valid-ish
    frontmatter rather than crashing. The production path always has PyYAML (the registry +
    runtime already require it); the fallback exists only so this PURE module never hard-fails.
    """
    try:
        import yaml  # optional dep; the runtime already depends on it
        return yaml.safe_dump(
            dict(data),
            default_flow_style=False,
            allow_unicode=False,
            sort_keys=True,
            width=4096,
        )
    except Exception:
        return _fallback_yaml(data)


def _fallback_yaml(data: Mapping[str, Any]) -> str:
    """Minimal safe YAML emitter (used only if PyYAML is absent). Quotes strings, handles
    scalars + one level of list/dict. Not a full YAML serializer -- a degrade-never floor."""
    lines: List[str] = []
    for key in sorted(str(k) for k in data.keys()):
        value = data[key]
        lines.append("%s: %s" % (key, _fallback_scalar(value)))
    return "\n".join(lines) + "\n"


def _fallback_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_fallback_scalar(v) for v in value) + "]"
    if isinstance(value, Mapping):
        inner = ", ".join("%s: %s" % (k, _fallback_scalar(v)) for k, v in value.items())
        return "{" + inner + "}"
    s = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return '"%s"' % s


def _scalar_for_fence(value: Any) -> str:
    """Render a value for a code-fenced MD body line (compact, single line)."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    if isinstance(value, Mapping):
        return ", ".join("%s=%s" % (k, v) for k, v in value.items())
    return " ".join(str(value).split())  # collapse newlines/whitespace


def _scalar_for_html(value: Any) -> str:
    """Render a value for an HTML cell (the caller escapes the result)."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Sim" if value else "Nao"
    if isinstance(value, (int, float)):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    if isinstance(value, Mapping):
        return ", ".join("%s=%s" % (k, v) for k, v in value.items())
    return " ".join(str(value).split())


__all__ = [
    "render",
    "build_anuncio_open_vars",
    "compute_ready_for_ads",
    "PESQUISA_PRODUTO_CONTRACT",
    "SCHEMA_VERSION",
]
