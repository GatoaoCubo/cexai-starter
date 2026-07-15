#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI YouTube social-INBOUND research lane -- cex_youtube_data (research-universe build).

The SOCIAL-INBOUND video lane. Where the marketplace passes (cex_marketplace_detail_meli /
cex_meli_trends / cex_marketplace_detail_shopee) read the SELLING surface, this lane reads what
the AUDIENCE produces + reacts to on video: which videos a query surfaces, their public stats
(views / likes / comments), the comment threads on one video (the raw voice-of-customer signal),
and a channel's reach. It is a GREEN source: the OFFICIAL YouTube Data API v3, on a free quota
key -- no scraping, no anti-bot, no fabricated number.

The 4 endpoints (https://www.googleapis.com/youtube/v3/{...}):
  search        -> videos matching a free-text query (ids + light snippet)
  videos        -> full statistics + contentDetails (view/like/comment counts, duration, tags)
  commentThreads-> top-level comments on ONE video (author / text / likes / published)
  channels      -> a channel's statistics (subscriber / view / video counts)

THE single most important SECURITY rule of this module (the exact cybersec-audit concern):
the YouTube API key is passed in the URL QUERY (``?key=<secret>``). Therefore an error /
exception MUST NEVER echo the full request URL -- the key would leak into logs/output. EVERY
error string this module emits is built from the exception TYPE NAME + the endpoint PATH with
the key STRIPPED/MASKED (``key=REDACTED``). _redact() is applied defensively to every reason
string before it lands in the returned dict. A dedicated test asserts the key string NEVER
appears in any returned dict OR error/reason field on a forced failure.

CARDINAL RULE -- NEVER fabricate (memory: reference_ml_scraping_antibot_hallucination). A 4xx
(bad/over-quota key) / a missing field / a non-mapping body -> the signal stays an honest
``null``/``[]`` and the failure is recorded in ``endpoint_status`` / ``data_sources``; the
function CONTINUES. youtube_research is TOTAL: it NEVER raises (no key, a 403, a transport drop
-> an honest record, never a guess).

ANTI-INJECTION: a caller-supplied video_id / channel_id is VALIDATED against
``^[A-Za-z0-9_-]{6,64}$`` BEFORE it is ever placed in a URL (the cybersec lesson -- an id is
never trusted into a request unchecked). A free-text ``query`` is sent ONLY as a urlencoded
``q`` param (requests does the encoding), never spliced into a path.

REUSE (from cex_tool_resolver_live, NOT re-implemented): _HTTP_TIMEOUT (the degrade-never
ceiling), _safe_json (TOTAL resp.json). NEW here: the id validator, the key-redactor, the
session-less _youtube_get seam, and the search/videos/comments/channel normalizers.

SECRET HYGIENE: the key is read at call time from CEX_YOUTUBE_API_KEY (preferred) or
YOUTUBE_API_KEY (the sibling repos set this -- both documented + accepted); it lands ONLY in the
request ``params`` (so requests urlencodes it) and is NEVER logged, printed, stored, or
interpolated into any message. The CLI never echoes the key.

ASCII-only (.claude/rules/ascii-code-rule.md). Fully type-hinted. Composes; modifies nothing.

Live proof (the orchestrator runs this -- real network; needs a key, else an honest 'blocked'):
  python _tools/cex_youtube_data.py "comedouro gato inteligente"
  python _tools/cex_youtube_data.py video:dQw4w9WgXcQ
  python _tools/cex_youtube_data.py channel:UC_x5XG1OV2P6uZZ5FSM9Ttw
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

# REUSE the live resolver's PROVEN glue (import-light: no driver/key read at import). We import the
# MODULE so a test can monkeypatch ``_youtube_get`` on THIS module and have youtube_research pick it
# up (the same seam posture the ML/Shopee adapters use).
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_tool_resolver_live as _live  # type: ignore[import]

_HTTP_TIMEOUT = _live._HTTP_TIMEOUT
_safe_json = _live._safe_json

# The OFFICIAL YouTube Data API v3 base (GREEN -- key-gated, free quota, no scraping).
_YT_API_BASE = "https://www.googleapis.com/youtube/v3"

# The env vars that hold the API key. CEX_YOUTUBE_API_KEY is the CEXAI-canonical name; the sibling
# repos (CODEXA et al.) set YOUTUBE_API_KEY -- BOTH are accepted, CEX_ name wins when both present.
_KEY_ENV_PRIMARY = "CEX_YOUTUBE_API_KEY"
_KEY_ENV_FALLBACK = "YOUTUBE_API_KEY"

# Anti-injection: a video_id / channel_id MUST match this before it touches a URL. YouTube video
# ids are 11 chars and channel ids 24, but we accept a generous bounded alnum/_/- range so the gate
# is robust without being a fabricated-format assertion.
_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,64}$")

# Bounds (degrade-never + cost). The API itself caps maxResults at 50; we never exceed it.
_MAX_SEARCH_RESULTS = 25      # videos returned per query (<= 50, the API ceiling).
_MAX_COMMENTS = 50            # comment threads kept for a video_id (<= 100 page, we cap at 50).
_API_MAX_RESULTS_CEILING = 50

# A short, secret-free reason a key-less call self-reports (the honest 'blocked' contract).
_REASON_NO_KEY = "youtube_api_key_required"


# --------------------------------------------------------------------------- #
# Status sentinel (carries NO secret -- only a short, already-redacted reason).
# --------------------------------------------------------------------------- #
class YouTubeUnavailable(RuntimeError):
    """Raised INTERNALLY by _youtube_get on an HTTP/transport error OR a no-key call so
    youtube_research records an honest failure. Its message is ALWAYS secret-free: built from the
    exception TYPE NAME + the endpoint PATH (key stripped). NEVER carries the API key or full URL."""


# --------------------------------------------------------------------------- #
# Secret redaction -- the linchpin of the cybersec concern. NEVER let a key reach output/logs.
# --------------------------------------------------------------------------- #
def _redact(text: Any) -> str:
    """Mask any ``key=<value>`` occurrence to ``key=REDACTED`` in a string (defense in depth).

    The module is ALREADY built to never interpolate the key into a message, but this is the
    belt-and-suspenders pass applied to EVERY reason string before it lands in the returned dict:
    even if a future change (or a library exception text) ever embedded the URL, the secret is
    scrubbed here. TOTAL -- a non-string -> its repr, then scrubbed. NEVER raises."""
    try:
        s = text if isinstance(text, str) else repr(text)
    except Exception:
        return "redaction_error"
    # Mask key=... up to the next & / whitespace / quote (covers URL query + any embedded form).
    return re.sub(r"(?i)([?&]?key=)[^&\s\"'<>]+", r"\1REDACTED", s)


# --------------------------------------------------------------------------- #
# Key resolution (NAME-only logging ever; the VALUE never leaves this function except into params).
# --------------------------------------------------------------------------- #
def _resolve_api_key(explicit: Optional[str] = None) -> Optional[str]:
    """Return the YouTube API key from (in order) an explicit arg, CEX_YOUTUBE_API_KEY, then
    YOUTUBE_API_KEY. None when absent (-> the honest 'blocked' path). The value is NEVER logged."""
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    for env_name in (_KEY_ENV_PRIMARY, _KEY_ENV_FALLBACK):
        val = os.environ.get(env_name)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


# --------------------------------------------------------------------------- #
# id validation -- anti-injection. An id NEVER reaches a URL unchecked.
# --------------------------------------------------------------------------- #
def _valid_id(value: Any) -> bool:
    """True iff ``value`` is a safe id token (``^[A-Za-z0-9_-]{6,64}$``). This is the anti-injection
    gate: a caller-supplied video_id / channel_id MUST pass this BEFORE it is placed in any request
    param. A non-string / out-of-range / metacharacter-bearing input -> False (rejected, never
    fabricated into a call)."""
    return isinstance(value, str) and bool(_ID_RE.match(value))


# --------------------------------------------------------------------------- #
# THE network seam -- the ONLY place a request is built. Key lands in params ONLY.
# --------------------------------------------------------------------------- #
def _youtube_get(endpoint: str, params: Mapping[str, Any], api_key: str) -> Any:
    """GET ``{base}/{endpoint}`` with ``params`` + the API key (the key goes in ``params['key']`` so
    requests urlencodes it -- it is NEVER concatenated into a URL string here).

    RAISES YouTubeUnavailable on any HTTP/transport error. The raised message is SECRET-FREE: it is
    built from the exception TYPE NAME + the endpoint PATH only (the key / full URL are NEVER in it),
    and is _redact()-scrubbed for defense in depth. NEVER fabricates a body.

    ``endpoint`` is one of the fixed literals (search/videos/commentThreads/channels) chosen by this
    module -- NEVER caller free-text -- so the PATH itself can never carry an injected secret."""
    import requests  # type: ignore[import]  # lazy (offline-import friendly; tests never reach here)

    url = "%s/%s" % (_YT_API_BASE, endpoint)
    # Copy params and attach the key LAST. requests does the urlencoding; the key value stays only
    # in this dict + the wire -- never in a string we build or log.
    q: Dict[str, Any] = dict(params)
    q["key"] = api_key
    try:
        resp = requests.get(url, params=q, timeout=_HTTP_TIMEOUT)
        resp.raise_for_status()
    except Exception as exc:
        # CRITICAL: build the reason from the TYPE NAME + the endpoint PATH ONLY. NEVER include the
        # URL/params/key. _redact is the final scrub (in case a library exception text embeds it).
        raise YouTubeUnavailable(
            _redact("%s on GET /%s" % (type(exc).__name__, endpoint))
        ) from None  # 'from None' so no chained exception re-surfaces the key-bearing request.
    return _safe_json(resp)


# --------------------------------------------------------------------------- #
# THE entry -- fetch the YouTube research record for a query OR a video_id OR a channel_id.
# --------------------------------------------------------------------------- #
def youtube_research(
    query: Optional[str] = None,
    video_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    now: Optional[Any] = None,
    *,
    api_key: Optional[str] = None,
    max_results: int = _MAX_SEARCH_RESULTS,
) -> Dict[str, Any]:
    """Fetch the YouTube social-inbound research record. TOTAL: NEVER raises, NEVER fabricates,
    NEVER leaks the API key (into output OR any error/reason field).

    Provide AT LEAST one of:
      query: free-text -> search videos (then enrich each with stats via the videos endpoint).
      video_id: a single video -> its stats + its top comment threads (voice-of-customer).
      channel_id: a single channel -> its public statistics.
    (All three may be combined; each drives its own endpoints independently, degrade-never.)

    Args:
      query: a search string (sent ONLY as the urlencoded ``q`` param -- never spliced into a path).
      video_id: a YouTube video id; VALIDATED (``^[A-Za-z0-9_-]{6,64}$``) before any URL-build. An
        invalid id is REJECTED (recorded in endpoint_status), never sent.
      channel_id: a YouTube channel id; same validation + rejection posture.
      now: an OPTIONAL ISO-8601 timestamp echoed into ``fetched_at`` (for deterministic tests /
        provenance). When None, fetched_at stays None (no wall-clock dependency baked into the data).
      api_key: an explicit key (OPTIONAL); when None, resolved from CEX_YOUTUBE_API_KEY then
        YOUTUBE_API_KEY. No key -> the honest 'blocked' record (NOT a crash).
      max_results: search videos to request (clamped to 1.._API_MAX_RESULTS_CEILING).

    Returns a dict (all honest-null when unavailable):
      query, video_id, channel_id,
      videos (list of {id, title, channel, channel_id, published_at, view_count, like_count,
        comment_count, duration, tags}),
      comments (list of {author, text, like_count, published_at} -- when a video_id is given),
      channel (a {id, title, subscriber_count, view_count, video_count} dict | None),
      sentiment (None -- a reserved hook; this lane does NOT compute sentiment, it never guesses),
      data_sources (provenance per endpoint), endpoint_status (ok|failed|skipped|rejected per
        endpoint), fetched_at (the echoed ``now`` | None),
      mock (ALWAYS False -- real API data or an explicit null, never a simulated value)."""
    rec = _empty_record()
    rec["query"] = _opt_str(query)
    rec["fetched_at"] = _opt_str(now)
    # Echo a provided id ONLY if valid; an invalid id is not trusted even into the echo field.
    vid = video_id if _valid_id(video_id) else None
    chan = channel_id if _valid_id(channel_id) else None
    rec["video_id"] = vid
    rec["channel_id"] = chan

    key = _resolve_api_key(api_key)
    if not key:
        # No key -> honest 'blocked' self-report on EVERY requested signal. NEVER hits the network.
        rec["endpoint_status"]["api_key"] = "blocked: %s (set %s or %s)" % (
            _REASON_NO_KEY, _KEY_ENV_PRIMARY, _KEY_ENV_FALLBACK)
        return rec

    # Record a rejection for any id the caller supplied that FAILED validation (transparency: the
    # caller learns their id was dropped, and it is provably never sent).
    if video_id is not None and vid is None:
        rec["endpoint_status"]["video"] = "rejected: invalid video_id (anti-injection gate)"
    if channel_id is not None and chan is None:
        rec["endpoint_status"]["channel"] = "rejected: invalid channel_id (anti-injection gate)"

    n = _clamp(max_results, 1, _API_MAX_RESULTS_CEILING)

    # 1) SEARCH (when a query is given) -> ids, then enrich with the videos endpoint for real stats.
    if rec["query"]:
        search_body = _safe_endpoint(
            rec, "search",
            lambda: _youtube_get("search",
                                 {"part": "snippet", "q": rec["query"], "type": "video",
                                  "maxResults": n},
                                 key))
        ids = _search_video_ids(search_body) if search_body is not None else []
        if ids:
            videos_body = _safe_endpoint(
                rec, "videos",
                lambda: _youtube_get("videos",
                                     {"part": "snippet,statistics,contentDetails",
                                      "id": ",".join(ids), "maxResults": n},
                                     key))
            if videos_body is not None:
                _apply_videos(rec, videos_body)

    # 2) A single VIDEO id -> its stats (videos endpoint) + its top comment threads.
    if vid:
        v_body = _safe_endpoint(
            rec, "video",
            lambda: _youtube_get("videos",
                                 {"part": "snippet,statistics,contentDetails", "id": vid},
                                 key))
        if v_body is not None:
            _apply_videos(rec, v_body)  # appends the single video into the videos list.
        c_body = _safe_endpoint(
            rec, "comments",
            lambda: _youtube_get("commentThreads",
                                 {"part": "snippet", "videoId": vid,
                                  "maxResults": _clamp(_MAX_COMMENTS, 1, 100), "order": "relevance"},
                                 key))
        if c_body is not None:
            _apply_comments(rec, c_body)

    # 3) A single CHANNEL id -> its public statistics.
    if chan:
        ch_body = _safe_endpoint(
            rec, "channel",
            lambda: _youtube_get("channels",
                                 {"part": "snippet,statistics", "id": chan},
                                 key))
        if isinstance(ch_body, Mapping):
            _apply_channel(rec, ch_body)

    # If the caller asked for NOTHING valid (no query + no valid ids), note it (still TOTAL).
    if not rec["query"] and not vid and not chan:
        rec["endpoint_status"].setdefault(
            "input", "skipped: no query and no valid video_id/channel_id provided")

    return rec


# --------------------------------------------------------------------------- #
# search -> the list of video ids. PURE + TOTAL (NEVER fabricate an id).
# --------------------------------------------------------------------------- #
def _search_video_ids(body: Any) -> List[str]:
    """Pull video ids out of a search response: {items:[{id:{videoId}}, ...]}. A non-mapping / a
    missing/invalid id is dropped (never fabricated). Each id is RE-VALIDATED before being kept (an
    id from the API is still passed through the same anti-injection gate before it feeds the next
    request)."""
    items = body.get("items") if isinstance(body, Mapping) else None
    if not isinstance(items, list):
        return []
    ids: List[str] = []
    for it in items:
        if not isinstance(it, Mapping):
            continue
        id_field = it.get("id")
        vid: Optional[str]
        if isinstance(id_field, Mapping):
            vid = _opt_str(id_field.get("videoId"))
        else:
            vid = _opt_str(id_field)  # some shapes return a bare id string.
        if vid is not None and _valid_id(vid) and vid not in ids:
            ids.append(vid)
    return ids


# --------------------------------------------------------------------------- #
# videos -> full stats. PURE + TOTAL. APPENDS (so query-search + a video_id both feed one list).
# --------------------------------------------------------------------------- #
def _apply_videos(rec: Dict[str, Any], body: Any) -> None:
    """Map a videos (or search-enriched) body onto rec['videos']. The official shape is
    {items:[{id, snippet:{title, channelTitle, channelId, publishedAt, tags},
             statistics:{viewCount, likeCount, commentCount}, contentDetails:{duration}}, ...]}.
    Each absent field stays None (honest). De-dupes by video id. NEVER fabricates a number -- a
    missing count is None, never a 0 stand-in."""
    items = body.get("items") if isinstance(body, Mapping) else None
    if not isinstance(items, list):
        return
    existing = {v.get("id") for v in rec["videos"] if isinstance(v, Mapping)}
    for it in items:
        if not isinstance(it, Mapping):
            continue
        vid = _opt_str(it.get("id"))
        if vid is None or vid in existing:
            continue
        snip = it.get("snippet") if isinstance(it.get("snippet"), Mapping) else {}
        stats = it.get("statistics") if isinstance(it.get("statistics"), Mapping) else {}
        details = it.get("contentDetails") if isinstance(it.get("contentDetails"), Mapping) else {}
        rec["videos"].append({
            "id": vid,
            "title": _opt_str(snip.get("title")),
            "channel": _opt_str(snip.get("channelTitle")),
            "channel_id": _opt_str(snip.get("channelId")),
            "published_at": _opt_str(snip.get("publishedAt")),
            "view_count": _to_int(stats.get("viewCount")),       # API returns counts as STRINGS.
            "like_count": _to_int(stats.get("likeCount")),
            "comment_count": _to_int(stats.get("commentCount")),
            "duration": _opt_str(details.get("duration")),        # ISO-8601 duration, e.g. PT4M13S.
            "tags": _str_list(snip.get("tags")),
        })
        existing.add(vid)
    rec["videos_count"] = len(rec["videos"])


# --------------------------------------------------------------------------- #
# commentThreads -> the top-level comments (voice-of-customer). PURE + TOTAL.
# --------------------------------------------------------------------------- #
def _apply_comments(rec: Dict[str, Any], body: Any) -> None:
    """Map a commentThreads body onto rec['comments']. The official shape nests the top-level
    comment under
    {items:[{snippet:{topLevelComment:{snippet:{authorDisplayName, textDisplay, likeCount,
             publishedAt}}}}, ...]}. Each absent field stays None (honest). Capped at _MAX_COMMENTS.
    A comment with NO text is dropped (never fabricated)."""
    items = body.get("items") if isinstance(body, Mapping) else None
    if not isinstance(items, list):
        return
    out: List[Dict[str, Any]] = []
    for it in items:
        snip = _dig(it, "snippet", "topLevelComment", "snippet")
        if not isinstance(snip, Mapping):
            continue
        text = _opt_str(snip.get("textDisplay")) or _opt_str(snip.get("textOriginal"))
        if text is None:
            continue  # a comment with no body is dropped -- never fabricated.
        out.append({
            "author": _opt_str(snip.get("authorDisplayName")),
            "text": text,
            "like_count": _to_int(snip.get("likeCount")),
            "published_at": _opt_str(snip.get("publishedAt")),
        })
        if len(out) >= _MAX_COMMENTS:
            break
    rec["comments"] = out
    rec["comments_count"] = len(out)


# --------------------------------------------------------------------------- #
# channels -> public statistics. PURE + TOTAL.
# --------------------------------------------------------------------------- #
def _apply_channel(rec: Dict[str, Any], body: Mapping[str, Any]) -> None:
    """Map a channels body onto rec['channel']. Shape:
    {items:[{id, snippet:{title}, statistics:{subscriberCount, viewCount, videoCount}}]}. Uses the
    first item. Absent -> rec['channel'] stays None (honest). NEVER fabricates a count."""
    items = body.get("items")
    if not isinstance(items, list) or not items:
        return
    first = items[0]
    if not isinstance(first, Mapping):
        return
    snip = first.get("snippet") if isinstance(first.get("snippet"), Mapping) else {}
    stats = first.get("statistics") if isinstance(first.get("statistics"), Mapping) else {}
    rec["channel"] = {
        "id": _opt_str(first.get("id")),
        "title": _opt_str(snip.get("title")),
        "subscriber_count": _to_int(stats.get("subscriberCount")),
        "view_count": _to_int(stats.get("viewCount")),
        "video_count": _to_int(stats.get("videoCount")),
    }


# --------------------------------------------------------------------------- #
# Per-endpoint safe runner (records ok / failed in endpoint_status + data_sources). SECRET-FREE.
# --------------------------------------------------------------------------- #
def _safe_endpoint(rec: Dict[str, Any], name: str, call: Any) -> Any:
    """Run ONE endpoint call; record its provenance + status. DEGRADE-NEVER: a YouTubeUnavailable
    (4xx/5xx/transport -- e.g. a 403 over-quota key) OR any unexpected error -> the endpoint is
    marked 'failed: <reason>' (the reason is ALREADY secret-free, and is _redact()-scrubbed again
    here for defense in depth) and None is returned. NEVER fabricates, NEVER leaks the key."""
    try:
        body = call()
    except YouTubeUnavailable as exc:
        rec["endpoint_status"][name] = "failed: %s" % _redact(str(exc) or "unavailable")
        return None
    except Exception as exc:  # defensive: a parse/shape surprise must not crash the record.
        rec["endpoint_status"][name] = "failed: %s" % _redact(type(exc).__name__)
        return None
    rec["endpoint_status"][name] = "ok"
    rec["data_sources"][name] = "youtube:%s" % name
    return body


# --------------------------------------------------------------------------- #
# PURE helpers (TOTAL -- absent/garbage -> None; NEVER fabricate).
# --------------------------------------------------------------------------- #
def _opt_str(value: Any) -> Optional[str]:
    """A non-empty stripped string, or None. An int/float is stringified. A bool is NOT a string.
    TOTAL."""
    if isinstance(value, bool):
        return None
    if isinstance(value, str):
        s = value.strip()
        return s or None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def _to_int(value: Any) -> Optional[int]:
    """A non-negative int, or None. The YouTube API returns counts as STRINGS ('12345'); a numeric
    string is parsed. A bool / negative / non-numeric -> None (NEVER a fabricated 0)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float):
        return int(value) if value >= 0 and value == value else None  # value==value rejects NaN.
    if isinstance(value, str):
        s = value.strip()
        if s.isdigit():
            return int(s)
    return None


def _str_list(value: Any) -> List[str]:
    """A list of non-empty strings (e.g. video tags), or []. A non-list / non-string entries are
    dropped. NEVER fabricates an entry."""
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for v in value:
        s = _opt_str(v)
        if s is not None:
            out.append(s)
    return out


def _clamp(value: Any, lo: int, hi: int) -> int:
    """Clamp value into [lo, hi]; a non-int -> lo. PURE."""
    if not isinstance(value, int) or isinstance(value, bool):
        return lo
    return max(lo, min(hi, value))


def _dig(obj: Any, *keys: str) -> Any:
    """Walk nested mappings by ``keys``; return the leaf or None at the first non-mapping. TOTAL."""
    cur = obj
    for k in keys:
        if not isinstance(cur, Mapping):
            return None
        cur = cur.get(k)
    return cur


def _empty_record() -> Dict[str, Any]:
    """The all-null YouTube research record skeleton (every contract field present, honest null).
    mock is ALWAYS False -- this record is real API data or an explicit null, never a simulated
    value. sentiment is ALWAYS None here: this lane does NOT compute sentiment (a reserved hook --
    it never guesses one)."""
    return {
        "query": None,
        "video_id": None,
        "channel_id": None,
        "videos": [],
        "videos_count": 0,
        "comments": [],
        "comments_count": 0,
        "channel": None,
        "sentiment": None,          # reserved hook -- never fabricated by this lane.
        "data_sources": {},
        "endpoint_status": {},
        "fetched_at": None,
        "mock": False,
    }


__all__ = [
    "youtube_research",
    "YouTubeUnavailable",
]


# --------------------------------------------------------------------------- #
# CLI -- the orchestrator runs this LIVE (real network). With NO key it prints the honest 'blocked'
# record (live proof needs CEX_YOUTUBE_API_KEY / YOUTUBE_API_KEY). NEVER prints the key.
# --------------------------------------------------------------------------- #
def _print_record(rec: Mapping[str, Any]) -> None:
    """Print a SHORT, credential-free summary of a research record (NEVER prints the API key)."""
    print("  %-18s %s" % ("query", rec.get("query")))
    print("  %-18s %s" % ("video_id", rec.get("video_id")))
    print("  %-18s %s" % ("channel_id", rec.get("channel_id")))
    print("  %-18s %s" % ("videos_count", rec.get("videos_count")))
    for v in (rec.get("videos") or [])[:10]:
        if isinstance(v, Mapping):
            print("    [%s] views=%s likes=%s  %s" % (
                v.get("id"), v.get("view_count"), v.get("like_count"), v.get("title")))
    print("  %-18s %s" % ("comments_count", rec.get("comments_count")))
    for c in (rec.get("comments") or [])[:5]:
        if isinstance(c, Mapping):
            txt = c.get("text") or ""
            print("    - %s: %s" % (c.get("author"), txt[:80]))
    ch = rec.get("channel")
    if isinstance(ch, Mapping):
        print("  %-18s subs=%s views=%s videos=%s  (%s)" % (
            "channel", ch.get("subscriber_count"), ch.get("view_count"),
            ch.get("video_count"), ch.get("title")))
    print("  %-18s %s" % ("endpoint_status", rec.get("endpoint_status")))
    print("  %-18s %s" % ("data_sources", rec.get("data_sources")))


def _parse_target(arg: str) -> Dict[str, Optional[str]]:
    """Map a CLI arg to youtube_research kwargs: 'video:ID' / 'channel:ID' / anything-else -> query.
    The ID half is NOT validated here (youtube_research does the authoritative anti-injection gate);
    this only routes the intent."""
    s = (arg or "").strip()
    if s.lower().startswith("video:"):
        return {"query": None, "video_id": s.split(":", 1)[1].strip() or None, "channel_id": None}
    if s.lower().startswith("channel:"):
        return {"query": None, "video_id": None, "channel_id": s.split(":", 1)[1].strip() or None}
    return {"query": s or None, "video_id": None, "channel_id": None}


def _main(argv: List[str]) -> int:
    if not argv:
        print("CEXAI YouTube social-inbound research lane (research-universe build). Usage:")
        print("  python _tools/cex_youtube_data.py \"<search query>\"        (search videos + stats)")
        print("  python _tools/cex_youtube_data.py video:<VIDEO_ID>          (stats + comments)")
        print("  python _tools/cex_youtube_data.py channel:<CHANNEL_ID>      (channel statistics)")
        print("")
        print("NOTE needs an OFFICIAL YouTube Data API v3 key in CEX_YOUTUBE_API_KEY (preferred) or")
        print("YOUTUBE_API_KEY. With NO key it self-reports 'blocked: %s' and NEVER" % _REASON_NO_KEY)
        print("fabricates. The key is passed in the URL query and is NEVER logged/echoed (REDACTED).")
        return 0

    kwargs = _parse_target(argv[0])
    label = "query" if kwargs["query"] else ("video" if kwargs["video_id"] else "channel")
    print("[youtube] %s research for: %s (NO key -> expect honest 'blocked') ..." % (
        label, argv[0]))
    # NOTE: youtube_research uses json import only via _safe_json; we serialize the summary here.
    rec = youtube_research(
        query=kwargs["query"], video_id=kwargs["video_id"], channel_id=kwargs["channel_id"])
    _print_record(rec)
    # Also emit the full record as JSON (contract: JSON + exit 0). Never contains the key.
    import json
    print(json.dumps(rec, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
