#!/usr/bin/env python3
# -*- coding: ascii -*-
"""email_builder -- N02 CAPGEN Wave 1: email sequence copy generator (LLM-creative lane).

KIND = "email_builder" (capability #11, N02; CEX kind = prompt_template).
6 inputs -> 6 output sections: Assunto A/B / Preheader / Blocos do corpo /
Voz da marca / Compliance / Render notes.

LLM-creative: calls credential(prompt) -> JSON for email body blocks + subject lines.
Degrade-never: deterministic scaffold when credential absent or fails.

N07 WIRING NOTE: CEX kind = "prompt_template" (same as ads). Runtime seam
_get_structured_generator looks up by kind, not cap -- so "email_builder" slug must
be tried FIRST. See ads.py N07 note for the 2-line patch to cex_run_capability.py.
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

KIND = "email_builder"
CONTRACT_VERSION = "1.0.0"

_GOAL_ENUM = {"nutricao", "reativacao", "conversao", "lancamento", "anuncio"}
_REGISTER_ENUM = {"warm", "bold", "playful"}
_FUNNEL_ENUM = {"awareness", "consideration", "decision"}
_AB_AXIS_ENUM = {"assunto", "cta", "oferta", "personalizacao"}

# Register default per email goal (n02_brand_voice spec)
_GOAL_REGISTER: dict = {
    "nutricao": "warm",
    "reativacao": "warm",
    "conversao": "bold",
    "lancamento": "bold",
    "anuncio": "bold",
}

_FUNNEL_FORMULA: dict = {
    "awareness": "AIDA (Attention + Interest + Desire + Action suave)",
    "consideration": "PAS (Problem + Agitation + Solution) ou BAB (Before + After + Bridge)",
    "decision": "Oferta + Urgencia + Garantia + CTA forte",
}

# Skeptic + Marketer forbidden words (brand_voice_templates sec. 7)
_FORBIDDEN_MKTR = [
    ("amazing", "resultado especifico com numero"),
    ("voce vai amar", "'se voce ja quis X, isso entrega X'"),
    ("limited time", "data de expiracao real + razao"),
    ("engagement", "a acao concreta: clique, abertura, resposta"),
]

# Persuasive functions for email blocks
_BLOCK_FUNCTIONS = [
    "Estabelecer credibilidade (por que ouvir?)",
    "Provocar dor latente (o problema que voce nao nomeou)",
    "Apresentar solucao (o mecanismo, nao o produto)",
    "Prova social (resultado verificavel de cliente real)",
    "CTA primario (uma acao, sem alternativa)",
    "Urgencia + garantia (reducao de risco de compra)",
]

# A/B axis -> human label (n02_brand_voice). Hoisted from build()'s local dict (Missao A
# export-deepening) so domain_contract() below can reference it BY NAME instead of
# re-typing it -- single source of truth, build() reads the SAME constant.
_AB_AXIS_LABEL: Dict[str, str] = {
    "assunto": "Linha de assunto (assunto A vs B)",
    "cta": "Call to action (texto e cor do botao)",
    "oferta": "Oferta apresentada (desconto vs bonus vs gratis)",
    "personalizacao": "Nivel de personalizacao (nome vs segmento vs generico)",
}

# A/B decision rule (sec1 "Metrica de decisao") -- when a variant is trusted as a winner.
# Hoisted (was an inline literal) so domain_contract() can reference the SAME constant.
_AB_DECISION_METRIC: Dict[str, str] = {
    "metric": "Taxa de abertura no primeiro 2h",
    "min_sample_size": "200 envios",
}

# Preheader structural rules (sec2) -- length convention + persuasive function. Hoisted
# (was 2 inline literals) so domain_contract() can reference the SAME constant.
_PREHEADER_RULES: Dict[str, str] = {
    "length_target": "40-60 caracteres (exibido em Gmail/Outlook sem corte)",
    "function": "Complementar o assunto, nao repetiir -- aumenta abertura em 10-15%",
}

# Compliance gates (sec5) -- LGPD/CAN-SPAM/SPF-DKIM-DMARC. ALWAYS emitted (not gated by
# credential/LLM success) -- REAL regulatory/technical law, not scaffold. Hoisted from an
# inline literal list so domain_contract() references the SAME constant build() reads.
_COMPLIANCE_ITEMS: List[str] = [
    "LGPD: link de descadastramento (unsubscribe) obrigatorio e funcional",
    "CAN-SPAM: razao de contato explicita no rodape + endereco fisico do remetente",
    "Sem claim nao-verificavel: depoimentos exigem nome real + resultado mensuravel",
    "Remetente autenticado: SPF + DKIM + DMARC configurados antes de enviar",
    "Sem domain spoofing: remetente deve ser dominio proprio (nunca gmail/yahoo)",
    "LGPD art. 7: base legal de consentimento documentada para cada segmento",
]

# Render notes (sec6) -- email client rendering constraints (Outlook/Gmail/dark mode/VML).
# ALWAYS emitted (not gated by credential/LLM success) -- REAL technical law, not scaffold.
# Hoisted from an inline literal list so domain_contract() references the SAME constant.
_RENDER_NOTES_FIELDS: List[Tuple[str, str]] = [
    ("Largura maxima", "600px (Outlook 2016 + Gmail clips acima disso)"),
    ("CSS", "Inline apenas -- clientes de email ignoram stylesheets externos"),
    ("Outlook MSO", "Usar tabelas HTML para layout; evitar CSS flexbox/grid"),
    ("Dark mode", "media prefers-color-scheme:dark + meta[name=color-scheme] content=light dark"),
    ("Imagens", "Alt text em todas -- 40% dos leitores bloqueiam imagens por padrao"),
    ("CTA botao", "VML fallback para Outlook: <!--[if mso]>...<!endif-->"),
]

# Deterministic email body block SCAFFOLD (used by _scaffold_blocks() below when no
# credential/LLM output is available). "%s" in content_template is filled with the
# audience string at call time; templates with no "%s" are emitted verbatim. Hoisted from
# a function-local list so domain_contract() can expose it (LABELED as scaffold -- every
# row's own text carries "generation_pending", so a consumer can never mistake this for
# live per-campaign copy).
_BODY_BLOCK_SCAFFOLD: List[Tuple[str, str, str]] = [
    ("Abertura", "[Hook: provocacao ou empatia baseada no perfil %s]",
     "Estabelecer credibilidade e relevancia imediata (generation_pending)"),
    ("Problema", "[Nomear dor especifica do perfil %s sem solucao ainda]",
     "Provocar dor latente -- leitora nao nomeou, mas reconhece (generation_pending)"),
    ("Solucao", "[Apresentar mecanismo sem vender produto diretamente]",
     "Apresentar solucao: o como funciona, nao o produto (generation_pending)"),
    ("Prova", "[Depoimento real: nome + cargo + resultado especifico + foto]",
     "Prova social verificavel -- nome real, resultado mensuravel (generation_pending)"),
    ("CTA", "[Uma acao, claro, sem opcoes paralelas: link destacado + botao]",
     "CTA primario: uma acao, zero alternativas (generation_pending)"),
    ("Urgencia", "[Prazo real ou escassez verificavel -- nunca fabricar]",
     "Urgencia + garantia: reducao do risco de nao-compra (generation_pending)"),
]

# Deterministic subject/preheader SCAFFOLD (build()'s fallback when the LLM/credential
# path yields nothing). Hoisted from 3 inline literals -- LABELED as scaffold (each value
# carries "generation_pending").
_SUBJECT_LINE_SCAFFOLD: Dict[str, str] = {
    "subject_a": "[Assunto A: benefit-driven, sem superlativo] (generation_pending)",
    "subject_b": "[Assunto B: curiosidade ou numero] (generation_pending)",
    "preheader": "[Preheader: 40-60 chars, complementa assunto sem repetir] (generation_pending)",
}


def _pick(val: Any, valid: set, default: str) -> str:
    s = str(val or "").strip().lower()
    return s if s in valid else default


def _coerce_bool(val: Any, default: bool = False) -> bool:
    if isinstance(val, bool):
        return val
    s = str(val or "").strip().lower()
    return s in {"true", "1", "yes", "sim"}


def _resolve_register(goal: str, register_in: Any) -> str:
    if register_in and str(register_in).strip().lower() in _REGISTER_ENUM:
        return str(register_in).strip().lower()
    return _GOAL_REGISTER.get(goal, "warm")


def _scaffold_blocks(n: int, goal: str, audience: str) -> List[List[str]]:
    """Deterministic email body blocks (scaffold mode). Content template sourced from the
    module-level _BODY_BLOCK_SCAFFOLD -- single source of truth shared with domain_contract()
    below, so an exported bundle can never drift from what this function actually emits."""
    rows: List[List[str]] = []
    for i in range(min(n, len(_BODY_BLOCK_SCAFFOLD))):
        block, content_template, func = _BODY_BLOCK_SCAFFOLD[i]
        content = content_template % audience if "%s" in content_template else content_template
        rows.append([block, content, func])
    return rows


def _parse_llm_blocks(raw: str, n: int) -> List[List[str]]:
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            return []
        rows: List[List[str]] = []
        for item in data[:n]:
            if not isinstance(item, dict):
                continue
            block = str(item.get("bloco") or "Bloco")
            content = str(item.get("conteudo") or "")
            func = str(item.get("funcao") or "")
            rows.append([block, content, func])
        return rows
    except Exception:
        return []


@register(KIND)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> dict:
    """``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND."""
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # F1 CONSTRAIN
    campaign = str(inputs.get("campaign") or "").strip() or "Campanha nao informada"
    audience = str(inputs.get("audience") or "").strip() or "Publico-alvo"
    goal = _pick(inputs.get("goal"), _GOAL_ENUM, "nutricao")
    register_in = inputs.get("register")
    reg = _resolve_register(goal, register_in)
    funnel = _pick(inputs.get("funnel_stage"), _FUNNEL_ENUM, "consideration")
    ab_test = _coerce_bool(inputs.get("ab_test"), True)
    num_blocks = 5

    # BRAND_MUSTACHE: frame the email copy for THIS tenant from the brand context the run path
    # injected. Section TITLES + the "Voz da marca" 4-row shape stay STABLE (tests assert
    # count==4 + the warm-default value); the brand rides an ADDITIVE clause on the EXISTING
    # "Registro aplicado" row VALUE + a brand note appended to the EXISTING section note.
    # Un-branded -> neutral value, no note delta (degrade-never). NEVER hardcodes the brand.
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    # F6 PRODUCE -- email blocks
    block_rows: List[List[str]] = []
    subject_a, subject_b = "", ""
    preheader = ""

    if credential is not None:
        prompt = (
            "Write email marketing copy in Portuguese. "
            "campaign='%s', audience='%s', goal='%s', register='%s', funnel_stage='%s'. "
            "Return a JSON object with keys: "
            "subject_a (string, subject line A), subject_b (string, subject line B for A/B), "
            "preheader (string, 40-60 chars), "
            "blocks (array of %d objects: {bloco, conteudo, funcao}). "
            "Each block 'funcao' must explain its persuasive job. "
            "Never fabricate customer testimonials or verifiable claims without data. "
            "Never use: amazing, voce vai amar, limited time. "
            "Output ONLY the JSON object."
        ) % (campaign, audience, goal, reg, funnel, num_blocks)
        try:
            resp = str(credential(prompt)) if callable(credential) else ""
            if resp:
                data = json.loads(resp)
                subject_a = str(data.get("subject_a") or "")
                subject_b = str(data.get("subject_b") or "")
                preheader = str(data.get("preheader") or "")
                block_rows = _parse_llm_blocks(
                    json.dumps(data.get("blocks") or []), num_blocks
                )
                if block_rows:
                    notes.append("blocks: LLM credential")
        except Exception:
            pass
    if not block_rows:
        block_rows = _scaffold_blocks(num_blocks, goal, audience)
        notes.append("generation_pending: scaffold blocks (no credential or LLM failed)")
    if not subject_a:
        subject_a = _SUBJECT_LINE_SCAFFOLD["subject_a"]
    if not subject_b:
        subject_b = _SUBJECT_LINE_SCAFFOLD["subject_b"]
    if not preheader:
        preheader = _SUBJECT_LINE_SCAFFOLD["preheader"]

    ab_axis = _pick(inputs.get("ab_axis"), _AB_AXIS_ENUM, "assunto")
    ab_axis_label = _AB_AXIS_LABEL.get(ab_axis, ab_axis)

    # Section 1: Assunto A/B
    sec1 = fields_section(
        "Assunto A/B",
        [
            ("Assunto A", subject_a),
            ("Assunto B", subject_b),
            ("Eixo testado", ab_axis_label if ab_test else "A/B desativado"),
            ("Vencedor previsto", "A (mais direto em etapa %s)" % funnel),
            ("Metrica de decisao", "%s (amostra minima: %s)" % (
                _AB_DECISION_METRIC["metric"], _AB_DECISION_METRIC["min_sample_size"])),
        ],
        note="Linhas de assunto otimizadas para inbox placement. Medir abertura antes de decidir escala.",
    )

    # Section 2: Preheader
    sec2 = fields_section(
        "Preheader",
        [
            ("Texto", preheader),
            ("Comprimento alvo", _PREHEADER_RULES["length_target"]),
            ("Funcao", _PREHEADER_RULES["function"]),
        ],
        note="Preheader e o segundo assunto. Nunca deixar em branco (cliente de email preenche com lixo).",
    )

    # Section 3: Blocos do corpo (table)
    sec3 = table_section(
        "Blocos do corpo",
        ["Bloco", "Conteudo", "Funcao persuasiva"],
        block_rows,
        column_types=["string", "string", "string"],
        key_col_index=0,
        note="Cada bloco declara a funcao persuasiva (o JOB que faz na sequencia de conversao).",
    )

    # Section 4: Voz da marca (4 canonical keys)
    forbidden_row = "; ".join("'%s' -> '%s'" % (w, r) for w, r in _FORBIDDEN_MKTR[:2])
    _registro_val = "%s -- padrao para goal '%s' (n02_brand_voice)" % (reg.capitalize(), goal)
    if brand_name:
        # name the tenant whose voice this register serves (keeps "warm"/reg as a substring).
        _registro_val = "%s: %s" % (brand_name, _registro_val)
    _voz_note = "Prova de que o registro foi aplicado -- auditavel pela brand_audit crew."
    if _bnote:
        _voz_note = "%s %s" % (_voz_note, _bnote)
    sec4 = fields_section(
        "Voz da marca",
        [
            ("Registro aplicado", _registro_val),
            ("Estrategia de lead", "Empatia antes da solucao (abertura valida a dor; produto entra no bloco 3+)"),
            ("Perspectiva", "Segunda pessoa -- 'voce', 'seu', nunca 'nossos clientes adoram'"),
            ("Palavras removidas (segmento: Tutor + Marketer)", forbidden_row),
        ],
        note=_voz_note,
    )

    # Section 5: Compliance
    sec5 = list_section(
        "Compliance",
        list(_COMPLIANCE_ITEMS),
        note="Gate de compliance: verificar ANTES de disparar. Falha aqui = multa ou blacklist.",
    )

    # Section 6: Render notes
    sec6 = fields_section(
        "Render notes",
        list(_RENDER_NOTES_FIELDS),
        note="Checklist de render antes de disparar. Testar em Litmus ou Email on Acid.",
    )

    sections = [sec1, sec2, sec3, sec4, sec5, sec6]

    # F7 GOVERN
    has_blocks = len(block_rows) >= 3
    has_4_voz = len(sec4.get("rows", [])) == 4
    compliance_ok = len(sec5.get("items", [])) >= 4
    has_ab = bool(subject_a and subject_b)
    score = 1.0
    if not has_4_voz:
        score -= 0.2
        notes.append("[FAIL] voz-da-marca: faltam chaves canonicas")
    if not has_blocks:
        score -= 0.15
        notes.append("[FAIL] blocos do corpo < 3")
    if not compliance_ok:
        score -= 0.1
        notes.append("[FAIL] compliance < 4 itens")
    if not has_ab:
        score -= 0.05
        notes.append("[WARN] assunto A ou B vazio")
    passed = bool(has_4_voz and has_blocks and compliance_ok and score >= 0.7)

    return structured_output(
        KIND, sections, passed=passed, score=score,
        artifact=json.dumps({
            "kind": _kind, "contract_version": CONTRACT_VERSION,
            "goal": goal, "register": reg,
            "funnel_stage": funnel, "ab_test": ab_test,
            "num_blocks": len(block_rows),
        }, ensure_ascii=True),
        real=True, notes=notes,
    )


# --------------------------------------------------------------------------- #
# Domain contract (Missao A / MOLDED_REAL_SEAM export-deepening) -- the REAL domain law
# this generator enforces, exposed for cex_export_agent.py to bake into an exported agent
# package (system_instruction GROUNDING + a new knowledge/domain_contract.md bundle file)
# instead of a generic ISO-scaffold. Discovered via capability_generators._base.
# get_domain_contract (module-level convention -- see that function's docstring).
#
# SINGLE SOURCE OF TRUTH: every value below is a REFERENCE to a module constant. Several
# (_AB_AXIS_LABEL, _AB_DECISION_METRIC, _PREHEADER_RULES, _COMPLIANCE_ITEMS,
# _RENDER_NOTES_FIELDS, _BODY_BLOCK_SCAFFOLD, _SUBJECT_LINE_SCAFFOLD) were HOISTED out of
# build()'s own inline literals as part of this change -- a mechanical hoist (same values,
# same call sites, zero output change; see build()'s sec1/sec2/sec5/sec6 + _scaffold_blocks()
# above) done specifically so this function has something real to reference instead of
# re-typing a literal. build() reads the SAME constants this function returns, so an
# exported bundle can never drift from what build() actually enforces at runtime.
#
# HONEST FRAMING: 2 of the 8 pre-existing module constants are declared but NOT read by
# any of build()'s active code today (found while auditing this file, not introduced by
# this change): _FUNNEL_FORMULA (a copy formula per funnel_stage -- AIDA/PAS+BAB/Oferta)
# and _BLOCK_FUNCTIONS (a canonical 6-function persuasive taxonomy). Neither is fabricated
# -- both are real, hand-authored constants -- but no output section build() emits reads
# either one today (sec1 "Vencedor previsto" only names the funnel stage, never the
# formula; _scaffold_blocks() carries its own separate per-block function text rather than
# quoting _BLOCK_FUNCTIONS verbatim). Included below for honesty (never silently drop real
# declared content) but marked vestigial/reserved, not "law build() enforces on every run"
# the way the other groups genuinely are.
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law email_builder.py enforces on every generated email (Missao A).
    Returns a structured, JSON-serialisable dict -- never {} for THIS generator (email_builder
    DOES declare domain law: goal/register/funnel_stage/ab_axis enums, the goal->register
    default, forbidden words, the A/B decision metric + preheader rules + compliance gates +
    render constraints ALWAYS emitted regardless of LLM/scaffold mode, plus the deterministic
    body/subject/preheader scaffold labeled as such; {} is only the _base.py no-op default for
    a generator with none). See the honest-framing comment above: funnel_copy_formulas +
    body_block_persuasive_functions are real, declared constants NOT currently read by
    build()'s active output -- included for honesty, not fabricated, but flagged as
    vestigial/reserved rather than active law."""
    return {
        "contract_version": CONTRACT_VERSION,
        "enums": {
            "goal": sorted(_GOAL_ENUM),
            "register": sorted(_REGISTER_ENUM),
            "funnel_stage": sorted(_FUNNEL_ENUM),
            "ab_axis": sorted(_AB_AXIS_ENUM),
        },
        "register_default_by_goal": dict(_GOAL_REGISTER),
        "ab_axis_labels": dict(_AB_AXIS_LABEL),
        "forbidden_words": [
            {"word": w, "replacement": r} for (w, r) in _FORBIDDEN_MKTR
        ],
        "ab_decision_metric": dict(_AB_DECISION_METRIC),
        "preheader_rules": dict(_PREHEADER_RULES),
        "compliance_gates": list(_COMPLIANCE_ITEMS),
        "render_constraints": [
            {"aspect": k, "rule": v} for (k, v) in _RENDER_NOTES_FIELDS
        ],
        # declared but NOT wired into any build() output section today (honest-framing
        # comment above) -- real, non-fabricated, flagged as vestigial/reserved.
        "funnel_copy_formulas": dict(_FUNNEL_FORMULA),
        "body_block_persuasive_functions": list(_BLOCK_FUNCTIONS),
        # LABELED scaffold: deterministic default content emitted only when no credential/
        # LLM output is available -- never live per-campaign copy (every leaf value carries
        # its own "generation_pending" marker).
        "body_block_scaffold": [
            {"block": name, "content_template": tmpl, "function": func}
            for (name, tmpl, func) in _BODY_BLOCK_SCAFFOLD
        ],
        "default_subject_and_preheader_when_unspecified": dict(_SUBJECT_LINE_SCAFFOLD),
    }


# --------------------------------------------------------------------------- #
# Media hooks (DUALROLL N02) -- opt-in dual-output media layer.
# Discovered by _base.resolve_media via the prefixed naming convention
# (email_builder_media_requests / email_builder_produced_media). No edit to _base.
# --------------------------------------------------------------------------- #

def email_builder_media_requests(inputs):
    """One email_hero image slot for the email header/hero area.

    Always declared so the human face has an upload-fallback dropzone for the
    campaign header. Produced only if inputs carry a real hero URL (see
    email_builder_produced_media). NEVER fabricates a src.
    """
    return [
        {
            "key": "email_hero",
            "kind": "image",
            "section": "Render notes",
            "label": "Hero / header da campanha",
        }
    ]


def email_builder_produced_media(inputs):
    """Produce the email_hero slot when inputs carry a real header image URL.

    Checks inputs['hero_image'] or inputs['header_image'] for a non-blank URL.
    If present: emits the slot as generated (real src). If absent: omits the key
    -> the dual-output layer renders an editable upload-fallback dropzone.
    NEVER fabricate a src when no URL is provided.
    """
    url = str(inputs.get("hero_image") or inputs.get("header_image") or "").strip()
    if url:
        return {"email_hero": {"src": url, "alt": "Email hero"}}
    return {}


__all__ = [
    "KIND",
    "CONTRACT_VERSION",
    "build",
    "email_builder_media_requests",
    "email_builder_produced_media",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
