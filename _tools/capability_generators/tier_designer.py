#!/usr/bin/env python3
# -*- coding: ascii -*-
"""subscription_tier capability generator -- N06 unit-economics lane (CAPGEN Wave 1).

PURE MATH: no LLM, no network. Designs good/better/best subscription tier matrix from
7 contract inputs. Uses features, personas and value_metric to populate the matrix.
DEGRADE-NEVER: guards division-by-zero and non-finite results.
"""
from __future__ import annotations

import json
import math
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

KIND = "subscription_tier"
CAPABILITY = "tier_designer"  # council A4: the generator registers by SLUG, not KIND
CONTRACT_VERSION = "1.0.0"
# Universal-envelope honest run_mode (mission CAPABILITY_COMPLETENESS W1): REAL deterministic
# math (no LLM), so it declares offline-deterministic. _base.structured_output reads it.
RUN_MODE = "offline-deterministic"

MOEDA = "R$"

# Fixed tier names and baseline prices (not in contract; hardcoded per output shape)
_TIER_NAMES = ["Starter", "Pro", "Enterprise"]
_PRICES     = [29.0, 79.0, 199.0]

# Default feature rows when features input is absent or short
_DEFAULT_FEATURES = [
    "Volume incluido",
    "Suporte",
    "API access",
    "Relatorios",
    "SLA",
    "Usuarios",
]

# Default tier values per feature row: [good_val, better_val, best_val]
_DEFAULT_VALUES = [
    ["ate 10 {vm}",   "ate 100 {vm}", "ilimitado"],
    ["email (48h)",        "prioritario (24h)", "dedicado (4h)"],
    ["nao",                "sim",               "sim"],
    ["basico",             "avancado",          "personalizado"],
    ["99%",                "99.5%",             "99.9%"],
    ["1",                  "5",                 "ilimitado"],
]


def _fmt(val: float) -> str:
    if not math.isfinite(val):
        return "N/A"
    return "%s %.0f" % (MOEDA, val)


def _uplift(low: float, high: float) -> str:
    if low <= 0 or not math.isfinite(low) or not math.isfinite(high):
        return "N/A"
    return "+%.0f%%" % ((high - low) / low * 100.0)


def _anchor_pos(anchor_tier: str) -> int:
    """Map anchor_tier string to 0/1/2 index. Default = 1 (middle/better)."""
    at = anchor_tier.lower() if anchor_tier else ""
    if at in ("starter", "good", "0", _TIER_NAMES[0].lower()):
        return 0
    if at in ("enterprise", "best", "2", _TIER_NAMES[2].lower()):
        return 2
    return 1  # "Pro", "better", or any unrecognized value -> middle


@register(CAPABILITY)  # council A4: SLUG is the sole generator key (was KIND=subscription_tier)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> "Any":
    """``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND."""
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # F1 CONSTRAIN: read EXACTLY the contract input keys (capability_contracts_v1.0.md section 10).
    def _f(key, default):
        v = inputs.get(key)
        return float(v) if v is not None else float(default)

    product              = str(inputs.get("product") or "Produto")
    num_tiers            = max(2, min(4, int(_f("num_tiers", 3))))
    features_raw         = inputs.get("features") or []
    anchor_tier          = str(inputs.get("anchor_tier") or "Pro")
    personas_raw         = inputs.get("personas") or []
    value_metric         = str(inputs.get("value_metric") or "unidades")
    anchor_margin_target = _f("anchor_margin_target", 0.70)

    features = list(features_raw) if hasattr(features_raw, "__iter__") and not isinstance(features_raw, str) else []
    personas = list(personas_raw) if hasattr(personas_raw, "__iter__") and not isinstance(personas_raw, str) else []

    # Drive the matrix rows from the features input (CAPABILITY_COMPLETENESS W1 bug-fix #5):
    # the `features` input was accepted but the matrix was hardcoded to 6 rows -- supplying 8
    # features dropped 2, supplying 3 padded with defaults. Now the matrix has ONE row per
    # supplied feature (no cap), and falls back to the 6 default rows ONLY when none are given.
    # So the declared input genuinely MOVES the output (matrix size tracks the feature count).
    feat_rows = list(features) if features else list(_DEFAULT_FEATURES)

    apos = _anchor_pos(anchor_tier)

    good_name   = _TIER_NAMES[0]
    better_name = _TIER_NAMES[1]
    best_name   = _TIER_NAMES[2]
    anchor_name = _TIER_NAMES[apos]

    preco_good   = _PRICES[0]
    preco_better = _PRICES[1]
    preco_best   = _PRICES[2]

    # Price ratios (anti-cannibalization)
    ratio_bg = preco_better / preco_good   if preco_good   > 0 else 0.0
    ratio_sb = preco_best   / preco_better if preco_better > 0 else 0.0
    canni_ok = ratio_bg >= 1.5 and ratio_sb >= 1.5

    # Column headers: anchor tier gets (*) marker
    col_labels = [
        (_TIER_NAMES[i] + " (*)") if i == apos else _TIER_NAMES[i]
        for i in range(3)
    ]

    # Build feature value rows (6 rows, each 3 columns)
    def _feat_vals(idx: int) -> list:
        """Return [good_val, better_val, best_val] for feature row idx."""
        template = _DEFAULT_VALUES[idx] if idx < len(_DEFAULT_VALUES) else ["nao", "sim", "sim"]
        return [v.replace("{vm}", value_metric) for v in template]

    feature_matrix_rows = [
        [feat_rows[i]] + _feat_vals(i)
        for i in range(len(feat_rows))
    ]

    # BRAND_MUSTACHE: frame the tier matrix for THIS tenant from the brand context the run path
    # injected. The section TITLE + columns + the 8 rows stay STABLE (golden tests assert the
    # matrix shape); the brand rides an ADDITIVE section ``note`` + the tenant name on the
    # EXISTING "Trial" migration-note row value. Un-branded -> no note, neutral value
    # (byte-identical; degrade-never). NEVER hardcodes the brand.
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    # Section 1: Matriz de planos (8 rows: price + uplift + 6 features)
    matriz = table_section(
        "Matriz de planos",
        ["Recurso"] + col_labels,
        [
            ["Preco/mes", _fmt(preco_good), _fmt(preco_better), _fmt(preco_best)],
            ["Uplift vs anterior", "--",
             _uplift(preco_good, preco_better),
             _uplift(preco_better, preco_best)],
        ] + feature_matrix_rows,
        key_col_index=0,
        note=_bnote,  # brand-frame note when tenant-branded; None -> no note (degrade-never)
        contract_version=CONTRACT_VERSION,
    )

    # Section 2: Regras de gating (5 items)
    # Use persona labels if provided (pad with empty string)
    p = (personas + ["", "", ""])[:3]
    persona_note = lambda i: (" [%s]" % p[i]) if p[i] else ""
    gating = list_section(
        "Regras de gating",
        [
            "%s (good)%s: volume ate 10 %s; sem API; suporte email 48h" % (good_name, persona_note(0), value_metric),
            "%s (better)%s: volume ate 100 %s; API habilitada; upsell ao atingir 80%%%% do limite" % (better_name, persona_note(1), value_metric),
            "%s (best)%s: volume ilimitado; SLA 99.9%%%%; CSM dedicado; relatorios personalizados" % (best_name, persona_note(2)),
            "Upgrade sugerido automaticamente ao atingir 80%% do volume do tier atual",
            "Downgrade bloqueado no 1o mes (cooling-off 30 dias) para prevenir churn por preco",
        ],
        contract_version=CONTRACT_VERSION,
    )

    # Section 3: Notas de migracao (4 rows)
    notas_mig = fields_section(
        "Notas de migracao",
        [
            {"label": "%s -> %s" % (good_name, better_name),
             "value": "Pro-rated: cobrar diferenca de preco no mes da upgrade; sem interrupcao de servico"},
            {"label": "%s -> %s" % (better_name, best_name),
             "value": "Contrato anual recomendado; desconto de 20%% para lock-in de LTV; "
                      "margem-alvo do ancora: %.0f%%" % (anchor_margin_target * 100)},
            {"label": "Downgrade",
             "value": "Permitido apos cooling-off de 30 dias; dados preservados por 90 dias pos-downgrade"},
            {"label": "Trial",
             "value": "%s14 dias no tier %s para novos cadastros; converte para %s se cartao nao ativado" % (
                 ("%s -- " % brand_name) if brand_name else "", better_name, good_name)},
        ],
        contract_version=CONTRACT_VERSION,
    )

    # Section 4: Caminho de expansao (4 rows)
    expansao = table_section(
        "Caminho de expansao",
        ["Trigger", "Resposta esperada", "Lift estimado (mock)"],
        [
            [
                "Volume > 80%% do limite do tier atual",
                "Email de upsell + CTA in-app para tier acima",
                "+15%% MRR (estimado)",
            ],
            [
                "2+ usuarios adicionados no %s" % good_name,
                "Oferta de bundle para 5 usuarios no %s" % better_name,
                "+22%% conversao (estimado)",
            ],
            [
                "%s ativo por 6+ meses" % better_name,
                "Proposta de contrato anual com 20%% desconto",
                "+18%% LTV (estimado)",
            ],
            [
                "NPS >= 9 no %s" % better_name,
                "Convite para programa beta do %s" % best_name,
                "+30%% probabilidade de upgrade (estimado)",
            ],
        ],
        key_col_index=0,
        contract_version=CONTRACT_VERSION,
    )

    # F7 GOVERN
    passed = True
    score = 0.9
    if not (0.0 < anchor_margin_target < 1.0):
        notes.append("F7 [FAIL]: anchor_margin_target %.2f fora do intervalo (0, 1)" % anchor_margin_target)
        passed = False
        score = min(score, 0.5)
    elif anchor_margin_target > 0.95:
        notes.append("F7 [WARN]: anchor_margin_target > 95%%; revisar sustentabilidade do negocio")
        score = min(score, 0.80)
    if not canni_ok:
        notes.append("F7 [WARN]: ratio entre tiers < 1.5x -- risco de canibalizacao de receita")
        score = min(score, 0.75)

    output_sections = [matriz, gating, notas_mig, expansao]

    artifact = json.dumps(
        {
            "kind": _kind,
            "product": product,
            "anchor_tier": anchor_name,
            "anchor_margin_target": anchor_margin_target,
            "feature_count": len(feat_rows),
            "tiers": [
                {"label": "good",   "name": good_name,   "preco": preco_good},
                {"label": "better", "name": better_name, "preco": preco_better},
                {"label": "best",   "name": best_name,   "preco": preco_best},
            ],
            "ratios": {
                "better_vs_good": round(ratio_bg, 2),
                "best_vs_better": round(ratio_sb, 2),
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

def tier_designer_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Declare the optional tier-comparison visual image slot.

    The visual shows the good/better/best tier matrix at a glance.
    Pure-math generator: no image is auto-produced; slot starts as an
    upload-fallback until the media pipeline or the user fills it.
    NEVER-FABRICATE."""
    return [
        {
            "key": "tier_visual",
            "kind": "image",
            "section": "Matriz de planos",
            "label": "Visual comparativo de tiers (upload)",
        }
    ]


def tier_designer_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Return produced media for the subscription_tier generator.

    Pure-math generator -- no image is auto-produced.  Returns an empty dict so
    every declared slot (tier_visual) becomes an upload-fallback dropzone.
    NEVER-FABRICATE: do not invent a src."""
    return {}


__all__ = [
    "KIND",
    "CONTRACT_VERSION",
    "build",
    "tier_designer_media_requests",
    "tier_designer_produced_media",
]
