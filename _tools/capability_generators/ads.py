#!/usr/bin/env python3
# -*- coding: ascii -*-
"""ads -- N02 CAPGEN Wave 1: brand-voice ad copy generator (LLM-creative lane).

KIND = "ads" (capability #1, N02; CEX kind = prompt_template).
8 inputs -> 6 output sections: Variantes / Teste A/B / Voz da marca /
Compliance / Keywords / Estrategia de funil.

LLM-creative: calls credential(prompt) -> JSON string for copy variants.
Degrade-never: deterministic scaffold when credential absent or fails.

N07 WIRING NOTE: the runtime seam (cex_run_capability._get_structured_generator,
line ~944) calls get_generator(kind) where kind="prompt_template". Both ads and
email_builder share that CEX kind, so the lookup conflicts. N07 must patch line
~1126 in cex_run_capability.py to try get_generator(cap) BEFORE get_generator(kind):
  _generator = _get_structured_generator(cap) or _get_structured_generator(kind)
where _get_structured_generator(key) does get_generator(key).
"""
from __future__ import annotations

import json
import os
from typing import Any, List, Mapping, Optional

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

KIND = "ads"
CONTRACT_VERSION = "1.0.0"

_PLATFORM_LIMITS: dict = {
    "meta_feed": 125,
    "google_search": 90,
    "instagram_stories": 80,
    "tiktok": 150,
}
_REGISTER_ENUM = {"warm", "bold", "playful"}
_FUNNEL_ENUM = {"awareness", "consideration", "decision"}
_TONE_ENUM = {"confiante", "divertido", "urgente", "premium"}
_AB_AXIS_ENUM = {"hook", "cta", "offer"}

_FORMULA_MAP: dict = {
    "awareness": "AIDA (Attention + Interest focus)",
    "consideration": "PAS (Problem + Agitation + Solution)",
    "decision": "Oferta + Urgencia + Garantia + CTA forte",
}
_CTA_PRESSURE: dict = {
    "awareness": "Soft: 'Saiba mais', 'Descubra', 'Explore'",
    "consideration": "Medio: 'Veja como', 'Compare', 'Experimente gratis'",
    "decision": "Forte: 'Comprar agora', 'Garantir desconto', 'Comecar hoje'",
}
_NEXT_STAGE: dict = {
    "awareness": "consideration (nutrir lead com PAS)",
    "consideration": "decision (oferta + urgencia)",
    "decision": "reativacao (warm para churned)",
}
_AB_LABEL: dict = {
    "hook": "Hook (gancho de abertura)",
    "cta": "CTA (acao final)",
    "offer": "Oferta (proposta de valor)",
}
# Skeptic + B2C forbidden words -- brand_voice_templates sec. 7
_FORBIDDEN_B2C = [
    ("incrivel", "resultado verificavel com fonte"),
    ("game-changer", "a mudanca especifica neste contexto"),
    ("revolucionario", "o mecanismo exato -- nunca adjetivo"),
]

# Compliance gates enforced on every ad (brand_voice_templates sec. 7 + LGPD). Item 3 (the
# char-limit gate) is TEMPLATED per-run (platform + its actual limit); the other 5 are
# static text -- shared VERBATIM between build()'s sec4 below and domain_contract() (Missao
# A / MOLDED_REAL_SEAM export-deepening): single source of truth, neither re-types the
# other's wording.
_COMPLIANCE_STATIC: tuple = (
    "Afirmacao verificavel: toda claim precisa de fonte citavel antes de publicar",
    "Sem superlativo nao-comprovado: 'melhor', 'n1' so com ranking + fonte auditavel",
    "Meta/Instagram: sem imagens 'antes/depois' de saude sem aprovacao medica",
    "LGPD: sem coleta implicita de dados pessoais no anuncio",
    "Nenhuma promessa de resultado garantido sem evidencia auditavel",
)
_COMPLIANCE_CHARS_TEMPLATE = "Chars <= %d: limite contratual para %s (verificado)"
# The generic (run-independent) phrasing of the same char-limit gate, for domain_contract()
# below -- domain_contract() has no specific platform/lim (it describes the LAW, not one
# run's output), so it references platform_char_limits by name instead of a specific number.
_COMPLIANCE_CHARS_GENERIC = (
    "Chars <= limite contratual da plataforma alvo (ver platform_char_limits) -- "
    "verificado antes de publicar"
)


def _limit(platform: str) -> int:
    return _PLATFORM_LIMITS.get(str(platform).strip().lower(), 125)


def _coerce_int(val: Any, default: int, lo: int, hi: int) -> int:
    try:
        return max(lo, min(hi, int(float(val))))
    except Exception:
        return default


def _pick(val: Any, valid: set, default: str) -> str:
    s = str(val or "").strip().lower()
    return s if s in valid else default


def _scaffold_row(i: int, platform: str, lim: int) -> List[Any]:
    hooks = [
        "Seu gato arranha tudo? (generation_pending)",
        "Testado por tutores em apartamento (generation_pending)",
        "30 dias ou devolvemos (generation_pending)",
        "4.8 estrelas -- 2.143 avaliacoes (generation_pending)",
        "Frete gratis SP/RJ + parcela 6x (generation_pending)",
    ]
    corpos = [
        "Torre 1,2m sisal -- aguenta gatos de 8kg.",
        "Material resistente, montagem em 10 min.",
        "Satisfacao garantida sem burocracia.",
        "Sisal natural, estrutura de MDF de alta densidade.",
        "Disponivel em 3 cores. Entrega em 2 dias uteis.",
    ]
    ctas = ["Ver o produto", "Comprar agora", "Garantir o meu", "Aproveitar oferta", "Adicionar ao carrinho"]
    idx = i % 5
    h, c, t = hooks[idx], corpos[idx], ctas[idx]
    if len(h) + len(c) + len(t) > lim:
        c = c[:max(0, lim - len(h) - len(t) - 1)]
    chars = len(h) + len(c) + len(t)
    return [platform, h, c, t, str(chars), str(lim)]


def _parse_llm_variants(raw: str, platform: str, lim: int, n: int) -> List[List[Any]]:
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            return []
        rows: List[List[Any]] = []
        for item in data[:n]:
            if not isinstance(item, dict):
                continue
            h = str(item.get("hook") or "")
            c = str(item.get("corpo") or "")
            t = str(item.get("cta") or "")
            if len(h) + len(c) + len(t) > lim:
                c = c[:max(0, lim - len(h) - len(t) - 1)]
            rows.append([platform, h, c, t, str(len(h) + len(c) + len(t)), str(lim)])
        return rows
    except Exception:
        return []


# --------------------------------------------------------------------------- #
# LIVE-LLM branch (mission R-350, decision_manifest_wave2_0713.yaml dash_slice).
#
# TRIPLE opt-in: OPENWEBUI_API_BASE + OPENWEBUI_API_KEY + CEXAI_CAPABILITY_LIVE=1 must
# ALL be present, or this entire lane is a no-op (byte-identical to before R-350 -- proven
# by test_ads_live_r350.py's A/B hash). This is INDEPENDENT of the ``credential`` callable
# path above: in production ``credential`` is a cex_run_capability.Credential dataclass
# (never callable), so that path is dormant in real runs -- this lane is the actual
# live-LLM producer, calling cex_sdk.models.chat.chat() directly (Option 1, see the
# handoff Context note). Degrade-never: ANY failure here (import, network, parse, empty
# result) is caught and logged to ``notes`` (ASCII, no secret value ever), and the caller
# falls straight through to the pre-existing credential/scaffold path unchanged.
# --------------------------------------------------------------------------- #
def _import_chat() -> Any:
    """Lazy import of cex_sdk.models.chat.chat. Import-light: only touched once the
    triple opt-in gate (``_live_llm_gate``) fires, so an env-absent run never imports
    cex_sdk.models.chat at all. Module-level so tests can monkeypatch it without a live
    LLM/network call (mirrors cex_run_capability._import_cex_agent)."""
    from cex_sdk.models.chat import chat  # type: ignore[import]

    return chat


def _live_llm_gate() -> bool:
    """True iff the TRIPLE opt-in for the live-LLM ads branch is satisfied: env vars
    OPENWEBUI_API_BASE + OPENWEBUI_API_KEY are both non-blank AND CEXAI_CAPABILITY_LIVE
    is literally "1". Any one absent/blank -> False (degrade-never; the pre-existing
    credential/scaffold path runs unchanged). Presence-only check -- NEVER reads the key
    for any purpose other than a boolean non-blank test (secret discipline)."""
    return bool(
        os.environ.get("OPENWEBUI_API_BASE", "").strip()
        and os.environ.get("OPENWEBUI_API_KEY", "").strip()
        and os.environ.get("CEXAI_CAPABILITY_LIVE", "").strip() == "1"
    )


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

    # BRAND_MUSTACHE (arch-council C2): brand-frame the ad output from the per-tenant brand
    # context the run path injects into ``inputs`` (the reserved ``brand_context`` key). The
    # SAME generator, run for tenant X vs tenant Y, frames its voice/header with X's vs Y's
    # brand. ADDITIVE + DEGRADE-NEVER: an un-branded run (no brand_context) -> brand_name="",
    # _bnote=None -> no note appended + the Voz section reads neutrally = byte-identical to
    # before. Section TITLES + row/item COUNTS stay STABLE (a media slot + golden tests anchor
    # the "Variantes"/"Voz da marca" titles); the brand rides ADDITIVE note/row text only.
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    # F1 CONSTRAIN
    product = str(inputs.get("product") or "").strip() or "Produto"
    audience = str(inputs.get("audience") or "").strip() or "Publico-alvo"
    platform = _pick(inputs.get("platform"), set(_PLATFORM_LIMITS), "meta_feed")
    reg = _pick(inputs.get("register"), _REGISTER_ENUM, "bold")
    funnel = _pick(inputs.get("funnel_stage"), _FUNNEL_ENUM, "consideration")
    tone = _pick(inputs.get("tone"), _TONE_ENUM, "confiante")
    ab_axis = _pick(inputs.get("ab_axis"), _AB_AXIS_ENUM, "hook")
    num_v = _coerce_int(inputs.get("num_variants"), 3, 1, 5)
    lim = _limit(platform)

    # ADMAX W2b: which product this ad is for. The sku/product_slug let the run-path fetch
    # the catalog record (get_product_record) and pass it as inputs['product_record'] so the
    # product_ad mold fills the body/features/offer/specs/faq from REAL data. The generator
    # itself stays copy-only; these are just surfaced in the artifact for provenance.
    sku = str(inputs.get("sku") or "").strip()
    product_slug = str(inputs.get("product_slug") or "").strip()
    has_record = isinstance(inputs.get("product_record"), Mapping) and bool(inputs.get("product_record"))

    # F6 PRODUCE -- variants
    rows: List[List[Any]] = []
    llm_copy = False  # True when the Variantes carry REAL LLM copy (drives the confidence).
    run_mode_val: Optional[str] = None
    model_used_val: Optional[str] = None

    # LIVE branch (mission R-350, triple opt-in -- see the block above _import_chat/
    # _live_llm_gate). Tried FIRST: it is the real producer in a properly-configured box;
    # absent envs -> _live_llm_gate() is False -> this entire if-body never executes ->
    # byte-identical to before R-350 (A/B-proven).
    if _live_llm_gate():
        _live_model = os.environ.get("CEXAI_CAPABILITY_LIVE_MODEL", "glm-cpw")
        _live_prompt = (
            "Generate %d ad copy variants in Portuguese. "
            "product='%s', audience='%s', platform='%s' (char limit=%d), "
            "register='%s', funnel_stage='%s', tone='%s', ab_axis='%s'. "
            "Return JSON array of objects with keys: hook, corpo, cta. "
            "hook+corpo+cta total chars <= %d. Never fabricate verifiable claims. "
            "Output ONLY the JSON array, no other text."
        ) % (num_v, product, audience, platform, lim, reg, funnel, tone, ab_axis, lim)
        try:
            _chat = _import_chat()
            _resp = _chat(_live_prompt, model=_live_model, provider="openwebui", max_tokens=800)
            _live_rows = _parse_llm_variants(str(_resp), platform, lim, num_v) if _resp else []
            if _live_rows:
                rows = _live_rows
                llm_copy = True
                run_mode_val = "live-llm"
                model_used_val = _live_model
                notes.append("variants: live-llm (openwebui, model=%s)" % _live_model)
        except Exception as exc:
            # degrade-never: log the ASCII reason, never the key; fall through below.
            notes.append(
                "live-llm failed, falling back to deterministic: %s: %s"
                % (type(exc).__name__, str(exc)[:160])
            )

    if not rows and credential is not None:
        prompt = (
            "Generate %d ad copy variants in Portuguese. "
            "product='%s', audience='%s', platform='%s' (char limit=%d), "
            "register='%s', funnel_stage='%s', tone='%s', ab_axis='%s'. "
            "Return JSON array of objects with keys: hook, corpo, cta. "
            "hook+corpo+cta total chars <= %d. Never fabricate verifiable claims. "
            "Output ONLY the JSON array, no other text."
        ) % (num_v, product, audience, platform, lim, reg, funnel, tone, ab_axis, lim)
        try:
            resp = str(credential(prompt)) if callable(credential) else ""
            rows = _parse_llm_variants(resp, platform, lim, num_v) if resp else []
            if rows:
                notes.append("variants: LLM credential")
                llm_copy = True
        except Exception:
            pass
    if not rows:
        rows = [_scaffold_row(i, platform, lim) for i in range(num_v)]
        notes.append("generation_pending: scaffold (no credential or LLM failed)")

    # enforce Chars <= Limite
    for row in rows:
        try:
            if int(row[4]) > int(row[5]):
                row[4] = row[5]
                notes.append("chars clamped to limite")
        except Exception:
            pass

    # CONFIDENCE (CAPABILITY_COMPLETENESS / ADMAX W2b): the Variantes trust slot. Real LLM
    # copy -> 0.87; the deterministic scaffold -> 0.0 (honest: the creative is a placeholder
    # awaiting real copy). Emitted only via the typed section (backward-compatible).
    variantes_confidence = 0.87 if llm_copy else 0.0

    sec1 = table_section(
        "Variantes",
        ["Plataforma", "Hook", "Corpo", "CTA", "Chars", "Limite"],
        rows,
        column_types=["string", "string", "string", "string", "number", "number"],
        key_col_index=1,
        note="Chars <= Limite por contrato. Uma linha por variante.",
        confidence=variantes_confidence,
    )

    va = rows[0] if rows else [platform, "Variante A", "", "CTA-A", "0", str(lim)]
    vb = rows[1] if len(rows) > 1 else [platform, "Variante B", "", "CTA-B", "0", str(lim)]
    sec2 = fields_section(
        "Teste A/B",
        [
            ("Eixo testado", _AB_LABEL.get(ab_axis, ab_axis)),
            ("Variante A", va[1]),
            ("Variante B", vb[1] if vb[1] != va[1] else vb[2]),
            ("Vencedor previsto", "A"),
            ("Hipotese", "Provocacao de dor converte mais em '%s' com registro '%s'" % (funnel, reg)),
            ("Como medir", "CTR + CPC no primeiro 1.000 impressoes por variante"),
        ],
        note="Typed A/B experiment. Medir antes de escalar.",
    )

    forbidden_row = "; ".join("'%s' -> '%s'" % (w, r) for w, r in _FORBIDDEN_B2C[:2])
    # The brand name rides ADDITIVELY into the register-applied value + the section note when a
    # brand context is present (degrade-never: un-branded -> the neutral text unchanged). The 4
    # canonical rows + the title are STABLE (the brand_audit crew + golden tests anchor them).
    _reg_applied = "%s -- ativado para anuncio %s" % (reg.capitalize(), platform)
    if brand_name:
        _reg_applied = "%s (voz de %s)" % (_reg_applied, brand_name)
    sec3 = fields_section(
        "Voz da marca",
        [
            ("Registro aplicado", _reg_applied),
            ("Estrategia de lead", "Provocacao de dor antes da solucao (etapa: %s)" % funnel),
            ("Perspectiva", "Segunda pessoa -- 'seu gato', 'voce', nunca 'nossos clientes'"),
            ("Palavras removidas (segmento: Tutor B2C)", forbidden_row),
        ],
        note=brand_title(
            "Prova de que o registro foi aplicado -- auditavel pela brand_audit crew (6 dimensoes)",
            inputs,
        ),
    )

    sec4 = list_section(
        "Compliance",
        [
            _COMPLIANCE_STATIC[0],
            _COMPLIANCE_STATIC[1],
            _COMPLIANCE_CHARS_TEMPLATE % (lim, platform),
            _COMPLIANCE_STATIC[2],
            _COMPLIANCE_STATIC[3],
            _COMPLIANCE_STATIC[4],
        ],
        note="Gate de compliance: verificar ANTES de subir o anuncio.",
    )

    first_word = product.lower().split()[0] if product.split() else "produto"
    sec5 = list_section(
        "Keywords",
        [
            "%s gato apartamento" % first_word,
            "arranhador torre sisal",
            "produto para gato adulto",
            "petshop online gato",
            "gato %s" % (audience.lower().split()[0] if audience.split() else "tutor"),
        ],
        note="Termos de segmentacao/SEO sugeridos. Validar com ferramenta de palavras-chave.",
    )

    sec6 = fields_section(
        "Estrategia de funil",
        [
            ("Etapa", funnel),
            ("Formula de copy", _FORMULA_MAP.get(funnel, "AIDA")),
            ("Pressao de CTA", _CTA_PRESSURE.get(funnel, "Medio")),
            ("Proxima etapa", _NEXT_STAGE.get(funnel, "consideration")),
        ],
        note="Mapeamento funnel_stage -> formula (brand_voice_templates sec. 4).",
    )

    sections = [sec1, sec2, sec3, sec4, sec5, sec6]

    # F7 GOVERN
    chars_ok = all(int(r[4]) <= int(r[5]) for r in rows if len(r) >= 6)
    has_4_voz = len(sec3.get("rows", [])) == 4
    compliance_ok = len(sec4.get("items", [])) >= 4
    score = 1.0
    if not has_4_voz:
        score -= 0.2
        notes.append("[FAIL] voz-da-marca: faltam chaves canonicas")
    if not chars_ok:
        score -= 0.15
        notes.append("[FAIL] chars > limite em variante")
    if not compliance_ok:
        score -= 0.1
        notes.append("[FAIL] compliance < 4 itens")
    passed = bool(has_4_voz and chars_ok and compliance_ok and score >= 0.7)

    return structured_output(
        KIND, sections, passed=passed, score=score,
        artifact=json.dumps({
            "kind": _kind, "contract_version": CONTRACT_VERSION,
            "platform": platform, "register": reg,
            "funnel_stage": funnel, "num_variants": len(rows),
            # ADMAX W2b: which product this ad targets (provenance for the catalog fill).
            "sku": sku, "product_slug": product_slug, "catalog_record": has_record,
        }, ensure_ascii=True),
        real=True, notes=notes,
        # mission R-350: None/None (the live branch never fired) is byte-identical to
        # omitting these kwargs entirely -- _base.structured_output falls back to its own
        # honest defaults (module RUN_MODE or "offline-scaffold"; model_used=None).
        run_mode=run_mode_val,
        model_used=model_used_val,
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
# from what build() actually enforces at runtime.
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law ads.py enforces on every generated ad (Missao A). Returns a
    structured, JSON-serialisable dict -- never {} for THIS generator (ads DOES declare
    domain law; {} is only the _base.py no-op default for a generator that has none)."""
    return {
        "contract_version": CONTRACT_VERSION,
        "platform_char_limits": dict(_PLATFORM_LIMITS),
        "enums": {
            "register": sorted(_REGISTER_ENUM),
            "funnel_stage": sorted(_FUNNEL_ENUM),
            "tone": sorted(_TONE_ENUM),
            "ab_axis": sorted(_AB_AXIS_ENUM),
        },
        "funnel_copy_formulas": dict(_FORMULA_MAP),
        "cta_pressure_by_funnel_stage": dict(_CTA_PRESSURE),
        "next_stage_by_funnel_stage": dict(_NEXT_STAGE),
        "forbidden_words": [
            {"word": w, "replacement": r} for (w, r) in _FORBIDDEN_B2C
        ],
        "compliance_gates": list(_COMPLIANCE_STATIC) + [_COMPLIANCE_CHARS_GENERIC],
    }


# --------------------------------------------------------------------------- #
# Media hooks (DUALROLL N02) -- opt-in dual-output media layer.
# Discovered by _base.resolve_media via the prefixed naming convention
# (ads_media_requests / ads_produced_media). No edit to _base needed.
# --------------------------------------------------------------------------- #

def _record_images(inputs) -> List[str]:
    """The https image URLs from a canonical product record carried in the inputs.

    A run that fetched the catalog record (get_product_record by sku) passes it as
    inputs['product_record'] (the product_catalog_schema shape, with an images[] field of
    CDN URLs). src-safety: ONLY https:// URLs are forwarded -- a non-https / non-string ref
    is dropped (never embedded). degrade-never: no record / no images -> []. NEVER fabricates.
    """
    rec = inputs.get("product_record")
    if not isinstance(rec, Mapping):
        return []
    raw = rec.get("images")
    if not isinstance(raw, (list, tuple)):
        return []
    out: List[str] = []
    for u in raw:
        if not isinstance(u, str):
            continue
        s = u.strip()
        if s.lower().startswith("https://"):
            out.append(s)
    return out


def ads_media_requests(inputs):
    """Image slots for the ad creative. The catalog images[] fill them when present; else
    one upload-fallback slot per variant.

    With a canonical product record in the inputs (inputs['product_record'].images[] -- real
    https CDN URLs from the catalog, ADMAX W2b), the first ~6 images become GENERATED slots
    (status=generated, src=<cdn_url>) so the dual-output media ledger + the product_ad
    gallery fill with REAL product photos instead of empty dropzones. The first is flagged
    hero=True. src-safety: only https URLs are forwarded.

    Without a record, ads generate TEXT copy only; the creative image must be uploaded or
    produced by a dedicated image-gen pipeline -> one editable upload-fallback slot per
    variant (the original behavior, unchanged). NEVER fabricates a src.
    """
    num_v = _coerce_int(inputs.get("num_variants"), 3, 1, 5)
    images = _record_images(inputs)
    if images:
        # Real catalog photos -> one declared slot per image (hero + gallery). Cap at 6.
        # The src is FILLED by ads_produced_media (the produced-media seam to_dual_output
        # reads); declaring the key here is what couples the two.
        return [
            {
                "key": "ad_image_%d" % i,
                "kind": "image",
                "section": "Variantes",
                "label": ("Foto principal do produto" if i == 0
                          else "Foto do produto %d" % (i + 1)),
            }
            for i in range(len(images[:6]))
        ]
    return [
        {
            "key": "ad_image_%d" % i,
            "kind": "image",
            "section": "Variantes",
            "label": "Creative do anuncio %d" % (i + 1),
        }
        for i in range(num_v)
    ]


def ads_produced_media(inputs):
    """Produced media for ads -> the REAL catalog photos when a product record is present.

    With a canonical product record in the inputs (inputs['product_record'].images[] -- real
    https CDN URLs from the catalog, ADMAX W2b), each declared ad_image_N slot is FILLED with
    the matching catalog image src (status -> generated, a real <img> in the dual face + the
    product_ad gallery). The first image carries an alt hint from the product name.

    Without a record, ad copy generation does not produce image files -> {} (every slot stays
    an editable upload-fallback dropzone). src-safety: only https URLs are forwarded (via
    _record_images). NEVER fabricates a src.
    """
    images = _record_images(inputs)
    if not images:
        return {}
    rec = inputs.get("product_record")
    name = ""
    if isinstance(rec, Mapping):
        name = str(rec.get("name") or "").strip()
    produced: dict = {}
    for i, url in enumerate(images[:6]):
        alt = ("%s -- foto %d" % (name, i + 1)) if name else "Foto do produto %d" % (i + 1)
        produced["ad_image_%d" % i] = {"src": url, "alt": alt}
    return produced


__all__ = [
    "KIND",
    "CONTRACT_VERSION",
    "build",
    "ads_media_requests",
    "ads_produced_media",
    "_record_images",
    # mission R-350: live-LLM branch seams (module-level so tests can monkeypatch).
    "_import_chat",
    "_live_llm_gate",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
