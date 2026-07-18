#!/usr/bin/env python3
# -*- coding: ascii -*-
"""product_docs -- structured product documentation generator (N04 CAPGEN Wave 1).

Registers under "product_docs" (synthetic kind -- N07 must add to _BASE_CAPABILITIES).
N07 action: add _BASE_CAPABILITIES["product_docs"] = ("N04","product_docs","P01","document")
5 inputs -> 6 sections: Resumo / Setup / Referencia de campos / FAQ / Fontes / RAG-readiness.
LLM body scaffold in wave 1; RAG-readiness + Fontes deterministic.
Domain-rigor: n04_rag (Variant B) + n04_grounding + n04_kc_depth.
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

KIND = "product_docs"   # synthetic -- N07 adds to _BASE_CAPABILITIES
CONTRACT_VERSION = "1.0.0"
_DATE_MOCK = "2026-06-21"

_SECTIONS_ALL = frozenset({"setup", "referencia", "faq"})
_SECTION_LABELS: Dict[str, str] = {
    "setup": "Setup",
    "referencia": "Referencia de campos",
    "faq": "FAQ",
}

_AUDIENCE_LABEL: Dict[str, str] = {
    "cliente_final": "Tutor/cliente final -- sem conhecimento tecnico previo",
    "suporte": "Equipe de suporte tecnico (nivel 1 e 2)",
    "revendedor": "Revendedor autorizado -- instalacao e configuracao",
    "integrador": "Integrador de sistemas -- APIs e extensoes",
}

_NOT_SCOPE_PRODUCT = (
    "Nao e manual de servico tecnico; para desmontagem/reparo avancado "
    "consultar o guia de revendedor ou contatar suporte autorizado"
)

_DEFAULT_SOURCE_REFS: List[str] = [
    "Manual do fabricante v1.0 (exemplo simulado)",
]

# Scaffold data -- generic Alimentador Automatico (automatic pet feeder) theme, a
# tenant-neutral IoT device example (this module is FROZEN_TOOLS_CORE, vendored
# byte-identical into every distilled tenant -- it must never name any ONE real brand).
_SCAFFOLD_SETUP: List[str] = [
    "Encaixe o reservatorio na base ate o clique (toque mecanico confirma o encaixe correto)",
    "Ligue na tomada (5V USB-C) ou insira 3 pilhas tipo D como backup de energia",
    "No app do fabricante, toque em 'Adicionar dispositivo' e escaneie o QR code na base do produto",
    "Conecte ao WiFi 2.4GHz -- 5GHz nao suportado (conexao falha silenciosamente em 5GHz)",
    "Programe os horarios: no app toque '+' para cada refeicao (max 4); slider porcao = 1-10 doses (1 dose aprox 2g)",
]

_SCAFFOLD_REFERENCIA: List[List[Any]] = [
    ["porcao",      "inteiro",           "1-10 doses (1 dose = 2g aprox)",  "2"],
    ["horarios",    "lista (HH:MM)",     "ate 4 entradas",                  "2 (07:00 e 18:00)"],
    ["som_chamada", "bool (on/off)",     "on ou off",                       "on"],
    ["modo_ferias", "bool (on/off)",     "on ou off",                       "off"],
    ["volume_audio","inteiro",           "0-100 (%)",                       "60"],
]

_SCAFFOLD_FAQ: List[str] = [
    "Trava na racao umida? Use apenas racao seca de 5-12mm de diametro -- umida entope o mecanismo",
    "Internet cai durante uso? Porcoes programadas executam offline pelo firmware; perde apenas logs remotos",
    "Mais de 2 gatos brigam pelo produto? Use 1 unidade por 1-2 gatos (3+ gatos = unidades adicionais)",
    "Como limpar? Giro anti-horario no reservatorio; pano umido + detergente neutro; secar antes de reinserir (umidade corroe sensor)",
]

_CONF_MAP: List[float] = [0.95, 0.88, 0.72, 0.60]
_REL_MAP: List[str] = ["alta", "alta", "media", "baixa"]


def _coerce_str(val: Any, default: str) -> str:
    s = str(val).strip() if val is not None else ""
    return s or default


def _coerce_list_of_str(val: Any, default: List[str]) -> List[str]:
    if isinstance(val, (list, tuple)):
        out = [str(x).strip() for x in val if str(x).strip()]
        return out if out else list(default)
    if isinstance(val, str) and val.strip():
        parts = val.replace("\n", ",").split(",")
        out = [p.strip() for p in parts if p.strip()]
        return out if out else list(default)
    return list(default)


def _coerce_sections(val: Any) -> List[str]:
    requested = _coerce_list_of_str(val, list(_SECTIONS_ALL))
    valid = [s for s in requested if s in _SECTIONS_ALL]
    return valid if valid else list(_SECTIONS_ALL)


def _fontes_rows(source_refs: List[str]) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for i, src in enumerate(source_refs):
        name = (src if ("exemplo simulado" in src or "(simulado)" in src)
                else "%s (exemplo simulado)" % src)
        conf: float = _CONF_MAP[min(i, len(_CONF_MAP) - 1)]
        rel: str = _REL_MAP[min(i, len(_REL_MAP) - 1)]
        rows.append([name, rel, _DATE_MOCK, conf])
    return rows


def _artifact(product: str, version: str, audience: str,
              n_sections: int, n_sources: int, passed: bool, kind: str = KIND) -> str:
    obj = {
        "kind": kind,
        "mold_id": KIND,
        "contract_version": CONTRACT_VERSION,
        "product": product,
        "version": version,
        "audience": audience,
        "section_count": n_sections,
        "source_count": n_sources,
        "passed": passed,
    }
    try:
        return json.dumps(obj, ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


# --------------------------------------------------------------------------- #
# Media helpers (public -- called by tests and the edge runtime).
# --------------------------------------------------------------------------- #

def _parse_product_images(raw: Any) -> List[str]:
    """Parse inputs['product_images'] (list or comma-sep string) into a URL list. TOTAL."""
    if isinstance(raw, (list, tuple)):
        return [str(u).strip() for u in raw if str(u).strip()]
    if isinstance(raw, str) and raw.strip():
        return [u.strip() for u in raw.split(",") if u.strip()]
    return []


def product_docs_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Build the media_requests list for cex_dual_output.to_dual_output from product_docs inputs.

    Declares one product_img_N image slot per URL in inputs['product_images'], with a
    minimum of 1 slot (upload-fallback when no images are provided). Every declared slot
    is anchored to the Resumo section (the product overview). PURE + TOTAL: never raises."""
    urls = _parse_product_images(inputs.get("product_images") or "")
    n = max(len(urls), 1)
    return [
        {
            "key": "product_img_%d" % i,
            "kind": "image",
            "section": "Resumo",
            "label": "Imagem do produto %d" % (i + 1),
        }
        for i in range(n)
    ]


def product_docs_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Build the produced_media dict for cex_dual_output.to_dual_output from product_docs inputs.

    Maps product_img_N keys to real image src for each non-blank URL in
    inputs['product_images']. Un-supplied or blank-URL slots stay upload-fallback
    (status='empty', no src) in to_dual_output. PURE + TOTAL: never raises, never fabricates."""
    urls = _parse_product_images(inputs.get("product_images") or "")
    produced: Dict[str, Any] = {}
    for i, url in enumerate(urls):
        if url:
            produced["product_img_%d" % i] = {"src": url, "alt": "Imagem do produto %d" % (i + 1)}
    return produced


@register(KIND)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> "Dict[str, Any]":
    """Produce structured product documentation (product_docs, knowledge_card domain).

    DEGRADE-NEVER: scaffold when no credential; RAG-readiness + Fontes always computed.
    F7: n04_kc_depth (Resumo Produto+Versao+O que NAO e) + n04_grounding (float conf) +
        n04_rag Variant B (chunk_size_prose + chunk_size_table).

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND.
    """
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # F1 CONSTRAIN
    product = _coerce_str(inputs.get("product"), "Produto Exemplo (produto nao informado)")
    if not inputs.get("product"):
        notes.append("product ausente; usando placeholder Produto Exemplo -- fornecer nome do produto")
    version = _coerce_str(inputs.get("version"), "v1.0")
    sections_req = _coerce_sections(inputs.get("sections"))
    audience = _coerce_str(inputs.get("audience"), "cliente_final")
    source_refs = _coerce_list_of_str(inputs.get("source_refs"), _DEFAULT_SOURCE_REFS)

    if credential is not None:
        notes.append("credential presente; LLM body deferred to wave 2 -- usando scaffold")

    # BRAND_MUSTACHE: frame the product doc for THIS tenant from the brand context the run path
    # injected. Section TITLE + row LABELS stay STABLE (tests assert Produto/Versao/O que NAO e);
    # the brand rides an ADDITIVE clause on the EXISTING "TLDR" row VALUE + a brand note appended
    # to the EXISTING section note. Un-branded -> neutral value, no note delta (degrade-never).
    # NEVER hardcodes the brand.
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)
    _tldr = "Documentacao do produto %s versao %s para %s" % (
        product, version, _AUDIENCE_LABEL.get(audience, audience))
    if brand_name:
        _tldr = "%s -- %s" % (brand_name, _tldr)
    _resumo_note = "Sintese do knowledge card de produto (exemplo simulado)."
    if _bnote:
        _resumo_note = "%s %s" % (_resumo_note, _bnote)

    # F6 PRODUCE -- 6 sections in contract order: Resumo -> body -> Fontes -> RAG-readiness
    sec_resumo = fields_section(
        "Resumo",
        [
            ("TLDR", _tldr),
            ("Produto", product),
            ("Versao", version),
            ("Publico", _AUDIENCE_LABEL.get(audience, audience)),
            ("O que NAO e", _NOT_SCOPE_PRODUCT),
        ],
        note=_resumo_note,
        contract_version=CONTRACT_VERSION,
    )

    sec_setup = list_section(
        "Setup",
        _SCAFFOLD_SETUP,
        note="Passos de instalacao em ordem exata (scaffold -- gerar via credential LLM em wave 2).",
        contract_version=CONTRACT_VERSION,
    )

    sec_referencia = table_section(
        "Referencia de campos",
        ["Campo", "Tipo", "Faixa", "Default"],
        _SCAFFOLD_REFERENCIA,
        column_types=["string", "string", "string", "string"],
        key_col_index=0,
        note="Campos configuravies do produto (scaffold).",
        contract_version=CONTRACT_VERSION,
    )

    sec_faq = list_section(
        "FAQ",
        _SCAFFOLD_FAQ,
        note="Perguntas frequentes com resposta fundamentada (scaffold).",
        contract_version=CONTRACT_VERSION,
    )

    fontes_rows = _fontes_rows(source_refs)
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
            ("chunk_size_prose", "512 tokens"),
            ("chunk_size_table", "256 tokens (referencia de campos)"),
            ("chunk_overlap", "64 tokens"),
            ("preserve_metadata", "true -- produto + versao + campo"),
            ("source_type", "file"),
            ("format", "markdown"),
            ("refresh_frequency", "on_change (firmware versao)"),
            ("top_k", "5"),
            ("similarity_metric", "cosine"),
            ("hybrid", "dense + sparse (BM25)"),
        ],
        note="Parametros de indexacao e recuperacao -- Variante B (product_docs, mixed prose+table).",
        contract_version=CONTRACT_VERSION,
    )

    output_sections = [
        sec_resumo, sec_setup, sec_referencia, sec_faq, sec_fontes, sec_rag,
    ]

    # F7 GOVERN: n04_kc_depth + n04_grounding + n04_rag Variant B
    resumo_labels = {r.get("label") for r in sec_resumo.get("rows", [])}
    resumo_ok = bool(
        "O que NAO e" in resumo_labels
        and "Produto" in resumo_labels
        and "Versao" in resumo_labels
    )
    fontes_ok = bool(
        sec_fontes.get("columns") == ["Fonte", "Confiabilidade", "Acessado", "Confianca"]
        and sec_fontes.get("table")
        and all(isinstance(r[3], float) for r in sec_fontes["table"])
    )
    rag_labels = {r.get("label") for r in sec_rag.get("rows", [])}
    rag_ok = all(k in rag_labels for k in (
        "chunk_size_prose", "chunk_size_table", "top_k", "hybrid", "preserve_metadata",
    ))
    title_ok = [s.get("title") for s in output_sections] == [
        "Resumo", "Setup", "Referencia de campos", "FAQ", "Fontes", "RAG-readiness",
    ]
    count_ok = len(output_sections) == 6

    passed = bool(resumo_ok and fontes_ok and rag_ok and title_ok and count_ok)
    score = 0.9 if passed else 0.7

    return structured_output(
        KIND,
        output_sections,
        passed=passed,
        score=score,
        artifact=_artifact(product, version, audience, len(output_sections),
                           len(source_refs), passed, kind=_kind),
        real=True,
        notes=notes,
    )


# --------------------------------------------------------------------------- #
# Domain contract (Missao A / MOLDED_REAL_SEAM export-deepening) -- the REAL domain
# law this generator enforces, exposed for cex_export_agent.py to bake into an
# exported agent package (system_instruction GROUNDING + a new knowledge/
# domain_contract.md bundle file) instead of a generic ISO-scaffold. Discovered via
# capability_generators._base.get_domain_contract (module-level convention -- see
# that function's docstring).
#
# SINGLE SOURCE OF TRUTH: every value below is a REFERENCE to the SAME module
# constant build() reads above -- never a re-typed literal -- so an exported bundle
# can never drift from what build() actually enforces at runtime.
#
# DELIBERATELY EXCLUDED: _SCAFFOLD_SETUP / _SCAFFOLD_REFERENCIA / _SCAFFOLD_FAQ /
# _DATE_MOCK. Those are wave-1 illustrative placeholder CONTENT (a generic,
# tenant-neutral pet-feeder IoT example -- see the module docstring above), not
# enforceable domain LAW -- the same distinction ads.py's own domain_contract()
# already draws by excluding its analogous _scaffold_row placeholder ad copy.
# Baking example body text into an exported agent's grounding would risk exactly
# the kind of content leak this repo has flagged before (brand-leak, R-405) --
# an exported product_docs agent for a real tenant must never be primed to talk
# about automatic pet feeders.
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law product_docs.py enforces on every generated product
    document (Missao A). Returns a structured, JSON-serialisable dict -- never {}
    for THIS generator (product_docs DOES declare domain law): the optional-section
    enum + canonical titles, the audience enum, the fixed out-of-scope/compliance
    statement, the default source refs, and the confidence/reliability-by-rank
    ladder applied to Fontes rows. See the module comment above for what is
    deliberately left out and why."""
    return {
        "contract_version": CONTRACT_VERSION,
        "optional_sections": sorted(_SECTIONS_ALL),
        "section_labels": dict(_SECTION_LABELS),
        "audience_enum": dict(_AUDIENCE_LABEL),
        "out_of_scope_statement": _NOT_SCOPE_PRODUCT,
        "default_source_refs": list(_DEFAULT_SOURCE_REFS),
        "source_confidence_by_rank": list(_CONF_MAP),
        "source_reliability_by_rank": list(_REL_MAP),
    }


__all__ = [
    "KIND",
    "CONTRACT_VERSION",
    "build",
    "product_docs_media_requests",
    "product_docs_produced_media",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
