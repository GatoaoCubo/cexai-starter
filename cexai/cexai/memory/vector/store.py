"""HNSW vector store (cexai-specs/02_ruflo US P1, FR-001..003).

Implements the frozen ``VectorStore`` protocol
(``cexai.memory._shared.types.VectorStore``):

  * ``insert``  -- index a record under its embedding. HNSW has no in-place
                   update, so re-indexing the same id is delete+insert (02
                   acceptance #3).
  * ``query``   -- top-K cosine recall, ranked best-first with stable scoring
                   (FR-002, SC-001's stability requirement).
  * ``delete``  -- drop a record + its embedding (FR-002).
  * ``persist`` -- flush to a JSON sidecar that survives a process restart
                   (FR-003).

Backend: the authoritative index is an in-memory dict of exact vectors, scored
with pure-Python cosine -- no third-party dependency, so the offline test suite
runs without ``hnswlib`` or ``numpy``. When ``hnswlib`` IS installed it is used
lazily as an approximate-nearest-neighbour ACCELERATOR for candidate selection;
candidates are always re-scored with the exact cosine above, so hnswlib only
affects which records are scored (recall), never the scores themselves. If the
hnswlib path raises for any reason it degrades silently to the exact brute-force
scan. The hnswlib acceleration is validated by the SC-001 latency benchmark in
v0.2-W3; this wave proves correctness on the brute-force path.

absorbs: 02_ruflo/vector-store-hnsw
"""

from __future__ import annotations

import json
import logging
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from cexai.memory._shared.types import (
    Embedding,
    MemoryQuery,
    MemoryRecord,
    VectorHit,
)

_LOG = logging.getLogger("cexai.memory.vector")

_PERSIST_VERSION = "1.0.0"


def _cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Exact cosine similarity (higher = closer). Returns 0.0 if either vector is
    the zero vector. Works for any embedder, normalized or not."""
    dot = 0.0
    for x, y in zip(a, b):
        dot += x * y
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _matches(filters: Mapping[str, Any], metadata: Mapping[str, Any]) -> bool:
    """A record is a candidate when every filter facet equals its metadata value.
    Empty filters match everything (MemoryQuery default)."""
    for key, value in filters.items():
        if metadata.get(key) != value:
            return False
    return True


class HnswVectorStore:
    """Persistent vector index over ``MemoryRecord``s. Satisfies ``VectorStore``.

    ``dim`` may be ``None`` -- it is then inferred from the first inserted
    embedding. ``metric`` is ``cosine`` in v0.2 (the only metric the scorer
    implements). ``path`` enables ``persist`` and, when it already exists, the
    index is reloaded from it on construction (FR-003). ``M`` / ``ef_construction``
    are the hnswlib build params used only when that accelerator is active.
    ``backend`` is ``auto`` (use hnswlib if importable, else brute) or ``brute``
    to force the pure-Python scan."""

    def __init__(
        self,
        dim: int | None = None,
        metric: str = "cosine",
        path: str | Path | None = None,
        M: int = 16,
        ef_construction: int = 200,
        backend: str = "auto",
    ) -> None:
        self._dim = dim
        self._metric = metric
        self._path = Path(path) if path is not None else None
        self._M = M
        self._ef_construction = ef_construction
        self._records: dict[str, MemoryRecord] = {}
        self._vectors: dict[str, tuple[float, ...]] = {}
        self._model_id: str | None = None
        self._backend_name = self._resolve_backend(backend)
        # hnswlib accelerator state (rebuilt lazily from _vectors when dirty).
        self._hnsw = None
        self._label_ids: dict[int, str] = {}
        self._dirty = True
        if self._path is not None and self._path.exists():
            self._load()

    # -- construction helpers ------------------------------------------------ #

    @staticmethod
    def _resolve_backend(backend: str) -> str:
        if backend == "brute":
            return "brute"
        try:
            import hnswlib  # noqa: F401
        except Exception:
            # Documented pure-Python fallback when the optional extra is absent.
            return "brute"
        return "hnswlib"

    @property
    def backend(self) -> str:
        """Active backend: ``hnswlib`` (accelerated) or ``brute`` (pure-Python)."""
        return self._backend_name

    def __len__(self) -> int:
        return len(self._records)

    def records(self) -> tuple[MemoryRecord, ...]:
        """The full indexed records, in insertion order. The TF-IDF fallback
        reads these when the embedding model is unavailable."""
        return tuple(self._records.values())

    # -- VectorStore protocol ------------------------------------------------ #

    def insert(self, record: MemoryRecord, embedding: Embedding) -> None:
        vector = tuple(float(value) for value in embedding.vector)
        if self._dim is None:
            self._dim = embedding.dim or len(vector)
        if embedding.dim != self._dim or len(vector) != self._dim:
            raise ValueError(
                f"embedding dim {embedding.dim} (len {len(vector)}) "
                f"!= store dim {self._dim}"
            )
        # HNSW has no in-place update: re-indexing an id is delete then insert.
        if record.id in self._records:
            self.delete(record.id)
        self._records[record.id] = record
        self._vectors[record.id] = vector
        self._model_id = embedding.model_id
        self._dirty = True

    def query(
        self, q: MemoryQuery, embedding: tuple[float, ...]
    ) -> tuple[VectorHit, ...]:
        if not self._vectors:
            return ()  # 02 edge case: empty corpus -> [] (never raises)

        candidate_ids = list(self._vectors)
        if self._backend_name == "hnswlib":
            accelerated = self._hnsw_candidates(embedding, q.top_k)
            if accelerated is not None:
                candidate_ids = accelerated

        scored: list[tuple[float, str]] = []
        for record_id in candidate_ids:
            record = self._records.get(record_id)
            if record is None:
                continue
            if q.filters and not _matches(q.filters, record.metadata):
                continue
            score = _cosine(embedding, self._vectors[record_id])
            scored.append((score, record_id))

        # Stable ordering: score desc, then id asc as a deterministic tie-break
        # (SC-001 requires stable scoring across runs).
        scored.sort(key=lambda item: (-item[0], item[1]))
        return tuple(
            VectorHit(record_id=record_id, score=score, rank=rank)
            for rank, (score, record_id) in enumerate(scored[: q.top_k])
        )

    def delete(self, record_id: str) -> None:
        self._records.pop(record_id, None)
        self._vectors.pop(record_id, None)
        self._dirty = True

    def persist(self) -> None:
        if self._path is None:
            raise ValueError("no path configured; construct with path=... to persist")
        payload = {
            "version": _PERSIST_VERSION,
            "dim": self._dim,
            "metric": self._metric,
            "model_id": self._model_id,
            "records": [
                {
                    "id": record.id,
                    "content": record.content,
                    "kind": record.kind,
                    "source_path": record.source_path,
                    "timestamp": record.timestamp,
                    "metadata": dict(record.metadata),
                    "vector": list(self._vectors[record.id]),
                }
                for record in self._records.values()
            ],
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(payload, ensure_ascii=True), encoding="utf-8"
        )

    # -- persistence + hnswlib internals ------------------------------------- #

    def _load(self) -> None:
        assert self._path is not None
        data = json.loads(self._path.read_text(encoding="utf-8"))
        self._dim = data.get("dim", self._dim)
        self._metric = data.get("metric", self._metric)
        self._model_id = data.get("model_id")
        for row in data.get("records", []):
            record = MemoryRecord(
                id=row["id"],
                content=row["content"],
                kind=row["kind"],
                source_path=row.get("source_path"),
                timestamp=row["timestamp"],
                metadata=dict(row.get("metadata") or {}),
            )
            self._records[record.id] = record
            self._vectors[record.id] = tuple(float(value) for value in row["vector"])
        self._dirty = True

    def _hnsw_candidates(
        self, embedding: tuple[float, ...], top_k: int
    ) -> list[str] | None:
        """Return an over-fetched candidate id list via hnswlib, or ``None`` to
        signal the caller to scan everything. Never raises -- any failure
        degrades to the exact brute-force scan."""
        try:
            import hnswlib

            self._ensure_hnsw(hnswlib)
            count = len(self._vectors)
            if count == 0 or self._hnsw is None:
                return None
            # Over-fetch so the exact re-score + filters still have headroom.
            k = min(count, max(top_k * 4, top_k + 10))
            self._hnsw.set_ef(max(k, 64))
            labels, _distances = self._hnsw.knn_query([list(embedding)], k=k)
            return [
                self._label_ids[int(label)]
                for label in labels[0]
                if int(label) in self._label_ids
            ]
        except Exception as exc:  # accelerator is best-effort; exact scan is truth
            _LOG.debug("hnswlib candidate lookup failed; using brute-force (%s)", exc)
            return None

    def _ensure_hnsw(self, hnswlib: Any) -> None:
        """(Re)build the hnswlib index from the authoritative vectors when dirty."""
        if not self._dirty and self._hnsw is not None:
            return
        ids = list(self._vectors)
        index = hnswlib.Index(space="cosine", dim=self._dim)
        index.init_index(
            max_elements=max(len(ids), 1),
            ef_construction=self._ef_construction,
            M=self._M,
        )
        self._label_ids = {}
        if ids:
            data = []
            labels = []
            for label, record_id in enumerate(ids):
                self._label_ids[label] = record_id
                data.append(list(self._vectors[record_id]))
                labels.append(label)
            index.add_items(data, labels)
        self._hnsw = index
        self._dirty = False


def build_store(
    dim: int | None = None,
    *,
    path: str | Path | None = None,
    metric: str = "cosine",
    M: int = 16,
    ef_construction: int = 200,
    backend: str = "auto",
) -> HnswVectorStore:
    """Construct an ``HnswVectorStore``. If ``path`` already exists, the index is
    reloaded from it (FR-003); otherwise an empty store is returned that will
    persist to ``path`` on ``persist()``."""
    return HnswVectorStore(
        dim=dim,
        metric=metric,
        path=path,
        M=M,
        ef_construction=ef_construction,
        backend=backend,
    )
