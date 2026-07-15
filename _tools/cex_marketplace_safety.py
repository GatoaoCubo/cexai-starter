#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI Marketplace Ban-Safety layer (kind: backpressure_policy, P09 -- composed, no new kind).

THE GOOD-CITIZEN layer the marketplace lanes (playwright / firecrawl-vision) call. It exists to
PROTECT THE TENANT'S MARKETPLACE ACCOUNT while reading STRICTLY LEGITIMATE public marketplace data
(the SAME search grid any shopper loads -- it exploits nothing, bypasses no auth, reads no private
data). It does NOT make the scrape "sneakier"; it makes CEXAI a polite, rate-respecting visitor so
the account is never flagged for hammering. Four cooperating mechanisms:

  1. PER-DOMAIN PACING (copy the cex_ratelimit_guard rolling-window posture): a minimum interval
     between hits to the SAME marketplace host (default 1.5s + jitter). The biggest "don't get the
     account flagged" lever after the cache. Rolling-window timestamps per host; advisory + bounded.
  2. URL-SCRAPE CACHE (copy the cex_prompt_cache content-addressed posture + the codexa-v2
     p10_pc_url_scrape_cache spec): content-addressed by SHA-256 of (marketplace, normalized-query)
     -> the listings result, TTL 3600s, LRU eviction (max 50 entries). A REPEAT query serves from
     cache with ZERO fetch -- the single biggest ban-risk reducer (you cannot get flagged for a
     request you never send). JSON-per-entity under .cex/cache/marketplace_scrape/.
  3. PER-DOMAIN CIRCUIT BREAKER: on repeated BLOCK signals from a host (empty result / 403 /
     captcha-marker), OPEN that domain for a cooldown so CEXAI STOPS hammering a host that is already
     pushing back. Half-open after the cooldown (one trial). The defensive "back off, don't escalate"
     reflex that keeps a soft block from becoming a hard ban.
  4. ROBOTS.TXT / CRAWL-DELAY AWARENESS (good citizen): fetch + cache a host's robots.txt and respect
     its Crawl-delay (raises the effective pacing interval when the host asks for more). Best-effort;
     a missing/!200 robots.txt simply means "no extra delay requested".

SAFETY CONTRACT (this feeds the load-bearing live-fetch path):
  - FAIL-OPEN / DEGRADE-NEVER: ANY error inside ANY mechanism resolves to "proceed with the legit
    fetch". A safety-layer bug must NEVER block a legitimate public-data read. Every public function
    is TOTAL (wrapped) and returns a permissive default on failure.
  - NEVER FABRICATE (mirrors p11_gr_anti_hallucination_pesquisa + the existing lanes): the cache only
    ever stores/serves a REAL prior result; on a block it returns an 'unavailable' SKIP, never an
    invented listing. The breaker only SKIPS; it never substitutes data.
  - Flag-gated, DEFAULT-OFF (zero-regression posture, mirrors cex_ratelimit_guard / cex_reuse_gate /
    thin-boot): the lanes wire through this ONLY when CEX_MARKETPLACE_SAFETY == '1'. With the flag
    unset/0 the layer is a COMPLETE NO-OP (cache miss + pace 0 + breaker always-closed + no robots
    fetch) so the lane's fetch behavior is byte-identical to the pre-safety path. The live smoke
    (N07) sets CEX_MARKETPLACE_SAFETY=1 to engage the good-citizen layer for a real run. This OFF
    default is deliberate: the on-disk URL cache is process-persistent, so turning it on globally
    would change repeat-query behavior across unrelated runs/tests -- opt-in keeps that explicit.

Determinism for unit tests: the wall clock is the module seam ``_clock`` (a callable -> float
seconds). A test injects a fake clock to assert pacing waits, TTL expiry, and breaker cooldown
WITHOUT real time. ``sleep`` is the seam ``_sleeper`` (default time.sleep) so a test asserts the
wait amount without actually sleeping. The robots fetch is the seam ``_robots_fetcher`` (default a
urllib GET) so a test injects a fake robots.txt with NO network.

ASCII-only (.claude/rules/ascii-code-rule.md). NO secret is read/stored/printed (public data only).
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Repo root + the cache dir (mirror cex_prompt_cache: JSON-per-entity under .cex/cache/<sub>/).
_REPO_ROOT = Path(__file__).resolve().parent.parent
_CACHE_DIR = _REPO_ROOT / ".cex" / "cache" / "marketplace_scrape"
_ROBOTS_CACHE_DIR = _REPO_ROOT / ".cex" / "cache" / "marketplace_robots"

# ---------------------------------------------------------------------------
# Tunables (overridable via env; conservative good-citizen defaults).
# ---------------------------------------------------------------------------
# Minimum interval between hits to the SAME marketplace host (seconds) + a jitter ceiling.
_DEFAULT_MIN_INTERVAL_S = 1.5
_DEFAULT_JITTER_S = 0.75
# URL-scrape cache: TTL (codexa-v2 p10_pc_url_scrape_cache spec = 3600s) + LRU cap (= 50 entries).
_DEFAULT_CACHE_TTL_S = 3600.0
_DEFAULT_CACHE_MAX_ENTRIES = 50
# Circuit breaker: open a host after N consecutive block signals; stay open for the cooldown.
_DEFAULT_BREAKER_THRESHOLD = 3
_DEFAULT_BREAKER_COOLDOWN_S = 300.0
# Pacing safety ceiling: never sleep longer than this for one hit (a runaway crawl-delay is capped).
_MAX_PACING_SLEEP_S = 30.0

# Block markers that count as a "host is pushing back" signal for the breaker / a cache-skip.
_BLOCK_MARKERS = (
    "captcha", "are you a robot", "verifica", "unusual traffic", "access denied",
    "forbidden", "blocked", "robot check", "challenge",
)

# Module seams (None -> use the real impl lazily). Tests inject deterministic versions.
_clock = None        # type: ignore[assignment]  # callable() -> float seconds
_sleeper = None      # type: ignore[assignment]  # callable(float) -> None
_rng = None          # type: ignore[assignment]  # random.Random-like (.uniform)
_robots_fetcher = None  # type: ignore[assignment]  # callable(robots_url) -> Optional[str]


# ---------------------------------------------------------------------------
# Seam accessors (TOTAL).
# ---------------------------------------------------------------------------
def _now() -> float:
    seam = globals().get("_clock")
    if seam is not None:
        try:
            return float(seam())
        except Exception:
            pass
    return time.time()


def _sleep(seconds: float) -> None:
    if seconds <= 0:
        return
    seam = globals().get("_sleeper")
    if seam is not None:
        try:
            seam(seconds)
            return
        except Exception:
            return
    try:
        time.sleep(seconds)
    except Exception:
        pass


def _jitter(ceiling: float) -> float:
    if ceiling <= 0:
        return 0.0
    seam = globals().get("_rng")
    try:
        if seam is not None:
            return float(seam.uniform(0.0, ceiling))
        import random
        return random.uniform(0.0, ceiling)
    except Exception:
        return 0.0


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def is_enabled() -> bool:
    """The flag gate. DEFAULT-OFF (zero-regression): the whole layer engages ONLY when
    CEX_MARKETPLACE_SAFETY == '1'. Unset/0 -> a complete no-op so the lane's fetch behavior is
    byte-identical to the pre-safety path (the on-disk cache is process-persistent, so opt-in keeps
    repeat-query behavior explicit). The live smoke sets the flag for a real good-citizen run."""
    return os.environ.get("CEX_MARKETPLACE_SAFETY", "0") == "1"


# ---------------------------------------------------------------------------
# Host + key helpers (PURE / TOTAL).
# ---------------------------------------------------------------------------
def _host_for(marketplace: str, url: str = "") -> str:
    """Resolve a stable per-DOMAIN key. Prefer the URL's netloc; else the marketplace slug. The
    breaker + pacing are keyed on this so all queries to one marketplace host share a budget. TOTAL
    -> '' only when there is nothing to key on (then the layer no-ops for that call)."""
    u = (url or "").strip()
    if u:
        try:
            netloc = urlparse(u).netloc.strip().lower()
            if netloc:
                # Collapse a 'lista.mercadolivre.com.br' / 'www....' to the registrable-ish host so
                # all ML subhosts share one budget (best-effort, not a PSL parse).
                parts = netloc.split(".")
                if len(parts) >= 3:
                    return ".".join(parts[-3:]) if parts[-2] in ("com", "co") else ".".join(parts[-2:])
                return netloc
        except Exception:
            pass
    return (marketplace or "").strip().lower()


def _normalize_query(query: str) -> str:
    """Normalize a query for the content-addressed cache key: lowercase + collapse whitespace. So
    'Comedouro  Gatos' and 'comedouro gatos' share a cache entry. TOTAL."""
    return " ".join(str(query or "").lower().split())


def cache_key(marketplace: str, query: str) -> str:
    """SHA-256 content-address of (marketplace, normalized-query) -- the cex_prompt_cache posture.
    Stable + collision-resistant; the on-disk filename. NEVER contains a secret (public inputs)."""
    norm = _normalize_query(query)
    blob = ("%s\x00%s" % ((marketplace or "").strip().lower(), norm)).encode("utf-8", "ignore")
    return hashlib.sha256(blob).hexdigest()


def _block_signal(listings: Optional[List[Any]], status: str = "", marker_text: str = "") -> bool:
    """Decide whether a fetch RESULT looks like the host pushed back (a block signal for the
    breaker + a reason to NOT cache). True when: status is a block status (403/429/captcha/empty),
    OR the marker text contains a known block phrase, OR (listings is an EMPTY list AND status
    signals empty/blocked). An ok result with listings is NEVER a block. TOTAL."""
    st = (status or "").strip().lower()
    if st in ("403", "429", "captcha", "blocked", "forbidden"):
        return True
    txt = (marker_text or "").lower()
    if any(m in txt for m in _BLOCK_MARKERS):
        return True
    if st in ("empty", "unavailable") and (not listings):
        return True
    return False


# ---------------------------------------------------------------------------
# (1) PER-DOMAIN PACING (in-process rolling state; advisory; copies the ratelimit-guard posture).
# ---------------------------------------------------------------------------
# host -> last-hit epoch seconds (the rolling-window state; in-process, per run).
_LAST_HIT: Dict[str, float] = {}


def _min_interval() -> float:
    return _env_float("CEX_MARKETPLACE_MIN_INTERVAL_S", _DEFAULT_MIN_INTERVAL_S)


def _jitter_ceiling() -> float:
    return _env_float("CEX_MARKETPLACE_JITTER_S", _DEFAULT_JITTER_S)


def pace(marketplace: str, url: str = "", crawl_delay: Optional[float] = None) -> float:
    """Enforce the minimum interval since the last hit to this host: SLEEP for the remaining time
    (+ a small jitter), then record the hit. Returns the seconds actually waited (0.0 when no wait
    was needed). The effective interval is max(configured min interval, the host's robots
    Crawl-delay) so a host that asks for more politeness gets it. FAIL-OPEN: any error -> 0.0 (no
    wait, proceed). Bounded by _MAX_PACING_SLEEP_S so a hostile crawl-delay never stalls a run."""
    try:
        if not is_enabled():
            return 0.0
        host = _host_for(marketplace, url)
        if not host:
            return 0.0
        base = _min_interval()
        if crawl_delay is not None and crawl_delay > base:
            base = crawl_delay
        now = _now()
        last = _LAST_HIT.get(host)
        wait = 0.0
        if last is not None:
            elapsed = now - last
            remaining = base - elapsed
            if remaining > 0:
                wait = remaining + _jitter(_jitter_ceiling())
        wait = max(0.0, min(wait, _MAX_PACING_SLEEP_S))
        if wait > 0:
            _sleep(wait)
        _LAST_HIT[host] = _now()
        return wait
    except Exception:
        return 0.0  # fail-open: never block a legit fetch on a pacing error.


def record_hit(marketplace: str, url: str = "") -> None:
    """Record a hit timestamp for a host WITHOUT pacing (used when the fetch happened outside pace,
    e.g. a cache-miss path that already paced). TOTAL."""
    try:
        host = _host_for(marketplace, url)
        if host:
            _LAST_HIT[host] = _now()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# (2) URL-SCRAPE CACHE (content-addressed JSON-per-entity; TTL + LRU; cex_prompt_cache posture).
# ---------------------------------------------------------------------------
def _cache_ttl() -> float:
    return _env_float("CEX_MARKETPLACE_CACHE_TTL_S", _DEFAULT_CACHE_TTL_S)


def _cache_max_entries() -> int:
    return _env_int("CEX_MARKETPLACE_CACHE_MAX", _DEFAULT_CACHE_MAX_ENTRIES)


def _cache_path(key: str) -> Path:
    return _CACHE_DIR / ("%s.json" % key)


def cache_get(marketplace: str, query: str) -> Optional[List[Dict[str, Any]]]:
    """Return the cached listings for (marketplace, query) when a FRESH entry exists, else None
    (miss). A repeat query served from here is ZERO fetch -- the biggest ban-risk reducer. Staleness:
    an entry older than the TTL is a miss (and is removed). FAIL-OPEN: any error -> None (treat as a
    miss -> the lane fetches normally). NEVER returns a fabricated listing -- only a real prior
    result. ``listings`` is the SAME STORM page shape the lanes produce."""
    try:
        if not is_enabled():
            return None
        path = _cache_path(cache_key(marketplace, query))
        if not path.exists():
            return None
        entry = json.loads(path.read_text(encoding="utf-8"))
        cached_at = float(entry.get("cached_at", 0) or 0)
        if (_now() - cached_at) > _cache_ttl():
            try:
                path.unlink()  # stale -> evict.
            except OSError:
                pass
            return None
        listings = entry.get("listings")
        if not isinstance(listings, list):
            return None
        # Touch atime-ish for LRU (rewrite last_access); best-effort, non-fatal.
        try:
            entry["last_access"] = _now()
            path.write_text(json.dumps(entry, ensure_ascii=True), encoding="utf-8")
        except Exception:
            pass
        return listings
    except Exception:
        return None  # fail-open: a cache read error must not block a fetch.


def cache_put(marketplace: str, query: str, listings: List[Dict[str, Any]]) -> bool:
    """Store a REAL fetch result for (marketplace, query). Only stores a NON-EMPTY result (an empty
    result is a block/no-grid signal -- caching it would suppress future legit retries, and it is
    NOT useful data). Enforces the LRU cap (evict oldest by last_access) AFTER writing. FAIL-OPEN:
    any error -> False (no cache, but the fetch result still flows). NEVER stores fabricated data."""
    try:
        if not is_enabled():
            return False
        if not isinstance(listings, list) or not listings:
            return False  # never cache an empty/blocked result (keeps legit retries open).
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = _cache_path(cache_key(marketplace, query))
        now = _now()
        entry = {
            "marketplace": (marketplace or "").strip().lower(),
            "query_normalized": _normalize_query(query),
            "cached_at": now,
            "last_access": now,
            "count": len(listings),
            "listings": listings,
        }
        path.write_text(json.dumps(entry, ensure_ascii=True), encoding="utf-8")
        _evict_lru()
        return True
    except Exception:
        return False  # fail-open: a cache write error must not break the lane.


def _evict_lru() -> None:
    """Keep at most _cache_max_entries() cache files; remove the oldest by last_access (LRU).
    TOTAL -> best-effort, never raises."""
    try:
        cap = _cache_max_entries()
        files = list(_CACHE_DIR.glob("*.json"))
        if len(files) <= cap:
            return
        scored: List[Tuple[float, Path]] = []
        for f in files:
            try:
                entry = json.loads(f.read_text(encoding="utf-8"))
                ts = float(entry.get("last_access", entry.get("cached_at", 0)) or 0)
            except Exception:
                ts = 0.0
            scored.append((ts, f))
        scored.sort(key=lambda x: x[0])  # oldest first.
        for _ts, f in scored[: len(files) - cap]:
            try:
                f.unlink()
            except OSError:
                pass
    except Exception:
        pass


def cache_clear() -> int:
    """Remove all marketplace-scrape cache files. Returns the count removed. TOTAL (for tests/ops)."""
    removed = 0
    try:
        for f in _CACHE_DIR.glob("*.json"):
            try:
                f.unlink()
                removed += 1
            except OSError:
                pass
    except Exception:
        pass
    return removed


# ---------------------------------------------------------------------------
# (3) PER-DOMAIN CIRCUIT BREAKER (in-process; open on repeated block signals; half-open after
#     cooldown). Defensive: it only SKIPS a host that is pushing back -- it never fabricates.
# ---------------------------------------------------------------------------
# host -> {"failures": int, "opened_at": float|None}
_BREAKER: Dict[str, Dict[str, Any]] = {}


def _breaker_threshold() -> int:
    return _env_int("CEX_MARKETPLACE_BREAKER_THRESHOLD", _DEFAULT_BREAKER_THRESHOLD)


def _breaker_cooldown() -> float:
    return _env_float("CEX_MARKETPLACE_BREAKER_COOLDOWN_S", _DEFAULT_BREAKER_COOLDOWN_S)


def breaker_is_open(marketplace: str, url: str = "") -> bool:
    """True when the host's breaker is OPEN (in cooldown) -> the lane should SKIP the fetch (and
    return an honest 'unavailable'). After the cooldown elapses the breaker goes HALF-OPEN (returns
    False -> one trial fetch allowed); a subsequent success resets it, a failure re-opens it.
    FAIL-OPEN: any error -> False (allow the fetch)."""
    try:
        if not is_enabled():
            return False
        host = _host_for(marketplace, url)
        if not host:
            return False
        state = _BREAKER.get(host)
        if not state:
            return False
        opened_at = state.get("opened_at")
        if opened_at is None:
            return False
        if (_now() - float(opened_at)) >= _breaker_cooldown():
            # Cooldown elapsed -> half-open: allow ONE trial (clear opened_at, keep failures so a
            # repeat block re-opens immediately).
            state["opened_at"] = None
            return False
        return True
    except Exception:
        return False  # fail-open.


def record_result(marketplace: str, url: str = "", *, blocked: bool) -> None:
    """Feed a fetch outcome to the breaker. A BLOCK increments the host's failure count and OPENS
    the breaker once it reaches the threshold. A SUCCESS resets the host (closes the breaker).
    TOTAL -> never raises (a breaker bug must not affect the lane)."""
    try:
        if not is_enabled():
            return
        host = _host_for(marketplace, url)
        if not host:
            return
        state = _BREAKER.setdefault(host, {"failures": 0, "opened_at": None})
        if not blocked:
            state["failures"] = 0
            state["opened_at"] = None
            return
        state["failures"] = int(state.get("failures", 0)) + 1
        if state["failures"] >= _breaker_threshold() and state.get("opened_at") is None:
            state["opened_at"] = _now()
    except Exception:
        pass


def breaker_reset(marketplace: str = "", url: str = "") -> None:
    """Reset the breaker for one host, or ALL hosts when neither marketplace nor url is given.
    TOTAL (for tests/ops)."""
    try:
        if not marketplace and not url:
            _BREAKER.clear()
            return
        host = _host_for(marketplace, url)
        if host in _BREAKER:
            del _BREAKER[host]
    except Exception:
        pass


# ---------------------------------------------------------------------------
# (4) ROBOTS.TXT / CRAWL-DELAY AWARENESS (good citizen; fetch + cache; respect crawl-delay).
# ---------------------------------------------------------------------------
# host -> {"fetched_at": float, "crawl_delay": float|None}
_ROBOTS_CACHE: Dict[str, Dict[str, Any]] = {}
_ROBOTS_TTL_S = 3600.0


def _robots_url_for(url: str) -> str:
    """Build the robots.txt URL for a page URL's origin. TOTAL -> '' when the URL has no scheme/host."""
    try:
        p = urlparse((url or "").strip())
        if p.scheme and p.netloc:
            return "%s://%s/robots.txt" % (p.scheme, p.netloc)
    except Exception:
        pass
    return ""


def _default_robots_fetch(robots_url: str) -> Optional[str]:
    """Default robots.txt fetch via urllib (short timeout). Returns the body text, or None on any
    error / non-200 (treated as 'no robots -> no extra delay'). NO secret involved (public file)."""
    try:
        import urllib.request

        req = urllib.request.Request(robots_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:  # nosec - public robots.txt
            if getattr(resp, "status", 200) and resp.status != 200:
                return None
            raw = resp.read()
            return raw.decode("utf-8", "ignore") if isinstance(raw, (bytes, bytearray)) else str(raw)
    except Exception:
        return None


def _parse_crawl_delay(robots_text: str) -> Optional[float]:
    """Parse the most permissive applicable Crawl-delay from robots.txt. Simplification (good
    citizen, not a full robots engine): scan all 'Crawl-delay:' directives and take the MINIMUM
    positive value (respect the politest stated delay that applies broadly). TOTAL -> None when none
    is declared / unparseable."""
    if not robots_text:
        return None
    delays: List[float] = []
    for line in robots_text.splitlines():
        s = line.strip().lower()
        if s.startswith("crawl-delay:"):
            val = s.split(":", 1)[1].strip()
            try:
                d = float(val)
                if d > 0:
                    delays.append(d)
            except ValueError:
                continue
    if not delays:
        return None
    return min(delays)


def crawl_delay_for(url: str) -> Optional[float]:
    """Return the host's robots.txt Crawl-delay (seconds) when declared, else None. Fetches + caches
    robots.txt per host (TTL 1h) via the _robots_fetcher seam. FAIL-OPEN: any error -> None (the
    pacing layer then uses just its configured min interval). The fetch is best-effort + cached so it
    adds at most one extra request per host per hour."""
    try:
        if not is_enabled():
            return None
        host = _host_for("", url)
        if not host:
            return None
        state = _ROBOTS_CACHE.get(host)
        now = _now()
        if state is not None and (now - float(state.get("fetched_at", 0))) < _ROBOTS_TTL_S:
            cd = state.get("crawl_delay")
            return float(cd) if cd is not None else None
        robots_url = _robots_url_for(url)
        if not robots_url:
            return None
        fetcher = globals().get("_robots_fetcher") or _default_robots_fetch
        body = fetcher(robots_url)
        cd = _parse_crawl_delay(body or "")
        _ROBOTS_CACHE[host] = {"fetched_at": now, "crawl_delay": cd}
        return cd
    except Exception:
        return None  # fail-open.


# ---------------------------------------------------------------------------
# Composed guard helpers the lane calls (cache-check -> breaker -> pace -> fetch -> record/store).
# ---------------------------------------------------------------------------
def before_fetch(marketplace: str, query: str, url: str = "") -> Dict[str, Any]:
    """The single pre-fetch gate the lane calls. Returns a decision dict:
        {"action": "serve_cache", "listings": [...]}            -- a fresh cache HIT (zero fetch)
        {"action": "skip", "reason": "breaker_open"}            -- the host breaker is OPEN
        {"action": "fetch", "paced_seconds": <float>}           -- proceed; pacing already applied

    Order: cache-check FIRST (a hit is the cheapest + safest -> no host contact at all); else the
    breaker (skip a host that is pushing back); else pace (respect the min interval + robots
    crawl-delay) and tell the lane to fetch. FAIL-OPEN: any error -> {"action": "fetch"} (proceed
    with the legit fetch). NEVER returns a fabricated listing -- 'serve_cache' is a real prior
    result; 'skip' carries NO data."""
    try:
        if not is_enabled():
            return {"action": "fetch", "paced_seconds": 0.0}
        cached = cache_get(marketplace, query)
        if cached is not None:
            return {"action": "serve_cache", "listings": cached, "reason": "cache_hit"}
        if breaker_is_open(marketplace, url):
            return {"action": "skip", "reason": "breaker_open"}
        crawl_delay = crawl_delay_for(url) if url else None
        waited = pace(marketplace, url, crawl_delay=crawl_delay)
        return {"action": "fetch", "paced_seconds": waited}
    except Exception:
        return {"action": "fetch", "paced_seconds": 0.0}  # fail-open.


def after_fetch(
    marketplace: str, query: str, url: str = "", *,
    listings: Optional[List[Dict[str, Any]]] = None, status: str = "", marker_text: str = "",
) -> bool:
    """The single post-fetch hook the lane calls with the fetch outcome. Feeds the breaker (block vs
    success) and stores a NON-EMPTY result in the cache. Returns the `blocked` verdict (for the
    caller's logging). FAIL-OPEN + NEVER FABRICATE: any error -> returns False; an empty/blocked
    result is NEVER cached."""
    try:
        if not is_enabled():
            return False
        blocked = _block_signal(listings, status=status, marker_text=marker_text)
        record_result(marketplace, url, blocked=blocked)
        if not blocked and listings:
            cache_put(marketplace, query, listings)
        return blocked
    except Exception:
        return False  # fail-open.


def reset_all() -> None:
    """Reset ALL in-process state (pacing timestamps, breaker, robots cache). For tests/ops; does
    NOT touch the on-disk cache (use cache_clear for that). TOTAL."""
    _LAST_HIT.clear()
    _BREAKER.clear()
    _ROBOTS_CACHE.clear()


__all__ = [
    "is_enabled",
    "cache_key",
    "cache_get",
    "cache_put",
    "cache_clear",
    "pace",
    "record_hit",
    "breaker_is_open",
    "record_result",
    "breaker_reset",
    "crawl_delay_for",
    "before_fetch",
    "after_fetch",
    "reset_all",
]
