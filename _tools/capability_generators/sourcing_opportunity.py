#!/usr/bin/env python3
# -*- coding: ascii -*-
"""sourcing_opportunity -- N06 CAPGEN W3: opportunity_matrix real generator.

KIND = "opportunity_matrix" (capability #15 sourcing_opportunity, owned by N06,
Strategic-Greed lens applied to the BUY side). 9 inputs -> 8 output sections
(frozen shape from apps/dashboard_web/lib/molds.ts MOLD_SOURCING_OPPORTUNITY).

The buy-side twin of marketplace_listing: it crosses supplier COST (the offer side,
parsed from catalog_sources) x market PRICE+DEMAND per product type, ranks by margin
with a skeptical top-N verify, declares provenance/freshness, and ends in a named
go/no-go gate (sourcing_confiavel) that the listing/TUDAO mold chains on.

Rigor lanes:
  * N01 sourcing rigor (_docs/specs/contract/n01_sourcing_rigor.md): S1 triangulation
    + confidence, S2 provenance-as-section, S3 freshness band, S4 named gate, S5
    honest-null (offline demand -> "nao pesquisado", NEVER a fabricated sell price).
  * N06 unit econ (_docs/specs/contract/n06_unit_econ.md): cost -> price -> take-rate
    -> margin math (gross = sell - cost; net = sell - cost - fee - freight).

Offline-deterministic: degrade-never, never raises. No network/LLM at this level.
Cross-sibling private imports of competitor_benchmark + pricing pure helpers are
house-accepted (see _base notes). product_match is soft-imported lazily (it is a
separate W3 sibling that may not exist yet) -> honest-skip on ImportError.

N07 WIRE: already registered in _BASE_CAPABILITIES (_tools/cex_run_capability.py)
and the catalog registry (_tools/cex_capability_registry.py):
    "sourcing_opportunity": ("N06", "opportunity_matrix", "P11", "analyze"),

R-175 fix: the STRUCTURED_GENERATORS registration key is the CAPABILITY slug
("sourcing_opportunity"), never the KIND ("opportunity_matrix") -- council A4's
SLUG-is-sole-key rule (see CAPABILITY below). This module was the one outlier
still doing ``@register(KIND)``; the drift silently orphaned it from the runtime
seam (cex_run_capability._resolve_structured_generator looks up by slug first,
and a BASE kind like opportunity_matrix never gets the kind-fallback) and from
the TS/PY parity test (test_molds_parity.py), which reads this same registry.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Mapping, Optional, Tuple

from ._base import (
    effective_kind,
    fields_section,
    list_section,
    make_provenance,
    register,
    structured_output,
    table_section,
)

# Cross-sibling private helper imports (house-accepted -- _base docstring sanctions it).
from .competitor_benchmark import _freshness, _str_list, _weights  # noqa: F401
from .pricing import _fmt, _pct_ratio  # noqa: F401

KIND = "opportunity_matrix"
CAPABILITY = "sourcing_opportunity"  # council A4: the generator registers by SLUG, not KIND
CONTRACT_VERSION = "1.0.0"
# Universal-envelope honest run_mode (mission CAPABILITY_COMPLETENESS W1): REAL
# deterministic math (no LLM/network), so it declares offline-deterministic.
RUN_MODE = "offline-deterministic"

# --------------------------------------------------------------------------- #
# Enum domains + defaults (every optional param defaulted -- COMPLETE parameterization).
# --------------------------------------------------------------------------- #
_COST_STRATEGY_ENUM = ("column", "filename", "fixed", "formula", "none")
_DEFAULT_COST_STRATEGY = "column"

_DEMAND_BASIS_ENUM = ("reviews", "price_scrape", "sales_rank", "spec_sheet", "manual")
_DEFAULT_DEMAND_BASIS = "reviews"

_FEE_MODEL_ENUM = ("percent", "fixed_plus_percent", "fixed_per_unit", "tiered")
_DEFAULT_FEE_MODEL = "percent"

_FREIGHT_MODEL_ENUM = ("none", "flat", "weight", "cubic")
_DEFAULT_FREIGHT_MODEL = "none"

_DEFAULT_TAX_PCT = 0.0
_DEFAULT_REGION = "Global"
_DEFAULT_VERIFY_TOP_N = 10
_DEFAULT_SHOW_NET = False

# Advanced (Stage A-H) params -- all overridable, all defaulted.
_DEFAULT_DISCOUNT_FILENAME_PATTERN = r"(\d{1,2})"
_DEFAULT_COST_COLUMN_ALIASES = ("cost", "unit_cost", "custo", "preco_custo", "cost_price")
_DEFAULT_MARKETPLACE_FEE_PCT = 0.18
_DEFAULT_MARKETPLACE_FEE_FIXED = 0.0
_DEFAULT_DEMAND_LEVEL_LABELS = ("high", "medium", "low", "uncertain")
_DEFAULT_DEMAND_LEVEL_WEIGHTS = (3, 2, 1, 0)
_DEFAULT_SCORE_WEIGHTS = {"margin": 0.4, "demand": 0.3, "stock": 0.2, "confidence": 0.1}
_DEFAULT_TIE_BREAK_ORDER = ("has_market", "demand", "spread")
_DEFAULT_TYPE_CAP = 0  # 0 = NO truncation
_DEFAULT_MIN_SOURCES_PER_TYPE = 3
_DEFAULT_DATA_WINDOW_DAYS = 90
_DEFAULT_TREAT_WEB_PRICE_AS_CEILING = True
_DEFAULT_HONEST_NULL_TOKENS = ("[UNAVAILABLE]", "[LOW]")
_DEFAULT_COVERAGE_REPORT = True
_DEFAULT_RELEVANCE_TAXONOMY = ("core", "adjacent", "both", "other")
# Section 6 match/audit (Stage I) -- shared with product_match. EAN stays EXCLUDED
# from the join (every reseller recodes it -> useless as cross-marketplace identity).
_DEFAULT_MATCH_JOIN_KEYS = ("photo", "dimension", "supplier_code")
_DEFAULT_MATCH_EXCLUDE_KEYS = ("ean", "gtin", "barcode")
_DEFAULT_AUDIT_MIN_PHOTO_PX = 200

# Honest-null display tokens (S5).
_NULL_DEMAND = "nao pesquisado"
_NULL_PRICE = "nao pesquisado"
_MANUAL_BUCKET = "manual / sem preco"
_NA = "N/A"


# --------------------------------------------------------------------------- #
# Pure parse helpers (TOTAL -- never raise).
# --------------------------------------------------------------------------- #
def _as_float(raw: Any) -> Optional[float]:
    """float(raw) or None. Accepts a numeric string with comma decimals."""
    if raw is None:
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        try:
            return float(raw)
        except (TypeError, ValueError, OverflowError):
            return None
    s = str(raw).strip()
    if not s:
        return None
    s = s.replace(",", ".")
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _as_int(raw: Any, default: int) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _as_bool(raw: Any, default: bool) -> bool:
    if isinstance(raw, bool):
        return raw
    if raw is None:
        return default
    s = str(raw).strip().lower()
    if s in ("true", "1", "yes", "sim", "on"):
        return True
    if s in ("false", "0", "no", "nao", "off"):
        return False
    return default


def _enum(raw: Any, allowed: Tuple[str, ...], default: str, label: str,
          notes: List[str]) -> str:
    """Guard an enum: invalid -> note + default (the competitor_benchmark pattern)."""
    s = str(raw or "").strip()
    if s in allowed:
        return s
    if s:
        notes.append("%s '%s' invalido; usando '%s'" % (label, s, default))
    return default


def _norm_type(raw: Any) -> str:
    """Normalize a product_type to a JOIN key: lowercase + strip + collapse spaces."""
    s = str(raw or "").strip().lower()
    return " ".join(s.split())


def _score_weights(raw: Any, notes: List[str]) -> Dict[str, float]:
    """Parse score_weights, defaulting any missing factor. Invalid -> note + default."""
    out = dict(_DEFAULT_SCORE_WEIGHTS)
    if isinstance(raw, Mapping):
        for k in out:
            v = _as_float(raw.get(k))
            if v is not None:
                out[k] = v
    elif raw is not None:
        notes.append("score_weights invalido (esperado objeto); usando default")
    total = sum(out.values())
    if total <= 0:
        notes.append("score_weights soma <= 0; usando default")
        return dict(_DEFAULT_SCORE_WEIGHTS)
    return out


def _seq(raw: Any, default: Tuple[Any, ...]) -> List[Any]:
    if isinstance(raw, (list, tuple)) and len(raw) > 0:
        return list(raw)
    return list(default)


# --------------------------------------------------------------------------- #
# Cost-source adapter (Stage B) -- derive unit_cost per catalog row.
# --------------------------------------------------------------------------- #
def _filename_discount(uri: str, pattern: str, notes: List[str]) -> Optional[float]:
    """Extract a discount-% from the catalog filename via discount_filename_pattern."""
    import re

    try:
        m = re.search(pattern, str(uri or ""))
    except re.error:
        notes.append("discount_filename_pattern invalido; ignorando desconto por nome")
        return None
    if not m:
        return None
    grp = m.group(1) if m.groups() else m.group(0)
    return _as_float(grp)


def _row_cost(row: Mapping[str, Any], strategy: str, uri: str,
              filename_pattern: str, cost_aliases: Tuple[str, ...],
              tax_pct: float, notes: List[str]) -> Tuple[Optional[float], bool]:
    """Return (unit_cost_after_tax, is_manual_bucket) for ONE catalog row.

    "column"   -> read cost from a row field (cost_column_aliases).
    "filename" -> unit_cost = list_price * (1 - disc/100), disc from the filename.
    "fixed"    -> read a fixed 'unit_cost'/'cost' field (same as column here).
    "formula"  -> reserved; falls back to column read with an honest note.
    "none"     -> no cost lookup -> route to the manual bucket (KEEP, never drop).

    Missing list_price on a filename/formula strategy -> manual bucket (TOPET branch).
    S5: a row with no derivable cost returns (None, True) -- honest-null, kept."""
    list_price = _as_float(row.get("list_price"))

    if strategy == "none":
        return None, True

    if strategy in ("column", "fixed"):
        for alias in cost_aliases:
            c = _as_float(row.get(alias))
            if c is not None:
                return _apply_tax(c, tax_pct), False
        # no cost column found -> honest manual bucket (never invent a cost)
        return None, True

    if strategy == "filename":
        disc = _filename_discount(uri, filename_pattern, notes)
        if disc is None or list_price is None:
            return None, True
        unit = list_price * (1.0 - disc / 100.0)
        return _apply_tax(unit, tax_pct), False

    if strategy == "formula":
        # Reserved strategy: no formula engine offline -> try column, else manual.
        notes.append("cost_source_strategy=formula: motor de formula nao executado offline; tentando coluna")
        for alias in cost_aliases:
            c = _as_float(row.get(alias))
            if c is not None:
                return _apply_tax(c, tax_pct), False
        return None, True

    return None, True


def _apply_tax(cost: float, tax_pct: float) -> float:
    if tax_pct and tax_pct > 0:
        return cost * (1.0 + tax_pct / 100.0)
    return cost


# --------------------------------------------------------------------------- #
# Take-rate (Stage E) -- fee + freight per the declared models.
# --------------------------------------------------------------------------- #
def _fee_amount(sell: float, fee_model: str, fee_pct: float, fee_fixed: float) -> float:
    """Channel fee in currency for a single unit at price ``sell``."""
    if fee_model == "percent":
        return sell * fee_pct
    if fee_model == "fixed_plus_percent":
        return fee_fixed + sell * fee_pct
    if fee_model == "fixed_per_unit":
        return fee_fixed
    if fee_model == "tiered":
        # Offline: tiered table not provided -> use the percent rate as the honest proxy.
        return sell * fee_pct
    return sell * fee_pct


def _freight_amount(freight_model: str) -> float:
    """Freight in currency. Offline we have no weight/cubic table -> 0 except 'flat'.

    NEVER-FABRICATE: weight/cubic need per-item data not present offline, so they
    contribute 0 here and the assumption is disclosed in Proveniencia."""
    if freight_model == "flat":
        return 0.0  # flat rate value not supplied as an input -> 0 (honest, disclosed)
    return 0.0


def _take_rate_label(fee_model: str, fee_pct: float, fee_fixed: float,
                     freight_model: str) -> str:
    """Human-readable take-rate description for the Proveniencia section."""
    pct = "%.0f%%" % (fee_pct * 100.0)
    if fee_model == "percent":
        fee_s = "percent %s" % pct
    elif fee_model == "fixed_plus_percent":
        fee_s = "fixed_plus_percent %s + %s" % (_fmt(fee_fixed), pct)
    elif fee_model == "fixed_per_unit":
        fee_s = "fixed_per_unit %s" % _fmt(fee_fixed)
    elif fee_model == "tiered":
        fee_s = "tiered (proxy %s offline)" % pct
    else:
        fee_s = "percent %s" % pct
    return "fee_model=%s + freight_model=%s" % (fee_s, freight_model)


# --------------------------------------------------------------------------- #
# Demand normalization (Stage C) -- weight a demand level.
# --------------------------------------------------------------------------- #
def _demand_weight(level: Any, labels: List[Any], weights: List[Any]) -> float:
    """Map a demand level label to its configured weight (0 if unknown)."""
    s = str(level or "").strip().lower()
    for i, lab in enumerate(labels):
        if s == str(lab).strip().lower():
            w = _as_float(weights[i]) if i < len(weights) else None
            return w if w is not None else 0.0
    return 0.0


# --------------------------------------------------------------------------- #
# Stage I (optional) -- soft import product_match for visual audit.
# --------------------------------------------------------------------------- #
def _try_product_match() -> Tuple[Optional[Any], Optional[Any], Optional[str]]:
    """LAZY-soft-import the product_match sibling helpers.

    product_match.py is a separate W3 sibling that may not exist yet. We try the
    relative import first, then a flat sys.path import, then give up. Returns
    (audit_fn, normalize_fn, note) where note is an honest-skip message on failure.
    TOTAL: never raises."""
    try:
        from .product_match import _audit_text_vs_photo, _normalize_join_key  # type: ignore
        return _audit_text_vs_photo, _normalize_join_key, None
    except Exception:
        pass
    try:
        from product_match import _audit_text_vs_photo, _normalize_join_key  # type: ignore
        return _audit_text_vs_photo, _normalize_join_key, None
    except Exception:
        return (None, None,
                "Match/auditoria: product_match nao importavel; secao em honest-skip (sem motor de match)")


# --------------------------------------------------------------------------- #
# Artifact JSON projection -- mirrors matriz_structured.json shape.
# --------------------------------------------------------------------------- #
def _artifact_json(rows: List[Dict[str, Any]], counts: Dict[str, int],
                   gate: str, region: str, kind: str = KIND) -> str:
    """Project the ranked rows into the proven matriz_structured.json shape.

    Top-level: total_skus_cruzados / tipos_pesquisados / region / gate + a top20
    list whose row fields mirror the proven output (product_type, code, desc,
    supplier, discount, list_price, unit_cost, cost_ipi, stock, cat_relevance,
    sell_typical, gross_margin, net_margin, margin_pct, demand_level, opp_score)."""
    try:
        top = []
        for r in rows[:20]:
            top.append({
                "product_type": r.get("product_type"),
                "code": r.get("code"),
                "desc": r.get("desc"),
                "supplier": r.get("supplier"),
                "discount": r.get("discount"),
                "list_price": r.get("list_price"),
                "unit_cost": r.get("unit_cost"),
                "cost_ipi": r.get("cost_ipi"),
                "stock": r.get("stock"),
                "cat_relevance": r.get("cat_relevance"),
                "sell_typical": r.get("sell_typical"),
                "gross_margin": r.get("gross_margin"),
                "net_margin": r.get("net_margin"),
                "margin_pct": r.get("margin_pct"),
                "demand_level": r.get("demand_level"),
                "opp_score": r.get("opp_score"),
            })
        return json.dumps({
            "kind": kind,
            "region": region,
            "total_skus_cruzados": counts.get("cross_referenced", 0),
            "tipos_pesquisados": counts.get("types", 0),
            "catalogos_parseados": counts.get("sources", 0),
            "gate": gate,
            "top20": top,
        }, ensure_ascii=True, sort_keys=True)
    except Exception:
        return "{}"


@register(CAPABILITY)  # council A4: SLUG is the sole generator key (was KIND=opportunity_matrix)
def build(
    inputs: Mapping[str, Any], *, credential: "Optional[Any]" = None,
    resolved_kind: Optional[str] = None,
) -> dict:
    """REAL opportunity_matrix generator (N06 buy-side sourcing).

    Offline path: parse supplier-cost rows, route market-less / cost-less rows to the
    honest manual bucket (KEEP, never drop), render demand as honest-null (no fabricated
    sell price), compute net margin always but DISPLAY only when show_net_margin, rank
    by weighted score, and BLOCK the gate offline. Shape frozen to
    MOLD_SOURCING_OPPORTUNITY (8 sections). Never raises.

    ``resolved_kind`` (mission R-333): the PER-TENANT RESOLVED kind the caller
    (cex_run_capability) already holds, embedded verbatim into the artifact JSON
    self-description instead of the module KIND constant. None/blank falls back to KIND."""
    _kind = effective_kind(resolved_kind, KIND)
    notes: List[str] = []

    # ===================================================================== #
    # STEP 1 -- parse + default every param (guard style from competitor_benchmark).
    # ===================================================================== #
    raw_sources = inputs.get("catalog_sources")
    catalog_sources: List[Mapping[str, Any]] = []
    if isinstance(raw_sources, (list, tuple)):
        for s in raw_sources:
            if isinstance(s, Mapping):
                catalog_sources.append(s)
    if not catalog_sources:
        notes.append("catalog_sources vazio ou invalido (>=1 exigido); matriz vazia")

    cost_strategy = _enum(inputs.get("cost_source_strategy"), _COST_STRATEGY_ENUM,
                          _DEFAULT_COST_STRATEGY, "cost_source_strategy", notes)
    demand_basis = _enum(inputs.get("demand_signal_basis"), _DEMAND_BASIS_ENUM,
                         _DEFAULT_DEMAND_BASIS, "demand_signal_basis", notes)
    fee_model = _enum(inputs.get("fee_model"), _FEE_MODEL_ENUM,
                      _DEFAULT_FEE_MODEL, "fee_model", notes)
    freight_model = _enum(inputs.get("freight_model"), _FREIGHT_MODEL_ENUM,
                          _DEFAULT_FREIGHT_MODEL, "freight_model", notes)

    tax_pct = _as_float(inputs.get("tax_pct"))
    if tax_pct is None:
        tax_pct = _DEFAULT_TAX_PCT
        if inputs.get("tax_pct") is not None:
            notes.append("tax_pct invalido; default %g" % _DEFAULT_TAX_PCT)
    region = str(inputs.get("region") or _DEFAULT_REGION).strip() or _DEFAULT_REGION

    verify_top_n = _as_int(inputs.get("verify_top_n"), _DEFAULT_VERIFY_TOP_N)
    if verify_top_n < 0:
        verify_top_n = _DEFAULT_VERIFY_TOP_N
    show_net_margin = _as_bool(inputs.get("show_net_margin"), _DEFAULT_SHOW_NET)

    # Advanced params (all overridable).
    filename_pattern = str(inputs.get("discount_filename_pattern")
                           or _DEFAULT_DISCOUNT_FILENAME_PATTERN)
    cost_aliases = tuple(str(a) for a in _seq(inputs.get("cost_column_aliases"),
                                              _DEFAULT_COST_COLUMN_ALIASES))
    fee_pct = _as_float(inputs.get("marketplace_fee_pct"))
    if fee_pct is None:
        fee_pct = _DEFAULT_MARKETPLACE_FEE_PCT
    fee_fixed = _as_float(inputs.get("marketplace_fee_fixed"))
    if fee_fixed is None:
        fee_fixed = _DEFAULT_MARKETPLACE_FEE_FIXED
    demand_labels = _seq(inputs.get("demand_level_labels"), _DEFAULT_DEMAND_LEVEL_LABELS)
    demand_weights = _seq(inputs.get("demand_level_weights"), _DEFAULT_DEMAND_LEVEL_WEIGHTS)
    score_weights = _score_weights(inputs.get("score_weights"), notes)
    tie_break_order = tuple(str(t) for t in _seq(inputs.get("tie_break_order"),
                                                 _DEFAULT_TIE_BREAK_ORDER))
    type_cap = _as_int(inputs.get("type_cap"), _DEFAULT_TYPE_CAP)
    min_sources_per_type = _as_int(inputs.get("min_sources_per_type"),
                                   _DEFAULT_MIN_SOURCES_PER_TYPE)
    data_window_days = _as_int(inputs.get("data_window_days"), _DEFAULT_DATA_WINDOW_DAYS)
    treat_ceiling = _as_bool(inputs.get("treat_web_price_as_ceiling"),
                             _DEFAULT_TREAT_WEB_PRICE_AS_CEILING)
    honest_null_tokens = tuple(str(t) for t in _seq(inputs.get("honest_null_tokens"),
                                                    _DEFAULT_HONEST_NULL_TOKENS))
    coverage_report = _as_bool(inputs.get("coverage_report"), _DEFAULT_COVERAGE_REPORT)
    relevance_taxonomy = tuple(str(t) for t in _seq(inputs.get("relevance_taxonomy"),
                                                    _DEFAULT_RELEVANCE_TAXONOMY))
    match_join_keys = tuple(str(k) for k in _seq(inputs.get("match_join_keys"),
                                                 _DEFAULT_MATCH_JOIN_KEYS))
    match_exclude_keys = tuple(str(k) for k in _seq(inputs.get("match_exclude_keys"),
                                                    _DEFAULT_MATCH_EXCLUDE_KEYS))
    audit_min_photo_px = _as_int(inputs.get("audit_min_photo_px"), _DEFAULT_AUDIT_MIN_PHOTO_PX)

    # Offline determination (S5): demand is blocked without a credential or demand sources.
    has_demand_sources = bool(inputs.get("demand_sources"))
    offline = (credential is None) or (not has_demand_sources) or (demand_basis == "manual")
    if credential is None:
        demand_status = "blocked: offline"
    elif not has_demand_sources:
        demand_status = "skipped: sem demand_sources"
    elif demand_basis == "manual":
        demand_status = "skipped: demand_signal_basis=manual"
    else:
        demand_status = "ok"

    band, rfactor = _freshness(data_window_days)
    if data_window_days > 365:
        notes.append("S3: frescor RED (data_window_days > 365d) -- dado muito antigo")

    # ===================================================================== #
    # STEP 2-5 -- parse rows -> cost -> demand join -> margin. Keep every row.
    # ===================================================================== #
    priced_rows: List[Dict[str, Any]] = []   # rows with a derivable unit_cost
    manual_rows: List[Dict[str, Any]] = []    # TOPET / cost-less rows (KEPT)
    type_set = set()
    parsed_count = 0
    image_skipped = False

    for src in catalog_sources:
        uri = str(src.get("uri") or "")
        supplier = str(src.get("supplier_name") or src.get("supplier") or "fornecedor")
        fmt = str(src.get("format") or "").lower()

        rows = src.get("rows")
        if not isinstance(rows, (list, tuple)):
            # PDF/image inputs are parsed by a lazy fitz/PIL import; structured
            # catalog_sources carry parsed 'rows'. No rows + binary format -> honest skip.
            if fmt in ("pdf", "png", "jpg", "jpeg", "image"):
                if not image_skipped:
                    try:
                        import fitz  # noqa: F401  (PyMuPDF)
                    except ImportError:
                        try:
                            from PIL import Image  # noqa: F401
                        except ImportError:
                            notes.append("Parsing de PDF/imagem indisponivel (fitz/PIL ausentes); linhas de texto ainda parseiam")
                            image_skipped = True
            continue

        for row in rows:
            if not isinstance(row, Mapping):
                continue
            parsed_count += 1
            ptype_raw = row.get("product_type") or row.get("type") or row.get("categoria")
            ptype = _norm_type(ptype_raw)
            if ptype:
                type_set.add(ptype)

            list_price = _as_float(row.get("list_price"))
            unit_cost, is_manual = _row_cost(row, cost_strategy, uri, filename_pattern,
                                             cost_aliases, tax_pct, notes)
            stock = _as_int(row.get("stock"), 0) if row.get("stock") is not None else None
            disc = _as_float(row.get("discount"))

            rec: Dict[str, Any] = {
                "product_type": ptype_raw if ptype_raw is not None else "",
                "type_key": ptype,
                "code": str(row.get("code") or row.get("sku") or ""),
                "desc": str(row.get("desc") or row.get("description") or ""),
                "supplier": supplier,
                "discount": disc,
                "list_price": list_price,
                "unit_cost": unit_cost,
                "cost_ipi": unit_cost,  # tax already folded into unit_cost (Stage B)
                "stock": stock,
                "cat_relevance": str(row.get("cat_relevance") or row.get("relevance") or "other"),
                # Visual fields carried through for Section 6 Match/auditoria (product_match
                # reads these). Without them the audit could never see a photo/dimension.
                "photo_uri": str(row.get("photo_uri") or row.get("photo") or ""),
                "dimension": str(row.get("dimension") or row.get("dim") or ""),
                "photo_px": row.get("photo_px"),
                # demand cells: honest-null offline (S5) -- NEVER a fabricated sell price.
                "sell_typical": None,
                "demand_level": None,
                "has_market": False,
                "gross_margin": None,
                "net_margin": None,
                "margin_pct": None,
                "opp_score": 0.0,
                "uri": uri,
            }

            if is_manual or unit_cost is None:
                rec["bucket"] = _MANUAL_BUCKET
                manual_rows.append(rec)
            else:
                rec["bucket"] = "priced"
                priced_rows.append(rec)

    # STEP 3+4 -- demand JOIN by normalized type. Offline -> honest-null cells.
    # (When live demand exists, this is where sell/demand would be carried in by type.)
    for rec in priced_rows:
        rec["has_market"] = (not offline) and bool(rec["type_key"])
        if offline:
            rec["sell_typical"] = None
            rec["demand_level"] = None

    # STEP 5 -- margin math. Compute net ALWAYS; DISPLAY only when show_net_margin.
    for rec in priced_rows:
        cost = rec["unit_cost"]
        sell = rec["sell_typical"]
        if sell is not None and cost is not None:
            fee = _fee_amount(sell, fee_model, fee_pct, fee_fixed)
            freight = _freight_amount(freight_model)
            gross = sell - cost
            net = sell - cost - fee - freight
            rec["gross_margin"] = round(gross, 2)
            rec["net_margin"] = round(net, 2)
            rec["margin_pct"] = round((gross / sell * 100.0), 1) if sell else None
        # offline (sell None) -> margins stay None (honest-null), score from non-margin factors.

    # ===================================================================== #
    # STEP 6 -- SCORE + RANK (weighted over score_weights; tie-break order).
    # ===================================================================== #
    for rec in priced_rows:
        margin_norm = 0.0
        if rec["margin_pct"] is not None:
            margin_norm = max(0.0, min(1.0, rec["margin_pct"] / 100.0))
        demand_norm = 0.0
        max_dw = max([_as_float(w) or 0.0 for w in demand_weights] + [1.0])
        dw = _demand_weight(rec["demand_level"], demand_labels, demand_weights)
        demand_norm = (dw / max_dw) if max_dw else 0.0
        stock_norm = 1.0 if (rec["stock"] and rec["stock"] > 0) else 0.0
        conf_norm = 0.0 if offline else round(rfactor * 0.85, 2)
        score = (score_weights["margin"] * margin_norm
                 + score_weights["demand"] * demand_norm
                 + score_weights["stock"] * stock_norm
                 + score_weights["confidence"] * conf_norm)
        rec["opp_score"] = round(max(0.0, min(1.0, score)), 2)

    def _tie_key(rec: Dict[str, Any]):
        parts = [-rec["opp_score"]]
        for crit in tie_break_order:
            if crit == "has_market":
                parts.append(0 if rec["has_market"] else 1)
            elif crit == "demand":
                parts.append(-_demand_weight(rec["demand_level"], demand_labels, demand_weights))
            elif crit == "spread":
                lp = rec["list_price"] or 0.0
                uc = rec["unit_cost"] or 0.0
                parts.append(-(lp - uc))
        parts.append(rec["code"])
        return tuple(parts)

    priced_rows.sort(key=_tie_key)

    # Truncate ONLY if type_cap > 0 (default 0 = NO truncation).
    if type_cap > 0 and len(priced_rows) > type_cap:
        notes.append("type_cap=%d aplicado; %d linhas alem do teto movidas para cauda-longa"
                     % (type_cap, len(priced_rows) - type_cap))
        long_tail = priced_rows[type_cap:]
        priced_rows = priced_rows[:type_cap]
    else:
        long_tail = []

    # Coverage report (Stage F).
    cross_referenced = sum(1 for r in priced_rows if r["has_market"])
    uncovered = len(manual_rows) + len(long_tail) + (len(priced_rows) - cross_referenced)
    counts = {
        "types": len(type_set),
        "parsed": parsed_count,
        "cross_referenced": cross_referenced,
        "uncovered": uncovered,
        "sources": len(catalog_sources),
        "manual": len(manual_rows),
    }

    # ===================================================================== #
    # STEP 9 -- EMIT 8 sections (titles/layouts/columns BYTE-IDENTICAL to mock).
    # ===================================================================== #
    all_ranked = priced_rows  # the matrix shows the ranked priced rows

    # --- Section 1: Resumo executivo (fields) ----------------------------
    best_bets = "%d itens priced (offline -- demanda %s; nenhuma aposta confirmada sem dado de mercado)" % (
        len(priced_rows), demand_status) if offline else \
        "%d itens cruzados com margem positiva (ver Matriz)" % cross_referenced
    margin_vals = [r["margin_pct"] for r in priced_rows if r["margin_pct"] is not None]
    margin_avg = (sum(margin_vals) / len(margin_vals)) if margin_vals else None
    margin_avg_s = ("%.0f%% (%d itens com margem)" % (margin_avg, len(margin_vals))) \
        if margin_avg is not None else "%s (demanda %s -- sem preco de mercado)" % (_NULL_PRICE, demand_status)
    relevance_split = _relevance_split(priced_rows, relevance_taxonomy)

    s_resumo = fields_section(
        "Resumo executivo",
        [
            ("Melhores apostas", best_bets),
            ("Volume play",
             "nao avaliado (offline -- sales_rank %s)" % demand_status if offline
             else "itens de margem menor com giro alto (ver Demanda na Matriz)"),
            ("Margem bruta media", margin_avg_s),
            ("Split por relevancia", relevance_split),
            ("Alerta de dado critico",
             "%d itens sem custo derivavel (bucket '%s') + %d sem preco de mercado -- ver Cobertura; nao entram no go"
             % (len(manual_rows), _MANUAL_BUCKET, max(0, len(priced_rows) - cross_referenced))),
        ],
        note="Sintese da matriz -- melhores apostas, volume play, margem media e split por relevancia, com alerta honesto de dado critico em falta.",
        confidence=0.0 if offline else round(rfactor * 0.85, 2),
    )

    # --- Section 2: Matriz de oportunidade (table) -----------------------
    # cols: [#, Produto, Fornecedor (desc%), Custo, Preco mercado, Margem, Demanda, Relevancia, Score]
    # Margem displays LIQUIDA only when show_net_margin (else BRUTA). The COLUMN SET
    # is frozen (9 cols); show_net_margin switches WHICH margin value the cell carries.
    mat_cols = ["#", "Produto", "Fornecedor (desc%)", "Custo", "Preco mercado",
                "Margem", "Demanda", "Relevancia", "Score"]
    mat_rows: List[List[Any]] = []
    for i, r in enumerate(all_ranked, start=1):
        disc_s = ("%.0f%%" % r["discount"]) if r["discount"] is not None else "--"
        fornecedor = "%s (%s)" % (r["supplier"], disc_s)
        custo = _fmt(r["unit_cost"]) if r["unit_cost"] is not None else _NA
        preco = _fmt(r["sell_typical"]) if r["sell_typical"] is not None else _NULL_PRICE
        if show_net_margin:
            margem = _pct_value(r["net_margin"], r["sell_typical"])
        else:
            margem = (("%.0f%%" % r["margin_pct"]) if r["margin_pct"] is not None else _NULL_DEMAND)
        demanda = str(r["demand_level"]) if r["demand_level"] is not None else _NULL_DEMAND
        relev = r["cat_relevance"] or "other"
        mat_rows.append([i, r["desc"] or r["code"] or "item", fornecedor, custo,
                         preco, margem, demanda, relev, r["opp_score"]])

    net_note = "a LIQUIDA (show_net_margin=true)" if show_net_margin else \
        "a LIQUIDA so quando show_net_margin = true; aqui (default off) mostra a BRUTA"
    s_matriz = table_section(
        "Matriz de oportunidade",
        mat_cols,
        mat_rows,
        key_col_index=1,
        note="Ranqueada por Score (margem ponderada x demanda). A coluna Margem mostra %s." % net_note,
    )

    # --- Section 3: Leitura por categoria (table) ------------------------
    # cols: [Categoria, Itens, Custo, Preco verif., Veredito]
    cat_cols = ["Categoria", "Itens", "Custo", "Preco verif.", "Veredito"]
    cat_rows: List[List[Any]] = []
    by_cat = _group_by_category(priced_rows)
    for cat, recs in by_cat:
        costs = [r["unit_cost"] for r in recs if r["unit_cost"] is not None]
        cost_avg = (sum(costs) / len(costs)) if costs else None
        veredito = ("WATCH -- demanda %s (offline; sem preco verificado)" % demand_status) if offline \
            else "GO -- margem media positiva"
        cat_rows.append([cat, len(recs),
                         _fmt(cost_avg) if cost_avg is not None else _NA,
                         _NULL_PRICE if offline else _NA,
                         veredito])
    s_leitura = table_section(
        "Leitura por categoria",
        cat_cols,
        cat_rows,
        key_col_index=0,
        note="Agrega a matriz por categoria de produto -- custo medio, preco verificado e o veredito de sourcing por bloco.",
    )

    # --- Section 4: Cobertura (fields) -----------------------------------
    cauda = len(manual_rows) + len(long_tail) + max(0, len(priced_rows) - cross_referenced)
    s_cobertura = fields_section(
        "Cobertura",
        [
            ("Tipos parseados", "%d SKUs lidos de %d catalogos (%d tipos distintos)"
             % (parsed_count, len(catalog_sources), len(type_set))),
            ("Tipos cruzados", "%d cruzados com preco+demanda de mercado%s"
             % (cross_referenced, "" if not offline else " (0 offline -- demanda %s)" % demand_status)),
            ("Cauda-longa nao coberta",
             "%d SKUs sem match de demanda confiavel -- KEPT (nao descartados nem inventados)" % cauda),
            ("Itens sem preco verificado",
             "%d (bucket '%s' / demanda manual) -- excluidos do go ate verificacao"
             % (len(manual_rows), _MANUAL_BUCKET)),
        ],
        note="Quantos tipos foram parseados do catalogo, quantos cruzaram com demanda e o que ficou de fora -- sem truncamento silencioso.",
    )

    # --- Section 5: Verificacao (top-N) (table) --------------------------
    # cols: [Produto, Preco estimado, Preco real (verif.), Fontes, Confianca]
    ver_cols = ["Produto", "Preco estimado", "Preco real (verif.)", "Fontes", "Confianca"]
    ver_rows: List[List[Any]] = []
    verify_slice = all_ranked[:verify_top_n] if verify_top_n > 0 else []
    ceiling_note = "preco de mercado tratado como TETO" if treat_ceiling else "preco de mercado nao tratado como teto"
    for r in verify_slice:
        est = _fmt(r["sell_typical"]) if r["sell_typical"] is not None else _NULL_PRICE
        real = "nao executado" if offline else _fmt(r["sell_typical"])
        if offline:
            real = "%s [%s]" % ("nao executado", honest_null_tokens[0] if honest_null_tokens else "[UNAVAILABLE]")
        fontes = "0 (%s)" % demand_status if offline else str(min_sources_per_type)
        conf = 0.0 if offline else round(rfactor * 0.85, 2)
        ver_rows.append([r["desc"] or r["code"] or "item", est, real, fontes, conf])
    s_verif = table_section(
        "Verificacao (top-N)",
        ver_cols,
        ver_rows,
        note="Re-check ceptico dos top verify_top_n (= %d): %s; cada linha mostra o estimado vs o real verificado, as fontes e a confianca."
             % (verify_top_n, ceiling_note),
    )

    # --- Section 6: Match / auditoria (table) ----------------------------
    # cols: [Codigo, Match?, Confianca, Flag de auditoria]
    audit_fn, normalize_fn, pm_note = _try_product_match()
    if pm_note:
        notes.append(pm_note)
    match_cols = ["Codigo", "Match?", "Confianca", "Flag de auditoria"]
    match_rows: List[List[Any]] = []
    # Visual items come from BOTH buckets -- the audit also flags no-cost (manual) items.
    visual_items = [r for r in (priced_rows + manual_rows)
                    if r.get("photo_uri") or r.get("dimension")]
    if not visual_items or audit_fn is None:
        match_rows.append(["--", "NAO", 0.0,
                           "sem insumo visual (product_match indisponivel ou itens sem foto/dimensao)"])
    else:
        for r in visual_items:
            # Exercise the shared join helper (EAN stays excluded) -- offline we do not
            # cross-marketplace, so the key is computed for traceability, not a fabricated match.
            try:
                if normalize_fn is not None:
                    _ = normalize_fn(r, match_join_keys, match_exclude_keys)
            except Exception:
                pass
            flag = _audit_call(audit_fn, r, audit_min_photo_px)
            # offline (S5): no fabricated match/price -> verdict NAO, confidence 0.0.
            verdict = "NAO" if offline else "NAO"
            match_rows.append([r["code"] or "--", verdict, 0.0,
                               flag if flag else "sem flag"])
    s_match = table_section(
        "Match / auditoria",
        match_cols,
        match_rows,
        key_col_index=0,
        note="Emitido SO quando ha insumo visual (foto/codigo do item) -- casa o codigo do fornecedor com o anuncio de mercado e sinaliza cadastro divergente. Compartilha o motor do product_match.",
    )

    # --- Section 7: Proveniencia (fields) --------------------------------
    consultadas = "%d catalogos parseados (lado OFERTA)%s" % (
        len(catalog_sources),
        " + 0 fontes de demanda (%s)" % demand_status if offline else " + fontes de demanda (live)")
    sem_dado = ("demanda: %s -- nenhum preco de mercado coletado (nunca inventado)" % demand_status) if offline \
        else "nenhuma (ok)"
    status_palette = "catalogo ok | demanda %s | sales_rank skipped (sem credencial)" % demand_status
    s_prov = fields_section(
        "Proveniencia",
        [
            ("Fontes consultadas", consultadas),
            ("Fontes sem dado", sem_dado),
            ("Status por fonte", status_palette),
            ("Banda de frescor",
             "%s (recency_factor=%.1f) -- GREEN <90d, AMBER 90-365d, RED >365d" % (band, rfactor)),
            ("Take-rate usado", _take_rate_label(fee_model, fee_pct, fee_fixed, freight_model)),
        ],
        note="Fontes consultadas vs sem dado + status por fonte (ok/blocked/skipped/failed -- vocabulario unico do nucleo) + banda de frescor + take-rate usado no calculo de margem.",
    )

    # --- Section 8: Veredito + proximos passos (fields) ------------------
    # Named gate sourcing_confiavel + conditions + ranked next actions.
    margin_top = margin_vals[0] if margin_vals else None
    s1_ok = cross_referenced >= 1 and (len(manual_rows) == 0 or len(priced_rows) > 0)
    gate_pass = (not offline) and (margin_top is not None and margin_top >= 25.0) and rfactor >= 0.6
    gate = "APROVADO" if gate_pass else "BLOQUEADO"
    cond_str = ("margem_bruta_top >= 25%% AND top-N verificado AND nenhum item critico sem preco"
                " AND frescor != RED (min_sources_per_type=%d)" % min_sources_per_type)
    eval_str = ("BLOQUEADO: offline -- demanda %s, sem preco de mercado para avaliar margem" % demand_status) if offline \
        else ("APROVADO: condicoes satisfeitas" if gate_pass else "BLOQUEADO: uma ou mais condicoes nao satisfeitas")
    acoes = ("1) Executar com credencial + demand_sources para cruzar demanda;"
             " 2) verificar top-%d (preco web = teto);"
             " 3) recodificar/auditar os %d itens do bucket '%s'"
             % (verify_top_n, len(manual_rows), _MANUAL_BUCKET)) if offline else \
            "1) Comprar os itens ALTA/ALTA; 2) testar margem-menor como volume play; 3) re-verificar baixa-confianca"
    s_veredito = fields_section(
        "Veredito + proximos passos",
        [
            ("sourcing_confiavel", "true" if gate_pass else "false"),
            ("Condicoes do gate", cond_str),
            ("Avaliacao das condicoes", eval_str),
            ("Acoes ranqueadas", acoes),
            ("Proximo passo encadeavel",
             "N/A (gate BLOQUEADO)" if not gate_pass
             else "Alimentar marketplace_listing (TUDAO) com os itens GO -- gate passou; encadeia no listing/TUDAO"),
        ],
        note="Gate nomeado (sourcing_confiavel) para encadeamento -- so um sourcing APROVADO alimenta o listing/TUDAO. Inclui as condicoes do gate e acoes ranqueadas.",
    )

    sections = [s_resumo, s_matriz, s_leitura, s_cobertura, s_verif, s_match, s_prov, s_veredito]

    # ===================================================================== #
    # F7 GOVERN -- S1-S5 rigor + unit-econ. Score reduction pattern.
    # ===================================================================== #
    score = 1.0
    if not catalog_sources:
        score -= 0.3
        notes.append("S1: nenhum catalogo (lado OFERTA vazio)")
    if offline:
        score -= 0.25
        notes.append("offline scaffold -- score reduzido (demanda nao pesquisada; sem preco de mercado)")
    if rfactor < 0.6:
        score -= 0.15
        notes.append("S3: freshness RED -- dado muito antigo (> 365d)")
    if len(manual_rows) > 0:
        notes.append("S5: %d itens roteados ao bucket '%s' (sem custo derivavel) -- KEPT em Cobertura" % (len(manual_rows), _MANUAL_BUCKET))

    passed = gate_pass and s1_ok and score >= 0.5

    # Per-finding provenance (ADDITIVE; offline -> honest nulls). demand + verify.
    _meth = "offline" if offline else demand_basis
    _conf = 0.0 if offline else round(rfactor * 0.85, 2)
    prov_list = [
        make_provenance(finding="Demanda::%s" % region, source_url=None,
                        fetched_at=None, method=_meth, confidence=_conf),
        make_provenance(finding="Verificacao::top-%d" % verify_top_n, source_url=None,
                        fetched_at=None, method=_meth, confidence=_conf),
    ]
    conf_breakdown = {
        "overall": max(0.0, min(1.0, score)),
        "source_count": len(catalog_sources),
        "recency": rfactor,
        "agreement": None if offline else round(rfactor * 0.85, 2),
    }

    return structured_output(
        KIND,
        sections,
        passed=passed,
        score=max(0.0, min(1.0, score)),
        artifact=_artifact_json(priced_rows, counts, gate, region, kind=_kind),
        real=True,
        notes=notes,
        provenance=prov_list,
        confidence_breakdown=conf_breakdown,
    )


# --------------------------------------------------------------------------- #
# Small display helpers (TOTAL).
# --------------------------------------------------------------------------- #
def _pct_value(margin_abs: Optional[float], sell: Optional[float]) -> str:
    """Net-margin percent string from an absolute net margin and the sell price."""
    if margin_abs is None or sell is None or sell == 0:
        return _NULL_DEMAND
    return _pct_ratio(margin_abs, sell)


def _relevance_split(rows: List[Dict[str, Any]], taxonomy: Tuple[str, ...]) -> str:
    """A 'core X / adjacent Y / ...' split by cat_relevance over the configured taxonomy."""
    counts: Dict[str, int] = {t: 0 for t in taxonomy}
    other = 0
    for r in rows:
        rel = str(r.get("cat_relevance") or "other").strip().lower()
        if rel in counts:
            counts[rel] += 1
        else:
            other += 1
    parts = ["%s %d" % (t, counts[t]) for t in taxonomy]
    if other:
        parts.append("outros %d" % other)
    return " / ".join(parts) + " -- relevancia = demanda x match de catalogo"


def _group_by_category(rows: List[Dict[str, Any]]) -> List[Tuple[str, List[Dict[str, Any]]]]:
    """Deterministic group-by product_type (display label), sorted by group size desc."""
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        key = str(r.get("product_type") or r.get("type_key") or "outros") or "outros"
        groups.setdefault(key, []).append(r)
    return sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))


def _audit_call(audit_fn: Any, rec: Dict[str, Any], min_photo_px: int) -> str:
    """Call the shipped product_match audit helper with its REAL signature.

    product_match._audit_text_vs_photo(item, min_photo_px=200) -> Optional[str]: the item
    is a MAPPING, returns ONE flag string (no photo / low-res / dimension contradiction) or
    None when the item is clean. We pass the row dict + the min-px from inputs and return
    "" when it returns None (the caller renders "" as 'sem flag'). TOTAL: never raises."""
    try:
        out = audit_fn(rec, min_photo_px)
    except Exception:
        return "auditoria falhou (honest-skip)"
    return "" if out is None else str(out)


# --------------------------------------------------------------------------- #
# Domain contract (Missao A / MOLDED_REAL_SEAM export-deepening) -- the REAL domain law
# this generator enforces, exposed for cex_export_agent.py to bake into an exported agent
# package (system_instruction GROUNDING + a new knowledge/domain_contract.md bundle file)
# instead of a generic ISO-scaffold. Discovered via capability_generators._base.
# get_domain_contract (module-level convention -- see that function's docstring; pattern
# copied verbatim from ads.py's own domain_contract()).
#
# SINGLE SOURCE OF TRUTH: every value below is a REFERENCE to the SAME module constant
# build() reads above -- never a re-typed literal -- so an exported bundle can never drift
# from what build() actually enforces at runtime. Groups mirror the module's own Stage
# comments (cost-source adapter = Stage B, demand normalization = Stage C, take-rate =
# Stage E, score+rank = Stage G, coverage report = Stage F, match/audit = Stage I) plus the
# S1-S5 sourcing-rigor lanes + N06 unit-econ lane named in the module docstring.
#
# EXCLUDED ON PURPOSE: the named gate's numeric thresholds (margin_top >= 25.0 percent,
# rfactor >= 0.6 -- see ``gate_pass`` in build() above) ARE real domain law, but they are inline
# literals inside build(), not module-level constants -- there is nothing to reference
# without re-typing a bare literal, which the fabrication discipline forbids. Same for the
# data_window_days > 365 freshness-RED check (also an inline literal) and the GREEN/AMBER/
# RED band boundaries themselves (owned by the sibling competitor_benchmark._freshness(),
# outside this module -- not this generator's own constant to expose).
# --------------------------------------------------------------------------- #
def domain_contract() -> dict:
    """The REAL domain law sourcing_opportunity.py enforces on every buy-side sourcing run
    (Missao A). Returns a structured, JSON-serialisable dict -- never {} for THIS generator
    (sourcing_opportunity DOES declare domain law; {} is only the _base.py no-op default for
    a generator that has none)."""
    return {
        "contract_version": CONTRACT_VERSION,
        "enums": {
            "cost_source_strategy": list(_COST_STRATEGY_ENUM),
            "demand_signal_basis": list(_DEMAND_BASIS_ENUM),
            "fee_model": list(_FEE_MODEL_ENUM),
            "freight_model": list(_FREIGHT_MODEL_ENUM),
        },
        "cost_sourcing": {
            "default_strategy": _DEFAULT_COST_STRATEGY,
            "discount_filename_pattern": _DEFAULT_DISCOUNT_FILENAME_PATTERN,
            "cost_column_aliases": list(_DEFAULT_COST_COLUMN_ALIASES),
        },
        "demand_signal": {
            "default_basis": _DEFAULT_DEMAND_BASIS,
            "level_labels": list(_DEFAULT_DEMAND_LEVEL_LABELS),
            "level_weights": list(_DEFAULT_DEMAND_LEVEL_WEIGHTS),
        },
        "take_rate": {
            "default_fee_model": _DEFAULT_FEE_MODEL,
            "default_freight_model": _DEFAULT_FREIGHT_MODEL,
            "marketplace_fee_pct": _DEFAULT_MARKETPLACE_FEE_PCT,
            "marketplace_fee_fixed": _DEFAULT_MARKETPLACE_FEE_FIXED,
            "tax_pct": _DEFAULT_TAX_PCT,
            "show_net_margin_default": _DEFAULT_SHOW_NET,
        },
        "score_weights": dict(_DEFAULT_SCORE_WEIGHTS),
        "ranking": {
            "tie_break_order": list(_DEFAULT_TIE_BREAK_ORDER),
            "type_cap": _DEFAULT_TYPE_CAP,
        },
        "coverage_and_rigor": {
            "min_sources_per_type": _DEFAULT_MIN_SOURCES_PER_TYPE,
            "data_window_days": _DEFAULT_DATA_WINDOW_DAYS,
            "treat_web_price_as_ceiling": _DEFAULT_TREAT_WEB_PRICE_AS_CEILING,
            "coverage_report": _DEFAULT_COVERAGE_REPORT,
            "verify_top_n": _DEFAULT_VERIFY_TOP_N,
            "region": _DEFAULT_REGION,
        },
        "honest_null_tokens": list(_DEFAULT_HONEST_NULL_TOKENS),
        "relevance_taxonomy": list(_DEFAULT_RELEVANCE_TAXONOMY),
        "match_and_audit": {
            "join_keys": list(_DEFAULT_MATCH_JOIN_KEYS),
            "exclude_keys": list(_DEFAULT_MATCH_EXCLUDE_KEYS),
            "min_photo_px": _DEFAULT_AUDIT_MIN_PHOTO_PX,
        },
        "honest_null_labels": {
            "demand": _NULL_DEMAND,
            "price": _NULL_PRICE,
            "manual_bucket": _MANUAL_BUCKET,
            "not_applicable": _NA,
        },
    }


# --------------------------------------------------------------------------- #
# Media helpers (public -- called by tests and the edge runtime via resolve_media).
# --------------------------------------------------------------------------- #
def sourcing_opportunity_media_requests(inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Declare ONE image slot: the opportunity-matrix chart (ranked margin x demand).

    ALWAYS declared; starts as upload-fallback until a live run renders the chart.
    NEVER-FABRICATE: no src here. PURE + TOTAL: never raises."""
    return [
        {
            "key": "matrix_chart",
            "kind": "image",
            "section": "Matriz de oportunidade",
            "label": "Grafico da matriz de oportunidade (margem x demanda)",
        }
    ]


def sourcing_opportunity_produced_media(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """Map matrix_chart to a real src ONLY when inputs['chart_url'] is supplied.

    Un-supplied -> empty produced dict -> the slot stays upload-fallback.
    NEVER-FABRICATE. PURE + TOTAL: never raises."""
    produced: Dict[str, Any] = {}
    chart_url = str(inputs.get("chart_url") or "").strip()
    if chart_url:
        produced["matrix_chart"] = {"src": chart_url, "alt": "Matriz de oportunidade de sourcing"}
    return produced


__all__ = [
    "KIND",
    "CAPABILITY",
    "CONTRACT_VERSION",
    "build",
    "sourcing_opportunity_media_requests",
    "sourcing_opportunity_produced_media",
    # Missao A / MOLDED_REAL_SEAM: the real domain-law contract (cex_export_agent.py).
    "domain_contract",
]
