#!/usr/bin/env python3
# -*- coding: ascii -*-
"""leadgen -- N01 lead-gen (scraping) real generator (spec 05_leadgen_suite, Phase 1a).

SLUG = "leadgen" (capability "Captacao de Leads"). Tuple N01 / research_pipeline / P04 /
analyze. It is a research/extraction PIPELINE: find leads around a seed across the
available channels (b2c_marketplace | b2b_cnpj | ugc_social), emit a typed lead LIST + an
honest per-source provenance + a go/no-go verdict.

7 inputs -> 5 output sections (frozen shape from apps/dashboard_web/lib/molds.ts
MOLD_LEADGEN): Resumo (fields), Leads (table), Proveniencia (fields), Fontes (list),
Veredito (fields).

DESIGN (mirrors research.py exactly): the build is PURE -- no network / no LLM / no DB at
build time. The OFFLINE path (no credential) is an HONEST SCAFFOLD: 0 leads found, every
channel honest-blocked/skipped, confianca 0 -- it NEVER fabricates a lead, a name, a
contact, a CNPJ, or a signal. The realistic, plausible MOCK leads live ONLY in the TS
MOLD_LEADGEN (the "dados simulados" demo face); the generator itself stays never-fabricate,
exactly the way research.py's build({}) is honest-empty while MOLD_RESEARCH is rich-mock.

Honesty gate (S1-S5 from _docs/specs/contract/n01_sourcing_rigor.md + spec 4.6):
  * never invent a name / contact / CNPJ / signal -- unknown -> field absent (not a fake);
  * every channel reports ok | blocked | skipped | failed in Proveniencia;
  * degrade-never -- a broken lane is honest-blocked, the others proceed; missing optional
    input -> the mold default;
  * the lead record is forward-compatible (spec sec 5) so the CRM (next vertical) consumes
    the SAME rows: nome/tipo/canal/fonte/contato/sinal/score/status/provenancia.
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

KIND = "research_pipeline"
CAPABILITY = "leadgen"

# The frozen output contract (spec 4.3): the 5 section titles + the Leads columns, in order.
# Exposed as module constants so the REAL orchestrator (cex_leadgen_run) reproduces the SAME
# shape (mold_id="leadgen", these 5 sections, this 7-col Leads table) -- the parity guarantee
# is that BOTH the offline scaffold here AND the real path call _assemble_output below, so the
# shape can never drift between them.
SECTION_TITLES = ("Resumo", "Leads", "Proveniencia", "Fontes", "Veredito")
LEADS_COLUMNS = ["Nome/Handle", "Tipo", "Canal", "Contato", "Sinal", "Confianca", "Status"]

# The v1 channels (spec D2). Order is the canonical display order.
_CHANNEL_ENUM = ("b2c_marketplace", "b2b_cnpj", "ugc_social")
_DEFAULT_CHANNELS = list(_CHANNEL_ENUM)
_DEFAULT_REGION = "Brasil"
_DEFAULT_TARGET = 25
_DEFAULT_MIN_SINAIS = 1  # the N01 honesty floor: >=1 signal/source per lead to count

# The "absent contact" marker (never-fabricate): a lead with no contact a lane actually
# returned carries EXACTLY this in the Contato column. Shared so the real path uses the same.
CONTACT_ABSENT = "--"

# Per-channel default source labels for the OFFLINE honest scaffold + the Fontes list. These
# are the lanes a real run (Phase 1b) would route to -- declared here so the offline path can
# report them honestly as planned-but-not-executed (never as "consulted with data").
_CHANNEL_SOURCES: Dict[str, List[str]] = {
    "b2c_marketplace": ["mercadolivre.com.br", "shopee.com.br"],
    "b2b_cnpj": ["cnpj.gov (Receita/CNPJ)", "ibge (firmografia)"],
    "ugc_social": ["reddit.com", "youtube.com", "instagram.com"],
}

# Human label per channel (display only -- never a fabricated datum).
_CHANNEL_LABEL: Dict[str, str] = {
    "b2c_marketplace": "B2C marketplace",
    "b2b_cnpj": "B2B CNPJ",
    "ugc_social": "UGC social",
}


def _str_list(raw: Any) -> List[str]:
    """Parse a list-or-CSV string into a clean list of non-empty strings. TOTAL."""
    if isinstance(raw, (list, tuple)):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        return [p.strip() for p in raw.replace("\n", ",").split(",") if p.strip()]
    return []


def _resolve_channels(raw: Any, notes: List[str]) -> List[str]:
    """Resolve the requested channels to the valid subset, defaulting to all available.

    DEGRADE-NEVER: an unknown channel is dropped honestly (noted, never run); an empty/missing
    selection defaults to all three. Order follows _CHANNEL_ENUM (canonical display order)."""
    requested = _str_list(raw)
    if not requested:
        return list(_DEFAULT_CHANNELS)
    valid: List[str] = []
    for ch in requested:
        if ch in _CHANNEL_ENUM:
            if ch not in valid:
                valid.append(ch)
        else:
            notes.append("canal '%s' invalido; ignorado (canais validos: %s)"
                         % (ch, ", ".join(_CHANNEL_ENUM)))
    if not valid:
        notes.append("nenhum canal valido informado; usando todos os disponiveis")
        return list(_DEFAULT_CHANNELS)
    # Preserve canonical order regardless of input order.
    return [ch for ch in _CHANNEL_ENUM if ch in valid]


def _channel_sources(channels: List[str]) -> List[str]:
    """The flat list of planned source labels for the selected channels (no duplicates)."""
    seen: List[str] = []
    for ch in channels:
        for src in _CHANNEL_SOURCES.get(ch, []):
            if src not in seen:
                seen.append(src)
    return seen


def _artifact_json(objetivo: str, seed: str, region: str,
                   channels: List[str], gate: str, confianca: float,
                   n_leads: int, n_qualificados: int, kind: str = KIND) -> str:
    """A compact JSON projection for persist/results (ASCII-safe). TOTAL."""
    try:
        return json.dumps({
            "kind": kind,
            "capability": CAPABILITY,
            "objetivo": objetivo,
            "seed": seed,
            "region": region,
            "canais": list(channels),
            "gate": gate,
            "confianca_agregada": confianca,
            "leads_encontrados": n_leads,
            "leads_qualificados": n_qualificados,
        }, ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


# --------------------------------------------------------------------------- #
# SHARED INPUT PARSE + OUTPUT ASSEMBLER (Phase 1b parity seam).
#
# Phase 1a's offline scaffold (build below) AND Phase 1b's real orchestrator
# (cex_leadgen_run.leadgen_run) BOTH go through ``parse_inputs`` + ``assemble_output`` so the
# frozen shape (mold_id="leadgen", the 5 SECTION_TITLES in order, the 7-col LEADS_COLUMNS) is
# IDENTICAL between them -- it is built in ONE place and can never drift. The real path differs
# only in the DATA it feeds in (real lead rows + real per-source statuses); the SHAPE is shared.
# --------------------------------------------------------------------------- #
def parse_inputs(inputs: Mapping[str, Any], notes: List[str]) -> Dict[str, Any]:
    """Parse + default the 7-field input contract (degrade-never). Appends honest notes for any
    coerced field. Returns a dict of the resolved values the assembler needs. NEVER raises."""
    objetivo = str(inputs.get("objetivo") or "").strip() or "perfil de lead a encontrar"
    seed = str(inputs.get("seed") or "").strip() or "termo/CNPJ/marca a pesquisar"
    region = str(inputs.get("regiao") or "").strip() or _DEFAULT_REGION
    qualificacao = str(inputs.get("qualificacao") or "").strip()
    channels = _resolve_channels(inputs.get("canais"), notes)

    try:
        qtd_alvo = int(inputs.get("qtd_alvo") or _DEFAULT_TARGET)
    except (TypeError, ValueError):
        qtd_alvo = _DEFAULT_TARGET
        notes.append("qtd_alvo invalido; usando %d" % _DEFAULT_TARGET)
    if qtd_alvo < 1:
        qtd_alvo = _DEFAULT_TARGET

    try:
        min_sinais = int(inputs.get("min_sinais") or _DEFAULT_MIN_SINAIS)
    except (TypeError, ValueError):
        min_sinais = _DEFAULT_MIN_SINAIS
    if min_sinais < 1:
        min_sinais = _DEFAULT_MIN_SINAIS

    return {
        "objetivo": objetivo,
        "seed": seed,
        "region": region,
        "qualificacao": qualificacao,
        "channels": channels,
        "qtd_alvo": qtd_alvo,
        "min_sinais": min_sinais,
    }


def _lead_row(lead: Mapping[str, Any], canais_label: str) -> List[Any]:
    """Project ONE lead record (spec sec 5) into a FROZEN 7-col Leads row. NEVER-FABRICATE:
    a missing nome -> '(sem nome)'; a missing/empty contato -> CONTACT_ABSENT ('--'); a missing
    sinal/status -> honest defaults. The contato cell is ASSEMBLED ONLY from contact fields a
    lane actually returned (the caller passes a pre-formatted ``contato_display`` string or
    None). PURE + TOTAL."""
    nome = str(lead.get("nome") or "").strip() or "(sem nome)"
    tipo = str(lead.get("tipo") or "").strip() or "--"
    canal = str(lead.get("canal") or "").strip() or canais_label
    contato_display = lead.get("contato_display")
    contato = str(contato_display).strip() if contato_display and str(contato_display).strip() else CONTACT_ABSENT
    sinal = str(lead.get("sinal") or "").strip() or "--"
    try:
        score = round(float(lead.get("score") or 0.0), 2)
    except (TypeError, ValueError):
        score = 0.0
    status = str(lead.get("status") or "").strip() or "novo"
    return [nome, tipo, canal, contato, sinal, score, status]


def assemble_output(
    parsed: Mapping[str, Any],
    *,
    offline: bool,
    lead_rows: List[List[Any]],
    leads_encontrados: int,
    leads_qualificados: int,
    confianca_agregada: float,
    frescor: str,
    n_fontes_ok: int,
    n_fontes_sem_dado: int,
    status_por_canal: str,
    fontes_consultadas_label: str,
    fontes_sem_dado_label: str,
    total_brutos_label: str,
    captura_ts_label: str,
    cobertura_ok: bool,
    fontes_items: List[str],
    notes: List[str],
    inputs: Mapping[str, Any],
    provenance: Optional[List[Dict[str, Any]]] = None,
    run_mode: Optional[str] = None,
    model_used: Optional[str] = None,
    resolved_kind: Optional[str] = None,
) -> dict:
    """Assemble the COMPLETE StructuredOutput (the 5 FROZEN sections in order) from already-
    computed lane outcomes. THE single shape source -- both the offline scaffold and the real
    orchestrator (cex_leadgen_run.leadgen_run) call this, so the mold shape is identical. PURE +
    TOTAL (never raises).

    NEVER-FABRICATE: ``lead_rows`` is whatever the caller computed from REAL lane results (one
    7-col row per lead via _lead_row, or a single honest empty-state row when 0 leads). The
    contato cells are already absent-marked ('--') by the caller for lane-less contacts.

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind a caller already holds,
    embedded verbatim into the artifact JSON self-description instead of the module KIND
    constant. None/blank (the real orchestrator does not thread it today) falls back to KIND --
    byte-identical to before R-333."""
    _kind = effective_kind(resolved_kind, KIND)
    objetivo = str(parsed["objetivo"])
    channels = list(parsed["channels"])
    qtd_alvo = int(parsed["qtd_alvo"])
    min_sinais = int(parsed["min_sinais"])

    canais_label = ", ".join(_CHANNEL_LABEL.get(ch, ch) for ch in channels)
    taxa_qualificacao = (
        "%.0f%%" % (100.0 * leads_qualificados / leads_encontrados)
        if leads_encontrados > 0 else "n/a (0 leads)"
    )

    # Sect 1: Resumo (fields) -- FROZEN shape.
    s_resumo = fields_section(
        "Resumo",
        [
            ("Objetivo", objetivo[:120]),
            ("Canais consultados", canais_label),
            ("Leads encontrados", str(leads_encontrados)),
            ("Leads qualificados", "%d (piso de sinais: %d)" % (leads_qualificados, min_sinais)),
            ("Taxa de qualificacao", taxa_qualificacao),
            ("Confianca agregada", "%.2f -- 0 a 1" % confianca_agregada),
            ("Frescor", frescor),
        ],
        note=brand_title(
            "Sintese da captacao: canais, leads encontrados vs qualificados e confianca", inputs
        ),
    )

    # Sect 2: Leads (table) -- FROZEN shape. NEVER padded to qtd_alvo; honest count.
    s_leads = table_section(
        "Leads",
        list(LEADS_COLUMNS),
        lead_rows,
        note="Um lead por linha (registro forward-compatible com o CRM). Contato NUNCA"
             " fabricado -- ausente quando nao encontrado. Contagem honesta, nunca preenchida"
             " ate qtd_alvo (%d alvo)." % qtd_alvo,
    )

    # Sect 3: Proveniencia (fields) -- S4/S5: per-source honest status.
    s_prov = fields_section(
        "Proveniencia",
        [
            ("Fontes consultadas (%d)" % n_fontes_ok, fontes_consultadas_label),
            ("Fontes sem dado / bloqueadas (%d)" % n_fontes_sem_dado, fontes_sem_dado_label),
            ("Status por canal", status_por_canal),
            ("Total de leads brutos", total_brutos_label),
            ("Data/hora da captacao", captura_ts_label),
        ],
        note="Fontes consultadas vs sem-dado/bloqueado (lacunas honestas). Bloqueado e"
             " anotado, nunca fabricado -- proveniencia e secao, nao rodape.",
    )

    # Sect 4: Fontes (list).
    s_fontes = list_section(
        "Fontes",
        fontes_items,
        note="Fontes especificas por canal, com o recorte (query) de cada consulta.",
    )

    # Sect 5: Veredito (fields) -- S4: named gate with 3 explicit conditions (spec 4.3.5).
    c1_ok = leads_qualificados >= min_sinais        # (a) leads_qualificados >= floor?
    c2_ok = confianca_agregada >= 0.70              # (b) confianca >= 0.70?
    c3_ok = cobertura_ok                            # (c) >=1 canal retornou dado?
    gate_pass = c1_ok and c2_ok and c3_ok
    gate = "PROSSEGUIR" if gate_pass else "REVISAR"

    s_veredito = fields_section(
        "Veredito",
        [
            ("Recomendacao",
             "PROSSEGUIR -- alimentar o CRM (entidade leads)" if gate_pass
             else "REVISAR -- execute com credencial + lanes reais (fase 1b) para captar leads"),
            ("Gate", gate),
            ("Condicao (a) -- leads qualificados",
             "qualificados %d >= piso %d -> %s"
             % (leads_qualificados, min_sinais, "OK" if c1_ok else "FAIL")),
            ("Condicao (b) -- confianca",
             "confianca_agregada %.2f >= 0.70 -> %s"
             % (confianca_agregada, "OK" if c2_ok else "FAIL")),
            ("Condicao (c) -- cobertura",
             "pelo menos 1 canal retornou dado -> %s"
             % ("OK" if c3_ok else "FAIL (nenhum canal com dado)")),
            ("Encadeia para",
             "leadgen -> CRM (entidade leads) / Sales Assistant (gate %s)" % gate),
        ],
        note="Gate explicito para encadear o CRM (entidade leads) + o Sales Assistant."
             " Booleanos visiveis.",
    )

    sections = [s_resumo, s_leads, s_prov, s_fontes, s_veredito]

    # F7: govern (S1-S5).
    score = 1.0
    if offline:
        score -= 0.3
    if not c3_ok:
        score -= 0.2
    passed = gate_pass and score >= 0.7

    return structured_output(
        CAPABILITY,            # mold_id = the SLUG (moldFor("leadgen") -> MOLD_LEADGEN)
        sections,
        passed=passed,
        score=max(0.0, min(1.0, score)),
        artifact=_artifact_json(
            objetivo, str(parsed["seed"]), str(parsed["region"]), channels, gate,
            confianca_agregada, leads_encontrados, leads_qualificados, kind=_kind,
        ),
        real=True,
        notes=notes,
        provenance=provenance,
        run_mode=run_mode,
        model_used=model_used,
    )


@register(CAPABILITY)  # council A4: register by SLUG (the sole, unique generator key)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> dict:
    """OFFLINE / fixtures-scaffold lead-gen generator (N01). Spec 05_leadgen_suite sec 4.

    THE OFFLINE PATH (the degrade-never fallback). The REAL network lanes live in Phase 1b's
    cex_leadgen_run.leadgen_run, which the run path engages for a non-fixtures run; this
    generator stays the offline/fixtures scaffold:
      * credential is None (offline): an HONEST SCAFFOLD -- 0 leads, every channel honest-
        blocked, confianca 0. NEVER fabricates a lead/name/contact/CNPJ/signal.
      * credential present here: Phase 1a behaviour is preserved (honest-empty, lanes are
        'skipped (lanes reais chegam na fase 1b)') -- the REAL lanes run via the cex_run_capability
        leadgen route (cex_leadgen_run), NOT via this generator. If the route falls through to
        the structured-generator seam, this scaffold is the honest, never-fabricate floor.
    Shape frozen to MOLD_LEADGEN (5 sections, in order) via the SHARED ``assemble_output``
    (the SAME assembler the real orchestrator uses -> shape parity). Never raises (degrade-never).

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND."""
    notes: List[str] = []

    # BRAND_MUSTACHE: brand-frame the brief from the per-tenant brand context the run path
    # injects into ``inputs`` (the reserved ``brand_context`` key). ADDITIVE + DEGRADE-NEVER:
    # an un-branded run -> _bnote=None -> no note + neutral text (byte-identical, zero-regression).
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    # F1: parse inputs (degrade-never; default each optional from the mold contract) via the
    # SHARED parser (the SAME the real orchestrator uses).
    parsed = parse_inputs(inputs, notes)
    seed = parsed["seed"]
    region = parsed["region"]
    channels = parsed["channels"]

    offline = (credential is None)
    planned_sources = _channel_sources(channels)

    # S5: honest provenance. OFFLINE -> nothing is consulted; EVERY channel is honest-blocked
    # (sem credencial). With a credential here Phase 1a stays honest-empty (the REAL lanes are
    # the cex_leadgen_run route, not this generator). NEVER a fabricated lead.
    if offline:
        status_por_canal = "; ".join(
            "%s: blocked (sem credencial)" % _CHANNEL_LABEL.get(ch, ch) for ch in channels
        )
    else:
        status_por_canal = "; ".join(
            "%s: skipped (lanes reais chegam na fase 1b)" % _CHANNEL_LABEL.get(ch, ch)
            for ch in channels
        )
        notes.append("credencial presente, mas as lanes reais sao da fase 1b -- "
                     "resultado honesto-vazio (nenhum lead fabricado)")

    if offline:
        notes.append("scaffold offline -- sem credencial; nenhum lead fabricado (never-fabricate)")

    # Sect 2 data: zero real leads -> ONE honest empty-state row (never a fabricated lead).
    canais_label = ", ".join(_CHANNEL_LABEL.get(ch, ch) for ch in channels)
    lead_rows: List[List[Any]] = [[
        "(nenhum lead encontrado)",
        "--",
        canais_label,
        CONTACT_ABSENT,
        "execute com credencial + lanes reais (fase 1b)" if offline
        else "lanes reais chegam na fase 1b",
        0.0,
        "vazio",
    ]]

    # Sect 4 data: the planned sources, each honest-blocked (not executed).
    if planned_sources:
        fontes_items = []
        for ch in channels:
            for src in _CHANNEL_SOURCES.get(ch, []):
                fontes_items.append(
                    "%s [%s] -- recorte: '%s' em %s (BLOQUEADO: %s, nao executado)"
                    % (src, _CHANNEL_LABEL.get(ch, ch), seed[:40], region,
                       "sem credencial" if offline else "lanes reais chegam na fase 1b")
                )
        fontes_items.append(
            "execute com credencial + lanes reais (fase 1b) para popular esta secao"
        )
    else:
        fontes_items = ["nenhuma fonte planejada para os canais selecionados"]

    # F7 notes (preserved from 1a -- the assembler computes the score; we keep the notes here).
    if offline:
        notes.append("offline scaffold -- score reduzido (sem dados reais)")
    notes.append("cobertura: nenhum canal retornou dado (lanes reais: fase 1b)")

    # Per-finding provenance (ADDITIVE; offline -> honest nulls, NEVER-FABRICATE URLs).
    _meth = "offline" if offline else "fetch"
    prov_list = [
        make_provenance(
            finding="Fontes::%s" % src[:60],
            source_url=None,        # NEVER invent a URL offline
            fetched_at=None,
            method=_meth,
            confidence=0.0,
        )
        for src in planned_sources
    ]

    return assemble_output(
        parsed,
        offline=offline,
        lead_rows=lead_rows,
        leads_encontrados=0,
        leads_qualificados=0,
        confianca_agregada=0.0,
        frescor="nao disponivel (offline)" if offline else "nao disponivel (lanes reais: fase 1b)",
        n_fontes_ok=0,
        n_fontes_sem_dado=len(planned_sources),
        status_por_canal=status_por_canal,
        fontes_consultadas_label="nenhuma (offline)" if offline else "nenhuma (lanes reais: fase 1b)",
        fontes_sem_dado_label="; ".join(planned_sources) if planned_sources else "nenhuma planejada",
        total_brutos_label="0 (offline)" if offline else "0 (lanes reais: fase 1b)",
        captura_ts_label="nao executado (offline)" if offline else "nao executado (lanes reais: fase 1b)",
        cobertura_ok=False,
        fontes_items=fontes_items,
        notes=notes,
        inputs=inputs,
        provenance=prov_list,
        resolved_kind=resolved_kind,
    )


__all__ = [
    "KIND",
    "CAPABILITY",
    "SECTION_TITLES",
    "LEADS_COLUMNS",
    "CONTACT_ABSENT",
    "build",
    "parse_inputs",
    "assemble_output",
    "_lead_row",
]
