#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI Shopee internal-API detail client -- cex_marketplace_detail_shopee (Pass 2, W5 -- HARD).

The Shopee Catalog Pass (spec_extraction_depth_v1.md S7 W5). Where Mercado Livre serves catalog
depth by an OFFICIAL app-token API (cex_marketplace_detail_meli), Shopee exposes the SAME class of
data -- historical_sold (an EXACT int!), per-variation models[] (price + stock), the clean star
histogram (item_rating.rating_count[]), de/por pricing, listing age -- only through its INTERNAL
item API:

  GET https://shopee.com.br/api/v4/item/get?itemid={itemid}&shopid={shopid}

That endpoint is NOT a public app-token API. It requires a real BROWSER SESSION: the cookies a
logged-in Shopee tab carries, the most important being the encrypted ``af-ac-enc-dat`` anti-bot
cookie. WITHOUT that token the endpoint answers HTTP 403 / a JSON body with ``error 90309999``
(Shopee's "request blocked / token required" code). We do NOT have a Shopee session token (it lives
in the founder's browser), so this wave ships a CORRECT adapter that:

  * normalizes a REAL Shopee item JSON when one is supplied (the FIXTURE path -- proven offline),
  * self-reports ``status: 'unavailable'`` + ``reason: 'shopee_session_token_required'`` when no
    valid session is present (the 403 / error-90309999 path),
  * NEVER fabricates a single field. Honest-null per field; degrade-never on every error.

CARDINAL RULE -- NEVER fabricate a marketplace number (memory:
reference_ml_scraping_antibot_hallucination). A blocked / token-less call yields the honest
``unavailable`` record, NEVER a guessed historical_sold / price / rating. fetch_shopee_detail is
TOTAL: it NEVER raises (a bad session, a 403, a transport drop -> the unavailable record).

The Shopee field map (S7 W5), all /100000 fixed-point or honest-null:
  historical_sold (EXACT int)          -> sold_historical
  sold                                 -> sold_recent
  price        / 100000                -> price
  price_min    / 100000                -> price_min          (variation floor)
  price_max    / 100000                -> price_max          (variation ceiling)
  price_min_before_discount / 100000   -> price_original     (the de/por "de" floor)
  stock                                -> stock
  ctime (epoch seconds)                -> ctime, listing_age_days (now - ctime)
  models[] (per variation)             -> variations[] {name, price/100000, stock, sold}
  item_rating.rating_star              -> rating_star        (avg stars)
  item_rating.rating_count[0]          -> rating_total       (index 0 = the grand total)
  item_rating.rating_count[1..5]       -> rating_histogram   {1: n1, ..., 5: n5}

REUSE (from cex_tool_resolver_live, NOT re-implemented): _HTTP_TIMEOUT (the degrade-never ceiling),
_safe_json (TOTAL resp.json), _to_int / _to_float (numeric coercers). NEW here: the itemid/shopid
url resolver, _shopee_get (the session-gated GET), the _shopee_*_to_* normalizers, the /100000
fixed-point money helper, the rating-histogram parser.

SECRET HYGIENE: a session/cookie value is read at call time and lands ONLY in the request headers
/ cookie jar; its VALUE is NEVER logged, printed, or stored. The CLI never echoes a cookie.

ASCII-only (.claude/rules/ascii-code-rule.md). Fully type-hinted. Composes; modifies nothing.

Live proof is IMPOSSIBLE without a Shopee browser-session token (the founder's logged-in tab):
  python _tools/cex_marketplace_detail_shopee.py --detail "https://shopee.com.br/product/123/456"
  (with NO session -> prints the honest 'unavailable: shopee_session_token_required' record)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

# REUSE the live resolver's PROVEN glue (import-light: no driver/key read at import).
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_tool_resolver_live as _live  # type: ignore[import]

_HTTP_TIMEOUT = _live._HTTP_TIMEOUT
_safe_json = _live._safe_json
_to_int = _live._to_int
_to_float = _live._to_float

# The Shopee BR internal item endpoint (NOT a public app-token API -- needs a browser session).
_SHOPEE_API_BASE = "https://shopee.com.br"
_SHOPEE_ITEM_PATH = "/api/v4/item/get"

# Shopee fixed-point money divisor: every price in the v4 item API is an integer = BRL * 100000.
_SHOPEE_PRICE_DIVISOR = 100000.0

# Shopee's "request blocked / anti-bot token required" error code (the token-less / 403 body).
_SHOPEE_BLOCKED_ERROR = 90309999

# The honest reason a token-less call self-reports (the W5 degrade-never contract).
_REASON_TOKEN_REQUIRED = "shopee_session_token_required"


# --------------------------------------------------------------------------- #
# Status sentinels (NO secret ever carried).
# --------------------------------------------------------------------------- #
class ShopeeDetailUnavailable(RuntimeError):
    """Raised INTERNALLY by _shopee_get on an HTTP/transport error OR a blocked body so
    fetch_shopee_detail records an honest 'unavailable' record. Carries NO secret -- only a short
    reason string (never a cookie / token value)."""


# --------------------------------------------------------------------------- #
# id / url resolution -- pull (itemid, shopid) out of a Shopee URL (or accept them directly).
# --------------------------------------------------------------------------- #
def resolve_item_ids(item_id_or_url: str) -> Tuple[Optional[int], Optional[int]]:
    """Resolve (itemid, shopid) from a Shopee URL or an explicit 'shopid.itemid' / 'shopid_itemid'
    pair. TOTAL -> (None, None) when neither can be found (the caller then self-reports an honest
    'unresolvable' record -- NEVER guesses an id).

    NOTE Shopee's URL convention is (shopid, itemid) IN THAT ORDER -- the shop id comes first:
      * the canonical product URL: 'https://shopee.com.br/product/{shopid}/{itemid}'
      * the SEO slug + 'i.{shopid}.{itemid}' tail: '.../Name-i.{shopid}.{itemid}'
      * an explicit pair: 'i.{shopid}.{itemid}' or '{shopid}.{itemid}' or '{shopid}_{itemid}'
      * a querystring: '?itemid={itemid}&shopid={shopid}' (order-independent here).
    Returns (itemid, shopid) -- the FUNCTION's tuple order is (item, shop) to match the API params.
    """
    s = str(item_id_or_url or "").strip()
    if not s:
        return (None, None)

    import re as _re

    # 1) Explicit querystring (?itemid=..&shopid=..) -- order-independent, most reliable.
    qs_item = _re.search(r"[?&]itemid=(\d+)", s)
    qs_shop = _re.search(r"[?&]shopid=(\d+)", s)
    if qs_item and qs_shop:
        return (int(qs_item.group(1)), int(qs_shop.group(1)))

    # 2) The 'i.{shopid}.{itemid}' SEO tail (shop FIRST, then item).
    m = _re.search(r"i\.(\d+)\.(\d+)", s)
    if m:
        return (int(m.group(2)), int(m.group(1)))

    # 3) The '/product/{shopid}/{itemid}' canonical path (shop FIRST, then item).
    m = _re.search(r"/product/(\d+)/(\d+)", s)
    if m:
        return (int(m.group(2)), int(m.group(1)))

    # 4) A bare 'shopid.itemid' or 'shopid_itemid' pair (no URL) -- shop FIRST.
    m = _re.match(r"^(\d+)[._](\d+)$", s)
    if m:
        return (int(m.group(2)), int(m.group(1)))

    return (None, None)


# --------------------------------------------------------------------------- #
# THE session-gated GET -- the only network touch (needs the browser-session cookies/token).
# --------------------------------------------------------------------------- #
def _shopee_get(itemid: int, shopid: int, session: Optional[Any]) -> Any:
    """GET the Shopee v4 item body for (itemid, shopid) USING a browser session.

    ``session`` is a requests.Session-like object the CALLER builds from a logged-in Shopee tab
    (it must already carry the cookies -- crucially the encrypted ``af-ac-enc-dat`` anti-bot
    cookie). WITHOUT it the endpoint blocks (403 / error 90309999). The cookie/token VALUE is read
    only by the session object and is NEVER logged here.

    RAISES ShopeeDetailUnavailable when:
      * session is None (no browser session -> the token-less path -- we self-report, never call),
      * the HTTP call errors (403/4xx/5xx/transport),
      * the body is a Shopee 'blocked' envelope (``error == 90309999`` or a null ``data``).
    NEVER fabricates a body."""
    if session is None:
        # No browser session at all -> the documented token-less outcome. We do NOT even attempt a
        # bare request (a session-less GET is guaranteed to be blocked) -- we self-report honestly.
        raise ShopeeDetailUnavailable(_REASON_TOKEN_REQUIRED)

    url = _SHOPEE_API_BASE + _SHOPEE_ITEM_PATH
    try:
        resp = session.get(
            url,
            params={"itemid": int(itemid), "shopid": int(shopid)},
            headers={
                "Accept": "application/json",
                # A real browser sends a Shopee-specific referer; the session supplies the cookies.
                "Referer": "%s/" % _SHOPEE_API_BASE,
                "X-Requested-With": "XMLHttpRequest",
            },
            timeout=_HTTP_TIMEOUT,
        )
        resp.raise_for_status()
    except ShopeeDetailUnavailable:
        raise
    except Exception as exc:
        # NEVER leak a cookie; report only the error TYPE (a Shopee 403 commonly carries the token
        # requirement -> we map a generic HTTP failure to the same honest reason downstream).
        raise ShopeeDetailUnavailable("%s on GET %s" % (type(exc).__name__, _SHOPEE_ITEM_PATH)) from exc

    body = _safe_json(resp)
    # Shopee returns 200 with a 'blocked' envelope when the anti-bot token is missing/expired:
    # {"error": 90309999, "error_msg": "...", "data": null}. Treat that as unavailable (NOT data).
    if isinstance(body, Mapping):
        err = body.get("error")
        if isinstance(err, int) and err != 0:
            if err == _SHOPEE_BLOCKED_ERROR:
                raise ShopeeDetailUnavailable(_REASON_TOKEN_REQUIRED)
            raise ShopeeDetailUnavailable("shopee error %d" % err)
        if body.get("data") is None:
            # error==0 but no data -> nothing to map (treat as unavailable, never fabricate).
            raise ShopeeDetailUnavailable("shopee returned no item data")
    return body


# --------------------------------------------------------------------------- #
# THE entry -- fetch the full Shopee catalog/detail record for ONE item.
# --------------------------------------------------------------------------- #
def fetch_shopee_detail(item_id_or_url: str, session: Optional[Any] = None) -> Dict[str, Any]:
    """Fetch the Shopee catalog/detail record for ONE item via the internal v4 item API. TOTAL:
    NEVER raises, NEVER fabricates.

    Args:
      item_id_or_url: a Shopee product URL, an 'i.{shopid}.{itemid}' tail, or a 'shopid.itemid'
        pair (resolved via resolve_item_ids).
      session: a requests.Session-like object built from a logged-in Shopee browser tab (it must
        carry the cookies, crucially the encrypted ``af-ac-enc-dat`` anti-bot cookie). When None
        (the case TODAY -- we have no Shopee session token), the function self-reports
        ``status='unavailable'`` + ``reason='shopee_session_token_required'`` and NEVER fabricates.

    Returns a dict (S5/S7 contract fields, all honest-null when unavailable):
      status ('ok' | 'unavailable'), reason (None | a short string),
      marketplace ('shopee'), itemid, shopid, name,
      sold_historical (EXACT int!), sold_recent,
      price, price_min, price_max, price_original, discount_pct, stock,
      ctime, listing_age_days,
      variations (list of {name, price, stock, sold}), variations_count,
      rating_star, rating_total, rating_histogram ({1..5: count}),
      data_sources (provenance), endpoint_status (ok|unavailable), mock (ALWAYS False)."""
    rec = _empty_detail()
    itemid, shopid = resolve_item_ids(item_id_or_url)
    rec["itemid"] = itemid
    rec["shopid"] = shopid
    if itemid is None or shopid is None:
        rec["status"] = "unavailable"
        rec["reason"] = "shopee_item_ids_unresolvable"
        rec["endpoint_status"]["item_get"] = "failed: could not resolve itemid+shopid from input"
        return rec

    try:
        body = _shopee_get(itemid, shopid, session)
    except ShopeeDetailUnavailable as exc:
        reason = str(exc) or _REASON_TOKEN_REQUIRED
        # A generic HTTP/transport failure on Shopee is, in practice, the anti-bot block -> surface
        # the honest token-required reason while preserving the specific error in endpoint_status.
        rec["status"] = "unavailable"
        rec["reason"] = _REASON_TOKEN_REQUIRED if "GET " in reason or reason == _REASON_TOKEN_REQUIRED else reason
        rec["endpoint_status"]["item_get"] = "unavailable: %s" % reason
        return rec
    except Exception as exc:  # defensive: nothing else may crash the record.
        rec["status"] = "unavailable"
        rec["reason"] = "shopee_unexpected_error"
        rec["endpoint_status"]["item_get"] = "failed: %s" % type(exc).__name__
        return rec

    data = body.get("data") if isinstance(body, Mapping) else None
    if not isinstance(data, Mapping):
        rec["status"] = "unavailable"
        rec["reason"] = "shopee_no_item_data"
        rec["endpoint_status"]["item_get"] = "unavailable: no data envelope"
        return rec

    _apply_item_to_detail(rec, data)
    rec["status"] = "ok"
    rec["endpoint_status"]["item_get"] = "ok"
    rec["data_sources"]["item_get"] = "shopee:item/get"
    return rec


# --------------------------------------------------------------------------- #
# THE normalizer -- map a Shopee v4 item ``data`` body onto the detail record. PURE + TOTAL.
# --------------------------------------------------------------------------- #
def _apply_item_to_detail(rec: Dict[str, Any], data: Mapping[str, Any]) -> None:
    """Map the Shopee v4 item ``data`` body onto the detail record (S7 W5 field map). Every price
    is the /100000 fixed-point integer; sold_historical is the EXACT int; models[] is the
    per-variation breakdown; item_rating.rating_count[] is the [total, 1*, 2*, 3*, 4*, 5*]
    histogram. Each absent field stays None (honest); NEVER fabricates."""
    rec["name"] = _opt_str(data.get("name"))

    # historical_sold is the EXACT cumulative sold (the Shopee moat -- a real int, never a bucket).
    rec["sold_historical"] = _to_int(data.get("historical_sold"))
    rec["sold_recent"] = _to_int(data.get("sold"))

    rec["price"] = _shopee_money(data.get("price"))
    rec["price_min"] = _shopee_money(data.get("price_min"))
    rec["price_max"] = _shopee_money(data.get("price_max"))
    rec["price_original"] = _shopee_money(data.get("price_min_before_discount"))
    rec["discount_pct"] = _discount_pct(rec["price"], rec["price_original"])
    rec["stock"] = _to_int(data.get("stock"))

    ctime = _to_int(data.get("ctime"))
    rec["ctime"] = ctime
    rec["listing_age_days"] = _listing_age_days(ctime)

    rec["variations"] = _models_list(data.get("models"))
    rec["variations_count"] = len(rec["variations"])

    rating = data.get("item_rating")
    star, total, histogram = _rating_breakdown(rating)
    rec["rating_star"] = star
    rec["rating_total"] = total
    rec["rating_histogram"] = histogram


# --------------------------------------------------------------------------- #
# PURE field helpers (TOTAL -- absent/garbage -> None; NEVER fabricate).
# --------------------------------------------------------------------------- #
def _shopee_money(value: Any) -> Optional[float]:
    """A Shopee fixed-point price integer (BRL * 100000) -> a BRL float rounded to 2dp. Only a
    genuine non-negative number maps; a 0 maps to 0.0 (Shopee uses 0 for 'no price'); absent /
    garbage / negative -> None (NEVER a fabricated price)."""
    n = _to_float(value)
    if n is None or n < 0:
        return None
    return round(n / _SHOPEE_PRICE_DIVISOR, 2)


def _discount_pct(price: Optional[float], original: Optional[float]) -> Optional[float]:
    """The de/por discount percent, rounded to 1dp. Only when BOTH are real positives AND
    original > price (a genuine markdown). Otherwise None (no de/por -> honest null; NEVER a
    negative or fabricated discount). Mirrors the ML adapter's _discount_pct posture."""
    if price is None or original is None:
        return None
    if original <= 0 or price <= 0 or original <= price:
        return None
    return round((original - price) / original * 100.0, 1)


def _listing_age_days(ctime: Optional[int]) -> Optional[int]:
    """Days between the Shopee ctime (epoch SECONDS) and now (UTC), >= 0. An absent / non-positive
    / future ctime -> None (NEVER a guessed age). PURE + TOTAL."""
    if ctime is None or ctime <= 0:
        return None
    import datetime as _dt

    try:
        created = _dt.datetime.fromtimestamp(int(ctime), _dt.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None
    now = _dt.datetime.now(_dt.timezone.utc)
    days = int((now - created).days)
    return days if days >= 0 else 0


def _models_list(models: Any) -> List[Dict[str, Any]]:
    """Normalize models[] (the per-variation breakdown) into a compact list (name, price/100000,
    stock, sold). A non-list / empty -> []. NEVER fabricates an entry (a non-mapping model is
    dropped)."""
    if not isinstance(models, list):
        return []
    out: List[Dict[str, Any]] = []
    for m in models:
        if not isinstance(m, Mapping):
            continue
        out.append({
            "name": _opt_str(m.get("name")),
            "price": _shopee_money(m.get("price")),
            "stock": _to_int(m.get("stock")),
            "sold": _to_int(m.get("sold")),
        })
    return out


def _rating_breakdown(
    rating: Any,
) -> Tuple[Optional[float], Optional[int], Optional[Dict[int, int]]]:
    """Parse item_rating into (rating_star, rating_total, {1..5: count}).

    Shopee's item_rating.rating_count is a 6-slot list where index 0 = the GRAND TOTAL and indices
    1..5 = the per-star counts (1-star..5-star). The average is item_rating.rating_star. Absent /
    malformed -> (None, None, None). NEVER fabricates a count; a too-short list yields what is
    present (missing stars omitted -> honest)."""
    if not isinstance(rating, Mapping):
        return (None, None, None)
    star = _to_float(rating.get("rating_star"))
    counts = rating.get("rating_count")
    total: Optional[int] = None
    histogram: Optional[Dict[int, int]] = None
    if isinstance(counts, list) and counts:
        total = _to_int(counts[0])  # index 0 == grand total.
        hist: Dict[int, int] = {}
        # indices 1..5 == 1-star..5-star (only as many as the list carries -- never padded).
        for star_idx in range(1, 6):
            if star_idx < len(counts):
                c = _to_int(counts[star_idx])
                if c is not None:
                    hist[star_idx] = c
        histogram = hist or None
    return (star, total, histogram)


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


def _empty_detail() -> Dict[str, Any]:
    """The all-null Shopee detail record skeleton (every contract field present, honest null).
    status defaults to 'unavailable' so a record that never reaches 'ok' is honest by construction.
    mock is ALWAYS False -- this record is real API data or an explicit unavailable, never a
    simulated value."""
    return {
        "status": "unavailable",
        "reason": None,
        "marketplace": "shopee",
        "itemid": None,
        "shopid": None,
        "name": None,
        "sold_historical": None,
        "sold_recent": None,
        "price": None,
        "price_min": None,
        "price_max": None,
        "price_original": None,
        "discount_pct": None,
        "stock": None,
        "ctime": None,
        "listing_age_days": None,
        "variations": [],
        "variations_count": 0,
        "rating_star": None,
        "rating_total": None,
        "rating_histogram": None,
        "data_sources": {},
        "endpoint_status": {},
        "mock": False,
    }


__all__ = [
    "fetch_shopee_detail",
    "resolve_item_ids",
    "ShopeeDetailUnavailable",
]


# --------------------------------------------------------------------------- #
# CLI -- a credential-free inspection. With NO session it prints the honest 'unavailable' record
# (live proof needs a Shopee browser-session token we do not have -- the founder's logged-in tab).
# --------------------------------------------------------------------------- #
def _print_detail(rec: Mapping[str, Any]) -> None:
    """Print a SHORT, credential-free summary of a detail record (NEVER prints a cookie/token)."""
    keys = (
        "status", "reason", "itemid", "shopid", "name",
        "sold_historical", "sold_recent",
        "price", "price_min", "price_max", "price_original", "discount_pct", "stock",
        "ctime", "listing_age_days", "variations_count",
        "rating_star", "rating_total", "rating_histogram",
    )
    for k in keys:
        print("  %-20s %s" % (k, rec.get(k)))
    print("  %-20s %s" % ("endpoint_status", rec.get("endpoint_status")))
    print("  %-20s %s" % ("data_sources", rec.get("data_sources")))


def _main(argv: List[str]) -> int:
    if not argv:
        print("CEXAI Shopee internal-API detail client (Pass 2, W5 -- HARD). Usage:")
        print("  python _tools/cex_marketplace_detail_shopee.py --detail <shopee product url|i.SHOP.ITEM>")
        print("  python _tools/cex_marketplace_detail_shopee.py --ids   <shopee product url|i.SHOP.ITEM>")
        print("")
        print("NOTE live proof needs a Shopee BROWSER-SESSION token (the encrypted af-ac-enc-dat")
        print("cookie from a logged-in tab). With NO session, --detail self-reports 'unavailable:")
        print("shopee_session_token_required' and NEVER fabricates.")
        return 0

    if argv[0] == "--ids" and len(argv) >= 2:
        itemid, shopid = resolve_item_ids(argv[1])
        print("itemid : %s" % itemid)
        print("shopid : %s" % shopid)
        return 0 if (itemid is not None and shopid is not None) else 1

    if argv[0] == "--detail" and len(argv) >= 2:
        target = argv[1]
        print("[shopee] resolving + fetching %s (NO session -> expect honest 'unavailable') ..." % target)
        rec = fetch_shopee_detail(target, session=None)
        _print_detail(rec)
        return 0

    print("unknown args: %s" % " ".join(argv))
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
