"""Embedders for the vector subsystem (cexai-specs/02_ruflo, FR-009).

Two implementations of the frozen ``Embedder`` protocol
(``cexai.memory._shared.types.Embedder``):

  * ``FakeEmbedder``   -- deterministic, dependency-free, offline. A stable hash
                          of each token folds into fixed buckets, then the vector
                          is L2-normalized so cosine self-similarity is exactly
                          1.0. Same text always yields the same vector across
                          processes (Article XIV: the substrate is testable
                          without a live model).
  * ``OllamaEmbedder`` -- production default (BGE-M3 via Ollama, FR-009). The
                          ``ollama`` client is imported lazily inside ``_call`` so
                          importing this module never requires it; any failure to
                          reach the model surfaces as the recoverable
                          ``EmbeddingUnavailableError`` (02 edge case -> TF-IDF
                          fallback).

absorbs: 02_ruflo/vector-store-hnsw
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

from cexai.memory._shared.errors import EmbeddingUnavailableError

# Default embedding model per spec FR-009 (BGE-M3 via Ollama, master_plan matrix).
DEFAULT_OLLAMA_MODEL = "bge-m3"
# FakeEmbedder dimension -- small + constant so test vectors are cheap to compare.
_FAKE_DIM = 32

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokens. Shared by FakeEmbedder and the TF-IDF
    fallback so both score text the same way."""
    return _TOKEN_RE.findall(text.lower())


def _stable_bucket(token: str, dim: int) -> int:
    """Map a token to a bucket via a process-stable hash (blake2b, not the
    salted builtin ``hash``), so embeddings are reproducible across runs."""
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % dim


@dataclass(frozen=True, slots=True)
class FakeEmbedder:
    """A deterministic offline ``Embedder``. ``name`` stamps the ``model_id`` on
    produced embeddings; ``embed`` is pure (same text -> same L2-normalized
    vector), so vector-store behaviour is verifiable without a live model."""

    name: str = "fake-hash-32"
    dim: int = _FAKE_DIM

    def embed(self, text: str) -> tuple[float, ...]:
        buckets = [0.0] * self.dim
        for token in _tokenize(text):
            buckets[_stable_bucket(token, self.dim)] += 1.0
        norm = math.sqrt(sum(value * value for value in buckets))
        if norm == 0.0:
            return tuple(buckets)
        return tuple(value / norm for value in buckets)


class OllamaEmbedder:
    """The production embedder (BGE-M3 via Ollama, FR-009).

    Construction is cheap and connectionless -- it only records config. The
    ``ollama`` client is imported lazily inside ``_call`` so this module imports
    without the optional ``cexai[memory]`` extra. Any failure (missing client,
    refused connection, unknown model) is wrapped as ``EmbeddingUnavailableError``
    so callers fall back to the TF-IDF retriever (02 edge case)."""

    def __init__(self, model: str = DEFAULT_OLLAMA_MODEL, host: str | None = None) -> None:
        self.model = model
        self.host = host

    @property
    def name(self) -> str:
        return f"ollama:{self.model}"

    def _call(self, text: str) -> list[float]:
        """Perform the live embedding call. Isolated so tests can substitute it
        and so all transport errors funnel through ``embed``'s wrapper."""
        import ollama  # lazy: optional dependency, not needed to import this module

        client = ollama.Client(host=self.host) if self.host else ollama
        response = client.embeddings(model=self.model, prompt=text)
        return list(response["embedding"])

    def embed(self, text: str) -> tuple[float, ...]:
        try:
            return tuple(float(value) for value in self._call(text))
        except EmbeddingUnavailableError:
            raise
        except Exception as exc:  # ImportError, ConnectionError, KeyError, ...
            raise EmbeddingUnavailableError(
                f"ollama embedder '{self.model}' unavailable: {exc}"
            ) from exc
