#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI Marketplace Detail-Page Extraction (kind: parser, P05 -- composed, no new kind).

Given a single LISTING URL, pull the STRUCTURED product detail (specs / description /
attributes / images / price / title) via the firecrawl /v1/extract REST endpoint. This is
the depth lane that complements the search-grid lanes (playwright / vision): the grid lanes
read MANY cards shallowly (title + price); this reads ONE listing DEEPLY (the full spec
table, the attribute key/values, the description, the gallery).

THE EXTRACTOR SEAM (offline-testable): the firecrawl /v1/extract call is injected via the
``extractor`` argument (a callable url -> the firecrawl response dict). Default is a thin
REST client built on the firecrawl key resolved from cex_tool_resolver_live (read at call
time; NEVER logged). A unit test injects a FAKE extractor returning a fixed payload, so NO
network is touched. The schema we ASK firecrawl for is the product-detail shape below.

NEVER FABRICATE (mirrors p11_gr_anti_hallucination_pesquisa + the existing lanes): a field
the response does NOT carry is returned as null AND named in the ``missing`` list (so the
caller knows it is an honest absence, not a zero). The extractor only ever transcribes what
firecrawl returned -- it invents NOTHING. An anti-bot / empty response yields a detail dict
with every field null + status='empty' (honest), never a guessed spec.

DEGRADE-NEVER + TOTAL: extract_detail NEVER raises. A bad URL, an extractor exception, a
non-dict response -> a detail dict with status='unavailable' + an error type + all fields
null. The caller (the tier-router's TIER 3) reads status/listings/detail and degrades.

SAFETY-AWARE: when CEX_MARKETPLACE_SAFETY=1 the fetch routes through cex_marketplace_safety
(pace per host + cache by URL + breaker). With the flag off it is a no-op (byte-identical).

Return shape (a typed dict -- never None):
  {
    "url": str, "marketplace": str, "status": "ok"|"empty"|"unavailable",
    "detail": {
      "title": str|None, "price": float|None, "description": str|None,
      "specs": {str: str},        # the spec table (key -> value); {} when none
      "attributes": {str: str},   # extra key/value attributes; {} when none
      "images": [str, ...],       # image URLs; [] when none
    },
    "missing": [str, ...],        # the detail keys that came back null/empty (honest)
    "mock": bool,                 # True when an injected (test) extractor served it
  }

ASCII-only (.claude/rules/ascii-code-rule.md). NO secret is logged (the firecrawl key lands
ONLY in the Authorization header inside the default REST client). COMPOSES the shipped
seams; modifies NONE of them.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_tool_resolver_live as _live  # type: ignore[import]

# The firecrawl extract REST endpoint (v1). Overridable for a future API change.
_FIRECRAWL_EXTRACT_URL = "https://api.firecrawl.dev/v1/extract"
# The per-call HTTP timeout (the same short degrade-never ceiling the live resolver uses).
_HTTP_TIMEOUT = _live._HTTP_TIMEOUT

# The product-detail schema we ASK firecrawl /v1/extract to return (JSON-schema-ish). The
# default REST client sends this so firecrawl returns the structured shape directly. A
# response that omits a key -> that key is reported in ``missing`` (NEVER fabricated).
_EXTRACT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "price": {"type": "number"},
        "description": {"type": "string"},
        "specs": {"type": "object"},
        "attributes": {"type": "object"},
        "images": {"type": "array", "items": {"type": "string"}},
    },
}
# The strict extraction prompt (anti-hallucination: transcribe only; null on absence).
_EXTRACT_PROMPT = (
    "Extract the product detail from this marketplace listing page. Return title, price "
    "(a number in BRL, digits only), description, a specs object (technical spec name -> "
    "value), an attributes object (other attribute -> value), and an images array (image "
    "URLs). If a field is not present on the page, OMIT it (do not guess). NEVER invent a "
    "spec, a value, a price, or an image -- transcribe only what is literally on the page."
)

# The detail keys we always report on (so ``missing`` is complete + stable).
_DETAIL_KEYS: Tuple[str, ...] = (
    "title", "price", "description", "specs", "attributes", "images",
)


# --------------------------------------------------------------------------- #
# The public extractor.
# --------------------------------------------------------------------------- #
def extract_detail(
    url: str,
    *,
    marketplace: str = "",
    extractor: Optional[Callable[[str], Any]] = None,
    safety: Optional[Any] = None,
) -> Dict[str, Any]:
    """Extract the structured product detail for ONE listing URL. TOTAL: NEVER raises, NEVER
    fabricates.

    ``extractor`` (optional): a callable ``url -> firecrawl_response_dict``. When None the
    default REST client is used (needs FIRECRAWL_API_KEY; absent -> status='unavailable').
    A test injects a fake extractor returning a fixed dict -> NO network.

    ``safety`` (optional): the ban-safety module (defaults to cex_marketplace_safety when
    importable). When its flag is on, the fetch routes through cache/breaker/pace."""
    u = _s(url)
    if not u or not _looks_like_url(u):
        return _detail_result(u, marketplace, "unavailable", _empty_detail(),
                              missing=list(_DETAIL_KEYS), mock=False, error="bad_url")

    sf = safety if safety is not None else _safety_module()
    host_q = u  # the cache/pace key for a single-URL extract is the URL itself.

    gate = _safety_before(sf, marketplace, host_q, u)
    if gate.get("action") == "serve_cache":
        cached = gate.get("listings") or []
        rec = cached[0] if cached and isinstance(cached[0], Mapping) else None
        if isinstance(rec, Mapping):
            detail, missing = _normalize_detail(rec)
            return _detail_result(u, marketplace, "ok", detail, missing=missing, mock=False)
        # An empty/odd cache payload -> fall through to a live extract.
    elif gate.get("action") == "skip":
        return _detail_result(u, marketplace, "unavailable", _empty_detail(),
                              missing=list(_DETAIL_KEYS), mock=False, error="breaker_open")

    injected = extractor is not None
    fn = extractor if injected else _default_firecrawl_extract
    try:
        raw = fn(u)
    except Exception as exc:
        _safety_after(sf, marketplace, host_q, u, listings=[], status="unavailable")
        return _detail_result(u, marketplace, "unavailable", _empty_detail(),
                              missing=list(_DETAIL_KEYS), mock=injected, error=type(exc).__name__)

    extracted = _extracted_object(raw)
    if extracted is None:
        # The response carried no structured object (anti-bot / empty render) -> honest empty.
        _safety_after(sf, marketplace, host_q, u, listings=[], status="empty")
        return _detail_result(u, marketplace, "empty", _empty_detail(),
                              missing=list(_DETAIL_KEYS), mock=injected)

    detail, missing = _normalize_detail(extracted)
    # A detail is 'ok' only if SOMETHING usable was transcribed (a title, a price, specs,
    # attributes, a description, or images). All-null -> 'empty' (honest, not a fabricated row).
    status = "ok" if _has_signal(detail) else "empty"
    # Cache only a non-empty result (mirrors the safety layer's never-cache-empty rule); we
    # store the normalized detail as a single-record list so a cache hit re-serves it.
    cache_records = [detail] if status == "ok" else []
    _safety_after(sf, marketplace, host_q, u, listings=cache_records, status=status)
    return _detail_result(u, marketplace, status, detail, missing=missing, mock=injected)


# --------------------------------------------------------------------------- #
# The default firecrawl /v1/extract REST client (lazy; needs FIRECRAWL_API_KEY).
# --------------------------------------------------------------------------- #
def _default_firecrawl_extract(url: str) -> Dict[str, Any]:
    """POST firecrawl /v1/extract for ONE url with the product-detail schema + prompt -> the
    response dict. The key is read at call time (NEVER logged; it lands ONLY in the
    Authorization header). RAISES on a missing key or an HTTP error (extract_detail catches it
    -> status='unavailable'). Imported requests lazily (offline-import friendly)."""
    key = _live._read_env_key("FIRECRAWL_API_KEY")
    if key is None:
        raise RuntimeError("FIRECRAWL_API_KEY missing/empty -- firecrawl extract unavailable.")
    import requests  # type: ignore[import]

    resp = requests.post(
        _FIRECRAWL_EXTRACT_URL,
        headers={"Authorization": "Bearer %s" % key, "Content-Type": "application/json"},
        json={"urls": [url], "schema": _EXTRACT_SCHEMA, "prompt": _EXTRACT_PROMPT},
        timeout=_HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    return _live._safe_json(resp)


# --------------------------------------------------------------------------- #
# Response normalization (PURE / TOTAL). NEVER fabricates.
# --------------------------------------------------------------------------- #
def _extracted_object(raw: Any) -> Optional[Mapping[str, Any]]:
    """Pull the extracted product object from a firecrawl /v1/extract response. Tolerates the
    shapes: {'data': {...}}, {'data': [{...}]}, {'extract': {...}}, or a bare {...} that
    already holds the detail fields. TOTAL -> None when no usable object is present (the caller
    then records an honest 'empty')."""
    if not isinstance(raw, Mapping):
        return None
    # Preferred: the 'data' envelope firecrawl returns.
    data = raw.get("data")
    if isinstance(data, Mapping):
        return data
    if isinstance(data, list):
        for it in data:
            if isinstance(it, Mapping):
                return it
        return None
    # Some responses nest under 'extract'.
    extract = raw.get("extract")
    if isinstance(extract, Mapping):
        return extract
    # Last resort: the top-level object already looks like the detail (has a known key).
    if any(k in raw for k in _DETAIL_KEYS):
        return raw
    return None


def _normalize_detail(obj: Mapping[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Normalize the extracted object into the canonical detail dict + the ``missing`` list.
    Each field is coerced to its safe type; a field that is absent / empty / unparseable is
    set null (or {} / [] for the container fields) AND added to ``missing``. NEVER fabricates."""
    detail = _empty_detail()
    missing: List[str] = []

    title = _s(obj.get("title"))
    detail["title"] = title or None
    if not title:
        missing.append("title")

    price = _to_float(obj.get("price"))
    detail["price"] = price
    if price is None:
        missing.append("price")

    desc = _s(obj.get("description"))
    detail["description"] = desc or None
    if not desc:
        missing.append("description")

    specs = _str_map(obj.get("specs"))
    detail["specs"] = specs
    if not specs:
        missing.append("specs")

    attrs = _str_map(obj.get("attributes"))
    detail["attributes"] = attrs
    if not attrs:
        missing.append("attributes")

    images = _str_list(obj.get("images"))
    detail["images"] = images
    if not images:
        missing.append("images")

    return detail, missing


def _empty_detail() -> Dict[str, Any]:
    """A fully-null detail dict (every field absent). The honest 'nothing extracted' baseline."""
    return {
        "title": None, "price": None, "description": None,
        "specs": {}, "attributes": {}, "images": [],
    }


def _has_signal(detail: Mapping[str, Any]) -> bool:
    """True when the detail carries at least ONE usable field (so the status is 'ok' not
    'empty'). An all-null detail -> False (honest empty, never a fabricated row)."""
    if detail.get("title") or detail.get("description") or detail.get("price") is not None:
        return True
    if detail.get("specs") or detail.get("attributes") or detail.get("images"):
        return True
    return False


def _str_map(value: Any) -> Dict[str, str]:
    """Coerce a mapping into a clean {str: str} dict (drop empty keys/values; stringify scalars;
    skip nested containers). A non-mapping -> {}. NEVER fabricates a key. TOTAL."""
    if not isinstance(value, Mapping):
        return {}
    out: Dict[str, str] = {}
    for k, v in value.items():
        key = _s(k) if isinstance(k, str) else (str(k).strip() if k is not None else "")
        if not key:
            continue
        val = _scalar_str(v)
        if val:
            out[key] = val
    return out


def _str_list(value: Any) -> List[str]:
    """Coerce a list into a clean list of non-empty strings (deduped, order-preserved). A
    non-list -> []. NEVER fabricates an entry. TOTAL."""
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for it in value:
        s = _scalar_str(it)
        if s and s not in out:
            out.append(s)
    return out


def _scalar_str(value: Any) -> str:
    """Stringify a scalar (str/int/float/bool) into a trimmed string; a container / None -> ''.
    NEVER fabricates. TOTAL."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _to_float(value: Any) -> Optional[float]:
    """Coerce to float, or None (a bool is NOT a number; a BR '1.234,56' is normalized). TOTAL."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        # Keep digits + separators; normalize a BR decimal comma. Strip currency/text.
        cleaned = "".join(ch for ch in s if ch.isdigit() or ch in ".,")
        if not cleaned:
            return None
        if "," in cleaned and "." in cleaned:
            # '1.234,56' -> drop thousands dots, comma becomes the decimal point.
            cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            cleaned = cleaned.replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


# --------------------------------------------------------------------------- #
# Safety-layer glue (FAIL-OPEN; a no-op when the flag is off / the module is absent).
# --------------------------------------------------------------------------- #
def _safety_module() -> Optional[Any]:
    try:
        import cex_marketplace_safety as _ms  # type: ignore[import]
        return _ms
    except Exception:
        return None


def _safety_before(safety: Optional[Any], marketplace: str, query: str, url: str) -> Dict[str, Any]:
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
    if safety is None:
        return
    try:
        if not safety.is_enabled():
            return
        safety.after_fetch(marketplace, query, url, listings=listings, status=status)
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# Small PURE helpers.
# --------------------------------------------------------------------------- #
def _detail_result(
    url: str, marketplace: str, status: str, detail: Dict[str, Any], *,
    missing: List[str], mock: bool, error: str = "",
) -> Dict[str, Any]:
    """Assemble the canonical typed result. NEVER None. An error type is included only when set."""
    out: Dict[str, Any] = {
        "url": url,
        "marketplace": _s(marketplace),
        "status": status,
        "detail": detail,
        "missing": list(missing),
        "mock": bool(mock),
    }
    if error:
        out["error"] = error
    return out


def _looks_like_url(value: str) -> bool:
    v = (value or "").strip().lower()
    return v.startswith("http://") or v.startswith("https://")


def _s(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


__all__ = ["extract_detail"]


def _main(argv: List[str]) -> int:
    if not argv:
        print("CEXAI marketplace detail-extract (firecrawl /v1/extract).")
        print("Usage: python _tools/cex_marketplace_detail_extract.py <listing_url> [marketplace]")
        print("Programmatic (offline test): extract_detail(url, extractor=<fake>)")
        return 0
    url = argv[0]
    marketplace = argv[1] if len(argv) > 1 else ""
    # A real run needs FIRECRAWL_API_KEY (costs a credit); print a credential-free summary.
    res = extract_detail(url, marketplace=marketplace)
    print("url     : %s" % res["url"])
    print("status  : %s" % res["status"])
    print("missing : %s" % (", ".join(res["missing"]) if res["missing"] else "(none)"))
    d = res["detail"]
    print("title   : %s" % (d.get("title") or "(absent)"))
    print("price   : %s" % (d.get("price") if d.get("price") is not None else "(absent)"))
    print("specs   : %d keys" % len(d.get("specs") or {}))
    print("images  : %d" % len(d.get("images") or []))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
