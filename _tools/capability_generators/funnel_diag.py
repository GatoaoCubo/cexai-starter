#!/usr/bin/env python3
# -*- coding: ascii -*-
"""funnel_diag -- the N05 (Operations / Gating Wrath) structured generator.

KIND = "tool_card" (capability "funnel_diag"). A GATE-grade funnel diagnostic: it does
not merely DISPLAY per-stage numbers, it JUDGES them -- it emits an explicit VEREDITO
(LEAK / OK) against a TUNABLE bar (drop > health_threshold_pct) and reconstructs that
verdict from the per-stage evidence so a reviewer can re-derive the pass/fail by hand.
That is the Gating-Wrath discipline: the bar is the bar.

PURE deterministic gate-math: every value is COMPUTED from the inputs (per-stage
conversao + drop, the LEAK/WARN/OK sinal vs the threshold, the biggest leak, the ranked
corrections). No LLM, no network, no clock. The ``credential`` arg is ignored.

CONTRACT BINDINGS (capability_contracts_v1.0.md / molds.ts MOLD_FUNNEL_DIAG -- FROZEN):
  INPUT (input_contract -- 6 fields):
    product               : string,   required        (the funnel label)
    stages                : string[], required         (ordered stage names)
    stage_volumes         : number[], required         (1:1 with stages, same order)
    window_days           : number,   optional (=30)   (metrics window)
    health_threshold_pct  : number,   optional (=60)   (drop %% above which a stage LEAKs -- the BAR)
    baseline_window_days  : number,   optional (=30)   (comparison window; reproducibility handle)
  OUTPUT (output_sections -- this FROZEN order + layout):
    1. "Veredito"             fields  Status(LEAK/OK) + Bar(the threshold) + Confianca(sample)
    2. "Metricas por etapa"   table   [Etapa, Volume, Conversao, Drop, Sinal]
    3. "Maior vazamento"      fields  Etapa critica + Perda absoluta + Projecao (estimada, nao medida)
    4. "Correcoes priorizadas" table  [#, Correcao, Impacto, Esforco]

GATE DOCTRINE (the F7 honesty this generator self-checks):
  * VERDICT is binary by the BAR, not by absolute loss: a stage with a huge absolute
    loss but a drop <= threshold is OK (and we say so honestly in notes); a stage with
    drop > threshold is a LEAK. Anyone can re-derive Status from the metrics table.
  * Projections are labelled "estimada, nao medida" -- a what-if, never a measurement.
  * ``passed`` is the GENERATOR's gate verdict (did it produce a valid diagnostic),
    NOT whether the funnel is healthy: a clean LEAK report still passes.

For the canonical contract input (Visitas/Ver produto/Adicionar ao carro/Iniciar
checkout/Compra at 42000/18480/5544/2218/1109, bar 60) the output is BYTE-EQUAL in
SHAPE to molds.ts -- real computed data, identical shape (Status=LEAK, the carro step at
70%% drop is the LEAK, the projection +924 carrinhos -> ~+185 compras).
"""

from __future__ import annotations

import json
import math
import re
from typing import Any, Dict, List, Mapping, Optional, Tuple

from ._base import (
    StructuredOutput,
    brand_frame_note,
    brand_name_of,
    effective_kind,
    fields_section,
    list_section,  # noqa: F401  (imported for parity with the package surface)
    register,
    structured_output,
    table_section,
)

KIND = "tool_card"
CAPABILITY = "funnel_diag"  # council A4: the generator registers by SLUG, not KIND (tool_card)
CONTRACT_VERSION = "1.0.0"

# -- Defaults from the input_contract (optional fields). --------------------------
_DEFAULT_WINDOW_DAYS = 30
_DEFAULT_THRESHOLD_PCT = 60.0
_DEFAULT_BASELINE_DAYS = 30
_DEFAULT_PRODUCT = "Funil"

# The canonical contract example (used ONLY when BOTH stages and volumes are absent,
# so the dashboard demo still renders a real computed run instead of crashing).
_EXAMPLE_STAGES: List[str] = [
    "Visitas", "Ver produto", "Adicionar ao carro", "Iniciar checkout", "Compra",
]
_EXAMPLE_VOLUMES: List[float] = [42000.0, 18480.0, 5544.0, 2218.0, 1109.0]

# A what-if scenario constant for the projection (close N percentage points of the
# worst drop). It is an ASSUMPTION, surfaced as "estimada, nao medida"; never measured.
_PROJECTION_PP = 5

# Impact grade thresholds (share of total funnel loss) -- auditable, tunable here.
_IMPACT_ALTO = 0.30
_IMPACT_MEDIO = 0.12

# pt-BR thousands pattern (e.g. "42.000" / "1.109") for best-effort string coercion.
_PTBR_THOUSANDS = re.compile(r"^\d{1,3}(\.\d{3})+$")


# --------------------------------------------------------------------------- #
# Coercion / parsing helpers (degrade-never; never raise on a malformed value).
# --------------------------------------------------------------------------- #
def _to_number(x: Any) -> Optional[float]:
    """Best-effort coerce a single value to a finite float, else None.

    Accepts int/float directly; for strings, strips spaces, treats a pt-BR
    ``1.234.567`` group as thousands (dots removed) and a ``,`` as the decimal sep.
    Booleans and non-finite values are rejected (None). Never raises."""
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        v = float(x)
        return v if math.isfinite(v) else None
    if isinstance(x, str):
        s = x.strip().replace(" ", "")
        if not s:
            return None
        if _PTBR_THOUSANDS.match(s):
            s = s.replace(".", "")
        else:
            s = s.replace(",", ".")
        try:
            v = float(s)
        except (TypeError, ValueError):
            return None
        return v if math.isfinite(v) else None
    return None


def _coerce_str_list(raw: Any) -> List[str]:
    """Normalise to an ordered list of non-empty strings (list/tuple or split string)."""
    if isinstance(raw, (list, tuple)):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        parts = raw.replace("\n", ",").split(",")
        return [p.strip() for p in parts if p.strip()]
    return []


def _coerce_num_list(raw: Any) -> Tuple[List[Optional[float]], bool]:
    """Normalise to a list of numbers (None for an unparseable cell).

    Returns (numbers, any_unparseable). Accepts a list/tuple or a comma/newline/space
    separated string. The any_unparseable flag drives an honest validity verdict."""
    items: List[Any]
    if isinstance(raw, (list, tuple)):
        items = list(raw)
    elif isinstance(raw, str) and raw.strip():
        items = [p for p in re.split(r"[,\n\s]+", raw.strip()) if p]
    else:
        return [], False
    nums = [_to_number(it) for it in items]
    any_bad = any(n is None for n in nums)
    return nums, any_bad


def _resolve_number(raw: Any, default: float) -> Tuple[float, bool]:
    """Resolve an optional numeric input to (value, was_defaulted). Non-positive -> default."""
    v = _to_number(raw)
    if v is None or v <= 0:
        return float(default), True
    return v, False


def _fmt_int(n: float) -> str:
    """Format a number as a pt-BR integer with '.' thousands separators (42000 -> '42.000')."""
    try:
        i = int(round(float(n)))
    except (TypeError, ValueError):
        return str(n)
    sign = "-" if i < 0 else ""
    digits = str(abs(i))
    groups = []
    while len(digits) > 3:
        groups.insert(0, digits[-3:])
        digits = digits[:-3]
    groups.insert(0, digits)
    return sign + ".".join(groups)


def _fmt_pct(p: Optional[float]) -> str:
    """Format an integer percent ('44%') or '--' for an undefined (guarded) cell."""
    if p is None:
        return "--"
    return "%d%%" % int(round(p))


def _fmt_threshold(thr: float) -> str:
    """Threshold display: drop the trailing '.0' for an integer-valued bar (60.0 -> '60')."""
    if abs(thr - round(thr)) < 1e-9:
        return str(int(round(thr)))
    return ("%.2f" % thr).rstrip("0").rstrip(".")


# --------------------------------------------------------------------------- #
# Error path -- still emits the 4 frozen sections (shape stays frozen on failure).
# --------------------------------------------------------------------------- #
def _error_output(reason: str, notes: List[str], kind: str = KIND) -> "StructuredOutput":
    """Return a well-formed StructuredOutput with Status=ERRO (never crash, shape frozen)."""
    notes = list(notes) + ["entrada invalida: " + reason]
    sec_verdict = fields_section(
        "Veredito",
        [("Status", "ERRO"), ("Bar", "n/a -- entrada invalida"), ("Confianca", reason)],
        note="Nao foi possivel computar o diagnostico a partir da entrada.",
    )
    sec_metrics = table_section(
        "Metricas por etapa",
        ["Etapa", "Volume", "Conversao", "Drop", "Sinal"],
        [],
        column_types=["string", "number", "string", "string", "string"],
        key_col_index=0,
        note="Sem metricas: a entrada nao passou na validacao.",
    )
    sec_leak = fields_section(
        "Maior vazamento",
        [("Etapa critica", "n/a"), ("Perda absoluta", "n/a"),
         ("Projecao (estimada, nao medida)", "n/a")],
    )
    sec_fixes = table_section(
        "Correcoes priorizadas",
        ["#", "Correcao", "Impacto", "Esforco"],
        [[1, "Corrigir a entrada: " + reason, "--", "--"]],
        column_types=["number", "string", "string", "string"],
        key_col_index=0,
        note="Ranqueadas por impacto / esforco.",
    )
    return structured_output(
        KIND,
        [sec_verdict, sec_metrics, sec_leak, sec_fixes],
        passed=False,
        score=0.0,
        artifact=json.dumps({"kind": kind, "error": reason}, ensure_ascii=True, sort_keys=True),
        real=True,
        notes=notes,
    )


# --------------------------------------------------------------------------- #
# Core gate-math.
# --------------------------------------------------------------------------- #
def _per_stage(
    stages: List[str], volumes: List[float], threshold: float
) -> List[Dict[str, Any]]:
    """Compute per-stage conversao / drop / sinal / absolute loss (index 0 is the entry).

    conversao[i] = v[i]/v[i-1]; drop[i] = 100 - conversao_pct[i]; sinal vs the bar.
    Division-by-zero (v[i-1] == 0) is guarded -> conv/drop None ('--'), sinal 'n/a'."""
    rows: List[Dict[str, Any]] = []
    for i, (name, vol) in enumerate(zip(stages, volumes)):
        if i == 0:
            rows.append({
                "stage": name, "volume": vol, "conv_pct": None, "drop_pct": None,
                "sinal": "--", "abs_loss": 0.0,
            })
            continue
        prev = volumes[i - 1]
        if prev <= 0:
            rows.append({
                "stage": name, "volume": vol, "conv_pct": None, "drop_pct": None,
                "sinal": "n/a", "abs_loss": max(0.0, prev - vol),
            })
            continue
        conv_pct = round((vol / prev) * 100.0)
        drop_pct = 100 - conv_pct
        if drop_pct > threshold:
            sinal = "LEAK"
        elif drop_pct == threshold:
            sinal = "WARN"
        else:
            sinal = "OK"
        rows.append({
            "stage": name, "volume": vol, "conv_pct": float(conv_pct),
            "drop_pct": float(drop_pct), "sinal": sinal, "abs_loss": prev - vol,
        })
    return rows


def _critical_index(rows: List[Dict[str, Any]]) -> Optional[int]:
    """Index of the worst LEAK = max drop_pct (tie-break: bigger abs_loss, then earlier)."""
    best: Optional[int] = None
    for i, r in enumerate(rows):
        if i == 0 or r["drop_pct"] is None:
            continue
        if best is None:
            best = i
            continue
        cur, prv = rows[i], rows[best]
        if (cur["drop_pct"], cur["abs_loss"]) > (prv["drop_pct"], prv["abs_loss"]):
            best = i
    return best


def _artifact(product: str, window: float, threshold: float, status: str,
              rows: List[Dict[str, Any]], kind: str = KIND) -> str:
    """A compact ASCII-safe JSON projection of the computed diagnostic (persist/results)."""
    projection = {
        "kind": kind,
        "contract_version": CONTRACT_VERSION,
        "product": product,
        "window_days": int(round(window)),
        "health_threshold_pct": threshold,
        "verdict": status,
        "stages": [
            {
                "etapa": r["stage"],
                "volume": int(round(r["volume"])),
                "conversao_pct": (None if r["conv_pct"] is None else int(r["conv_pct"])),
                "drop_pct": (None if r["drop_pct"] is None else int(r["drop_pct"])),
                "sinal": r["sinal"],
            }
            for r in rows
        ],
    }
    try:
        return json.dumps(projection, ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


@register(CAPABILITY)  # council A4: SLUG is the sole generator key (was KIND=tool_card)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> "StructuredOutput":
    """Produce the REAL funnel_diag structured output (deterministic; ignores credential).

    Computes the per-stage metrics, the LEAK/OK verdict against the tunable bar, the
    biggest leak (+ an explicitly-estimated projection) and the impact-ranked corrections.
    Validates the input (length parity, >=2 stages, finite non-negative volumes); on an
    invalid entry returns a clean Status=ERRO output. Never raises (degrade-never).

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND."""
    notes: List[str] = []
    _kind = effective_kind(resolved_kind, KIND)

    # -- F1 CONSTRAIN: parse + validate inputs. ------------------------------------
    product = str(inputs.get("product") or "").strip() or _DEFAULT_PRODUCT
    product = product.replace("\n", " ").replace("\r", " ")
    stages = _coerce_str_list(inputs.get("stages"))
    volumes_raw, vol_bad = _coerce_num_list(inputs.get("stage_volumes"))

    if not stages and not volumes_raw:
        stages = list(_EXAMPLE_STAGES)
        volumes_raw = list(_EXAMPLE_VOLUMES)
        notes.append("stages/stage_volumes ausentes: usando o exemplo do contrato")

    if vol_bad:
        return _error_output("stage_volumes contem valor nao numerico", notes, kind=_kind)
    if len(stages) != len(volumes_raw):
        return _error_output(
            "len(stages)=%d != len(stage_volumes)=%d" % (len(stages), len(volumes_raw)),
            notes, kind=_kind,
        )
    if len(stages) < 2:
        return _error_output("um funil precisa de >= 2 etapas", notes, kind=_kind)
    volumes = [float(v) for v in volumes_raw]  # vol_bad already excluded None
    if any(v < 0 for v in volumes):
        return _error_output("stage_volumes nao pode ser negativo", notes, kind=_kind)

    window, win_def = _resolve_number(inputs.get("window_days"), _DEFAULT_WINDOW_DAYS)
    threshold, thr_def = _resolve_number(inputs.get("health_threshold_pct"), _DEFAULT_THRESHOLD_PCT)
    baseline, _bl_def = _resolve_number(inputs.get("baseline_window_days"), _DEFAULT_BASELINE_DAYS)
    if win_def and inputs.get("window_days") is not None:
        notes.append("window_days invalido; usando o default %d" % _DEFAULT_WINDOW_DAYS)
    if thr_def and inputs.get("health_threshold_pct") is not None:
        notes.append("health_threshold_pct invalido; usando o default %d" % int(_DEFAULT_THRESHOLD_PCT))

    # Monotonic-funnel sanity (a funnel should not grow stage-over-stage).
    grew = [i for i in range(1, len(volumes)) if volumes[i] > volumes[i - 1]]
    if grew:
        notes.append(
            "anomalia: %d etapa(s) com volume maior que a anterior (funil nao monotonico)"
            % len(grew)
        )

    # -- F6 PRODUCE: per-stage gate-math. -----------------------------------------
    rows = _per_stage(stages, volumes, threshold)
    leak_idx = [i for i, r in enumerate(rows) if r["sinal"] == "LEAK"]
    warn_idx = [i for i, r in enumerate(rows) if r["sinal"] == "WARN"]
    status = "LEAK" if leak_idx else "OK"
    top_volume = volumes[0]
    thr_disp = _fmt_threshold(threshold)

    # BRAND_MUSTACHE: frame the gate for THIS tenant from the brand context the run path
    # injected. Section TITLE + the 3 rows stay STABLE (tests assert the verdict shape); the
    # brand framing rides an ADDITIVE clause on the EXISTING "Confianca" row VALUE + a brand
    # note appended to the EXISTING section note. Un-branded -> no clause, no note delta
    # (byte-identical; degrade-never). NEVER hardcodes the brand; "" -> neutral.
    brand_name = brand_name_of(inputs)
    _bnote = brand_frame_note(inputs)
    if _bnote:
        notes.append(_bnote)

    # Section 1 -- Veredito (the gate; renders first).
    confianca = "amostra %s sessoes / %dd; %d etapas" % (
        _fmt_int(top_volume), int(round(window)), len(stages))
    if brand_name:
        confianca = "%s -- %s" % (brand_name, confianca)
    _verdict_note = ("Status do funil contra a barra (drop > limite vira LEAK). "
                     "Reconstruido pela tabela abaixo.")
    if _bnote:
        _verdict_note = "%s %s" % (_verdict_note, _bnote)
    sec_verdict = fields_section(
        "Veredito",
        [
            ("Status", status),
            ("Bar", "drop > %s%% na etapa" % thr_disp),
            ("Confianca", confianca),
        ],
        note=_verdict_note,
    )

    # Section 2 -- Metricas por etapa (the evidence; reconstructs the verdict).
    metric_rows: List[List[Any]] = [
        [r["stage"], _fmt_int(r["volume"]), _fmt_pct(r["conv_pct"]),
         _fmt_pct(r["drop_pct"]), r["sinal"]]
        for r in rows
    ]
    sec_metrics = table_section(
        "Metricas por etapa",
        ["Etapa", "Volume", "Conversao", "Drop", "Sinal"],
        metric_rows,
        column_types=["string", "number", "string", "string", "string"],
        key_col_index=0,
        note="Volume, conversao, drop e sinal por etapa (janela de %dd). "
             "Sinal = LEAK se drop>%s, WARN se ==%s, OK caso contrario."
             % (int(round(window)), thr_disp, thr_disp),
    )

    # Section 3 -- Maior vazamento (worst drop %, its absolute loss, an estimated what-if).
    crit = _critical_index(rows)
    if crit is None:
        sec_leak = fields_section(
            "Maior vazamento",
            [
                ("Etapa critica", "nenhuma etapa com drop computavel"),
                ("Perda absoluta", "n/a"),
                ("Projecao (estimada, nao medida)", "n/a"),
            ],
        )
    else:
        cr = rows[crit]
        prev_stage = stages[crit - 1]
        cur_stage = stages[crit]
        final_stage = stages[-1]
        abs_loss = cr["abs_loss"]
        entry_vol = volumes[crit - 1]
        extra_at_stage = round((_PROJECTION_PP / 100.0) * entry_vol)
        crit_vol = volumes[crit]
        downstream_conv = (volumes[-1] / crit_vol) if crit_vol > 0 else 0.0
        extra_final = round(extra_at_stage * downstream_conv)
        proj = (
            "Fechar %d p.p. do drop em '%s' ~= +%s avancos para '%s' (~+%s em '%s'), "
            "janela %dd"
            % (_PROJECTION_PP, cur_stage, _fmt_int(extra_at_stage), cur_stage,
               _fmt_int(extra_final), final_stage, int(round(window)))
        )
        sec_leak = fields_section(
            "Maior vazamento",
            [
                ("Etapa critica", "%s -> %s (%s de drop)"
                 % (prev_stage, cur_stage, _fmt_pct(cr["drop_pct"]))),
                ("Perda absoluta", "~%s sessoes entram em '%s' e nao avancam para '%s'"
                 % (_fmt_int(abs_loss), prev_stage, cur_stage)),
                ("Projecao (estimada, nao medida)", proj),
            ],
            note="A etapa critica e a de maior drop %% (nao a de maior perda absoluta). "
                 "A projecao e um cenario, nao uma medicao.",
        )

    # Section 4 -- Correcoes priorizadas (the non-OK stages, ranked by absolute loss).
    total_loss = max(0.0, volumes[0] - volumes[-1])
    actionable = [i for i in range(1, len(rows)) if rows[i]["sinal"] in ("LEAK", "WARN")]
    actionable.sort(key=lambda i: rows[i]["abs_loss"], reverse=True)
    fix_rows: List[List[Any]] = []
    for rank, i in enumerate(actionable, start=1):
        r = rows[i]
        share = (r["abs_loss"] / total_loss) if total_loss > 0 else 0.0
        if share >= _IMPACT_ALTO:
            impacto = "Alto"
        elif share >= _IMPACT_MEDIO:
            impacto = "Medio"
        else:
            impacto = "Baixo"
        if i == len(rows) - 1:
            esforco = "Baixo"     # last transition (checkout/payment) -- usually UX tweaks
        elif i == 1:
            esforco = "Alto"      # first transition (acquisition/landing) -- traffic/creative
        else:
            esforco = "Medio"
        correcao = "Reduzir o drop de %s de '%s' -> '%s' (%s)" % (
            _fmt_pct(r["drop_pct"]), stages[i - 1], stages[i], r["sinal"])
        fix_rows.append([rank, correcao, impacto, esforco])
    if not fix_rows:
        fix_rows = [[1, "Nenhum vazamento acima da barra (drop > %s%%)" % thr_disp, "--", "--"]]
    sec_fixes = table_section(
        "Correcoes priorizadas",
        ["#", "Correcao", "Impacto", "Esforco"],
        fix_rows,
        column_types=["number", "string", "string", "string"],
        key_col_index=0,
        note="Ranqueadas pela perda absoluta computada (impacto). Esforco e uma "
             "heuristica por posicao no funil (estimativa, nao medida).",
    )

    output_sections = [sec_verdict, sec_metrics, sec_leak, sec_fixes]

    # -- F7 GOVERN: the generator's OWN gate verdict (not the funnel's health). -----
    score = 1.0
    if "usando o exemplo do contrato" in " ".join(notes):
        score -= 0.1
    if grew:
        score -= 0.1
    guarded = any(r["sinal"] == "n/a" for r in rows[1:])
    if guarded:
        score -= 0.1
        notes.append("uma ou mais etapas com volume anterior zero (conversao guardada)")
    # Honest gate nuance: flag when the biggest ABSOLUTE loss sits at an OK stage.
    non_entry = rows[1:]
    if non_entry:
        max_loss_row = max(non_entry, key=lambda r: r["abs_loss"])
        if max_loss_row["sinal"] == "OK" and max_loss_row["abs_loss"] > 0:
            notes.append(
                "maior perda absoluta em '%s' (~%s sessoes) esta ABAIXO da barra "
                "(drop %s <= %s%%): nao classificada como LEAK (a barra e a barra)"
                % (max_loss_row["stage"], _fmt_int(max_loss_row["abs_loss"]),
                   _fmt_pct(max_loss_row["drop_pct"]), thr_disp))
    notes.append("verdito=%s; leaks=%d; warns=%d; etapas=%d; bar=drop>%s%%; baseline=%dd"
                 % (status, len(leak_idx), len(warn_idx), len(stages), thr_disp,
                    int(round(baseline))))
    notes.append("passed = o gerador produziu um diagnostico valido (NAO = funil saudavel)")
    sections_ok = all(bool(s.get("rows") or s.get("table")) for s in output_sections)
    passed = bool(sections_ok and score >= 0.8)

    return structured_output(
        KIND,
        output_sections,
        passed=passed,
        score=score,
        artifact=_artifact(product, window, threshold, status, rows, kind=_kind),
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
# build()/_per_stage() read above -- never a re-typed literal -- so an exported bundle can
# never drift from what build() actually enforces at runtime.
#
# SHAPE NOTE: unlike ads.py (enum/vocabulary-heavy: platforms, tones, funnel stages),
# funnel_diag's real domain law is GATE-MATH-heavy: a tunable health-threshold bar, the
# input defaults, the canonical contract example, a projection assumption, and the
# impact-grading thresholds. The LEAK/WARN/OK verdict labels and the "Alto"/"Medio"/
# "Baixo" impact/effort labels are inline branch literals in _per_stage()/build() --
# NOT stored in a named module constant -- so they are deliberately NOT re-typed here
# (that would be inventing a lookup that does not exist in the source); only the
# numeric thresholds/defaults that actually gate those branches are exposed.
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law funnel_diag.py enforces on every generated diagnostic (Missao A).
    Returns a structured, JSON-serialisable dict -- never {} for THIS generator (funnel_diag
    DOES declare domain law: the health-threshold bar + other input defaults, the canonical
    contract example funnel, the projection assumption, and the impact-grading thresholds)."""
    return {
        "contract_version": CONTRACT_VERSION,
        "input_defaults": {
            "window_days": _DEFAULT_WINDOW_DAYS,
            "health_threshold_pct": _DEFAULT_THRESHOLD_PCT,
            "baseline_window_days": _DEFAULT_BASELINE_DAYS,
            "product_label": _DEFAULT_PRODUCT,
        },
        "canonical_example_funnel": [
            {"stage": s, "stage_volume": v}
            for s, v in zip(_EXAMPLE_STAGES, _EXAMPLE_VOLUMES)
        ],
        "projection_closure_pp": _PROJECTION_PP,
        "impact_grade_thresholds": {
            "alto_min_share_of_total_loss": _IMPACT_ALTO,
            "medio_min_share_of_total_loss": _IMPACT_MEDIO,
        },
    }


# --------------------------------------------------------------------------- #
# Media helpers (public -- called by tests and the edge runtime; mission DUALROLL W4).
#
# A funnel diagnostic's HUMAN face naturally carries ONE funnel DIAGRAM image: the staged
# volumes + drops drawn as a chart, bound to the "Metricas por etapa" section it visualizes.
# The generator computes the funnel from NUMBERS only -- it does NOT render a chart -- so the
# slot is an empty UPLOAD-FALLBACK by default. If a charting pipeline (or the caller) injects
# a pre-rendered diagram URL via inputs ('funnel_diagram_url' or 'diagram_url'), it is mapped
# as a produced image. NEVER-FABRICATE a URL; an absent/blank value -> an omitted key -> an
# editable upload-fallback slot. Discovered generically by _base.resolve_media (the run path
# is already wired; this file only exposes the two prefixed hooks). PURE + TOTAL.
# --------------------------------------------------------------------------- #
_FUNNEL_DIAGRAM_KEY = "funnel_diagram"
# Must match the build() output-section title EXACTLY so the slot renders under that section.
_FUNNEL_DIAGRAM_SECTION = "Metricas por etapa"
# Optional input keys a caller/pipeline may use to supply a pre-rendered diagram URL.
_DIAGRAM_URL_KEYS = ("funnel_diagram_url", "diagram_url")


def _diagram_src(inputs: Mapping[str, Any]) -> str:
    """Return a non-empty diagram URL from inputs, or '' when none is supplied. TOTAL.

    Scans the accepted URL-bearing input keys in order; a non-string or blank value is
    treated as ABSENT (-> upload-fallback). NEVER fabricates a URL; never raises."""
    for k in _DIAGRAM_URL_KEYS:
        v = inputs.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def funnel_diag_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Build the media_requests list for cex_dual_output.to_dual_output from funnel inputs.

    Declares ONE image slot (key='funnel_diagram', kind=image) bound to the
    'Metricas por etapa' section -- the funnel chart that visualizes the per-stage volumes
    and drops. ALWAYS declared; it starts as an upload-fallback affordance until a chart is
    produced. PURE + TOTAL: never raises (``inputs`` is accepted for signature parity with the
    discovery seam; the single slot does not depend on the funnel size)."""
    return [{
        "key": _FUNNEL_DIAGRAM_KEY,
        "kind": "image",
        "section": _FUNNEL_DIAGRAM_SECTION,
        "label": "Diagrama do funil",
    }]


def funnel_diag_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Build the produced_media dict for cex_dual_output.to_dual_output from funnel inputs.

    Maps the 'funnel_diagram' slot to a real image src ONLY when the caller supplied a
    pre-rendered diagram URL ('funnel_diagram_url' or 'diagram_url'). The deterministic
    gate-math does NOT render a chart, so by default this returns {} -> the slot stays an empty
    upload-fallback. NEVER-FABRICATE: an absent/blank URL -> an omitted key. PURE + TOTAL."""
    url = _diagram_src(inputs)
    produced: Dict[str, Any] = {}
    if url:
        produced[_FUNNEL_DIAGRAM_KEY] = {"src": url, "alt": "Diagrama do funil"}
    return produced


__all__ = [
    "KIND",
    "CONTRACT_VERSION",
    "build",
    "funnel_diag_media_requests",
    "funnel_diag_produced_media",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
