"""Frozen type contracts for the CEXAI memory substrate -- the v0.2 linchpin.

These names and shapes are FROZEN for the whole v0.2 (memory) mission. Every
v0.2 cell -- W1 (vector + graph) and W2 (episodic) -- imports these symbols and
MUST NOT change their names or fields. If a shape must evolve, that is a
versioned, peer-reviewed change, not an in-flight edit. This mirrors the v0.1
discipline in ``cexai.foundation._shared.types``.

Design constraints (Article VIII -- Anti-Abstraction):
  * stdlib typing only -- NO pydantic in this hot path.
  * every value type is an immutable ``@dataclass(frozen=True, slots=True)``.
  * collection fields are tuples / read-only mappings so instances are safely
    shareable across threads and backends without defensive copying.

Three subsystems share one vocabulary here:
  * vector   (semantic recall)   -- MemoryRecord, Embedding, VectorHit,
                                     MemoryQuery; VectorStore + Embedder.
  * graph    (structural)        -- GraphNode, GraphEdge, GraphHit; GraphStore.
  * episodic (session memory)    -- SessionEvent, CompressedSession;
                                     EpisodicStore.

TAXONOMY NOTE (founder rule): these Python types are CODE. The CEX *artifact
kinds* (``vector_store``, ``knowledge_graph``, ``episodic_memory``,
``session_state``, ``memory_summary``, ``knowledge_index``) are reused as-is --
no kind is registered by this wave.

Spec provenance: cexai-specs/02_ruflo/spec.md (US P1, FR-001..003, SC-001/002),
cexai-specs/06_graphify/spec.md (US P1, FR-001..005), and
cexai-specs/07_claude-mem/spec.md (US P1, FR-001..003, FR-011 hash chain).

absorbs: 02_ruflo/vector + 06_graphify/graph + 07_claude-mem/episodic
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Protocol, runtime_checkable

__all__ = [
    "MemoryRecord",
    "Embedding",
    "VectorHit",
    "MemoryQuery",
    "GraphNode",
    "GraphEdge",
    "GraphHit",
    "SessionEvent",
    "CompressedSession",
    "VectorStore",
    "Embedder",
    "GraphStore",
    "EpisodicStore",
]

# Immutable empty mapping -- safe shared default for the optional ``metadata`` /
# ``filters`` / ``attrs`` fields. A frozen dataclass cannot take a dict default
# (mutable); MappingProxyType is read-only, so one shared instance is correct.
_EMPTY_META: Mapping[str, Any] = MappingProxyType({})


# --------------------------------------------------------------------------- #
# Vector subsystem (cexai-specs/02_ruflo) -- semantic recall.                   #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """One indexable unit of memory -- a CEX artifact (or a fragment of one).
    ``kind`` is the CEX artifact kind (e.g. ``knowledge_card``); ``source_path``
    is the on-disk origin, ``None`` for in-memory or synthetic records.
    ``timestamp`` is ISO-8601. ``metadata`` carries arbitrary index-time facets
    (frontmatter, tags) and is kept read-only."""

    id: str
    content: str
    kind: str
    source_path: str | None
    timestamp: str
    metadata: Mapping[str, Any] = _EMPTY_META


@dataclass(frozen=True, slots=True)
class Embedding:
    """A dense vector for a single ``MemoryRecord``. ``vector`` is a tuple so the
    instance stays immutable and hashable; ``dim`` is its length (carried
    explicitly so a store can validate without materializing the tuple).
    ``model_id`` identifies the embedder (delete+reinsert on model change --
    02 acceptance #3). ``created_at`` is ISO-8601."""

    record_id: str
    model_id: str
    vector: tuple[float, ...]
    dim: int
    created_at: str


@dataclass(frozen=True, slots=True)
class VectorHit:
    """One result of a vector ``query``. ``score`` is the similarity under the
    query metric (higher = closer for cosine); ``rank`` is the 0-based position
    in the returned ordering (SC-002 recall@K is computed over these)."""

    record_id: str
    score: float
    rank: int


@dataclass(frozen=True, slots=True)
class MemoryQuery:
    """A semantic query against a ``VectorStore``. ``text`` is embedded by the
    caller's ``Embedder`` and passed alongside this query. ``top_k`` bounds the
    result set; ``filters`` restricts candidates by ``MemoryRecord.metadata``
    facets (read-only); ``metric`` selects the distance function."""

    text: str
    top_k: int = 10
    filters: Mapping[str, Any] = _EMPTY_META
    metric: str = "cosine"


# --------------------------------------------------------------------------- #
# Graph subsystem (cexai-specs/06_graphify) -- structural query.               #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class GraphNode:
    """A typed node in the knowledge graph (an artifact, symbol, or file).
    ``type`` is the node label (e.g. ``function``, ``spec``); ``attrs`` holds
    typed properties (read-only). ``source`` is the file origin, ``None`` if
    synthetic. ``parse_error`` is set when the source could not be parsed
    (06 edge case: node still created, flagged)."""

    id: str
    type: str
    attrs: Mapping[str, Any]
    source: str | None = None
    parse_error: bool = False


@dataclass(frozen=True, slots=True)
class GraphEdge:
    """A typed directed edge ``src -> dst`` (e.g. ``imports``, ``references``).
    ``attrs`` carries edge properties such as ``file:line`` provenance and is
    kept read-only."""

    src: str
    dst: str
    type: str
    attrs: Mapping[str, Any] = _EMPTY_META


@dataclass(frozen=True, slots=True)
class GraphHit:
    """One result of a graph ``query``. ``score`` ranks relevance; ``hops`` is
    the neighborhood distance from the query seed (0 = direct match), bounding
    the N-hop expansion of 06 US P2."""

    node_id: str
    score: float
    hops: int = 0


# --------------------------------------------------------------------------- #
# Episodic subsystem (cexai-specs/07_claude-mem) -- session memory.            #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class SessionEvent:
    """One append-only event in a session log. Hash-chained for tamper
    detection (07 FR-011): ``hash`` covers this event plus ``prev_hash``;
    ``prev_hash`` is ``None`` only for the genesis event. ``seq`` is monotonic
    within a session; ``timestamp`` is ISO-8601; ``payload`` is read-only."""

    seq: int
    timestamp: str
    type: str
    payload: Mapping[str, Any]
    prev_hash: str | None
    hash: str


@dataclass(frozen=True, slots=True)
class CompressedSession:
    """The compression output for one session (07 FR-012 -- BOTH stored).
    ``structured`` is the typed digest (decisions, files_touched, errors,
    kc_candidates), read-only; ``narrative`` is the free-text summary;
    ``topic_embedding`` is the session topic vector (07 US P1 definition of
    "topic"), ``None`` until computed. ``created_at`` is ISO-8601."""

    session_id: str
    structured: Mapping[str, Any]
    narrative: str
    topic_embedding: tuple[float, ...] | None
    created_at: str


# --------------------------------------------------------------------------- #
# Protocols -- the seams W1/W2 implement. Structural (no base class required);  #
# runtime_checkable allows isinstance smoke checks. A deterministic FAKE        #
# Embedder lets the whole substrate be tested offline (Article XIV).            #
# --------------------------------------------------------------------------- #
@runtime_checkable
class Embedder(Protocol):
    """Turns text into a dense vector. ``name`` identifies the model so an
    ``Embedding`` can record its ``model_id``. The single seam tests inject a
    deterministic fake through, so vector behaviour is verifiable without a live
    embedding model (02 edge case: model-unavailable falls back to TF-IDF)."""

    name: str

    def embed(self, text: str) -> tuple[float, ...]:
        """Return the embedding of ``text`` as an immutable vector."""
        ...


@runtime_checkable
class VectorStore(Protocol):
    """Persistent vector index over ``MemoryRecord``s (02 FR-001..003). HNSW has
    no in-place update, so re-indexing is delete+insert (02 acceptance #3).
    ``query`` takes the pre-computed query ``embedding`` alongside the
    ``MemoryQuery`` so the store never depends on a specific ``Embedder``."""

    def insert(self, record: MemoryRecord, embedding: Embedding) -> None:
        """Index ``record`` under ``embedding``. Re-indexing = delete then insert."""
        ...

    def query(self, q: MemoryQuery, embedding: tuple[float, ...]) -> tuple[VectorHit, ...]:
        """Return up to ``q.top_k`` hits for the query ``embedding``, best first."""
        ...

    def delete(self, record_id: str) -> None:
        """Remove the record (and its embedding) from the index."""
        ...

    def persist(self) -> None:
        """Flush the index to durable storage (02 FR-003: survive restarts)."""
        ...


@runtime_checkable
class GraphStore(Protocol):
    """Typed knowledge graph over a source tree (06 FR-001..005). ``query``
    accepts a Cypher string or a pattern; ``is_stale`` reports whether the
    source changed after indexing (06 FR-005 -- results flagged ``[STALE]``)."""

    def add_node(self, n: GraphNode) -> None:
        """Add (or replace) a typed node."""
        ...

    def add_edge(self, e: GraphEdge) -> None:
        """Add a typed directed edge between existing nodes."""
        ...

    def query(self, cypher_or_pattern: str) -> tuple[GraphHit, ...]:
        """Run a Cypher query or pattern match; return ranked hits."""
        ...

    def is_stale(self) -> bool:
        """Return True if the indexed source has changed since the last build."""
        ...


@runtime_checkable
class EpisodicStore(Protocol):
    """Append-capture + compress + inject session memory (07 FR-001..003).
    ``capture`` appends a hash-chained event; ``compress`` distills a session;
    ``inject`` returns the most relevant compressed sessions within a token
    budget (07 FR-003/FR-014 -- empty when nothing clears the similarity floor);
    ``search`` backs ``cexai mem search``; ``forget`` is retroactive deletion
    of a session and its derivatives (07 FR-015)."""

    def capture(self, event: SessionEvent) -> None:
        """Append ``event`` to the active session's hash-chained log."""
        ...

    def compress(self, session_id: str) -> CompressedSession:
        """Distill a captured session into structured + narrative outputs."""
        ...

    def inject(
        self, query_embedding: tuple[float, ...], budget_tokens: int
    ) -> tuple[CompressedSession, ...]:
        """Return relevant compressed sessions fitting ``budget_tokens``."""
        ...

    def search(self, text: str) -> tuple[CompressedSession, ...]:
        """Return compressed sessions matching ``text`` (cexai mem search)."""
        ...

    def forget(self, session_id: str) -> None:
        """Delete a session and every compressed derivative of it."""
        ...
