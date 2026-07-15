"""CEXAI memory exception hierarchy (vector + graph + episodic subsystems).

Rooted at the foundation's ``CexaiError`` so a caller can still catch the whole
package with one ``except CexaiError``. ``MemoryError`` is the memory subtree
root; the leaves below map to the specific failure modes the v0.2 specs name.

W1/W2 MAY add more leaves under ``MemoryError`` in their own lanes (e.g. a
vector-index corruption error); the names defined here are FROZEN for v0.2.

Spec provenance:
  * EmbeddingUnavailableError -> cexai-specs/02_ruflo/spec.md edge case
    "Embedding model unavailable: fallback to existing TF-IDF retriever".
  * GraphStaleError           -> cexai-specs/06_graphify/spec.md FR-005 / SC
    (stale graph detection; results flagged, re-index suggested).
  * MemoryRetentionError      -> cexai-specs/07_claude-mem/spec.md FR-010
    (disk retention policy) / FR-015 (forget).

absorbs: 02_ruflo/vector + 06_graphify/graph + 07_claude-mem/episodic
"""

from __future__ import annotations

from cexai.foundation._shared.errors import CexaiError

__all__ = [
    "MemoryError",
    "EmbeddingUnavailableError",
    "GraphStaleError",
    "MemoryRetentionError",
]


class MemoryError(CexaiError):
    """Root of the memory subtree -- vector, graph, or episodic failure. Subclasses
    ``CexaiError`` so a single ``except CexaiError`` still covers it."""


class EmbeddingUnavailableError(MemoryError):
    """The configured embedding model could not be reached or loaded.

    Per 02 edge case, callers SHOULD catch this and fall back to the existing
    TF-IDF retriever (emitting a ``[FALLBACK]`` marker). It is therefore a
    recoverable, expected condition -- not a programming error."""


class GraphStaleError(MemoryError):
    """A graph query ran against an index whose source has since changed.

    Per 06 FR-005, results are stale and a re-index is suggested. Raised when a
    caller demands fresh results and the store cannot guarantee them."""


class MemoryRetentionError(MemoryError):
    """A retention or forget operation could not be honored (07 FR-010/FR-015).

    Covers an unsatisfiable retention policy or a ``forget`` that failed to
    remove a session's compressed derivatives."""
