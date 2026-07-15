#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI Marketplace Tier-Router (kind: search_strategy, P04 -- composed, no new kind).

THE degrade-never resolver that clones the codexa-v2 tier-router DECISION
(_bundles/codexa-v2/pesquisa/cexai/p08_dr_tier_router_decision.md): a single
marketplace lookup tries lanes IN ORDER and returns the FIRST success, recording
which tier WON + each prior tier's failure reason. It is the marketplace twin of
the codexa "3 action providers + decision tree + fallback chain that always
degrades to TIER 1 paste" -- only the lanes differ (the codexa router picks web
search providers; this one picks marketplace structured sources):

  TIER 1 OFFICIAL_API   -- the marketplace's OWN API (the structured-truth source).
                           For Mercado Livre the public /search is RESTRICTED (0
                           results even with a valid token -- memory:
                           reference_ml_scraping_antibot_hallucination), so this
                           tier returns a clean 'restricted' result for ML and the
                           router falls through. The SEAM is kept so a Shopee /
                           Amazon official API (or the ML seller-catalog path) slots
                           in later -- inject the api client; NO live call in tests.
  TIER 2 REAL_BROWSER   -- drive a real Chrome to the search page + read the live
                           DOM (cex_playwright_scrape, the PROVEN anti-bot lane). A
                           real browser defeats the anti-bot that blocks the API /
                           firecrawl. Injected / mocked in tests (NO real browser).
  TIER 3 FIRECRAWL_EXTRACT -- structured extraction via firecrawl /v1/extract
                           (cex_marketplace_detail_extract). Injected in tests.
  TIER 4 MANUAL_PASTE   -- the always-available floor (mirrors codexa's TIER 1 paste
                           baseline): return a 'needs_paste' sentinel carrying the
                           search URL so a HUMAN can paste the page. NEVER fabricates.

SAFETY-AWARE (good citizen): when CEX_MARKETPLACE_SAFETY=1 each lane fetch routes
through cex_marketplace_safety (cache-check -> breaker -> pace -> record/store). A
cache HIT short-circuits to TIER 2 'cache' (zero browser contact -- the biggest
ban-risk reducer); a breaker-OPEN host SKIPS the browser tier (stops hammering a
host pushing back) and the router degrades to the next tier. With the flag
unset/0 the safety layer is a complete no-op -> the lane behaves byte-identically.

DEGRADE-NEVER + FAIL-OPEN + NEVER-FABRICATE (mirrors the existing lanes + the
ban-safety layer): EVERY tier is wrapped; a tier's exception / empty result is
recorded as that tier's failure reason and the router tries the next tier. resolve()
is TOTAL -- it NEVER raises and NEVER invents a listing (an empty corpus degrades to
the paste floor, exactly like the STORM merge). The injected clients are the test
seam (the real browser / firecrawl / API client never run under unit test).

Return shape (a typed dict -- never None):
  {
    "marketplace": str, "query": str,
    "winning_tier": str|None,   # 'official_api'|'real_browser'|'firecrawl_extract'|
                                # 'manual_paste'|None  (None only if even paste has no url)
    "result": {...}|None,       # the winning tier's payload (listings / detail / sentinel)
    "tier_failures": [ {"tier": str, "reason": str}, ... ],  # each tier that did NOT win
    "mock": bool,               # True when ANY injected (test) client served the win
    "search_url": str,          # the resolved marketplace search URL (stable, for paste)
  }

ASCII-only (.claude/rules/ascii-code-rule.md). NO secret is read/logged/stored (the
router holds NO credential -- the injected clients own their own keys, never logged).
This module COMPOSES the shipped seams; it modifies NONE of them.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

# Reuse the live resolver's PURE helpers (the marketplace target table, the search-URL
# builders, the slug, the official-API token resolver, the playwright scrape seam). The
# module is import-light (no driver/key/browser touched at import), so importing it here
# is cheap + offline-safe.
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_tool_resolver_live as _live  # type: ignore[import]

# Tier name constants (the winning_tier values + the tier_failures 'tier' field).
TIER_OFFICIAL_API = "official_api"
TIER_REAL_BROWSER = "real_browser"
TIER_FIRECRAWL_EXTRACT = "firecrawl_extract"
TIER_MANUAL_PASTE = "manual_paste"

# The fixed tier order (the codexa decision-tree order: structured API first, then the
# proven browser, then structured extraction, then the always-available human floor).
TIER_ORDER: Tuple[str, ...] = (
    TIER_OFFICIAL_API, TIER_REAL_BROWSER, TIER_FIRECRAWL_EXTRACT, TIER_MANUAL_PASTE,
)

# Marketplaces whose OFFICIAL search API is known-RESTRICTED for competitor search (the
# tier returns a clean 'restricted' result and the router falls through). Mercado Livre's
# public /sites/MLB/search returns 0 results even with a valid token (the documented
# restriction). Shopee/Amazon are NOT listed -> their official tier would attempt the
# injected api_client (a real client slots in later; in tests it is mocked).
_OFFICIAL_API_RESTRICTED = {"mercadolivre", "mercado_livre", "meli", "ml"}

# Shopee marketplace keys (the resolve_detail Shopee branch routes these to the internal-API
# adapter cex_marketplace_detail_shopee.fetch_shopee_detail -- W5). Any normalized key here is
# treated as Shopee in the DETAIL pass only (the search pass is unchanged).
_SHOPEE_KEYS = {"shopee", "shopee_br", "shopee.com.br"}

# Default listings cap a browser/api tier returns (mirrors the playwright lane default).
_DEFAULT_LIMIT = 20


# --------------------------------------------------------------------------- #
# The public resolver.
# --------------------------------------------------------------------------- #
def resolve(
    marketplace: str,
    query_or_url: str,
    *,
    limit: int = _DEFAULT_LIMIT,
    api_client: Optional[Callable[..., Any]] = None,
    browser_scraper: Optional[Callable[..., Any]] = None,
    firecrawl_extractor: Optional[Callable[..., Any]] = None,
    safety: Optional[Any] = None,
) -> Dict[str, Any]:
    """Resolve (marketplace, query_or_url) by trying the 4 tiers IN ORDER; return the FIRST
    success + the full failure trail. TOTAL: NEVER raises, NEVER fabricates.

    Injected seams (ALL optional -> the real impl is used when None; tests inject fakes so
    NO real browser / network / API call ever runs offline):
      api_client(marketplace, query, *, limit) -> {"status": str, "listings": [...]} | None
          The marketplace OFFICIAL API. status 'restricted'/'unavailable'/'empty' -> the
          tier did not win; status 'ok' + non-empty listings -> it wins. For a RESTRICTED
          marketplace (ML) with NO injected client, the tier short-circuits to 'restricted'
          WITHOUT a call (the documented behavior).
      browser_scraper(query, *, marketplace, limit) -> {"status": str, "listings": [...]}
          The real-browser lane (defaults to cex_playwright_scrape.scrape). 'ok' wins.
      firecrawl_extractor(url|query, marketplace) -> {"status"/"listings"/"detail" ...}
          The firecrawl /v1/extract lane (defaults to the detail-extract module). A
          non-empty structured payload wins.
      safety -- the ban-safety module (defaults to cex_marketplace_safety when importable).
          When its flag is on, the browser/extract fetches route through cache/breaker/pace.

    The MANUAL_PASTE tier always 'wins' last (it returns a needs_paste sentinel with the
    search URL) UNLESS there is no URL to paste (then winning_tier is None -- the honest
    'nothing to do' result)."""
    mp = _norm_marketplace(marketplace)
    q = _s(query_or_url)
    search_url = _resolve_search_url(mp, q)
    failures: List[Dict[str, str]] = []
    mock_used = False

    sf = safety if safety is not None else _safety_module()

    # TIER 1 -- OFFICIAL_API.
    won, payload, reason, mock = _try_official_api(mp, q, limit, api_client)
    mock_used = mock_used or mock
    if won:
        return _result(mp, q, TIER_OFFICIAL_API, payload, failures, mock_used, search_url)
    failures.append({"tier": TIER_OFFICIAL_API, "reason": reason})

    # TIER 2 -- REAL_BROWSER (safety-aware: cache hit short-circuits; breaker-open skips).
    won, payload, reason, mock = _try_real_browser(mp, q, limit, search_url, browser_scraper, sf)
    mock_used = mock_used or mock
    if won:
        return _result(mp, q, TIER_REAL_BROWSER, payload, failures, mock_used, search_url)
    failures.append({"tier": TIER_REAL_BROWSER, "reason": reason})

    # TIER 3 -- FIRECRAWL_EXTRACT (safety-aware on the fetch).
    won, payload, reason, mock = _try_firecrawl_extract(mp, q, search_url, firecrawl_extractor, sf)
    mock_used = mock_used or mock
    if won:
        return _result(mp, q, TIER_FIRECRAWL_EXTRACT, payload, failures, mock_used, search_url)
    failures.append({"tier": TIER_FIRECRAWL_EXTRACT, "reason": reason})

    # TIER 4 -- MANUAL_PASTE (the always-available floor). NEVER fabricates a listing.
    won, payload, reason = _try_manual_paste(mp, q, search_url)
    if won:
        return _result(mp, q, TIER_MANUAL_PASTE, payload, failures, mock_used, search_url)
    failures.append({"tier": TIER_MANUAL_PASTE, "reason": reason})

    # No tier produced anything actionable (only when there is no URL even to paste).
    return _result(mp, q, None, None, failures, mock_used, search_url)


# --------------------------------------------------------------------------- #
# The DETAIL resolver (pass=detail) -- spec_extraction_depth_v1 S2/S3 + S7. A PARALLEL entry to
# resolve(): it takes a listing URL / item id (NOT a search query) and routes TIER 1 by
# marketplace: Mercado Livre -> the OFFICIAL_API DETAIL lane (price_to_win + products/items +
# items + users in cex_marketplace_detail_meli); Shopee -> the INTERNAL-API DETAIL lane (the v4
# item/get endpoint in cex_marketplace_detail_shopee, W5 -- token-gated, self-reports 'unavailable'
# with no Shopee browser-session token). Either runs BEFORE any browser/firecrawl tier. It keeps
# the SAME degrade-never contract (typed dict, never raises, never fabricates, records per-tier
# failures, firecrawl detail-extract floor). The shipped resolve() (pass=search) is UNCHANGED.
# --------------------------------------------------------------------------- #
def resolve_detail(
    marketplace: str,
    item_id_or_url: str,
    *,
    meli_detail_fetcher: Optional[Callable[..., Any]] = None,
    shopee_detail_fetcher: Optional[Callable[..., Any]] = None,
    firecrawl_extractor: Optional[Callable[..., Any]] = None,
    safety: Optional[Any] = None,
) -> Dict[str, Any]:
    """Resolve the CATALOG/detail record for ONE listing (pass=detail). TOTAL: NEVER raises,
    NEVER fabricates.

    For Mercado Livre, TIER 1 is the OFFICIAL_API DETAIL lane (cex_marketplace_detail_meli.
    fetch_detail -- E1/E2/E3/E4). For Shopee, TIER 1 is the INTERNAL-API DETAIL lane
    (cex_marketplace_detail_shopee.fetch_shopee_detail -- the v4 item/get endpoint, W5); a record
    with status='ok' + at least one captured field wins, while a token-less 'unavailable' record
    (no Shopee browser-session token) is NOT a win and degrades honestly. For other marketplaces
    (or when the chosen lane yields nothing usable), it degrades to TIER 3 firecrawl /v1/extract on
    the listing URL (cex_marketplace_detail_extract). The MANUAL_PASTE floor carries the listing
    URL when every tier degrades.

    Injected seams (ALL optional -> the real impl is used when None; tests inject fakes so NO
    real network call ever runs offline):
      meli_detail_fetcher(item_id_or_url, token=None) -> {...detail record...}
          The ML official detail client (defaults to cex_marketplace_detail_meli.fetch_detail).
          A record with at least one captured field (buy_box/num_sellers/sold/date/etc) wins.
      shopee_detail_fetcher(item_id_or_url, session=None) -> {...detail record...}
          The Shopee internal-API client (defaults to cex_marketplace_detail_shopee.
          fetch_shopee_detail). A status='ok' record with signal wins; a status='unavailable'
          (token-less) record degrades (NEVER fabricates).
      firecrawl_extractor(url, marketplace) -> {"status"/"listings"/"detail" ...}
          The firecrawl /v1/extract detail lane (defaults to the detail-extract module).
      safety -- the ban-safety module (defaults to cex_marketplace_safety when importable).

    Return shape (mirrors resolve(), with pass='detail'):
      {
        "marketplace": str, "query": str (the item id/url), "pass": "detail",
        "winning_tier": 'official_api'|'firecrawl_extract'|'manual_paste'|None,
        "result": {...detail record...}|None,
        "tier_failures": [ {"tier": str, "reason": str}, ... ],
        "mock": bool, "search_url": str (the listing URL),
      }
    """
    mp = _norm_marketplace(marketplace)
    q = _s(item_id_or_url)
    # For detail, the 'search_url' is the listing URL itself (a URL passes through verbatim; a bare
    # id has no canonical URL until resolved -> the ML lane resolves it internally).
    listing_url = q if q.lower().startswith("http") else ""
    failures: List[Dict[str, str]] = []
    mock_used = False
    sf = safety if safety is not None else _safety_module()

    # TIER 1 -- OFFICIAL_API DETAIL. Shopee routes to its INTERNAL-API lane (W5); all other
    # marketplaces route to the ML official lane (ML-only today -> non-ML, non-Shopee yields a clean
    # 'no detail api' failure). A test-injected shopee fetcher always uses the Shopee branch.
    if mp in _SHOPEE_KEYS or shopee_detail_fetcher is not None:
        won, payload, reason, mock = _try_shopee_detail(mp, q, shopee_detail_fetcher)
    else:
        won, payload, reason, mock = _try_meli_detail(mp, q, meli_detail_fetcher)
    mock_used = mock_used or mock
    if won:
        return _detail_result(mp, q, TIER_OFFICIAL_API, payload, failures, mock_used, listing_url)
    failures.append({"tier": TIER_OFFICIAL_API, "reason": reason})

    # TIER 3 -- FIRECRAWL_EXTRACT on the listing URL (the DOM detail fallback; safety-aware).
    won, payload, reason, mock = _try_firecrawl_extract(mp, q, listing_url, firecrawl_extractor, sf)
    mock_used = mock_used or mock
    if won:
        return _detail_result(mp, q, TIER_FIRECRAWL_EXTRACT, payload, failures, mock_used, listing_url)
    failures.append({"tier": TIER_FIRECRAWL_EXTRACT, "reason": reason})

    # TIER 4 -- MANUAL_PASTE floor (carries the listing URL when present). NEVER fabricates.
    won, payload, reason = _try_manual_paste(mp, q, listing_url)
    if won:
        return _detail_result(mp, q, TIER_MANUAL_PASTE, payload, failures, mock_used, listing_url)
    failures.append({"tier": TIER_MANUAL_PASTE, "reason": reason})

    return _detail_result(mp, q, None, None, failures, mock_used, listing_url)


def _try_meli_detail(
    marketplace: str, item_id_or_url: str, fetcher: Optional[Callable[..., Any]],
) -> Tuple[bool, Optional[Dict[str, Any]], str, bool]:
    """Try the Mercado Livre OFFICIAL detail lane. Returns (won, payload, failure_reason,
    mock_used). For a non-ML marketplace with NO injected fetcher: short-circuit to a clean
    'no detail api' failure WITHOUT a call (only ML has an official detail client today). When a
    fetcher IS injected (a test fake), it is used for ANY marketplace. DEGRADE-NEVER: an exception
    -> a recorded failure (never raises). NEVER fabricates -- an all-null record (no captured
    field) is NOT a win (it degrades to the next tier)."""
    injected = fetcher is not None
    if fetcher is None:
        if marketplace not in _OFFICIAL_API_RESTRICTED:
            return (False, None, "no official detail api client for this marketplace", False)
        fetcher = _default_meli_detail_fetcher
    try:
        record = fetcher(item_id_or_url)
    except Exception as exc:
        return (False, None, "meli detail error: %s" % type(exc).__name__, injected)
    if not isinstance(record, Mapping):
        return (False, None, "meli detail returned no record", injected)
    if _detail_has_signal(record):
        payload = {"source": TIER_OFFICIAL_API, "detail": dict(record)}
        return (True, payload, "", injected)
    # The lane RAN but captured nothing real (bad token / unresolvable id / all 4xx). Surface the
    # honest reason from the record's endpoint_status so the failure trail is diagnosable. NEVER
    # treats an all-null record as a win.
    reason = _detail_failure_reason(record)
    return (False, None, "meli detail captured no fields (%s)" % reason, injected)


def _default_meli_detail_fetcher(item_id_or_url: str) -> Dict[str, Any]:
    """The ML official detail client (cex_marketplace_detail_meli.fetch_detail). Imported lazily
    (offline-import friendly). TOTAL (fetch_detail never raises / never fabricates)."""
    import cex_marketplace_detail_meli as _dm  # type: ignore[import]

    return _dm.fetch_detail(item_id_or_url)


def _try_shopee_detail(
    marketplace: str, item_id_or_url: str, fetcher: Optional[Callable[..., Any]],
) -> Tuple[bool, Optional[Dict[str, Any]], str, bool]:
    """Try the Shopee INTERNAL-API detail lane (W5 -- cex_marketplace_detail_shopee.
    fetch_shopee_detail). Returns (won, payload, failure_reason, mock_used).

    DEGRADE-NEVER + NEVER-FABRICATE:
      * an exception -> a recorded failure (the lane is TOTAL, but be defensive at the seam).
      * a record with status != 'ok' (the token-less 'unavailable' path -- no Shopee browser-session
        token) is NOT a win: it degrades with an honest reason carrying the record's `reason`.
      * a status='ok' record with NO captured signal also degrades (never fabricates a win).
    When a fetcher is INJECTED (a test fake), it is used regardless of marketplace; with NO injected
    fetcher the default Shopee client is used (offline that self-reports 'unavailable')."""
    injected = fetcher is not None
    if fetcher is None:
        fetcher = _default_shopee_detail_fetcher
    try:
        record = fetcher(item_id_or_url)
    except Exception as exc:
        return (False, None, "shopee detail error: %s" % type(exc).__name__, injected)
    if not isinstance(record, Mapping):
        return (False, None, "shopee detail returned no record", injected)
    status = record.get("status")
    if status != "ok":
        # The token-less / blocked / unresolvable path -- surface the honest reason (e.g.
        # 'shopee_session_token_required'). NEVER a win, NEVER a fabricated field.
        reason = record.get("reason") or _detail_failure_reason(record)
        return (False, None, "shopee detail unavailable (%s)" % reason, injected)
    if _detail_has_signal(record):
        payload = {"source": TIER_OFFICIAL_API, "detail": dict(record)}
        return (True, payload, "", injected)
    return (False, None, "shopee detail ok but captured no fields", injected)


def _default_shopee_detail_fetcher(item_id_or_url: str) -> Dict[str, Any]:
    """The Shopee internal-API detail client (cex_marketplace_detail_shopee.fetch_shopee_detail).
    Imported lazily (offline-import friendly). Called with NO session here -> offline / token-less
    it self-reports status='unavailable' (NEVER fabricates). A real run injects a session-carrying
    fetcher built from the founder's logged-in Shopee tab."""
    import cex_marketplace_detail_shopee as _ds  # type: ignore[import]

    return _ds.fetch_shopee_detail(item_id_or_url)


# The detail fields that count as 'captured real signal' (any one present -> the lane won). A
# record with ONLY null/empty data fields is NOT a win (it degrades). item_id / mock / provenance
# are NOT signal (item_id is just the echoed input; mock is always False). Covers BOTH the ML
# detail record (catalog/buy_box/sold_exact/...) and the Shopee detail record (sold_historical/
# rating_total/stock/... -- W5); shared field names (price/price_original/discount_pct) serve both.
_DETAIL_SIGNAL_FIELDS = (
    # ML (cex_marketplace_detail_meli) fields.
    "catalog_product_id", "buy_box_winner", "buy_box_status", "num_sellers",
    "sold_exact", "sold_bucket", "date_created", "logistic_type",
    "installments", "seller_reputation", "seller_power_status", "seller_sales_total",
    # Shopee (cex_marketplace_detail_shopee) fields.
    "sold_historical", "sold_recent", "stock", "rating_total", "rating_star",
    "listing_age_days",
    # Shared.
    "price", "price_original",
)


def _detail_has_signal(record: Mapping[str, Any]) -> bool:
    """True iff the detail record captured at least one real data field (not just the echoed
    item_id / provenance). PURE + TOTAL. NEVER counts a null/empty field as signal."""
    for name in _DETAIL_SIGNAL_FIELDS:
        v = record.get(name)
        if v is None:
            continue
        if isinstance(v, str) and not v.strip():
            continue
        if isinstance(v, (list, dict)) and not v:
            continue
        return True
    # Non-empty variations/attributes/sellers also count as captured signal.
    for name in ("variations", "attributes", "sellers"):
        v = record.get(name)
        if isinstance(v, (list, dict)) and v:
            return True
    return False


def _detail_failure_reason(record: Mapping[str, Any]) -> str:
    """Build a short honest reason from a captured-nothing detail record's endpoint_status (e.g.
    'items=failed: HTTPError on GET /items/MLBx'). TOTAL -> 'all endpoints null'."""
    es = record.get("endpoint_status")
    if isinstance(es, Mapping) and es:
        parts = ["%s=%s" % (k, v) for k, v in es.items()]
        return "; ".join(parts)[:300]
    return "all endpoints null"


def _detail_result(
    marketplace: str, query: str, winning_tier: Optional[str], result: Optional[Dict[str, Any]],
    failures: List[Dict[str, str]], mock_used: bool, listing_url: str,
) -> Dict[str, Any]:
    """Assemble the canonical detail result dict (mirrors _result, with pass='detail'). NEVER None."""
    return {
        "marketplace": marketplace,
        "query": query,
        "pass": "detail",
        "winning_tier": winning_tier,
        "result": result,
        "tier_failures": list(failures),
        "mock": bool(mock_used),
        "search_url": listing_url,
    }


# --------------------------------------------------------------------------- #
# TIER 1 -- OFFICIAL_API.
# --------------------------------------------------------------------------- #
def _try_official_api(
    marketplace: str, query: str, limit: int, api_client: Optional[Callable[..., Any]],
) -> Tuple[bool, Optional[Dict[str, Any]], str, bool]:
    """Try the marketplace OFFICIAL API. Returns (won, payload, failure_reason, mock_used).

    For a RESTRICTED marketplace (ML) with NO injected client: short-circuit to a clean
    'restricted' failure WITHOUT a call (the documented ML /search restriction). When an
    api_client IS injected (a test fake OR a future Shopee/Amazon client), call it and let
    its result decide. DEGRADE-NEVER: an exception -> a recorded failure (never raises)."""
    if api_client is None:
        if marketplace in _OFFICIAL_API_RESTRICTED:
            return (False, None, "restricted (official /search returns 0 for competitor search)", False)
        return (False, None, "no official api client wired for this marketplace", False)
    try:
        raw = api_client(marketplace, query, limit=limit)
    except Exception as exc:
        return (False, None, "official api error: %s" % type(exc).__name__, True)
    listings, status = _listings_and_status(raw)
    if status == "restricted":
        return (False, None, "restricted (official api reported restricted)", True)
    if listings:
        return (True, {"source": TIER_OFFICIAL_API, "listings": listings, "count": len(listings)}, "", True)
    return (False, None, "official api returned no listings (status=%s)" % (status or "empty"), True)


# --------------------------------------------------------------------------- #
# TIER 2 -- REAL_BROWSER (delegates to cex_playwright_scrape; safety-aware).
# --------------------------------------------------------------------------- #
def _try_real_browser(
    marketplace: str, query: str, limit: int, search_url: str,
    browser_scraper: Optional[Callable[..., Any]], safety: Optional[Any],
) -> Tuple[bool, Optional[Dict[str, Any]], str, bool]:
    """Try the real-browser lane. Safety-aware: a fresh cache HIT short-circuits to a win
    (zero browser contact); a breaker-OPEN host SKIPS the fetch (degrade to the next tier).
    Returns (won, payload, failure_reason, mock_used). DEGRADE-NEVER (never raises)."""
    # Safety pre-gate (cache hit / breaker skip). FAIL-OPEN: any error -> proceed to fetch.
    gate = _safety_before(safety, marketplace, query, search_url)
    if gate.get("action") == "serve_cache":
        cached = gate.get("listings") or []
        if cached:
            return (True, {"source": "cache", "tier": TIER_REAL_BROWSER, "listings": cached,
                           "count": len(cached)}, "", False)
        # An empty cached payload is not a win -> fall through to the live fetch.
    elif gate.get("action") == "skip":
        return (False, None, "skipped (circuit breaker open for host)", False)

    injected = browser_scraper is not None
    scraper = browser_scraper if injected else _default_browser_scraper
    try:
        raw = scraper(query, marketplace=marketplace, limit=limit)
    except Exception as exc:
        _safety_after(safety, marketplace, query, search_url, listings=[], status="unavailable")
        return (False, None, "real browser error: %s" % type(exc).__name__, injected)
    listings, status = _listings_and_status(raw)
    url = _result_url(raw) or search_url
    _safety_after(safety, marketplace, query, url, listings=listings,
                  status=("ok" if listings else (status or "empty")))
    if listings:
        return (True, {"source": TIER_REAL_BROWSER, "listings": listings, "count": len(listings),
                       "url": url}, "", injected)
    if status == "unavailable":
        return (False, None, "real browser unavailable (no browser / driver)", injected)
    return (False, None, "real browser reached but empty (anti-bot / no grid)", injected)


def _default_browser_scraper(query: str, *, marketplace: str, limit: int) -> Dict[str, Any]:
    """The real-browser lane (cex_playwright_scrape.scrape) -- drives a real Chrome on its own
    main thread. Imported lazily (offline-import friendly). DEGRADE-NEVER (scrape() is TOTAL)."""
    import cex_playwright_scrape as _cps  # type: ignore[import]

    return _cps.scrape(query, marketplace=marketplace, limit=limit)


# --------------------------------------------------------------------------- #
# TIER 3 -- FIRECRAWL_EXTRACT (delegates to cex_marketplace_detail_extract; safety-aware).
# --------------------------------------------------------------------------- #
def _try_firecrawl_extract(
    marketplace: str, query: str, search_url: str,
    firecrawl_extractor: Optional[Callable[..., Any]], safety: Optional[Any],
) -> Tuple[bool, Optional[Dict[str, Any]], str, bool]:
    """Try structured extraction via firecrawl /v1/extract on the search URL. A non-empty
    structured payload (listings OR a detail dict) wins. Safety-aware on the fetch.
    Returns (won, payload, failure_reason, mock_used). DEGRADE-NEVER (never raises)."""
    if not search_url:
        return (False, None, "no url to extract", False)
    gate = _safety_before(safety, marketplace, query, search_url)
    if gate.get("action") == "skip":
        return (False, None, "skipped (circuit breaker open for host)", False)

    injected = firecrawl_extractor is not None
    extractor = firecrawl_extractor if injected else _default_firecrawl_extractor
    try:
        raw = extractor(search_url, marketplace)
    except Exception as exc:
        _safety_after(safety, marketplace, query, search_url, listings=[], status="unavailable")
        return (False, None, "firecrawl extract error: %s" % type(exc).__name__, injected)
    listings, status = _listings_and_status(raw)
    detail = raw.get("detail") if isinstance(raw, Mapping) else None
    payload_records = listings if listings else ([detail] if isinstance(detail, Mapping) and detail else [])
    _safety_after(safety, marketplace, query, search_url, listings=payload_records,
                  status=("ok" if payload_records else (status or "empty")))
    if listings:
        return (True, {"source": TIER_FIRECRAWL_EXTRACT, "listings": listings,
                       "count": len(listings)}, "", injected)
    if isinstance(detail, Mapping) and detail:
        return (True, {"source": TIER_FIRECRAWL_EXTRACT, "detail": detail}, "", injected)
    return (False, None, "firecrawl extract returned nothing usable (status=%s)" % (status or "empty"), injected)


def _default_firecrawl_extractor(url: str, marketplace: str) -> Dict[str, Any]:
    """The firecrawl extract lane (cex_marketplace_detail_extract.extract_detail). Imported
    lazily (offline-import friendly). Returns the structured detail dict the module produces.
    DEGRADE-NEVER (the detail module is TOTAL)."""
    import cex_marketplace_detail_extract as _de  # type: ignore[import]

    return _de.extract_detail(url, marketplace=marketplace)


# --------------------------------------------------------------------------- #
# TIER 4 -- MANUAL_PASTE (the always-available human floor).
# --------------------------------------------------------------------------- #
def _try_manual_paste(
    marketplace: str, query: str, search_url: str,
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """The paste floor: return a needs_paste SENTINEL with the search URL so a human can open
    the page + paste it. ALWAYS wins WHEN there is a URL (mirrors codexa's always-free TIER 1
    paste baseline). NEVER fabricates a listing -- it carries NO data, only the URL + a note."""
    url = search_url or _resolve_search_url(marketplace, query)
    if not url:
        return (False, None, "no search url to paste")
    sentinel = {
        "source": TIER_MANUAL_PASTE,
        "needs_paste": True,
        "url": url,
        "marketplace": marketplace,
        "query": query,
        "instruction": (
            "All automated tiers degraded. Open the URL in a browser and paste the visible "
            "listings so the engine can read them. No listing was fabricated."
        ),
    }
    return (True, sentinel, "")


# --------------------------------------------------------------------------- #
# Safety-layer glue (FAIL-OPEN; a no-op when the flag is off / the module is absent).
# --------------------------------------------------------------------------- #
def _safety_module() -> Optional[Any]:
    """Return cex_marketplace_safety, or None when it cannot be imported (DEGRADE-NEVER: the
    tiers then fetch exactly as before). No network/secret touched at import."""
    try:
        import cex_marketplace_safety as _ms  # type: ignore[import]
        return _ms
    except Exception:
        return None


def _safety_before(safety: Optional[Any], marketplace: str, query: str, url: str) -> Dict[str, Any]:
    """Call safety.before_fetch -> a decision dict. FAIL-OPEN: a missing/disabled module OR any
    error -> {'action': 'fetch'} (proceed). NEVER fabricates -- 'serve_cache' carries a REAL
    prior result; 'skip' carries no data."""
    if safety is None:
        return {"action": "fetch"}
    try:
        if not safety.is_enabled():
            return {"action": "fetch"}
        decision = safety.before_fetch(marketplace, query, url)
        return decision if isinstance(decision, dict) else {"action": "fetch"}
    except Exception:
        return {"action": "fetch"}


def _safety_after(
    safety: Optional[Any], marketplace: str, query: str, url: str, *,
    listings: List[Dict[str, Any]], status: str,
) -> None:
    """Feed the fetch outcome to the breaker + cache (safety.after_fetch). FAIL-OPEN: a missing/
    disabled module OR any error is swallowed (a safety bug never affects the tier result)."""
    if safety is None:
        return
    try:
        if not safety.is_enabled():
            return
        safety.after_fetch(marketplace, query, url, listings=listings, status=status)
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# PURE / TOTAL helpers.
# --------------------------------------------------------------------------- #
def _result(
    marketplace: str, query: str, winning_tier: Optional[str], result: Optional[Dict[str, Any]],
    failures: List[Dict[str, str]], mock_used: bool, search_url: str,
) -> Dict[str, Any]:
    """Assemble the canonical typed result dict. NEVER None."""
    return {
        "marketplace": marketplace,
        "query": query,
        "winning_tier": winning_tier,
        "result": result,
        "tier_failures": list(failures),
        "mock": bool(mock_used),
        "search_url": search_url,
    }


def _listings_and_status(raw: Any) -> Tuple[List[Dict[str, Any]], str]:
    """Pull (listings, status) from a lane result. Tolerates the lane shapes: a dict with
    'listings' + optional 'status', a bare list of listings, or anything else (-> [], '').
    A listing must be a mapping (a non-mapping item is dropped -- NEVER fabricated). TOTAL."""
    if isinstance(raw, Mapping):
        status = raw.get("status") if isinstance(raw.get("status"), str) else ""
        items = raw.get("listings")
        listings = [it for it in items if isinstance(it, Mapping)] if isinstance(items, list) else []
        return listings, status
    if isinstance(raw, list):
        return [it for it in raw if isinstance(it, Mapping)], ""
    return [], ""


def _result_url(raw: Any) -> str:
    """The 'url' a lane result reports (the page it actually hit). TOTAL -> ''."""
    if isinstance(raw, Mapping):
        u = raw.get("url")
        if isinstance(u, str) and u.strip():
            return u.strip()
    return ""


def _norm_marketplace(marketplace: str) -> str:
    """Normalize the marketplace key: lowercase + strip; default to the proven ML lane key."""
    name = _s(marketplace).lower()
    return name or _live._DEFAULT_PLAYWRIGHT_MARKETPLACE


def _resolve_search_url(marketplace: str, query_or_url: str) -> str:
    """Build the marketplace search-results URL via the SAME builder the playwright lane uses
    (so the paste URL matches what a real fetch would hit). A query that already IS a URL is
    used verbatim. TOTAL -> '' when nothing can be built."""
    q = _s(query_or_url)
    if not q:
        return ""
    try:
        target = _live._resolve_playwright_target(marketplace)
        return _live._playwright_search_url(target, q)
    except Exception:
        return ""


def _s(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


__all__ = [
    "resolve",
    "resolve_detail",
    "TIER_ORDER",
    "TIER_OFFICIAL_API",
    "TIER_REAL_BROWSER",
    "TIER_FIRECRAWL_EXTRACT",
    "TIER_MANUAL_PASTE",
]


# --------------------------------------------------------------------------- #
# CLI -- a credential-free dry inspection (prints the tier order + resolved URL; the live
# tiers are NOT run here -- a real run goes through the STORM engine / the orchestrator).
# --------------------------------------------------------------------------- #
def _main(argv: List[str]) -> int:
    if not argv:
        print("CEXAI marketplace tier-router. Tier order (codexa-cloned):")
        for i, t in enumerate(TIER_ORDER, 1):
            print("  TIER %d  %s" % (i, t))
        print("Usage (dry URL resolve): python _tools/cex_marketplace_tier_router.py "
              "<marketplace> <query>")
        print("Programmatic: import cex_marketplace_tier_router as r; "
              "r.resolve('mercadolivre', 'comedouro gatos', api_client=..., browser_scraper=...)")
        return 0
    marketplace = argv[0]
    query = " ".join(argv[1:]).strip()
    url = _resolve_search_url(_norm_marketplace(marketplace), query)
    print("marketplace : %s" % _norm_marketplace(marketplace))
    print("query       : %s" % query)
    print("search_url  : %s" % (url or "(none)"))
    print("tier_order  : %s" % ", ".join(TIER_ORDER))
    print("(dry: no live tier executed -- inject clients via resolve() for a real run.)")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
