"""Tier-escalating web fetcher (cexai-specs/09_scrapling US P1 + FR-001..007).

``TieredFetcher`` is the concrete implementation of the frozen ``Fetcher`` Protocol
(``cexai.tools._shared.types.Fetcher``). One ``fetch(url, tier)`` API spans three
EXPLICIT tiers -- ``basic`` (light HTTP), ``stealthy`` (anti-bot bypass), and
``dynamic`` (headless-browser DOM) -- and escalation is never silent: the caller
declares the tier and the fetcher passes it straight through to the backend
(FR-002). The actual fetching is done by an injected ``backend`` so the whole hot
path is offline-testable with a fake (Article XIV); production lazily resolves the
scrapling MCP backend (vertical-08 loader, Mode A -- consume upstream, do not
re-derive) and, when scrapling is absent, every fetch returns a clean error
``FetchResult`` rather than raising.

Three behaviors are layered around the backend call:
  * cache (FR-004 / SC-003): a successful fetch is stored under ``(url, tier)``;
    a repeat within the TTL is served with ``from_cache=True`` and no backend call.
  * robots.txt (FR-003 / SC-004): when the policy says ``respect``, the fetcher
    obtains ``/robots.txt`` through the same backend and enforces an RFC 9309-style
    decision -- a disallowed path with no override raises ``RobotsBlockedError``,
    and a malformed robots.txt FAILS CLOSED (also ``RobotsBlockedError``).
  * error handling (FR-007): a network / 4xx / 5xx failure -- or any backend
    exception -- is RETURNED as ``FetchResult(status="error", errors=(...))``, never
    raised. The single raising path is the robots.txt block above.

Crawl-level resumability (US P2) lives in the sibling ``crawl`` module and drives
this fetcher one URL at a time.

absorbs: 09_scrapling
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any, Protocol, runtime_checkable
from urllib.parse import urlsplit

from cexai.tools._shared.errors import RobotsBlockedError
from cexai.tools._shared.types import FetchResult, RobotsPolicy
from cexai.tools.ingestion.cache import TTLCache
from cexai.tools.ingestion.robots import RobotsTxt

__all__ = ["RawResponse", "FetchBackend", "TieredFetcher", "build_fetcher"]

_LOG = logging.getLogger("cexai.tools.ingestion")

# The canonical tier set (mirrors the frozen ``FetchTier`` Literal). Kept here so
# an unknown tier is a loud caller error rather than a silent mis-fetch.
_TIERS = frozenset({"basic", "stealthy", "dynamic"})

_EMPTY: Mapping[str, Any] = MappingProxyType({})


@dataclass(frozen=True, slots=True)
class RawResponse:
    """The raw, pre-policy outcome a backend returns for one URL. ``status_code`` is
    HTTP-ish: 2xx/3xx is success, >= 400 is an HTTP error, and <= 0 marks a
    transport failure (no response). ``content`` is the body on success (``None``
    otherwise); ``headers`` is the response header map; ``error`` is a human-readable
    cause set on any failure. This is the backend seam's vocabulary -- the public
    typed result the fetcher hands callers is the frozen ``FetchResult``."""

    status_code: int
    content: str | None = None
    headers: Mapping[str, Any] = field(default=_EMPTY)
    error: str | None = None


@runtime_checkable
class FetchBackend(Protocol):
    """The injected fetch transport. ``get`` retrieves one URL at one tier and
    returns a ``RawResponse``. The fake in the test suite, the scrapling MCP adapter
    in production, and the robots.txt sub-fetch all speak this one method."""

    def get(self, url: str, tier: str) -> RawResponse:
        """Fetch ``url`` at ``tier``, returning a ``RawResponse`` (never raises for
        ordinary HTTP failures -- those ride in ``status_code`` / ``error``)."""
        ...


class _UnavailableBackend:
    """The default backend when no backend is injected and scrapling is not
    installed. Every fetch reports a transport failure, so an un-provisioned
    ``TieredFetcher()`` degrades to clean error ``FetchResult``s (FR-007) instead of
    raising -- this is the offline contract-test path."""

    _MESSAGE = (
        "scrapling backend unavailable; install the ingestion extra or inject a "
        "backend via TieredFetcher(backend=...)"
    )

    def get(self, url: str, tier: str) -> RawResponse:
        return RawResponse(status_code=0, content=None, error=self._MESSAGE)


def _load_default_backend() -> FetchBackend:
    """Lazily resolve the production backend. scrapling is an optional heavy dep
    imported only here (never at module load), so importing this package stays
    light. When it is absent we fall back to ``_UnavailableBackend`` -- the impl of
    the scrapling MCP adapter lands when the vertical-08 loader is wired; offline
    correctness does not depend on it."""
    try:
        import scrapling  # noqa: F401
    except Exception:
        return _UnavailableBackend()
    # The concrete scrapling/MCP adapter is provisioned by the vertical-08 wiring
    # wave; until then a present-but-unadapted scrapling still yields the safe
    # error path rather than a half-wired fetch.
    return _UnavailableBackend()


class TieredFetcher:
    """Concrete ``Fetcher``: tiered fetch + robots gate + TTL cache (09 scrapling).

    ``backend`` is the injected transport (defaults to the lazily-resolved scrapling
    backend, or the offline-safe ``_UnavailableBackend``). ``robots_policy`` drives
    robots.txt enforcement (default: respect, fail-closed on malformed, no
    override). ``cache`` is the within-TTL fetch cache (a fresh ``TTLCache`` of
    ``ttl_seconds`` if not supplied). ``user_agent`` is the token matched against
    robots.txt groups. ``clock`` is forwarded to the default cache so TTL is
    deterministic under test."""

    def __init__(
        self,
        backend: FetchBackend | None = None,
        *,
        robots_policy: RobotsPolicy | None = None,
        cache: TTLCache | None = None,
        ttl_seconds: float = 300.0,
        user_agent: str = "cexai",
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._backend = backend if backend is not None else _load_default_backend()
        self._robots_policy = robots_policy if robots_policy is not None else RobotsPolicy()
        self._cache = cache if cache is not None else TTLCache(ttl_seconds, clock=clock)
        self._user_agent = user_agent

    # -- Fetcher protocol ---------------------------------------------------- #
    def fetch(self, url: str, tier: str) -> FetchResult:
        """Fetch ``url`` at ``tier`` and return a typed ``FetchResult``.

        Order: cache -> robots gate -> backend. A within-TTL repeat short-circuits
        before any robots or network call. A robots disallow / malformed body raises
        ``RobotsBlockedError``; every other failure rides in ``FetchResult.errors``
        (FR-007). ``tier`` MUST be one of basic/stealthy/dynamic -- escalation is the
        caller's explicit choice, never silent (FR-002)."""
        if tier not in _TIERS:
            raise ValueError(
                f"unknown fetch tier {tier!r}; expected one of {sorted(_TIERS)}"
            )

        cache_key = (url, tier)
        cached = self._cache.get(cache_key)
        if cached is not None:
            # [CACHE_HIT] -- served within TTL, no robots re-check, no network.
            return replace(cached, from_cache=True)

        if self._robots_policy.respect:
            self._enforce_robots(url, tier)

        result = self._backend_fetch(url, tier)
        if result.status == "ok":
            self._cache.put(cache_key, result)
        return result

    # -- internals ----------------------------------------------------------- #
    def _backend_fetch(self, url: str, tier: str) -> FetchResult:
        """Call the backend and normalize its ``RawResponse`` to a ``FetchResult``.
        Any backend exception is captured as an error result (FR-007)."""
        try:
            raw = self._backend.get(url, tier)
        except Exception as exc:  # FR-007: transport blow-ups never escape as raises
            _LOG.debug("backend fetch raised for %r at %s: %s", url, tier, exc)
            return FetchResult(
                url=url, status="error", content=None, errors=(f"{type(exc).__name__}: {exc}",)
            )
        return self._normalize(url, raw)

    @staticmethod
    def _normalize(url: str, raw: RawResponse) -> FetchResult:
        headers = MappingProxyType(dict(raw.headers))
        if 200 <= raw.status_code < 400 and raw.content is not None:
            return FetchResult(
                url=url, status="ok", content=raw.content, headers=headers
            )
        if raw.status_code >= 400:
            reason = raw.error or f"HTTP {raw.status_code}"
            return FetchResult(
                url=url,
                status="error",
                content=None,
                headers=headers,
                errors=(f"HTTP {raw.status_code}: {reason}",),
            )
        # status_code <= 0 (transport failure) or a 2xx/3xx with no body.
        reason = raw.error or "no response body"
        return FetchResult(url=url, status="error", content=None, headers=headers, errors=(reason,))

    def _enforce_robots(self, url: str, tier: str) -> None:
        """Fetch + evaluate robots.txt for ``url``; raise ``RobotsBlockedError`` on a
        disallow (no override), a malformed body (fail-closed), or a non-network
        error during the robots.txt sub-fetch (fail-closed, R-234). Only a
        genuinely unreachable (network-level) or 404 robots.txt means 'no rules'
        -> allow; any other ambiguous failure fails closed rather than silently
        proceeding."""
        policy = self._robots_policy
        split = urlsplit(url)
        if not split.scheme or not split.netloc:
            return  # not an absolute http(s) URL -> nothing to gate
        robots_url = f"{split.scheme}://{split.netloc}/robots.txt"
        try:
            raw = self._backend.get(robots_url, tier)
        except (TimeoutError, ConnectionError, OSError) as exc:
            # R-234: narrow to network-level failure only (unreachable host, DNS,
            # connection refused, timeout) -- a genuinely unreachable robots.txt
            # reads as "no rules" (RFC 9309 2.2.3), same as an HTTP 404 below.
            _LOG.debug(
                "robots fetch unreachable for %s: %s -- treating as no rules",
                robots_url,
                exc,
            )
            return
        except Exception as exc:
            # R-234: anything OTHER than a network-level failure means the robots
            # sub-fetch reached *something* but could not be trusted (e.g. the
            # backend blew up decoding/parsing the response). That is NOT
            # "absent" -- it is ambiguous, so fail closed instead of silently
            # proceeding, mirroring the malformed-body gate below.
            _LOG.debug(
                "robots fetch raised a non-network error for %s: %s -- failing closed",
                robots_url,
                exc,
            )
            if policy.fail_closed_on_malformed and not policy.allow_override:
                raise RobotsBlockedError(url, "[ROBOTS_FETCH_ERROR]") from exc
            return

        if raw.status_code <= 0 or raw.status_code >= 400 or raw.content is None:
            # Unreachable / not-found robots.txt: RFC 9309 treats absence as allow.
            return

        robots = RobotsTxt.parse(raw.content)
        if robots.malformed:
            if policy.fail_closed_on_malformed and not policy.allow_override:
                raise RobotsBlockedError(url, "[ROBOTS_MALFORMED]")
            return  # fail-open only when explicitly configured (or overridden)

        path = split.path or "/"
        if split.query:
            path = f"{path}?{split.query}"
        decision = robots.is_allowed(path, user_agent=self._user_agent)
        if not decision.allowed and not policy.allow_override:
            raise RobotsBlockedError(url, decision.rule or path)


def build_fetcher(
    backend: FetchBackend | None = None,
    *,
    robots_policy: RobotsPolicy | None = None,
    ttl_seconds: float = 300.0,
    user_agent: str = "cexai",
) -> TieredFetcher:
    """Convenience constructor mirroring the memory subsystem's ``build_store``.
    Returns a ready ``TieredFetcher`` with a fresh TTL cache."""
    return TieredFetcher(
        backend,
        robots_policy=robots_policy,
        ttl_seconds=ttl_seconds,
        user_agent=user_agent,
    )
