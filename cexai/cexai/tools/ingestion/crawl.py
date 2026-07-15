"""Checkpoint-based crawl resume (cexai-specs/09_scrapling US P2 / FR-005 / SC-002).

A thin crawl loop over ``TieredFetcher``: process a URL frontier one fetch at a
time, persisting a resumable state every ``checkpoint_interval`` URLs. A killed
crawl (process death, network blip, rate-limit wait) resumes from its last
checkpoint and completes -- SC-002's 100/100 kill-resume guarantee.

This REUSES the existing ``checkpoint`` kind concept (``domain: crawl``) -- it
registers NO new kind (the v0.4 wave is taxonomy-neutral). ``CrawlState`` is the
runtime projection of that checkpoint; it is persisted as a JSON sidecar at
``<checkpoint_dir>/<crawl_id>/checkpoint.json``, mirroring the spec's
``.cexai/crawls/{id}/checkpoint.json`` layout.

Backoff on 429 / Retry-After (US P2 acceptance #3) is intentionally deferred to a
later wave -- this module delivers the durable-resume core (FR-005 / SC-002) and
keeps the suite offline and sleep-free.

absorbs: 09_scrapling
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

__all__ = ["CrawlState", "CheckpointingCrawler"]

_LOG = logging.getLogger("cexai.tools.ingestion.crawl")

_CHECKPOINT_VERSION = "1.0.0"


class _FetchLike(Protocol):
    """The minimal fetch seam the crawler needs (``TieredFetcher`` satisfies it)."""

    def fetch(self, url: str, tier: str) -> Any:
        ...


@dataclass(slots=True)
class CrawlState:
    """Resumable crawl progress -- the runtime projection of a ``checkpoint``
    artifact (``domain: crawl``, NOT a new kind). ``pending`` is the remaining
    frontier (FIFO); ``completed`` / ``failed`` are the resolved URLs. Serializes to
    a JSON-safe dict via ``to_dict`` / ``from_dict``."""

    crawl_id: str
    pending: list[str] = field(default_factory=list)
    completed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": _CHECKPOINT_VERSION,
            "crawl_id": self.crawl_id,
            "pending": list(self.pending),
            "completed": list(self.completed),
            "failed": list(self.failed),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CrawlState:
        return cls(
            crawl_id=data["crawl_id"],
            pending=list(data.get("pending", [])),
            completed=list(data.get("completed", [])),
            failed=list(data.get("failed", [])),
        )


class CheckpointingCrawler:
    """Crawls a URL frontier through a fetcher, checkpointing every N URLs.

    ``fetcher`` is anything with ``fetch(url, tier) -> FetchResult`` (the v0.4
    ``TieredFetcher``). ``tier`` is the declared fetch tier for the crawl.
    ``checkpoint_interval`` is how many processed URLs between checkpoint writes.
    ``checkpoint_dir`` roots the per-crawl sidecar directory."""

    def __init__(
        self,
        fetcher: _FetchLike,
        *,
        tier: str = "basic",
        checkpoint_interval: int = 10,
        checkpoint_dir: str | Path = ".cexai/crawls",
    ) -> None:
        if checkpoint_interval <= 0:
            raise ValueError("checkpoint_interval must be positive")
        self._fetcher = fetcher
        self._tier = tier
        self._interval = checkpoint_interval
        self._root = Path(checkpoint_dir)

    # -- public API ---------------------------------------------------------- #
    def crawl(self, crawl_id: str, urls: Iterable[str]) -> CrawlState:
        """Start (or continue) a crawl. If a checkpoint for ``crawl_id`` already
        exists it is resumed; otherwise ``urls`` seed a fresh frontier."""
        state = self.load_state(crawl_id)
        if state is None:
            state = CrawlState(crawl_id=crawl_id, pending=list(urls))
        self._run(state)
        return state

    def resume(self, crawl_id: str) -> CrawlState:
        """Resume a previously checkpointed crawl. Raises ``FileNotFoundError`` if no
        checkpoint exists for ``crawl_id``."""
        state = self.load_state(crawl_id)
        if state is None:
            raise FileNotFoundError(
                f"no crawl checkpoint for {crawl_id!r} under {self._root}"
            )
        self._run(state)
        return state

    def load_state(self, crawl_id: str) -> CrawlState | None:
        """Load the persisted ``CrawlState`` for ``crawl_id``, or ``None`` if absent."""
        path = self._checkpoint_path(crawl_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return CrawlState.from_dict(data)

    # -- internals ----------------------------------------------------------- #
    def _run(self, state: CrawlState) -> None:
        """Drain ``state.pending`` front-to-back. A URL is popped only AFTER its
        fetch returns, so a fetch that raises (a simulated kill) leaves the URL in
        the frontier and the last checkpoint stays consistent for resume."""
        processed = 0
        while state.pending:
            url = state.pending[0]
            result = self._fetcher.fetch(url, self._tier)  # may raise -> caller resumes
            state.pending.pop(0)
            if getattr(result, "status", "error") == "ok":
                state.completed.append(url)
            else:
                state.failed.append(url)
            processed += 1
            if processed >= self._interval:
                self._write_checkpoint(state)
                processed = 0
        self._write_checkpoint(state)  # final flush

    def _checkpoint_path(self, crawl_id: str) -> Path:
        return self._root / crawl_id / "checkpoint.json"

    def _write_checkpoint(self, state: CrawlState) -> None:
        path = self._checkpoint_path(state.crawl_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(state.to_dict(), ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
        _LOG.debug(
            "[CHECKPOINT] crawl %s: %d done, %d pending",
            state.crawl_id,
            len(state.completed),
            len(state.pending),
        )
