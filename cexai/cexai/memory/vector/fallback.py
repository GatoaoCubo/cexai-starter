"""TF-IDF fallback for the vector subsystem (cexai-specs/02_ruflo edge case).

When the embedding model is unavailable the spec requires falling back to the
existing TF-IDF retriever and emitting a ``[FALLBACK]`` marker. This module is a
self-contained, pure-stdlib TF-IDF cosine ranker over ``MemoryRecord``s (the
shape of ``_tools/cex_retriever.py``, without its filesystem/CLI coupling) plus
``query_with_fallback``, the small router that tries the embedder first and
drops to TF-IDF on ``EmbeddingUnavailableError``.

absorbs: 02_ruflo/vector-store-hnsw
"""

from __future__ import annotations

import logging
import math
from collections import Counter
from collections.abc import Iterable
from typing import Any

from cexai.memory._shared.errors import EmbeddingUnavailableError
from cexai.memory._shared.types import Embedder, MemoryQuery, MemoryRecord, VectorHit
from cexai.memory.vector.embedder import _tokenize

_LOG = logging.getLogger("cexai.memory.vector")


def _sparse_cosine(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine similarity over two sparse term -> weight maps."""
    common = a.keys() & b.keys()
    if not common:
        return 0.0
    dot = sum(a[term] * b[term] for term in common)
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class TfidfFallback:
    """TF-IDF cosine retriever over a fixed corpus of ``MemoryRecord``s.

    Built once from the records the vector store already holds, so the fallback
    answers the same corpus the semantic index would have. Pure stdlib: no
    numpy, no sklearn -- identical in spirit to the legacy CEX retriever it
    stands in for."""

    def __init__(self, records: Iterable[MemoryRecord]) -> None:
        self._records: tuple[MemoryRecord, ...] = tuple(records)
        corpus = [_tokenize(record.content) for record in self._records]
        self._n = len(corpus)
        self._df: Counter[str] = Counter()
        for tokens in corpus:
            for term in set(tokens):
                self._df[term] += 1
        self._doc_vectors = [self._tfidf(tokens) for tokens in corpus]

    def _tfidf(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        total = len(tokens)
        counts = Counter(tokens)
        vector: dict[str, float] = {}
        for term, count in counts.items():
            tf = count / total
            idf = math.log(self._n / (1 + self._df.get(term, 0))) + 1.0
            weight = tf * idf
            if weight > 0.0:
                vector[term] = weight
        return vector

    def query(self, text: str, top_k: int = 10) -> tuple[VectorHit, ...]:
        if self._n == 0:
            return ()
        query_vector = self._tfidf(_tokenize(text))
        if not query_vector:
            return ()
        scored: list[tuple[float, str]] = []
        for record, doc_vector in zip(self._records, self._doc_vectors):
            score = _sparse_cosine(query_vector, doc_vector)
            if score > 0.0:
                scored.append((score, record.id))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return tuple(
            VectorHit(record_id=record_id, score=score, rank=rank)
            for rank, (score, record_id) in enumerate(scored[:top_k])
        )


def query_with_fallback(
    store: Any, embedder: Embedder, query: MemoryQuery
) -> tuple[VectorHit, ...]:
    """Embed ``query.text`` and search ``store``; on ``EmbeddingUnavailableError``
    log the ``[FALLBACK]`` marker and answer from the TF-IDF retriever over the
    store's own records (02 edge case). Never propagates the recoverable error."""
    try:
        embedding = embedder.embed(query.text)
    except EmbeddingUnavailableError as exc:
        _LOG.warning(
            "[FALLBACK] embedding model unavailable (%s); using TF-IDF retriever",
            exc,
        )
        return TfidfFallback(store.records()).query(query.text, query.top_k)
    return store.query(query, embedding)
