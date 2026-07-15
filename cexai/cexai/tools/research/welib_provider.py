"""WelibProvider -- the concrete ResearchProvider seam (cexai-specs/11_welib).

Implements the frozen ``ResearchProvider`` Protocol
(``cexai.tools._shared.types``): a topic ``WelibQuery`` returns a ranked tuple of
``Citation`` over a welib ``rag_source`` (``source_type: welib``). Three behaviours
this layer owns on top of the dumb frozen types (Article VIII):

  * US P1 / FR-002 -- ranked retrieval, capped at ``query.max_results``.
  * Edge "no matches" -- an EMPTY tuple, NEVER a fabricated reference. Fabricating
    sources is N01's cardinal anti-pattern (Analytical Envy must cite, not invent).
  * FR-004 / SC-003 / WL2 -- a bulk request (``max_results >= bulk_threshold``,
    default N=10) is refused with ``BulkDownloadRefusedError`` BEFORE any fetch.
    welib is a metadata + excerpt channel, not a bulk-download pipe.
  * FR-007 / [WELIB_DOWN] -- when welib is unreachable the provider falls back to
    an injected arXiv source and marks the provenance (arXiv is unambiguously
    legitimate; Article XV citizenship is preserved).

The retrieval BACKEND is injected (Dependency Inversion) so the lane tests run
fully offline: the impl wave wires welib over the 09 stealthy ``Fetcher`` and the
arXiv API; the tests inject fakes. Constructing ``WelibProvider()`` with no backend
is valid -- it is the no-source state and ``search`` returns an empty tuple (this
is the path the shared contract test ``test_research_provider_cites`` drives, and
it cannot fabricate because there is no source).

REUSES existing kinds -- ``rag_source`` (the welib source descriptor,
``source_type: welib``) and ``citation`` (the per-reference artifact). This module
registers ZERO new kinds; ``Citation`` here is the frozen runtime shape, not a kind
definition.

absorbs: 11_welib
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from cexai.tools._shared.errors import BulkDownloadRefusedError, ToolsError
from cexai.tools._shared.types import Citation, WelibQuery

__all__ = [
    "WelibBackend",
    "WelibUnreachableError",
    "WelibProvider",
]


class WelibUnreachableError(ToolsError):
    """The welib endpoint could not be reached (11 FR-007 / the ``[WELIB_DOWN]``
    path). A lane-local ``ToolsError`` leaf -- the frozen ``errors`` module
    explicitly allows impl waves to add leaves under ``ToolsError`` in their own
    lane. An injected backend RAISES this to signal an outage, which is distinct
    from a reachable-but-empty result (no match -> empty tuple, no fallback).
    ``WelibProvider.search`` catches it internally to trigger the arXiv fallback;
    it never escapes ``search`` (a total outage degrades to an empty tuple rather
    than re-raising, so a caller never sees fabricated or failed results)."""

    def __init__(self, reason: str = "welib unreachable") -> None:
        self.reason = reason
        super().__init__(reason)


@runtime_checkable
class WelibBackend(Protocol):
    """The injected retrieval seam behind ``WelibProvider`` (offline-testable).

    A concrete backend queries one source and returns its ranked candidate
    references. The welib backend runs over the 09 stealthy ``Fetcher``; the
    fallback backend hits the arXiv API. ``fetch`` returns an empty tuple on no
    match (NEVER fabricated) and raises ``WelibUnreachableError`` when its endpoint
    is down. Ranking + the ``max_results`` cap are applied by ``WelibProvider``,
    so a backend may return its full ranked candidate set."""

    def fetch(self, query: WelibQuery) -> tuple[Citation, ...]:
        """Return ranked candidate ``Citation`` for ``query`` (empty on no match)."""
        ...


class WelibProvider:
    """Concrete ``ResearchProvider`` over a welib ``rag_source`` with ethical-use
    bulk refusal and an arXiv fallback. See the module docstring for the contract.

    ``backend`` is the primary (welib) source; ``arxiv_fallback`` is the FR-007
    fallback; both are optional injected ``WelibBackend`` instances. ``source_type``
    is the provenance label for the primary source (the ``rag_source`` variant,
    default ``"welib"``). ``last_provenance`` records which source answered the most
    recent ``search`` (``"welib"`` / ``"arxiv"`` / ``None`` when no source
    answered) -- the side channel for provenance marking, since the frozen
    ``Citation`` shape carries no source field and ``search`` must return exactly a
    ``tuple[Citation, ...]``."""

    def __init__(
        self,
        backend: WelibBackend | None = None,
        *,
        arxiv_fallback: WelibBackend | None = None,
        source_type: str = "welib",
    ) -> None:
        self._backend = backend
        self._arxiv = arxiv_fallback
        self.source_type = source_type
        self.last_provenance: str | None = None

    def search(self, query: WelibQuery) -> tuple[Citation, ...]:
        """Return a ranked tuple of ``Citation`` for ``query`` (empty on no match).

        Refuses a bulk request before touching any source (FR-004); queries welib,
        falling back to arXiv on an unreachable welib (FR-007); never fabricates."""
        # FR-004 / SC-003 / WL2: refuse a bulk request up front -- before any fetch,
        # so the refusal is unconditional and no source work is wasted.
        if query.max_results >= query.bulk_threshold:
            raise BulkDownloadRefusedError(query.max_results, query.bulk_threshold)

        self.last_provenance = None

        if self._backend is not None:
            try:
                refs = self._backend.fetch(query)
            except WelibUnreachableError:
                return self._fallback(query)
            self.last_provenance = self.source_type
            return self._rank(refs, query.max_results)

        # No primary source wired: try the fallback if present, else empty.
        return self._fallback(query)

    def _fallback(self, query: WelibQuery) -> tuple[Citation, ...]:
        """FR-007 arXiv fallback. Returns empty (never fabricated) when no fallback
        is configured or the fallback is also unreachable."""
        if self._arxiv is None:
            return ()
        try:
            refs = self._arxiv.fetch(query)
        except WelibUnreachableError:
            return ()  # both sources down -> degrade to empty, never fabricate
        self.last_provenance = "arxiv"
        return self._rank(refs, query.max_results)

    @staticmethod
    def _rank(refs: tuple[Citation, ...], max_results: int) -> tuple[Citation, ...]:
        """Enforce the ``max_results`` cap on already-ranked backend results. No
        re-ordering and no synthetic entries: a source can never return more than
        the caller asked for, and the provider never invents references."""
        if max_results <= 0:
            return ()
        return tuple(refs[:max_results])
