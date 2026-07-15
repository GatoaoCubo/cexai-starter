"""GoapPlanner -- the concrete GOAP ``Planner`` (cexai-specs/02_ruflo US P2 / FR-004/005).

Implements the frozen ``Planner`` protocol from ``cexai.orchestration._shared.types``:
``plan(goal) -> Plan``. Search is A* over operator state-space (see ``goap.py``); the
planner adds the typed-result policy on top of the raw search:

  * unreachable by a missing producer  -> Plan(validation_status="NO_PLAN"), empty chain,
                                          NO fabricated steps (02 US P2 edge case).
  * unreachable by a dependency cycle   -> raise CyclicGoalError(cycle) (02 US P2 edge case).
  * reachable but over token budget      -> Plan(validation_status="[PARTIAL]"), best-effort
                                          prefix (02 US P2 edge case).
  * reachable                            -> Plan(validation_status="valid"); the lower-cost
                                          plan is chosen and sibling viable plans are recorded
                                          in ``alternatives`` (02 US P2 acceptance #3).

This REUSES the existing ``planning_strategy`` kind -- a ``Plan`` maps to
``planning_strategy.operators[]`` -- and registers NO new kind.

absorbs: 02_ruflo/goap
"""

from __future__ import annotations

from cexai.orchestration._shared.errors import CyclicGoalError
from cexai.orchestration._shared.types import Plan, PlanOperator

from . import goap

# v1 default is unbounded: token-only cost (FR-010), no artificial depth cap. Callers
# pass a finite budget to bound search and opt into [PARTIAL] best-effort results.
DEFAULT_TOKEN_BUDGET: float = float("inf")


class GoapPlanner:
    """A goal-oriented action planner satisfying the frozen ``Planner`` protocol.

    ``operators`` is the catalog the planner searches; ``token_budget`` caps the summed
    operator cost A* will spend before returning a ``[PARTIAL]`` best-effort plan
    (default unbounded -- v1 cost is token-only, FR-010).
    """

    def __init__(
        self,
        operators: tuple[PlanOperator, ...],
        *,
        token_budget: float = DEFAULT_TOKEN_BUDGET,
    ) -> None:
        self._operators = tuple(operators)
        self._token_budget = token_budget

    def plan(self, goal: str) -> Plan:
        """Decompose ``goal`` (a target fact, or whitespace/comma-separated facts) into a
        verified, cost-optimized ``Plan``. See the module docstring for the full
        typed-result policy."""
        goal_facts = goap.parse_goal_facts(goal)
        if not goal_facts:
            return Plan(goal=goal, operators=(), total_cost=0.0, validation_status="valid")

        reachable = goap.reachable_facts(self._operators)
        if not goal_facts <= reachable:
            cycle = self._blocking_cycle(goal_facts, reachable)
            if cycle is not None:
                raise CyclicGoalError(cycle)
            return Plan(goal=goal, operators=(), total_cost=0.0, validation_status="NO_PLAN")

        relevant = goap.needed_facts(self._operators, goal_facts)
        result = goap.astar(self._operators, goal_facts, self._token_budget, relevant)
        if result.status == "valid":
            goap.verify_chain(result.operators)  # defensive: never fires for an A* chain
            alternatives = self._alternatives(goal, goal_facts, relevant, result.operators)
            return Plan(
                goal=goal,
                operators=result.operators,
                total_cost=result.cost,
                validation_status="valid",
                alternatives=alternatives,
            )
        # Reachable with unlimited budget but not within token_budget -> best effort.
        return Plan(
            goal=goal,
            operators=result.operators,
            total_cost=result.cost,
            validation_status="[PARTIAL]",
        )

    @staticmethod
    def verify(operators: tuple[PlanOperator, ...]) -> None:
        """Defensive precondition check on an ordered operator chain (delegates to
        ``goap.verify_chain``). Raises ``PlanInvalidError(step_id, violated_precondition)``
        on the first operator whose preconditions are not met by prior effects."""
        goap.verify_chain(operators)

    def _blocking_cycle(
        self, goal_facts: frozenset[str], reachable: frozenset[str]
    ) -> tuple[str, ...] | None:
        """Return a dependency cycle that BLOCKS the goal (goal-relevant operators that can
        never ground from the empty state), or ``None`` if the goal is simply unsatisfiable
        by a missing producer. The relevance filter keeps an unrelated cycle elsewhere in
        the catalog from masking a plain NO_PLAN."""
        needed = goap.needed_facts(self._operators, goal_facts)
        blocked = tuple(
            op
            for op in self._operators
            if not set(op.preconditions) <= reachable and set(op.effects) & needed
        )
        return goap.find_cycle(blocked)

    def _alternatives(
        self,
        goal: str,
        goal_facts: frozenset[str],
        relevant: frozenset[str],
        chosen: tuple[PlanOperator, ...],
    ) -> tuple[Plan, ...]:
        """Find sibling viable plans via leave-one-out A*: omit each operator of the chosen
        plan in turn and re-search. Distinct results (by operator-name set) become
        alternatives, sorted by ascending total cost (02 US P2 acceptance #3)."""
        seen = {frozenset(op.name for op in chosen)}
        alternatives: list[Plan] = []
        for omit in chosen:
            reduced = tuple(op for op in self._operators if op != omit)
            result = goap.astar(reduced, goal_facts, self._token_budget, relevant)
            if result.status != "valid" or not result.operators:
                continue
            key = frozenset(op.name for op in result.operators)
            if key in seen:
                continue
            seen.add(key)
            alternatives.append(
                Plan(
                    goal=goal,
                    operators=result.operators,
                    total_cost=result.cost,
                    validation_status="valid",
                )
            )
        alternatives.sort(key=lambda p: (p.total_cost, tuple(op.name for op in p.operators)))
        return tuple(alternatives)
