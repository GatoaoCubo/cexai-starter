"""CEXAI orchestration exception hierarchy (topology + planning + streaming).

Rooted at the foundation's ``CexaiError`` so a caller can still catch the whole
package with one ``except CexaiError``. ``OrchestrationError`` is the v0.3
subtree root; the leaves below map to the specific failure modes the v0.3 specs
name, with the spec-named signatures encoded as structured attributes so callers
and contract tests branch on fields (``.cycle_path``, ``.expected_seq``, ...)
rather than parsing messages -- mirroring ``ProviderConfigError`` in the
foundation.

W1/W2/W3 MAY add more leaves under ``OrchestrationError`` in their own lanes
(e.g. a ``PoolExhaustedError`` for worker overflow -- 03 US1 edge case); the
names defined here are FROZEN for v0.3.

Spec provenance:
  * CyclicTopologyError -> 03_swarms US1 acceptance #3 -- CyclicTopologyError(cycle_path).
  * EmptyTopologyError  -> 03_swarms US1 edge case -- zero-node topology refused.
  * UnknownVariantError -> 03_swarms FR-006 -- UnknownVariantError(variant, known_variants[]).
  * QuorumFailureError  -> 03_swarms US2 edge case -- MoA worker quorum not met.
  * MoaStructuralError  -> 03_swarms US2 / FR-005 -- MoA structural violation (R-236).
  * PlanInvalidError    -> 02_ruflo US P2 acceptance #2 -- PlanInvalidError(step_id, violated_precondition).
  * CyclicGoalError     -> 02_ruflo US P2 edge case -- CyclicGoalError(cycle).
  * StreamProtocolError -> 02_ruflo US P3 edge case -- StreamProtocolError(expected_seq, received_seq).
  * StreamAbortedError  -> 02_ruflo US P3 acceptance #2 -- StreamAbortedError(upstream, last_seq_id).

absorbs: 03_swarms/topology + 02_ruflo/goap+stream + 04_claude-flow/sparc
"""

from __future__ import annotations

from cexai.foundation._shared.errors import CexaiError

__all__ = [
    "OrchestrationError",
    "CyclicTopologyError",
    "EmptyTopologyError",
    "UnknownVariantError",
    "QuorumFailureError",
    "MoaStructuralError",
    "PlanInvalidError",
    "CyclicGoalError",
    "StreamProtocolError",
    "StreamAbortedError",
]


class OrchestrationError(CexaiError):
    """Root of the orchestration subtree -- a topology, planning, or streaming
    failure. Subclasses ``CexaiError`` so a single ``except CexaiError`` covers it."""


# --------------------------------------------------------------------------- #
# Topology (cexai-specs/03_swarms)                                             #
# --------------------------------------------------------------------------- #
class CyclicTopologyError(OrchestrationError):
    """A topology's ``graph`` variant contains a cycle (03 US1 acceptance #3).
    ``cycle_path`` is the offending node sequence, surfaced for debugging."""

    def __init__(self, cycle_path: tuple[str, ...]) -> None:
        self.cycle_path = tuple(cycle_path)
        super().__init__(f"topology contains a cycle: {' -> '.join(self.cycle_path)}")


class EmptyTopologyError(OrchestrationError):
    """A topology declares zero nodes (03 US1 edge case). The validator refuses
    and suggests a minimum of one node; emptiness is the whole error, so no
    payload is carried."""


class UnknownVariantError(OrchestrationError):
    """A topology names a variant outside the canonical catalog (03 FR-006).
    Carries the bad ``variant`` and the ``known_variants`` for a helpful message."""

    def __init__(self, variant: str, known_variants: tuple[str, ...]) -> None:
        self.variant = variant
        self.known_variants = tuple(known_variants)
        super().__init__(
            f"unknown topology variant {variant!r}; "
            f"known: {', '.join(self.known_variants)}"
        )


class QuorumFailureError(OrchestrationError):
    """An MoA topology did not reach worker quorum (03 US2 edge case). Quorum
    defaults to ``M = ceil(N/2) + 1``; ``required`` is M and ``succeeded`` is the
    number of workers that produced output before the synthesizer would run."""

    def __init__(self, required: int, succeeded: int) -> None:
        self.required = required
        self.succeeded = succeeded
        super().__init__(
            f"MoA quorum not met: {succeeded} of {required} required workers succeeded"
        )


class MoaStructuralError(OrchestrationError):
    """An MoA topology violates FR-005's structural requirements -- node role,
    worker count, provider diversity, or exactly-one-synthesizer (03 US2 / FR-005,
    R-236). Raised by ``_partition`` BEFORE any provider call. ``node_id`` is the
    offending node's id when the violation is node-local (bad ``role``), or ``""``
    when the violation is topology-wide (wrong worker/synthesizer count, duplicate
    providers). ``reason`` is the human-readable violation detail.

    Previously these 4 sites raised a bare ``ValueError`` -- NOT a ``CexaiError``
    subclass -- so they were invisible to the package's documented "catch the
    whole package with one ``except CexaiError``" contract."""

    def __init__(self, node_id: str, reason: str) -> None:
        self.node_id = node_id
        self.reason = reason
        message = f"MoA node {node_id!r}: {reason}" if node_id else f"MoA structural violation: {reason}"
        super().__init__(message)


# --------------------------------------------------------------------------- #
# Planning / GOAP (cexai-specs/02_ruflo US P2)                                 #
# --------------------------------------------------------------------------- #
class PlanInvalidError(OrchestrationError):
    """A plan step's preconditions are not satisfied by prior steps' effects
    (02 US P2 acceptance #2). Carries the offending ``step_id`` and the
    ``violated_precondition``."""

    def __init__(self, step_id: str, violated_precondition: str) -> None:
        self.step_id = step_id
        self.violated_precondition = violated_precondition
        super().__init__(
            f"plan step {step_id!r} violates precondition: {violated_precondition}"
        )


class CyclicGoalError(OrchestrationError):
    """A goal's operator dependencies form a cycle (02 US P2 edge case). ``cycle``
    is the offending step sequence; the planner refuses rather than loop."""

    def __init__(self, cycle: tuple[str, ...]) -> None:
        self.cycle = tuple(cycle)
        super().__init__(f"goal has cyclic dependencies: {' -> '.join(self.cycle)}")


# --------------------------------------------------------------------------- #
# Streaming / stream-json (cexai-specs/02_ruflo US P3)                         #
# --------------------------------------------------------------------------- #
class StreamProtocolError(OrchestrationError):
    """A stream chunk arrived out of monotonic order (02 US P3 edge case). The
    stream is NOT recoverable. Carries the ``expected_seq`` and ``received_seq``."""

    def __init__(self, expected_seq: int, received_seq: int) -> None:
        self.expected_seq = expected_seq
        self.received_seq = received_seq
        super().__init__(
            f"stream protocol violation: expected seq {expected_seq}, "
            f"received {received_seq}"
        )


class StreamAbortedError(OrchestrationError):
    """An upstream stream ended without a ``completion`` marker (02 US P3
    acceptance #2). The downstream aborts; ``upstream`` is the source agent and
    ``last_seq_id`` the final sequence id seen before EOF."""

    def __init__(self, upstream: str, last_seq_id: int) -> None:
        self.upstream = upstream
        self.last_seq_id = last_seq_id
        super().__init__(
            f"stream from {upstream!r} aborted after seq {last_seq_id} "
            f"(no completion marker)"
        )
