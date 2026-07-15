"""GOAP state-space search core -- A* over PlanOperator effects (cexai-specs/02_ruflo US P2).

Pure algorithm, offline (Article XIV: no live LLM, no network, no provider). A world
STATE is a ``frozenset[str]`` of established facts; an operator is APPLICABLE when its
``preconditions`` are a subset of the state, and APPLYING it unions in its ``effects``.
A* searches from the empty state to any state that is a superset of the goal facts,
minimizing summed operator cost (v1 = token-only cost, FR-010). The heuristic is the
count of unmet goal facts -- admissible while every operator costs >= 1.0 and adds goal
facts no faster than one per step (true for the v0.3 fixtures), so the first goal node
popped is cost-optimal.

This module raises only ``PlanInvalidError`` (from ``verify_chain``). The planner layer
(``planner.py``) maps an unreachable-by-cycle goal to ``CyclicGoalError`` using
``find_cycle``, and an unreachable-by-missing-producer goal to a typed NO_PLAN result.

absorbs: 02_ruflo/goap
"""

from __future__ import annotations

import heapq
import itertools
from dataclasses import dataclass

from cexai.orchestration._shared.errors import PlanInvalidError
from cexai.orchestration._shared.types import PlanOperator


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Outcome of an A* search. ``status`` is one of:

      * ``valid``   -- goal reached; ``operators`` is the cost-optimal ordered chain.
      * ``partial`` -- token budget exhausted before the goal; ``operators`` is the
                       best-effort prefix (most progress toward the goal under budget).
      * ``no_plan`` -- search space exhausted without the budget biting; the goal is
                       unreachable and ``operators`` is empty.

    ``cost`` is the summed operator cost of ``operators``.
    """

    status: str
    operators: tuple[PlanOperator, ...]
    cost: float


def parse_goal_facts(goal: str) -> frozenset[str]:
    """Split a v1 goal string into target facts (whitespace- or comma-separated).

    v1 scope (per the W1 handoff): ``goal`` names the target fact(s) the plan must
    establish; full natural-language goal decomposition is LLM-assisted and OUT of W1
    scope (Article XIV: no live LLM in tests). ``"approved"`` -> ``{"approved"}``;
    ``"draft, approved"`` -> ``{"draft", "approved"}``.
    """
    return frozenset(goal.replace(",", " ").split())


def reachable_facts(operators: tuple[PlanOperator, ...]) -> frozenset[str]:
    """Facts establishable from the empty state with UNLIMITED budget (a cost-blind
    forward fixpoint). Lets the planner separate 'goal truly unreachable' (NO_PLAN /
    CyclicGoalError) from 'goal merely too expensive for the current budget' ([PARTIAL])."""
    facts: set[str] = set()
    changed = True
    while changed:
        changed = False
        for op in operators:
            if set(op.preconditions) <= facts and not set(op.effects) <= facts:
                facts |= set(op.effects)
                changed = True
    return frozenset(facts)


def needed_facts(
    operators: tuple[PlanOperator, ...], goal_facts: frozenset[str]
) -> frozenset[str]:
    """Backward closure of the facts the goal depends on: the goal facts plus, for any
    operator that produces a needed fact, that operator's preconditions (to fixpoint).
    Drives the best-effort partial tie-break (progress toward the goal) and the
    relevance filter for cycle detection."""
    needed: set[str] = set(goal_facts)
    changed = True
    while changed:
        changed = False
        for op in operators:
            if set(op.effects) & needed and not set(op.preconditions) <= needed:
                needed |= set(op.preconditions)
                changed = True
    return frozenset(needed)


def find_cycle(operators: tuple[PlanOperator, ...]) -> tuple[str, ...] | None:
    """Return a producer/consumer dependency cycle among ``operators`` as an ordered
    tuple of operator names, or ``None`` if the dependency graph is acyclic. An edge
    C -> P exists when operator C has a precondition that operator P produces (P enables
    C); a cycle means a set of operators mutually block one another and none can ground.

    Iterative explicit-stack DFS (white/gray/black colouring) -- NOT recursive -- so a
    large operator catalog cannot hit Python's recursion limit (R-235: this mirrors the
    iterative approach ``topology.validate._find_cycle`` already uses; the two cycle
    detectors were implemented twice with different robustness before this fix)."""
    producers: dict[str, list[int]] = {}
    for i, op in enumerate(operators):
        for effect in op.effects:
            producers.setdefault(effect, []).append(i)
    adjacency: dict[int, list[int]] = {i: [] for i in range(len(operators))}
    for i, op in enumerate(operators):
        for pre in op.preconditions:
            for j in producers.get(pre, ()):
                if j != i:
                    adjacency[i].append(j)

    white, gray, black = 0, 1, 2
    color = [white] * len(operators)

    for s in range(len(operators)):
        if color[s] != white:
            continue
        # Each stack frame is [node, next-neighbour-index]; ``path`` is the current
        # gray chain, sliced out to build the cycle when a gray neighbour is hit.
        stack: list[list[int]] = [[s, 0]]
        path: list[int] = [s]
        color[s] = gray
        while stack:
            node, index = stack[-1]
            neighbours = adjacency[node]
            if index < len(neighbours):
                stack[-1][1] = index + 1
                nxt = neighbours[index]
                state = color[nxt]
                if state == gray:
                    start = path.index(nxt)
                    return tuple(operators[k].name for k in path[start:])
                if state == white:
                    color[nxt] = gray
                    stack.append([nxt, 0])
                    path.append(nxt)
            else:
                color[node] = black
                stack.pop()
                path.pop()
    return None


def verify_chain(operators: tuple[PlanOperator, ...]) -> None:
    """Defensive precondition check on an ORDERED operator chain, starting from the empty
    state (02 US P2 acceptance #2). Raises ``PlanInvalidError(step_id,
    violated_precondition)`` at the first operator whose preconditions are not all met by
    the prior operators' effects. Returns ``None`` for a valid chain."""
    state: set[str] = set()
    for op in operators:
        for pre in op.preconditions:
            if pre not in state:
                raise PlanInvalidError(step_id=op.name, violated_precondition=pre)
        state |= set(op.effects)


def astar(
    operators: tuple[PlanOperator, ...],
    goal_facts: frozenset[str],
    token_budget: float,
    relevant: frozenset[str] | None = None,
) -> SearchResult:
    """A* from the empty state to any superset of ``goal_facts``, minimizing summed
    operator cost and bounded by ``token_budget``. Returns the optimal plan (``valid``),
    a best-effort prefix (``partial``, when the budget pruned the path to the goal), or
    ``no_plan`` (goal unreachable within the explored, no-operator-reuse space).

    ``relevant`` (default = ``goal_facts``) is the backward-closure fact set used only to
    rank the best-effort partial by progress toward the goal. Operators are never reused
    on a path -- in additive GOAP re-applying an operator only adds cost, so this keeps
    the search finite without losing any optimal plan.
    """
    if relevant is None:
        relevant = goal_facts
    start: frozenset[str] = frozenset()
    if goal_facts <= start:
        return SearchResult("valid", (), 0.0)

    counter = itertools.count()
    # heap entries: (f, tiebreak_counter, g, state, path). The unique counter makes
    # every entry orderable, so heapq never compares the frozenset / PlanOperator payload.
    heap: list[tuple[float, int, float, frozenset[str], tuple[PlanOperator, ...]]] = [
        (float(len(goal_facts - start)), next(counter), 0.0, start, ())
    ]
    best_g: dict[frozenset[str], float] = {}
    budget_pruned = False

    best_path: tuple[PlanOperator, ...] = ()
    best_cost = 0.0
    # Rank partial progress by (unmet goal facts, -relevant facts present, cost spent).
    best_key = (len(goal_facts - start), -len(relevant & start), 0.0)

    while heap:
        _, _, g, state, path = heapq.heappop(heap)
        if goal_facts <= state:
            return SearchResult("valid", path, g)
        settled = best_g.get(state)
        if settled is not None and settled <= g:
            continue
        best_g[state] = g

        key = (len(goal_facts - state), -len(relevant & state), g)
        if key < best_key:
            best_key, best_path, best_cost = key, path, g

        for op in operators:
            if op in path:
                continue
            if not set(op.preconditions) <= state:
                continue
            new_state = state | set(op.effects)
            if new_state == state:
                continue  # operator adds nothing here -- no progress
            g2 = g + op.cost
            if g2 > token_budget:
                budget_pruned = True
                continue
            f2 = g2 + len(goal_facts - new_state)
            heapq.heappush(heap, (f2, next(counter), g2, new_state, path + (op,)))

    if budget_pruned:
        return SearchResult("partial", best_path, best_cost)
    return SearchResult("no_plan", (), 0.0)
