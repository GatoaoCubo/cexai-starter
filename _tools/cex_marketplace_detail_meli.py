#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI Mercado Livre OFFICIAL detail client -- cex_marketplace_detail_meli (Pass 2, W1+W2).

THE ML Catalog Pass (spec_extraction_depth_v1.md S3). The research engine today reads only the
SEARCH surface (the results grid -- title, integer-reais price, seller name, coarse badges). This
module opens the CATALOG level for ONE listing via the Mercado Livre OFFICIAL API -- the verdict
is decisive: 90% of the extraction gap lives at catalog depth, and ML serves it by official API
(NO scraping, NO fabrication). Only /sites/MLB/search is restricted (0 results); the item/catalog
/user endpoints below are NOT search and DO return data for any public id with the app token that
get_meli_token() already mints (client_credentials, 6h, cached).

The 4 endpoints (S3 E1-E4):
  E1 GET /items/{id}/price_to_win              -> buy_box {winner_item_id, price, status}
  E2 GET /products/{catalog_product_id}/items  -> num_sellers (paging.total) + sellers[] + sold sum
  E3 GET /items/{id}                           -> catalog_product_id, date_created (listing age),
                                                  logistic_type, price/original_price, sold/avail,
                                                  installments, variations[], attributes[], category
  E4 GET /users/{seller_id}                    -> power_seller_status (MercadoLider),
                                                  seller_reputation.level_id, transactions.total

CARDINAL RULE -- NEVER fabricate a marketplace number (memory:
reference_ml_scraping_antibot_hallucination). Every field is captured-AND-real or an honest
``null`` with provenance. A 4xx / missing field / non-mapping body -> that field is None, the call
records its failure in ``data_sources`` / ``endpoint_status``, and fetch_detail continues. fetch_detail
is TOTAL: it NEVER raises (the only thing that can fail it -- a bad token -- yields an all-null record
with a recorded failure, never a guess).

REUSE (from cex_tool_resolver_live, NOT re-implemented): get_meli_token (the app-token mint+cache),
_HTTP_TIMEOUT (the degrade-never ceiling), _safe_json (TOTAL resp.json), _to_int / _to_float (the
numeric coercers), the Bearer/never-log discipline. NEW here: _meli_get (a generic GET helper for
arbitrary item paths) + the _meli_*_to_* normalizers + the per-run seller cache.

SECRET HYGIENE: the token is read at call time via get_meli_token and lands ONLY in the
Authorization header; its VALUE is NEVER logged, printed, or stored.

ASCII-only (.claude/rules/ascii-code-rule.md). Fully type-hinted. Composes; modifies nothing.

Live proof (the orchestrator runs this -- real network, app token works for ITEM endpoints; the
/search API is restricted but these are NOT search):
  python _tools/cex_marketplace_detail_meli.py --detail MLBxxxxxxxxx
  python _tools/cex_marketplace_detail_meli.py --probe "comedouro gato inox"
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

# REUSE the live resolver's PROVEN ML glue (import-light: no driver/key read at import).
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_tool_resolver_live as _live  # type: ignore[import]

get_meli_token = _live.get_meli_token  # the app-token mint + cache (reused verbatim)
_HTTP_TIMEOUT = _live._HTTP_TIMEOUT
_safe_json = _live._safe_json
_to_int = _live._to_int
_to_float = _live._to_float

# The ML official API base (the item / catalog / user endpoints live here -- NOT the restricted
# /sites/MLB/search). All GETs carry the Bearer app token; the value is NEVER logged.
_MELI_API_BASE = "https://api.mercadolibre.com"

# The catalog products/items page size (paging.total carries the true seller count regardless).
_PRODUCTS_ITEMS_LIMIT = 50

# The buy-box statuses ML reports on price_to_win (the item's standing vs the winner).
_BUY_BOX_STATUSES = ("winning", "sharing", "competing", "listed")

# SECURITY (response-sourced id validation): ids that come back INSIDE an API RESPONSE body
# (catalog_product_id / seller_id) are interpolated into the NEXT request's path
# (/products/{id}/items, /users/{id}). A malicious/garbled response could carry a crafted value
# (e.g. catalog_product_id='../oauth/token') that would traverse the path. Unlike the user-entry
# resolve_item_id (which hard-validates), the response-sourced ids were trusted verbatim. These
# strict full-match patterns gate every response-sourced id BEFORE it is interpolated: a catalog
# product id is MLB + digits; a seller id is digits only. A value that fails -> the call is NOT
# issued and the field stays an honest null (NEVER fabricated, NEVER traversed).
import re as _re_id  # module-level (ASCII): compiled once, used by the id validators.

_RE_CATALOG_ID = _re_id.compile(r"MLB\d+")     # catalog product id: 'MLB' + digits (no dash here).
_RE_SELLER_ID = _re_id.compile(r"\d+")          # seller id: digits only.


def _valid_catalog_id(value: Any) -> Optional[str]:
    """A response-sourced catalog_product_id that is SAFE to interpolate into a path, or None.
    Accepts ONLY '^MLB\\d+$' (re.fullmatch). A non-string / traversal / empty -> None (the caller
    then skips the /products/{id}/items call and keeps the field null). PURE + TOTAL."""
    if not isinstance(value, str):
        return None
    s = value.strip()
    return s if _RE_CATALOG_ID.fullmatch(s) else None


def _valid_seller_id(value: Any) -> Optional[str]:
    """A response-sourced seller_id that is SAFE to interpolate into /users/{id}, or None. Accepts
    ONLY '^\\d+$' (re.fullmatch). A non-string / 'a/../b' / empty -> None (the caller then skips the
    /users/{id} call and keeps the seller fields null). PURE + TOTAL."""
    if not isinstance(value, str):
        return None
    s = value.strip()
    return s if _RE_SELLER_ID.fullmatch(s) else None


# --------------------------------------------------------------------------- #
# Errors / status sentinels (NO secret ever carried).
# --------------------------------------------------------------------------- #
class MeliDetailUnavailable(RuntimeError):
    """Raised INTERNALLY by _meli_get on an HTTP/transport error so each endpoint can record an
    honest per-endpoint failure. fetch_detail catches it (degrade-never) -> the field stays None.
    Carries NO secret -- only the path + the failure reason string."""


# --------------------------------------------------------------------------- #
# THE generic GET helper -- the _meli_search posture generalized to arbitrary item paths.
# --------------------------------------------------------------------------- #
def _meli_get(path: str, token: str, *, params: Optional[Mapping[str, Any]] = None) -> Any:
    """GET an ML official-API path with the Bearer app token; return the parsed JSON body.

    Mirrors the _meli_search HTTP posture EXACTLY (timeout=_HTTP_TIMEOUT, raise_for_status,
    _safe_json, 'Authorization: Bearer <token>' + 'Accept: application/json'). The token lands
    ONLY in the header; its value is NEVER logged.

    RAISES MeliDetailUnavailable on ANY HTTP / transport error (a 4xx for a missing/forbidden id,
    a 5xx, a network drop) so the caller records an honest per-endpoint failure and degrades to a
    null field. NEVER fabricates a body."""
    import requests  # type: ignore[import]  # lazy (offline-import friendly)

    url = _MELI_API_BASE + (path if path.startswith("/") else "/" + path)
    try:
        resp = requests.get(
            url,
            headers={"Authorization": "Bearer %s" % token, "Accept": "application/json"},
            params=dict(params) if params else None,
            timeout=_HTTP_TIMEOUT,
        )
        resp.raise_for_status()
    except Exception as exc:
        # NEVER leak the token; report only the path + the error TYPE (status code stays out of
        # the message because some HTTPError reprs echo the full URL with query params).
        raise MeliDetailUnavailable("%s on GET %s" % (type(exc).__name__, path)) from exc
    return _safe_json(resp)


# --------------------------------------------------------------------------- #
# id / url resolution -- pull the MLB item id out of a /p/ or /MLB url (or pass an id through).
# --------------------------------------------------------------------------- #
def resolve_item_id(item_id_or_url: str) -> Optional[str]:
    """Resolve a usable ML item id (``MLB`` + digits) from a raw id OR a listing URL. TOTAL ->
    None when no MLB id can be found (the caller then records an honest 'no item id' failure --
    NEVER guesses one).

    Accepts:
      * a bare id: 'MLB1234567890' (returned uppercased, whitespace-stripped).
      * a product/listing URL: 'https://www.mercadolivre.com.br/.../p/MLB1234567890' or
        '.../MLB-1234567890-...' (the dashed catalog-URL form -> the dash is dropped).
    """
    s = str(item_id_or_url or "").strip()
    if not s:
        return None
    upper = s.upper()
    # Fast path: the whole token already IS an MLB id (optionally with a single dash after MLB).
    bare = upper.replace("MLB-", "MLB")
    if bare.startswith("MLB") and bare[3:].isdigit() and len(bare) > 3:
        return bare
    # URL / mixed string: scan for the FIRST 'MLB' followed by digits (a leading dash is allowed
    # -- the dashed catalog URL form 'MLB-1234' -- and folded out).
    import re as _re

    m = _re.search(r"MLB-?(\d{6,})", upper)
    if m:
        return "MLB" + m.group(1)
    return None


# --------------------------------------------------------------------------- #
# THE entry -- fetch the full catalog/detail record for ONE listing.
# --------------------------------------------------------------------------- #
def fetch_detail(
    item_id_or_url: str,
    token: Optional[str] = None,
    *,
    seller_cache: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Fetch the ML catalog/detail record for ONE listing (E3 core + E1 buy-box + E2 sellers +
    E4 reputation), mapped onto the extended contract fields (spec S5). TOTAL: NEVER raises,
    NEVER fabricates -- a 4xx / missing field yields an honest ``null`` + a recorded provenance
    failure, and the function continues.

    Args:
      item_id_or_url: an MLB item id OR a listing/product URL (resolved via resolve_item_id).
      token: an explicit ML app token (OPTIONAL); when None, get_meli_token() mints/reads one.
      seller_cache: an optional per-RUN cache (seller_id -> E4 record) so a seller hit once is
        not re-fetched across many candidates in the same run (S3 E4 rate-limit mitigation).

    Returns a dict with the contract fields (all honest-null when unavailable):
      item_id, catalog_product_id, catalog_listing,
      buy_box_winner, buy_box_status,
      num_sellers, sold_exact, sold_bucket, available_quantity,
      date_created, listing_age_days, logistic_type, category_id,
      price, price_original, discount_pct, installments,
      variations, variations_count, attributes, attributes_count,
      seller_id, seller_reputation, seller_power_status, seller_sales_total, seller_location,
      data_sources (provenance per endpoint), endpoint_status (ok|failed|skipped per endpoint),
      mock (ALWAYS False -- this is real API or an honest null, never a simulated value)."""
    rec = _empty_detail()
    item_id = resolve_item_id(item_id_or_url)
    rec["item_id"] = item_id
    if item_id is None:
        rec["endpoint_status"]["resolve"] = "failed: no MLB item id in input"
        return rec

    tok = token if (isinstance(token, str) and token.strip()) else get_meli_token()
    if not tok:
        rec["endpoint_status"]["token"] = "failed: no ML token (set MELI_ACCESS_TOKEN or client creds)"
        return rec

    cache: Dict[str, Dict[str, Any]] = seller_cache if isinstance(seller_cache, dict) else {}

    # E3 -- the ficha core (catalog id, dates, logistic, price/original, sold/avail, installments,
    # variations, attributes, category, seller id). Run FIRST: it yields the catalog_product_id E2
    # needs + the seller_id E4 needs.
    item_body = _safe_endpoint(rec, "items", lambda: _meli_get("/items/%s" % item_id, tok))
    if isinstance(item_body, Mapping):
        _apply_item_to_detail(rec, item_body)

    # E1 -- buy-box winner + this item's status vs the winner.
    pw_body = _safe_endpoint(
        rec, "price_to_win", lambda: _meli_get("/items/%s/price_to_win" % item_id, tok)
    )
    if isinstance(pw_body, Mapping):
        _apply_pricetowin_to_detail(rec, pw_body)

    # E2 -- all sellers on the catalog ficha (num_sellers + per-seller + catalog sold sum). Only
    # when E3 surfaced a catalog_product_id (a non-catalog listing has none -> honest null). The
    # catalog_product_id is RESPONSE-SOURCED -> validate '^MLB\d+$' BEFORE interpolating the path
    # (SECURITY: a crafted body could carry a traversal value -> do NOT call, keep the field null).
    catalog_id = _valid_catalog_id(rec.get("catalog_product_id"))
    if catalog_id:
        items_body = _safe_endpoint(
            rec, "products_items",
            lambda: _meli_get(
                "/products/%s/items" % catalog_id, tok, params={"limit": _PRODUCTS_ITEMS_LIMIT}
            ),
        )
        if isinstance(items_body, Mapping):
            _apply_products_items_to_detail(rec, items_body)
    elif isinstance(rec.get("catalog_product_id"), str) and rec.get("catalog_product_id"):
        rec["endpoint_status"]["products_items"] = "skipped: invalid catalog_product_id (not ^MLB\\d+$)"
    else:
        rec["endpoint_status"]["products_items"] = "skipped: not a catalog ficha (no catalog_product_id)"

    # E4 -- the seller reputation / MercadoLider tier / total sales (cache per seller per run). The
    # seller_id is RESPONSE-SOURCED -> validate '^\d+$' BEFORE interpolating /users/{id} (SECURITY:
    # a crafted body could carry '1/../x' -> do NOT call, keep the seller fields null).
    seller_id = _valid_seller_id(rec.get("seller_id"))
    if seller_id:
        user_rec = _fetch_user_cached(rec, seller_id, tok, cache)
        if isinstance(user_rec, Mapping):
            _apply_user_to_detail(rec, user_rec)
    elif isinstance(rec.get("seller_id"), str) and rec.get("seller_id"):
        rec["endpoint_status"]["users"] = "skipped: invalid seller_id (not ^\\d+$)"
    else:
        rec["endpoint_status"]["users"] = "skipped: no seller_id from item"

    return rec


def fetch_catalog_detail(
    catalog_product_id_or_url: str,
    token: Optional[str] = None,
    *,
    seller_cache: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Fetch the catalog/detail record keyed by CATALOG PRODUCT id (the app-token path).

    LIVE-VERIFIED (2026-06-19): with the client_credentials APP token, the ITEM endpoints
    GET /items/{id} (E3) + /items/{id}/price_to_win (E1) return HTTP 403 access_denied (E1 only
    serves the caller's OWN items), but the CATALOG endpoints GET /products/{id}/items (E2),
    GET /products/{id}, and GET /users/{seller_id} (E4) return HTTP 200 real data. So when only
    the app token is available, this is the entry that WORKS: it reads num_sellers + per-seller
    price/original_price/logistic_type/category + the buy-box seller (the lowest-price seller on
    the catalog as an honest proxy when price_to_win is forbidden) + the top seller's reputation.

    Use fetch_detail(item_id) instead when a USER token is present (it unlocks E1+E3 for the full
    buy-box + listing age + variations + attributes). This function never fabricates: an endpoint
    403/4xx -> the field stays null + endpoint_status records it; TOTAL (never raises).

    Args:
      catalog_product_id_or_url: an MLB catalog product id (e.g. 'MLB52110393') OR a /p/ URL.
      token: an explicit ML token (OPTIONAL); when None, get_meli_token() is used.
      seller_cache: optional per-run seller cache (seller_id -> E4 record).
    """
    rec = _empty_detail()
    catalog_id = resolve_item_id(catalog_product_id_or_url)  # same MLB-id extractor (catalog ids are MLBxxx)
    rec["catalog_product_id"] = catalog_id
    if catalog_id is None:
        rec["endpoint_status"]["resolve"] = "failed: no MLB catalog id in input"
        return rec

    tok = token if (isinstance(token, str) and token.strip()) else get_meli_token()
    if not tok:
        rec["endpoint_status"]["token"] = "failed: no ML token (set MELI_ACCESS_TOKEN or client creds)"
        return rec

    cache: Dict[str, Dict[str, Any]] = seller_cache if isinstance(seller_cache, dict) else {}

    # /products/{id} -- the catalog header (name, domain, category). Optional context; failure is
    # non-fatal (the field map below does not depend on it for the core metrics).
    prod_body = _safe_endpoint(rec, "product", lambda: _meli_get("/products/%s" % catalog_id, tok))
    if isinstance(prod_body, Mapping):
        rec["category_id"] = _opt_str(prod_body.get("domain_id")) or rec.get("category_id")
        rec["catalog_name"] = _opt_str(prod_body.get("name"))

    # E2 -- /products/{id}/items: num_sellers + per-seller + the lowest-price seller as the buy-box
    # proxy (honest: labelled 'lowest_price_proxy' because price_to_win is app-token-forbidden).
    items_body = _safe_endpoint(
        rec, "products_items",
        lambda: _meli_get(
            "/products/%s/items" % catalog_id, tok, params={"limit": _PRODUCTS_ITEMS_LIMIT}
        ),
    )
    if isinstance(items_body, Mapping):
        _apply_products_items_to_detail(rec, items_body)
        _apply_catalog_buybox_proxy(rec)

    # E4 -- the buy-box-proxy seller's reputation (cache per seller per run). The seller_id is
    # RESPONSE-SOURCED (from the E2 lowest-price seller) -> validate '^\d+$' BEFORE interpolating
    # /users/{id} (SECURITY: a crafted body could carry '1/../x' -> do NOT call, keep null).
    seller_id = _valid_seller_id(rec.get("seller_id"))
    if seller_id:
        user_rec = _fetch_user_cached(rec, seller_id, tok, cache)
        if isinstance(user_rec, Mapping):
            _apply_user_to_detail(rec, user_rec)
    elif isinstance(rec.get("seller_id"), str) and rec.get("seller_id"):
        rec["endpoint_status"]["users"] = "skipped: invalid seller_id (not ^\\d+$)"
    else:
        rec["endpoint_status"]["users"] = "skipped: no seller_id from catalog items"

    return rec


def _apply_catalog_buybox_proxy(rec: Dict[str, Any]) -> None:
    """When price_to_win (E1) is forbidden on the app token, derive an HONEST buy-box proxy from
    the E2 sellers: the LOWEST-price seller is the catalog's most-likely winner. It is LABELLED as
    a proxy (buy_box_status='lowest_price_proxy') so it is NEVER presented as the authoritative ML
    buy-box. Also fills rec['seller_id'] / rec['price'] / rec['price_original'] / discount_pct /
    logistic_type from that seller. NEVER fabricates -- absent sellers -> no change."""
    sellers = rec.get("sellers")
    if not isinstance(sellers, list) or not sellers:
        return
    # SECURITY/correctness (bool-as-int): isinstance(True, int) is True, so a seller with
    # price=True (a crafted/garbled payload) would slip through and min() would treat it as 1.0 --
    # fabricating a buy-box price. Exclude bool explicitly so only a REAL numeric price qualifies.
    priced = [
        s for s in sellers
        if isinstance(s, Mapping)
        and isinstance(s.get("price"), (int, float))
        and not isinstance(s.get("price"), bool)
    ]
    if not priced:
        return
    winner = min(priced, key=lambda s: s["price"])
    rec["buy_box_winner"] = winner.get("item_id")
    rec["buy_box_winner_price"] = winner.get("price")
    rec["buy_box_status"] = "lowest_price_proxy"  # honest label: NOT the official price_to_win.
    rec["seller_id"] = winner.get("seller_id")
    rec["price"] = winner.get("price")
    rec["price_original"] = winner.get("original_price")
    rec["discount_pct"] = _discount_pct(rec["price"], rec["price_original"])
    rec["logistic_type"] = winner.get("logistic_type")


# --------------------------------------------------------------------------- #
# Per-endpoint safe runner (records ok / failed in endpoint_status + data_sources).
# --------------------------------------------------------------------------- #
def _safe_endpoint(rec: Dict[str, Any], name: str, call: Any) -> Any:
    """Run ONE endpoint call; record its provenance + status. DEGRADE-NEVER: a
    MeliDetailUnavailable (4xx/5xx/transport) OR any unexpected error -> the endpoint is marked
    'failed: <reason>' and None is returned (the fields it feeds stay null). NEVER fabricates."""
    try:
        body = call()
    except MeliDetailUnavailable as exc:
        rec["endpoint_status"][name] = "failed: %s" % (str(exc) or "unavailable")
        return None
    except Exception as exc:  # defensive: a parse/shape surprise must not crash the record.
        rec["endpoint_status"][name] = "failed: %s" % type(exc).__name__
        return None
    rec["endpoint_status"][name] = "ok"
    rec["data_sources"][name] = "meli:%s" % name
    return body


def _fetch_user_cached(
    rec: Dict[str, Any], seller_id: str, token: str, cache: Dict[str, Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """E4 with a per-run seller cache: a seller fetched once is reused (no second /users call in
    the same run). A cached entry still records provenance honestly ('meli:users (cached)')."""
    cached = cache.get(seller_id)
    if isinstance(cached, Mapping):
        rec["endpoint_status"]["users"] = "ok (cached)"
        rec["data_sources"]["users"] = "meli:users"
        return dict(cached)
    body = _safe_endpoint(rec, "users", lambda: _meli_get("/users/%s" % seller_id, token))
    if isinstance(body, Mapping):
        cache[seller_id] = dict(body)
    return body if isinstance(body, Mapping) else None


# --------------------------------------------------------------------------- #
# E3 -- /items/{id} -> the ficha core. PURE mappers (NEVER fabricate; absent -> None).
# --------------------------------------------------------------------------- #
def _apply_item_to_detail(rec: Dict[str, Any], item: Mapping[str, Any]) -> None:
    """Map the GET /items/{id} body onto the detail record (E3). Reads catalog id, date_created
    (+ derived listing age in days), shipping.logistic_type, price/original_price, sold/available
    (bucketed on the public token -> stored verbatim + labelled), installments, variations[],
    attributes[], category_id, seller id. Each absent field stays None (honest)."""
    rec["catalog_product_id"] = _opt_str(item.get("catalog_product_id"))
    cl = item.get("catalog_listing")
    rec["catalog_listing"] = bool(cl) if isinstance(cl, bool) else None

    rec["date_created"] = _opt_str(item.get("date_created"))
    rec["listing_age_days"] = _listing_age_days(rec["date_created"])

    rec["price"] = _to_float(item.get("price"))
    rec["price_original"] = _to_float(item.get("original_price"))
    rec["discount_pct"] = _discount_pct(rec["price"], rec["price_original"])

    rec["logistic_type"] = _logistic_type(item.get("shipping"))
    rec["category_id"] = _opt_str(item.get("category_id"))

    # sold_quantity / available_quantity are BUCKETED on the public token -> store verbatim, label
    # honestly, NEVER interpolate inside a bucket. Only a GENUINE integer (an int, or a pure-digit
    # string) is treated as exact; a bucket label ('+100', 'mais de 100') is kept verbatim as a
    # string and NEVER coerced (E2's catalog sum is the better exact source and OVERWRITES
    # sold_exact when present -- see _apply_products_items_to_detail).
    sold_exact, sold_bucket = _exact_or_bucket(item.get("sold_quantity"))
    rec["sold_exact"] = sold_exact
    rec["sold_bucket"] = sold_bucket
    avail = item.get("available_quantity")
    rec["available_quantity"] = str(avail) if avail is not None else None

    rec["installments"] = _installments_label(item.get("installments"))
    variations = item.get("variations")
    rec["variations"] = _variations_list(variations)
    rec["variations_count"] = len(rec["variations"]) if rec["variations"] else 0
    attributes = item.get("attributes")
    rec["attributes"] = _attributes_obj(attributes)
    rec["attributes_count"] = len(rec["attributes"]) if rec["attributes"] else 0

    rec["seller_id"] = _opt_str(item.get("seller_id"))


# --------------------------------------------------------------------------- #
# E1 -- /items/{id}/price_to_win -> buy-box.
# --------------------------------------------------------------------------- #
def _apply_pricetowin_to_detail(rec: Dict[str, Any], pw: Mapping[str, Any]) -> None:
    """Map GET /items/{id}/price_to_win onto buy_box_* (E1). The winning seller's item id + the
    buy-box price + THIS item's status vs the winner. Absent -> None. NEVER fabricates."""
    winner = pw.get("winner")
    winner_item = None
    winner_price = None
    if isinstance(winner, Mapping):
        winner_item = _opt_str(winner.get("item_id"))
        winner_price = _to_float(winner.get("price"))
    # The winning item id may also appear at the top level on some shapes.
    if winner_item is None:
        winner_item = _opt_str(pw.get("buy_box_winner_item_id")) or _opt_str(pw.get("item_id"))
    rec["buy_box_winner"] = winner_item
    rec["buy_box_winner_price"] = winner_price if winner_price is not None else _to_float(pw.get("price"))

    status = _opt_str(pw.get("status"))
    if status is not None:
        status = status.lower()
        rec["buy_box_status"] = status if status in _BUY_BOX_STATUSES else status
    else:
        rec["buy_box_status"] = None


# --------------------------------------------------------------------------- #
# E2 -- /products/{catalog_product_id}/items -> all sellers.
# --------------------------------------------------------------------------- #
def _apply_products_items_to_detail(rec: Dict[str, Any], body: Mapping[str, Any]) -> None:
    """Map GET /products/{catalog_id}/items onto num_sellers + sellers[] + the catalog sold sum
    (E2). paging.total IS the true seller count (independent of the page size). The catalog
    sold_exact = sum of every seller's sold_quantity (the better EXACT source than the bucketed
    E3 field -> it overwrites sold_exact when computable). Absent -> None; NEVER fabricates."""
    paging = body.get("paging")
    total = None
    if isinstance(paging, Mapping):
        total = _to_int(paging.get("total"))
    rec["num_sellers"] = total

    results = body.get("results")
    sellers: List[Dict[str, Any]] = []
    sold_sum = 0
    saw_sold = False
    if isinstance(results, list):
        for it in results:
            seller = _products_item_to_seller(it)
            if seller is None:
                continue
            sellers.append(seller)
            s = seller.get("sold_quantity")
            if isinstance(s, int):
                sold_sum += s
                saw_sold = True
    rec["sellers"] = sellers
    # num_sellers floor: when paging.total is absent but we have a result page, the visible count
    # is an HONEST lower bound -> only use it if it is non-zero AND total was missing.
    if rec["num_sellers"] is None and sellers:
        rec["num_sellers"] = len(sellers)
    # Catalog EXACT sold = sum across sellers (the reliable exact figure; the per-item E3 value is
    # bucketed). Only set when at least one seller carried an integer sold (else leave E3's value).
    if saw_sold:
        rec["sold_exact"] = sold_sum
        rec["sold_bucket"] = None  # we now have an exact catalog sum -> the bucket is superseded.


def _products_item_to_seller(item: Any) -> Optional[Dict[str, Any]]:
    """Normalize ONE /products/{id}/items result into a seller record. TOTAL: a non-mapping is
    dropped (NEVER fabricated). Maps seller_id, price, original_price, sold_quantity,
    logistic_type (shipping.logistic_type), official_store_id, seller_address."""
    if not isinstance(item, Mapping):
        return None
    out: Dict[str, Any] = {
        "seller_id": _opt_str(item.get("seller_id")),
        "item_id": _opt_str(item.get("item_id")),
        "price": _to_float(item.get("price")),
        "original_price": _to_float(item.get("original_price")),
        "sold_quantity": _to_int(item.get("sold_quantity")),
        "logistic_type": _logistic_type(item.get("shipping")),
        "official_store_id": _opt_str(item.get("official_store_id")),
        "seller_address": _seller_address(item.get("seller_address")),
    }
    return out


# --------------------------------------------------------------------------- #
# E4 -- /users/{seller_id} -> reputation / MercadoLider / total sales / location.
# --------------------------------------------------------------------------- #
def _apply_user_to_detail(rec: Dict[str, Any], user: Mapping[str, Any]) -> None:
    """Map GET /users/{seller_id} onto seller_reputation (level_id e.g. '5_green'),
    seller_power_status (MercadoLider tier), seller_sales_total (transactions.total),
    seller_location (E4). Absent -> None; NEVER fabricates."""
    rec["seller_power_status"] = _opt_str(user.get("power_seller_status"))
    reputation = user.get("seller_reputation")
    if isinstance(reputation, Mapping):
        rec["seller_reputation"] = _opt_str(reputation.get("level_id"))
        tx = reputation.get("transactions")
        if isinstance(tx, Mapping):
            rec["seller_sales_total"] = _to_int(tx.get("total"))
    addr = user.get("address")
    if isinstance(addr, Mapping):
        city = _opt_str(addr.get("city")) or ""
        state = _opt_str(addr.get("state")) or ""
        loc = ", ".join([p for p in (city, state) if p])
        rec["seller_location"] = loc or None


# --------------------------------------------------------------------------- #
# PURE field helpers (TOTAL -- absent/garbage -> None; NEVER fabricate).
# --------------------------------------------------------------------------- #
def _logistic_type(shipping: Any) -> Optional[str]:
    """shipping.logistic_type -> the FULL/flex string. 'fulfillment' = ML FULL, 'self_service' =
    Flex, 'cross_docking'/'drop_off' etc. pass through verbatim. Absent -> None."""
    if isinstance(shipping, Mapping):
        return _opt_str(shipping.get("logistic_type"))
    return None


def _discount_pct(price: Optional[float], original: Optional[float]) -> Optional[float]:
    """The de/por discount percent, rounded to 1 decimal. Only when BOTH are real positives AND
    original > price (a genuine markdown). Otherwise None (no de/por -> honest null; NEVER a
    negative or fabricated discount)."""
    if price is None or original is None:
        return None
    if original <= 0 or price <= 0 or original <= price:
        return None
    return round((original - price) / original * 100.0, 1)


def _listing_age_days(date_created: Optional[str]) -> Optional[int]:
    """Days between date_created (ISO-8601) and now (UTC), >= 0. A malformed/absent date -> None
    (NEVER a guessed age). Parses the common ML form '2021-03-15T10:00:00.000-03:00' and plain
    'YYYY-MM-DD...' prefixes; degrade-never on anything else."""
    s = str(date_created or "").strip()
    if not s:
        return None
    import datetime as _dt

    parsed: Optional[_dt.datetime] = None
    # Try fromisoformat first (Python 3.7+; ML's '.000-03:00' offset is accepted on 3.11+, and the
    # '.000' millis are accepted on 3.11+). Normalize a trailing 'Z' to +00:00 for older parsers.
    iso = s.replace("Z", "+00:00")
    try:
        parsed = _dt.datetime.fromisoformat(iso)
    except Exception:
        parsed = None
    if parsed is None:
        # Fallback: parse just the YYYY-MM-DD date prefix (10 chars) -- a coarse but honest age.
        try:
            parsed = _dt.datetime.strptime(s[:10], "%Y-%m-%d")
        except Exception:
            return None
    now = _dt.datetime.now(_dt.timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_dt.timezone.utc)
    delta = now - parsed
    days = int(delta.days)
    return days if days >= 0 else 0


def _installments_label(installments: Any) -> Optional[str]:
    """A compact installments label from the ML installments object ('12x R$ 30,65 sem juros').
    Reads quantity + amount + (rate==0 -> 'sem juros'). Absent / no quantity -> None (honest)."""
    if not isinstance(installments, Mapping):
        return None
    qty = _to_int(installments.get("quantity"))
    amount = _to_float(installments.get("amount"))
    if qty is None or qty <= 0:
        return None
    rate = _to_float(installments.get("rate"))
    label = "%dx" % qty
    if amount is not None:
        # BR money rendering: comma decimal, 2 places. ASCII-only (no currency glyph beyond 'R$').
        label += " R$ %s" % _br_money_str(amount)
    if rate is not None and rate == 0:
        label += " sem juros"
    return label


def _variations_list(variations: Any) -> List[Dict[str, Any]]:
    """Normalize variations[] into a compact list (id, price, available_quantity, and the joined
    attribute_combinations as 'name: value'). A non-list / empty -> []. NEVER fabricates an entry."""
    if not isinstance(variations, list):
        return []
    out: List[Dict[str, Any]] = []
    for v in variations:
        if not isinstance(v, Mapping):
            continue
        combos = v.get("attribute_combinations")
        label_parts: List[str] = []
        if isinstance(combos, list):
            for c in combos:
                if not isinstance(c, Mapping):
                    continue
                nm = _opt_str(c.get("name")) or ""
                val = _opt_str(c.get("value_name")) or ""
                if nm or val:
                    label_parts.append((("%s: %s" % (nm, val)).strip(": ")).strip())
        out.append({
            "id": _opt_str(v.get("id")),
            "price": _to_float(v.get("price")),
            "available_quantity": (
                str(v.get("available_quantity")) if v.get("available_quantity") is not None else None
            ),
            "combination": ", ".join([p for p in label_parts if p]) or None,
        })
    return out


def _attributes_obj(attributes: Any) -> Dict[str, str]:
    """Normalize attributes[] into a flat {name: value_name} ficha-tecnica object. A non-list /
    empty -> {}. Skips entries with no name OR no value. NEVER fabricates a value."""
    if not isinstance(attributes, list):
        return {}
    out: Dict[str, str] = {}
    for a in attributes:
        if not isinstance(a, Mapping):
            continue
        nm = _opt_str(a.get("name"))
        val = _opt_str(a.get("value_name"))
        if val is None:
            val = _opt_str(a.get("value_id"))
        if nm and val:
            out[nm] = val
    return out


def _seller_address(addr: Any) -> Optional[str]:
    """Join an E2 seller_address (city.name / state.id) into a compact string. Absent -> None."""
    if not isinstance(addr, Mapping):
        return None
    city = addr.get("city")
    state = addr.get("state")
    city_name = _opt_str(city.get("name")) if isinstance(city, Mapping) else _opt_str(city)
    state_name = _opt_str(state.get("id")) if isinstance(state, Mapping) else _opt_str(state)
    parts = [p for p in (city_name, state_name) if p]
    return ", ".join(parts) or None


def _br_money_str(amount: float) -> str:
    """Render a float as BR money digits ('30,65', '1.234,56') WITHOUT a currency glyph. PURE.
    Used only for the installments label (display); never a parsed/authoritative number."""
    try:
        whole = int(amount)
        cents = int(round((amount - whole) * 100))
        if cents >= 100:  # rounding edge (e.g. 30.999 -> 31,00)
            whole += 1
            cents = 0
        # Thousands dots on the integer part (BR grouping), comma + 2-digit cents.
        s_whole = "{:,}".format(whole).replace(",", ".")
        return "%s,%02d" % (s_whole, cents)
    except Exception:
        return str(amount)


def _exact_or_bucket(value: Any) -> Tuple[Optional[int], Optional[str]]:
    """Classify an ML sold/quantity value as (exact_int, bucket_label). The public token may
    return either a GENUINE integer (an int, or a pure-digit string like '150') OR a FAIXA bucket
    label ('+100', 'mais de 100'). An exact int -> (int, None); a bucket -> (None, verbatim string)
    so it is stored honestly and NEVER interpolated. A bool / None -> (None, None). PURE + TOTAL.

    This deliberately does NOT use _to_int on a string: _to_int('+100') would read 100, fabricating
    an exact value from a bucket. Only a pure-digit string is exact."""
    if isinstance(value, bool) or value is None:
        return (None, None)
    if isinstance(value, int):
        return (value, None)
    if isinstance(value, float):
        return (int(value), None)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return (None, None)
        if s.isdigit():
            return (int(s), None)
        return (None, s)  # a bucket label -> verbatim, never coerced.
    return (None, None)


def _opt_str(value: Any) -> Optional[str]:
    """A non-empty stripped string, or None. An int/float id is stringified (ML seller_id can be
    an int). A bool is NOT a string here. TOTAL."""
    if isinstance(value, bool):
        return None
    if isinstance(value, str):
        s = value.strip()
        return s or None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def _empty_detail() -> Dict[str, Any]:
    """The all-null detail record skeleton (every contract field present, honest null). mock is
    ALWAYS False -- this record is real API data or an explicit null, never a simulated value."""
    return {
        "item_id": None,
        "catalog_product_id": None,
        "catalog_name": None,
        "catalog_listing": None,
        "buy_box_winner": None,
        "buy_box_winner_price": None,
        "buy_box_status": None,
        "num_sellers": None,
        "sellers": [],
        "sold_exact": None,
        "sold_bucket": None,
        "available_quantity": None,
        "date_created": None,
        "listing_age_days": None,
        "logistic_type": None,
        "category_id": None,
        "price": None,
        "price_original": None,
        "discount_pct": None,
        "installments": None,
        "variations": [],
        "variations_count": 0,
        "attributes": {},
        "attributes_count": 0,
        "seller_id": None,
        "seller_reputation": None,
        "seller_power_status": None,
        "seller_sales_total": None,
        "seller_location": None,
        "data_sources": {},
        "endpoint_status": {},
        "mock": False,
    }


__all__ = [
    "fetch_detail",
    "fetch_catalog_detail",
    "resolve_item_id",
    "MeliDetailUnavailable",
]


# --------------------------------------------------------------------------- #
# CLI -- the orchestrator runs this LIVE (real network; the app token works for ITEM endpoints).
# --------------------------------------------------------------------------- #
def _print_detail(rec: Mapping[str, Any]) -> None:
    """Print a SHORT, credential-free summary of a detail record (NEVER prints a token)."""
    keys = (
        "item_id", "catalog_product_id", "buy_box_winner", "buy_box_status",
        "num_sellers", "sold_exact", "sold_bucket", "date_created", "listing_age_days",
        "logistic_type", "price", "price_original", "discount_pct", "installments",
        "variations_count", "attributes_count",
        "seller_id", "seller_reputation", "seller_power_status", "seller_sales_total",
    )
    for k in keys:
        print("  %-22s %s" % (k, rec.get(k)))
    print("  %-22s %s" % ("endpoint_status", rec.get("endpoint_status")))
    print("  %-22s %s" % ("data_sources", rec.get("data_sources")))


def _main(argv: List[str]) -> int:
    if not argv:
        print("CEXAI Mercado Livre detail client (Pass 2). Usage:")
        print("  python _tools/cex_marketplace_detail_meli.py --detail <MLB item id|listing url>  "
              "(item-id entry; needs a USER token for E1/E3 -- app token gets 403 on /items)")
        print("  python _tools/cex_marketplace_detail_meli.py --catalog <MLB catalog product id|/p/ url>  "
              "(catalog entry; WORKS on the app token -- E2/E4/products are 200)")
        print("  python _tools/cex_marketplace_detail_meli.py --probe \"<search query>\"  "
              "(find a real item id via _meli_search -- /search is restricted)")
        return 0

    if argv[0] == "--detail" and len(argv) >= 2:
        target = argv[1]
        print("[detail] resolving + fetching %s ..." % target)
        rec = fetch_detail(target)
        _print_detail(rec)
        return 0

    if argv[0] == "--catalog" and len(argv) >= 2:
        target = argv[1]
        print("[catalog] resolving + fetching catalog %s (app-token path) ..." % target)
        rec = fetch_catalog_detail(target)
        _print_detail(rec)
        return 0

    if argv[0] == "--probe":
        query = " ".join(argv[1:]).strip() or "comedouro gato inox"
        token = get_meli_token()
        if not token:
            print("[probe] NO ML token (MELI_ACCESS_TOKEN unset AND no client creds) -- cannot probe.")
            return 1
        print("[probe] searching ML for an item id: %r" % query)
        try:
            _text, pages, _url = _live._meli_search(query, token)
        except Exception as exc:
            # The /search API is documented-RESTRICTED (0 results even with a valid token); report
            # it HONESTLY -- do NOT fabricate an item id.
            print("[probe] _meli_search failed (the /search API is restricted): %s" % type(exc).__name__)
            print("[probe] pass a known MLB id via --detail instead.")
            return 1
        item_id = None
        for p in pages:
            cand = resolve_item_id(str(p.get("permalink") or p.get("url") or ""))
            if cand:
                item_id = cand
                break
        if not item_id:
            print("[probe] /search returned %d listings but no resolvable MLB id "
                  "(restricted search returns 0) -- pass a known id via --detail." % len(pages))
            return 1
        print("[probe] resolved item id: %s -- fetching detail ..." % item_id)
        rec = fetch_detail(item_id, token)
        _print_detail(rec)
        return 0

    print("unknown args: %s" % " ".join(argv))
    return 2


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
