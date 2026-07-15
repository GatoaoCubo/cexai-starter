#!/usr/bin/env python3
# -*- coding: ascii -*-
"""content_monetization capability generator -- N06 unit-economics lane (CAPGEN Wave 1).

PURE MATH: no LLM, no network. Derives tier pricing from wtp_band + gross_margin; computes
margins, anchoring, and contribution-margin verdict from 8 contract inputs.
DEGRADE-NEVER: guards division-by-zero and non-finite results.
"""
from __future__ import annotations

import json
import math
import re
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

KIND = "content_monetization"
CAPABILITY = "pricing"  # council A4: the generator registers by SLUG, not KIND
CONTRACT_VERSION = "1.0.0"
# Universal-envelope honest run_mode (mission CAPABILITY_COMPLETENESS W1): REAL deterministic
# math (no LLM), so it declares offline-deterministic. _base.structured_output reads it.
RUN_MODE = "offline-deterministic"

MOEDA = "R$"  # house style; not a contract input

# Tier labels (fixed shape per contract output spec)
_TIER_LABELS = ["Basico", "Plus", "Premium"]


def _segment_posture(segment: str) -> str:
    """Strategic pricing posture for a customer ``segment`` (CAPABILITY_COMPLETENESS W1
    bug-fix #5: the ``segment`` input was accepted but never moved the output).

    A DETERMINISTIC keyword heuristic -- HONEST guidance, never a fabricated market datum.
    Different segments yield different postures (recurring vs transactional vs enterprise vs
    generic), so the input now genuinely drives the notes + the monetization verdict. An
    unrecognized / empty segment gets the neutral default."""
    s = (segment or "").lower()
    if any(k in s for k in ("recorrente", "assinatura", "subscription", "tutor", "saas")):
        return ("perfil recorrente -- enfatizar plano anual com lock-in e gating por uso "
                "continuo; expansao via limite de uso")
    if any(k in s for k in ("avulso", "unico", "one-time", "transacional", "varejo")):
        return ("perfil transacional -- enfatizar bundles de valor e upsell por ticket; "
                "menos peso em lock-in anual")
    if any(k in s for k in ("enterprise", "corporativo", "b2b", "empresa")):
        return ("perfil enterprise -- ancorar no tier alto, contratos anuais e SLA dedicado; "
                "negociar volume")
    return ("perfil generico -- manter ancoragem no tier do meio; revisar a estrategia com "
            "dados reais do segmento")


def _fmt(val: float) -> str:
    if not math.isfinite(val):
        return "N/A"
    return "%s %.0f" % (MOEDA, val)


def _pct_ratio(num: float, denom: float) -> str:
    if not denom or not math.isfinite(num) or not math.isfinite(denom):
        return "N/A"
    return "%.1f%%" % (num / denom * 100.0)


def _parse_wtp_band(band: str) -> tuple:
    """Extract (low, high) from a string like 'R$ 49-129'. Returns floats."""
    nums = re.findall(r"\d+(?:\.\d+)?", str(band))
    if len(nums) >= 2:
        return float(nums[-2]), float(nums[-1])
    if len(nums) == 1:
        v = float(nums[0])
        return v * 0.4, v
    return 29.0, 149.0  # contract-example fallback


@register(CAPABILITY)  # council A4: SLUG is the sole generator key (was KIND=content_monetization)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> "Any":
    """``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND."""
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # F1 CONSTRAIN: read EXACTLY the contract input keys (capability_contracts_v1.0.md section 2).
    def _f(key, default):
        v = inputs.get(key)
        return float(v) if v is not None else float(default)

    product        = str(inputs.get("product") or "Produto")
    segment        = str(inputs.get("segment") or "")
    num_tiers      = max(2, min(4, int(_f("num_tiers", 3))))
    billing_period = str(inputs.get("billing_period") or "mensal")
    anchor_tier    = str(inputs.get("anchor_tier") or "Plus")
    gross_margin   = _f("gross_margin", 0.75)
    value_metric   = str(inputs.get("value_metric") or "unidades")
    wtp_band       = str(inputs.get("wtp_band") or "R$ 29-149")

    wtp_low, wtp_high = _parse_wtp_band(wtp_band)
    if wtp_low <= 0:
        wtp_low = 1.0
        notes.append("wtp_band low <= 0; clamped to 1")
    if wtp_high <= wtp_low:
        wtp_high = wtp_low * 3.0
        notes.append("wtp_band high <= low; set to 3x low")

    # Derive 3 tier prices from band (low -> mid -> high)
    preco_basico  = wtp_low
    preco_anchor  = (wtp_low + wtp_high) / 2.0
    preco_premium = wtp_high

    # Guard prices
    if preco_basico <= 0:
        preco_basico = 1.0
        notes.append("preco_basico <= 0; clamped to 1")
    if preco_anchor <= 0:
        preco_anchor = 1.0
        notes.append("preco_anchor <= 0; clamped to 1")
    if preco_premium <= 0:
        preco_premium = 1.0
        notes.append("preco_premium <= 0; clamped to 1")

    # COGS derived from gross_margin target: cogs = price * (1 - gm)
    gm_factor = 1.0 - gross_margin
    cogs_basico  = preco_basico  * gm_factor
    cogs_anchor  = preco_anchor  * gm_factor
    cogs_premium = preco_premium * gm_factor

    # Margins (should all equal gross_margin when gm_factor is applied)
    margem_basico  = (preco_basico  - cogs_basico)  / preco_basico  if preco_basico  > 0 else 0.0
    margem_anchor  = (preco_anchor  - cogs_anchor)  / preco_anchor  if preco_anchor  > 0 else 0.0
    margem_premium = (preco_premium - cogs_premium) / preco_premium if preco_premium > 0 else 0.0

    # Anti-cannibalization: premium should be >= 1.5x anchor
    ratio_prem_anchor = preco_premium / preco_anchor if preco_anchor > 0 else 0.0
    canni_ok = ratio_prem_anchor >= 1.5

    # Determine which column gets (*) based on anchor_tier input
    anchor_lower = anchor_tier.lower()
    if anchor_lower in ("basico", "basic", "0"):
        anchor_pos = 0
    elif anchor_lower in ("premium", "best", "2"):
        anchor_pos = 2
    else:
        anchor_pos = 1  # default: "Plus"

    col_labels = [
        (_TIER_LABELS[i] + " (*)") if i == anchor_pos else _TIER_LABELS[i]
        for i in range(3)
    ]

    prices  = [preco_basico,  preco_anchor,  preco_premium]
    cogs    = [cogs_basico,   cogs_anchor,   cogs_premium]
    margens = [margem_basico, margem_anchor, margem_premium]

    # Annual framing on anchor tier
    annual_anchor     = prices[anchor_pos] * 12.0 * 0.80
    monthly_equiv_ann = annual_anchor / 12.0

    # F6 PRODUCE

    # BRAND_MUSTACHE: frame the output for THIS tenant from the brand context the run path
    # injected. The section TITLE stays stable (a media slot anchors to it + golden tests assert
    # it); the brand framing rides an ADDITIVE section ``note`` + a provenance note + the verdict
    # row, so an un-branded run is byte-identical (degrade-never; no note added).
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    # Section 1: Planos (dados simulados) -- title STABLE; brand-frame note when tenant-branded.
    planos = table_section(
        "Planos (dados simulados)",
        ["Recurso"] + col_labels,
        [
            ["Preco/mes"] + [_fmt(p) for p in prices],
            ["COGS"]      + [_fmt(c) for c in cogs],
            ["Margem bruta"] + [
                _pct_ratio(prices[i] - cogs[i], prices[i]) for i in range(3)
            ],
            [value_metric + "/mes", "ate 10", "ate 50", "ilimitado"],
            ["Brinquedo (add-on)",  "nao", "sim", "sim"],
            ["Frete gratis",        "nao", "nao", "sim"],
            ["Desconto anual",      "nao", "20%", "20%"],
            ["Consultoria",         "nao", "nao", "1h/mes"],
        ],
        key_col_index=0,
        note=_bnote,  # brand-frame note when tenant-branded; None -> no note (degrade-never)
        contract_version=CONTRACT_VERSION,
    )

    # Section 2: Logica de ancoragem
    canni_label = (
        "[OK] Premium %.1fx ancora -- diferenciacao adequada" % ratio_prem_anchor
        if canni_ok
        else "[WARN] Premium %.1fx ancora -- muito proximo, risco de canibalizacao" % ratio_prem_anchor
    )
    anchor_label = col_labels[anchor_pos]
    ancoragem = fields_section(
        "Logica de ancoragem",
        [
            {"label": "Plano-ancora",
             "value": "%s -- maximiza conversao para o tier do meio" % anchor_label},
            {"label": "Anchor alto (decoy)",
             "value": "Premium %s faz %s parecer acessivel" % (_fmt(preco_premium), anchor_label)},
            {"label": "Captura de preco (downgrade guard)",
             "value": "Basico limitado a 10 %s/mes; expansao natural para %s" % (value_metric, anchor_label)},
            {"label": "Framing anual",
             "value": "%s anual = %s/ano (%s/mes equiv) [%s]" % (
                 anchor_label, _fmt(annual_anchor), _fmt(monthly_equiv_ann), billing_period)},
            {"label": "Cannibalizacao", "value": canni_label},
        ],
        contract_version=CONTRACT_VERSION,
    )

    # Section 3: Gating de valor
    gating = list_section(
        "Gating de valor",
        [
            "Basico: ate 10 %s/mes -- converte quem quer testar sem compromisso" % value_metric,
            "Plus: ate 50 %s/mes + suporte prioritario -- ancora da receita recorrente" % value_metric,
            "Premium: ilimitado + consultoria 1h/mes -- retencao de contas enterprise",
            "Trigger de expansao: uso > 80%% do limite -> upsell automatico sugerido para tier acima",
            "Trigger de retencao: 2 meses abaixo de 20%% do limite -> risco de downgrade; acionar CSM",
        ],
        contract_version=CONTRACT_VERSION,
    )

    # Section 4: Veredito de monetizacao
    ancora_ok_str = (
        "[OK] Margem ancora = %.1f%%" % (margens[anchor_pos] * 100)
        if margens[anchor_pos] > 0
        else "[FAIL] Margem ancora negativa -- revisar gross_margin do tier ancora"
    )
    # segment now MOVES the output (bug-fix #5): a strategic posture drives both a note AND
    # the MRR-mix verdict row, instead of the input being silently dropped. The section SHAPE
    # is frozen at 4 rows -- segment enriches an existing row value, it does not add a row.
    posture = _segment_posture(segment)
    if segment:
        notes.append("Segmento '%s': %s" % (segment, posture))
    seg_note = ("Segmento: %s" % segment) if segment else "Segmento nao especificado"
    # BRAND_MUSTACHE: a branded run names the tenant in the MRR-mix verdict (same template,
    # tenant-filled); an un-branded run keeps the neutral framing (byte-identical). The SHAPE is
    # unchanged (one row value enriched), so the frozen 4-row verdict + tests still hold.
    _brand_prefix = ("%s -- " % brand_name) if brand_name else ""
    mrr_value = "%s60%% %s + 25%% Premium + 15%% Basico (mix saudavel de expansao). %s" % (
        _brand_prefix, anchor_label, posture,
    )
    veredito = fields_section(
        "Veredito de monetizacao",
        [
            {"label": "Ancora lucrativa?",    "value": ancora_ok_str},
            {"label": "Caveat principal",
             "value": "COGS por tier derivados de gross_margin=%.0f%%; validar com dados reais" % (gross_margin * 100)},
            {"label": "Payback_period estimado (mock)",
             "value": "3-6 meses (estimado -- depende de CAC nao fornecido); %s" % seg_note},
            {"label": "MRR-mix recomendado", "value": mrr_value},
        ],
        contract_version=CONTRACT_VERSION,
    )

    # F7 GOVERN
    passed = True
    score = 0.9
    if gross_margin <= 0:
        notes.append("F7 [FAIL]: margem invalida -- gross_margin <= 0")
        passed = False
        score = min(score, 0.5)
    elif gross_margin >= 1.0:
        notes.append("F7 [FAIL]: margem invalida -- gross_margin >= 1.0")
        passed = False
        score = min(score, 0.5)
    if not canni_ok:
        notes.append("F7 [WARN]: cannibalizacao -- ratio_prem_anchor %.2f < 1.5" % ratio_prem_anchor)
        score = min(score, 0.75)

    output_sections = [planos, ancoragem, gating, veredito]

    artifact = json.dumps(
        {
            "kind": _kind,
            "product": product,
            "segment": segment,
            "gross_margin": gross_margin,
            "wtp_band": wtp_band,
            "tiers": {
                "basico":  {"preco": preco_basico,  "cogs": round(cogs_basico, 2),  "margem": round(margem_basico, 4)},
                "anchor":  {"preco": preco_anchor,  "cogs": round(cogs_anchor, 2),  "margem": round(margem_anchor, 4)},
                "premium": {"preco": preco_premium, "cogs": round(cogs_premium, 2), "margem": round(margem_premium, 4)},
            },
        },
        ensure_ascii=True,
        sort_keys=True,
    )

    return structured_output(
        KIND,
        output_sections,
        passed=passed,
        score=score,
        artifact=artifact,
        real=True,
        notes=notes,
    )


# --------------------------------------------------------------------------- #
# Media helpers (public -- called by tests and the edge runtime via resolve_media).
# --------------------------------------------------------------------------- #

def pricing_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Declare the optional pricing-chart image slot.

    The chart visualises the tier price comparison table.  This is a pure-math
    generator: no image is auto-produced; the slot starts as an upload-fallback
    until the media pipeline (or the user) fills it.  NEVER-FABRICATE."""
    return [
        {
            "key": "pricing_chart",
            "kind": "image",
            "section": "Planos (dados simulados)",
            "label": "Grafico comparativo de planos (upload)",
        }
    ]


def pricing_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Return produced media for the pricing generator.

    Pure-math generator -- no image is auto-produced.  Returns an empty dict so
    every declared slot (pricing_chart) becomes an upload-fallback dropzone.
    NEVER-FABRICATE: do not invent a src."""
    return {}


__all__ = [
    "KIND",
    "CONTRACT_VERSION",
    "build",
    "pricing_media_requests",
    "pricing_produced_media",
]
