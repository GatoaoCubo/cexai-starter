#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI Reclame Aqui REPUTATION lane -- cex_reclame_aqui (BR; the highest-value reputation source).

THE Reputation pass of CEXAI's research universe (memory: reference_research_universe_taxonomy --
reputation / ReclameAqui is a named GREEN-edge GAP). Where the marketplace passes read price /
catalog / demand, THIS lane reads how a COMPANY is perceived: its RA1000 reputation score, its
complaint-resolution rate, its response rate, the "would do business again" percentage, and the
recent complaint stream. For a BR seller deciding who to compete with (or how to position), the
Reclame Aqui reputation IS the trust signal.

THE source is Reclame Aqui's UNDOCUMENTED internal JSON API (the same one its own SPA calls -- NO
Selenium, NO headless browser):

  company info / score : GET https://iosearch.reclameaqui.com.br
                              /raichu-io-site-search-v1/companies/info/{companyId}
  complaints (paged)   : GET https://iosearch.reclameaqui.com.br
                              /raichu-io-site-search-v1/query/companyComplains/{page}/{size}?company={companyId}
  search a name        : GET https://iosearch.reclameaqui.com.br
                              /raichu-io-site-search-v1/query/companies/{page}/{size}?q={term}

That host sits BEHIND CLOUDFLARE. With realistic browser headers a plain request MAY pass; but the
EXPECTED state for a plain ``requests`` call is a Cloudflare challenge (HTTP 403, or a 200 whose
body is an HTML "Just a moment..." interstitial, NOT JSON).

STEALTH TRANSPORT (the LIVE unlock): when ``FIRECRAWL_API_KEY`` is present, this lane can fetch the
SAME iosearch URLs through Firecrawl's stealth scrape (anti-bot proxy + JS render) and extract the
JSON out of the returned body. Two triggers:
  * ``CEX_RA_VIA_FIRECRAWL`` set (truthy) -> Firecrawl is the PRIMARY transport, OR
  * AUTO-FALLBACK -> the plain request is tried first; if it returns a Cloudflare challenge / non-JSON
    / transport error, the lane RETRIES the same URL via Firecrawl stealth.
The Firecrawl POST is ``POST https://api.firecrawl.dev/v1/scrape`` with ``formats=['rawHtml']`` +
``proxy='stealth'`` + a short ``waitFor``; the JSON is parsed out of the returned ``rawHtml`` /
``content`` body. The PROVEN normalizers (_apply_company_info / _apply_complaints / _apply_search)
run UNCHANGED on the extracted JSON -- the transport is the ONLY thing that changes.

HONEST-BLOCKED STILL HOLDS: if Firecrawl ALSO returns a challenge / non-JSON / empty body (or no key
is set, or the plain path is used and is blocked), the lane self-reports
``endpoint_status='blocked: reclame_aqui_cloudflare_challenge'``, returns the TOTAL honest-null dict
(NO complaints, NO score), exits 0, NEVER crashes, and NEVER fabricates a reputation number. The
Firecrawl path is ADDITIVE + degrade-never: it never replaces the plain path, only augments it.

CARDINAL RULE -- NEVER fabricate a reputation number (memory:
reference_ml_scraping_antibot_hallucination). A blocked / challenge / garbage body yields the
honest-null record, NEVER a guessed RA1000 / resolution rate / response rate. fetch_reputation and
search_company are TOTAL: they NEVER raise (a 403, a challenge HTML, a transport drop, a malformed
JSON body -> the honest-null / blocked record).

PROXY POSTURE (the RED reality, documented but NOT required): set ``CEX_RA_PROXY`` to a proxy URL
(e.g. a residential / stealth egress) and the PLAIN path will route the iosearch GETs through it.
With NO proxy AND no Firecrawl key the lane runs anyway and, when Cloudflare challenges, reports the
honest block. The proxy is an OPT-IN unlock, never a hard dependency; the Firecrawl stealth
transport (above) is the preferred LIVE unlock.

ANTI-INJECTION: a company id / slug is validated against ``^[A-Za-z0-9_-]{1,80}$`` BEFORE it is
ever placed into a URL path; a non-matching id is rejected (the record self-reports an honest
``invalid_company_id`` reason and NO request is made). A free-text search term is URL-encoded.

SECRET HYGIENE: only an exception TYPE name + the (static) path is ever logged -- NEVER a response
body, NEVER the ``CEX_RA_PROXY`` value, NEVER the ``FIRECRAWL_API_KEY``, NEVER a cookie. The
Firecrawl key lands ONLY in the Authorization header; every reason string is _redact()-scrubbed
(mirrors cex_youtube_data) so a key=<value> can never survive into a returned dict. The CLI never
echoes a credential.

ASCII-only (.claude/rules/ascii-code-rule.md). Fully type-hinted. Composes; modifies nothing.

Live proof (the orchestrator runs this -- real network; WITHOUT a stealth proxy expect the honest
'blocked: reclame_aqui_cloudflare_challenge' record, NEVER a fabricated score):
  python _tools/cex_reclame_aqui.py nubank
  python _tools/cex_reclame_aqui.py search:magazine luiza
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

# REUSE the live resolver's PROVEN glue (import-light: no driver/key read at import). _HTTP_TIMEOUT
# is the degrade-never ceiling; _safe_json is the TOTAL resp.json; _to_int / _to_float are the
# numeric coercers (a garbage value -> None, NEVER a fabricated number).
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_tool_resolver_live as _live  # type: ignore[import]

_HTTP_TIMEOUT = _live._HTTP_TIMEOUT
_safe_json = _live._safe_json
_to_int = _live._to_int
_to_float = _live._to_float

# The Reclame Aqui internal SPA JSON API (UNDOCUMENTED -- the host its own front-end calls).
_RA_API_BASE = "https://iosearch.reclameaqui.com.br"
_RA_INFO_PATH = "/raichu-io-site-search-v1/companies/info/%s"
_RA_COMPLAINS_PATH = "/raichu-io-site-search-v1/query/companyComplains/%d/%d"
_RA_SEARCH_PATH = "/raichu-io-site-search-v1/query/companies/%d/%d"

# Anti-injection: a company id / slug must match this BEFORE it touches a URL path.
_COMPANY_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,80}$")

# Bounded: how many complaints we keep (the page size cap -- never an unbounded pull).
_COMPLAINTS_PAGE = 0
_COMPLAINTS_SIZE = 10
_SEARCH_SIZE = 10

# The honest reason a Cloudflare-blocked call self-reports (the RED-reality degrade-never contract).
_BLOCKED_STATUS = "blocked: reclame_aqui_cloudflare_challenge"

# The env hook for a FUTURE stealth / residential proxy (OPT-IN; never required).
_PROXY_ENV = "CEX_RA_PROXY"

# --- Firecrawl stealth transport (the LIVE unlock; ADDITIVE) ----------------------------------- #
# The key NAME (value read at call time, NEVER logged) + the scrape endpoint + the render knobs.
_FIRECRAWL_KEY_ENV = "FIRECRAWL_API_KEY"
# Truthy -> Firecrawl is the PRIMARY transport. Unset -> Firecrawl is the AUTO-FALLBACK after a
# plain-request Cloudflare block (so the plain path still runs first + free).
_VIA_FIRECRAWL_ENV = "CEX_RA_VIA_FIRECRAWL"
_FIRECRAWL_SCRAPE_URL = "https://api.firecrawl.dev/v1/scrape"
# Firecrawl waits this long for the anti-bot page to settle before capturing the body (ms).
_FIRECRAWL_WAIT_MS = 6000
# The Firecrawl proxy mode that defeats Cloudflare (anti-bot stealth egress).
_FIRECRAWL_PROXY = "stealth"

# A realistic browser User-Agent + Accept set (Cloudflare inspects these; a bare client is blocked
# instantly). Even WITH these, the host frequently challenges without a residential proxy -> that
# is the EXPECTED honest-blocked state.
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Referer": "https://www.reclameaqui.com.br/",
    "Origin": "https://www.reclameaqui.com.br",
    "X-Requested-With": "XMLHttpRequest",
}


# --------------------------------------------------------------------------- #
# Status sentinel (carries NO secret -- only a short reason string).
# --------------------------------------------------------------------------- #
class ReclameAquiBlocked(RuntimeError):
    """Raised INTERNALLY by _ra_get on a Cloudflare challenge / HTTP / transport error so the
    public entrypoints record an honest 'blocked' record. Carries NO secret -- only a short reason
    (never a body, never the proxy URL, never the Firecrawl key)."""


# --------------------------------------------------------------------------- #
# Secret redaction (mirrors cex_youtube_data._redact -- belt-and-suspenders).
# --------------------------------------------------------------------------- #
def _redact(text: Any) -> str:
    """Mask any ``key=<value>`` / Bearer-token occurrence to ``...REDACTED`` in a string (defense in
    depth). The module is ALREADY built to never interpolate the Firecrawl key into a message, but
    this is the belt-and-suspenders pass applied to EVERY reason string before it lands in a returned
    dict: even if a future change (or a library exception text) ever embedded the key/URL, the secret
    is scrubbed here. TOTAL -- a non-string -> its repr, then scrubbed. NEVER raises."""
    try:
        s = text if isinstance(text, str) else repr(text)
    except Exception:
        return "redaction_error"
    # Mask key=... up to the next & / whitespace / quote (covers a URL query + any embedded form).
    s = re.sub(r"(?i)([?&]?(?:api[_-]?key|key|token|access_token)=)[^&\s\"'<>]+", r"\1REDACTED", s)
    # Mask a Bearer <token> Authorization fragment, just in case one ever leaks into a message.
    s = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._\-]+", r"\1REDACTED", s)
    return s


def _truthy(value: Optional[str]) -> bool:
    """True iff an env string is set to a truthy token ('1'/'true'/'yes'/'on'). PURE + TOTAL."""
    return isinstance(value, str) and value.strip().lower() in ("1", "true", "yes", "on")


# --------------------------------------------------------------------------- #
# Anti-injection id validation (BEFORE any URL build).
# --------------------------------------------------------------------------- #
def is_valid_company_id(company_id: Any) -> bool:
    """True iff company_id is a safe id / slug: ``^[A-Za-z0-9_-]{1,80}$``. Anything else (spaces,
    slashes, a path traversal, a querystring, an over-long blob, a non-string) is rejected so it can
    NEVER be interpolated into an iosearch URL path. PURE + TOTAL."""
    if not isinstance(company_id, str):
        return False
    return bool(_COMPANY_ID_RE.match(company_id))


# --------------------------------------------------------------------------- #
# THE network touch -- the only place a request leaves (Cloudflare-gated; honest-blocked by design).
# --------------------------------------------------------------------------- #
def _ra_get(path: str, *, params: Optional[Mapping[str, Any]] = None) -> Any:
    """GET an iosearch path and return the parsed JSON body, choosing a TRANSPORT:

      * Firecrawl-PRIMARY: when ``CEX_RA_VIA_FIRECRAWL`` is truthy AND ``FIRECRAWL_API_KEY`` is
        present -> fetch via Firecrawl stealth FIRST (the anti-bot path); on a Firecrawl block fall
        back to the plain request (which is itself usually blocked -> honest block).
      * AUTO-FALLBACK (default): try the PLAIN request first (free); if it returns a Cloudflare
        challenge / non-JSON / transport error AND ``FIRECRAWL_API_KEY`` is present -> RETRY the
        SAME url via Firecrawl stealth. If neither transport yields JSON -> ReclameAquiBlocked.
      * Plain-only: no Firecrawl key -> exactly the prior behaviour (plain request, honest block).

    This is the SINGLE network seam the tests monkeypatch; both transports converge on the SAME
    parsed-JSON contract so the PROVEN normalizers run unchanged. RAISES ReclameAquiBlocked when no
    transport yields the API's JSON. NEVER leaks the proxy value or the Firecrawl key (reasons are
    _redact()-scrubbed). NEVER fabricates a body."""
    fc_key = _read_firecrawl_key()
    if _truthy(os.environ.get(_VIA_FIRECRAWL_ENV)) and fc_key is not None:
        # Firecrawl PRIMARY: try the stealth transport first; degrade to plain on a Firecrawl block.
        try:
            return _ra_get_firecrawl(path, params=params, key=fc_key)
        except ReclameAquiBlocked:
            return _ra_get_plain(path, params=params)

    # AUTO-FALLBACK: plain first (free); on a block, retry via Firecrawl stealth when a key exists.
    try:
        return _ra_get_plain(path, params=params)
    except ReclameAquiBlocked:
        if fc_key is None:
            raise  # no stealth transport available -> honest block (prior behaviour).
        return _ra_get_firecrawl(path, params=params, key=fc_key)


def _ra_get_plain(path: str, *, params: Optional[Mapping[str, Any]] = None) -> Any:
    """The PLAIN transport: GET an iosearch path with realistic browser headers, optionally via
    ``CEX_RA_PROXY``; return the parsed JSON body.

    DEGRADE-NEVER / RED reality: the Reclame Aqui host is Cloudflare-gated. WITHOUT a stealth /
    residential proxy a challenge is the EXPECTED outcome. This helper RAISES ReclameAquiBlocked
    when:
      * the HTTP call errors (a 403 challenge, any 4xx/5xx, a transport drop), OR
      * the response is a Cloudflare interstitial (an HTML 'Just a moment...' body, NOT JSON), OR
      * the body is not the JSON object/array the API would return (a challenge served as 200).
    The proxy URL is read here and handed ONLY to the requests layer -- its VALUE is NEVER logged.
    NEVER fabricates a body."""
    import requests  # type: ignore[import]  # lazy (offline-import friendly)

    url = _RA_API_BASE + path
    proxy = os.environ.get(_PROXY_ENV)
    proxies = {"http": proxy, "https": proxy} if proxy else None
    try:
        resp = requests.get(
            url,
            headers=dict(_BROWSER_HEADERS),
            params=dict(params) if params else None,
            proxies=proxies,
            timeout=_HTTP_TIMEOUT,
        )
        resp.raise_for_status()
    except ReclameAquiBlocked:
        raise
    except Exception as exc:
        # NEVER leak a body or the proxy value; report only the error TYPE + the static path. A 403
        # here is, in practice, the Cloudflare challenge -> the caller maps it to the honest block.
        raise ReclameAquiBlocked(
            _redact("%s on GET %s" % (type(exc).__name__, _static_path(path)))
        ) from None

    # A Cloudflare challenge is frequently served as HTTP 200 whose BODY is an HTML interstitial,
    # not JSON. Detect that (the body is not a dict/list, or the content-type/text smells like the
    # 'Just a moment...' page) and treat it as a block -- NEVER parse a challenge into a score.
    if _looks_like_challenge(resp):
        raise ReclameAquiBlocked("cloudflare_challenge")
    body = _safe_json(resp)
    if not isinstance(body, (Mapping, list)):
        # _safe_json maps a non-JSON body to {} -> a string/HTML response is not the API's JSON.
        raise ReclameAquiBlocked("non_json_body")
    return body


# --------------------------------------------------------------------------- #
# Firecrawl stealth transport -- fetch the SAME iosearch URL through Firecrawl's anti-bot scrape
# and extract the JSON out of the returned body. The key lands ONLY in the Authorization header.
# --------------------------------------------------------------------------- #
def _read_firecrawl_key() -> Optional[str]:
    """Read FIRECRAWL_API_KEY from env at call time (a non-empty stripped string, else None). The
    VALUE is NEVER logged or returned to any caller that prints it -- it is handed ONLY to the
    Firecrawl Authorization header. TOTAL."""
    val = os.environ.get(_FIRECRAWL_KEY_ENV)
    if val is None or not str(val).strip():
        return None
    return str(val).strip()


def _firecrawl_full_url(path: str, params: Optional[Mapping[str, Any]]) -> str:
    """Build the FULL iosearch URL (base + path + urlencoded params) that Firecrawl will fetch.

    The complaints path ALREADY embeds its ``?company=`` querystring; the callers ALSO pass the same
    value in ``params``. To avoid a duplicated ``company=x&company=x`` (which some backends reject),
    a param key that is ALREADY present in the path's querystring is SKIPPED -- only genuinely new
    keys (e.g. the search ``q``) are appended. PURE + TOTAL."""
    from urllib.parse import urlencode

    url = _RA_API_BASE + path
    if not params:
        return url
    existing = url.split("?", 1)[1] if "?" in url else ""
    existing_keys = {kv.split("=", 1)[0] for kv in existing.split("&") if kv}
    new_pairs = {str(k): str(v) for k, v in dict(params).items() if str(k) not in existing_keys}
    if not new_pairs:
        return url
    sep = "&" if "?" in url else "?"
    return url + sep + urlencode(new_pairs)


def _ra_get_firecrawl(
    path: str, *, params: Optional[Mapping[str, Any]] = None, key: str,
) -> Any:
    """The STEALTH transport: ``POST https://api.firecrawl.dev/v1/scrape`` for the iosearch URL with
    ``formats=['rawHtml']`` + ``proxy='stealth'`` + ``waitFor`` (the anti-bot render), then extract
    the API's JSON out of the returned body and return it parsed.

    RAISES ReclameAquiBlocked when:
      * the Firecrawl HTTP call errors (any 4xx/5xx, a transport drop, quota), OR
      * Firecrawl reports a failed scrape / returns no usable body, OR
      * the returned body is itself a Cloudflare interstitial ('Just a moment...'), OR
      * no JSON object/array can be extracted from the returned body (still blocked / non-JSON).
    The Firecrawl key lands ONLY in the Authorization header; the reason strings are
    _redact()-scrubbed. NEVER fabricates a body."""
    import requests  # type: ignore[import]  # lazy (offline-import friendly; tests never reach here)

    target_url = _firecrawl_full_url(path, params)
    payload = {
        "url": target_url,
        # rawHtml = the verbatim body (the iosearch JSON arrives as a text/JSON body Firecrawl
        # returns under rawHtml/content -- we parse the JSON out of it).
        "formats": ["rawHtml"],
        "proxy": _FIRECRAWL_PROXY,          # anti-bot stealth egress (defeats the Cloudflare gate).
        "waitFor": _FIRECRAWL_WAIT_MS,      # let the challenge settle before capture.
        # Ask Firecrawl to forward the JSON Accept so the host serves the API body, not the SPA HTML.
        "headers": {"Accept": "application/json, text/plain, */*"},
    }
    try:
        resp = requests.post(
            _FIRECRAWL_SCRAPE_URL,
            headers={"Authorization": "Bearer %s" % key, "Content-Type": "application/json"},
            json=payload,
            timeout=_HTTP_TIMEOUT,
        )
        resp.raise_for_status()
    except ReclameAquiBlocked:
        raise
    except Exception as exc:
        # NEVER leak the key / URL / body: report only the error TYPE + the static path, then redact.
        raise ReclameAquiBlocked(
            _redact("firecrawl %s on scrape %s" % (type(exc).__name__, _static_path(path)))
        ) from None

    body_text = _firecrawl_body_text(_safe_json(resp))
    if not body_text:
        raise ReclameAquiBlocked("firecrawl_empty_body")
    if _text_looks_like_challenge(body_text):
        raise ReclameAquiBlocked("firecrawl_cloudflare_challenge")
    parsed = _extract_json(body_text)
    if not isinstance(parsed, (Mapping, list)):
        # Firecrawl rendered something, but it is not the API's JSON (still a challenge / HTML) ->
        # honest block. NEVER parse a non-JSON body into a score.
        raise ReclameAquiBlocked("firecrawl_non_json_body")
    return parsed


def _firecrawl_body_text(data: Any) -> str:
    """Pull the page body text out of a Firecrawl /v1/scrape response. Firecrawl nests the result
    under ``data`` with the requested format keys (rawHtml / html / content / markdown). A
    ``success: false`` envelope yields '' (the caller maps it to a block). TOTAL -> '' when no body.
    NEVER raises."""
    if not isinstance(data, Mapping):
        return ""
    # An explicit failure envelope -> no body.
    if data.get("success") is False:
        return ""
    inner = data.get("data")
    src = inner if isinstance(inner, Mapping) else data
    for fmt_key in ("rawHtml", "rawhtml", "html", "content", "markdown", "text"):
        val = src.get(fmt_key)
        if isinstance(val, str) and val.strip():
            return val
    return ""


def _text_looks_like_challenge(text: str) -> bool:
    """True iff a body STRING smells like a Cloudflare interstitial (the same markers
    _looks_like_challenge checks on a response, applied to a Firecrawl-returned body). TOTAL."""
    head = (text or "")[:600].lower()
    for marker in ("just a moment", "cf-challenge", "challenge-platform",
                   "attention required", "cloudflare"):
        if marker in head:
            return True
    return False


def _extract_json(text: str) -> Any:
    """Extract the iosearch JSON out of a (possibly HTML-wrapped) body string. The iosearch endpoint
    returns a bare JSON object/array; Firecrawl's rawHtml may return it verbatim OR wrapped in a
    ``<pre>``/``<body>`` shell. Strategy (degrade-never, NEVER fabricate):
      1. Try a direct json.loads of the stripped text.
      2. Else extract the FIRST balanced ``{...}`` or ``[...]`` span and parse that.
    Returns the parsed value, or None when nothing parses (the caller maps None -> a block)."""
    s = (text or "").strip()
    if not s:
        return None
    direct = _try_json(s)
    if direct is not None:
        return direct
    # Fallback: find the first JSON object/array span embedded in the body.
    span = _first_json_span(s)
    if span is not None:
        return _try_json(span)
    return None


def _try_json(text: str) -> Any:
    """json.loads, but TOTAL -> None on any failure or a non-object/array result. NEVER raises."""
    try:
        val = json.loads(text)
    except Exception:
        return None
    return val if isinstance(val, (dict, list)) else None


def _first_json_span(s: str) -> Optional[str]:
    """The first balanced ``{...}`` or ``[...]`` substring in ``s`` (bracket-matching, quote-aware so
    a brace inside a JSON string does not unbalance the scan). Returns None when no balanced span is
    found. Bounded by the input length. PURE + TOTAL."""
    # Pick whichever opener appears first.
    candidates = [(s.find("{"), "{", "}"), (s.find("["), "[", "]")]
    candidates = [c for c in candidates if c[0] != -1]
    if not candidates:
        return None
    start, opener, closer = min(candidates, key=lambda c: c[0])
    depth = 0
    in_str = False
    escaped = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return s[start:i + 1]
    return None


def _looks_like_challenge(resp: Any) -> bool:
    """True iff the response looks like a Cloudflare interstitial rather than the API JSON. Checks
    the Content-Type header and a short, body prefix for the classic challenge markers. TOTAL (any
    attribute access failure -> False; the JSON-shape guard in _ra_get is the backstop)."""
    try:
        ctype = ""
        headers = getattr(resp, "headers", None)
        if isinstance(headers, Mapping):
            ctype = str(headers.get("Content-Type") or headers.get("content-type") or "").lower()
        if "text/html" in ctype:
            return True
        text = getattr(resp, "text", None)
        if isinstance(text, str):
            head = text[:600].lower()
            for marker in ("just a moment", "cf-challenge", "challenge-platform",
                           "attention required", "cloudflare"):
                if marker in head:
                    return True
    except Exception:
        return False
    return False


def _static_path(path: str) -> str:
    """The path WITHOUT any querystring (so a logged reason never echoes a search term / id beyond
    the static route). PURE."""
    return path.split("?", 1)[0]


# --------------------------------------------------------------------------- #
# THE entry -- reputation (info + complaints) for ONE company id / slug. TOTAL.
# --------------------------------------------------------------------------- #
def fetch_reputation(company_id: str, now: Optional[str] = None) -> Dict[str, Any]:
    """Fetch the Reclame Aqui reputation record for ONE company id / slug. TOTAL: NEVER raises,
    NEVER fabricates.

    Args:
      company_id: a Reclame Aqui company id or slug. VALIDATED against ``^[A-Za-z0-9_-]{1,80}$``
        BEFORE any URL build (anti-injection); a non-matching id yields an honest
        ``reputation_status='invalid_company_id'`` record and NO request is made.
      now: an OPTIONAL ISO-8601 timestamp to stamp ``fetched_at`` (the caller may pass a frozen
        clock; when None ``fetched_at`` is the real UTC now). NEVER affects a reputation value.

    Returns a dict (honest-null when blocked / unavailable):
      company: {id, name, ra1000_score, resolution_rate, complaints_total, response_rate,
                would_do_business_again_pct, reputation_status},
      complaints: list of {title, status, category, created_at, company_reply},
      data_sources: provenance per endpoint,
      endpoint_status: {info, complaints} -- 'ok' | 'blocked: ...' | 'failed: ...' | 'skipped: ...',
      fetched_at: the ISO-8601 stamp (or None),
      mock: ALWAYS False (real API data or an explicit honest-null, NEVER a simulated value).

    The EXPECTED state without a stealth proxy (the RED reality) is a Cloudflare block: both
    endpoints report ``blocked: reclame_aqui_cloudflare_challenge`` and EVERY reputation field
    stays null. A garbage / challenge body NEVER becomes a guessed score."""
    rec = _empty_reputation(now)
    rec["company"]["id"] = company_id if isinstance(company_id, str) else None

    if not is_valid_company_id(company_id):
        rec["company"]["reputation_status"] = "invalid_company_id"
        rec["endpoint_status"]["info"] = "skipped: invalid company id (anti-injection)"
        rec["endpoint_status"]["complaints"] = "skipped: invalid company id (anti-injection)"
        return rec

    # E1 -- company info / score. A block here leaves every reputation field honest-null.
    info_body = _safe_endpoint(rec, "info", lambda: _ra_get(_RA_INFO_PATH % company_id))
    if isinstance(info_body, Mapping):
        _apply_company_info(rec, info_body)

    # E2 -- the complaint stream (paged, bounded). Independent: a block on info does NOT skip this,
    # and a block here does NOT erase a (separately fetched) score -- degrade-never per endpoint.
    complaints_path = (_RA_COMPLAINS_PATH % (_COMPLAINTS_PAGE, _COMPLAINTS_SIZE)) + (
        "?company=%s" % company_id
    )
    complaints_body = _safe_endpoint(
        rec, "complaints",
        lambda: _ra_get(complaints_path, params={"company": company_id}),
    )
    if complaints_body is not None:
        _apply_complaints(rec, complaints_body)

    # The overall reputation_status: 'ok' only if info succeeded; else surface the honest block.
    if rec["company"]["reputation_status"] is None:
        info_state = rec["endpoint_status"].get("info", "")
        if info_state == "ok":
            rec["company"]["reputation_status"] = "ok"
        elif info_state.startswith("blocked"):
            rec["company"]["reputation_status"] = "blocked"
        else:
            rec["company"]["reputation_status"] = "unavailable"
    return rec


# --------------------------------------------------------------------------- #
# THE search entry -- resolve a company NAME to candidate id/slug rows. TOTAL.
# --------------------------------------------------------------------------- #
def search_company(term: str, now: Optional[str] = None) -> Dict[str, Any]:
    """Search Reclame Aqui for a company by free-text NAME -> candidate {id, name, slug} rows.
    TOTAL: NEVER raises, NEVER fabricates.

    The term is URL-ENCODED before the request (it is a query value, never a path segment -- so the
    strict id regex does NOT apply here; encoding is the injection guard). An empty term yields an
    honest empty record with NO request.

    Returns a dict:
      term, companies: list of {id, name, slug}, companies_count, data_sources,
      endpoint_status: {search}, fetched_at, mock (ALWAYS False).

    The EXPECTED state without a stealth proxy is a Cloudflare block -> ``companies`` stays the
    empty list, endpoint_status records ``blocked: reclame_aqui_cloudflare_challenge``, and NO
    candidate is fabricated."""
    rec = _empty_search(term, now)
    t = term.strip() if isinstance(term, str) else ""
    if not t:
        rec["endpoint_status"]["search"] = "skipped: empty search term"
        return rec

    path = _RA_SEARCH_PATH % (0, _SEARCH_SIZE)
    body = _safe_endpoint(rec, "search", lambda: _ra_get(path, params={"q": t}))
    if body is not None:
        _apply_search(rec, body)
    return rec


# --------------------------------------------------------------------------- #
# Normalizers -- map iosearch bodies onto the records. PURE + TOTAL (NEVER fabricate).
# --------------------------------------------------------------------------- #
def _apply_company_info(rec: Dict[str, Any], body: Mapping[str, Any]) -> None:
    """Map the companies/info body onto rec['company']. Reclame Aqui nests the reputation under a
    ``companyDetails`` (or returns it flat); we read both shapes. EVERY field is honest-null when
    absent / malformed -- the RA1000 score, the resolution rate, the response rate, and the
    'would do business again' percentage are NEVER fabricated, only mapped from a real number."""
    src = body
    details = body.get("companyDetails")
    if isinstance(details, Mapping):
        src = details

    rec["company"]["name"] = _opt_str(src.get("companyName") or src.get("fantasyName")
                                      or src.get("name"))

    # The RA1000 score (Reclame Aqui's 0-10 reputation index). Only a genuine number maps.
    rec["company"]["ra1000_score"] = _ra1000(src)

    # Resolution rate + response rate + 'would do business again' -- all PERCENTAGES (0-100),
    # honest-null unless a real number is present.
    rec["company"]["resolution_rate"] = _pct(
        src.get("solvedPercentual"), src.get("resolvedPercentage"), src.get("solved"))
    rec["company"]["response_rate"] = _pct(
        src.get("answeredPercentual"), src.get("responseRate"), src.get("answered"))
    rec["company"]["would_do_business_again_pct"] = _pct(
        src.get("dealAgainPercentual"), src.get("wouldDoBusinessAgain"), src.get("dealAgain"))

    rec["company"]["complaints_total"] = _to_int(
        src.get("complainsTotal")
        if src.get("complainsTotal") is not None
        else (src.get("totalComplains")
              if src.get("totalComplains") is not None
              else src.get("complaintsTotal"))
    )

    # The textual reputation status Reclame Aqui assigns (e.g. 'OTIMO' / 'BOM' / 'RUIM'); honest
    # null when absent -- never invented.
    status_text = _opt_str(src.get("status") or src.get("finalScore") or src.get("reputationLevel"))
    if status_text is not None:
        rec["company"]["reputation_status"] = status_text


def _apply_complaints(rec: Dict[str, Any], body: Any) -> None:
    """Map the companyComplains body onto rec['complaints'] (bounded by _COMPLAINTS_SIZE). The API
    returns {complains: [...]} (or a bare list). Each row -> {title, status, category, created_at,
    company_reply}. A row with no usable content is dropped -- NEVER fabricated. Absent -> []."""
    rows = _complaints_items(body)
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        title = _opt_str(row.get("title") or row.get("description"))
        status = _opt_str(row.get("status"))
        category = _opt_str(row.get("category") or row.get("problemType"))
        created_at = _opt_str(row.get("created") or row.get("createdDate") or row.get("date"))
        # A company reply may be a bool flag or a nested object; we record its PRESENCE honestly.
        reply = row.get("answered")
        if isinstance(reply, bool):
            company_reply = reply
        elif isinstance(row.get("interactions"), int) and not isinstance(row.get("interactions"), bool):
            company_reply = row.get("interactions") > 0
        else:
            company_reply = None
        if title is None and status is None and category is None:
            continue  # nothing usable -> drop (never fabricate a complaint).
        out.append({
            "title": title,
            "status": status,
            "category": category,
            "created_at": created_at,
            "company_reply": company_reply,
        })
        if len(out) >= _COMPLAINTS_SIZE:
            break
    rec["complaints"] = out
    rec["complaints_count"] = len(out)


def _apply_search(rec: Dict[str, Any], body: Any) -> None:
    """Map the companies search body onto rec['companies'] (bounded by _SEARCH_SIZE). The API
    returns {companies: [...]} (or a bare list). Each candidate -> {id, name, slug}. A candidate
    with no id AND no slug is dropped (un-actionable) -- NEVER fabricated."""
    rows = _search_items(body)
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        cid = _opt_str(row.get("id") or row.get("companyId"))
        slug = _opt_str(row.get("shortname") or row.get("slug") or row.get("urlName"))
        name = _opt_str(row.get("companyName") or row.get("fantasyName") or row.get("name"))
        if cid is None and slug is None:
            continue  # no actionable identifier -> drop.
        out.append({"id": cid, "name": name, "slug": slug})
        if len(out) >= _SEARCH_SIZE:
            break
    rec["companies"] = out
    rec["companies_count"] = len(out)


# --------------------------------------------------------------------------- #
# Per-endpoint safe runner (records ok / blocked / failed in endpoint_status + data_sources).
# --------------------------------------------------------------------------- #
def _safe_endpoint(rec: Dict[str, Any], name: str, call: Any) -> Any:
    """Run ONE iosearch call; record its provenance + status. DEGRADE-NEVER: a ReclameAquiBlocked
    (the EXPECTED Cloudflare outcome without a stealth proxy) -> the endpoint is marked
    ``blocked: reclame_aqui_cloudflare_challenge`` and None is returned (the signal it feeds stays
    the honest empty/null). Any OTHER unexpected error -> 'failed: <type>'. NEVER fabricates."""
    try:
        body = call()
    except ReclameAquiBlocked:
        rec["endpoint_status"][name] = _BLOCKED_STATUS
        return None
    except Exception as exc:  # defensive: a parse/shape surprise must not crash the record.
        rec["endpoint_status"][name] = "failed: %s" % type(exc).__name__
        return None
    rec["endpoint_status"][name] = "ok"
    rec["data_sources"][name] = "reclame_aqui:%s" % name
    return body


# --------------------------------------------------------------------------- #
# PURE shape + field helpers (TOTAL -- absent/garbage -> None; NEVER fabricate).
# --------------------------------------------------------------------------- #
def _complaints_items(body: Any) -> List[Any]:
    """Pull the complaint rows out of {complains:[...]} / {complaints:[...]} / {data:[...]} / a bare
    list. TOTAL -> [] when none found."""
    if isinstance(body, list):
        return body
    if isinstance(body, Mapping):
        for key in ("complains", "complaints", "data", "results"):
            val = body.get(key)
            if isinstance(val, list):
                return val
    return []


def _search_items(body: Any) -> List[Any]:
    """Pull the company candidate rows out of {companies:[...]} / {data:[...]} / a bare list.
    TOTAL -> [] when none found."""
    if isinstance(body, list):
        return body
    if isinstance(body, Mapping):
        for key in ("companies", "data", "results"):
            val = body.get(key)
            if isinstance(val, list):
                return val
    return []


def _ra1000(src: Mapping[str, Any]) -> Optional[float]:
    """The RA1000 / reputation score (Reclame Aqui's 0-10 index), rounded to 2dp. Reads the common
    keys; only a genuine in-range number maps. Absent / garbage / out-of-range -> None (the score
    is NEVER fabricated, and a nonsense value is rejected rather than guessed)."""
    for key in ("ra1000", "finalScore", "score", "ra1000Score", "reputationScore"):
        n = _to_float(src.get(key))
        if n is not None and 0.0 <= n <= 10.0:
            return round(n, 2)
    return None


def _pct(*candidates: Any) -> Optional[float]:
    """The FIRST candidate that is a genuine percentage in [0, 100], rounded to 1dp. Absent /
    garbage / out-of-range -> None. A rate is NEVER fabricated; a value outside [0,100] is rejected
    (not clamped to a guess). PURE + TOTAL."""
    for c in candidates:
        n = _to_float(c)
        if n is not None and 0.0 <= n <= 100.0:
            return round(n, 1)
    return None


def _opt_str(value: Any) -> Optional[str]:
    """A non-empty stripped string, or None. An int/float id is stringified (RA ids can be ints). A
    bool is NOT a string here. TOTAL."""
    if isinstance(value, bool):
        return None
    if isinstance(value, str):
        s = value.strip()
        return s or None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def _utc_now_iso() -> str:
    """The current UTC time as an ISO-8601 string (seconds precision, 'Z' suffix). PURE-ish (reads
    the clock only)."""
    import datetime as _dt

    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z")


def _stamp(now: Optional[str]) -> Optional[str]:
    """The fetched_at stamp: a caller-supplied ISO string verbatim, else the real UTC now. A caller
    may pass None to request the live clock; the optional-now contract NEVER alters a value."""
    if isinstance(now, str) and now.strip():
        return now.strip()
    return _utc_now_iso()


def _empty_reputation(now: Optional[str]) -> Dict[str, Any]:
    """The all-null reputation record skeleton (every contract field present, honest null). mock is
    ALWAYS False -- this record is real API data or an explicit honest-null / blocked, NEVER a
    simulated value. reputation_status defaults to None so a record that never reaches 'ok' is
    honest by construction."""
    return {
        "company": {
            "id": None,
            "name": None,
            "ra1000_score": None,
            "resolution_rate": None,
            "complaints_total": None,
            "response_rate": None,
            "would_do_business_again_pct": None,
            "reputation_status": None,
        },
        "complaints": [],
        "complaints_count": 0,
        "data_sources": {},
        "endpoint_status": {},
        "fetched_at": _stamp(now),
        "mock": False,
    }


def _empty_search(term: Any, now: Optional[str]) -> Dict[str, Any]:
    """The all-null search record skeleton. mock is ALWAYS False."""
    return {
        "term": term if isinstance(term, str) else None,
        "companies": [],
        "companies_count": 0,
        "data_sources": {},
        "endpoint_status": {},
        "fetched_at": _stamp(now),
        "mock": False,
    }


__all__ = [
    "fetch_reputation",
    "search_company",
    "is_valid_company_id",
    "ReclameAquiBlocked",
    "_ra_get_firecrawl",
    "_read_firecrawl_key",
]


# --------------------------------------------------------------------------- #
# CLI -- the orchestrator runs this LIVE (real network). WITHOUT a stealth proxy expect the honest
# 'blocked: reclame_aqui_cloudflare_challenge' record (RED reality), never a fabricated score.
# --------------------------------------------------------------------------- #
def _print_reputation(rec: Mapping[str, Any]) -> None:
    """Print a SHORT, credential-free summary of a reputation record (NEVER prints a proxy value)."""
    company = rec.get("company") or {}
    for k in ("id", "name", "ra1000_score", "resolution_rate", "complaints_total",
              "response_rate", "would_do_business_again_pct", "reputation_status"):
        print("  company.%-26s %s" % (k, company.get(k) if isinstance(company, Mapping) else None))
    print("  %-34s %s" % ("complaints_count", rec.get("complaints_count")))
    complaints = rec.get("complaints") or []
    for c in complaints[:5]:
        if isinstance(c, Mapping):
            print("    - [%s] %s (%s)" % (c.get("status"), c.get("title"), c.get("category")))
    print("  %-34s %s" % ("endpoint_status", rec.get("endpoint_status")))
    print("  %-34s %s" % ("data_sources", rec.get("data_sources")))
    print("  %-34s %s" % ("fetched_at", rec.get("fetched_at")))
    print("  %-34s %s" % ("mock", rec.get("mock")))


def _print_search(rec: Mapping[str, Any]) -> None:
    """Print a SHORT, credential-free summary of a search record."""
    print("  %-20s %s" % ("term", rec.get("term")))
    print("  %-20s %s" % ("companies_count", rec.get("companies_count")))
    for c in (rec.get("companies") or [])[:10]:
        if isinstance(c, Mapping):
            print("    id=%-10s slug=%-22s %s" % (c.get("id"), c.get("slug"), c.get("name")))
    print("  %-20s %s" % ("endpoint_status", rec.get("endpoint_status")))


def _emit_json(rec: Mapping[str, Any]) -> None:
    """Print the FULL record as JSON (ASCII-safe). NEVER prints a proxy value (not in the record)."""
    import json

    print(json.dumps(rec, ensure_ascii=True, indent=2, sort_keys=True))


def _transport_label() -> str:
    """A SHORT, credential-free label of the active transport (NEVER prints the key VALUE -- only its
    PRESENCE). Used by the CLI progress lines so the operator sees plain vs Firecrawl-stealth."""
    has_fc = _read_firecrawl_key() is not None
    if not has_fc:
        return "plain (no Firecrawl key -> may be honest-blocked)"
    if _truthy(os.environ.get(_VIA_FIRECRAWL_ENV)):
        return "Firecrawl stealth PRIMARY (key present)"
    return "plain->Firecrawl stealth auto-fallback (key present)"


def _main(argv: List[str]) -> int:
    if not argv:
        print("CEXAI Reclame Aqui reputation lane (BR; Cloudflare-gated). Usage:")
        print("  python _tools/cex_reclame_aqui.py <company_id|slug>   "
              "(reputation: RA1000 score + complaints)")
        print("  python _tools/cex_reclame_aqui.py search:<name>       "
              "(resolve a company name -> id/slug candidates)")
        print("")
        print("TRANSPORT: the Reclame Aqui host is behind Cloudflare. Set FIRECRAWL_API_KEY to fetch")
        print("the iosearch JSON through Firecrawl's stealth scrape (anti-bot). With CEX_RA_VIA_FIRECRAWL")
        print("set, Firecrawl is PRIMARY; otherwise it is the AUTO-FALLBACK after a plain-request block.")
        print("If BOTH transports are blocked (or no key), the EXPECTED outcome is an honest")
        print("'blocked: reclame_aqui_cloudflare_challenge' record -- NEVER a fabricated score.")
        return 0

    arg = argv[0]
    if arg.startswith("search:"):
        term = arg[len("search:"):].strip()
        # Allow the term to span multiple argv tokens (an unquoted name).
        if len(argv) > 1:
            term = (term + " " + " ".join(argv[1:])).strip()
        print("[reclame_aqui] searching companies for %r via %s ..." % (term, _transport_label()))
        rec = search_company(term)
        _print_search(rec)
        return 0

    print("[reclame_aqui] fetching reputation for %r via %s ..." % (arg, _transport_label()))
    rec = fetch_reputation(arg)
    _print_reputation(rec)
    if "--json" in argv[1:]:
        _emit_json(rec)
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
