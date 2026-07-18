#!/usr/bin/env python3
# -*- coding: ascii -*-
"""docs -- structured product documentation generator [knowledge_card] (N04 CAPGEN Wave 1).

Registers under "docs" (slug) AND "knowledge_card" (current seam key).
N07 action: update _BASE_CAPABILITIES["docs"] to kind="docs" in cex_run_capability.py
to avoid kind-collision with N01 research generator (also knowledge_card).
5 inputs -> 6 sections: Resumo / Passos / Manutencao / Troubleshooting / Fontes / RAG-readiness.
LLM body scaffold in wave 1; RAG-readiness + Fontes deterministic.
Domain-rigor: n04_rag (Variant A) + n04_grounding + n04_kc_depth.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional

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

KIND = "knowledge_card"   # current seam lookup (N07: change to "docs" in _BASE_CAPABILITIES)
CAPABILITY = "docs"        # slug -- also registered so tests + slug-based lookup work
CONTRACT_VERSION = "1.0.0"
_DATE_MOCK = "2026-06-21"

_AUDIENCE_ENUM = frozenset({"cliente_final", "suporte", "revendedor"})
_FORMAT_ENUM = frozenset({"passo_a_passo", "faq", "referencia"})
_CHUNK_ENUM = frozenset({"passo", "secao", "paragrafo"})

_AUDIENCE_LABEL: Dict[str, str] = {
    "cliente_final": "Tutor/cliente final -- sem conhecimento tecnico previo",
    "suporte": "Equipe de suporte tecnico (nivel 1 e 2)",
    "revendedor": "Revendedor autorizado -- montagem e configuracao inicial",
}

_FORMAT_DESC: Dict[str, str] = {
    "passo_a_passo": "passo_a_passo -- etapas sequenciais numeradas",
    "faq": "faq -- perguntas e respostas agrupadas por tema",
    "referencia": "referencia -- tabela de campos e valores aceitos",
}

_NOT_SCOPE: Dict[str, str] = {
    "passo_a_passo": "Nao e manual de servico tecnico; para reparo avancado consultar o guia do revendedor",
    "faq": "Nao e guia de configuracao avancada; para integradores usar o SDK guide separado",
    "referencia": "Nao e manual de uso final; para uso basico consultar o guia rapido incluso",
}

# Chunk size by chunk_target (n04_rag Variant A)
_CHUNK_SIZE: Dict[str, str] = {
    "passo": "256 tokens (granularidade por passo)",
    "secao": "512 tokens",
    "paragrafo": "384 tokens",
}

# Scaffold steps per format (density-gated per n04_kc_depth rubric)
_STEPS_PASSO_A_PASSO: List[List[Any]] = [
    ["1", "Separe as 3 secoes e a base; confira os 6 parafusos",
     "Superficie plana min 60x60cm; evite carpete (base desliza durante o aperto)"],
    ["2", "Fixe a base reforcada primeiro (chave Allen inclusa)",
     "Aperte em cruz -- 4 parafusos x 2Nm (rosca M6 plastico, quebra acima de 2Nm)"],
    ["3", "Rosqueie as secoes de baixo para cima",
     "Pare ao sentir resistencia; nao force (rosca M6 plastico)"],
    ["4", "Posicione a 50-150cm de janela ou luz natural; evite corredor de passagem",
     "Altura do topo >= altura dos olhos do gato sentado (ref 30-40cm SRD adulto)"],
    ["5", "Aplique catnip no topo na 1a semana",
     "Reaplicar a cada 3 dias; nao usar apos 7 dias (dependencia olfativa nao desejada)"],
]

_STEPS_FAQ: List[List[Any]] = [
    ["1", "Identifique a questao pelo codigo de erro ou sintoma visivel",
     "Codigos: E01 (conexao), E02 (sensor), E03 (motor)"],
    ["2", "Consulte a secao de FAQ do manual na pagina indicada pelo codigo",
     "Manter manual em local acessivel durante o uso"],
    ["3", "Siga as instrucoes na ordem indicada sem pular etapas",
     "Cada passo depende do anterior para funcionar corretamente"],
]

_STEPS_REFERENCIA: List[List[Any]] = [
    ["1", "Localize o campo no painel de configuracao do produto",
     "Campo identificado por etiqueta ou numero de serie"],
    ["2", "Verifique o tipo de dado aceito (inteiro/string/enum)",
     "Consulte a tabela de referencia de campos do manual"],
    ["3", "Aplique o valor dentro da faixa declarada pelo fabricante",
     "Valores fora da faixa sao rejeitados com codigo E04"],
]

_FORMAT_STEPS: Dict[str, List[List[Any]]] = {
    "passo_a_passo": _STEPS_PASSO_A_PASSO,
    "faq": _STEPS_FAQ,
    "referencia": _STEPS_REFERENCIA,
}

_MANUTENCAO_ROWS: List[List[Any]] = [
    ["Limpar superficie e mecanismo externo", "Semanal",
     "Sem residuos, odor ou particulas visiveis"],
    ["Verificar fixacoes e conectores", "Mensal",
     "Nenhuma peca solta; conectores firmes ao toque"],
    ["Inspecionar desgaste de partes moveis", "Trimestral",
     "Sem folga excessiva (tolerancia >1mm = substituir)"],
    ["Substituir componente de consumivel", "~12 meses ou desgaste >30%",
     "Componente em bom estado visual e funcional"],
]

_TROUBLESHOOTING_ITEMS: List[str] = [
    "Produto nao liga -> verificar conexao de energia e fusivel interno (manual sec 3.1)",
    "Barulho incomum -> inspecionar partes moveis; se persistir contatar suporte com codigo de erro",
    "Falha de conectividade -> resetar modulo WiFi (botao reset 5s); confirmar rede 2.4GHz",
    "Peca danificada -> acionar garantia com nota fiscal; nao tentar reparo sem autorizacao tecnica",
]

_DEFAULT_SOURCES: List[str] = [
    "Manual do fabricante (exemplo simulado)",
    "Base de suporte interna (simulado)",
]

_CONF_MAP: List[float] = [0.92, 0.78, 0.61, 0.55]
_REL_MAP: List[str] = ["alta", "media", "baixa", "baixa"]


def _coerce_str(val: Any, default: str) -> str:
    s = str(val).strip() if val is not None else ""
    return s or default


def _coerce_enum(val: Any, allowed: frozenset, default: str) -> str:
    s = str(val).strip() if val is not None else ""
    return s if s in allowed else default


def _coerce_list(val: Any, default: List[str]) -> List[str]:
    if isinstance(val, (list, tuple)):
        out = [str(x).strip() for x in val if str(x).strip()]
        return out if out else list(default)
    if isinstance(val, str) and val.strip():
        parts = val.replace("\n", ",").split(",")
        out = [p.strip() for p in parts if p.strip()]
        return out if out else list(default)
    return list(default)


def _fontes_rows(sources: List[str]) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for i, src in enumerate(sources):
        name = (src if ("exemplo simulado" in src or "(simulado)" in src)
                else "%s (exemplo simulado)" % src)
        conf: float = _CONF_MAP[min(i, len(_CONF_MAP) - 1)]
        rel: str = _REL_MAP[min(i, len(_REL_MAP) - 1)]
        rows.append([name, rel, _DATE_MOCK, conf])
    return rows


def _artifact(topic: str, audience: str, fmt: str, chunk_target: str,
              n_sources: int, passed: bool, kind: str = KIND) -> str:
    obj = {
        "kind": kind,
        "mold_id": CAPABILITY,
        "contract_version": CONTRACT_VERSION,
        "topic": topic,
        "audience": audience,
        "format": fmt,
        "chunk_target": chunk_target,
        "source_count": n_sources,
        "section_count": 6,
        "passed": passed,
    }
    try:
        return json.dumps(obj, ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


# --------------------------------------------------------------------------- #
# Media helpers (public -- called by tests and the edge runtime).
# --------------------------------------------------------------------------- #

def docs_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Build the media_requests list for cex_dual_output.to_dual_output from docs inputs.

    For passo_a_passo format: one fig_N image slot per assembly step (setup diagrams).
    For faq and referencia formats: one fig_0 image slot (product overview or schema).
    PURE + TOTAL: never raises, never fabricates a src."""
    fmt = _coerce_enum(inputs.get("format"), _FORMAT_ENUM, "passo_a_passo")
    steps = _FORMAT_STEPS.get(fmt, _STEPS_PASSO_A_PASSO)
    if fmt == "passo_a_passo":
        requests: List[Dict[str, Any]] = []
        for i in range(len(steps)):
            requests.append({
                "key": "fig_%d" % i,
                "kind": "image",
                "section": "Passos",
                "label": "Diagrama passo %d" % (i + 1),
            })
        return requests
    # faq / referencia: one generic product overview or schema image.
    return [{
        "key": "fig_0",
        "kind": "image",
        "section": None,
        "label": "Imagem do produto ou diagrama geral",
    }]


def docs_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Build the produced_media dict for cex_dual_output.to_dual_output from docs inputs.

    Maps fig_N slots to real image src when inputs['fig_images'] or inputs['step_images']
    supplies a non-empty URL for that index. A dict {fig_0: url, ...} or a list [url0, ...]
    are both accepted. Un-supplied or blank-URL slots stay upload-fallback.
    n_slots is capped to match docs_media_requests for the same format.
    PURE + TOTAL: never raises, never fabricates."""
    fmt = _coerce_enum(inputs.get("format"), _FORMAT_ENUM, "passo_a_passo")
    steps = _FORMAT_STEPS.get(fmt, _STEPS_PASSO_A_PASSO)
    n_slots = len(steps) if fmt == "passo_a_passo" else 1

    fig_imgs = inputs.get("fig_images") or inputs.get("step_images") or {}
    produced: Dict[str, Any] = {}

    if isinstance(fig_imgs, dict):
        for i in range(n_slots):
            key = "fig_%d" % i
            url = str(fig_imgs.get(key) or fig_imgs.get(str(i)) or "").strip()
            if url:
                produced[key] = {"src": url, "alt": "Diagrama %d" % (i + 1)}
    elif isinstance(fig_imgs, (list, tuple)):
        for i, url_raw in enumerate(fig_imgs):
            if i >= n_slots:
                break
            url = str(url_raw or "").strip()
            if url:
                produced["fig_%d" % i] = {"src": url, "alt": "Diagrama %d" % (i + 1)}
    return produced


@register(CAPABILITY)  # council A4: SLUG-only (dropped @register(KIND=knowledge_card) -- it collided
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> "Dict[str, Any]":
    """Produce structured product documentation (docs, knowledge_card).

    DEGRADE-NEVER: scaffold when no credential; RAG-readiness + Fontes always computed.
    F7: n04_kc_depth (Resumo + O que NAO e) + n04_grounding (Fontes float conf) + n04_rag (10 fields).

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND.
    """
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # F1 CONSTRAIN
    topic = _coerce_str(inputs.get("topic"), "Produto (topico nao informado)")
    if not inputs.get("topic"):
        notes.append("topic ausente; usando placeholder -- fornecer topico para conteudo especifico")
    audience = _coerce_enum(inputs.get("audience"), _AUDIENCE_ENUM, "cliente_final")
    fmt = _coerce_enum(inputs.get("format"), _FORMAT_ENUM, "passo_a_passo")
    chunk_target = _coerce_enum(inputs.get("chunk_target"), _CHUNK_ENUM, "secao")
    sources = _coerce_list(inputs.get("sources"), _DEFAULT_SOURCES)

    if credential is not None:
        notes.append("credential presente; LLM body deferred to wave 2 -- usando scaffold")

    # BRAND_MUSTACHE: frame the doc for THIS tenant from the brand context the run path injected.
    # Section TITLE + the row LABELS stay STABLE (tests assert "O que NAO e" etc.); the brand
    # rides an ADDITIVE clause on the EXISTING "TLDR" row VALUE + a brand note appended to the
    # EXISTING section note. Un-branded -> neutral value, no note delta (degrade-never). NEVER
    # hardcodes the brand.
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)
    _tldr = "Documentacao estruturada: %s -- formato %s" % (topic, fmt)
    if brand_name:
        _tldr = "%s -- %s" % (brand_name, _tldr)
    _resumo_note = "Sintese do knowledge card (exemplo simulado)."
    if _bnote:
        _resumo_note = "%s %s" % (_resumo_note, _bnote)

    # F6 PRODUCE -- 6 sections in contract order
    sec_resumo = fields_section(
        "Resumo",
        [
            ("TLDR", _tldr),
            ("Publico", _AUDIENCE_LABEL.get(audience, audience)),
            ("Formato aplicado", _FORMAT_DESC.get(fmt, fmt)),
            ("O que NAO e", _NOT_SCOPE.get(fmt, "Nao e manual de servico avancado")),
        ],
        note=_resumo_note,
        contract_version=CONTRACT_VERSION,
    )

    sec_passos = table_section(
        "Passos",
        ["#", "Passo", "Dica"],
        _FORMAT_STEPS.get(fmt, _STEPS_PASSO_A_PASSO),
        column_types=["string", "string", "string"],
        key_col_index=0,
        note="Etapas ordenadas (scaffold -- gerar via credential LLM em wave 2).",
        contract_version=CONTRACT_VERSION,
    )

    sec_manutencao = table_section(
        "Manutencao",
        ["Tarefa", "Frequencia", "Indicador"],
        _MANUTENCAO_ROWS,
        column_types=["string", "string", "string"],
        key_col_index=0,
        note="Manutencao preventiva recomendada (scaffold).",
        contract_version=CONTRACT_VERSION,
    )

    sec_troubleshooting = list_section(
        "Troubleshooting",
        _TROUBLESHOOTING_ITEMS,
        note="Sintoma -> diagnostico (scaffold).",
        contract_version=CONTRACT_VERSION,
    )

    fontes_rows = _fontes_rows(sources)
    sec_fontes = table_section(
        "Fontes",
        ["Fonte", "Confiabilidade", "Acessado", "Confianca"],
        fontes_rows,
        column_types=["string", "string", "string", "number"],
        key_col_index=0,
        note="Origens consultadas (exemplo simulado).",
        contract_version=CONTRACT_VERSION,
    )

    sec_rag = fields_section(
        "RAG-readiness",
        [
            ("chunk_method", "recursive-markdown (por secao H2)"),
            ("chunk_size", _CHUNK_SIZE.get(chunk_target, "512 tokens")),
            ("chunk_overlap", "64 tokens"),
            ("preserve_metadata", "true -- topico + secao + passo"),
            ("source_type", "file"),
            ("format", "markdown"),
            ("refresh_frequency", "on_update"),
            ("top_k", "5"),
            ("similarity_metric", "cosine"),
            ("hybrid", "dense + sparse (BM25)"),
        ],
        note="Parametros de indexacao e recuperacao -- Variante A (how-to docs).",
        contract_version=CONTRACT_VERSION,
    )

    output_sections = [
        sec_resumo, sec_passos, sec_manutencao,
        sec_troubleshooting, sec_fontes, sec_rag,
    ]

    # F7 GOVERN: n04_kc_depth + n04_grounding + n04_rag
    resumo_ok = bool(
        sec_resumo.get("rows")
        and any(r.get("label") == "O que NAO e" for r in sec_resumo["rows"])
    )
    fontes_ok = bool(
        sec_fontes.get("columns") == ["Fonte", "Confiabilidade", "Acessado", "Confianca"]
        and sec_fontes.get("table")
        and all(isinstance(r[3], float) for r in sec_fontes["table"])
    )
    rag_labels = {r.get("label") for r in sec_rag.get("rows", [])}
    rag_ok = all(k in rag_labels for k in (
        "chunk_method", "top_k", "hybrid", "preserve_metadata",
    ))
    title_ok = [s.get("title") for s in output_sections] == [
        "Resumo", "Passos", "Manutencao", "Troubleshooting", "Fontes", "RAG-readiness",
    ]

    passed = bool(resumo_ok and fontes_ok and rag_ok and title_ok and len(output_sections) == 6)
    score = 0.9 if passed else 0.7

    return structured_output(
        CAPABILITY,
        output_sections,
        passed=passed,
        score=score,
        artifact=_artifact(topic, audience, fmt, chunk_target, len(sources), passed, kind=_kind),
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
# from what build() actually enforces at runtime. Only the CONTAINER shape changes (e.g. a
# 3-col row -> a named dict {step, instruction, tip}) so the generic markdown renderer in
# cex_export_agent.py (_render_domain_contract_body) produces a clean table -- the leaf
# values themselves are never retyped.
#
# HONEST FRAMING (docs.py is a wave-1 scaffold generator -- LLM body generation is deferred
# to wave 2, see build()'s docstring): the enums/labels/scope/chunk-size entries are durable
# domain law (they gate every real run via _coerce_enum/_CHUNK_SIZE regardless of wave), while
# the *_scaffold / default_*_when_unspecified / source_trust_by_rank entries describe the
# DETERMINISTIC fallback content this generator emits today when no credential/LLM is used --
# labelled as such so a consumer never mistakes placeholder text for a live, per-topic
# authored template. _DATE_MOCK (a hardcoded "today" stub stamped on every Fontes row) and
# KIND/CAPABILITY (seam plumbing, not document content) are deliberately NOT included here --
# they are wave-1 implementation details, not domain law.
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law docs.py enforces on every generated docs/knowledge_card artifact
    (Missao A). Returns a structured, JSON-serialisable dict -- never {} for THIS generator
    (docs DOES declare domain law: audience/format/chunk_target enums + their descriptions,
    per-format scope boundaries, RAG chunk sizing, the per-format section scaffold content,
    and the source confidence/reliability-by-rank grounding rule; {} is only the _base.py
    no-op default for a generator with none)."""
    return {
        "contract_version": CONTRACT_VERSION,
        "enums": {
            "audience": sorted(_AUDIENCE_ENUM),
            "format": sorted(_FORMAT_ENUM),
            "chunk_target": sorted(_CHUNK_ENUM),
        },
        "audience_labels": dict(_AUDIENCE_LABEL),
        "format_descriptions": dict(_FORMAT_DESC),
        "out_of_scope_by_format": dict(_NOT_SCOPE),
        "chunk_size_by_chunk_target": dict(_CHUNK_SIZE),
        "step_scaffold_by_format": [
            {"format": fmt, "step": row[0], "instruction": row[1], "tip": row[2]}
            for fmt, rows in _FORMAT_STEPS.items()
            for row in rows
        ],
        "maintenance_schedule_scaffold": [
            {"task": row[0], "frequency": row[1], "indicator": row[2]}
            for row in _MANUTENCAO_ROWS
        ],
        "troubleshooting_scaffold": list(_TROUBLESHOOTING_ITEMS),
        "default_sources_when_unspecified": list(_DEFAULT_SOURCES),
        "source_trust_by_rank": [
            {"rank": i + 1, "confidence": c, "reliability": r}
            for i, (c, r) in enumerate(zip(_CONF_MAP, _REL_MAP))
        ],
    }


__all__ = [
    "KIND",
    "CAPABILITY",
    "CONTRACT_VERSION",
    "build",
    "docs_media_requests",
    "docs_produced_media",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
