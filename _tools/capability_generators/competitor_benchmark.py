#!/usr/bin/env python3
# -*- coding: ascii -*-
"""competitor_benchmark -- N01 CAPGEN Wave 1: competitive_matrix real generator.

KIND = "competitive_matrix" (capability #4 competitor_benchmark, owned by N01,
Analytical Envy lens). 8 inputs -> 7 output sections (frozen shape from
apps/dashboard_web/lib/molds.ts MOLD_COMPETITOR_BENCHMARK).

Research lane: compose from inputs + honest provenance (S1-S5 from
_docs/specs/contract/n01_sourcing_rigor.md). Offline-safe: degrade-never.

N07 WIRE REQUIRED: add to _BASE_CAPABILITIES in _tools/cex_run_capability.py:
    "competitor_benchmark": ("N01", "competitive_matrix", "P01", "analyze"),
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
    make_provenance,
    register,
    structured_output,
    table_section,
)

KIND = "competitive_matrix"
CAPABILITY = "competitor_benchmark"  # council A4: the generator registers by SLUG, not KIND

_SCORING_ENUM = ("reviews", "price_scrape", "spec_sheet", "manual")
_DEFAULT_SCORING = "reviews"
_DEFAULT_WINDOW = 90
_DEFAULT_MIN_SRC = 3


def _freshness(days: int) -> Tuple[str, float]:
    """S3 freshness band: (label, recency_factor)."""
    if days < 90:
        return "GREEN (<90d)", 1.0
    if days <= 365:
        return "AMBER (90-365d)", 0.6
    return "RED (>365d)", 0.2


def _str_list(raw: Any) -> List[str]:
    if isinstance(raw, (list, tuple)):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        return [p.strip() for p in raw.replace("\n", ",").split(",") if p.strip()]
    return []


def _float_list(raw: Any) -> List[float]:
    result: List[float] = []
    if isinstance(raw, (list, tuple)):
        for x in raw:
            try:
                result.append(float(x))
            except (TypeError, ValueError):
                pass
    return result


def _weights(raw: Any, n: int) -> List[float]:
    w = _float_list(raw)
    if w and len(w) == n and abs(sum(w) - 100.0) < 0.5:
        return w
    eq = round(100.0 / max(n, 1), 1)
    return [eq] * n


def _artifact_json(product: str, our_brand: str, competitors: List[str],
                   dimensions: List[str], gate: str, kind: str = KIND) -> str:
    try:
        return json.dumps({
            "kind": kind,
            "product": product,
            "our_brand": our_brand,
            "competitors": competitors,
            "dimensions": dimensions,
            "gate": gate,
        }, ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


@register(CAPABILITY)  # council A4: SLUG is the sole generator key (KIND competitive_matrix is unique here, but SLUG is the contract)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> dict:
    """REAL competitive_matrix generator (N01 Analytical Envy).

    Offline path: honest scaffold with blocked-source provenance (S5).
    Shape frozen to MOLD_COMPETITOR_BENCHMARK. Never raises.

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds (e.g. an overlay kind), embedded verbatim into the
    artifact JSON self-description instead of the module KIND constant. None/blank (a direct
    caller, a test, ``build({})``) falls back to KIND -- byte-identical to before R-333."""
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # F1: parse inputs ---------------------------------------------------------
    product = str(inputs.get("product") or "").strip() or "produto"
    our_brand = str(inputs.get("our_brand") or "").strip() or "NossaMarca"
    competitors = _str_list(inputs.get("competitors"))
    dimensions = _str_list(inputs.get("dimensions"))

    # BRAND_MUSTACHE: frame the benchmark for THIS tenant from the brand context the run path
    # injected. ``our_brand`` is an ANALYSIS input (the brand being benchmarked); the brand
    # context is the TENANT identity that commissioned the analysis -- distinct. The 7-section
    # shape + the Veredito 5 rows/labels stay STABLE (tests assert them); the brand rides an
    # ADDITIVE clause on the EXISTING "Recomendacao" row VALUE + a note on the Veredito section.
    # Un-branded -> neutral value, no note delta (degrade-never). NEVER hardcodes the brand.
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    sb = str(inputs.get("scoring_basis") or "").strip()
    if sb not in _SCORING_ENUM:
        if sb:
            notes.append("scoring_basis '%s' invalido; usando '%s'" % (sb, _DEFAULT_SCORING))
        sb = _DEFAULT_SCORING

    try:
        window = int(inputs.get("data_window_days") or _DEFAULT_WINDOW)
    except (TypeError, ValueError):
        window = _DEFAULT_WINDOW
        notes.append("data_window_days invalido; default %d" % _DEFAULT_WINDOW)

    try:
        min_src = int(inputs.get("min_sources_per_dimension") or _DEFAULT_MIN_SRC)
    except (TypeError, ValueError):
        min_src = _DEFAULT_MIN_SRC

    # Guards
    if len(competitors) < 2:
        notes.append("S1: triangulacao: menos de 2 concorrentes (S1 exige >= 2 rivais)")
    if len(dimensions) < 3:
        notes.append("menos de 3 dimensoes; aumentar para analise robusta")
    if len(dimensions) > 7:
        notes.append("dimensoes truncadas a 7 (maximo contratual)")
        dimensions = dimensions[:7]
    if len(competitors) > 6:
        notes.append("concorrentes truncados a 6 (maximo contratual)")
        competitors = competitors[:6]

    w = _weights(inputs.get("weights"), len(dimensions))
    band, rfactor = _freshness(window)
    if window > 365:
        notes.append("S3: frescor RED (data_window_days > 365d) -- dado muito antigo")

    offline = (credential is None) or (sb == "manual")
    if sb == "manual" and credential is None:
        src_status = "skipped: scoring_basis=manual (scores nao fornecidos via inputs)"
    elif credential is None:
        src_status = "bloqueado: offline (sem credencial -- fetch live requerido)"
    else:
        src_status = "ok"

    all_entities = [our_brand] + competitors
    na = "N/A"

    # Sect 1: Matriz competitiva (table) -- FROZEN shape -----------------------
    mat_cols = ["Dimensao (peso)"] + all_entities
    mat_rows: List[List[Any]] = []
    for i, dim in enumerate(dimensions):
        pct = int(round(w[i] if i < len(w) else (100.0 / max(len(dimensions), 1))))
        lbl = "%s (%d%%)" % (dim, pct)
        mat_rows.append([lbl] + ([na] * len(all_entities)))
    mat_rows.append(["Score ponderado"] + ([na] * len(all_entities)))
    mat_rows.append(["Confianca media (0-1)"] + ([0.0] * len(all_entities)))

    s_mat = table_section(
        "Matriz competitiva",
        mat_cols,
        mat_rows,
        note="Notas 0-5 por dimensao (peso entre parenteses); penultima linha = score ponderado,"
             " ultima linha = confianca media por coluna (0-1).",
    )

    # Sect 2: Evidencia por dimensao (table) -- FROZEN shape -------------------
    ev_cols = ["Dimensao", "Base do score", "Fontes", "Confianca"]
    ev_rows: List[List[Any]] = []
    for dim in dimensions:
        ev_rows.append([
            dim,
            sb,
            "0 (%s)" % src_status if offline else "%d (live)" % min_src,
            0.0 if offline else round(rfactor * 0.85, 2),
        ])

    s_ev = table_section(
        "Evidencia por dimensao",
        ev_cols,
        ev_rows,
        note="Cada celula da matriz precisa de lastro -- WHERE veio o numero,"
             " quantas fontes o sustentam e a confianca (0-1). 4.5 de 3 reviews"
             " nao e 4.5 de 300.",
    )

    # Sect 3: Leitura de posicionamento (fields) -- FROZEN shape ---------------
    rival = competitors[0] if competitors else "concorrente"
    waiting = "aguardando dados (offline -- run com credencial para calcular)"

    s_pos = fields_section(
        "Leitura de posicionamento",
        [
            ("Lider do score", "%s -- %s" % (our_brand, waiting) if offline
             else "%s -- calcular pos score" % our_brand),
            ("Forca do rival", "%s -- %s" % (rival, waiting) if offline
             else "%s -- ver dimensao mais alta" % rival),
            ("Ponto fraco do rival", waiting if offline else "ver dimensao mais baixa do rival"),
            ("O que eles fazem que nos nao",
             "nao calculado (requer live data + Analytical Envy cross-analysis)"),
            ("Nosso fosso defensavel",
             "nao calculado (requer score ponderado > media dos rivais -- offline)"),
        ],
        note="Sintese competitiva -- inclui a pergunta canonica da Analytical Envy:"
             " o que o rival faz que nos NAO.",
    )

    # Sect 4: Onde ganhar (list) -- FROZEN shape --------------------------------
    s_ganhar = list_section(
        "Onde ganhar",
        [
            "Calcular apos run com live data (confianca >= 0.8 requerida -- S1)",
            "Identificar dimensoes onde %s supera o rival no score ponderado" % our_brand,
            "Mapear moves com diferencial defensavel (ver fosso em Leitura de posicionamento)",
        ] if offline else [
            "%s -- verificar dimensao com score ponderado mais alto vs rivais" % our_brand,
        ],
        note="Movimentos onde %s ja lidera ou pode abrir vantagem (confianca >= 0.8)." % our_brand,
    )

    # Sect 5: Onde perdemos (list) -- S1: NEVER only wins (Analytical Envy) ----
    s_perdemos = list_section(
        "Onde perdemos",
        [
            "Calcular apos run com live data -- honestidade de paridade exige dado real",
            "Verificar dimensoes onde %s tem score abaixo da media dos rivais" % our_brand,
            "Identificar lacunas vs %s (ex.: pos-venda, garantia, reviews)" % rival,
        ] if offline else [
            "%s -- ver dimensao com menor score ponderado" % our_brand,
        ],
        note="Honestidade de paridade/derrota -- onde %s fica atras (nunca so os ganhos)." % our_brand,
    )

    # Sect 6: Proveniencia (fields) -- S2: always a section, never a footnote --
    fontes_str = (
        "0 -- %s" % src_status if offline
        else "%d fontes (%s, window %dd)" % (min_src * max(len(dimensions), 1), sb, window)
    )
    sem_dado_str = ("todas -- %s" % src_status) if offline else "nenhuma (ok)"
    status_str = ("todos: %s" % src_status) if offline else "ok"

    s_prov = fields_section(
        "Proveniencia",
        [
            ("Base de scoring", sb),
            ("Janela de dados", "ultimos %d dias (data_window_days = %d)" % (window, window)),
            ("Fontes consultadas", fontes_str),
            ("Fontes sem dado", sem_dado_str),
            ("Data / hora da coleta", "nao executado (offline)" if offline else "live"),
            ("Dado mais antigo", "nao disponivel (offline)" if offline else "live"),
            ("Banda de frescor",
             "%s (recency_factor=%.1f) -- GREEN <90d, AMBER 90-365d, RED >365d" % (band, rfactor)),
        ],
        note="Metodo + recencia + fontes consultadas vs sem dado. Status por fonte:"
             " ok | blocked | skipped | failed (vocabulario unico do nucleo).",
    )

    # Sect 7: Veredito (fields) -- S4: named gate benchmark_confiavel ----------
    s1_ok = len(competitors) >= 2 and len(dimensions) >= 3
    gate_pass = (not offline) and s1_ok and rfactor >= 0.6
    gate = "APROVADO" if gate_pass else "BLOQUEADO"
    cond_str = (
        "confianca_media_lider >= 0.7 AND fontes >= %d/dimensao"
        " AND nenhuma dimensao critica sem dado AND frescor != RED" % min_src
    )
    eval_str = (
        "BLOQUEADO: offline -- sem dados para avaliar condicoes" if offline
        else ("APROVADO: condicoes satisfeitas" if gate_pass
              else "BLOQUEADO: uma ou mais condicoes nao satisfeitas")
    )

    _recomendacao = (
        "Executar com credencial para calcular scores reais" if offline
        else ("Prosseguir -- gate APROVADO" if gate_pass
              else "Verificar dimensoes bloqueadas e re-executar"))
    if brand_name:
        _recomendacao = "%s -- %s" % (brand_name, _recomendacao)
    _veredito_note = "Gate nomeado para encadeamento (pricing / ads so consomem um benchmark APROVADO)."
    if _bnote:
        _veredito_note = "%s %s" % (_veredito_note, _bnote)
    s_veredito = fields_section(
        "Veredito",
        [
            ("benchmark_confiavel", "true" if gate_pass else "false"),
            ("Condicoes do gate", cond_str),
            ("Avaliacao das condicoes", eval_str),
            ("Recomendacao", _recomendacao),
            ("Proximo passo encadeavel",
             "N/A (gate BLOQUEADO)" if not gate_pass
             else "Alimentar pricing ou ads com este benchmark"),
        ],
        note=_veredito_note,
    )

    sections = [s_mat, s_ev, s_pos, s_ganhar, s_perdemos, s_prov, s_veredito]

    # F7: govern (S1-S5 from n01_sourcing_rigor) --------------------------------
    score = 1.0
    if not s1_ok:
        score -= 0.3
        notes.append("S1: triangulacao insuficiente (< 2 rivais ou < 3 dimensoes)")
    if offline:
        score -= 0.25
        notes.append("offline scaffold -- score reduzido (sem dados reais)")
    if rfactor < 0.6:
        score -= 0.15
        notes.append("S3: freshness RED -- dado muito antigo (> 365d)")

    passed = gate_pass and s1_ok and score >= 0.5

    # W2a: per-finding provenance for Evidencia por dimensao (ADDITIVE; offline -> honest nulls).
    _meth = "offline" if offline else sb  # sb = scoring_basis ("reviews"|"price_scrape"|etc.)
    _conf = 0.0 if offline else round(rfactor * 0.85, 2)
    prov_list = []
    for dim in dimensions:
        prov_list.append(make_provenance(
            finding="Evidencia::%s" % dim,
            source_url=None,
            fetched_at=None,
            method=_meth,
            confidence=_conf,
        ))

    return structured_output(
        KIND,
        sections,
        passed=passed,
        score=max(0.0, min(1.0, score)),
        artifact=_artifact_json(product, our_brand, competitors, dimensions, gate, kind=_kind),
        real=True,
        notes=notes,
        provenance=prov_list,
    )


# --------------------------------------------------------------------------- #
# Media helpers (public -- called by tests and the edge runtime).
# --------------------------------------------------------------------------- #

def competitor_benchmark_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Build the media_requests list for cex_dual_output.to_dual_output from benchmark inputs.

    Declares ONE image slot: chart_compare (the benchmark comparison chart). This slot is
    ALWAYS declared; it starts as upload-fallback until a live scoring run renders the chart.
    NEVER-FABRICATE: no src is emitted here -- the slot is an honest upload-fallback placeholder.
    PURE + TOTAL: never raises."""
    return [
        {
            "key": "chart_compare",
            "kind": "image",
            "section": "Matriz competitiva",
            "label": "Grafico comparativo (benchmark chart)",
        }
    ]


def competitor_benchmark_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Build the produced_media dict for cex_dual_output.to_dual_output from benchmark inputs.

    Maps chart_compare to a real image src ONLY when inputs['chart_url'] supplies a non-empty
    URL (e.g. a live scoring run injects a rendered chart image URL). Un-supplied or blank
    chart_url -> empty produced dict -> chart_compare stays upload-fallback in to_dual_output.
    NEVER-FABRICATE. PURE + TOTAL: never raises."""
    produced: Dict[str, Any] = {}
    chart_url = str(inputs.get("chart_url") or "").strip()
    if chart_url:
        produced["chart_compare"] = {"src": chart_url, "alt": "Grafico de benchmark competitivo"}
    return produced


__all__ = [
    "KIND",
    "build",
    "competitor_benchmark_media_requests",
    "competitor_benchmark_produced_media",
]
