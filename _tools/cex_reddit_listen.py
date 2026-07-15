#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI social-INBOUND listening lane -- cex_reddit_listen (research-universe build).

THE Reddit listening pass. Where the marketplace lanes read what shoppers BUY (Mercado Livre /
Shopee catalog depth), this lane reads what people SAY -- the social-inbound surface: submissions +
comments + subreddit metadata, searched by keyword and/or subreddit. Reddit is the cleanest social
source (GREEN-ish): its PUBLIC JSON endpoints are keyless (rate-limited, a real User-Agent is the
price of entry) and its OAuth is a documented, polite upgrade -- no anti-bot arms race like the
marketplaces.

TWO postures, keyless-first (the W-honesty contract):
  * PRIMARY (keyless, GREEN-ish): the public *.json endpoints with a descriptive User-Agent --
      GET https://www.reddit.com/r/{sub}/search.json?q=&restrict_sr=1&sort=&t=&limit=   (sub-scoped)
      GET https://www.reddit.com/search.json?q=&sort=&t=&limit=                          (site-wide)
      GET https://www.reddit.com/r/{sub}/about.json                                      (sub metadata)
    Rate-limited but keyless. No token, no login.
  * OPTIONAL (OAuth, when CEX_REDDIT_CLIENT_ID + CEX_REDDIT_SECRET env are present): a script-app
    client_credentials token (POST https://www.reddit.com/api/v1/access_token) -> GETs route to
    https://oauth.reddit.com/... with 'Authorization: Bearer <token>'. Higher rate ceiling.

If the PUBLIC endpoint is blocked (HTTP 429/403/503 -- Reddit throttles keyless traffic) AND no
creds are present -> an HONEST-BLOCKED self-report (the Shopee pattern): status stays the empty
result list, endpoint_status records the block + a reason, and listen_reddit CONTINUES. It is NOT a
crash and it is NEVER a fabricated post.

CARDINAL RULE -- NEVER fabricate (memory: reference_ml_scraping_antibot_hallucination). Only
Reddit-returned posts are emitted. A blocked / token-less / non-mapping body -> an honest empty
``results`` + a recorded ``endpoint_status``, never a guessed thread. listen_reddit is TOTAL: it
NEVER raises (a 403, a transport drop, a garbage body -> the honest-null/blocked record).

ANTI-INJECTION: the subreddit is validated against ^[A-Za-z0-9_]{1,50}$ and the query is
length-capped BEFORE either is placed in a URL (a subreddit like '../../about' or a 5KB query never
reaches the network). The query is sent ONLY as a urlencoded ?q= parameter (never interpolated into
the path).

SECRET HYGIENE (the cybersec lesson): the client_secret + the bearer token land ONLY in the token
request body / the Authorization header. Their VALUES are NEVER logged, printed, stored, or placed
in any output field or error message -- an error records ONLY the exception TYPE name.

REUSE (from cex_tool_resolver_live, NOT re-implemented): _HTTP_TIMEOUT (the degrade-never ceiling),
_safe_json (TOTAL resp.json), _to_int / _to_float (numeric coercers). NEW here: the validators, the
keyless/OAuth GET seam (_reddit_get_json), the optional token mint, the listing normalizer.

ASCII-only (.claude/rules/ascii-code-rule.md). Fully type-hinted. Composes; modifies nothing.

Live proof (real network; keyless unless creds are set -- may be throttled, in which case the record
is an honest 'blocked', never fabricated):
  python _tools/cex_reddit_listen.py "comedouro gato"
  python _tools/cex_reddit_listen.py "fonte para gato" gatos
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

# REUSE the live resolver's PROVEN glue (import-light: no driver/key read at import). We import the
# MODULE for the coercers; the HTTP touch is a single local seam so a test can monkeypatch
# ``cex_reddit_listen._reddit_get_json`` and have listen_reddit pick that up (no network in tests).
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_tool_resolver_live as _live  # type: ignore[import]

_HTTP_TIMEOUT = _live._HTTP_TIMEOUT
_safe_json = _live._safe_json
_to_int = _live._to_int
_to_float = _live._to_float

# The Reddit hosts: keyless JSON lives on www; OAuth GETs go to oauth; the token mint is on www.
_REDDIT_WWW_BASE = "https://www.reddit.com"
_REDDIT_OAUTH_BASE = "https://oauth.reddit.com"
_REDDIT_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"

# A DESCRIPTIVE User-Agent is the price of keyless access -- Reddit hard-blocks the default
# python-requests UA. ASCII-only; carries NO secret (it is a public identifier, never a token).
# Tenant-neutral by design (this module is FROZEN_TOOLS_CORE, vendored byte-identical into
# every distilled tenant) -- it must never hardcode any ONE tenant's real domain.
_REDDIT_USER_AGENT = "cexai-research/1.0 (social-inbound listening; contact via tenant operator)"

# Bounds (anti-abuse + the spec cap): the query is length-capped; limit is clamped to [1, 100]
# (Reddit's own per-request ceiling). A descriptive sort/time whitelist keeps the URL well-formed.
_MAX_QUERY_LEN = 512
_LIMIT_CAP = 100
_DEFAULT_LIMIT = 25
_VALID_SORTS = ("relevance", "hot", "top", "new", "comments")
_VALID_TIMES = ("hour", "day", "week", "month", "year", "all")

# The honest reason a throttled keyless call self-reports when no creds are present (W contract).
_REASON_BLOCKED = "reddit_public_endpoint_blocked_no_credentials"

# The subreddit grammar -- validated BEFORE any URL is built (anti-injection). Compiled once.
import re as _re  # module-level (ASCII): used only by the validators.

_RE_SUBREDDIT = _re.compile(r"[A-Za-z0-9_]{1,50}")


# --------------------------------------------------------------------------- #
# Status sentinel (NO secret ever carried).
# --------------------------------------------------------------------------- #
class RedditListenUnavailable(RuntimeError):
    """Raised INTERNALLY by _reddit_get_json / the token mint on an HTTP/transport error so
    listen_reddit can record an honest 'blocked'/'failed' status. Carries NO secret -- only a short
    reason string (the URL path + the exception TYPE name), NEVER a token or client_secret."""


# --------------------------------------------------------------------------- #
# Validators -- run BEFORE any URL is built (anti-injection + bounds). PURE + TOTAL.
# --------------------------------------------------------------------------- #
def _valid_subreddit(value: Any) -> Optional[str]:
    """A subreddit name that is SAFE to interpolate into '/r/{sub}/...', or None. Accepts ONLY
    ^[A-Za-z0-9_]{1,50}$ (re.fullmatch). A leading 'r/' or '/r/' prefix is stripped first as a
    convenience, then the bare name is validated. A traversal ('../x'), a slash, a space, an empty
    or an oversized name -> None (the caller then does the SITE-WIDE search instead of building a
    path -- it NEVER reaches the network). PURE + TOTAL."""
    if not isinstance(value, str):
        return None
    s = value.strip()
    # Strip a friendly 'r/' or '/r/' prefix before validating the bare name.
    low = s.lower()
    if low.startswith("/r/"):
        s = s[3:]
    elif low.startswith("r/"):
        s = s[2:]
    s = s.strip().strip("/")
    if not s:
        return None
    return s if _RE_SUBREDDIT.fullmatch(s) else None


def _valid_query(value: Any) -> Optional[str]:
    """A non-empty, length-capped search query, or None. Whitespace-stripped; rejected when empty
    or longer than _MAX_QUERY_LEN (a 5KB query never reaches the network). The query is sent ONLY
    as a urlencoded ?q= param downstream (never path-interpolated). PURE + TOTAL."""
    if not isinstance(value, str):
        return None
    s = value.strip()
    if not s or len(s) > _MAX_QUERY_LEN:
        return None
    return s


def _clamp_limit(limit: Any) -> int:
    """Clamp the requested result count to [1, _LIMIT_CAP] (Reddit's per-request ceiling is 100).
    A non-int / out-of-range -> the nearest bound; garbage -> the default. PURE + TOTAL."""
    n = _to_int(limit)
    if n is None:
        return _DEFAULT_LIMIT
    if n < 1:
        return 1
    if n > _LIMIT_CAP:
        return _LIMIT_CAP
    return n


def _valid_sort(sort: Any) -> str:
    """A whitelisted sort, or the default 'relevance'. Keeps the URL well-formed (no arbitrary
    value reaches ?sort=). PURE + TOTAL."""
    if isinstance(sort, str) and sort.strip().lower() in _VALID_SORTS:
        return sort.strip().lower()
    return "relevance"


def _valid_time(time_filter: Any) -> Optional[str]:
    """A whitelisted time window for ?t=, or None (omit the param). PURE + TOTAL."""
    if isinstance(time_filter, str) and time_filter.strip().lower() in _VALID_TIMES:
        return time_filter.strip().lower()
    return None


# --------------------------------------------------------------------------- #
# OPTIONAL OAuth -- mint a script-app client_credentials token (only when creds present).
# --------------------------------------------------------------------------- #
def _read_reddit_creds() -> Tuple[Optional[str], Optional[str]]:
    """Read (client_id, client_secret) from CEX_REDDIT_CLIENT_ID / CEX_REDDIT_SECRET. Either absent
    -> (None, None) (the keyless posture). The VALUES are NEVER logged. PURE."""
    cid = os.environ.get("CEX_REDDIT_CLIENT_ID")
    secret = os.environ.get("CEX_REDDIT_SECRET")
    cid = cid.strip() if isinstance(cid, str) else None
    secret = secret.strip() if isinstance(secret, str) else None
    if not cid or not secret:
        return (None, None)
    return (cid, secret)


def get_reddit_token() -> Optional[str]:
    """Mint a Reddit script-app client_credentials bearer token, or None when no creds are present
    (-> the keyless posture). The client_secret lands ONLY in HTTP Basic auth on the token POST; the
    returned token is the caller's to place in an Authorization header. NEITHER value is logged.

    TOTAL: returns None on ANY failure (no creds, a 4xx on the mint, a transport drop) -- the caller
    then falls back to the keyless endpoint. NEVER raises out of here; NEVER leaks a secret."""
    cid, secret = _read_reddit_creds()
    if not cid or not secret:
        return None
    try:
        import requests  # type: ignore[import]  # lazy (offline-import friendly)

        resp = requests.post(
            _REDDIT_TOKEN_URL,
            auth=(cid, secret),  # HTTP Basic -- the secret never appears in a logged string.
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": _REDDIT_USER_AGENT},
            timeout=_HTTP_TIMEOUT,
        )
        resp.raise_for_status()
    except Exception:
        # NEVER leak the secret; a failed mint is simply 'no token' -> keyless fallback.
        return None
    body = _safe_json(resp)
    if isinstance(body, Mapping):
        tok = body.get("access_token")
        if isinstance(tok, str) and tok.strip():
            return tok.strip()
    return None


# --------------------------------------------------------------------------- #
# THE GET seam -- the ONLY network touch (keyless www OR OAuth oauth). Monkeypatch THIS in tests.
# --------------------------------------------------------------------------- #
def _reddit_get_json(path: str, params: Mapping[str, Any], token: Optional[str]) -> Any:
    """GET a Reddit JSON path and return the parsed body. The single network seam (tests
    monkeypatch ``cex_reddit_listen._reddit_get_json``).

    Routing: when ``token`` is a non-empty string, the GET goes to oauth.reddit.com with
    'Authorization: Bearer <token>'; otherwise it goes to www.reddit.com keyless. BOTH always send
    the descriptive User-Agent (keyless access is hard-blocked without it). The token VALUE is never
    logged.

    RAISES RedditListenUnavailable on ANY HTTP / transport error (a 429/403/503 keyless throttle, a
    5xx, a network drop) so the caller records an honest blocked/failed status and degrades to an
    empty result. NEVER fabricates a body."""
    import requests  # type: ignore[import]  # lazy (offline-import friendly)

    use_oauth = isinstance(token, str) and bool(token.strip())
    base = _REDDIT_OAUTH_BASE if use_oauth else _REDDIT_WWW_BASE
    url = base + (path if path.startswith("/") else "/" + path)
    headers: Dict[str, str] = {"User-Agent": _REDDIT_USER_AGENT, "Accept": "application/json"}
    if use_oauth:
        headers["Authorization"] = "Bearer %s" % token  # value NEVER logged below.
    try:
        resp = requests.get(
            url,
            params=dict(params) if params else None,
            headers=headers,
            timeout=_HTTP_TIMEOUT,
        )
        resp.raise_for_status()
    except Exception as exc:
        # NEVER leak the token; report ONLY the path + the error TYPE (some HTTPError reprs echo the
        # full URL with query params, so the status code/url stay out of the message).
        raise RedditListenUnavailable("%s on GET %s" % (type(exc).__name__, path)) from exc
    return _safe_json(resp)


# --------------------------------------------------------------------------- #
# THE entry -- listen to Reddit for a query (optionally scoped to a subreddit).
# --------------------------------------------------------------------------- #
def listen_reddit(
    query: str,
    subreddit: Optional[str] = None,
    *,
    sort: str = "relevance",
    time_filter: Optional[str] = None,
    limit: int = _DEFAULT_LIMIT,
    token: Optional[str] = None,
    now: Optional[str] = None,
) -> Dict[str, Any]:
    """Listen to Reddit for ``query`` (optionally restricted to ``subreddit``) via the keyless
    public JSON endpoint, upgrading to OAuth when CEX_REDDIT_CLIENT_ID + CEX_REDDIT_SECRET are set.
    TOTAL: NEVER raises, NEVER fabricates.

    Posture (keyless-first): if no token is passed AND no creds are present, the keyless www.json
    endpoint is used. If that endpoint is blocked (429/403/503 throttle) AND no creds exist, the
    record self-reports an HONEST 'blocked' status (the Shopee pattern) with an empty ``results`` --
    NEVER a fabricated post.

    Args:
      query: the search phrase (validated non-empty + length-capped BEFORE the URL is built; sent
        ONLY as a urlencoded ?q= parameter, never path-interpolated).
      subreddit: an OPTIONAL subreddit to restrict to (validated ^[A-Za-z0-9_]{1,50}$ BEFORE the
        '/r/{sub}/search.json' path is built -- a value that fails validation falls back to the
        SITE-WIDE search and is recorded; it NEVER reaches the network as a path segment).
      sort: one of relevance|hot|top|new|comments (anything else -> 'relevance').
      time_filter: an OPTIONAL window hour|day|week|month|year|all (anything else -> omitted).
      limit: result cap, clamped to [1, 100] (Reddit's per-request ceiling).
      token: an explicit bearer token (OPTIONAL); when None, get_reddit_token() is tried (returns
        None unless creds are set -> keyless).
      now: an OPTIONAL ISO-8601 timestamp echoed verbatim as ``fetched_at`` (for deterministic
        provenance in tests); when None the field is omitted.

    Returns a dict (honest-null when unavailable/blocked):
      query, subreddit,
      results (list of {id, subreddit, title, selftext, score, upvote_ratio, num_comments,
        author, created_utc, url, permalink}; [] when unavailable),
      result_count,
      sentiment (ALWAYS None here -- a null hook for the PT-sentiment tool to fill downstream),
      data_sources (provenance per endpoint), endpoint_status (ok|blocked|failed|skipped),
      fetched_at (only when ``now`` is provided),
      mock (ALWAYS False -- real API data or an honest null, never a simulated value)."""
    rec = _empty_listen()
    if isinstance(now, str) and now.strip():
        rec["fetched_at"] = now.strip()

    # 1) Validate the query BEFORE anything touches the network (anti-injection + bounds).
    q = _valid_query(query)
    rec["query"] = q
    if q is None:
        rec["endpoint_status"]["validate"] = (
            "failed: query empty or longer than %d chars" % _MAX_QUERY_LEN
        )
        return rec

    # 2) Validate the subreddit BEFORE building the path. An invalid value does NOT abort -- it
    # degrades to a site-wide search (recorded), and crucially NEVER reaches the URL as a segment.
    sub = _valid_subreddit(subreddit) if subreddit is not None else None
    rec["subreddit"] = sub
    if subreddit is not None and sub is None:
        rec["endpoint_status"]["subreddit"] = (
            "skipped: subreddit failed ^[A-Za-z0-9_]{1,50}$ validation -> site-wide search"
        )

    # 3) Resolve a token (keyless unless creds are present). A passed token wins; else try the mint
    # (None unless creds set). The keyless path is the default and is GREEN-ish.
    tok = token if (isinstance(token, str) and token.strip()) else get_reddit_token()
    have_creds = bool(tok) or bool(_read_reddit_creds()[0])

    # 4) Build the validated search params + path (query is urlencoded by requests as ?q=).
    params: Dict[str, Any] = {
        "q": q,
        "sort": _valid_sort(sort),
        "limit": _clamp_limit(limit),
    }
    tf = _valid_time(time_filter)
    if tf is not None:
        params["t"] = tf
    if sub is not None:
        path = "/r/%s/search.json" % sub
        params["restrict_sr"] = 1  # confine results to this subreddit.
    else:
        path = "/search.json"

    # 5) THE call (degrade-never). A throttle/transport error -> honest blocked/failed, never a raise.
    try:
        body = _reddit_get_json(path, params, tok)
    except RedditListenUnavailable as exc:
        reason = str(exc) or "unavailable"
        # Keyless + no creds + blocked -> the documented HONEST-BLOCKED self-report (Shopee pattern).
        if not have_creds:
            rec["endpoint_status"]["search"] = "blocked: %s (%s)" % (_REASON_BLOCKED, reason)
        else:
            rec["endpoint_status"]["search"] = "failed: %s" % reason
        return rec
    except Exception as exc:  # defensive: nothing else may crash the record.
        rec["endpoint_status"]["search"] = "failed: %s" % type(exc).__name__
        return rec

    # 6) Normalize the Listing body -> results[] (PURE; only Reddit-returned posts, never fabricated).
    _apply_listing(rec, body)
    rec["endpoint_status"]["search"] = "ok"
    rec["data_sources"]["search"] = "reddit:%s" % ("oauth" if tok else "public_json")
    return rec


# --------------------------------------------------------------------------- #
# Subreddit metadata -- GET /r/{sub}/about.json (a small, useful companion). TOTAL.
# --------------------------------------------------------------------------- #
def fetch_subreddit_about(
    subreddit: str, *, token: Optional[str] = None, now: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch one subreddit's metadata via GET /r/{sub}/about.json. TOTAL: NEVER raises, NEVER
    fabricates. The subreddit is validated ^[A-Za-z0-9_]{1,50}$ BEFORE the path is built; an invalid
    name yields an honest 'failed' record without any network touch.

    Returns: subreddit, about ({display_name, title, public_description, subscribers,
    active_user_count, over18, created_utc, url} or None when unavailable), data_sources,
    endpoint_status, fetched_at (when ``now`` given), mock (ALWAYS False)."""
    rec: Dict[str, Any] = {
        "subreddit": None,
        "about": None,
        "data_sources": {},
        "endpoint_status": {},
        "mock": False,
    }
    if isinstance(now, str) and now.strip():
        rec["fetched_at"] = now.strip()

    sub = _valid_subreddit(subreddit)
    rec["subreddit"] = sub
    if sub is None:
        rec["endpoint_status"]["about"] = (
            "failed: subreddit empty or failed ^[A-Za-z0-9_]{1,50}$ validation"
        )
        return rec

    tok = token if (isinstance(token, str) and token.strip()) else get_reddit_token()
    have_creds = bool(tok) or bool(_read_reddit_creds()[0])

    try:
        body = _reddit_get_json("/r/%s/about.json" % sub, {}, tok)
    except RedditListenUnavailable as exc:
        reason = str(exc) or "unavailable"
        if not have_creds:
            rec["endpoint_status"]["about"] = "blocked: %s (%s)" % (_REASON_BLOCKED, reason)
        else:
            rec["endpoint_status"]["about"] = "failed: %s" % reason
        return rec
    except Exception as exc:
        rec["endpoint_status"]["about"] = "failed: %s" % type(exc).__name__
        return rec

    about = _about_from_body(body)
    rec["about"] = about
    rec["endpoint_status"]["about"] = "ok" if about is not None else "failed: no data in about.json"
    if about is not None:
        rec["data_sources"]["about"] = "reddit:%s" % ("oauth" if tok else "public_json")
    return rec


# --------------------------------------------------------------------------- #
# THE normalizer -- map a Reddit Listing body onto results[]. PURE + TOTAL (NEVER fabricate).
# --------------------------------------------------------------------------- #
def _apply_listing(rec: Dict[str, Any], body: Any) -> None:
    """Map a Reddit Listing body ({kind:'Listing', data:{children:[{kind, data:{...}}, ...]}}) onto
    ``results``. Each child's ``data`` is one submission (or comment). A non-Listing / empty -> []
    (honest). An entry with no id is dropped (NEVER fabricated). Only Reddit-returned fields are
    read; nothing is invented."""
    children = _listing_children(body)
    results: List[Dict[str, Any]] = []
    for child in children:
        post = child.get("data") if isinstance(child, Mapping) else None
        if not isinstance(post, Mapping):
            continue
        post_id = _opt_str(post.get("id"))
        if post_id is None:
            continue  # an entry with no id is dropped -- never fabricated.
        results.append(_post_to_result(post_id, post))
    rec["results"] = results
    rec["result_count"] = len(results)


def _listing_children(body: Any) -> List[Any]:
    """Pull the children list out of a Reddit Listing body. Accepts the standard
    {data:{children:[...]}} shape AND a bare top-level list (some endpoints return an array of
    Listings -- e.g. a comments endpoint). TOTAL -> [] when none found."""
    if isinstance(body, Mapping):
        data = body.get("data")
        if isinstance(data, Mapping):
            children = data.get("children")
            if isinstance(children, list):
                return children
        return []
    if isinstance(body, list):
        # A list of Listings (e.g. the [post, comments] comments endpoint): flatten every child.
        out: List[Any] = []
        for entry in body:
            if isinstance(entry, Mapping):
                data = entry.get("data")
                if isinstance(data, Mapping):
                    children = data.get("children")
                    if isinstance(children, list):
                        out.extend(children)
        return out
    return []


def _post_to_result(post_id: str, post: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize ONE Reddit post ``data`` object into the result contract. Every field is
    captured-and-real or an honest null. ``selftext`` covers submissions; ``body`` covers comments
    (a comment has no selftext) -> selftext falls back to body so both shapes carry their text.
    NEVER fabricates a value."""
    selftext = _opt_str(post.get("selftext"))
    if selftext is None:
        selftext = _opt_str(post.get("body"))  # comment text lives under 'body'.
    permalink = _opt_str(post.get("permalink"))
    return {
        "id": post_id,
        "subreddit": _opt_str(post.get("subreddit")),
        "title": _opt_str(post.get("title")),
        "selftext": selftext,
        "score": _to_int(post.get("score")),
        "upvote_ratio": _to_float(post.get("upvote_ratio")),
        "num_comments": _to_int(post.get("num_comments")),
        "author": _opt_str(post.get("author")),
        "created_utc": _to_int(post.get("created_utc")),
        "url": _opt_str(post.get("url")),
        # permalink is a relative path on reddit.com -> absolutize for a usable link (honest:
        # only when Reddit actually returned one).
        "permalink": (_REDDIT_WWW_BASE + permalink) if permalink and permalink.startswith("/") else permalink,
    }


def _about_from_body(body: Any) -> Optional[Dict[str, Any]]:
    """Map a GET /r/{sub}/about.json body ({kind:'t5', data:{...}}) onto a compact metadata dict, or
    None when there is no data. NEVER fabricates a field (absent -> None within the dict)."""
    data = body.get("data") if isinstance(body, Mapping) else None
    if not isinstance(data, Mapping):
        return None
    out = {
        "display_name": _opt_str(data.get("display_name")),
        "title": _opt_str(data.get("title")),
        "public_description": _opt_str(data.get("public_description")),
        "subscribers": _to_int(data.get("subscribers")),
        "active_user_count": _to_int(data.get("active_user_count")),
        "over18": bool(data.get("over18")) if isinstance(data.get("over18"), bool) else None,
        "created_utc": _to_int(data.get("created_utc")),
        "url": _opt_str(data.get("url")),
    }
    # An all-null dict (a body with a data envelope but no usable fields) is still honest -> return
    # it only if at least the display_name OR a count is present; else None.
    if out["display_name"] is None and out["subscribers"] is None and out["title"] is None:
        return None
    return out


# --------------------------------------------------------------------------- #
# PURE helpers (TOTAL -- absent/garbage -> None; NEVER fabricate).
# --------------------------------------------------------------------------- #
def _opt_str(value: Any) -> Optional[str]:
    """A non-empty stripped string, or None. An int/float is stringified (some Reddit ids/counts can
    arrive numeric). A bool is NOT a string here. TOTAL."""
    if isinstance(value, bool):
        return None
    if isinstance(value, str):
        s = value.strip()
        return s or None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def _empty_listen() -> Dict[str, Any]:
    """The all-null listen record skeleton (every contract field present, honest null). sentiment is
    ALWAYS None here -- a deliberate null hook the downstream PT-sentiment tool fills. mock is ALWAYS
    False (real API data or an explicit null, never a simulated value)."""
    return {
        "query": None,
        "subreddit": None,
        "results": [],
        "result_count": 0,
        "sentiment": None,  # null hook for the PT-sentiment tool (this lane never scores sentiment).
        "data_sources": {},
        "endpoint_status": {},
        "mock": False,
    }


__all__ = [
    "listen_reddit",
    "fetch_subreddit_about",
    "get_reddit_token",
    "RedditListenUnavailable",
]


# --------------------------------------------------------------------------- #
# CLI -- the orchestrator runs this LIVE (real network; keyless unless creds are set). A keyless
# throttle is reported HONESTLY (endpoint_status 'blocked' + empty results), never fabricated.
# --------------------------------------------------------------------------- #
def _print_listen(rec: Mapping[str, Any]) -> None:
    """Print a SHORT, credential-free summary of a listen record (NEVER prints a token)."""
    print("  %-18s %s" % ("query", rec.get("query")))
    print("  %-18s %s" % ("subreddit", rec.get("subreddit")))
    print("  %-18s %s" % ("result_count", rec.get("result_count")))
    results = rec.get("results") or []
    for r in results[:10]:
        if isinstance(r, Mapping):
            title = r.get("title") or r.get("selftext") or "(no title)"
            if isinstance(title, str) and len(title) > 70:
                title = title[:67] + "..."
            print("    [score=%-5s c=%-4s] %s" % (r.get("score"), r.get("num_comments"), title))
    if len(results) > 10:
        print("    ... (%d more)" % (len(results) - 10))
    print("  %-18s %s" % ("sentiment", rec.get("sentiment")))
    print("  %-18s %s" % ("endpoint_status", rec.get("endpoint_status")))
    print("  %-18s %s" % ("data_sources", rec.get("data_sources")))


def _main(argv: List[str]) -> int:
    if not argv:
        print("CEXAI Reddit social-inbound listening lane. Usage:")
        print("  python _tools/cex_reddit_listen.py <query> [subreddit]")
        print("")
        print("  <query>      the search phrase (required; length-capped, anti-injected)")
        print("  [subreddit]  OPTIONAL subreddit to restrict to (validated ^[A-Za-z0-9_]{1,50}$)")
        print("")
        print("Posture: KEYLESS public JSON by default (GREEN-ish, rate-limited). Set")
        print("CEX_REDDIT_CLIENT_ID + CEX_REDDIT_SECRET to upgrade to OAuth (higher ceiling).")
        print("A keyless throttle -> an honest 'blocked' record, NEVER a fabricated post.")
        return 0

    query = argv[0]
    subreddit = argv[1] if len(argv) >= 2 else None
    where = ("r/%s" % subreddit) if subreddit else "site-wide"
    print("[reddit] listening for %r (%s; keyless unless creds set) ..." % (query, where))
    rec = listen_reddit(query, subreddit)
    _print_listen(rec)
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
