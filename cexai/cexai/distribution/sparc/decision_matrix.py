"""SPARC-vs-spec-kit decision matrix (cexai-specs/04_claude-flow FR-004 / SC-002).

A RUNTIME form of a ``decision_record`` with ``decision_type: methodology_choice``
(the founder-rule reuse -- NOT a new kind, see the v0.5 taxonomy ADR). It documents
WHEN to pick SPARC over the default spec-kit across >= 3 dimensions, with a concrete
recommendation per dimension cell (SC-002). This is the in-memory projection; the
persisted artifact, if one is ever authored, REUSES the existing ``decision_record``
kind unchanged.

Assumptions (04 section 4): spec-kit is the DEFAULT methodology; SPARC is opt-in and
suited to the minority of pure-algorithm features.

absorbs: 04_claude-flow
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "METHODOLOGY_CHOICE_DIMENSIONS",
    "methodology_decision_record",
    "recommend",
]

# >= 3 dimensions, each with a concrete recommendation per option (SC-002). Five are
# documented; ``problem_type`` is the primary discriminator (it drives SPARC_MISFIT).
METHODOLOGY_CHOICE_DIMENSIONS: tuple[dict[str, str], ...] = (
    {
        "dimension": "problem_type",
        "prefer_sparc_when": "pure-algorithm work where pseudocode-first reasoning pays off (sorting, search, numeric kernels)",
        "prefer_spec_kit_when": "intent-driven work: UI, CRUD, integration, glue -- behavior matters more than algorithm",
    },
    {
        "dimension": "time_to_impl_budget",
        "prefer_sparc_when": "budget allows five staged artifacts before code (deliberate, gated progression)",
        "prefer_spec_kit_when": "fast path from intent to working impl is the priority",
    },
    {
        "dimension": "team_size",
        "prefer_sparc_when": "multiple contributors benefit from explicit phase gates and hand-off points",
        "prefer_spec_kit_when": "a solo or small team keeps the spec-to-code loop tight without staged gates",
    },
    {
        "dimension": "traceability_need",
        "prefer_sparc_when": "strong code->requirement traceability is required (Code phase traces_to SPEC.req-N)",
        "prefer_spec_kit_when": "lightweight traceability via the spec doc is sufficient",
    },
    {
        "dimension": "change_frequency",
        "prefer_sparc_when": "the algorithm is stable enough that staged refinement is not churned away",
        "prefer_spec_kit_when": "requirements shift often and re-walking five phases would thrash",
    },
)


def methodology_decision_record() -> dict[str, Any]:
    """The runtime ``decision_record`` (``decision_type: methodology_choice``) for the
    SPARC-vs-spec-kit choice (FR-004 / SC-002). REUSE of the existing kind, never a
    new one: shape mirrors a ``decision_record`` so a caller can persist it verbatim."""
    return {
        "kind": "decision_record",
        "decision_type": "methodology_choice",
        "title": "SPARC vs spec-kit methodology choice",
        "options": ("sparc", "spec_kit"),
        "default": "spec_kit",  # 04 assumption: spec-kit is the default
        "dimensions": METHODOLOGY_CHOICE_DIMENSIONS,
        "recommendation": (
            "Pick SPARC for algorithmic, pseudocode-first features needing staged gates "
            "and strong traceability; otherwise stay on spec-kit (the default)."
        ),
    }


def recommend(*, algorithmic: bool) -> str:
    """The single-axis recommendation on the primary ``problem_type`` dimension:
    ``sparc`` for an algorithmic feature, else ``spec_kit`` (the default). The full
    matrix above covers the secondary dimensions for a judgement call."""
    return "sparc" if algorithmic else "spec_kit"
