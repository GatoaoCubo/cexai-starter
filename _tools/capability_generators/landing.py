#!/usr/bin/env python3
# -*- coding: ascii -*-
"""landing -- N02 CAPGEN Wave 1: landing page copy generator (LLM-creative lane).

KIND = "landing" (capability #13, N02; CEX kind = landing_page).
6 inputs -> 6 output sections: Hero / Secoes / CTA / Voz da marca /
Compliance / SEO.

LLM-creative: calls credential(prompt) -> JSON for hero copy, sections, CTA.
Degrade-never: deterministic scaffold when credential absent or fails.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional

from ._base import (
    brand_frame_note,
    brand_name_of,
    brand_title,
    effective_kind,
    fields_section,
    list_section,
    register,
    structured_output,
    table_section,
)

KIND = "landing"
CONTRACT_VERSION = "1.0.0"

_GOAL_ENUM = {"lead_capture", "venda_direta", "trial", "webinar", "download"}
_REGISTER_ENUM = {"warm", "bold", "playful"}
_FUNNEL_ENUM = {"awareness", "consideration", "decision"}

# Funnel -> CTA formula
_CTA_FORMULA: dict = {
    "awareness": "Soft call (Saiba mais / Descubra / Explorar) -- sem pressao de compra",
    "consideration": "Value-proof call (Ver como funciona / Comparar / Agendar demo)",
    "decision": "Close call (Comprar agora / Garantir desconto / Comecar hoje)",
}

# Page section templates per funnel stage (Funcao = objecao que quebra)
_SECTION_TEMPLATES: dict = {
    "awareness": [
        ("Hero", "Objecao: 'Por que devo me importar?' -- headline estabelece relevancia em <5s"),
        ("Problema", "Objecao: 'Voce nao entende meu problema' -- nomear a dor com precisao"),
        ("Solucao", "Objecao: 'Isso e so mais uma promessa' -- o mecanismo (como funciona de fato)"),
        ("Prova social", "Objecao: 'Funciona para pessoas como eu?' -- depoimento com nome + resultado"),
        ("FAQ", "Objecao: 'Tenho duvidas antes de continuar' -- 3-5 perguntas que bloqueiam acao"),
        ("CTA suave", "Objecao: 'Ainda nao estou pronto' -- opcao de baixa fricao (newsletter, ebook)"),
    ],
    "consideration": [
        ("Hero", "Objecao: 'Ja vi isso antes' -- diferenciar pelo mecanismo, nao pelo produto"),
        ("Comparativo", "Objecao: 'Por que voce e nao o concorrente?' -- matriz de comparacao honesta"),
        ("Demo / trial", "Objecao: 'Quero testar antes de comprar' -- CTA de baixo risco"),
        ("Prova de ROI", "Objecao: 'Vale o investimento?' -- calculadora ou caso de negocio"),
        ("Garantia", "Objecao: 'E se nao funcionar?' -- reversao de risco explicita"),
        ("CTA", "Objecao: 'Proximo passo nao e claro' -- uma acao, destaque visual"),
    ],
    "decision": [
        ("Hero urgencia", "Objecao: 'Posso deixar para depois' -- prazo ou escassez real"),
        ("Oferta", "Objecao: 'O preco e alto' -- valor + preco + comparativo de custo"),
        ("Prova definitiva", "Objecao: 'Preciso de mais evidencia' -- numero + fonte + cliente logo"),
        ("Garantia", "Objecao: 'Risco de arrepender' -- politica de devolucao clara"),
        ("CTA final", "Objecao: 'Uma ultima duvida' -- responder + botao de compra imediato"),
        ("Bump / upsell", "Objecao: 'So isso?' -- oferta complementar de alta aceitacao"),
    ],
}

# Skeptic + B2C forbidden words (brand_voice_templates sec. 7)
_FORBIDDEN_SKEPTIC = [
    ("incrivel", "resultado especifico + metrica"),
    ("trusted by", "nome do cliente + cargo + resultado real"),
    ("game-changer", "o mecanismo que muda especificamente"),
    ("superlativo sem fonte", "sempre par com ranking + data + fonte auditavel"),
]

# Voice mode per register: how each page zone (Hero/Body/Proof/CTA) should read
# (n02_brand_voice). Hoisted to module level (was a local `mode_switch` dict inside
# build()) so build()'s Voz da marca section and domain_contract() below share the SAME
# object -- neither re-types the other's wording (mirrors the ads.py _COMPLIANCE_STATIC
# hoist rationale).
_VOICE_MODE_BY_REGISTER: dict = {
    "warm": "Hero=Empatia, Body=Benefit, Proof=Testemunho, CTA=Convite",
    "bold": "Hero=Founder/Desafio, Body=Mecanismo, Proof=VP-dados, CTA=Skeptic",
    "playful": "Hero=Hook-viral, Body=Storytelling, Proof=Social, CTA=FOMO",
}

# Compliance / LGPD gates enforced on every generated page. Hoisted to module level (was
# an inline list inside build()'s Compliance section) -- shared VERBATIM between build()
# and domain_contract() below: single source of truth, neither re-types the other's wording.
_COMPLIANCE_ITEMS: tuple = (
    "Claim verificavel: toda afirmacao de resultado precisa de fonte e data",
    "Sem superlativo nao-comprovado: 'melhor', 'n1', 'lider' so com ranking auditavel",
    "Prova social real: depoimentos com nome completo, cargo, empresa (sem anon)",
    "LGPD: politica de privacidade linkada no header + footer + formulario",
    "Pixel de retargeting: consentimento informado antes de ativar rastreamento",
    "Garantia: politica de devolucao descrita com clareza (prazo + processo)",
)

# Deterministic LLM-fallback scaffold: what build()/_scaffold_sections() emit ONLY when no
# credential/LLM output is available ("%s" fills with target/product at call time). Hoisted
# to module level (was inline literals in build() + _scaffold_sections()) so the SAME
# templates back both the real fallback behavior and domain_contract()'s labelled
# `llm_fallback_scaffold` below -- never re-typed, never silently dropped (founder policy
# 2026-07-18: expose scaffold honestly, do not hide it).
_LLM_FALLBACK_SCAFFOLD: dict = {
    "hero_h1_a_template": "[H1-A: resultado para %s sem mencionar produto] (generation_pending)",
    "hero_h1_b_template": "[H1-B: provocacao de dor especifica de %s] (generation_pending)",
    "hero_winner_default": "A",
    "cta_sub_default": "Sem cartao de credito. Cancele quando quiser. (generation_pending)",
    "section_proof_template": "[Prova para '%s': dado verificavel + fonte] (generation_pending)",
}


def _pick(val: Any, valid: set, default: str) -> str:
    s = str(val or "").strip().lower()
    return s if s in valid else default


def _scaffold_sections(funnel: str, product: str) -> List[List[str]]:
    templates = _SECTION_TEMPLATES.get(funnel, _SECTION_TEMPLATES["consideration"])
    rows: List[List[str]] = []
    for secao, funcao in templates:
        rows.append([
            secao,
            funcao,
            _LLM_FALLBACK_SCAFFOLD["section_proof_template"] % product,
        ])
    return rows


def _parse_llm_sections(raw: str, num: int) -> List[List[str]]:
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            return []
        rows: List[List[str]] = []
        for item in data[:num]:
            if not isinstance(item, dict):
                continue
            rows.append([
                str(item.get("secao") or "Secao"),
                str(item.get("funcao") or ""),
                str(item.get("prova") or ""),
            ])
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

    # BRAND_MUSTACHE (arch-council C2): brand-frame the landing output from the per-tenant
    # brand context the run path injects into ``inputs`` (the reserved ``brand_context`` key).
    # The brand rides ADDITIVELY into the Hero H1/sub, the Voz section + the SEO title -- the
    # section TITLES + row/item COUNTS stay STABLE (golden tests anchor them). DEGRADE-NEVER:
    # an un-branded run (no brand_context) -> brand_name="", _bnote=None -> byte-identical.
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    # F1 CONSTRAIN
    product = str(inputs.get("product") or "").strip() or "Produto"
    goal = _pick(inputs.get("goal"), _GOAL_ENUM, "venda_direta")
    target = str(inputs.get("target") or "").strip() or "Publico-alvo"
    reg = _pick(inputs.get("register"), _REGISTER_ENUM, "bold")
    funnel = _pick(inputs.get("funnel_stage"), _FUNNEL_ENUM, "decision")
    num_sections = 5

    # F6 PRODUCE -- LLM or scaffold
    hero_h1_a, hero_h1_b, hero_winner = "", "", ""
    section_rows: List[List[str]] = []
    cta_primary, cta_sub = "", ""

    if credential is not None:
        prompt = (
            "Generate landing page copy in Portuguese. "
            "product='%s', goal='%s', target='%s', register='%s', funnel_stage='%s'. "
            "Return a JSON object with keys: "
            "hero_h1_a (headline A), hero_h1_b (headline B for A/B), "
            "hero_winner (predicted winner: A or B), "
            "sections (array of %d objects: {secao, funcao, prova}), "
            "cta_primary (primary CTA text), cta_sub (secondary/subtext). "
            "Never fabricate verifiable claims. "
            "hero_h1 must be outcome-focused, not product-name focused. "
            "Output ONLY the JSON object."
        ) % (product, goal, target, reg, funnel, num_sections)
        try:
            resp = str(credential(prompt)) if callable(credential) else ""
            if resp:
                data = json.loads(resp)
                hero_h1_a = str(data.get("hero_h1_a") or "")
                hero_h1_b = str(data.get("hero_h1_b") or "")
                hero_winner = str(data.get("hero_winner") or "A")
                section_rows = _parse_llm_sections(
                    json.dumps(data.get("sections") or []), num_sections
                )
                cta_primary = str(data.get("cta_primary") or "")
                cta_sub = str(data.get("cta_sub") or "")
                if section_rows:
                    notes.append("sections: LLM credential")
        except Exception:
            pass
    if not section_rows:
        section_rows = _scaffold_sections(funnel, product)
        notes.append("generation_pending: scaffold sections (no credential or LLM failed)")
    if not hero_h1_a:
        hero_h1_a = _LLM_FALLBACK_SCAFFOLD["hero_h1_a_template"] % target
    if not hero_h1_b:
        hero_h1_b = _LLM_FALLBACK_SCAFFOLD["hero_h1_b_template"] % target
    if not hero_winner:
        hero_winner = _LLM_FALLBACK_SCAFFOLD["hero_winner_default"]
    if not cta_primary:
        cta_primary = _CTA_FORMULA.get(funnel, "CTA (generation_pending)").split("(")[0].strip()
    if not cta_sub:
        cta_sub = _LLM_FALLBACK_SCAFFOLD["cta_sub_default"]

    # Section 1: Hero. The brand name (when present) frames the subheadline additively -- the
    # H1 A/B copy stays creative (LLM/scaffold), the 5 rows + the title are STABLE.
    _hero_sub = "[Clarifica H1 em 1 frase: quem e o produto + o mecanismo] (generation_pending)"
    if brand_name:
        _hero_sub = "[Clarifica H1 de %s em 1 frase: o produto + o mecanismo] (generation_pending)" % brand_name
    sec1 = fields_section(
        "Hero",
        [
            ("H1 A", hero_h1_a),
            ("H1 B", hero_h1_b),
            ("Vencedor previsto", "H1 %s" % hero_winner),
            ("Subheadline", _hero_sub),
            ("Social proof anchor", "[Prova rapida no hero: N clientes / N estrelas / logo de midia]"),
        ],
        note="Hero e o gate de 5 segundos. H1 deve explicar o beneficio, nao o produto.",
    )

    # Section 2: Secoes (table)
    sec2 = table_section(
        "Secoes",
        ["Secao", "Funcao (objecao que quebra)", "Prova (mecanismo)"],
        section_rows,
        column_types=["string", "string", "string"],
        key_col_index=0,
        note="Cada secao declara a objecao que quebra e qual prova carrega. "
             "Sequencia = arco de conversao para funnel '%s'." % funnel,
    )

    # Section 3: CTA
    sec3 = fields_section(
        "CTA",
        [
            ("CTA primario", cta_primary),
            ("Sub-text", cta_sub),
            ("Pressao", _CTA_FORMULA.get(funnel, "Medio")),
            ("Posicao", "Acima da dobra (hero) + apos prova social + rodape"),
            ("Cor", "Contraste maximo com fundo -- nao usar cinza ou branco sobre branco"),
        ],
        note="Uma acao, um destino. CTA secundario so se goal = lead_capture + venda_direta compostos.",
    )

    # Section 4: Voz da marca (4 canonical keys)
    forbidden_row = "; ".join("'%s' -> '%s'" % (w, r) for w, r in _FORBIDDEN_SKEPTIC[:2])
    sec4 = fields_section(
        "Voz da marca",
        [
            ("Registro aplicado", "%s -- padrao para landing de '%s' (n02_brand_voice)" % (reg.capitalize(), goal)),
            ("Estrategia de lead", "Hero abre com resultado (nao produto); solucao emerge do problema"),
            ("Perspectiva", "Segunda pessoa singular -- 'voce', 'seu negocio'; nunca 'nossos clientes'"),
            ("Palavras removidas (segmento: Skeptic + B2C)", forbidden_row),
        ],
        note=brand_title(
            "Mode switching por secao: %s" % _VOICE_MODE_BY_REGISTER.get(reg, "registro %s" % reg),
            inputs,
        ),
    )

    # Section 5: Compliance
    sec5 = list_section(
        "Compliance",
        list(_COMPLIANCE_ITEMS),
        note="Gate de compliance: verificar ANTES de publicar. Falha = PROCON ou chargebacks.",
    )

    # Section 6: SEO (table). The SEO <title> carries the brand name when present (brand-first
    # title is the SEO convention); un-branded -> the product-only title (byte-identical). The
    # 7 rows + the 2 columns are STABLE -- only the title VALUE is brand-framed.
    product_slug = "-".join(product.lower().split()[:3]) if product.split() else "produto"
    _seo_title = (
        "[%s -- %s | Beneficio principal] -- 50-60 chars" % (product, brand_name)
        if brand_name
        else "[%s | Beneficio principal] -- 50-60 chars" % product
    )
    seo_rows: List[List[str]] = [
        ["title", _seo_title],
        ["meta_description", "[Descricao da proposta de valor em 150-160 chars com KW primaria]"],
        ["slug", "/%s" % product_slug],
        ["h1", "Mesmo texto do H1 vencedor (consistencia SEO + UX)"],
        ["keywords", "%s, arranhador gato, produto pet, %s" % (product.lower(), target.lower())],
        ["og:title", "[Mesmo title ou variante para redes sociais]"],
        ["og:description", "[Resumo de 1 frase para compartilhamento social]"],
    ]
    sec6 = table_section(
        "SEO",
        ["Campo", "Valor"],
        seo_rows,
        column_types=["string", "string"],
        key_col_index=0,
        note="Meta tags e estrutura on-page. Validar com Screaming Frog ou ahrefs apos publicar.",
    )

    sections = [sec1, sec2, sec3, sec4, sec5, sec6]

    # F7 GOVERN
    has_sections = len(section_rows) >= 3
    has_4_voz = len(sec4.get("rows", [])) == 4
    compliance_ok = len(sec5.get("items", [])) >= 4
    has_h1_ab = bool(hero_h1_a and hero_h1_b)
    score = 1.0
    if not has_4_voz:
        score -= 0.2
        notes.append("[FAIL] voz-da-marca: faltam chaves canonicas")
    if not has_sections:
        score -= 0.15
        notes.append("[FAIL] secoes < 3")
    if not compliance_ok:
        score -= 0.1
        notes.append("[FAIL] compliance < 4 itens")
    if not has_h1_ab:
        score -= 0.05
        notes.append("[WARN] H1 A ou B vazio")
    passed = bool(has_4_voz and has_sections and compliance_ok and score >= 0.7)

    return structured_output(
        KIND, sections, passed=passed, score=score,
        artifact=json.dumps({
            "kind": _kind, "contract_version": CONTRACT_VERSION,
            "goal": goal, "register": reg,
            "funnel_stage": funnel, "num_sections": len(section_rows),
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
# SINGLE SOURCE OF TRUTH: every value below is a REFERENCE to the SAME module constant
# build() / _scaffold_sections() read above -- never a re-typed literal -- so an exported
# bundle can never drift from what build() actually enforces at runtime.
# _VOICE_MODE_BY_REGISTER and _COMPLIANCE_ITEMS were hoisted from what used to be inline
# literals in build() (a local `mode_switch` dict and an inline Compliance items list)
# specifically so this contract and build() share the exact same object -- mirroring the
# ads.py precedent (its own _COMPLIANCE_STATIC hoist, same rationale). Only the CONTAINER
# shape changes below (e.g. _SECTION_TEMPLATES' dict-of-tuples -> a row-dict per section)
# so the generic markdown renderer in cex_export_agent.py (_render_domain_contract_body)
# produces a clean table -- the leaf values themselves are never retyped.
#
# LAW vs SCAFFOLD (founder policy 2026-07-18): goal/register/funnel_stage enums, the
# funnel->CTA formula, the per-funnel-stage section structure (+ the objection each section
# breaks), the voice mode per register, the forbidden-word list, and the compliance/LGPD
# gates are REAL domain law -- they gate every run regardless of whether a credential/LLM
# is present. `llm_fallback_scaffold` is the DETERMINISTIC placeholder content this
# generator emits ONLY when no credential/LLM output is available (see build()'s
# `if not hero_h1_a: ...` fallbacks and `_scaffold_sections()`) -- labelled `_scaffold` so a
# consumer never mistakes a "%s"-templated placeholder for live, per-run-authored copy.
# KIND is seam plumbing (excluded); CONTRACT_VERSION is kept as `contract_version`, as in
# ads.py/docs.py, so a consumer can tell which shape of contract it received.
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law landing.py enforces on every generated landing page (Missao A).
    Returns a structured, JSON-serialisable dict -- never {} for THIS generator (landing
    DOES declare domain law: goal/register/funnel_stage enums, the funnel->CTA formula, the
    per-funnel-stage page structure + which objection each section breaks, the voice mode by
    register, the forbidden-word list, and the compliance/LGPD gates -- plus the labelled
    deterministic LLM-fallback scaffold; {} is only the _base.py no-op default for a
    generator with none)."""
    return {
        "contract_version": CONTRACT_VERSION,
        "enums": {
            "goal": sorted(_GOAL_ENUM),
            "register": sorted(_REGISTER_ENUM),
            "funnel_stage": sorted(_FUNNEL_ENUM),
        },
        "cta_formula_by_funnel_stage": dict(_CTA_FORMULA),
        "section_structure_by_funnel_stage": [
            {"funnel_stage": stage, "order": i + 1, "section": secao, "breaks_objection": funcao}
            for stage, rows in _SECTION_TEMPLATES.items()
            for i, (secao, funcao) in enumerate(rows)
        ],
        "voice_mode_by_register": dict(_VOICE_MODE_BY_REGISTER),
        "forbidden_words": [
            {"word": w, "replacement": r} for (w, r) in _FORBIDDEN_SKEPTIC
        ],
        "compliance_gates": list(_COMPLIANCE_ITEMS),
        "llm_fallback_scaffold": dict(_LLM_FALLBACK_SCAFFOLD),
    }


# --------------------------------------------------------------------------- #
# Media helpers (public -- called by tests and the edge runtime).
# DUALROLL (mission DUALROLL, Wave 4): roll the founder dual-output media pattern to
# landing. The HUMAN face wants a hero image (the 5-second visual gate) + one supporting
# image per page section. landing is an LLM-creative TEXT lane: it does NOT auto-produce
# image URLs, so by default EVERY slot is an empty upload-fallback (NEVER-FABRICATE). When
# the inputs DO carry image URLs (hero_image and/or section_images), those slots fill; the
# rest stay upload-fallback. resolve_media auto-discovers the prefixed landing_* names (no
# edit to _base / __init__ / cex_run_capability needed).
# --------------------------------------------------------------------------- #

def landing_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Build the media_requests list for cex_dual_output.to_dual_output from landing inputs.

    Declares:
      * ONE hero image slot (key='hero', kind=image, section='Hero') -- the 5-second visual
        gate of the page (renders under the Hero output section).
      * ONE supporting image slot per page section (key='section_N', kind=image,
        section='Secoes'); the count mirrors the funnel's _SECTION_TEMPLATES (6 for every
        funnel), so it lines up with the Secoes table the human face shows.
    ALL slots start as upload-fallback; this function NEVER fabricates a src. PURE + TOTAL."""
    funnel = _pick(inputs.get("funnel_stage"), _FUNNEL_ENUM, "decision")
    templates = _SECTION_TEMPLATES.get(funnel, _SECTION_TEMPLATES["consideration"])
    requests: List[Dict[str, Any]] = [{
        "key": "hero",
        "kind": "image",
        "section": "Hero",
        "label": "Imagem do hero (gate de 5s)",
    }]
    for i, (secao, _funcao) in enumerate(templates):
        requests.append({
            "key": "section_%d" % i,
            "kind": "image",
            "section": "Secoes",
            "label": "Imagem da secao: %s" % secao,
        })
    return requests


def landing_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Build the produced_media dict for cex_dual_output.to_dual_output from landing inputs.

    landing is a TEXT/creative lane -- it does not auto-produce images. A slot is filled
    ONLY when the inputs supply a real URL:
      * 'hero'      <- inputs['hero_image'] (or 'hero_image_url'), when non-empty.
      * 'section_N' <- inputs['section_images'], a dict {section_N: url} / {N: url} OR a list
                       [url0, url1, ...], when the entry is a non-empty URL.
    Any slot without a supplied URL stays upload-fallback (omitted here). NEVER-FABRICATE.
    PURE + TOTAL: never raises."""
    funnel = _pick(inputs.get("funnel_stage"), _FUNNEL_ENUM, "decision")
    templates = _SECTION_TEMPLATES.get(funnel, _SECTION_TEMPLATES["consideration"])
    produced: Dict[str, Any] = {}

    hero_url = str(inputs.get("hero_image") or inputs.get("hero_image_url") or "").strip()
    if hero_url:
        produced["hero"] = {"src": hero_url, "alt": "Imagem do hero"}

    section_images = inputs.get("section_images") or {}
    if isinstance(section_images, Mapping):
        for i, (secao, _funcao) in enumerate(templates):
            key = "section_%d" % i
            url = str(section_images.get(key) or section_images.get(str(i)) or "").strip()
            if url:
                produced[key] = {"src": url, "alt": "Imagem da secao: %s" % secao}
    elif isinstance(section_images, (list, tuple)):
        for i, url_raw in enumerate(section_images):
            url = str(url_raw or "").strip()
            if url and i < len(templates):
                produced["section_%d" % i] = {
                    "src": url, "alt": "Imagem da secao: %s" % templates[i][0],
                }

    return produced


__all__ = [
    "KIND",
    "CONTRACT_VERSION",
    "build",
    "landing_media_requests",
    "landing_produced_media",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
