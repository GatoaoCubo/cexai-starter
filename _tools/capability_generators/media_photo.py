#!/usr/bin/env python3
# -*- coding: ascii -*-
"""media_photo -- N02 CAPGEN Wave 1: multi-surface photo brief generator (LLM-creative lane).

KIND = "media_photo" (capability #7, N02; CEX kind = multimodal_prompt).
6 inputs -> 6 output sections: Brief / Iluminacao + camera / Shot list /
Brand fit / Negative prompt / Compliance / uso.

LLM-creative: calls credential(prompt) -> JSON for shot list + creative direction.
Degrade-never: deterministic scaffold when credential absent or fails.
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

KIND = "media_photo"
CONTRACT_VERSION = "1.0.0"

_STYLE_ENUM = {"lifestyle", "packshot", "editorial", "minimalista"}
_REGISTER_ENUM = {"warm", "bold", "playful"}

# Default aspect ratios per register (visual direction mapping)
_REGISTER_ASPECT: dict = {
    "warm": ["4:5", "1:1"],
    "bold": ["4:5", "9:16", "1:1"],
    "playful": ["9:16", "4:5", "1:1"],
}

# Camera/lighting baseline per register
_LIGHTING: dict = {
    "warm": [
        ("Luz", "Natural difusa, janela lateral ou reflector branco"),
        ("Lente", "50mm f/1.8 -- bokeh suave para aconchego"),
        ("Angulo", "Eye-level ou ligeiramente acima -- perspectiva do tutor"),
        ("Fundo", "Parede neutra ou sofa claro, planta desfocada"),
        ("Temperatura", "5500K -- luz do dia, branco quente"),
    ],
    "bold": [
        ("Luz", "Estudio com softbox lateral + fill light minimo"),
        ("Lente", "35mm f/2.8 -- campo aberto, produto dominante"),
        ("Angulo", "3/4 frontal baixo -- produto heroico"),
        ("Fundo", "Fundo preto ou cinza escuro, alto contraste"),
        ("Temperatura", "6500K -- frio e preciso"),
    ],
    "playful": [
        ("Luz", "Natural brilhante + rebatedor colorido lateral"),
        ("Lente", "24mm f/2.8 -- wide, movimento e energia"),
        ("Angulo", "Levemente abaixo ou nivel do pet -- dinamico"),
        ("Fundo", "Cores vibrantes ou estampas geometricas"),
        ("Temperatura", "6000K -- vivido, saturado"),
    ],
}

# Negative prompts per register
_NEGATIVE: dict = {
    "warm": ["corte abrupto ou enquadramento tenso", "cores saturadas ou neon", "flash direto"],
    "bold": ["fundo poluido ou desfocado demais", "suavidade excessiva", "angulo neutro"],
    "playful": ["tons neutros/acinzentados sem pop", "composicao estatica", "fundo branco simples"],
}


def _pick(val: Any, valid: set, default: str) -> str:
    s = str(val or "").strip().lower()
    return s if s in valid else default


def _coerce_int(val: Any, default: int, lo: int, hi: int) -> int:
    try:
        return max(lo, min(hi, int(float(val))))
    except Exception:
        return default


def _coerce_aspects(val: Any) -> List[str]:
    if isinstance(val, (list, tuple)):
        return [str(x).strip() for x in val if str(x).strip()] or ["4:5"]
    if isinstance(val, str) and val.strip():
        return [p.strip() for p in val.replace(";", ",").split(",") if p.strip()] or ["4:5"]
    return ["4:5"]


def _intent_for_aspect(aspect: str) -> str:
    mapping: dict = {
        "4:5": "Feed principal (Instagram/Facebook) -- produto hero",
        "9:16": "Stories/Reels -- formato vertical imersivo",
        "1:1": "Grid quadrado / packshot e-commerce",
        "16:9": "Banner web / YouTube thumbnail",
        "3:4": "Pinterest / portrait editorial",
    }
    return mapping.get(aspect, "Formato %s -- adaptar composicao" % aspect)


def _scaffold_shots(num: int, aspects: List[str], style: str) -> List[List[str]]:
    templates = [
        ("Shot 1 -- produto isolado", "Estabelecer produto como hero: forma + material + escala"),
        ("Shot 2 -- pet interagindo", "Prova de uso: gato no produto, comportamento natural"),
        ("Shot 3 -- ambiente lifestyle", "Contexto emocional: produto integrado ao lar"),
        ("Shot 4 -- detalhe de material", "Credibilidade tecnica: sisal, estrutura, acabamento"),
        ("Shot 5 -- CTA visual", "Shot de conversao: produto + preco/oferta visivel"),
        ("Shot 6 -- angulo criativo", "Diferenciar: perspectiva incomum, composicao ousada"),
        ("Shot 7 -- embalagem + unboxing", "Confianca de compra online: o que o cliente recebe"),
        ("Shot 8 -- comparativo de escala", "Contextualizar tamanho: produto + item conhecido"),
    ]
    rows: List[List[str]] = []
    for i in range(num):
        label, intent = templates[i % len(templates)]
        aspect = aspects[i % len(aspects)]
        rows.append([label, intent + " (generation_pending)", _intent_for_aspect(aspect)])
    return rows


def _parse_llm_shots(raw: str, aspects: List[str], num: int) -> List[List[str]]:
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            return []
        rows: List[List[str]] = []
        for i, item in enumerate(data[:num]):
            if not isinstance(item, dict):
                continue
            label = str(item.get("shot") or "Shot %d" % (i + 1))
            intent = str(item.get("intencao") or "")
            aspect = str(item.get("aspect") or aspects[i % len(aspects)])
            rows.append([label, intent, _intent_for_aspect(aspect)])
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
    scene = str(inputs.get("scene") or "").strip() or "Cena nao informada"
    subject = str(inputs.get("subject") or "").strip() or "Sujeito nao informado"
    style = _pick(inputs.get("style"), _STYLE_ENUM, "lifestyle")
    reg = _pick(inputs.get("register"), _REGISTER_ENUM, "warm")
    aspects = _coerce_aspects(inputs.get("aspect_ratios"))
    num_shots = _coerce_int(inputs.get("num_shots"), 5, 1, 8)

    # BRAND_MUSTACHE: frame the photo brief for THIS tenant from the brand context the run path
    # injected. This also REMOVES the previously HARDCODED tenant name from the Brand fit palette --
    # the palette now names the resolved tenant brand (or stays neutral un-branded). The 6-section
    # shape + the Brand fit 4-row fields layout stay STABLE (tests assert layout==fields); the
    # brand rides the EXISTING "Paleta" row VALUE + a note on the Brand fit section.
    # Un-branded -> neutral palette, no note delta (degrade-never). NEVER hardcodes the brand.
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    # F6 PRODUCE -- shot list via LLM or scaffold
    shot_rows: List[List[str]] = []
    if credential is not None:
        prompt = (
            "Generate a photo brief shot list in Portuguese for a pet product photo shoot. "
            "scene='%s', subject='%s', style='%s', register='%s', aspect_ratios=%s. "
            "Return JSON array of %d objects with keys: shot (label), intencao (persuasive intent), "
            "aspect (target aspect ratio from %s). "
            "Each intent must explain WHY the shot converts, not just what it shows. "
            "Output ONLY the JSON array."
        ) % (scene, subject, style, reg, json.dumps(aspects), num_shots, json.dumps(aspects))
        try:
            resp = str(credential(prompt)) if callable(credential) else ""
            shot_rows = _parse_llm_shots(resp, aspects, num_shots) if resp else []
            if shot_rows:
                notes.append("shot list: LLM credential")
        except Exception:
            pass
    if not shot_rows:
        shot_rows = _scaffold_shots(num_shots, aspects, style)
        notes.append("generation_pending: scaffold shot list (no credential or LLM failed)")

    mood_map: dict = {
        "warm": "Aconchego domestico -- luz natural, texturas, conexao emocional com o pet",
        "bold": "Hero de produto -- alto contraste, foco tecnico, autoridade visual",
        "playful": "Energia e cor -- movimento, alegria, vibes de redes sociais",
    }

    # Section 1: Brief
    sec1 = fields_section(
        "Brief",
        [
            ("Cena", scene),
            ("Sujeito", subject),
            ("Estilo", style),
            ("Proporcoes alvo", ", ".join(aspects)),
            ("Mood (creative direction)", mood_map.get(reg, "Registro %s" % reg)),
        ],
        note="Direcionamento criativo ANTES do set. Compartilhar com fotografo antes da sessao.",
    )

    # Section 2: Iluminacao + camera (table)
    light_rows = _LIGHTING.get(reg, _LIGHTING["warm"])
    sec2 = table_section(
        "Iluminacao + camera",
        ["Parametro", "Valor"],
        [[row[0], row[1]] for row in light_rows],
        column_types=["string", "string"],
        key_col_index=0,
        note="Setup de camera e luz para registro '%s'. Ajustar conforme ambiente real." % reg,
    )

    # Section 3: Shot list (table)
    sec3 = table_section(
        "Shot list",
        ["Shot", "Intencao persuasiva", "Aspect alvo"],
        shot_rows,
        column_types=["string", "string", "string"],
        key_col_index=0,
        note="Cada shot declara por que converte (intencao) e onde vai (aspect). "
             "Aspecto alvo = superficie de destino do shot.",
    )

    # Section 4: Brand fit -- the palette names the RESOLVED tenant brand (never a hardcoded
    # real tenant name); un-branded -> a neutral palette. This is the visible brand consumption.
    if brand_name:
        _paleta = "Preto / branco / cinza claro -- paleta da marca %s; accent cor do produto" % brand_name
    else:
        _paleta = "Preto / branco / cinza claro -- paleta neutra; accent cor do produto"
    _brandfit_note = "Verificar apos selecao: paleta + tom + ausencia de marcas de terceiros."
    if _bnote:
        _brandfit_note = "%s %s" % (_brandfit_note, _bnote)
    sec4 = fields_section(
        "Brand fit",
        [
            ("Paleta", _paleta),
            ("Tom visual", "%s -- mood da sessao alinhado ao registro" % reg),
            ("Sem logos de terceiros", "Nenhuma marca de terceiro visivel no frame (regra de compliance)"),
            ("Consistencia com o feed", "Enquadramento + temperatura de cor alinhados ao grid atual"),
        ],
        note=_brandfit_note,
    )

    # Section 5: Negative prompt (list)
    neg_base = _NEGATIVE.get(reg, [])
    neg_items = list(neg_base) + [
        "Claim de saude ou terapeutico no texto sobreposto sem aprovacao",
        "Promessa visual nao-verificavel (ex: produto maior do que e na realidade)",
        "Sombras duras nao intencionais que escondem detalhes do produto",
    ]
    sec5 = list_section(
        "Negative prompt",
        neg_items,
        note="O que evitar: estetico + brand-safety. Aplicar na selecao das fotos.",
    )

    # Section 6: Compliance / uso (list)
    sec6 = list_section(
        "Compliance / uso",
        [
            "Direitos de imagem: fotos de clientes reais so com consentimento escrito assinado",
            "Sem marca de terceiro visivel sem autorizacao de uso de marca",
            "Rotulo 'imagem ilustrativa' quando a foto diferir do produto entregue ao cliente",
            "Animal welfare: nenhum pet deve ser forcado a posicao desconfortavel para o shot",
            "Nao usar foto de pet alheio sem permissao explicita do tutor",
        ],
        note="Compliance de uso de imagem. Verificar ANTES de publicar qualquer foto.",
    )

    sections = [sec1, sec2, sec3, sec4, sec5, sec6]

    # F7 GOVERN
    has_shots = len(shot_rows) >= 1
    all_3_cols = all(len(r) == 3 for r in shot_rows)
    compliance_ok = len(sec6.get("items", [])) >= 4
    score = 1.0
    if not has_shots:
        score -= 0.2
        notes.append("[FAIL] shot list vazia")
    if not all_3_cols:
        score -= 0.1
        notes.append("[FAIL] shot list rows sem 3 colunas")
    if not compliance_ok:
        score -= 0.1
        notes.append("[FAIL] compliance < 4 itens")
    passed = bool(has_shots and all_3_cols and compliance_ok and score >= 0.7)

    return structured_output(
        KIND, sections, passed=passed, score=score,
        artifact=json.dumps({
            "kind": _kind, "contract_version": CONTRACT_VERSION,
            "style": style, "register": reg,
            "aspects": aspects, "num_shots": len(shot_rows),
        }, ensure_ascii=True),
        real=True, notes=notes,
    )


# --------------------------------------------------------------------------- #
# Media helpers (public -- called by tests and the edge runtime).
# --------------------------------------------------------------------------- #

def _mp_num_shots(inputs: Mapping[str, Any]) -> int:
    """Resolve num_shots from inputs, clamped [1, 8], default 5. TOTAL."""
    try:
        val = inputs.get("num_shots")
        if val is None:
            return 5
        return max(1, min(8, int(float(val))))
    except Exception:
        return 5


def _mp_parse_urls(inputs: Mapping[str, Any]) -> List[str]:
    """Parse inputs['photos'] or inputs['photo_urls'] into a list of URL strings. TOTAL."""
    raw = inputs.get("photos") or inputs.get("photo_urls") or ""
    if isinstance(raw, (list, tuple)):
        return [str(u).strip() for u in raw if str(u).strip()]
    raw_str = str(raw).strip()
    if not raw_str:
        return []
    if raw_str.startswith("["):
        try:
            parsed = json.loads(raw_str)
            if isinstance(parsed, list):
                return [str(u).strip() for u in parsed if str(u).strip()]
        except Exception:
            pass
    return [u.strip() for u in raw_str.split(",") if u.strip()]


def media_photo_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Build the media_requests list for cex_dual_output.to_dual_output from photo brief inputs.

    Declares one image slot per shot (photo_0..photo_{n-1}) where n = num_shots from inputs
    (clamped [1, 8], default 5). Each slot corresponds to a row in the Shot list section.
    Slots without a supplied URL stay upload-fallback (to be filled after the photo session).
    NEVER-FABRICATE: no src is produced here. PURE + TOTAL: never raises."""
    n = _mp_num_shots(inputs)
    return [
        {
            "key": "photo_%d" % i,
            "kind": "image",
            "section": "Shot list",
            "label": "Foto %d" % (i + 1),
        }
        for i in range(n)
    ]


def media_photo_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Build the produced_media dict for cex_dual_output.to_dual_output from photo brief inputs.

    Maps photo_N slots to a real image src ONLY when inputs['photos'] or inputs['photo_urls']
    supplies a non-empty URL for that index. Un-supplied or blank-URL slots stay upload-fallback
    (status='empty', no src) in to_dual_output. NEVER-FABRICATE. PURE + TOTAL: never raises."""
    urls = _mp_parse_urls(inputs)
    produced: Dict[str, Any] = {}
    for i, url in enumerate(urls):
        url = url.strip()
        if url:
            produced["photo_%d" % i] = {"src": url, "alt": "Foto %d" % (i + 1)}
    return produced


__all__ = [
    "KIND",
    "CONTRACT_VERSION",
    "build",
    "media_photo_media_requests",
    "media_photo_produced_media",
]
