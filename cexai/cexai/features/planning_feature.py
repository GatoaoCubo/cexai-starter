"""GOAP planning feature -- decompose a goal into a verified plan (activation wave).

A thin wrapper exposing the GOAP state-space planner
(``cexai.orchestration.planning.GoapPlanner``) through both invocation interfaces:
the library API (``run_feature("plan", ...)``) and the CLI (``cexai plan ...``). It
constructs a ``GoapPlanner`` over a caller-supplied operator catalog and returns the
typed ``Plan`` for ``goal``. The search is a pure A* over operator effects -- offline,
no live LLM and no network (Article XIV).

Public contract (keep EXACT):
    plan(goal, operators=(), *, token_budget=DEFAULT_TOKEN_BUDGET) -> Plan
        ``goal``      -- the target fact(s) the plan must establish (a single fact, or
                         whitespace/comma-separated facts; see goap.parse_goal_facts).
        ``operators`` -- the ``PlanOperator`` catalog the planner searches (each declares
                         preconditions/effects/cost). Defaults to the empty catalog: an
                         empty goal then yields a trivially ``valid`` empty Plan and any
                         non-empty goal yields a typed ``NO_PLAN`` (never a fabricated
                         step) -- the same documented boundary the planner enforces.
        ``token_budget`` -- caps summed operator cost before A* returns a ``[PARTIAL]``
                         best-effort plan (default unbounded -- v1 cost is token-only).
        Returns a frozen ``Plan`` (operators / total_cost / validation_status /
        alternatives).

Invocation: registered at import as the feature ``"plan"`` so it runs via both the
library API and the CLI (Article II / FR-006). The CLI / library only see the feature
once ``cexai.features`` is imported (the registration is a module side effect). A
real plan over a non-empty catalog is a library call (the operators are typed objects,
not CLI strings); the CLI surface plans over the empty catalog.

absorbs: 02_ruflo/goap
"""

from __future__ import annotations

from cexai.foundation.invocation import register_feature
from cexai.orchestration._shared.types import Plan, PlanOperator
from cexai.orchestration.planning import GoapPlanner
from cexai.orchestration.planning.planner import DEFAULT_TOKEN_BUDGET

__all__ = ["plan"]


def plan(
    goal: str,
    operators: tuple[PlanOperator, ...] = (),
    *,
    token_budget: float = DEFAULT_TOKEN_BUDGET,
) -> Plan:
    """Decompose ``goal`` into a verified, cost-optimized ``Plan`` over ``operators``.

    Constructs a ``GoapPlanner`` over the supplied operator catalog and delegates to its
    frozen ``.plan(goal)`` contract. See the module docstring for the empty-catalog
    boundary (empty goal -> valid empty plan; non-empty goal -> NO_PLAN, no fabricated
    steps) and the typed-result policy."""
    return GoapPlanner(tuple(operators), token_budget=token_budget).plan(goal)


# Module side effect: expose the feature to both invocation interfaces.
register_feature("plan", plan)
