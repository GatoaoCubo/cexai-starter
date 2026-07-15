"""Typed topology catalog -- the 6-variant registry (03 FR-001 / FR-006 / SC-001).

The registry is the single source of truth for "which coordination variants exist
and how does the generic interpreter walk each one". It is derived from the FROZEN
``TopologyVariant`` Literal in ``_shared.types`` via ``get_args`` so it can never
silently drift from the contract: an import-time assertion fails loudly if the
descriptor table and the Literal disagree.

Each variant maps to a ``TopologyDescriptor`` carrying the two facts the
interpreter needs -- the ``order_policy`` (how to sequence node execution) and
whether the variant is ``executable`` in this wave. ``mixture_of_agents`` is
registered and structurally valid but NOT executable in W1 (its multi-provider
synthesis needs ``cexai.foundation.llm``, which lands in v0.3-W2).

absorbs: 03_swarms/topology
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import get_args

from cexai.orchestration._shared.errors import UnknownVariantError
from cexai.orchestration._shared.types import TopologyVariant

__all__ = [
    "TopologyDescriptor",
    "TopologyRegistry",
    "KNOWN_VARIANTS",
    "known_variants",
    "lookup",
]

# The canonical catalog -- the frozen Literal IS the contract; the registry must
# match it exactly (enforced by the assertion at the bottom of this module).
KNOWN_VARIANTS: tuple[str, ...] = get_args(TopologyVariant)

# Execution-order policies the interpreter understands:
#   topological -- sequence nodes by edge dependency (a source feeds its targets).
#   declared    -- sequence nodes in declared order (parallel / round-robin shapes
#                  where edges may legitimately point "backwards").
#   synthesis   -- multi-provider fan-in + merge; not executable until W2 (MoA).
_TOPOLOGICAL = "topological"
_DECLARED = "declared"
_SYNTHESIS = "synthesis"


@dataclass(frozen=True, slots=True)
class TopologyDescriptor:
    """Catalog entry for one coordination variant. ``order_policy`` tells the
    generic interpreter how to sequence node execution; ``executable`` is ``False``
    only for ``mixture_of_agents`` in W1 (deferred to W2); ``summary`` is a
    human-readable one-liner for ``cexai`` tooling."""

    variant: str
    order_policy: str
    executable: bool
    summary: str


# Declared in the SAME order as KNOWN_VARIANTS so ``tuple(_DESCRIPTORS) ==
# KNOWN_VARIANTS`` holds (the import-time guard below depends on it).
_DESCRIPTORS: dict[str, TopologyDescriptor] = {
    "sequential": TopologyDescriptor(
        variant="sequential",
        order_policy=_TOPOLOGICAL,
        executable=True,
        summary="stages run in declared order; output of stage N feeds stage N+1",
    ),
    "concurrent": TopologyDescriptor(
        variant="concurrent",
        order_policy=_DECLARED,
        executable=True,
        summary="nodes run in parallel on a shared input; no inter-node ordering",
    ),
    "hierarchical": TopologyDescriptor(
        variant="hierarchical",
        order_policy=_TOPOLOGICAL,
        executable=True,
        summary="a director fans tasks to N workers and consumes their results",
    ),
    "graph": TopologyDescriptor(
        variant="graph",
        order_policy=_TOPOLOGICAL,
        executable=True,
        summary="arbitrary DAG of agents; cycles are refused at validation time",
    ),
    "group_chat": TopologyDescriptor(
        variant="group_chat",
        order_policy=_DECLARED,
        executable=True,
        summary="agents exchange in a shared round-robin chat (may wrap around)",
    ),
    "mixture_of_agents": TopologyDescriptor(
        variant="mixture_of_agents",
        order_policy=_SYNTHESIS,
        executable=False,  # W2: needs cexai.foundation.llm multi-provider workers
        summary="N distinct-provider workers in parallel + 1 synthesizer (W2)",
    ),
}


class TopologyRegistry:
    """Lookup over the variant catalog. The default instance wraps the canonical
    ``_DESCRIPTORS``; a custom mapping may be injected (e.g. a ruflo extension set
    per 03 FR-007) without mutating the canonical table."""

    def __init__(
        self, descriptors: dict[str, TopologyDescriptor] | None = None
    ) -> None:
        self._descriptors: dict[str, TopologyDescriptor] = (
            dict(descriptors) if descriptors is not None else dict(_DESCRIPTORS)
        )

    def known_variants(self) -> tuple[str, ...]:
        """The catalog's variant names, in canonical order."""
        return tuple(self._descriptors)

    def lookup(self, variant: str) -> TopologyDescriptor:
        """Resolve ``variant`` to its descriptor, or raise ``UnknownVariantError``
        carrying the full known catalog (03 FR-006)."""
        try:
            return self._descriptors[variant]
        except KeyError:
            raise UnknownVariantError(variant, tuple(self._descriptors)) from None

    def __contains__(self, variant: object) -> bool:
        return variant in self._descriptors


# Module-level default + convenience functions over a shared canonical registry.
_REGISTRY = TopologyRegistry()


def known_variants() -> tuple[str, ...]:
    """The canonical catalog's variant names, in frozen-Literal order."""
    return _REGISTRY.known_variants()


def lookup(variant: str) -> TopologyDescriptor:
    """Resolve a variant against the canonical catalog (see ``TopologyRegistry``)."""
    return _REGISTRY.lookup(variant)


# Drift guard: the descriptor table must mirror the frozen Literal exactly.
#
# This is a plain ``if``/``raise`` -- NOT a bare ``assert`` statement (R-237).
# ``assert`` is compiled to a no-op under ``python -O`` / ``PYTHONOPTIMIZE=1``,
# which would silently disable the ONE check whose whole purpose is catching
# catalog/contract disagreement. An explicit ``raise`` always fires, regardless
# of interpreter optimization flags. Factored into a function so the failure
# branch is independently unit-testable (the bare-assert form could only ever
# be exercised by actually corrupting the frozen catalog at import time).
def _assert_registry_matches_literal(
    descriptors: dict[str, TopologyDescriptor], known: tuple[str, ...]
) -> None:
    """Raise ``RuntimeError`` if ``descriptors`` keys don't match ``known``
    exactly, in order. Survives ``python -O`` (unlike a bare ``assert``)."""
    if tuple(descriptors) != known:
        raise RuntimeError(
            "topology registry drifted from the frozen TopologyVariant Literal: "
            f"{tuple(descriptors)} != {known}"
        )


_assert_registry_matches_literal(_DESCRIPTORS, KNOWN_VARIANTS)
