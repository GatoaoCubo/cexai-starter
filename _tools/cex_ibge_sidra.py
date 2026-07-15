#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI Brazil MARKET-SIZING lane -- cex_ibge_sidra (research-universe; the GREEN TAM/SAM source).

THE denominator pass. The marketplace + web lanes read what shoppers DO (price, demand, listings);
this lane reads HOW MANY THERE ARE -- the official Brazil population / PIB / household counts that
turn a competitive scan into a real TAM/SAM. Source: IBGE (Instituto Brasileiro de Geografia e
Estatistica), the official statistics agency -- GREEN (no key, public, no ToS data-resale wall) and
one of the 3 ownable BR-edge sources in the research-universe map (memory:
reference_research_universe_taxonomy_2026_06_19 -- ML-trends + Receita-CNPJ + IBGE-SIDRA).

THE endpoint (SIDRA values API, no key, 30s timeout):
  GET https://apisidra.ibge.gov.br/values/t/{table}/n{level}/{loc}/v/{var}/p/{period}
  ``table`` = a SIDRA aggregate table (e.g. 6579 = population estimate), ``var`` = a variable id,
  ``n{level}`` = a territorial level (1 = Brazil, 3 = UF/state, 6 = municipality), ``loc`` = a
  location filter (``all`` = every territory at that level, or specific ids), ``period`` = a period
  token (``last`` = latest, or a year/range). The level/loc are written as one path segment
  ``n{level}/{loc}`` (e.g. ``n3/all``).

THE SHAPE (confirmed live 2026-06-19): the body is a JSON ARRAY. ``[0]`` is a HEADER dict mapping
each field-code to its human label (``V`` -> 'Valor', ``D1N`` -> 'Unidade da Federacao',
``D2N`` -> 'Variavel', ``D3N`` -> 'Ano', ``MN`` -> 'Unidade de Medida', ...). ``[1:]`` are the data
rows, each a flat dict keyed by those SAME codes. The 'Dx' dimensions are POSITIONAL but their ROLE
(territory vs variable vs period) is declared in the header labels -- so this module READS the header
to discover which Dx is the variable ('Vari...'), which is the period ('Ano'/'Mes'/'Trimestre'/
'Periodo'), and treats the remaining geographic Dx as the territory. It does NOT hardcode D1=
territory (that would break on a table where the variable sits in D1).

CARDINAL RULE -- NEVER fabricate a number (memory: reference_ml_scraping_antibot_hallucination -- a
fabricated official figure is the cardinal sin, doubly so for a population/PIB denominator). EVERY
value emitted is an IBGE-returned ``V`` parsed as a number, OR an honest ``null``. IBGE encodes a
suppressed/absent cell as ``'-'`` / ``'..'`` / ``'...'`` / ``'X'`` -- those map to ``value: null``
(NEVER 0, NEVER a guess). A 4xx / 5xx / network drop / non-array body -> a TOTAL dict with empty
``rows`` + the failure recorded in ``endpoint_status`` / ``data_sources``. query_sidra is TOTAL: it
NEVER raises.

SECURITY (anti-injection -- the cybersec lesson, memory: project_cybersec_extraction_harness): every
path component (table / var / level / loc / period) is interpolated into the request URL, so each is
VALIDATED before the URL is built. table/var/level = digits only; loc = ``all`` OR a comma-list of
digits (with the SIDRA ``in n{lvl} all`` form also allowed); period = ``last`` / ``last N`` / a year
or comma/hyphen range of digits. A component that fails validation -> the call is NOT issued and the
result is an honest null with a recorded ``rejected`` status (NEVER a traversed path).

SECRET HYGIENE: IBGE needs no key, so there is no secret to leak. On ANY error we report ONLY the
exception TYPE name + the (already-validated) path -- NEVER the response body (which could echo a
large/sensitive payload). ASCII-only (.claude/rules/ascii-code-rule.md). Fully type-hinted.
Composes; modifies nothing.

Live proof (real network, no key):
  python _tools/cex_ibge_sidra.py populacao_brasil
  python _tools/cex_ibge_sidra.py populacao_por_uf
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Tuple

# The SIDRA values API base (no key). All requests are GETs against this host; the 30s ceiling is
# the degrade-never timeout (a slow IBGE response must not hang the research run).
_SIDRA_BASE = "https://apisidra.ibge.gov.br"
_HTTP_TIMEOUT = 30

# IBGE encodes a suppressed / non-applicable / withheld cell with one of these tokens in 'V'. They
# are NOT zero and NOT a number -- each maps to an honest ``value: null`` (NEVER fabricated).
_SUPPRESSED_VALUES = frozenset({"-", "..", "...", "x", "X", ".."})

# Header-label fragments (lower-cased, accent-free) that identify a dimension's ROLE. The territory
# is whatever geographic Dx is left after the variable + period dimensions are claimed.
_VARIABLE_LABEL_HINTS = ("variavel", "vari" + "avel", "vari")
_PERIOD_LABEL_HINTS = ("ano", "mes", "trimestre", "semestre", "periodo", "data")

# How many rows we keep from one query (a UF query is 27; a municipality query can be ~5570 -- we
# cap so a single pull can never balloon the research context). The cap is generous for sizing.
_MAX_ROWS = 6000


# --------------------------------------------------------------------------- #
# CANONICAL PRESETS -- usable out of the box. Each binds a known (table, var, level, loc, period)
# and a ``summary`` rule (whether a single total is meaningful for sizing). loc 'all' = every
# territory at that level. The preset NAMES are validated against this dict (anti-typo).
# --------------------------------------------------------------------------- #
_PRESETS: Dict[str, Dict[str, Any]] = {
    # Total resident population of Brazil (the top-line TAM denominator). Table 6579 var 9324 =
    # 'Populacao residente estimada'; n1 = Brazil; last = latest year. summary = the single total.
    "populacao_brasil": {
        "table": "6579", "var": "9324", "level": "1", "loc": "all", "period": "last",
        "summary_kind": "total", "label": "Brazil resident population (estimate)",
    },
    # Population by state (UF) -- the per-region SAM split. n3 = UF; 27 rows. summary = sum of UFs.
    "populacao_por_uf": {
        "table": "6579", "var": "9324", "level": "3", "loc": "all", "period": "last",
        "summary_kind": "sum", "label": "Brazil resident population by state (UF)",
    },
    # PIB by state (UF) -- 'Produto Interno Bruto a precos correntes' (Mil Reais), table 5938 var
    # 37, n3 = UF. A market-VALUE denominator. summary = sum (national PIB approximation by UF).
    "pib_municipios": {
        "table": "5938", "var": "37", "level": "3", "loc": "all", "period": "last",
        "summary_kind": "sum", "label": "PIB (GDP) at current prices by state (UF), Mil Reais",
    },
    # Households (domicilios) by state (UF) -- the household-count denominator for B2C sizing.
    # Table 4712 (Censo 2022) var 381 = 'Domicilios particulares permanentes ocupados' (unit
    # 'Domicilios'); n3 = UF. summary = sum (national household count). Verified live 2026-06-19.
    "domicilios_por_uf": {
        "table": "4712", "var": "381", "level": "3", "loc": "all", "period": "last",
        "summary_kind": "sum", "label": "Occupied permanent private households by state (UF)",
    },
}

# --------------------------------------------------------------------------- #
# Anti-injection validators -- every path component is checked BEFORE the URL is built. PURE+TOTAL.
# --------------------------------------------------------------------------- #
_RE_DIGITS = re.compile(r"\d+")
_RE_LOC = re.compile(r"(?:all|\d+(?:,\d+)*)")  # 'all' OR a comma-list of digits.
_RE_PERIOD = re.compile(r"(?:last(?: \d+)?|\d{4}(?:[,-]\d{4})*)")  # 'last' | 'last N' | year(range).


def _valid_id(value: Any) -> Optional[str]:
    """A table/var/level component: digits only (re.fullmatch). A non-string / non-digit / empty
    / path-traversal token -> None (the caller then refuses the call). PURE + TOTAL."""
    if isinstance(value, (int,)) and not isinstance(value, bool):
        value = str(value)
    if not isinstance(value, str):
        return None
    s = value.strip()
    return s if (s and _RE_DIGITS.fullmatch(s)) else None


def _valid_loc(value: Any) -> Optional[str]:
    """A location filter: ``all`` OR a comma-list of numeric territory ids. None on anything else
    (e.g. '../', a wildcard glob). PURE + TOTAL."""
    if value is None:
        return "all"
    if not isinstance(value, str):
        return None
    s = value.strip()
    return s if (s and _RE_LOC.fullmatch(s)) else None


def _valid_period(value: Any) -> Optional[str]:
    """A period token: ``last`` / ``last N`` / a 4-digit year / a comma|hyphen range of years.
    None on anything else. PURE + TOTAL."""
    if value is None:
        return "last"
    if isinstance(value, int) and not isinstance(value, bool):
        value = str(value)
    if not isinstance(value, str):
        return None
    s = value.strip()
    return s if (s and _RE_PERIOD.fullmatch(s)) else None


# --------------------------------------------------------------------------- #
# THE network seam -- ONE place a test monkeypatches (cex_ibge_sidra._sidra_get).
# --------------------------------------------------------------------------- #
class SidraUnavailable(RuntimeError):
    """Raised INTERNALLY by _sidra_get on an HTTP / transport error so query_sidra can record an
    honest failure. Carries NO response body -- only the path + the error TYPE name."""


def _sidra_get(path: str) -> Any:
    """GET a fully-built SIDRA values path (already validated) -> the parsed JSON body.

    Mirrors the house HTTP posture: lazy ``requests`` import (offline-import friendly),
    timeout=_HTTP_TIMEOUT, raise_for_status, JSON parse. RAISES SidraUnavailable on ANY HTTP /
    transport error (4xx for a bad id, 5xx, network drop) so the caller degrades to empty rows.
    On error we report ONLY the error TYPE name + the path -- NEVER the response body. NEVER
    fabricates a body."""
    import requests  # type: ignore[import]  # lazy: keeps import-time offline-friendly.

    url = _SIDRA_BASE + (path if path.startswith("/") else "/" + path)
    try:
        resp = requests.get(url, headers={"Accept": "application/json"}, timeout=_HTTP_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # NEVER leak a body; report only the type + the (validated) path.
        raise SidraUnavailable("%s on GET %s" % (type(exc).__name__, path)) from exc


# --------------------------------------------------------------------------- #
# THE entry -- run a preset (or a raw query) and map rows. TOTAL: NEVER raises, NEVER fabricates.
# --------------------------------------------------------------------------- #
def query_sidra(
    preset: Optional[str] = None,
    table: Optional[str] = None,
    var: Optional[str] = None,
    level: Optional[str] = None,
    loc: Optional[str] = None,
    period: Optional[str] = None,
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Query the IBGE SIDRA values API for ONE aggregate and map the rows. TOTAL: NEVER raises,
    NEVER fabricates -- a bad/unknown id, a rejected (anti-injection) component, a 4xx, or a
    non-array body all yield an honest empty-``rows`` dict with a recorded provenance failure.

    Two modes:
      * PRESET (recommended): pass ``preset`` = one of populacao_brasil / populacao_por_uf /
        pib_municipios / domicilios_por_uf. Unknown preset -> rejected (honest null), NEVER guessed.
      * RAW (power use): pass ``table`` + ``var`` + ``level`` (+ optional ``loc`` default 'all',
        ``period`` default 'last'). EACH id is validated (digits / all / last|year) BEFORE the URL
        is built; a component that fails -> rejected, the call is NOT issued.

    Args:
      preset: a canonical preset name (takes precedence over the raw args when set).
      table, var, level: SIDRA ids (digits). loc: 'all' or a comma-list of territory ids
        (default 'all'). period: 'last' / 'last N' / a year or year-range (default 'last').
      now: an OPTIONAL fixed timestamp for ``fetched_at`` provenance (testable determinism).

    Returns a dict (honest-null on any failure):
      preset (echoed or None), query ({table, var, level, loc, period} -- the resolved ids or what
        was rejected), rows (list of {territory, territory_code, period, variable, value, unit};
        [] when unavailable), row_count, summary (optional {kind, value, unit, label} -- a single
        total for a sizing preset; None when not applicable or unavailable), data_sources,
        endpoint_status (ok | rejected: ... | failed: ...), fetched_at (ISO-8601 UTC),
        mock (ALWAYS False -- real API or an honest null, never a simulated value)."""
    rec = _empty_result(now)

    # Resolve the 5 ids -- from the preset, else from the raw args. Validate EACH before any URL.
    resolved = _resolve_query(preset, table, var, level, loc, period)
    rec["preset"] = resolved["preset"]
    rec["query"] = resolved["query"]
    if resolved["reject_reason"] is not None:
        rec["endpoint_status"]["sidra"] = "rejected: %s" % resolved["reject_reason"]
        return rec

    q = resolved["query"]
    path = "/values/t/%s/n%s/%s/v/%s/p/%s" % (q["table"], q["level"], q["loc"], q["var"], q["period"])

    body = _safe_fetch(rec, path)
    if body is None:
        return rec  # failure already recorded in endpoint_status / data_sources.

    _apply_rows(rec, body)

    # A sizing summary (a single total) only when the preset declares one AND rows mapped. NEVER
    # invents a total: a 'total' preset uses the single returned row's value; a 'sum' preset adds
    # the non-null row values (and is honest about how many rows contributed).
    summary_kind = resolved.get("summary_kind")
    summary_label = resolved.get("summary_label")
    if summary_kind:
        rec["summary"] = _build_summary(rec["rows"], summary_kind, summary_label)

    return rec


def _resolve_query(
    preset: Optional[str],
    table: Optional[str],
    var: Optional[str],
    level: Optional[str],
    loc: Optional[str],
    period: Optional[str],
) -> Dict[str, Any]:
    """Resolve + VALIDATE the 5 ids. Returns {preset, query, reject_reason, summary_kind,
    summary_label}. When ``preset`` is given it must be known (else reject -- NEVER fall back to a
    guessed table). Then EVERY component is validated; the first invalid one is the reject_reason.
    PURE + TOTAL."""
    summary_kind: Optional[str] = None
    summary_label: Optional[str] = None

    if preset is not None:
        key = preset.strip() if isinstance(preset, str) else None
        spec = _PRESETS.get(key) if key else None
        if spec is None:
            return {
                "preset": preset,
                "query": {"table": None, "var": None, "level": None, "loc": None, "period": None},
                "reject_reason": "unknown preset %r (known: %s)"
                % (preset, ", ".join(sorted(_PRESETS))),
                "summary_kind": None,
                "summary_label": None,
            }
        table, var, level = spec["table"], spec["var"], spec["level"]
        loc, period = spec["loc"], spec["period"]
        summary_kind = spec.get("summary_kind")
        summary_label = spec.get("label")
        preset = key

    v_table = _valid_id(table)
    v_var = _valid_id(var)
    v_level = _valid_id(level)
    v_loc = _valid_loc(loc)
    v_period = _valid_period(period)

    # Echo what we resolved (or None for a component that failed) so the caller can see the gap.
    query = {
        "table": v_table, "var": v_var, "level": v_level, "loc": v_loc, "period": v_period,
    }
    reject: Optional[str] = None
    if v_table is None:
        reject = "invalid table id (digits required): %r" % (table,)
    elif v_var is None:
        reject = "invalid var id (digits required): %r" % (var,)
    elif v_level is None:
        reject = "invalid level (digits required): %r" % (level,)
    elif v_loc is None:
        reject = "invalid loc ('all' or comma-list of ids required): %r" % (loc,)
    elif v_period is None:
        reject = "invalid period ('last' / 'last N' / year(range) required): %r" % (period,)

    return {
        "preset": preset,
        "query": query,
        "reject_reason": reject,
        "summary_kind": summary_kind if reject is None else None,
        "summary_label": summary_label,
    }


def _safe_fetch(rec: Dict[str, Any], path: str) -> Any:
    """Run the ONE SIDRA GET; record provenance + status. DEGRADE-NEVER: a SidraUnavailable (HTTP/
    transport) OR any unexpected error -> 'failed: <reason>' + None (rows stay empty). NEVER
    fabricates."""
    try:
        body = _sidra_get(path)
    except SidraUnavailable as exc:
        rec["endpoint_status"]["sidra"] = "failed: %s" % (str(exc) or "unavailable")
        return None
    except Exception as exc:  # defensive: a transport surprise must not crash the record.
        rec["endpoint_status"]["sidra"] = "failed: %s" % type(exc).__name__
        return None
    rec["endpoint_status"]["sidra"] = "ok"
    rec["data_sources"]["sidra"] = "ibge:apisidra:values"
    return body


# --------------------------------------------------------------------------- #
# Row mapping -- introspect the SIDRA header, then map each data row. PURE (NEVER fabricate).
# --------------------------------------------------------------------------- #
def _apply_rows(rec: Dict[str, Any], body: Any) -> None:
    """Map the SIDRA values array onto ``rows``. ``body[0]`` is the header (code -> label);
    ``body[1:]`` are data rows. We READ the header to discover the territory / variable / period
    field-codes (their ROLE is in the label, NOT a fixed position), then emit, per data row,
    {territory, territory_code, period, variable, value, unit}. A suppressed/absent 'V' -> value
    None (NEVER 0, NEVER fabricated). A non-array body / header-only -> [] (honest)."""
    if not isinstance(body, list) or len(body) < 2:
        rec["rows"] = []
        rec["row_count"] = 0
        return
    header = body[0]
    if not isinstance(header, Mapping):
        rec["rows"] = []
        rec["row_count"] = 0
        return

    roles = _dimension_roles(header)
    terr_name_key = roles["territory_name"]
    terr_code_key = roles["territory_code"]
    var_name_key = roles["variable_name"]
    period_name_key = roles["period_name"]

    rows: List[Dict[str, Any]] = []
    for entry in body[1:]:
        if not isinstance(entry, Mapping):
            continue  # a non-dict row is dropped -- never fabricated.
        rows.append({
            "territory": _opt_str(entry.get(terr_name_key)) if terr_name_key else None,
            "territory_code": _opt_str(entry.get(terr_code_key)) if terr_code_key else None,
            "period": _opt_str(entry.get(period_name_key)) if period_name_key else None,
            "variable": _opt_str(entry.get(var_name_key)) if var_name_key else None,
            "value": _parse_value(entry.get("V")),
            "unit": _opt_str(entry.get("MN")),
        })
        if len(rows) >= _MAX_ROWS:
            break
    rec["rows"] = rows
    rec["row_count"] = len(rows)


def _dimension_roles(header: Mapping[str, Any]) -> Dict[str, Optional[str]]:
    """Inspect the SIDRA header dict (code -> label) and decide which 'Dx' codes are the territory /
    variable / period. The variable dimension's label contains 'vari...'; the period's contains an
    'ano'/'mes'/'trimestre'/'periodo' token; the remaining geographic Dx is the territory (its NAME
    code is 'DxN', its CODE code is 'DxC'). TOTAL -> any role we cannot find stays None (that field
    is then emitted as null, never guessed)."""
    # Collect the dimension indices present (D1, D2, ...). SIDRA names them DxN (name) + DxC (code).
    dims: List[str] = []
    for key in header.keys():
        m = re.fullmatch(r"D(\d+)N", str(key))
        if m and m.group(1) not in dims:
            dims.append(m.group(1))

    variable_dim: Optional[str] = None
    period_dim: Optional[str] = None
    for d in dims:
        label = _norm_label(header.get("D%sN" % d))
        if variable_dim is None and any(h in label for h in _VARIABLE_LABEL_HINTS):
            variable_dim = d
            continue
        if period_dim is None and any(_label_is_period(label, h) for h in _PERIOD_LABEL_HINTS):
            period_dim = d

    # The territory dimension = the first geographic Dx that is neither the variable nor the period.
    territory_dim: Optional[str] = None
    for d in dims:
        if d != variable_dim and d != period_dim:
            territory_dim = d
            break

    return {
        "territory_name": ("D%sN" % territory_dim) if territory_dim else None,
        "territory_code": ("D%sC" % territory_dim) if territory_dim else None,
        "variable_name": ("D%sN" % variable_dim) if variable_dim else None,
        "period_name": ("D%sN" % period_dim) if period_dim else None,
    }


def _label_is_period(label: str, hint: str) -> bool:
    """A period-label match must be a WHOLE word ('ano' must not match 'mediano'). The label is
    already accent-free + lower-cased; we word-boundary the hint. PURE."""
    return re.search(r"\b%s\b" % re.escape(hint), label) is not None


# --------------------------------------------------------------------------- #
# Summary (a single sizing total) -- PURE, honest about contribution. NEVER fabricates.
# --------------------------------------------------------------------------- #
def _build_summary(
    rows: List[Mapping[str, Any]], kind: str, label: Optional[str]
) -> Optional[Dict[str, Any]]:
    """Build a sizing summary from the mapped rows. ``total`` -> the single row's value (or None
    when there is not exactly one usable value). ``sum`` -> the sum of the non-null numeric row
    values, with ``contributing_rows`` stating how many of ``len(rows)`` were summable (honest: a
    sum over a partial set is reported as such). Returns None when no value is available. NEVER
    fabricates a number -- a sum of zero usable rows is None, not 0."""
    numeric: List[float] = []
    unit: Optional[str] = None
    for r in rows:
        val = r.get("value")
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            numeric.append(float(val))
            if unit is None:
                unit = r.get("unit") if isinstance(r.get("unit"), str) else None
    if not numeric:
        return None

    if kind == "total":
        if len(numeric) != 1:
            # 'total' expects a single denominator row; anything else is reported but not collapsed.
            return {
                "kind": "total",
                "value": None,
                "unit": unit,
                "label": label,
                "note": "expected 1 row, got %d usable values" % len(numeric),
            }
        only = numeric[0]
        # Preserve an int for an integral count (population/household totals are whole numbers).
        value_out: Any = int(only) if float(only).is_integer() else only
        return {"kind": "total", "value": value_out, "unit": unit, "label": label}

    if kind == "sum":
        total = sum(numeric)
        # Keep an int when every contributor is integral (population/household counts are integers).
        total_out: Any = int(total) if all(float(n).is_integer() for n in numeric) else total
        return {
            "kind": "sum",
            "value": total_out,
            "unit": unit,
            "label": label,
            "contributing_rows": len(numeric),
            "total_rows": len(rows),
        }

    return None  # unknown summary kind -> no summary (never fabricated).


# --------------------------------------------------------------------------- #
# PURE helpers (TOTAL -- absent/garbage -> None; NEVER fabricate).
# --------------------------------------------------------------------------- #
def _parse_value(raw: Any) -> Optional[float]:
    """Parse a SIDRA 'V' cell into a number, or None. A suppressed token ('-' / '..' / '...' / 'X')
    -> None (honest, NEVER 0). A blank / non-numeric -> None. An integral float is returned as an
    int (population/PIB counts are whole). NEVER fabricates. TOTAL."""
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        f = float(raw)
        return int(f) if f.is_integer() else f
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s or s in _SUPPRESSED_VALUES:
        return None
    # SIDRA values come as plain ASCII digit strings (no thousands separators in the API). Be tolerant
    # of a decimal comma just in case (BR locale), but only when the rest is digits.
    candidate = s.replace(",", ".") if (s.count(",") == 1 and s.replace(",", "").isdigit()) else s
    try:
        f = float(candidate)
    except (TypeError, ValueError):
        return None
    return int(f) if f.is_integer() else f


def _opt_str(value: Any) -> Optional[str]:
    """A non-empty stripped string, or None. An int/float code is stringified (IBGE codes can be
    ints). A bool is NOT a string here. TOTAL."""
    if isinstance(value, bool):
        return None
    if isinstance(value, str):
        s = value.strip()
        return s or None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def _norm_label(value: Any) -> str:
    """Lower-case + strip the common PT-BR accents off a header label so the role-hint match is
    accent-insensitive ('Variavel' / 'Variavel' both -> 'variavel'). NEVER raises. The accent map
    uses \\uXXXX escapes (ASCII source per the rule). TOTAL -> '' for a non-string."""
    if not isinstance(value, str):
        return ""
    s = value.strip().lower()
    # Strip the diacritics that appear in SIDRA dimension labels (a/e/i/o/u/c with PT-BR accents).
    # The keys are \uXXXX escapes so the SOURCE stays ASCII (.claude/rules/ascii-code-rule.md --
    # functional i18n strings use escapes, NOT literal chars); Python decodes them at runtime.
    accents = {
        "\u00e1": "a", "\u00e0": "a", "\u00e2": "a", "\u00e3": "a", "\u00e4": "a",
        "\u00e9": "e", "\u00e8": "e", "\u00ea": "e", "\u00eb": "e",
        "\u00ed": "i", "\u00ec": "i", "\u00ee": "i", "\u00ef": "i",
        "\u00f3": "o", "\u00f2": "o", "\u00f4": "o", "\u00f5": "o", "\u00f6": "o",
        "\u00fa": "u", "\u00f9": "u", "\u00fb": "u", "\u00fc": "u",
        "\u00e7": "c",
    }
    return "".join(accents.get(ch, ch) for ch in s)


def _empty_result(now: Optional[datetime]) -> Dict[str, Any]:
    """The all-null result skeleton. mock is ALWAYS False (real IBGE data or an explicit null, never
    a simulated value). ``fetched_at`` is the provided ``now`` (UTC) or call-time UTC, ISO-8601."""
    return {
        "preset": None,
        "query": {"table": None, "var": None, "level": None, "loc": None, "period": None},
        "rows": [],
        "row_count": 0,
        "summary": None,
        "data_sources": {},
        "endpoint_status": {},
        "fetched_at": _iso_now(now),
        "mock": False,
    }


def _iso_now(now: Optional[datetime]) -> str:
    """An ISO-8601 UTC timestamp for provenance. Accepts an injected ``now`` (testable); else uses
    the real UTC clock. TOTAL -> falls back to real clock on a bad ``now``."""
    dt = now if isinstance(now, datetime) else datetime.now(timezone.utc)
    try:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


__all__ = [
    "query_sidra",
    "SidraUnavailable",
    "PRESETS",
]

# Public, read-only view of the preset names (so a caller can list them without touching internals).
PRESETS: Tuple[str, ...] = tuple(sorted(_PRESETS))


# --------------------------------------------------------------------------- #
# CLI -- the orchestrator runs this LIVE (real network, no key). Prints JSON + exit 0.
# --------------------------------------------------------------------------- #
def _main(argv: List[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("CEXAI IBGE SIDRA market-sizing lane (GREEN, official, no key). Usage:")
        print("  python _tools/cex_ibge_sidra.py <preset>")
        print("  presets: %s" % ", ".join(PRESETS))
        print("  (raw power use is available via the importable query_sidra(table=,var=,level=,...))")
        return 0

    arg = argv[0].strip()
    if arg not in _PRESETS:
        # Honest rejection -- NEVER fall back to a guessed table. Still exit 0 with a TOTAL dict so a
        # caller piping JSON gets a parseable honest-null (the rejection is in endpoint_status).
        rec = query_sidra(preset=arg)
        print(json.dumps(rec, ensure_ascii=True, indent=2))
        return 0

    rec = query_sidra(preset=arg)
    print(json.dumps(rec, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
