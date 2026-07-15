"""Tenant-scoped marketplace time-series store -- the longitudinal foundation
(the Keepa / Nubimetrics moat). Spec: _docs/compiled/spec_extraction_depth_v1.md
Section 4 (the marketplace_observation table) + W4.

This is the WRITE + READ surface over the ``marketplace_observation`` table
(migration 20260619000001_marketplace_observation.sql). It is a thin specialization
of ``SupabaseDataAdapter`` -- it does NOT re-implement the tenant boundary; every
call goes THROUGH the adapter's ``write`` / ``query`` so the framework-side
cross-tenant mirror (spec C.1 of the data-plane spec) and the pooled-connection
claim bind (``bind_session_tenant``, is_local=True) apply unchanged. The DB-side
RLS policy on the table is the authoritative boundary; this module adds the
time-series shape on top.

THE BOUNDARY RULE (inherited from the data lane -- non-negotiable):
    Every method takes ``tenant_id`` as an EXPLICIT parameter; nothing reads
    ``CEX_TENANT_ID`` (that resolution is the ``_tools`` edge's job). The module
    MUST NOT import repo-root ``_tools`` (cexai is extraction-bound,
    cexai/pyproject.toml). It composes ``SupabaseDataAdapter`` from the same
    package, so the no-_tools-import + explicit-tenant_id invariants hold by
    construction.

READ-TIME METRICS (spec Section 4 "Read-time metrics -- computed, not stored"):
    ``read_series`` returns the raw ordered rows PLUS two derived series computed
    in Python at read time, never persisted:
      * sales_velocity -- diff(sold) between consecutive captured_at (units/day),
        from the LAST consecutive pair that carries two real ``sold`` integers.
      * price_history  -- the ordered (captured_at, price) series (the Keepa view).
    Both are honest-null when there are < 2 usable captures (the spec's
    "insufficient history" path); the engine never fabricates a trend.

WRITE PATH (spec Section 4 "Write path -- capture"):
    ``append_observation`` writes ONE row per candidate per capture through the
    adapter's ``write`` (so RLS WITH CHECK + the framework mirror both gate it).
    The Pass-2 ML lane calls this after each catalog pass; the scheduled
    re-capture (the schedule artifact) calls it per tracked item on a cadence.

ASCII-only per .claude/rules/ascii-code-rule.md. Import-light (Article VIII): only
stdlib + intra-package names at import time; NO concrete DB driver is imported
here (the ``DbSession`` Protocol is the injected seam, same as the adapter).

absorbs: marketplace-extraction-depth (W4 -- time-series store)
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from cexai.governance.data.adapter import DbSession, SupabaseDataAdapter

__all__ = [
    "Observation",
    "MarketplaceObservationStore",
]

# The table the store writes/reads (migration 20260619000001). A module constant
# (not a caller argument) so the SQL is fixed text, never built from input.
_TABLE = "marketplace_observation"

# The columns appended on a capture, in a FIXED order. ``id`` / ``captured_at`` /
# ``created_at`` are server-defaulted by the DDL (gen_random_uuid / now()) and are
# NOT written here -- a capture supplies the measured fields only; ``tenant_id``
# is bound from the explicit argument, never from the payload (so a payload cannot
# smuggle a foreign tenant past the boundary).
_INSERT_COLUMNS = (
    "tenant_id",
    "marketplace",
    "item_id",
    "catalog_id",
    "price",
    "sold",
    "sold_bucket",
    "bsr_rank",
    "buy_box_seller",
    "num_offers",
    "rating",
    "reviews",
    "source",
)

# The measured fields a caller may supply in an Observation mapping (everything in
# _INSERT_COLUMNS EXCEPT tenant_id, which is the explicit argument). ``source``
# defaults to 'meli_api' (matching the DDL default) when the caller omits it.
_PAYLOAD_FIELDS = tuple(c for c in _INSERT_COLUMNS if c != "tenant_id")

# A capture observation: a mapping of measured fields. Kept as a type alias (not a
# dataclass) so callers can pass a plain dict from the Pass-2 normalizers without
# importing a model -- import-light, and the store validates keys itself.
Observation = Mapping[str, Any]


def _coerce_str(value: Any) -> str:
    """Project a value to a stripped string; None -> empty string. Used to
    validate the required ``marketplace`` field (empty -> caller error)."""
    if value is None:
        return ""
    return str(value).strip()


class MarketplaceObservationStore:
    """Time-series store over ``marketplace_observation`` (spec Section 4).

    Wraps a ``SupabaseDataAdapter`` so the tenant boundary is enforced once, in
    one place: ``append_observation`` -> adapter.write, ``read_series`` ->
    adapter.query. The PRECONDITION on every call is that the session claim is
    already bound for the transaction (``adapter.bind_session_tenant``) -- the
    same contract the adapter documents; an unbound session fails closed with
    ``TenantDataDenied('missing_tenant')`` from the adapter, never a silent
    unscoped read.

    Constructed with the SAME ``DbSession`` factory as the adapter (or an
    already-built adapter, for callers that share one). The store holds no state
    of its own beyond the adapter."""

    def __init__(
        self,
        adapter: SupabaseDataAdapter,
    ) -> None:
        self._adapter = adapter

    @property
    def adapter(self) -> SupabaseDataAdapter:
        """The underlying tenant-scoped data adapter (exposes
        ``bind_session_tenant`` for the caller to bind the session claim)."""
        return self._adapter

    # -- write (capture) ----------------------------------------------------- #
    def append_observation(
        self,
        session: DbSession,
        tenant_id: str,
        obs: Observation,
    ) -> Any:
        """Append ONE capture row for ``tenant_id`` (spec Section 4 write path).

        ``obs`` is a mapping of measured fields (a subset of: marketplace,
        item_id, catalog_id, price, sold, sold_bucket, bsr_rank, buy_box_seller,
        num_offers, rating, reviews, source). ``marketplace`` is REQUIRED (the
        DDL has it NOT NULL); a missing/blank ``marketplace`` raises ``ValueError``
        BEFORE any DB call. ``tenant_id`` is the EXPLICIT boundary argument -- it
        is bound positionally into the INSERT and is NEVER taken from ``obs`` (a
        payload cannot smuggle a foreign tenant). ``source`` defaults to
        'meli_api' (the DDL default) when omitted.

        Goes through ``adapter.write`` so the RLS WITH CHECK + the framework-side
        cross-tenant mirror both gate the row; the adapter raises
        ``TenantDataDenied`` on a cross-tenant or unbound call (fail-closed)."""
        marketplace = _coerce_str(obs.get("marketplace"))
        if not marketplace:
            raise ValueError(
                "append_observation: 'marketplace' is required (NOT NULL in the "
                "marketplace_observation DDL)"
            )

        # Build the column list + positional params. tenant_id is bound from the
        # explicit argument (boundary), never from obs. Every other column is read
        # from obs (absent -> NULL, except source -> the DDL default).
        cols: list[str] = []
        params: list[Any] = []
        for col in _INSERT_COLUMNS:
            cols.append(col)
            if col == "tenant_id":
                params.append(tenant_id)
            elif col == "source":
                supplied = obs.get("source")
                params.append(supplied if supplied not in (None, "") else "meli_api")
            else:
                params.append(obs.get(col))

        placeholders = ", ".join(["%s"] * len(cols))
        sql = f"INSERT INTO {_TABLE} ({', '.join(cols)}) VALUES ({placeholders})"
        return self._adapter.write(session, tenant_id, sql, params)

    # -- read (series + read-time metrics) ----------------------------------- #
    def read_series(
        self,
        session: DbSession,
        tenant_id: str,
        marketplace: str,
        item_id: str,
    ) -> dict[str, Any]:
        """Read the time series for one tracked item and compute read-time metrics
        (spec Section 4 "Read-time metrics -- computed, not stored").

        Returns a dict::

            {
              "tenant_id": <tenant_id>,
              "marketplace": <marketplace>,
              "item_id": <item_id>,
              "observations": [<row>, ...],          # ordered by captured_at ASC
              "captures": <int>,                     # len(observations)
              "sales_velocity": <float | None>,      # diff(sold)/diff(days)
              "price_history": [                      # the Keepa view
                  {"captured_at": <ts>, "price": <num>}, ...
              ],
            }

        Goes through ``adapter.query`` (RLS-scoped + framework mirror). The rows
        are fetched ordered by ``captured_at`` ASC; velocity + price_history are
        derived HERE, never read from storage. ``sales_velocity`` is None when
        there are < 2 captures carrying real ``sold`` integers (the honest
        "insufficient history" path); ``price_history`` lists only captures whose
        ``price`` is non-null."""
        sql = (
            f"SELECT captured_at, price, sold, num_offers, rating, reviews, "
            f"buy_box_seller, bsr_rank, sold_bucket, source "
            f"FROM {_TABLE} "
            f"WHERE tenant_id = %s AND marketplace = %s AND item_id = %s "
            f"ORDER BY captured_at ASC"
        )
        raw = self._adapter.query(session, tenant_id, sql, [tenant_id, marketplace, item_id])
        rows = _rows_to_dicts(raw)

        return {
            "tenant_id": tenant_id,
            "marketplace": marketplace,
            "item_id": item_id,
            "observations": rows,
            "captures": len(rows),
            "sales_velocity": compute_velocity(rows),
            "price_history": compute_price_history(rows),
        }


# =========================================================================== #
# Read-time metric helpers (pure functions over the ordered rows)             #
# --------------------------------------------------------------------------- #
# Module-level + pure so they are unit-testable WITHOUT a DB or an adapter, and  #
# so a future surface (a richer reader, a CLI) reuses the same derivation. They  #
# NEVER fabricate: insufficient data -> None / empty, the honest path.          #
# =========================================================================== #

# The ordered fields read_series SELECTs, in order -- used to map a positional
# row (a DB cursor often yields tuples) into a dict. A row that is ALREADY a
# mapping is passed through unchanged.
_SELECT_FIELDS = (
    "captured_at",
    "price",
    "sold",
    "num_offers",
    "rating",
    "reviews",
    "buy_box_seller",
    "bsr_rank",
    "sold_bucket",
    "source",
)


def _rows_to_dicts(raw: Any) -> list[dict[str, Any]]:
    """Normalize the adapter/cursor result into a list of field dicts.

    Accepts: a list/tuple of rows where each row is either a mapping (returned
    as-is, shallow-copied) or a positional sequence (zipped against
    _SELECT_FIELDS). A non-iterable / None result -> empty list. This keeps the
    store agnostic to whether the injected DbSession yields dict-rows or tuples
    (the FakeDbSession in tests can hand back either)."""
    if raw is None:
        return []
    # A bare string/bytes is iterable but not a row collection -- guard it out.
    if isinstance(raw, (str, bytes)):
        return []
    try:
        iterator = list(raw)
    except TypeError:
        return []
    out: list[dict[str, Any]] = []
    for row in iterator:
        if isinstance(row, Mapping):
            out.append(dict(row))
        elif isinstance(row, Sequence) and not isinstance(row, (str, bytes)):
            out.append({field: row[i] if i < len(row) else None
                        for i, field in enumerate(_SELECT_FIELDS)})
        # anything else (a scalar) is not a usable row -> skipped (never invented)
    return out


def _to_epoch_seconds(value: Any) -> float | None:
    """Project a captured_at value to epoch seconds for diffing.

    Accepts a datetime (has .timestamp()), an int/float (already epoch seconds),
    or an ISO-8601 string (parsed leniently). Returns None when it cannot be
    interpreted (that capture is then unusable for a velocity diff -- honest)."""
    if value is None:
        return None
    # datetime-like: anything exposing timestamp()
    ts = getattr(value, "timestamp", None)
    if callable(ts):
        try:
            return float(ts())
        except (TypeError, ValueError, OverflowError):
            return None
    if isinstance(value, bool):  # bool is an int subclass -- not a timestamp
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        # Lenient ISO-8601 parse via datetime (stdlib). 'Z' -> '+00:00'.
        from datetime import datetime

        normalized = text.replace("Z", "+00:00") if text.endswith("Z") else text
        try:
            return datetime.fromisoformat(normalized).timestamp()
        except ValueError:
            return None
    return None


def _to_int_or_none(value: Any) -> int | None:
    """Project a ``sold`` value to int, or None if absent/uninterpretable. Bool is
    rejected (it is an int subclass but never a real sold count)."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return int(text)
        except ValueError:
            try:
                return int(float(text))
            except ValueError:
                return None
    return None


def compute_velocity(rows: Sequence[Mapping[str, Any]]) -> float | None:
    """Sales velocity = diff(sold) / diff(days) over the LAST consecutive pair of
    captures that BOTH carry a real ``sold`` integer AND a usable ``captured_at``
    (spec Section 4: "diff(sold) between consecutive captured_at, units/day").

    Returns None (honest "insufficient history") when fewer than 2 such usable
    captures exist, or when the two captures share the same instant (a zero time
    delta -- velocity is undefined, never fabricated). A negative diff (sold
    decreased, e.g. a corrected bucket) yields a negative velocity rather than
    being clamped -- the read layer reports what the rows say.

    Rows are assumed ordered by captured_at ASC (read_series orders them); the
    function uses the last two USABLE points so a late capture with a null sold
    does not blank out an otherwise-computable velocity."""
    usable: list[tuple[float, int]] = []
    for row in rows:
        epoch = _to_epoch_seconds(row.get("captured_at"))
        sold = _to_int_or_none(row.get("sold"))
        if epoch is None or sold is None:
            continue
        usable.append((epoch, sold))
    if len(usable) < 2:
        return None
    (t0, s0), (t1, s1) = usable[-2], usable[-1]
    delta_seconds = t1 - t0
    if delta_seconds == 0:
        return None  # same instant -> undefined units/day (never invented)
    delta_days = delta_seconds / 86400.0
    return (s1 - s0) / delta_days


def compute_price_history(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """The Keepa view: the ordered (captured_at, price) series (spec Section 4).

    Includes only captures whose ``price`` is non-null (a null-price capture is
    omitted, not interpolated). Order is preserved from the input (read_series
    feeds rows ordered by captured_at ASC). Returns [] when no capture carries a
    price -- the honest "insufficient history" empty series, never a fabricated
    point."""
    history: list[dict[str, Any]] = []
    for row in rows:
        price = row.get("price")
        if price is None:
            continue
        history.append({"captured_at": row.get("captured_at"), "price": price})
    return history
