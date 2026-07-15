"""Within-TTL fetch cache (cexai-specs/09_scrapling FR-004 / SC-003).

A tiny, dependency-free time-to-live cache. The fetcher stores successful
``FetchResult``s here keyed by ``(url, tier)``; a repeat within the TTL window is
served without a backend call (the ``[CACHE_HIT]`` path), which is what SC-003's
">= 80% hit on repeated fetches" measures. The clock is injectable so TTL expiry
is deterministic and instant under test -- no ``time.sleep`` in the suite
(Article XIV).

Eviction is lazy: an entry past its TTL is dropped on the ``get`` that observes it
(and a periodic sweep keeps a bounded cache from growing without bound). This is a
process-local cache; the spec's on-disk cache backing is an impl detail a future
wave can layer behind the same ``get`` / ``put`` seam.

absorbs: 09_scrapling
"""

from __future__ import annotations

import time
from collections.abc import Callable, Hashable
from typing import Any

__all__ = ["TTLCache"]


class TTLCache:
    """A monotonic-clock TTL cache. ``ttl_seconds`` is the freshness window;
    ``clock`` returns a monotonically increasing seconds value (defaults to
    ``time.monotonic`` -- never wall-clock, so a clock step-back cannot resurrect a
    stale entry). ``get`` returns the stored value when still fresh, else ``None``
    (evicting the expired entry); ``put`` stamps the value with the current time."""

    def __init__(
        self,
        ttl_seconds: float = 300.0,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._ttl = float(ttl_seconds)
        self._clock = clock
        self._entries: dict[Hashable, tuple[float, Any]] = {}

    def get(self, key: Hashable) -> Any | None:
        """Return the fresh value for ``key`` or ``None`` (expired/absent). An entry
        observed past its TTL is evicted here."""
        entry = self._entries.get(key)
        if entry is None:
            return None
        stamped_at, value = entry
        if self._clock() - stamped_at >= self._ttl:
            self._entries.pop(key, None)
            return None
        return value

    def put(self, key: Hashable, value: Any) -> None:
        """Store ``value`` under ``key``, stamped at the current clock time."""
        self._sweep()
        self._entries[key] = (self._clock(), value)

    def __contains__(self, key: Hashable) -> bool:
        return self.get(key) is not None

    def __len__(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()

    def _sweep(self) -> None:
        """Drop every entry whose TTL has elapsed -- keeps the cache bounded without
        a background task."""
        now = self._clock()
        expired = [
            key
            for key, (stamped_at, _value) in self._entries.items()
            if now - stamped_at >= self._ttl
        ]
        for key in expired:
            self._entries.pop(key, None)
