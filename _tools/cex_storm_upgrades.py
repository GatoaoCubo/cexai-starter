#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI STORM research-engine upgrades -- OPT-IN, ADDITIVE over cex_run_research.

TWO upgrades lifted from the best OSS deep-research frameworks, ADDED as a SEPARATE module so the
shipped cex_run_research core + ALL its tests stay byte-identical (the upgrades are OPT-IN, default
OFF). This module imports NOTHING heavy and binds NO LLM key / browser / network at import. It is a
PURE library of two helpers + one small opt-in plan-enrichment seam.

  1  MULTI-PERSPECTIVE QUESTION GENERATION (Stanford Co-STORM, Jiang et al. 2024).
     STORM's edge is asking from MANY expert perspectives, not one. Co-STORM composes a "perspective-
     guided" question pool. generate_multiperspective_questions(topic, perspectives, n_per, llm_fn)
     composes research SUB-QUESTIONS from N DIVERSE perspectives (default buyer / competitor /
     skeptic / technical / economic / regulatory). PURE + deterministic by default -- per-perspective
     question-FRAME templating, NO LLM required (method='template', honest). An OPTIONAL injected
     llm_fn seam enables real generation (method='llm'); WITHOUT it the deterministic frames run.
     It composes QUESTIONS, never answers -- it CANNOT fabricate a fact (n05 never-fabricate).

  2  BUDGET-BOUNDED REASONING LOOP (Jina node-DeepResearch / "DeepResearch on a token budget").
     Jina's engine reasons in a loop UNTIL a token budget is hit, then returns the best partial --
     it never runs unbounded and never pads to "finish". budget_bounded_loop(step_fn, budget,
     max_steps) calls step_fn(state) iteratively, accumulates the cost each step REPORTS, and STOPS
     when the budget is exceeded OR max_steps is reached OR a step signals converged. Returns the
     accumulated results + an HONEST stopped_reason -- a partial is returned as a partial, never
     fabricated into a full answer (n05 honest-partial > false completion).

OPT-IN WIRING into cex_run_research (default OFF -> byte-identical):
  enrich_plan_with_multiperspective(plan, options) is the 3-line wiring seam. cex_run_research only
  calls it when env CEX_STORM_MULTIPERSPECTIVE=1 OR options['use_multiperspective'] is True (mirrors
  the existing use_tier_router / use_storm opt-in precedent). When OFF it is never called and the
  plan's existing 5-angle path is unchanged. It enriches the plan's 'angles' (de-duplicated, capped)
  with multi-perspective sub-questions WITHOUT removing any existing angle -- additive only.

INVARIANTS (task contract + .claude/rules/ascii-code-rule.md):
  * degrade-never: bad input / a step raising -> a HONEST partial, never an exception bubbling up
    from the helpers' own logic (the loop surfaces a step error as stopped_reason, returns partial).
  * never-fabricate: the generator composes QUESTIONS (not answers); the loop returns the partial
    results it actually accumulated -- neither invents a datum.
  * ASCII-only; \\uXXXX escapes for any PT-BR accent that must survive at runtime.
  * additive / default-OFF -> ZERO regression. This module does NOT modify cex_run_research; the
    wiring there is a small guarded branch that is skipped unless the flag is set.

Frameworks referenced (method, not code -- clean-room): Stanford STORM / Co-STORM
(github.com/stanford-oval/storm) perspective-guided question generation; Jina node-DeepResearch
(github.com/jina-ai/node-DeepResearch) budget-bounded reason-act loop.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

# --------------------------------------------------------------------------- #
# Opt-in flags (mirror cex_run_research.USE_TIER_ROUTER_ENV / the use_storm precedent).
# --------------------------------------------------------------------------- #
USE_MULTIPERSPECTIVE_ENV = "CEX_STORM_MULTIPERSPECTIVE"
USE_MULTIPERSPECTIVE_OPTION = "use_multiperspective"

# The DEFAULT diverse perspective set (Co-STORM "perspective-guided" pool). Each is an expert lens
# that asks DIFFERENT questions about the same topic -- diversity is the whole point (a single
# perspective produces a narrow, biased question set; STORM's gain is the breadth). Order is the
# canonical emit order (deterministic). These are perspective KEYS (ASCII identifiers); the human
# label + the question frames live in _PERSPECTIVE_FRAMES.
DEFAULT_PERSPECTIVES: tuple = (
    "buyer", "competitor", "skeptic", "technical", "economic", "regulatory",
)

# Caps (validate/cap inputs -- never let a caller blow up the pool). A pool of
# len(perspectives) * n_per questions; cap each so the worst case stays bounded + cheap.
MAX_PERSPECTIVES = 12
MAX_QUESTIONS_PER_PERSPECTIVE = 8
# The hard ceiling on the flattened question pool (defense in depth past the per-axis caps).
MAX_TOTAL_QUESTIONS = MAX_PERSPECTIVES * MAX_QUESTIONS_PER_PERSPECTIVE

# Per-perspective question FRAMES. Each frame is a template with a single '%s' for the topic. The
# frames encode WHAT that expert lens interrogates -- a buyer asks about fit/value, a skeptic asks
# about failure modes, a regulator asks about compliance. n_per selects the first N frames for that
# perspective (so n_per is deterministic + stable). An UNKNOWN perspective key falls back to a
# generic frame set (degrade-never -> still composes usable questions). ASCII-only (these are EN
# research questions; no accents needed).
_PERSPECTIVE_FRAMES: Dict[str, List[str]] = {
    "buyer": [
        "What problem does %s solve for the buyer, and how urgent is it?",
        "What are the must-have features a buyer expects in %s?",
        "What price would a buyer consider fair for %s, and why?",
        "What objections or doubts stop a buyer from purchasing %s?",
        "Which alternatives does a buyer compare %s against?",
        "What proof or reviews does a buyer need before buying %s?",
        "How does a buyer discover and research %s?",
        "What post-purchase support does a buyer expect for %s?",
    ],
    "competitor": [
        "Who are the leading competitors offering %s, and what is their share?",
        "How do competitors price and bundle %s?",
        "What is each competitor's strongest differentiator for %s?",
        "Where are competitors weak or under-serving demand for %s?",
        "What marketing channels do competitors use to sell %s?",
        "How fast are new entrants appearing in the %s space?",
        "What do competitor reviews reveal as the top complaint about %s?",
        "Which competitor positioning gap is open for %s?",
    ],
    "skeptic": [
        "What are the most common failure modes or defects reported for %s?",
        "What claims about %s are unsupported or commonly exaggerated?",
        "Under what conditions does %s underperform or break?",
        "What hidden costs or trade-offs come with %s?",
        "What evidence would falsify the case for %s?",
        "What are the worst customer experiences documented for %s?",
        "Which risks of %s are under-discussed by sellers?",
        "What would make a careful buyer walk away from %s?",
    ],
    "technical": [
        "What are the key technical specifications that differentiate %s?",
        "What materials, components, or standards define quality in %s?",
        "How is %s manufactured, and what affects its durability?",
        "What certifications or test results matter for %s?",
        "How does %s integrate with or depend on other products?",
        "What measurable performance metrics rank options of %s?",
        "What are the maintenance or compatibility constraints of %s?",
        "Which technical trade-offs distinguish premium from budget %s?",
    ],
    "economic": [
        "What is the total cost of ownership for %s over its lifetime?",
        "How elastic is demand for %s with respect to price?",
        "What margin structure is typical for sellers of %s?",
        "How do supply, import, or logistics costs shape %s pricing?",
        "What is the unit economics break-even for selling %s?",
        "How seasonal or cyclical is demand for %s?",
        "What macro or currency factors move the %s market?",
        "What price points maximize revenue versus volume for %s?",
    ],
    "regulatory": [
        "What regulations, labeling, or standards govern selling %s?",
        "What safety or compliance certifications are required for %s?",
        "What consumer-protection or warranty rules apply to %s?",
        "What import, tax, or customs constraints affect %s?",
        "What advertising claims are restricted or prohibited for %s?",
        "What data, privacy, or environmental rules touch %s?",
        "What liability exposure comes with selling %s?",
        "Which jurisdictions impose the strictest rules on %s?",
    ],
}

# The generic fallback frames for an UNKNOWN perspective key (degrade-never -> usable questions).
_GENERIC_FRAMES: List[str] = [
    "From the %%s perspective, what are the most important facts about %s?",
    "From the %%s perspective, what risks or gaps matter for %s?",
    "From the %%s perspective, how should %s be evaluated?",
    "From the %%s perspective, what evidence is needed about %s?",
    "From the %%s perspective, what decision does %s drive?",
    "From the %%s perspective, what alternatives to %s exist?",
    "From the %%s perspective, what trade-offs define %s?",
    "From the %%s perspective, what is commonly misunderstood about %s?",
]


# --------------------------------------------------------------------------- #
# UPGRADE 1 -- Multi-perspective question generation (Co-STORM).
# --------------------------------------------------------------------------- #
def generate_multiperspective_questions(
    topic: str,
    perspectives: Optional[Sequence[str]] = None,
    n_per: int = 3,
    llm_fn: Optional[Callable[[str, str], Sequence[str]]] = None,
) -> Dict[str, Any]:
    """Compose research SUB-QUESTIONS from N DIVERSE perspectives (Co-STORM perspective-guided pool).

    PURE + DETERMINISTIC by default: with NO llm_fn, per-perspective question FRAMES are filled with
    the topic (method='template'). This is HONEST -- it composes the questions a STORM run should
    ASK; it never claims to have ANSWERED them and so cannot fabricate a fact.

    Optionally accept an injected ``llm_fn(perspective, topic) -> [questions]`` seam for REAL
    generation (method='llm'). The seam is called once per perspective; a seam that raises or
    returns nothing for a perspective DEGRADES to that perspective's template frames (so the result
    is never empty and never an exception). NEVER binds an LLM itself.

    Args:
      topic: the research subject (e.g. a product name). Coerced to a trimmed string; an empty topic
             yields an empty pool (count=0) rather than fabricating a subject.
      perspectives: the expert lenses to ask from. Default DEFAULT_PERSPECTIVES (6 diverse lenses).
                    De-duplicated (order-preserving) and capped at MAX_PERSPECTIVES.
      n_per: questions per perspective. Clamped to [1, MAX_QUESTIONS_PER_PERSPECTIVE].
      llm_fn: OPTIONAL real-generation seam; None -> deterministic template frames.

    Returns:
      {topic, perspectives, questions: [{perspective, question}], method, count}
      where method is 'template' (no llm_fn) or 'llm' (llm_fn produced at least one question) --
      'template' is the honest label when the deterministic path ran for every perspective.
    """
    clean_topic = _clean_str(topic)
    persps = _normalize_perspectives(perspectives)
    per = _clamp_int(n_per, 1, MAX_QUESTIONS_PER_PERSPECTIVE)

    questions: List[Dict[str, str]] = []
    if not clean_topic:
        # Never fabricate a subject -- an empty topic yields an empty, honest pool.
        return {
            "topic": "", "perspectives": list(persps), "questions": [],
            "method": "template", "count": 0,
        }

    used_llm = False
    seen: set = set()  # de-dup identical questions across perspectives (defensive).
    for persp in persps:
        llm_questions: List[str] = []
        if llm_fn is not None:
            llm_questions = _try_llm_fn(llm_fn, persp, clean_topic, per)
            if llm_questions:
                used_llm = True
        frames = llm_questions if llm_questions else _frames_for(persp, clean_topic, per)
        for q in frames:
            q_clean = _clean_str(q)
            if not q_clean:
                continue
            key = (persp, q_clean.lower())
            if key in seen:
                continue
            seen.add(key)
            questions.append({"perspective": persp, "question": q_clean})
            if len(questions) >= MAX_TOTAL_QUESTIONS:
                break
        if len(questions) >= MAX_TOTAL_QUESTIONS:
            break

    return {
        "topic": clean_topic,
        "perspectives": list(persps),
        "questions": questions,
        # 'llm' only when the injected seam actually produced questions; else the honest 'template'.
        "method": "llm" if used_llm else "template",
        "count": len(questions),
    }


def _normalize_perspectives(perspectives: Optional[Sequence[str]]) -> List[str]:
    """De-dup (order-preserving) + cap the perspective list. None/empty -> DEFAULT_PERSPECTIVES."""
    if not perspectives:
        return list(DEFAULT_PERSPECTIVES)
    out: List[str] = []
    seen: set = set()
    for p in perspectives:
        key = _clean_str(p).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
        if len(out) >= MAX_PERSPECTIVES:
            break
    return out or list(DEFAULT_PERSPECTIVES)


def _frames_for(perspective: str, topic: str, n_per: int) -> List[str]:
    """The first n_per template questions for a perspective (deterministic). An UNKNOWN perspective
    uses the generic frames with the perspective name woven in (degrade-never -> usable questions)."""
    frames = _PERSPECTIVE_FRAMES.get(perspective)
    if frames is not None:
        chosen = frames[:n_per]
        return [f % topic for f in chosen]
    # Unknown perspective: the generic frame carries a literal '%s' for the perspective name first,
    # then '%s' for the topic (the generic frames are pre-built with '%%s' so one % pass leaves the
    # perspective slot, then we fill both here).
    chosen_generic = _GENERIC_FRAMES[:n_per]
    out: List[str] = []
    for gf in chosen_generic:
        # gf has '%%s' (-> '%s' after the topic fill) for perspective and '%s' for topic; fill topic
        # first via the outer %, then the perspective via .replace to avoid format ambiguity.
        filled_topic = gf % topic
        out.append(filled_topic.replace("%s", perspective, 1))
    return out


def _try_llm_fn(
    llm_fn: Callable[[str, str], Sequence[str]], perspective: str, topic: str, n_per: int,
) -> List[str]:
    """Call the injected llm_fn(perspective, topic) seam (TOTAL -- a raise/non-sequence -> [], the
    caller then degrades to template frames). Caps the returned questions at n_per."""
    try:
        raw = llm_fn(perspective, topic)
    except Exception:
        return []
    if isinstance(raw, str) or not isinstance(raw, (list, tuple)):
        return []
    out: List[str] = []
    for item in raw:
        s = _clean_str(item)
        if s:
            out.append(s)
        if len(out) >= n_per:
            break
    return out


# --------------------------------------------------------------------------- #
# UPGRADE 2 -- Budget-bounded reasoning loop (Jina node-DeepResearch).
# --------------------------------------------------------------------------- #
def budget_bounded_loop(
    step_fn: Callable[[Dict[str, Any]], Mapping[str, Any]],
    budget: float,
    max_steps: int = 50,
) -> Dict[str, Any]:
    """Iterate ``step_fn(state)`` UNTIL a budget / max_steps / convergence stop (Jina-style).

    Calls step_fn(state) in a loop. ``state`` is a mutable dict the loop owns and threads through
    every step (the step reads/writes it -- the loop seeds it with 'step' + 'budget_used' so the
    step can self-limit). Each call MUST return a Mapping; the loop reads from it:
      * 'cost'      (number, default 0)  -- the cost this step consumed; accumulated into budget_used.
      * 'result'    (any, optional)      -- appended to results when present.
      * 'converged' (bool, default False)-- the step signals it is DONE -> stop with 'converged'.
      * 'stop'      (bool, default False)-- an alias for converged (explicit early stop).

    STOPS (checked in this order each iteration):
      1. the step signaled converged/stop           -> stopped_reason='converged'
      2. accumulated budget_used > budget            -> stopped_reason='budget_exhausted'
      3. step count reached max_steps                -> stopped_reason='max_steps'
    A step that RAISES stops the loop HONESTLY with stopped_reason='step_error' and returns the
    partial accumulated so far (never re-raises -- degrade-never). A non-positive budget or
    max_steps stops IMMEDIATELY with zero steps run (the partial is empty -- honest, not fabricated).

    Returns:
      {results, steps_run, budget_used, stopped_reason}
      stopped_reason in {budget_exhausted, max_steps, converged, exhausted_steps, step_error,
      invalid_budget}. 'exhausted_steps' is the (rare) clean fall-through when the loop body ends
      without any explicit stop firing -- it is reported HONESTLY, never dressed up as 'converged'.

    NEVER fabricates a result to "finish": the returned results are exactly those the steps produced;
    a partial run returns a partial (n05 honest-partial posture).
    """
    results: List[Any] = []
    budget_used: float = 0.0
    steps_run: int = 0
    state: Dict[str, Any] = {"step": 0, "budget_used": 0.0, "results": results}

    # Guard: a non-positive budget or max_steps refuses to run (honest empty partial).
    budget_num = _as_float(budget)
    max_n = _clamp_int(max_steps, 0, 10_000_000)
    if budget_num is None or budget_num <= 0 or max_n <= 0:
        return {
            "results": results, "steps_run": 0, "budget_used": 0.0,
            "stopped_reason": "invalid_budget",
        }

    stopped_reason = "exhausted_steps"
    while steps_run < max_n:
        state["step"] = steps_run
        state["budget_used"] = budget_used
        try:
            out = step_fn(state)
        except Exception:
            # Degrade-never: a step raising stops the loop honestly with the partial so far.
            stopped_reason = "step_error"
            break

        steps_run += 1
        out_map: Mapping[str, Any] = out if isinstance(out, Mapping) else {}
        if "result" in out_map:
            results.append(out_map.get("result"))
        cost = _as_float(out_map.get("cost")) or 0.0
        if cost > 0:
            budget_used += cost

        # 1. convergence signal (the step says it is done).
        if bool(out_map.get("converged")) or bool(out_map.get("stop")):
            stopped_reason = "converged"
            break
        # 2. budget exhausted (accumulated cost over the ceiling).
        if budget_used > budget_num:
            stopped_reason = "budget_exhausted"
            break
        # 3. max_steps reached on this iteration.
        if steps_run >= max_n:
            stopped_reason = "max_steps"
            break

    return {
        "results": results,
        "steps_run": steps_run,
        "budget_used": round(budget_used, 6),
        "stopped_reason": stopped_reason,
    }


# --------------------------------------------------------------------------- #
# OPT-IN WIRING SEAM into cex_run_research (default OFF -> byte-identical).
# --------------------------------------------------------------------------- #
def multiperspective_enabled(options: Optional[Mapping[str, Any]]) -> bool:
    """OPT-IN: multi-perspective plan enrichment is active iff options['use_multiperspective'] is
    True OR env CEX_STORM_MULTIPERSPECTIVE=1 (mirrors cex_run_research._use_tier_router). Default /
    absent -> False -> the existing 5-angle plan is byte-preserving."""
    if isinstance(options, Mapping) and options.get(USE_MULTIPERSPECTIVE_OPTION) is True:
        return True
    return os.environ.get(USE_MULTIPERSPECTIVE_ENV, "").strip() in ("1", "true", "True", "yes")


def enrich_plan_with_multiperspective(
    plan: Mapping[str, Any],
    options: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """The OPT-IN plan-enrichment seam cex_run_research calls (only when multiperspective_enabled).

    ADDITIVE: returns a COPY of the plan with the existing 'angles' EXTENDED by multi-perspective
    sub-questions (de-duplicated, capped) -- no existing angle is removed or reordered, and every
    other plan key is preserved verbatim. Records the structured pool under 'multiperspective' for
    provenance/audit. Degrade-never: a plan with no product_name yields the plan UNCHANGED (nothing
    to enrich). NEVER fabricates marketplace data -- it only adds research QUESTIONS to the angles.

    The 3-line wiring point in cex_run_research (after _plan_step returns `plan`):
        from cex_storm_upgrades import enrich_plan_with_multiperspective, multiperspective_enabled
        if multiperspective_enabled(options):
            plan = enrich_plan_with_multiperspective(plan, options)
    """
    enriched: Dict[str, Any] = dict(plan)  # shallow copy -- never mutate the caller's plan.
    topic = _clean_str(plan.get("product_name")) if isinstance(plan, Mapping) else ""
    if not topic:
        return enriched

    opts: Mapping[str, Any] = options if isinstance(options, Mapping) else {}
    perspectives = opts.get("perspectives") if isinstance(opts.get("perspectives"), (list, tuple)) else None
    n_per = opts.get("multiperspective_n_per", 3)
    pool = generate_multiperspective_questions(topic, perspectives=perspectives, n_per=n_per)

    existing_angles = list(enriched.get("angles") or [])
    seen_lower = {str(a).strip().lower() for a in existing_angles if str(a).strip()}
    added: List[str] = []
    for item in pool["questions"]:
        q = item["question"]
        if q.lower() not in seen_lower:
            seen_lower.add(q.lower())
            added.append(q)
    # Additive: existing angles first (order preserved), then the new perspective questions.
    enriched["angles"] = existing_angles + added
    # Provenance: the structured pool (so a downstream audit can see the perspectives used).
    enriched["multiperspective"] = {
        "perspectives": pool["perspectives"],
        "method": pool["method"],
        "count": pool["count"],
        "added": len(added),
    }
    return enriched


# --------------------------------------------------------------------------- #
# Small helpers (PURE + TOTAL) -- mirror cex_run_research's helper style.
# --------------------------------------------------------------------------- #
def _clean_str(value: Any) -> str:
    """A trimmed string, or '' (TOTAL on any input)."""
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _clamp_int(value: Any, lo: int, hi: int) -> int:
    """Coerce to int and clamp to [lo, hi] (TOTAL -- a non-number/bool -> lo)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return lo
    n = int(value)
    if n < lo:
        return lo
    if n > hi:
        return hi
    return n


def _as_float(value: Any) -> Optional[float]:
    """A finite float, or None (TOTAL -- bool/NaN/inf/non-number -> None)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    f = float(value)
    if f != f or f in (float("inf"), float("-inf")):  # NaN / inf guard.
        return None
    return f


__all__ = [
    "generate_multiperspective_questions",
    "budget_bounded_loop",
    "enrich_plan_with_multiperspective",
    "multiperspective_enabled",
    "DEFAULT_PERSPECTIVES",
    "USE_MULTIPERSPECTIVE_ENV",
    "USE_MULTIPERSPECTIVE_OPTION",
    "MAX_PERSPECTIVES",
    "MAX_QUESTIONS_PER_PERSPECTIVE",
    "MAX_TOTAL_QUESTIONS",
]
