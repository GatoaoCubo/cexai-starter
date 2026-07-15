"""Ingestion subsystem -- tier-escalating web fetch (impl: v0.4 impl wave).

The three explicit fetcher tiers (basic / stealthy / dynamic) behind one
``cexai.web.fetch(url)`` API, robots.txt enforcement (RFC 9309, fail-closed on
malformed), within-TTL caching, and checkpoint-based crawl resume over the
existing ``checkpoint`` kind (cexai-specs/09_scrapling FR-001..008). Integrates
scrapling via the vertical-08 MCP loader (consumer, Mode A -- no re-derivation).
The frozen ``FetchResult`` / ``FetchTier`` / ``RobotsPolicy`` / ``Fetcher``
contracts live in ``cexai.tools._shared.types``; this package will ship the
concrete fetcher behind that seam.

Public surface:
  * ``TieredFetcher`` / ``build_fetcher`` -- the concrete frozen ``Fetcher`` impl.
  * ``RawResponse`` / ``FetchBackend``    -- the injected transport seam (a fake in
                                             tests, the scrapling MCP adapter in prod).
  * ``TTLCache``                          -- the within-TTL fetch cache (FR-004).
  * ``RobotsTxt`` / ``RobotsDecision``    -- the RFC 9309-style robots gate (FR-003).
  * ``CheckpointingCrawler`` / ``CrawlState`` -- checkpoint-resumable crawl (US P2),
                                             reusing the ``checkpoint`` kind concept.

absorbs: 09_scrapling
"""

from cexai.tools.ingestion.cache import TTLCache
from cexai.tools.ingestion.crawl import CheckpointingCrawler, CrawlState
from cexai.tools.ingestion.fetcher import (
    FetchBackend,
    RawResponse,
    TieredFetcher,
    build_fetcher,
)
from cexai.tools.ingestion.robots import RobotsDecision, RobotsTxt

__all__ = [
    "TieredFetcher",
    "build_fetcher",
    "RawResponse",
    "FetchBackend",
    "TTLCache",
    "RobotsTxt",
    "RobotsDecision",
    "CheckpointingCrawler",
    "CrawlState",
]
