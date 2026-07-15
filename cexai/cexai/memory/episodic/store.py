"""Episodic store -- capture / compress / inject / search / forget (07 FR-001..016).

``EpisodicMemory`` implements the FROZEN ``EpisodicStore`` protocol
(``cexai.memory._shared.types``):

  * ``capture``  -- append a hash-chained ``SessionEvent`` to the active session's
                    ``raw.jsonl`` (FR-001/FR-011). No-op under ``CEXAI_NO_CAPTURE=1``
                    (FR-005). Tamper-evident: ``verify_integrity`` recomputes the
                    chain (SC-006).
  * ``compress`` -- distill a captured session into BOTH a structured digest and a
                    narrative (FR-012) via the injected ``Compressor`` (lazy Ollama
                    default), and stamp the topic embedding (US P1 "topic").
  * ``inject``   -- top-by-cosine compressed sessions within a token budget
                    (FR-003/FR-004); empty when nothing clears the floor (FR-014).
  * ``search``   -- query compressed sessions (FR-008); degrades to a substring
                    scan when the embedder is unavailable (``[FALLBACK]``).
  * ``forget``   -- delete a session and every derivative (FR-015).

STORAGE (constitution CM1; FR-001/FR-010). Local-first, one directory per session
under ``root`` (default ``.cexai/memory``, a gitignored runtime dir -- session
data is never committed). Tests pass ``root=tmp_path``:

    <root>/<session_id>/raw.jsonl        append-only hash-chained event log
    <root>/<session_id>/compressed.json  the compression derivative (FR-012)

The vector subsystem (W1) supplies the ``Embedder``; relevance ranking + budgeting
live in ``inject``. No live LLM or embedding model is required to import or test
this module (Article XIV): the offline path is ``DeterministicCompressor`` +
``FakeEmbedder``.

absorbs: 07_claude-mem/episodic
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path

from cexai.memory._shared.errors import EmbeddingUnavailableError
from cexai.memory._shared.errors import MemoryError as _MemoryError
from cexai.memory._shared.types import CompressedSession, Embedder, SessionEvent
from cexai.memory.episodic.compress import (
    CompressionUnavailableError,
    Compressor,
    DeterministicCompressor,
    OllamaCompressor,
    topic_text,
)
from cexai.memory.episodic.inject import (
    DEFAULT_SIMILARITY_FLOOR,
    inject_sessions,
    rank_by_similarity,
)

__all__ = [
    "EpisodicMemory",
    "chain_event",
    "compute_event_hash",
    "SessionNotFoundError",
    "DEFAULT_MEMORY_ROOT",
    "DEFAULT_CONTEXT_WINDOW",
]

DEFAULT_MEMORY_ROOT = ".cexai/memory"
# Injection budget defaults to 10% of the context window (constitution CM4 / FR-004).
DEFAULT_CONTEXT_WINDOW = 200_000
DEFAULT_BUDGET_FRACTION = 0.10
# In-process compressed-session cache bound (R-239): a long-lived server that
# compresses/scans many sessions must not grow this dict without limit. Eviction
# only drops the CACHE entry -- the on-disk ``compressed.json`` derivative is
# untouched, so a later access reloads it via ``_scan_disk`` (correctness is
# preserved; only repeat-access latency changes).
DEFAULT_MAX_CACHED_SESSIONS = 500

_NO_CAPTURE_ENV = "CEXAI_NO_CAPTURE"
_RAW_NAME = "raw.jsonl"
_COMPRESSED_NAME = "compressed.json"


class SessionNotFoundError(_MemoryError):
    """``compress`` / ``verify_integrity`` was asked for a session with no raw log."""


def compute_event_hash(
    seq: int,
    timestamp: str,
    type_: str,
    payload: Mapping[str, object],
    prev_hash: str | None,
) -> str:
    """SHA-256 over the canonical (sorted-key) JSON of an event's fields, including
    ``prev_hash`` -- the link that makes the log a tamper-evident chain (FR-011)."""
    canonical = json.dumps(
        {
            "seq": seq,
            "timestamp": timestamp,
            "type": type_,
            "payload": dict(payload),
            "prev_hash": prev_hash,
        },
        sort_keys=True,
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def chain_event(
    prev: SessionEvent | None,
    seq: int,
    type_: str,
    payload: Mapping[str, object],
    timestamp: str,
) -> SessionEvent:
    """Build a ``SessionEvent`` linked to ``prev`` (None for the genesis event).
    Computes ``prev_hash`` + ``hash`` so callers can produce a valid chain to
    ``capture`` without hand-rolling the hashing (FR-011)."""
    prev_hash = prev.hash if prev is not None else None
    digest = compute_event_hash(seq, timestamp, type_, payload, prev_hash)
    return SessionEvent(
        seq=seq,
        timestamp=timestamp,
        type=type_,
        payload=dict(payload),
        prev_hash=prev_hash,
        hash=digest,
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class EpisodicMemory:
    """Local episodic memory store (satisfies ``EpisodicStore``).

    ``session_id`` selects the active session that ``capture`` appends to (one
    ``EpisodicMemory`` per live session in production); it is generated from the
    clock when omitted. ``embedder`` (W1 ``Embedder``) embeds topic text + search
    queries; ``compressor`` distills sessions. Both default to lazily-built
    production clients (Ollama) and are injected with offline fakes in tests.
    ``similarity_floor`` is the topic cosine threshold (US P1, default 0.7)."""

    def __init__(
        self,
        root: str | Path | None = None,
        session_id: str | None = None,
        *,
        embedder: Embedder | None = None,
        compressor: Compressor | None = None,
        similarity_floor: float = DEFAULT_SIMILARITY_FLOOR,
        context_window: int = DEFAULT_CONTEXT_WINDOW,
        budget_fraction: float = DEFAULT_BUDGET_FRACTION,
        max_cached_sessions: int = DEFAULT_MAX_CACHED_SESSIONS,
    ) -> None:
        self._root = Path(root) if root is not None else Path(DEFAULT_MEMORY_ROOT)
        self._session_id = session_id or self._generate_session_id()
        self._embedder = embedder
        self._compressor = compressor
        self._similarity_floor = float(similarity_floor)
        self._context_window = int(context_window)
        self._budget_fraction = float(budget_fraction)
        self._max_cached_sessions = max(1, int(max_cached_sessions))
        # In-process cache of compressed sessions (bounded, R-239); ``_scan_disk``
        # hydrates it from any sibling sessions persisted by other store instances
        # under ``root``. An ``OrderedDict`` so ``_cache_put`` can evict the
        # least-recently-inserted entry once the cache is over capacity.
        self._compressed: OrderedDict[str, CompressedSession] = OrderedDict()

    # -- identity / paths ---------------------------------------------------- #

    @property
    def session_id(self) -> str:
        """The active capture session id."""
        return self._session_id

    @property
    def default_budget_tokens(self) -> int:
        """The injection budget when a caller does not specify one (CM4 / FR-004)."""
        return max(1, int(self._context_window * self._budget_fraction))

    @staticmethod
    def _generate_session_id() -> str:
        return "sess-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")

    def _session_dir(self, session_id: str) -> Path:
        return self._root / session_id

    def _raw_path(self, session_id: str) -> Path:
        return self._session_dir(session_id) / _RAW_NAME

    def _compressed_path(self, session_id: str) -> Path:
        return self._session_dir(session_id) / _COMPRESSED_NAME

    # -- EpisodicStore: capture --------------------------------------------- #

    def capture(self, event: SessionEvent) -> None:
        """Append ``event`` to the active session's hash-chained ``raw.jsonl``.
        No-op when ``CEXAI_NO_CAPTURE=1`` (FR-005: opt-out, capture nothing)."""
        if os.environ.get(_NO_CAPTURE_ENV) == "1":
            return
        raw = self._raw_path(self._session_id)
        raw.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "seq": event.seq,
            "timestamp": event.timestamp,
            "type": event.type,
            "payload": dict(event.payload),
            "prev_hash": event.prev_hash,
            "hash": event.hash,
        }
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")

    def verify_integrity(self, session_id: str) -> bool:
        """Recompute the hash chain of a captured session and report whether it is
        intact (SC-006: 100% detection of tamper). False when any event's seq is
        out of order, a ``prev_hash`` link is broken, a hash does not recompute, or
        the session has no log."""
        events = self._read_events(session_id)
        if not events:
            return False
        prev_hash: str | None = None
        for index, event in enumerate(events):
            if event.seq != index:
                return False
            if event.prev_hash != prev_hash:
                return False
            if compute_event_hash(
                event.seq, event.timestamp, event.type, event.payload, event.prev_hash
            ) != event.hash:
                return False
            prev_hash = event.hash
        return True

    # -- EpisodicStore: compress -------------------------------------------- #

    def compress(self, session_id: str) -> CompressedSession:
        """Distill a captured session into a ``CompressedSession`` (structured +
        narrative, FR-012) and stamp its topic embedding (US P1). Persists the
        derivative and caches it for injection. Raises ``SessionNotFoundError`` if
        the session was never captured.

        If the configured compressor is unavailable (``CompressionUnavailableError``
        -- e.g. no Ollama reachable), this degrades to the dependency-free
        ``DeterministicCompressor`` (R-223) rather than raising, matching the
        fallback that ``CompressionUnavailableError`` documents."""
        events = self._read_events(session_id)
        if not events:
            raise SessionNotFoundError(
                f"no captured session {session_id!r} under {self._root}"
            )
        try:
            structured, narrative = self._get_compressor().compress(session_id, events)
        except CompressionUnavailableError:
            structured, narrative = DeterministicCompressor().compress(session_id, events)
        text = topic_text(events)
        embedding = tuple(self._get_embedder().embed(text)) if text else None
        compressed = CompressedSession(
            session_id=session_id,
            structured=dict(structured),
            narrative=narrative,
            topic_embedding=embedding,
            created_at=_now_iso(),
        )
        self._cache_put(session_id, compressed)
        self._write_compressed(compressed)
        return compressed

    # -- EpisodicStore: inject / search ------------------------------------- #

    def inject(
        self, query_embedding: tuple[float, ...], budget_tokens: int
    ) -> tuple[CompressedSession, ...]:
        """Return the most relevant compressed sessions fitting ``budget_tokens``
        (FR-003/FR-004). Empty when no session clears the similarity floor
        (FR-014). Hydrates from disk so sessions compressed by other instances
        under the same ``root`` are visible."""
        sessions = self._scan_disk()
        return inject_sessions(
            query_embedding,
            sessions,
            budget_tokens=budget_tokens,
            floor=self._similarity_floor,
        )

    def search(self, text: str) -> tuple[CompressedSession, ...]:
        """Return compressed sessions matching ``text`` (FR-008, ``cexai mem
        search``), best-first. When the embedder is unavailable it degrades to a
        substring scan over narratives (the ``[FALLBACK]`` path, mirroring the
        vector subsystem's TF-IDF fallback) so search stays usable offline."""
        sessions = self._scan_disk()
        if not sessions:
            return ()
        try:
            query = self._get_embedder().embed(text)
        except EmbeddingUnavailableError:
            needle = text.lower()
            return tuple(cs for cs in sessions if needle in cs.narrative.lower())
        ranked = rank_by_similarity(query, sessions, floor=0.0)
        return tuple(cs for score, cs in ranked if score > 0.0)

    # -- EpisodicStore: forget ---------------------------------------------- #

    def forget(self, session_id: str) -> None:
        """Delete a session and every derivative -- the raw log, the compressed
        JSON, and the cached entry (FR-015). Idempotent: forgetting an unknown
        session is a clean no-op."""
        self._compressed.pop(session_id, None)
        session_dir = self._session_dir(session_id)
        if session_dir.exists():
            shutil.rmtree(session_dir)

    # -- internals ----------------------------------------------------------- #

    def _read_events(self, session_id: str) -> tuple[SessionEvent, ...]:
        raw = self._raw_path(session_id)
        if not raw.exists():
            return ()
        events: list[SessionEvent] = []
        for line in raw.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            events.append(
                SessionEvent(
                    seq=row["seq"],
                    timestamp=row["timestamp"],
                    type=row["type"],
                    payload=row.get("payload") or {},
                    prev_hash=row.get("prev_hash"),
                    hash=row["hash"],
                )
            )
        return tuple(events)

    def _write_compressed(self, compressed: CompressedSession) -> None:
        path = self._compressed_path(compressed.session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "session_id": compressed.session_id,
            "structured": dict(compressed.structured),
            "narrative": compressed.narrative,
            "topic_embedding": (
                list(compressed.topic_embedding)
                if compressed.topic_embedding is not None
                else None
            ),
            "created_at": compressed.created_at,
        }
        path.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")

    def _read_compressed(self, path: Path) -> CompressedSession:
        data = json.loads(path.read_text(encoding="utf-8"))
        embedding = data.get("topic_embedding")
        return CompressedSession(
            session_id=data["session_id"],
            structured=dict(data.get("structured") or {}),
            narrative=data.get("narrative", ""),
            topic_embedding=tuple(embedding) if embedding is not None else None,
            created_at=data.get("created_at", ""),
        )

    def _cache_put(self, session_id: str, compressed: CompressedSession) -> None:
        """Insert/refresh ``session_id`` in the bounded compressed-session cache
        (R-239), evicting the least-recently-inserted entry once over
        ``max_cached_sessions``. Eviction is cache-only: the on-disk derivative
        is unaffected, so ``_scan_disk`` reloads an evicted-but-still-persisted
        session on its next access -- inject/search correctness is preserved,
        only a bounded amount of memory is held at once."""
        self._compressed[session_id] = compressed
        self._compressed.move_to_end(session_id)
        while len(self._compressed) > self._max_cached_sessions:
            self._compressed.popitem(last=False)

    def _scan_disk(self) -> tuple[CompressedSession, ...]:
        """Return EVERY compressed session persisted under ``root`` (so a fresh
        store, or one that lost cache entries to eviction, still sees sessions
        compressed by other instances -- or by itself, earlier).

        Reads through the bounded cache (``_cache_put``, R-239): an already
        cached session is reused (and marked recently-used); a cache miss is
        read from disk and offered to the cache. The RETURNED tuple always
        contains every session found on disk regardless of the cache bound --
        ranking correctness for ``inject``/``search`` (FR-003/FR-004/FR-008)
        must see the full corpus. Only ``self._compressed``'s resident size is
        bounded between calls; a session that this same scan evicts to stay
        under ``max_cached_sessions`` is still included in the result (it was
        already read before being evicted) and will simply be re-read from
        disk on a later scan if it is needed again."""
        results: list[CompressedSession] = []
        if not self._root.exists():
            return tuple(self._compressed.values())
        for child in sorted(self._root.iterdir()):
            if not child.is_dir():
                continue
            cached = self._compressed.get(child.name)
            if cached is not None:
                self._compressed.move_to_end(child.name)
                results.append(cached)
                continue
            compressed_path = child / _COMPRESSED_NAME
            if compressed_path.exists():
                compressed = self._read_compressed(compressed_path)
                self._cache_put(child.name, compressed)
                results.append(compressed)
        return tuple(results)

    def _get_embedder(self) -> Embedder:
        if self._embedder is None:
            from cexai.memory.vector import OllamaEmbedder  # lazy: production default

            self._embedder = OllamaEmbedder()
        return self._embedder

    def _get_compressor(self) -> Compressor:
        if self._compressor is None:
            self._compressor = OllamaCompressor()  # lazy: production default (FR-002)
        return self._compressor
