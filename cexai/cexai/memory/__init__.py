"""CEXAI memory substrate -- the v0.2 layer over the v0.1 foundation.

Three complementary subsystems share one frozen vocabulary
(``cexai.memory._shared.types``):

  vector    semantic recall via HNSW + embeddings   (W1) -- cexai-specs/02_ruflo
  graph     structural query over a typed graph      (W1) -- cexai-specs/06_graphify
  episodic  capture -> compress -> inject session mem (W2) -- cexai-specs/07_claude-mem

W3 adds the ``recall`` facade below: the one cross-subsystem entrypoint that the
live CEX engine (``_tools/cex_8f_runner.py`` F3 INJECT) calls as an OPTIONAL,
richer-than-TF-IDF retrieval path. It is the only thing this package exposes at
the top level; the subsystems stay addressable at ``cexai.memory.{vector,graph,
episodic}``.

Import is intentionally light (Article VIII): this module only defines ``recall``
+ its tiny helpers. The vector store / embedder / TF-IDF fallback are imported
LAZILY inside ``recall`` so ``import cexai.memory`` never pulls the W1 stack (or
the optional ``hnswlib`` / ``ollama`` extras) until a recall actually runs.

TAXONOMY NOTE: memory entities reuse EXISTING CEX kinds (vector_store,
knowledge_graph, episodic_memory, session_state, memory_summary,
knowledge_index). No new kind is registered.

absorbs: 02_ruflo/vector + 06_graphify/graph + 07_claude-mem/episodic
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # annotations only -- no runtime import of the frozen contracts
    from cexai.memory._shared.types import MemoryRecord
    from cexai.memory.vector import HnswVectorStore

__all__ = ["recall"]

_LOG = logging.getLogger("cexai.memory")


def _default_embedder():
    """The production embedder (BGE-M3 via Ollama, 02 FR-009). Connectionless to
    construct; its first ``embed`` raises ``EmbeddingUnavailableError`` when no
    model is reachable, which ``recall`` catches to degrade to TF-IDF. Tests and
    offline callers pass a ``FakeEmbedder`` explicitly instead."""
    from cexai.memory.vector import OllamaEmbedder

    return OllamaEmbedder()


def recall(
    query: str,
    *,
    top_k: int = 10,
    records: "Iterable[MemoryRecord] | None" = None,
    embedder: Any | None = None,
    store: "HnswVectorStore | None" = None,
) -> list[dict]:
    """Recall the ``top_k`` records most relevant to ``query`` over the vector
    substrate, as a list of plain dicts (best first).

    The retrieval path mirrors cexai-specs/02_ruflo: embed each record + the
    query and rank by cosine via the HNSW vector store (Ollama when present, an
    injected ``FakeEmbedder`` offline); when the embedding model is unavailable
    it degrades to the TF-IDF retriever over the same records and stamps a
    ``[FALLBACK]`` log marker (the 02 edge case). It NEVER raises for an absent
    model -- that recoverable condition is the fallback trigger -- so a caller
    (e.g. the 8F F3 seam) can wrap it in a single try/except and treat any other
    failure as "skip enrichment".

    ``records`` is the corpus to search (the frozen ``MemoryRecord`` contract);
    with no corpus -- or an empty query -- this returns ``[]`` (nothing to
    recall). ``embedder`` overrides the default (tests inject ``FakeEmbedder``
    for deterministic, model-free recall).

    ``store`` is an OPTIONAL pre-built/persisted ``HnswVectorStore`` (e.g. one
    constructed with ``path=`` and reloaded via ``VectorStore.persist()``) that
    the caller wants reused across calls. When omitted (the default), ``recall``
    builds a fresh in-memory store and embeds every record every call -- exactly
    the original behaviour, unchanged. When provided, any record already present
    in ``store`` with identical content is NOT re-embedded (R-240): only new or
    changed records pay the embedding cost, so a caller that keeps passing the
    same ``store`` (module-level cache, or a store reloaded from ``persist()``)
    stops re-embedding the whole corpus on every ``recall()`` call. The corpus
    is still searched via ``store.query`` in full, so results are identical
    either way -- this only changes how much embedding work repeats.

    Each result dict: ``id``, ``score``, ``rank``, ``kind``, ``source_path``,
    ``tldr`` (a content preview), and ``fallback`` (True when TF-IDF answered).
    """
    corpus = tuple(records or ())
    if not corpus or not query or not query.strip():
        return []

    from cexai.memory._shared.errors import EmbeddingUnavailableError
    from cexai.memory._shared.types import Embedding, MemoryQuery
    from cexai.memory.vector import HnswVectorStore, TfidfFallback

    emb = embedder if embedder is not None else _default_embedder()
    fallback = False
    try:
        active_store = store if store is not None else HnswVectorStore()
        # Records already indexed with identical content skip re-embedding
        # (R-240). A fresh ``active_store`` (the default, no ``store=`` passed)
        # is always empty here, so every record is embedded -- unchanged
        # default behaviour.
        already_indexed = {
            indexed.id: indexed.content for indexed in active_store.records()
        }
        for record in corpus:
            if already_indexed.get(record.id) == record.content:
                continue
            vector = emb.embed(record.content)
            active_store.insert(
                record,
                Embedding(
                    record_id=record.id,
                    model_id=emb.name,
                    vector=vector,
                    dim=len(vector),
                    created_at=record.timestamp,
                ),
            )
        hits = active_store.query(MemoryQuery(text=query, top_k=top_k), emb.embed(query))
    except EmbeddingUnavailableError as exc:
        _LOG.warning(
            "[FALLBACK] embedding model unavailable (%s); recall() using TF-IDF retriever",
            exc,
        )
        hits = TfidfFallback(corpus).query(query, top_k)
        fallback = True

    by_id = {record.id: record for record in corpus}
    results: list[dict] = []
    for hit in hits:
        record = by_id.get(hit.record_id)
        results.append(
            {
                "id": hit.record_id,
                "score": round(float(hit.score), 6),
                "rank": hit.rank,
                "kind": record.kind if record is not None else None,
                "source_path": record.source_path if record is not None else None,
                "tldr": (record.content[:200] if record is not None else ""),
                "fallback": fallback,
            }
        )
    return results
