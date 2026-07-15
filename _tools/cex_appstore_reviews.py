#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI app-store REPUTATION lane -- cex_appstore_reviews (research-universe, REPUTATION pass).

THE reputation pass for mobile apps. Where the marketplace lanes read the SEARCH grid + the CATALOG
ficha (cex_marketplace_detail_meli / _shopee) and the demand surface (cex_meli_trends), THIS lane
reads what users SAY about an app: the public review streams of the two app stores. It is the
GREEN-ish, low-risk sibling of the facundoolano app-store-scraper pattern -- production-grade, but
honest about which store is a public feed and which is a brittle internal RPC.

THE two stores, with their HONEST risk grade:

  APPLE App Store -- GREEN. Apple publishes a PUBLIC, unauthenticated RSS-as-JSON customer-reviews
    feed. There is NO token, NO anti-bot, NO session: it is a documented content feed Apple serves
    for syndication. The endpoint (page 1, most-recent-first):
        GET https://itunes.apple.com/{country}/rss/customerreviews/page=1/id={appid}/sortby=mostrecent/json
    The app id is the NUMERIC track id (e.g. 6447526069). The feed's first ``entry`` is the app
    metadata (carrying ``im:rating``/``userRatingCount`` when present); the remaining entries are the
    reviews. We read up to _MAX_REVIEWS reviews from page 1 (bounded -- NO infinite paging).

  GOOGLE Play -- HONEST-BLOCKED (documented, NOT fabricated, NOT a crash). Google Play has NO public
    review feed. Its web client fetches reviews through an OBFUSCATED RPC endpoint:
        POST https://play.google.com/_/PlayStoreUi/data/batchexecute   (rpcids=UsvDTd, ...)
    whose request + response are a brittle, undocumented, periodically-rotated nested-array protocol
    (the same protocol the facundoolano google-play-scraper reverse-engineers). The shape is NOT a
    stable contract: when Google rotates the rpcid / the array layout, a naive parser would either
    crash or -- far worse -- silently mis-map a field into a fabricated rating. So THIS lane treats
    Google Play EXACTLY like the Shopee session-token-required pattern
    (cex_marketplace_detail_shopee): it documents the endpoint, attempts the DOCUMENTED parse, and on
    ANY shape mismatch / transport failure self-reports
    ``endpoint_status='blocked' + reason='google_play_batchexecute_shape_unstable'`` with an
    all-honest-null record. It NEVER fabricates a review and NEVER crashes the dict.

CARDINAL RULE -- NEVER fabricate a review or a rating (memory:
reference_ml_scraping_antibot_hallucination -- a fabricated number is the cardinal sin). Only a
review the store actually returned is emitted. A blocked / empty / garbage body yields the honest
record with ``reviews: []`` and a recorded reason -- NEVER a guessed star or invented author.
fetch_reviews is TOTAL: it NEVER raises (a bad id, a 404, a transport drop, a rotated Google RPC ->
the honest record).

ID FORMAT VALIDATED BEFORE ANY URL IS BUILT (anti-injection -- cybersec lesson):
  * Apple        -> a bare run of digits (optionally an 'id' prefix): ^id?\\d{3,}$. A package name,
                    a URL, a path-traversal payload, anything non-numeric -> honest 'invalid id',
                    NO URL built, NO request made.
  * Google Play  -> a reverse-DNS package name 'com.x.y' (^[A-Za-z][\\w]*(\\.[A-Za-z][\\w]*)+$). A
                    numeric id, a URL, an injection payload -> honest 'invalid id', NO URL built.
The country + lang are likewise constrained to 2-letter ASCII codes before they touch a URL.

REUSE (from cex_tool_resolver_live, NOT re-implemented -- the SAME glue the marketplace lanes use):
  _HTTP_TIMEOUT (the degrade-never ceiling), _to_int / _to_float (numeric coercers). NEW here: the
  per-store id validators, the Apple RSS normalizer, the Google-Play batchexecute documented-parse +
  honest-blocked path, the single ``_http_get_json`` network seam (the one place tests monkeypatch).

SECRET HYGIENE: this lane uses NO credentials (the Apple feed is public; the Google RPC is
key-less). On ANY error only the exception TYPE name is recorded -- NEVER a response body, NEVER a
header (a defensive habit even where no secret exists). The CLI echoes no credential.

SENTIMENT HOOK: every record carries ``sentiment: None`` -- a SEPARATE PT-sentiment tool fills it
later. This lane NEVER guesses a sentiment label (that would be fabrication).

ASCII-only (.claude/rules/ascii-code-rule.md). Fully type-hinted. Composes; modifies nothing.

Live proof (the orchestrator runs this -- Apple is real public network; Google Play self-reports
blocked unless a future batchexecute adapter is supplied):
  python _tools/cex_appstore_reviews.py apple 6447526069
  python _tools/cex_appstore_reviews.py googleplay com.whatsapp
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

# REUSE the live resolver's PROVEN glue (import-light: no driver/key read at import). _HTTP_TIMEOUT
# is the degrade-never short ceiling; _to_int / _to_float are the TOTAL numeric coercers (a bool is
# NOT a number; non-finite -> None). We import the MODULE so the reuse mirrors the marketplace lanes.
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_tool_resolver_live as _live  # type: ignore[import]

_HTTP_TIMEOUT = _live._HTTP_TIMEOUT
_to_int = _live._to_int
_to_float = _live._to_float

# The two stores this lane understands. Anything else -> an honest 'unsupported store' record.
STORE_APPLE = "apple"
STORE_GOOGLE = "googleplay"
_STORE_ALIASES = {
    "apple": STORE_APPLE,
    "ios": STORE_APPLE,
    "appstore": STORE_APPLE,
    "app_store": STORE_APPLE,
    "itunes": STORE_APPLE,
    "googleplay": STORE_GOOGLE,
    "google": STORE_GOOGLE,
    "play": STORE_GOOGLE,
    "android": STORE_GOOGLE,
    "google_play": STORE_GOOGLE,
}

# Apple's PUBLIC customer-reviews RSS-as-JSON feed (GREEN -- no token, no anti-bot, no session).
_APPLE_RSS_TMPL = (
    "https://itunes.apple.com/%(country)s/rss/customerreviews"
    "/page=1/id=%(appid)s/sortby=mostrecent/json"
)

# Google Play's OBFUSCATED reviews RPC (HONEST-BLOCKED -- a brittle, undocumented, rotated array
# protocol; documented here, parsed defensively, self-reported blocked on ANY shape surprise).
_GOOGLE_BATCHEXECUTE_URL = "https://play.google.com/_/PlayStoreUi/data/batchexecute"
_GOOGLE_REVIEWS_RPC_ID = "UsvDTd"  # the reviews rpcid (rotates -- never relied on as a contract).

# The honest reason a Google-Play call self-reports (the degrade-never contract for the rotated RPC).
_REASON_GOOGLE_BLOCKED = "google_play_batchexecute_shape_unstable"

# Bound: never read more than this many reviews per call, and never page past page 1 (no infinite
# paging). Apple's feed returns up to ~50 entries/page; we cap conservatively.
_MAX_REVIEWS = 100

# id validators (compiled once). Apple = a numeric track id (optionally 'id'-prefixed). Google Play
# = a reverse-DNS package name. Both are anchored -> a URL / injection payload can NEVER match.
_APPLE_ID_RE = re.compile(r"^id?(\d{3,})$", re.IGNORECASE)
_BARE_DIGITS_RE = re.compile(r"^\d{3,}$")
_GOOGLE_PKG_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+$")
# country / lang = a 2-letter ASCII code (ISO-3166 / ISO-639). Anything else -> rejected before URL.
_CC_RE = re.compile(r"^[A-Za-z]{2}$")


# --------------------------------------------------------------------------- #
# THE single network seam -- the ONLY HTTP touch. Tests monkeypatch THIS.
# --------------------------------------------------------------------------- #
def _http_get_json(url: str) -> Any:
    """GET ``url`` and return the decoded JSON body (TOTAL at the transport boundary, but RAISES on a
    hard HTTP/transport error so the caller can record an honest failure). This is the ONE place a
    test monkeypatches (``cex_appstore_reviews._http_get_json``) to stay fully offline.

    Uses requests with a short timeout (_HTTP_TIMEOUT) and a plain UA. NO credentials are sent (the
    Apple feed is public). On a non-2xx or transport error it raises; the caller maps that to the
    honest endpoint_status. A non-JSON 2xx body -> {} (never a crash, never a fabricated body)."""
    import requests  # local import -> import-light module; the seam is monkeypatched in tests.

    resp = requests.get(
        url,
        headers={"Accept": "application/json", "User-Agent": "cex-reputation/1.0"},
        timeout=_HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    try:
        return resp.json()
    except Exception:
        return {}


def _http_post_json(url: str, *, data: Any, headers: Optional[Mapping[str, str]] = None) -> str:
    """POST to ``url`` (form-encoded) and return the RAW text body. Used ONLY by the Google-Play
    batchexecute attempt. RAISES on a hard HTTP/transport error. NO credentials are sent. Tests
    monkeypatch this seam too. The body is returned as TEXT (the batchexecute response is a
    ')]}\\'-prefixed nested-array blob, NOT clean JSON)."""
    import requests  # local import (import-light).

    resp = requests.post(
        url,
        data=data,
        headers=dict(headers or {"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}),
        timeout=_HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.text if isinstance(resp.text, str) else ""


# --------------------------------------------------------------------------- #
# id / arg validation -- BEFORE any URL is built (anti-injection). PURE + TOTAL.
# --------------------------------------------------------------------------- #
def normalize_store(store: str) -> Optional[str]:
    """Map a store token to its canonical id (apple | googleplay), or None if unsupported. TOTAL."""
    if not isinstance(store, str):
        return None
    return _STORE_ALIASES.get(store.strip().lower())


def validate_app_id(store: str, app_id: str) -> Optional[str]:
    """Validate ``app_id`` for ``store`` and return the CANONICAL id string, or None if malformed.
    NEVER builds a URL; NEVER raises. This is the anti-injection gate -- a URL, a path-traversal
    ('../'), a shell/redirect payload, or a cross-store id can NEVER pass (the regexes are anchored).

      * apple      -> the numeric track id (an optional 'id' prefix is stripped): 'id6447526069' or
                      '6447526069' -> '6447526069'. A package name / URL / non-numeric -> None.
      * googleplay -> a reverse-DNS package name: 'com.whatsapp', 'br.com.gato.app' -> unchanged. A
                      numeric id / URL / single-token / injection -> None."""
    if not isinstance(app_id, str):
        return None
    s = app_id.strip()
    if not s or len(s) > 256:  # an absurdly long input is rejected outright (no URL built).
        return None
    if store == STORE_APPLE:
        m = _APPLE_ID_RE.match(s)
        if m:
            return m.group(1)
        if _BARE_DIGITS_RE.match(s):
            return s
        return None
    if store == STORE_GOOGLE:
        return s if _GOOGLE_PKG_RE.match(s) else None
    return None


def _safe_cc(value: Optional[str], default: str) -> str:
    """A 2-letter ASCII country/lang code, lower-cased, or the default. Anything that is not exactly
    two ASCII letters (a URL fragment, an injection payload, a 3-letter code) -> the default. This
    runs BEFORE the code touches a URL (anti-injection on the country/lang path too)."""
    if isinstance(value, str) and _CC_RE.match(value.strip()):
        return value.strip().lower()
    return default


# --------------------------------------------------------------------------- #
# THE entry -- fetch the reputation record (reviews + rating summary) for ONE app.
# --------------------------------------------------------------------------- #
def fetch_reviews(
    store: str,
    app_id: str,
    country: str = "br",
    lang: str = "pt",
    now: Optional[Any] = None,
) -> Dict[str, Any]:
    """Fetch the public-review reputation record for ONE app. TOTAL: NEVER raises, NEVER fabricates.

    Args:
      store: 'apple' (App Store, GREEN public RSS) or 'googleplay' (Play, HONEST-BLOCKED RPC).
        Aliases (ios/appstore/itunes; google/play/android) are accepted.
      app_id: Apple = the NUMERIC track id (e.g. '6447526069', optionally 'id'-prefixed); Google
        Play = the reverse-DNS package name (e.g. 'com.whatsapp'). VALIDATED per store BEFORE any URL
        is built -- a malformed/injection id yields an honest 'invalid id' record, NO request made.
      country: a 2-letter store country (default 'br'). Non-2-letter -> coerced to 'br' before URL.
      lang: a 2-letter language hint (default 'pt'); used by the Google-Play RPC. Non-2-letter ->
        'pt'. (Apple's RSS is country-keyed, not lang-keyed -- lang is recorded for provenance.)
      now: an OPTIONAL datetime injected for deterministic ``fetched_at`` (testing). When None, the
        current UTC time is used.

    Returns a dict (honest-null on every failure path):
      app_id, store, country, lang,
      rating_avg (float|None), ratings_count (int|None),
      reviews (list of {author, rating, title, text, version, date, thumbs_up, dev_reply}),
      reviews_count,
      score_histogram ({1..5: count}|None  -- when the store exposes it; Apple's RSS does NOT, so
        this is honest-null on Apple),
      sentiment (None ALWAYS -- a separate PT-sentiment tool fills it),
      data_sources (provenance per source), endpoint_status ('ok'|'blocked'|'failed: ...'|'invalid'),
      fetched_at (ISO-8601 UTC provenance), mock (ALWAYS False)."""
    rec = _empty_record()
    rec["fetched_at"] = _iso_now(now)

    canon = normalize_store(store)
    rec["store"] = canon if canon else (str(store).strip().lower() if isinstance(store, str) else None)
    rec["country"] = _safe_cc(country, "br")
    rec["lang"] = _safe_cc(lang, "pt")

    if canon is None:
        rec["endpoint_status"]["store"] = "invalid: unsupported store (use 'apple' or 'googleplay')"
        return rec

    valid_id = validate_app_id(canon, app_id)
    rec["app_id"] = valid_id  # the CANONICAL id (None when malformed -- never the raw injection).
    if valid_id is None:
        rec["endpoint_status"]["app_id"] = "invalid: malformed app id for %s (no request made)" % canon
        return rec

    if canon == STORE_APPLE:
        _fetch_apple(rec, valid_id)
    else:
        _fetch_googleplay(rec, valid_id, rec["lang"], rec["country"])
    return rec


# --------------------------------------------------------------------------- #
# APPLE -- the GREEN public RSS-as-JSON feed. PURE-ish (one seam call) + TOTAL.
# --------------------------------------------------------------------------- #
def _fetch_apple(rec: Dict[str, Any], appid: str) -> None:
    """Fetch + map Apple's public customer-reviews RSS feed (page 1, most-recent). DEGRADE-NEVER: a
    transport/HTTP error or a non-mapping body -> endpoint_status records the failure and the record
    stays honest-null (NEVER fabricated). The country was already validated."""
    url = _APPLE_RSS_TMPL % {"country": rec["country"], "appid": appid}
    rec["data_sources"]["apple_rss"] = "apple:rss/customerreviews"
    try:
        body = _http_get_json(url)
    except Exception as exc:  # transport / non-2xx / decode -> honest failure (no secret to leak).
        rec["endpoint_status"]["apple_rss"] = "failed: %s" % type(exc).__name__
        return

    entries = _apple_entries(body)
    if entries is None:
        # A 200 with no feed/entry array -> nothing to map (treat as honest empty, NEVER fabricate).
        rec["endpoint_status"]["apple_rss"] = "ok: no reviews on page 1"
        rec["reviews"] = []
        rec["reviews_count"] = 0
        return

    # Apple convention: entry[0] is the APP node (carries im:rating / userRatingCount when present);
    # the remaining entries are the reviews. A single-entry feed = the app node only (0 reviews).
    if entries:
        _apply_apple_app_node(rec, entries[0])
    review_entries = entries[1:] if len(entries) > 1 else []
    reviews: List[Dict[str, Any]] = []
    for ent in review_entries:
        mapped = _apple_review(ent)
        if mapped is not None:  # a non-mapping / textless entry is dropped (never fabricated).
            reviews.append(mapped)
        if len(reviews) >= _MAX_REVIEWS:
            break
    rec["reviews"] = reviews
    rec["reviews_count"] = len(reviews)
    rec["endpoint_status"]["apple_rss"] = "ok"


def _apple_entries(body: Any) -> Optional[List[Any]]:
    """Pull the ``feed.entry`` list out of Apple's RSS-JSON. Apple returns
    {'feed': {'entry': [...]}}; ``entry`` may be a single object (one node) or a list. A body with no
    feed/entry -> None (honest 'no reviews'); a single object -> a 1-list. TOTAL -> never raises."""
    if not isinstance(body, Mapping):
        return None
    feed = body.get("feed")
    if not isinstance(feed, Mapping):
        return None
    entry = feed.get("entry")
    if entry is None:
        return None
    if isinstance(entry, list):
        return entry
    if isinstance(entry, Mapping):
        return [entry]
    return None


def _apply_apple_app_node(rec: Dict[str, Any], node: Any) -> None:
    """Map the Apple feed's APP node (entry[0]) -> rating_avg + ratings_count, WHEN present. Apple's
    customer-reviews feed often omits these (they live on the lookup API), so this is best-effort:
    an absent field stays honest-null. NEVER fabricates a rating."""
    if not isinstance(node, Mapping):
        return
    rec["rating_avg"] = _to_float(_label(node.get("im:rating")))
    rec["ratings_count"] = _to_int(_label(node.get("im:userRatingCount")) or _label(node.get("userRatingCount")))


def _apple_review(node: Any) -> Optional[Dict[str, Any]]:
    """Map ONE Apple review entry -> {author, rating, title, text, version, date, thumbs_up,
    dev_reply}. Apple's RSS wraps scalars as {'label': value} (and author as {'name': {'label': ...}}).
    A non-mapping node, or one with NO text AND NO title, is dropped (None) -- never a fabricated
    review. A missing field within a real review stays honest-null."""
    if not isinstance(node, Mapping):
        return None
    text = _label(node.get("content"))
    title = _label(node.get("title"))
    if text is None and title is None:
        return None  # nothing substantive -> drop (never fabricate an empty review).
    author = None
    auth_node = node.get("author")
    if isinstance(auth_node, Mapping):
        name = auth_node.get("name")
        author = _label(name) if isinstance(name, Mapping) else (name if isinstance(name, str) else None)
    return {
        "author": _opt_str(author),
        "rating": _to_int(_label(node.get("im:rating"))),
        "title": _opt_str(title),
        "text": _opt_str(text),
        "version": _opt_str(_label(node.get("im:version"))),
        "date": _opt_str(_label(node.get("updated"))),
        # Apple's review feed exposes NEITHER a thumbs-up count NOR a developer reply -> honest null
        # (those fields exist for the Google-Play shape; we keep the contract uniform). NEVER faked.
        "thumbs_up": None,
        "dev_reply": None,
    }


def _label(value: Any) -> Any:
    """Unwrap Apple's {'label': X} scalar wrapper -> X. A plain scalar passes through. A non-mapping,
    non-label value returns as-is; absent -> None. TOTAL."""
    if isinstance(value, Mapping):
        return value.get("label")
    return value


# --------------------------------------------------------------------------- #
# GOOGLE PLAY -- the HONEST-BLOCKED batchexecute RPC. Documented, parsed defensively, self-reported
# blocked on ANY shape surprise (the Shopee session-token-required pattern). PURE-ish + TOTAL.
# --------------------------------------------------------------------------- #
def _fetch_googleplay(
    rec: Dict[str, Any],
    package: str,
    lang: str,
    country: str,
    rpc_caller: Optional[Any] = None,
) -> None:
    """Attempt the Google-Play reviews batchexecute RPC; on ANY shape mismatch / transport failure
    self-report ``endpoint_status='blocked'`` + ``reason=google_play_batchexecute_shape_unstable``
    with an all-honest-null record. NEVER fabricates a review, NEVER crashes.

    The RPC (documented, NOT a stable contract):
      POST https://play.google.com/_/PlayStoreUi/data/batchexecute
      body: f.req=[[["UsvDTd","[null,null,[2,<sort>,[<count>,null,null],null,[]],[\"{package}\",7]]",
                     null,"generic"]]]  + hl={lang} + gl={country}
      response: a ")]}'\\n"-prefixed blob whose nested arrays carry the reviews. Google ROTATES the
      rpcid + the array layout periodically -> a naive parser would crash or (worse) mis-map a field
      into a FABRICATED rating. So we attempt the documented parse and, on ANY surprise, self-report
      blocked. Today (no maintained reverse-engineered adapter wired) this lane ALWAYS self-reports
      blocked unless a ``rpc_caller`` returning a known-good shape is injected (the test seam)."""
    rec["data_sources"]["google_play_batchexecute"] = "googleplay:batchexecute/%s" % _GOOGLE_REVIEWS_RPC_ID
    # Build the documented body AFTER id-validation (package is already validated; lang/country are
    # 2-letter-validated) -- this is constructed but, absent a maintained adapter, treated as blocked.
    try:
        raw = _google_rpc_call(package, lang, country, rpc_caller)
    except Exception as exc:
        # Transport / non-2xx -> honest blocked (the RPC is unauthenticated; only the type is noted).
        rec["endpoint_status"]["google_play_batchexecute"] = "blocked: %s (%s)" % (
            _REASON_GOOGLE_BLOCKED, type(exc).__name__)
        rec["reason"] = _REASON_GOOGLE_BLOCKED
        _blank_google_fields(rec)
        return

    reviews = _parse_google_batchexecute(raw)
    if reviews is None:
        # The DOCUMENTED parse did not recognise the shape (rotated rpcid / layout) -> honest blocked.
        # We do NOT guess: a mis-mapped array would be a fabricated review. Self-report instead.
        rec["endpoint_status"]["google_play_batchexecute"] = "blocked: %s" % _REASON_GOOGLE_BLOCKED
        rec["reason"] = _REASON_GOOGLE_BLOCKED
        _blank_google_fields(rec)
        return

    rec["reviews"] = reviews[:_MAX_REVIEWS]
    rec["reviews_count"] = len(rec["reviews"])
    rec["endpoint_status"]["google_play_batchexecute"] = "ok"


def _google_rpc_call(package: str, lang: str, country: str, rpc_caller: Optional[Any]) -> Any:
    """Perform (or simulate, via the injected ``rpc_caller``) the batchexecute POST and return the
    RAW response body. When ``rpc_caller`` is None we build the documented request and POST it via the
    network seam (which, in practice, returns a body our documented parser will not recognise -> the
    honest blocked path). RAISES on transport failure (the caller maps it to blocked)."""
    inner = json.dumps([
        None, None,
        [2, 1, [_MAX_REVIEWS, None, None], None, []],
        [package, 7],
    ])
    freq = json.dumps([[[_GOOGLE_REVIEWS_RPC_ID, inner, None, "generic"]]])
    if rpc_caller is not None:
        # Test / future-adapter seam: an injected callable returns a known-good raw body.
        return rpc_caller(package=package, lang=lang, country=country, f_req=freq)
    return _http_post_json(
        "%s?rpcids=%s&hl=%s&gl=%s" % (_GOOGLE_BATCHEXECUTE_URL, _GOOGLE_REVIEWS_RPC_ID, lang, country),
        data={"f.req": freq},
    )


def _parse_google_batchexecute(raw: Any) -> Optional[List[Dict[str, Any]]]:
    """Attempt the DOCUMENTED parse of a batchexecute reviews body -> a list of normalized reviews,
    or None if the shape is not recognised (-> the caller self-reports blocked). NEVER fabricates a
    review; NEVER raises.

    The documented (today's) shape, stripped of the ")]}'" anti-JSON-hijack prefix, is a list of
    envelopes; the reviews envelope is ['wrb.fr', 'UsvDTd', '<json-string>', ...] whose 3rd element is
    a JSON string whose [0] is the review array. Each review row's well-known offsets are:
      row[1][0] = author name, row[2] = star rating, row[4] = review text, row[5] = [ts_seconds,...],
      row[6] = thumbs-up count, row[7][1] = developer reply text, row[10] = app version.
    Because Google ROTATES this, every offset access is guarded; the FIRST sign the layout moved
    (a non-list row, a missing rating, a non-string text) makes us return None for the WHOLE body
    rather than emit a half-fabricated review."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    text = raw
    # Strip the ")]}'" anti-hijack prefix (and any leading junk before the first '[').
    idx = text.find("[")
    if idx < 0:
        return None
    try:
        envelopes = json.loads(text[idx:])
    except Exception:
        return None
    review_blob = _google_reviews_blob(envelopes)
    if review_blob is None:
        return None
    rows = review_blob[0] if (isinstance(review_blob, list) and review_blob) else None
    if not isinstance(rows, list):
        return None
    out: List[Dict[str, Any]] = []
    for row in rows:
        mapped = _google_review_row(row)
        if mapped is None:
            # A row we cannot map confidently -> the layout likely rotated. Abort the WHOLE parse
            # (return None) so the caller self-reports blocked rather than emit fabricated reviews.
            return None
        out.append(mapped)
        if len(out) >= _MAX_REVIEWS:
            break
    return out


def _google_reviews_blob(envelopes: Any) -> Optional[Any]:
    """From the decoded batchexecute envelope list, find the reviews payload (the 'wrb.fr'/'UsvDTd'
    envelope's 3rd element, itself a JSON string) and decode it. None if not found / not decodable."""
    if not isinstance(envelopes, list):
        return None
    for env in envelopes:
        if (isinstance(env, list) and len(env) >= 3
                and env[0] == "wrb.fr" and env[1] == _GOOGLE_REVIEWS_RPC_ID
                and isinstance(env[2], str)):
            try:
                return json.loads(env[2])
            except Exception:
                return None
    return None


def _google_review_row(row: Any) -> Optional[Dict[str, Any]]:
    """Map ONE Google-Play review row -> the uniform review dict, or None if the row does not match
    the documented offsets (signalling a rotated layout). A review MUST have a rating AND some text
    to be emitted -- otherwise we return None (never a fabricated review)."""
    if not isinstance(row, list) or len(row) < 6:
        return None
    rating = _to_int(_at(row, 2))
    text = _at(row, 4)
    if rating is None or not isinstance(text, str) or not text.strip():
        return None  # missing the two load-bearing fields -> not confidently a review -> abort.
    author = None
    author_node = _at(row, 1)
    if isinstance(author_node, list):
        author = _at(author_node, 0)
    ts_node = _at(row, 5)
    date_val = _at(ts_node, 0) if isinstance(ts_node, list) else None
    reply_node = _at(row, 7)
    dev_reply = _at(reply_node, 1) if isinstance(reply_node, list) else None
    return {
        "author": _opt_str(author),
        "rating": rating,
        "title": None,  # Google-Play reviews have no separate title -> honest null.
        "text": _opt_str(text),
        "version": _opt_str(_at(row, 10)),
        "date": _opt_str(date_val if not isinstance(date_val, (list, Mapping)) else None),
        "thumbs_up": _to_int(_at(row, 6)),
        "dev_reply": _opt_str(dev_reply if isinstance(dev_reply, str) else None),
    }


def _at(seq: Any, idx: int) -> Any:
    """seq[idx] or None -- TOTAL index access (out-of-range / non-sequence -> None). NEVER raises."""
    if isinstance(seq, list) and 0 <= idx < len(seq):
        return seq[idx]
    return None


def _blank_google_fields(rec: Dict[str, Any]) -> None:
    """Ensure the Google-Play blocked record is honest-empty (reviews [] / counts 0 / summary null).
    Idempotent; NEVER fabricates."""
    rec["reviews"] = []
    rec["reviews_count"] = 0
    rec["score_histogram"] = None
    rec["rating_avg"] = None
    rec["ratings_count"] = None


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


def _iso_now(now: Optional[Any]) -> str:
    """An ISO-8601 UTC timestamp for provenance. ``now`` (a datetime) is used when supplied (for
    deterministic tests); else the current UTC time. TOTAL -> a bad ``now`` falls back to real now."""
    import datetime as _dt

    dt = now if isinstance(now, _dt.datetime) else _dt.datetime.now(_dt.timezone.utc)
    try:
        return dt.replace(microsecond=0).isoformat()
    except Exception:
        return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _empty_record() -> Dict[str, Any]:
    """The all-null reputation record skeleton (every contract field present, honest null). mock is
    ALWAYS False -- this record is real store data or an explicit blocked/invalid, never simulated.
    sentiment is ALWAYS None here -- a separate PT-sentiment tool fills it (this lane never guesses
    a sentiment, which would be fabrication)."""
    return {
        "app_id": None,
        "store": None,
        "country": None,
        "lang": None,
        "rating_avg": None,
        "ratings_count": None,
        "reviews": [],
        "reviews_count": 0,
        "score_histogram": None,
        # SENTIMENT HOOK: filled by a separate PT-sentiment tool later. NEVER guessed here.
        "sentiment": None,
        "reason": None,
        "data_sources": {},
        "endpoint_status": {},
        "fetched_at": None,
        "mock": False,
    }


__all__ = [
    "fetch_reviews",
    "validate_app_id",
    "normalize_store",
    "STORE_APPLE",
    "STORE_GOOGLE",
]


# --------------------------------------------------------------------------- #
# CLI -- a credential-free inspection. Apple is real public network; Google Play self-reports blocked
# (no maintained batchexecute adapter is wired -- the honest W-state). Prints JSON; exit 0.
# --------------------------------------------------------------------------- #
def _main(argv: List[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("CEXAI app-store reputation lane (reviews). Usage:")
        print("  python _tools/cex_appstore_reviews.py <store> <app_id> [country] [lang]")
        print("")
        print("  store   : apple | googleplay  (aliases: ios/appstore/itunes ; google/play/android)")
        print("  app_id  : apple = NUMERIC track id (e.g. 6447526069) ; googleplay = package (com.x.y)")
        print("  country : 2-letter store country (default br)")
        print("  lang    : 2-letter language hint (default pt)")
        print("")
        print("  Apple      = GREEN  (public RSS-as-JSON customer-reviews feed; no token/anti-bot).")
        print("  GooglePlay = BLOCKED honest self-report (batchexecute RPC shape is unstable/rotated;")
        print("               documented + parsed defensively, NEVER fabricated).")
        return 0

    store = argv[0]
    app_id = argv[1] if len(argv) >= 2 else ""
    country = argv[2] if len(argv) >= 3 else "br"
    lang = argv[3] if len(argv) >= 4 else "pt"
    rec = fetch_reviews(store, app_id, country=country, lang=lang)
    # Print the FULL record as JSON (no credential is ever present). Reviews are truncated in the
    # human echo to keep it readable, but the JSON carries them all.
    print(json.dumps(rec, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
