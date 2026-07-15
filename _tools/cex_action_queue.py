#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI action queue -- open-items + recommended next-actions (mission COMPLETE2, W2b).

Closes gap #4 of the capability completeness audit (_output/cexai_capability_completeness
_2026-06-22.md): "gates are static APROVADO/BLOQUEADO; there's no 'what's missing / retry X'."

After a capability runs, the result already carries everything needed to tell the user what
to DO next -- but nothing reads it. This module is the pure DERIVER: it reads a finished
CapabilityResult and turns its gate / score / run_mode / confidence_breakdown / per-lane
endpoint_status into a small, honest action queue:

    derive_action_queue(result) -> {
        "open_items":   [ ... ],   # honest "what is thin / illustrative" observations
        "next_actions": [ ... ],   # recommended things to DO to unlock / improve
        "blocking":     [ ... ],   # what blocks a usable result (the WHY + the fix)
        "idle":         bool,      # True iff all three lists are empty (nothing to do)
    }

DESIGN INVARIANTS (the constitution + the task contract):
  * NEVER-FABRICATE. Every item is DERIVED from real result state. The authoritative gate
    is the result's ``passed`` flag (this module never re-runs a gate); a numeric score is
    only quoted in the human message when it is actually present (> 0). A confidence factor
    is flagged ONLY when it is a real number below the thin threshold -- a null factor is an
    honest "not computed", never invented into a complaint. A blocked lane's credential hint
    is taken from a VERIFIED lane->env-var map (read out of the lane modules), with a generic
    honest fallback for lanes whose dependency is not known here.
  * DEGRADE-NEVER. derive_action_queue is TOTAL: any surprise in the result shape -> an empty
    (idle) queue, never a raise. The run that produced the result must never break because the
    queue could not be derived. The caller (cex_run_capability) guards too -- belt-and-braces.
  * ADDITIVE / ZERO-REGRESSION. This module reads a result; it mutates nothing. It is decoupled
    from cex_run_capability (it duck-types the result via getattr and imports nothing from it),
    so there is no import cycle and a test can pass any object with the right attributes.
  * ASCII-ONLY. Per .claude/rules/ascii-code-rule.md the human strings are unaccented PT-BR
    (the dashboard surface is PT-BR; the result sections already use unaccented PT-BR
    -- "Veredito", "Proveniencia", "Achados" -- so the queue matches them).

Reads (all optional, duck-typed): result.status, result.passed, result.score, result.errors,
result.capability, result.kind, result.structured (the W1 envelope: run_mode /
confidence_breakdown; OR the research_universe report: endpoint_status).
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

# --------------------------------------------------------------------------- #
# Thresholds + vocabulary -- explicit, honest, never re-deriving the gate.
# --------------------------------------------------------------------------- #

# The system publish/quality floor on the 0..10 display scale (CLAUDE.md "publish below 8.0").
# Used ONLY to phrase the human "why" message on a gate failure -- the AUTHORITATIVE gate
# signal is ``result.passed`` (set by the builder/generator), which this module never recomputes.
_SCORE_FLOOR = 8.0

# A confidence factor (0..1) below this is "thin". A null factor is NOT thin (honest unknown).
_CONFIDENCE_THIN = 0.5

# The conservative honest run_mode the W1 envelope stamps when no LLM/credential was used
# (mirrors capability_generators._base.DEFAULT_RUN_MODE). A result in this mode is structurally
# real but its data is illustrative -> the gap-#4 "supply a credential for real data" action.
_RUN_MODE_OFFLINE = "offline-scaffold"

# Per-lane retry hints for the research_universe route. VERIFIED against the lane modules (not
# guessed): reclame_aqui reads FIRECRAWL_API_KEY (cex_reclame_aqui.py), youtube reads
# CEX_YOUTUBE_API_KEY/YOUTUBE_API_KEY (cex_youtube_data.py), reddit OAuth reads
# CEX_REDDIT_CLIENT_ID + CEX_REDDIT_SECRET (cex_reddit_listen.py). A lane absent from this map
# gets the GENERIC honest hint below -- never a fabricated credential name.
_LANE_CREDENTIAL_HINT: Dict[str, str] = {
    "reclame_aqui": (
        "defina FIRECRAWL_API_KEY (o host do Reclame Aqui fica atras de Cloudflare; "
        "o scrape stealth da Firecrawl libera a coleta) e rode novamente"
    ),
    "youtube": (
        "defina CEX_YOUTUBE_API_KEY (ou YOUTUBE_API_KEY) -- uma chave oficial da "
        "YouTube Data API v3 -- e rode novamente"
    ),
    "reddit": (
        "defina CEX_REDDIT_CLIENT_ID + CEX_REDDIT_SECRET para a via OAuth (ou apenas rode "
        "de novo; a via publica sem chave pode estar limitada por rate-limit)"
    ),
}

# Friendly labels for the lane slugs (display only). A lane not listed falls back to its slug.
_LANE_LABEL: Dict[str, str] = {
    "cnpj": "CNPJ",
    "ibge": "IBGE",
    "appstore": "App Store",
    "reddit": "Reddit",
    "youtube": "YouTube",
    "reclame_aqui": "Reclame Aqui",
    "seo": "SEO",
    "questions": "Perguntas (PAA)",
}

# The honest fallback retry hint for a blocked lane whose credential dependency is not known here.
_GENERIC_LANE_HINT = "forneca a fonte/credencial desta lane e rode novamente"


# --------------------------------------------------------------------------- #
# Item + empty-queue helpers.
# --------------------------------------------------------------------------- #
def _item(code: str, title: str, *, detail: str = "", action: str = "") -> Dict[str, str]:
    """One queue item with a stable, renderable shape. ``detail`` = the WHY, ``action`` = the fix.

    ``code`` is a stable machine token (e.g. "gate_blocked", "go_live", "lane_retry:youtube") so
    the dashboard can key/group items; the title/detail/action are the human (PT-BR) strings."""
    return {"code": str(code), "title": str(title), "detail": str(detail), "action": str(action)}


def _empty_queue() -> Dict[str, Any]:
    """The idle queue: nothing open, nothing to do, nothing blocking (the all-green case)."""
    return {"open_items": [], "next_actions": [], "blocking": [], "idle": True}


# --------------------------------------------------------------------------- #
# Safe readers (TOTAL -- a wrong-shaped result never raises).
# --------------------------------------------------------------------------- #
def _safe_float(value: Any) -> float:
    """Coerce to float; any surprise -> 0.0 (never raises)."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _structured(result: Any) -> Optional[Mapping[str, Any]]:
    """The result's ``structured`` payload IFF it is a mapping, else None (TOTAL)."""
    s = getattr(result, "structured", None)
    return s if isinstance(s, Mapping) else None


def _run_mode(structured: Optional[Mapping[str, Any]]) -> str:
    """The W1 envelope ``run_mode`` (e.g. 'offline-scaffold' / 'offline-deterministic' / an LLM
    mode), or "" when there is no envelope (the generic build + universe routes carry none). A
    missing envelope -> "" -> this module makes NO liveness claim (honest)."""
    if not structured:
        return ""
    val = structured.get("run_mode")
    return str(val).strip() if isinstance(val, str) else ""


def _confidence_breakdown(structured: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """The W1 envelope ``confidence_breakdown`` ({overall, source_count, recency, agreement}),
    or {} when absent (TOTAL)."""
    if not structured:
        return {}
    cb = structured.get("confidence_breakdown")
    return dict(cb) if isinstance(cb, Mapping) else {}


def _endpoint_status(structured: Optional[Mapping[str, Any]]) -> Dict[str, str]:
    """The research_universe per-lane ``endpoint_status`` ({lane: ok|blocked|skipped|failed:..}),
    or {} when absent (only the universe route carries it). TOTAL."""
    if not structured:
        return {}
    es = structured.get("endpoint_status")
    if not isinstance(es, Mapping):
        return {}
    out: Dict[str, str] = {}
    for lane, st in es.items():
        out[str(lane)] = str(st).strip() if st is not None else ""
    return out


def _structured_notes(structured: Optional[Mapping[str, Any]]) -> List[str]:
    """The generator-emitted ``notes`` list (honest, builder-authored), or [] (TOTAL)."""
    if not structured:
        return []
    notes = structured.get("notes")
    if isinstance(notes, (list, tuple)):
        return [str(n) for n in notes if n]
    return []


def _lane_label(lane: str) -> str:
    """A friendly display label for a lane slug, else the slug itself."""
    return _LANE_LABEL.get(lane, lane)


def _lane_retry_hint(lane: str) -> str:
    """The VERIFIED per-lane credential/source retry hint, else the generic honest fallback."""
    return _LANE_CREDENTIAL_HINT.get(lane, _GENERIC_LANE_HINT)


# --------------------------------------------------------------------------- #
# Rule helpers.
# --------------------------------------------------------------------------- #
def _gate_failure_reason(score: float, structured: Optional[Mapping[str, Any]]) -> str:
    """The WHY for a gate failure (honest). Quotes the score vs the floor ONLY when a real
    numeric score is present (> 0); otherwise states the gate verdict plainly. Surfaces up to two
    generator-emitted notes when available (they carry the builder's own reason)."""
    reasons: List[str] = []
    if score > 0.0:
        reasons.append("score %.1f abaixo do piso de %.1f" % (score, _SCORE_FLOOR))
    else:
        reasons.append("o gate retornou reprovado (passed=false)")
    notes = _structured_notes(structured)
    if notes:
        reasons.append("notas do gerador: " + "; ".join(notes[:2]))
    return "; ".join(reasons)


# --------------------------------------------------------------------------- #
# THE deriver (TOTAL -- self-guarding degrade-never).
# --------------------------------------------------------------------------- #
def derive_action_queue(result: Any) -> Dict[str, Any]:
    """Derive {open_items, next_actions, blocking, idle} from a finished CapabilityResult.

    DATA-DRIVEN + NEVER-FABRICATE -- the rules (in order):
      1. status == 'error'         -> a BLOCKING item (the run errored): the captured errors as
                                       the WHY + "rode novamente / verifique a fonte" as the fix.
      2. status == 'not_attached'  -> a NEXT_ACTION: attach the module (the compose-by-talking-to
                                       -N07 loop). NOT blocking -- it is a clean, declared state.
      3. not passed (gate)         -> a BLOCKING item (BLOQUEADO): the score-vs-floor / verdict as
                                       the WHY + "refine os inputs e rode novamente" as the fix.
      4. run_mode == offline-scaffold -> a NEXT_ACTION (supply a credential / live source for real
                                       data) + an OPEN_ITEM (data is illustrative). Fires even on a
                                       PASSED run -- the gap-#4 insight: an APROVADO offline run is
                                       still illustrative and the user should know how to go live.
      5. low numeric confidence factor -> an OPEN_ITEM per thin factor ("thin on <factor>"). Only
                                       real numbers below the threshold; null factors are skipped.
      6. research_universe blocked/failed lanes -> a NEXT_ACTION per lane with the VERIFIED retry
                                       hint (credential/source). skipped/ok/unknown lanes are not
                                       nagged (honest: skipped means not selected for this seed).
      7. all green                 -> empty (idle) queue.

    TOTAL: any exception while reading the result -> the empty (idle) queue (degrade-never)."""
    try:
        return _derive(result)
    except Exception:
        # Belt-and-braces: the caller already guards, but the deriver is self-safe too so a
        # direct caller (dashboard / test) can never be broken by a malformed result.
        return _empty_queue()


def _derive(result: Any) -> Dict[str, Any]:
    # A real CapabilityResult ALWAYS carries a ``status`` field (the dataclass default is "error").
    # An object that lacks it is NOT a derivable result (None / a primitive / an unrelated object)
    # -> the idle queue. This keeps the deriver honest: a non-result is never mislabelled as a
    # failed gate (a bare object reads passed=False, which would otherwise look like BLOQUEADO).
    if not hasattr(result, "status"):
        return _empty_queue()

    status = str(getattr(result, "status", "") or "")
    passed = bool(getattr(result, "passed", False))
    score = _safe_float(getattr(result, "score", 0.0))
    errors = [str(e) for e in (getattr(result, "errors", None) or [])]
    structured = _structured(result)

    open_items: List[Dict[str, str]] = []
    next_actions: List[Dict[str, str]] = []
    blocking: List[Dict[str, str]] = []

    # -- Rules 1-3: the gate / run outcome (mutually exclusive by status). -----------------
    if status == "error":
        detail = "; ".join(errors[:3]) if errors else "a execucao falhou sem detalhe"
        blocking.append(_item(
            "run_error",
            "A execucao falhou",
            detail=detail,
            action="rode novamente; se persistir, verifique a credencial / a fonte e os logs",
        ))
    elif status == "not_attached":
        next_actions.append(_item(
            "attach_module",
            "Modulo nao acoplado",
            detail="esta capability esta declarada mas nao foi acoplada (enabled) para este tenant",
            action="acople o modulo (peca ao N07 ou ligue no gerenciador de modulos) e rode de novo",
        ))
    elif not passed:
        blocking.append(_item(
            "gate_blocked",
            "Reprovado no gate (BLOQUEADO)",
            detail=_gate_failure_reason(score, structured),
            action="refine os inputs (mais contexto / fontes) e rode novamente para passar o gate",
        ))

    # -- Rule 4: an offline-scaffold run is illustrative -> how to go live (even when APROVADO). -
    if _run_mode(structured) == _RUN_MODE_OFFLINE:
        open_items.append(_item(
            "illustrative_data",
            "Dados ilustrativos (modo offline-scaffold)",
            detail="nenhuma credencial/LLM foi usada; a estrutura e real, mas os dados sao ilustrativos",
        ))
        next_actions.append(_item(
            "go_live",
            "Forneca uma credencial ou fonte ao vivo",
            action="rode com uma credencial (byo_api_key) ou conecte uma fonte real para dados ao vivo",
        ))

    # -- Rule 5: a thin (low, numeric) confidence factor -> add sources / refresh. ----------
    cb = _confidence_breakdown(structured)
    for factor in ("source_count", "recency", "agreement"):
        val = cb.get(factor)
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            continue  # null / non-numeric = honest "not computed" -> never a fabricated complaint
        if float(val) < _CONFIDENCE_THIN:
            open_items.append(_item(
                "thin_confidence:%s" % factor,
                "Confianca baixa em %s" % factor,
                detail="fator %s = %.2f (abaixo de %.2f) -- adicione fontes / atualize os dados"
                % (factor, float(val), _CONFIDENCE_THIN),
            ))

    # -- Rule 6: research_universe blocked/failed lanes -> a per-lane retry hint. -----------
    for lane, st in sorted(_endpoint_status(structured).items()):
        token = st.lower()  # compare case-insensitively; DISPLAY the original ``st`` verbatim
        if token == "blocked" or token.startswith("failed"):
            next_actions.append(_item(
                "lane_retry:%s" % lane,
                "Lane %s: %s" % (_lane_label(lane), st),
                detail="a lane %s nao retornou dados (%s)" % (_lane_label(lane), st),
                action=_lane_retry_hint(lane),
            ))

    idle = not (open_items or next_actions or blocking)
    return {
        "open_items": open_items,
        "next_actions": next_actions,
        "blocking": blocking,
        "idle": idle,
    }


__all__ = ["derive_action_queue"]


# --------------------------------------------------------------------------- #
# Tiny offline self-demo (proof): green vs offline vs blocked-lane queues. ASCII.
# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover - manual proof helper, not a test
    import json
    from types import SimpleNamespace

    green = SimpleNamespace(
        status="persisted", passed=True, score=9.2, errors=[],
        structured={"run_mode": "offline-deterministic",
                    "confidence_breakdown": {"overall": 9.2, "source_count": 0.8,
                                             "recency": 0.7, "agreement": 0.9}},
    )
    offline = SimpleNamespace(
        status="produced", passed=True, score=8.5, errors=[],
        structured={"run_mode": "offline-scaffold",
                    "confidence_breakdown": {"overall": 8.5, "source_count": None,
                                             "recency": None, "agreement": None}},
    )
    universe = SimpleNamespace(
        status="produced", passed=True, score=0.0, errors=[],
        structured={"endpoint_status": {"cnpj": "ok", "ibge": "ok",
                                        "reclame_aqui": "blocked", "youtube": "failed: TimeoutError",
                                        "seo": "skipped"}},
    )
    blocked = SimpleNamespace(
        status="produced_unpersisted", passed=False, score=4.0,
        errors=[], structured={"run_mode": "offline-scaffold",
                               "confidence_breakdown": {"overall": 4.0}},
    )
    for name, r in (("GREEN", green), ("OFFLINE", offline),
                    ("UNIVERSE", universe), ("GATE-BLOCKED", blocked)):
        print("=== %s ===" % name)
        print(json.dumps(derive_action_queue(r), ensure_ascii=True, indent=2, sort_keys=True))
