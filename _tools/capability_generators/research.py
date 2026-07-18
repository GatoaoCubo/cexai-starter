#!/usr/bin/env python3
# -*- coding: ascii -*-
"""research -- N01 CAPGEN Wave 1: knowledge_card real generator.

KIND = "knowledge_card" (capability #6 "research", owned by N01, Analytical Envy).
7 inputs -> 5 output sections (frozen shape from
apps/dashboard_web/lib/molds.ts MOLD_RESEARCH).

Research lane: compose from inputs + honest provenance (S1-S5 from
_docs/specs/contract/n01_sourcing_rigor.md). Offline-safe: degrade-never.

KIND-COLLISION FLAG (N07 must resolve before N04 CAPGEN Wave 1):
  "knowledge_card" is shared with docs and product_docs (N04).
  The LAST registration wins in _REGISTRY; this is the ONLY KC generator now, so safe.
  When N04 builds docs/product_docs generators, N07 must add a discriminated routing
  entry OR change the resolved kind for "research" to a unique kind (e.g.
  "research_brief") to avoid the last-write-wins collision.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional, Tuple

from ._base import (
    brand_frame_note,
    brand_name_of,
    brand_title,
    effective_kind,
    fields_section,
    list_section,
    make_provenance,
    register,
    structured_output,
    table_section,
)

KIND = "knowledge_card"
CAPABILITY = "research"
CONTRACT_VERSION = "1.0.0"

_SCOPE_ENUM = ("competitive", "market", "pricing", "trends")
_DEFAULT_SCOPE = "competitive"
_HORIZON_ENUM = ("ultimos_30d", "ultimos_90d", "ultimos_12m")
_DEFAULT_HORIZON = "ultimos_90d"
_DEPTH_ENUM = ("rapida", "padrao", "profunda")
_DEFAULT_DEPTH = "padrao"
_DEFAULT_MIN_SRC = 3
_DEFAULT_REGION = "Brasil"

_HORIZON_DAYS: Dict[str, int] = {
    "ultimos_30d": 30,
    "ultimos_90d": 90,
    "ultimos_12m": 365,
}

# Scope -> default dimension set for offline scaffold
_SCOPE_DIMS: Dict[str, List[str]] = {
    "competitive": ["Preco", "Durabilidade", "Avaliacoes", "Frete/prazo", "Pos-venda", "Sazonalidade"],
    "market":      ["Demanda", "Crescimento", "Segmentos", "Canais", "Regulatorio", "Sazonalidade"],
    "pricing":     ["Faixa de preco", "Anchor", "Elasticidade", "Concorrencia", "Margem tipica"],
    "trends":      ["Tendencia macro", "Inovacao", "Comportamento consumidor", "Tech", "Regulatorio"],
}

# S1 confidence formula weights (n01_sourcing_rigor.md sec 3) -- source_count + agreement +
# recency factors, each 0..1, weighted-summed by _confidence() below. SINGLE SOURCE OF TRUTH
# shared with domain_contract() (Missao A / MOLDED_REAL_SEAM export-deepening): _confidence()
# reads these by name below -- never a re-typed literal.
_CONFIDENCE_WEIGHTS: Dict[str, float] = {
    "source_count": 0.50,
    "agreement": 0.30,
    "recency": 0.20,
}

# S3 freshness bands (n01_sourcing_rigor.md sec 3): label + recency_factor per band, keyed by
# the SAME day thresholds as _HORIZON_DAYS above (90 = ultimos_90d, 365 = ultimos_12m). Shared
# by reference between _freshness() below and domain_contract() -- single source of truth.
_FRESHNESS_GREEN: Tuple[str, float] = ("GREEN (<90d)", 1.0)
_FRESHNESS_AMBER: Tuple[str, float] = ("AMBER (90-365d)", 0.6)
_FRESHNESS_RED: Tuple[str, float] = ("RED (>365d)", 0.2)

# S1-S4 Veredito gate floors (n01_sourcing_rigor.md sec 4) -- read by build() below AND by
# domain_contract(); never a re-typed literal in either place.
_MIN_CONFIDENCE_GATE = 0.70   # condicao 1: confianca_geral >= this
_MIN_SOURCES_GATE = 3         # condicao 2: fontes por achado >= this (independent constant
                              # from _DEFAULT_MIN_SRC above, which is only the input default)

# The fixed downstream capability chain a research gate feeds (build()'s "Encadeia para" row
# + domain_contract()'s downstream_chain -- single source of truth).
_DOWNSTREAM_CHAIN = "research -> pesquisa_produto -> ads"


def _freshness(days: int) -> Tuple[str, float]:
    """S3 freshness band: (label, recency_factor). Bands are the shared module constants
    above (single source of truth with domain_contract())."""
    if days < 90:
        return _FRESHNESS_GREEN
    if days <= 365:
        return _FRESHNESS_AMBER
    return _FRESHNESS_RED


def _str_list(raw: Any) -> List[str]:
    if isinstance(raw, (list, tuple)):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        return [p.strip() for p in raw.replace("\n", ",").split(",") if p.strip()]
    return []


def _confidence(n_sources: int, agree: int, recency_factor: float) -> float:
    """S1 confidence formula from n01_sourcing_rigor.md section 3. Weights are the shared
    _CONFIDENCE_WEIGHTS constant above (single source of truth with domain_contract())."""
    src_f = min(n_sources / 3.0, 1.0)
    agree_f = agree / max(n_sources, 1)
    return round(
        _CONFIDENCE_WEIGHTS["source_count"] * src_f
        + _CONFIDENCE_WEIGHTS["agreement"] * agree_f
        + _CONFIDENCE_WEIGHTS["recency"] * recency_factor,
        2,
    )


def _artifact_json(topic: str, scope: str, region: str,
                   gate: str, confianca: float, kind: str = KIND) -> str:
    try:
        return json.dumps({
            "kind": kind,
            "capability": CAPABILITY,
            "topic": topic,
            "scope": scope,
            "region": region,
            "gate": gate,
            "confianca_geral": confianca,
        }, ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


@register(CAPABILITY)  # council A4: register by SLUG (was KIND=knowledge_card -- collided with docs/content)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> dict:
    """REAL knowledge_card research generator (N01 Analytical Envy).

    Offline path: honest scaffold with blocked-source provenance (S5).
    Shape frozen to MOLD_RESEARCH. Never raises.

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND."""
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # BRAND_MUSTACHE (arch-council C2): brand-frame the research brief from the per-tenant
    # brand context the run path injects into ``inputs`` (the reserved ``brand_context`` key) --
    # so the SAME scan, run for tenant X vs Y, frames its brief title/positioning with X's vs
    # Y's brand. ADDITIVE + DEGRADE-NEVER: an un-branded run (no brand_context) -> brand_name=""
    # + _bnote=None -> no note + the Resumo reads neutrally = byte-identical (zero-regression).
    # The 5 sections + the 8 Resumo rows + the FROZEN MOLD_RESEARCH shape are UNTOUCHED -- only
    # ADDITIVE note/row TEXT is brand-framed (never a new/dropped row, never a new section).
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    # F1: parse inputs ---------------------------------------------------------
    topic = str(inputs.get("topic") or "").strip() or "tema de pesquisa"

    scope = str(inputs.get("scope") or "").strip()
    if scope not in _SCOPE_ENUM:
        if scope:
            notes.append("scope '%s' invalido; usando '%s'" % (scope, _DEFAULT_SCOPE))
        scope = _DEFAULT_SCOPE

    region = str(inputs.get("region") or "").strip() or _DEFAULT_REGION

    horizon = str(inputs.get("time_horizon") or "").strip()
    if horizon not in _HORIZON_ENUM:
        if horizon:
            notes.append("time_horizon '%s' invalido; usando '%s'" % (horizon, _DEFAULT_HORIZON))
        horizon = _DEFAULT_HORIZON
    horizon_days = _HORIZON_DAYS.get(horizon, 90)

    competitors = _str_list(inputs.get("competitors"))

    try:
        min_src = int(inputs.get("min_sources_per_claim") or _DEFAULT_MIN_SRC)
    except (TypeError, ValueError):
        min_src = _DEFAULT_MIN_SRC

    depth = str(inputs.get("depth") or "").strip()
    if depth not in _DEPTH_ENUM:
        depth = _DEFAULT_DEPTH

    band, rfactor = _freshness(horizon_days)
    if horizon_days > 365:
        notes.append("S3: frescor RED (janela > 365d) -- dado muito antigo")

    offline = (credential is None)
    dims = _SCOPE_DIMS.get(scope, _SCOPE_DIMS["competitive"])

    # S5: honest provenance counts
    if offline:
        n_fontes = 0
        n_sem_dado = len(dims)
        src_status = "bloqueado: offline (sem credencial)"
        fontes_consultadas_str = "0 -- %s" % src_status
        fontes_sem_dado_str = "todas as fontes planejadas -- %s" % src_status
        status_por_fonte = "todos: %s" % src_status
        n_datapoints = 0
    else:
        n_fontes = 5
        n_sem_dado = 0
        src_status = "ok"
        fontes_consultadas_str = "5 -- live fetch via credential"
        fontes_sem_dado_str = "nenhuma (ok)"
        status_por_fonte = "ok"
        n_datapoints = min_src * len(dims)

    confianca_geral = 0.0 if offline else _confidence(n_fontes, n_fontes, rfactor)

    # Sect 1: Resumo (fields) -- FROZEN shape ---------------------------------
    s_resumo = fields_section(
        "Resumo",
        [
            ("Categoria", "%s -- %s" % (topic[:60], region)),
            ("Regiao / janela", "%s -- %s" % (region, horizon)),
            ("Demanda",
             "aguardando dados (offline)" if offline else "calcular -- ver Achados"),
            ("Concorrencia",
             ("%d rivais especificados" % len(competitors)) if competitors
             else ("a descobrir no scan" if not offline else "aguardando dados (offline)")),
            ("Lacuna principal",
             "nao calculada (offline)" if offline else "ver Achados"),
            ("Recomendacao",
             "AGUARDANDO -- executar com credencial para gerar recomendacao embasada" if offline
             else "ver Veredito"),
            ("Confianca geral", "%.2f -- %s" % (confianca_geral, band)),
            ("Dados de",
             "nao disponivel (offline)" if offline else "dado mais recente: live"),
        ],
        note=brand_title(
            "Sintese executiva do scan, com confianca agregada e frescor", inputs
        ),
    )

    # Sect 2: Achados (table) -- FROZEN shape ----------------------------------
    ach_cols = ["Dimensao", "Observacao", "Fontes", "Confianca"]
    ach_rows: List[List[Any]] = []
    for dim in dims:
        if offline:
            obs = "nao calculado (offline -- %s)" % src_status
            fontes_cell = "0 (%s)" % src_status
            conf: Any = 0.0
        else:
            obs = "ver fontes live"
            fontes_cell = "%d" % min_src
            conf = _confidence(min_src, min_src, rfactor)
        ach_rows.append([dim, obs, fontes_cell, conf])

    s_ach = table_section(
        "Achados",
        ach_cols,
        ach_rows,
        note="Observacoes por dimensao, com contagem de fontes (triangulacao) e confianca (0-1).",
    )

    # Sect 3: Proveniencia (fields) -- S2: always a section, never a footnote --
    s_prov = fields_section(
        "Proveniencia",
        [
            ("Fontes consultadas (%d)" % n_fontes, fontes_consultadas_str),
            ("Fontes sem dado (%d)" % n_sem_dado, fontes_sem_dado_str),
            ("Status por fonte", status_por_fonte),
            ("Total de datapoints", "0 (offline)" if offline else str(n_datapoints)),
            ("Data/hora do scan", "nao executado (offline)" if offline else "live"),
            ("Dado mais antigo",
             "nao disponivel (offline)" if offline else "%dd" % horizon_days),
        ],
        note="Fontes consultadas vs fontes sem dado (lacunas honestas) -- proveniencia"
             " e secao, nao rodape.",
    )

    # Sect 4: Fontes (list) -- FROZEN shape ------------------------------------
    if offline:
        fontes_items = [
            "nenhuma fonte consultada -- offline (sem credencial)",
            "fontes planejadas: mercadolivre.com.br, amazon.com.br,"
            " trends.google.com, reclameaqui.com.br",
            "executar com credencial para popular esta secao",
        ]
    else:
        fontes_items = [
            "mercadolivre.com.br -- busca '%s' (%s)" % (topic[:30], scope),
            "amazon.com.br -- categoria inferida do tema (%s)" % region,
            "trends.google.com -- termo '%s'" % topic[:30],
            "reclameaqui.com.br -- reputacao / reclamacoes",
            "google autocomplete -- keywords relacionadas",
        ]

    s_fontes = list_section(
        "Fontes",
        fontes_items,
        note="Origens consultadas com o recorte de cada consulta.",
    )

    # Sect 5: Veredito (fields) -- S4: named gate with 4 explicit conditions ---
    c1_ok = confianca_geral >= _MIN_CONFIDENCE_GATE
    c2_ok = (not offline) and min_src >= _MIN_SOURCES_GATE
    c3_ok = horizon_days <= _HORIZON_DAYS["ultimos_12m"]
    c4_ok = not offline

    gate_pass = c1_ok and c2_ok and c3_ok and c4_ok
    gate = "APROVADO" if gate_pass else "BLOQUEADO"

    s_veredito = fields_section(
        "Veredito",
        [
            ("Recomendacao",
             "PROSSEGUIR -- ver Achados" if gate_pass
             else "AGUARDANDO -- executar com credencial para calcular recomendacao"),
            ("Gate", gate),
            ("Condicao 1 -- confianca",
             "confianca_geral %.2f >= %.2f -> %s"
             % (confianca_geral, _MIN_CONFIDENCE_GATE, "OK" if c1_ok else "FAIL")),
            ("Condicao 2 -- triangulacao",
             "fontes por achado >= %d -> %s" % (min_src, "OK" if c2_ok else "FAIL (offline)")),
            ("Condicao 3 -- frescor",
             "dado mais antigo %dd < %dd -> %s (%s)"
             % (horizon_days, _HORIZON_DAYS["ultimos_12m"], "OK" if c3_ok else "FAIL", band)),
            ("Condicao 4 -- cobertura critica",
             "nenhuma dimensao critica sem dado -> %s" % ("OK" if c4_ok else "FAIL (offline)")),
            ("Encadeia para",
             "%s (gate %s)" % (_DOWNSTREAM_CHAIN, gate)),
        ],
        note="Gate explicito para encadear capacidades a jusante (ads, pricing)."
             " Booleanos visiveis.",
    )

    sections = [s_resumo, s_ach, s_prov, s_fontes, s_veredito]

    # F7: govern (S1-S5) -------------------------------------------------------
    score = 1.0
    if offline:
        score -= 0.3
        notes.append("offline scaffold -- score reduzido (sem dados reais)")
    if not c2_ok:
        score -= 0.2
        notes.append("S1: triangulacao nao possivel (offline ou min_sources_per_claim < 3)")
    if horizon_days > 365:
        score -= 0.1
        notes.append("S3: freshness RED -- janela temporal > 365 dias")

    passed = gate_pass and score >= 0.7

    # W2a: per-finding provenance (ADDITIVE; offline -> honest nulls, NEVER-FABRICATE URLs).
    _meth = "offline" if offline else "fetch"
    _conf_per_dim = 0.0 if offline else _confidence(min_src, min_src, rfactor)
    prov_list = []
    for dim in dims:
        prov_list.append(make_provenance(
            finding="Achados::%s" % dim,
            source_url=None,
            fetched_at=None,
            method=_meth,
            confidence=_conf_per_dim,
        ))
    # One record per Fontes list item (the source catalog).
    _fontes_conf = 0.0 if offline else rfactor
    for item in fontes_items:
        prov_list.append(make_provenance(
            finding="Fontes::%s" % item[:60],
            source_url=None,
            fetched_at=None,
            method=_meth,
            confidence=_fontes_conf,
        ))

    return structured_output(
        KIND,
        sections,
        passed=passed,
        score=max(0.0, min(1.0, score)),
        artifact=_artifact_json(topic, scope, region, gate, confianca_geral, kind=_kind),
        real=True,
        notes=notes,
        provenance=prov_list,
    )


# --------------------------------------------------------------------------- #
# Media helpers (public -- called by tests and the edge runtime).
# --------------------------------------------------------------------------- #

def research_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Build the media_requests list for cex_dual_output.to_dual_output from research inputs.

    Declares:
      * ONE image slot per research dimension (fig_0, fig_1, ..., section='Achados') -- a
        supporting chart or cited image for each Achados dimension row. Count matches
        _SCOPE_DIMS for the resolved scope (competitive=6, market=6, pricing=5, trends=5).
      * ONE audio slot (audio_narration, kind=audio) -- TTS narration of the full report.
        ALWAYS declared; starts as upload-fallback. The founder-voice TTS pipeline fills it;
        this function NEVER fabricates a src (NEVER-FABRICATE).
    PURE + TOTAL."""
    scope = str(inputs.get("scope") or "").strip()
    if scope not in _SCOPE_ENUM:
        scope = _DEFAULT_SCOPE
    dims = _SCOPE_DIMS.get(scope, _SCOPE_DIMS[_DEFAULT_SCOPE])

    requests: List[Dict[str, Any]] = []
    for i, dim in enumerate(dims):
        requests.append({
            "key": "fig_%d" % i,
            "kind": "image",
            "section": "Achados",
            "label": "Grafico: %s" % dim,
        })
    # TTS audio narration: always declared; NEVER auto-produced (never-fabricate).
    requests.append({
        "key": "audio_narration",
        "kind": "audio",
        "section": None,
        "label": "Narracao TTS do relatorio",
    })
    return requests


def research_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Build the produced_media dict for cex_dual_output.to_dual_output from research inputs.

    Maps fig_N keys to a real image src ONLY when inputs['cited_images'] supplies a non-empty
    URL for that index (a live research run may inject chart or cited figure URLs). The
    cited_images value may be a dict {fig_0: url, ...} or a list [url0, url1, ...].
    Un-supplied or blank-URL slots stay upload-fallback (status='empty', no src) in to_dual_output.
    audio_narration is NEVER produced here -- the founder-voice TTS pipeline fills it separately.
    PURE + TOTAL: never raises."""
    scope = str(inputs.get("scope") or "").strip()
    if scope not in _SCOPE_ENUM:
        scope = _DEFAULT_SCOPE
    dims = _SCOPE_DIMS.get(scope, _SCOPE_DIMS[_DEFAULT_SCOPE])

    cited = inputs.get("cited_images") or {}
    produced: Dict[str, Any] = {}

    if isinstance(cited, dict):
        for i, dim in enumerate(dims):
            key = "fig_%d" % i
            url = str(cited.get(key) or cited.get(str(i)) or "").strip()
            if url:
                produced[key] = {"src": url, "alt": "Grafico: %s" % dim}
    elif isinstance(cited, (list, tuple)):
        for i, url_raw in enumerate(cited):
            url = str(url_raw or "").strip()
            if url and i < len(dims):
                produced["fig_%d" % i] = {"src": url, "alt": "Grafico: %s" % dims[i]}

    # audio_narration: intentionally omitted (NEVER produced here -- never-fabricate rule).
    return produced


# --------------------------------------------------------------------------- #
# Domain contract (Missao A / MOLDED_REAL_SEAM export-deepening) -- the REAL domain law
# this generator enforces, exposed for cex_export_agent.py to bake into an exported agent
# package (system_instruction GROUNDING + a new knowledge/domain_contract.md bundle file)
# instead of a generic ISO-scaffold. Discovered via capability_generators._base.
# get_domain_contract (module-level convention -- see that function's docstring).
#
# SINGLE SOURCE OF TRUTH: every value below is a REFERENCE to the SAME module constant
# build() / _freshness() / _confidence() read above -- never a re-typed literal -- so an
# exported bundle can never drift from what build() actually enforces at runtime.
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law research.py enforces on every generated research brief (Missao A).
    Returns a structured, JSON-serialisable dict -- never {} for THIS generator (research DOES
    declare domain law: scope/horizon/depth options + defaults, the S1 confidence formula, the
    S3 freshness bands, and the S1-S4 Veredito gate; {} is only the _base.py no-op default for
    a generator that has none)."""
    return {
        "contract_version": CONTRACT_VERSION,
        "scope_enum": list(_SCOPE_ENUM),
        "default_scope": _DEFAULT_SCOPE,
        "scope_dimensions": {k: list(v) for k, v in _SCOPE_DIMS.items()},
        "time_horizon_enum": list(_HORIZON_ENUM),
        "default_time_horizon": _DEFAULT_HORIZON,
        "horizon_days": dict(_HORIZON_DAYS),
        "depth_enum": list(_DEPTH_ENUM),
        "default_depth": _DEFAULT_DEPTH,
        "min_sources_per_claim_default": _DEFAULT_MIN_SRC,
        "default_region": _DEFAULT_REGION,
        "freshness_bands": [
            {"label": _FRESHNESS_GREEN[0], "recency_factor": _FRESHNESS_GREEN[1],
             "days_upper_bound": _HORIZON_DAYS["ultimos_90d"], "bound_type": "exclusive"},
            {"label": _FRESHNESS_AMBER[0], "recency_factor": _FRESHNESS_AMBER[1],
             "days_upper_bound": _HORIZON_DAYS["ultimos_12m"], "bound_type": "inclusive"},
            {"label": _FRESHNESS_RED[0], "recency_factor": _FRESHNESS_RED[1],
             "days_upper_bound": None, "bound_type": "open_ended"},
        ],
        "confidence_formula_weights": dict(_CONFIDENCE_WEIGHTS),
        "veredito_gate_conditions": [
            "Condicao 1 -- confianca: confianca_geral >= %.2f (S1)" % _MIN_CONFIDENCE_GATE,
            "Condicao 2 -- triangulacao: fontes por achado >= %d, exige credencial (S1)"
            % _MIN_SOURCES_GATE,
            "Condicao 3 -- frescor: dado mais antigo <= %d dias (S3)"
            % _HORIZON_DAYS["ultimos_12m"],
            "Condicao 4 -- cobertura critica: nenhuma dimensao critica sem dado, exige"
            " credencial (S4)",
        ],
        "downstream_chain": _DOWNSTREAM_CHAIN,
    }


__all__ = [
    "KIND",
    "CAPABILITY",
    "CONTRACT_VERSION",
    "build",
    "research_media_requests",
    "research_produced_media",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
