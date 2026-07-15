"""Frozen type contracts for the CEXAI orchestration layer -- the v0.3 linchpin.

These names and shapes are FROZEN for the whole v0.3 (orchestration) mission.
Every v0.3 cell -- W1 (topology catalog + interpreter, GOAP planner), W2
(stream-json), W3 (SPARC templates) -- imports these symbols and MUST NOT change
their names or fields. If a shape must evolve, that is a versioned, peer-reviewed
change, not an in-flight edit. This mirrors the v0.1 foundation and v0.2 memory
discipline in ``cexai.foundation._shared.types`` / ``cexai.memory._shared.types``.

Design constraints (Article VIII -- Anti-Abstraction):
  * stdlib typing only -- NO pydantic in this hot path.
  * every value type is an immutable ``@dataclass(frozen=True, slots=True)``.
  * collection fields are tuples / read-only mappings so instances are safely
    shareable across threads, nuclei, and providers without defensive copying.

Four coordination subsystems share one vocabulary here:
  * topology  (agent coordination)  -- TopologyVariant, TopologyNode,
                                        TopologyEdge, Topology, CoordinationEvent,
                                        TopologyRun; TopologyInterpreter.
  * planning  (GOAP state-space)     -- PlanOperator, Plan; Planner.
  * streaming (agent-to-agent chain) -- StreamEvent; StreamChannel.
  * sparc     (methodology phases)   -- SparcPhaseId.

TAXONOMY NOTE (founder rule, taxonomy-neutral wave): these are Python CODE types.
Whether ``topology`` / ``sparc_phase`` become NEW CEX kinds or EXTENSIONS of
existing kinds (``collaboration_pattern``, ``pipeline_template``,
``planning_strategy``, ``event_schema``) is DEFERRED to W1 (it needs an ADR).
This module registers ZERO kinds and does NOT touch ``.cex/kinds_meta.json``.

Spec provenance: cexai-specs/03_swarms/spec.md (US P1/P2/P3, FR-001..008,
SC-001..005), cexai-specs/02_ruflo/spec.md (US P2 GOAP + US P3 stream-json,
FR-004..007), cexai-specs/04_claude-flow/spec.md (US P1 SPARC, FR-001/005).

absorbs: 03_swarms/topology + 02_ruflo/goap+stream + 04_claude-flow/sparc
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal, Protocol, runtime_checkable

__all__ = [
    "TopologyVariant",
    "TopologyNode",
    "TopologyEdge",
    "Topology",
    "CoordinationEvent",
    "TopologyRun",
    "PlanOperator",
    "Plan",
    "StreamEvent",
    "SparcPhaseId",
    "TopologyInterpreter",
    "Planner",
    "StreamChannel",
]

# Immutable empty mapping -- safe shared default for the optional ``config`` /
# ``audit_config`` fields. A frozen dataclass cannot take a dict default
# (mutable); MappingProxyType is read-only, so one shared instance is correct.
_EMPTY_CONFIG: Mapping[str, Any] = MappingProxyType({})


# --------------------------------------------------------------------------- #
# Topology subsystem (cexai-specs/03_swarms) -- agent coordination catalog.     #
# --------------------------------------------------------------------------- #
# The six absorbed coordination variants (03 FR-001 / SC-001). ``Topology.variant``
# stays ``str`` so a ruflo extension variant can ride along without breaking the
# contract; this Literal is the canonical, validator-enforced set.
TopologyVariant = Literal[
    "sequential",
    "concurrent",
    "hierarchical",
    "graph",
    "group_chat",
    "mixture_of_agents",
]


@dataclass(frozen=True, slots=True)
class TopologyNode:
    """One agent assignment in a topology. ``agent`` references a nucleus (e.g.
    ``N03``) or a provider config -- MoA workers MUST use DISTINCT providers
    (03 US2 / FR-005); ``config`` carries node-local knobs and is read-only."""

    id: str
    agent: str
    config: Mapping[str, Any] = _EMPTY_CONFIG


@dataclass(frozen=True, slots=True)
class TopologyEdge:
    """A directed coordination edge ``src -> dst``. ``event_type`` labels the
    coordination semantics (``data`` for an output handoff, ``control`` for
    backpressure / signalling) and defaults to ``data``."""

    src: str
    dst: str
    event_type: str = "data"


@dataclass(frozen=True, slots=True)
class Topology:
    """A typed coordination topology (03 FR-001/002). ``variant`` is one of
    ``TopologyVariant`` (kept ``str`` for extension headroom); ``nodes`` are the
    agent assignments and ``edges`` the coordination wiring. ``audit_config``
    references the vertical-05 OTel config (03 FR-004) and is read-only."""

    id: str
    variant: str
    nodes: tuple[TopologyNode, ...]
    edges: tuple[TopologyEdge, ...]
    audit_config: Mapping[str, Any] = _EMPTY_CONFIG


@dataclass(frozen=True, slots=True)
class CoordinationEvent:
    """One hop in a topology execution -- the audit-trail atom (03 US3 / FR-004).
    ``from_node`` is ``None`` only for an initial event (no predecessor, so the
    SC-004 "zero phantom inputs" check still holds); ``payload_ref`` points at
    the carried payload (not inlined, for trace compactness); ``timestamp`` is
    ISO-8601; ``event_type`` mirrors the triggering edge."""

    event_id: str
    from_node: str | None
    to_node: str
    payload_ref: str
    timestamp: str
    event_type: str


@dataclass(frozen=True, slots=True)
class TopologyRun:
    """One execution instance of a ``Topology`` (03 Key Entities). Tracked as an
    OTel span at runtime; this is its typed projection. ``completed_at`` is
    ``None`` while running; ``status`` is the lifecycle state (e.g. ``running``,
    ``completed``, ``failed``); ``events`` is the ordered coordination trail."""

    run_id: str
    topology_id: str
    started_at: str
    completed_at: str | None
    status: str
    events: tuple[CoordinationEvent, ...] = ()


# --------------------------------------------------------------------------- #
# Planning subsystem (cexai-specs/02_ruflo US P2) -- GOAP state-space search.   #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class PlanOperator:
    """One GOAP operator (02 US P2 Key Entities). ``preconditions`` must hold
    before the operator applies; ``effects`` are the world-state facts it
    establishes; ``cost`` feeds A* optimization (02 default = token-only,
    FR-010); ``owner`` is the nucleus that executes it (``None`` if unbound)."""

    name: str
    preconditions: tuple[str, ...]
    effects: tuple[str, ...]
    cost: float
    owner: str | None = None


@dataclass(frozen=True, slots=True)
class Plan:
    """A typed plan produced by a ``Planner`` (02 US P2). ``operators`` is the
    ordered sequence whose chained pre/effects the planner verified;
    ``total_cost`` is their summed cost; ``validation_status`` records the
    verdict (e.g. ``valid``, ``NO_PLAN``, ``[PARTIAL]``); ``alternatives``
    documents lower- or alternative-cost plans (02 acceptance #3), kept ``Any``
    so a W1 ``Plan`` may nest sibling plans without a forward reference."""

    goal: str
    operators: tuple[PlanOperator, ...]
    total_cost: float
    validation_status: str
    alternatives: tuple[Any, ...] = ()


# --------------------------------------------------------------------------- #
# Streaming subsystem (cexai-specs/02_ruflo US P3) -- stream-json a2a chaining.  #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class StreamEvent:
    """One logical chunk of an agent-to-agent stream (02 US P3). Exactly one
    ``StreamEvent`` per newline-terminated JSON line; ``sequence_id`` is
    monotonic (a gap aborts with ``StreamProtocolError``). ``type`` is one of
    ``data`` | ``control`` | ``EOF`` (``control`` carries PAUSE/RESUME
    backpressure); ``completion`` marks the terminal, successful end of stream
    (its absence at EOF triggers ``StreamAbortedError``). ``payload`` is
    read-only."""

    source: str
    target: str
    sequence_id: int
    payload: Mapping[str, Any]
    type: str
    completion: bool = False


# --------------------------------------------------------------------------- #
# SPARC subsystem (cexai-specs/04_claude-flow) -- opt-in methodology phases.     #
# --------------------------------------------------------------------------- #
# The five ordered SPARC phases (04 FR-001). A ``sparc_phase`` artifact carries
# one of these; whether ``sparc_phase`` is a NEW kind or an extension is the W1
# ADR decision (this wave does not register it).
SparcPhaseId = Literal[
    "specification",
    "pseudocode",
    "architecture",
    "refinement",
    "code",
]


# --------------------------------------------------------------------------- #
# Protocols -- the seams W1/W2 implement. Structural (no base class required);  #
# runtime_checkable allows isinstance smoke checks. Each maps to a contract     #
# test signature frozen in tests/orchestration/contract.                        #
# --------------------------------------------------------------------------- #
@runtime_checkable
class TopologyInterpreter(Protocol):
    """The generic executor for any typed ``Topology`` (03 FR-003). W1 ships the
    concrete interpreter behind this seam; the contract test
    ``test_topology_interpreter_runs`` drives it RED->GREEN."""

    def run(self, topology: Topology) -> TopologyRun:
        """Execute ``topology`` and return its completed ``TopologyRun``."""
        ...


@runtime_checkable
class Planner(Protocol):
    """The GOAP planner seam (02 US P2 / FR-004). ``plan`` consumes a plain-English
    goal and returns a typed, precondition-verified ``Plan`` (or a ``Plan`` with
    ``validation_status == 'NO_PLAN'`` for an unsatisfiable goal -- it never
    fabricates steps). W1 ships the concrete planner."""

    def plan(self, goal: str) -> Plan:
        """Decompose ``goal`` into a verified ``Plan``."""
        ...


@runtime_checkable
class StreamChannel(Protocol):
    """The stream-json transport seam (02 US P3 / FR-006). ``send`` emits one
    logical chunk; ``receive`` yields chunks in monotonic ``sequence_id`` order.
    W2 ships the concrete local-stdio channel; networked transport is v2."""

    def send(self, event: StreamEvent) -> None:
        """Emit one ``StreamEvent`` (one newline-terminated JSON line)."""
        ...

    def receive(self) -> Iterator[StreamEvent]:
        """Yield inbound stream events in monotonic sequence order."""
        ...
