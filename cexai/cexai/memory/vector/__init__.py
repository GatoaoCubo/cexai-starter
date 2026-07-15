"""Vector subsystem -- semantic recall via HNSW + embeddings (v0.2-W1).

Implements the ``VectorStore`` + ``Embedder`` protocols from
``cexai.memory._shared.types`` against an exact in-memory index (pure-Python
cosine) that lazily uses ``hnswlib`` as an accelerator when installed, satisfying
cexai-specs/02_ruflo/spec.md US P1 (FR-001..003). HNSW has no in-place update,
so re-indexing is delete+insert (02 acceptance #3). When the embedding model is
unavailable, ``query_with_fallback`` drops to the TF-IDF retriever and emits a
``[FALLBACK]`` marker (02 edge case). SC-001 latency + SC-002 recall benchmarks
land in v0.2-W3.

Heavy deps (``hnswlib`` via ``pip install cexai[memory]``, ``ollama``) are
OPTIONAL and imported lazily inside the implementations, so importing this
package never requires them.

Public surface:
  * ``HnswVectorStore`` / ``build_store`` -- the persistent vector index.
  * ``FakeEmbedder``    -- deterministic offline embedder (tests, dev).
  * ``OllamaEmbedder``  -- production BGE-M3 embedder (FR-009).
  * ``TfidfFallback`` / ``query_with_fallback`` -- the embedding-unavailable path.

``InMemoryVectorStore`` is an alias of ``HnswVectorStore`` kept so the frozen W0
contract seam (``tests/memory/contract/test_memory_contracts.py``) can be
un-skipped in a later wave without editing that file.

absorbs: 02_ruflo/vector-store-hnsw
"""

from cexai.memory.vector.embedder import (
    DEFAULT_OLLAMA_MODEL,
    FakeEmbedder,
    OllamaEmbedder,
)
from cexai.memory.vector.fallback import TfidfFallback, query_with_fallback
from cexai.memory.vector.store import HnswVectorStore, build_store

# Alias for the frozen contract seam (test_memory_contracts.test_vector_roundtrip).
InMemoryVectorStore = HnswVectorStore

__all__ = [
    "HnswVectorStore",
    "InMemoryVectorStore",
    "build_store",
    "FakeEmbedder",
    "OllamaEmbedder",
    "DEFAULT_OLLAMA_MODEL",
    "TfidfFallback",
    "query_with_fallback",
]
