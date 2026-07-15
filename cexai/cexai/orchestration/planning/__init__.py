"""Planning subsystem -- GOAP state-space planner over plain-English goals.

Decomposes a goal into a verified sequence of ``PlanOperator`` (preconditions /
effects / cost) and refuses invalid or cyclic plans with typed errors
(cexai-specs/02_ruflo US P2). ``GoapPlanner`` (v0.3-W1) implements the frozen
``Planner`` contract via A* state-space search (``goap.py``); the frozen
``Plan`` / ``PlanOperator`` / ``Planner`` contracts live in
``cexai.orchestration._shared.types``. This subsystem REUSES the existing
``planning_strategy`` kind and registers NO new kind.

absorbs: 02_ruflo/goap
"""

from .planner import GoapPlanner

__all__ = ["GoapPlanner"]
