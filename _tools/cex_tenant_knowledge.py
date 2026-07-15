# -*- coding: ascii -*-
"""cex_tenant_knowledge.py -- the FLYWHEEL RETURN LEG (arch-council wave 0.5, Group B / B1).

THE GAP THIS CLOSES (the council's B1 HIGH). The FORWARD leg works: a capability run ->
cex_runtime_sync.RuntimeSyncWriter.persist_artifact writes the produced artifact INTO the
tenant's OWN Supabase tenant_data (tenant_id EXPLICIT, RLS-enforced) -> the admin reads it
back via the dashboard /results, /entity, /summary routes. But the BRAIN side -- the
tenant's CEXAI CLI / agent -- had NO way to read what the capabilities produced: the
council found ZERO ``FROM tenant_data`` anywhere in cex_sdk/. So the loop was one-way: the
brain wrote knowledge but could never CONSUME it back. This module is that missing reader.

WHAT IT WIRES (the brain-side SELECT, REUSE > rebuild):
  * recent_knowledge(tenant_id, *, limit, capability=None) -> list[TenantKnowledge]
      SELECTs the tenant's most-recent tenant_data rows THROUGH the SAME audited
      SupabaseDataAdapter the WRITER uses, under the SAME verified-claim bind
      (bind_session_tenant -> set_config is_local=True), and projects each row's jsonb
      payload as TYPED knowledge: {record_id, capability, kind, created_at, artifact,
      structured, meta}. This is how the tenant's brain reads what the capabilities
      produced -- the mirror image of persist_artifact, on the SAME isolation seam.
  * recent_products(tenant_id, *, limit) / find_product(tenant_id, ref)
      the EDIT->REFLECT (B2) source: the admin product-editor persists a product as a
      MANAGED ENTITY row (tenant_data kind='products', via apps/dashboard_api/entities.
      EntityManager) -- so reading kind='products' back IS reading the admin's current
      product data. find_product matches a sku / slug / record_id against those rows so a
      run can hydrate inputs['product_record'] from the tenant's CURRENT catalog (the loop
      that makes "edit a product -> the next ad reflects it" real).

THE ISOLATION SEAM (REUSED, never re-implemented -- the council INVARIANT):
  Every read binds the verified-claim tenant onto a fresh session (adapter.
  bind_session_tenant) and calls adapter.query (NOT session.execute directly) so the
  adapter's cross-tenant equality mirror fires AND the row is scoped by the explicit
  ``WHERE tenant_id = %s`` predicate AND the DB-side RLS USING clause. THREE layers, same
  as the writer. A different tenant's claim can NEVER surface this tenant's rows: the bind
  + the predicate + RLS all agree. This module adds NO raw cross-tenant query (it never
  touches session.execute itself); it is a thin, read-only projection over the audited
  adapter -- exactly the writer's pattern, in reverse.

DEGRADE-NEVER / FAIL-CLOSED:
  * make_tenant_knowledge_reader(None) (no central creds / no session factory) returns a
    LOCAL-ONLY reader: every read returns [] (or None), NEVER raises, NEVER touches a
    session -> the brain proceeds with no recalled knowledge rather than crashing. A
    missing data plane never blocks the brain.
  * With a factory, an empty/missing tenant_id binds to nothing -> the adapter raises
    TenantDataDenied('missing_tenant') from bind_session_tenant; recent_knowledge catches
    it and returns [] (a read that cannot be tenant-scoped yields NOTHING, never another
    tenant's rows). A cross-tenant bound-vs-target mismatch is impossible here (the bind
    and the predicate use the SAME tid), but the adapter mirror still guards it.

ALLOWED IMPORT DIRECTION (ADR D6 / adapter THE BOUNDARY RULE): _tools MAY import cexai
(this glue depends on the package). cexai MUST NEVER import _tools. This reader lives in
_tools precisely so the cexai import sits on the allowed side. The adapter is REUSED, never
re-implemented; the RLS is REUSED, never re-declared. It mirrors cex_runtime_sync's path
shim + adapter construction verbatim so the two seams stay in lockstep.

ASCII-only per .claude/rules/ascii-code-rule.md.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

# --------------------------------------------------------------------------- #
# cexai import resolution -- MIRRORS cex_runtime_sync._ensure_cexai_importable #
# (the SAME allowed direction _tools -> cexai; cexai never imports back).      #
# --------------------------------------------------------------------------- #
_REPO_ROOT = Path(__file__).resolve().parent.parent
_CEXAI_IMPORT_ROOT = _REPO_ROOT / "cexai"


def _ensure_cexai_importable() -> None:
    """Idempotently put <repo_root>/cexai on sys.path so the package resolves. No-op if
    already importable / present. APPEND (not insert-0) so a real installed package or a
    caller's deliberate ordering is never shadowed. Mirrors cex_runtime_sync exactly."""
    p = str(_CEXAI_IMPORT_ROOT)
    if _CEXAI_IMPORT_ROOT.is_dir() and p not in sys.path:
        sys.path.append(p)


_ensure_cexai_importable()

# The package side (allowed import direction). The adapter + its deny leaf are REUSED
# as-is; this module re-implements NEITHER.
from cexai.governance.data.adapter import (  # noqa: E402
    DbSession,
    SupabaseDataAdapter,
)
from cexai.governance.data.errors import TenantDataDenied  # noqa: E402

__all__ = [
    "TenantKnowledge",
    "TenantKnowledgeReader",
    "LocalOnlyKnowledgeReader",
    "make_tenant_knowledge_reader",
    "PRODUCTS_ENTITY_KIND",
    "TenantDataDenied",
    "DbSession",
    "SupabaseDataAdapter",
]

# The tenant table the brain reads back FROM (the SAME table the writer persists INTO:
# supabase/migrations/20260616000002_tenant_data.sql + ...0001 capability column).
_TENANT_DATA_TABLE = "tenant_data"

# The managed-entity ``kind`` (= tenant_data.kind slug) the admin product-editor writes a
# product row under. IDENTICAL to the slug apps/dashboard_api/entities.EntityManager uses
# for the ``products`` managed entity (the slug IS the kind). The EDIT->REFLECT (B2) source.
PRODUCTS_ENTITY_KIND = "products"

# A bounded default page size so a brain recall never scans an unbounded table.
_DEFAULT_LIMIT = 25
_MAX_LIMIT = 500

# The product-ref payload keys find_product matches against (case-insensitive on the value),
# in priority order: an exact record_id (the row id) wins, then sku, then slug.
_PRODUCT_SKU_KEYS = ("sku", "SKU", "Sku")
_PRODUCT_SLUG_KEYS = ("slug", "handle", "Slug")


# --------------------------------------------------------------------------- #
# TenantKnowledge -- ONE recalled tenant_data row projected as typed knowledge.
# --------------------------------------------------------------------------- #
@dataclass
class TenantKnowledge:
    """One tenant_data row, projected for the brain. NEVER carries a secret (the writer's
    _safe_meta already stripped any key-shaped field before the row was written; this
    read-only projection adds nothing)."""

    record_id: str
    capability: str
    kind: str
    created_at: str = ""
    artifact: str = ""                      # the produced artifact text (payload.artifact)
    structured: Optional[dict] = None       # payload.meta.structured, when present
    meta: Dict[str, Any] = field(default_factory=dict)  # the safe meta (minus 'structured')
    payload: Dict[str, Any] = field(default_factory=dict)  # the FULL raw jsonb payload (managed-
    #   entity rows -- e.g. products -- store their fields at payload TOP level, not under .meta)

    def to_dict(self) -> Dict[str, Any]:
        """JSON-safe plain dict (the brain / CLI surface)."""
        return {
            "record_id": self.record_id,
            "capability": self.capability,
            "kind": self.kind,
            "created_at": self.created_at,
            "artifact": self.artifact,
            "structured": self.structured,
            "meta": dict(self.meta),
            "payload": dict(self.payload),
        }


def _coerce_tenant(value: Any) -> str:
    """Project a raw tenant value to a stripped string (mirrors the adapter/writer helper).
    None -> empty string; empty result means 'no usable tenant' -> the adapter fails closed."""
    if value is None:
        return ""
    return str(value).strip()


def _clamp_limit(limit: Any) -> int:
    """Coerce + clamp a caller limit into [1, _MAX_LIMIT], defaulting on a bad value."""
    try:
        n = int(limit)
    except (TypeError, ValueError):
        return _DEFAULT_LIMIT
    if n < 1:
        return 1
    if n > _MAX_LIMIT:
        return _MAX_LIMIT
    return n


class TenantKnowledgeReader:
    """The concrete brain-side reader (council B1). Wraps a SupabaseDataAdapter bound to a
    session factory -- the SAME adapter + session-factory seam cex_runtime_sync.
    RuntimeSyncWriter uses for the write path. Every method takes tenant_id EXPLICITLY,
    binds the verified claim onto a fresh session, and reads THROUGH adapter.query
    (tenant_id explicit, RLS + the cross-tenant mirror) inside that one session/transaction
    (spec A.5). Read-only: it never writes.

    Construct via make_tenant_knowledge_reader (which returns a LocalOnlyKnowledgeReader
    when no factory is configured -- degrade-never). The session_factory is a zero-arg
    callable returning a DbSession (production: a pooled Supabase connection; tests: a
    fake). The adapter is REUSED, never re-implemented."""

    def __init__(
        self,
        session_factory: Callable[[], DbSession],
        *,
        adapter: Optional[SupabaseDataAdapter] = None,
    ) -> None:
        self._factory = session_factory
        # Reuse the audited adapter; allow injection for tests, else construct the real one
        # over the SAME factory (identical to RuntimeSyncWriter.__init__).
        self._adapter = adapter if adapter is not None else SupabaseDataAdapter(session_factory)

    # -- the flywheel RETURN LEG (B1) --------------------------------------- #
    def recent_knowledge(
        self,
        tenant_id: str,
        *,
        limit: int = _DEFAULT_LIMIT,
        capability: Optional[str] = None,
    ) -> List[TenantKnowledge]:
        """Read the tenant's most-recent tenant_data rows as typed knowledge (B1).

        SELECTs id, capability, kind, payload, created_at FROM tenant_data WHERE
        tenant_id = <claim> [AND capability = <capability>] ORDER BY created_at DESC LIMIT
        <limit>, THROUGH adapter.query (tenant-scoped + the cross-tenant mirror). Each row's
        jsonb payload is projected: payload.artifact -> .artifact, payload.meta.structured
        -> .structured, the rest of payload.meta -> .meta.

        DEGRADE-NEVER: an empty tenant_id, an unbound/denied bind (TenantDataDenied), or ANY
        read surprise -> [] (NEVER another tenant's rows, NEVER a crash). The optional
        ``capability`` filter is a bound param (never string-concatenated) so there is no
        injection surface."""
        tid = _coerce_tenant(tenant_id)
        if not tid:
            return []  # no tenant to scope -> nothing (fail-closed, never a global read)
        cap = (capability or "").strip()
        n = _clamp_limit(limit)
        try:
            session = self._factory()
            # The bind is the verified-claim scope; a missing/denied bind raises here and we
            # degrade to [] below (a read that cannot be scoped yields nothing).
            self._adapter.bind_session_tenant(session, {"tenant": tid})
            if cap:
                sql = (
                    "SELECT id, capability, kind, payload, created_at FROM "
                    + _TENANT_DATA_TABLE
                    + " WHERE tenant_id = %s AND capability = %s "
                    "ORDER BY created_at DESC LIMIT %s"
                )
                params: List[Any] = [tid, cap, n]
            else:
                sql = (
                    "SELECT id, capability, kind, payload, created_at FROM "
                    + _TENANT_DATA_TABLE
                    + " WHERE tenant_id = %s "
                    "ORDER BY created_at DESC LIMIT %s"
                )
                params = [tid, n]
            result = self._adapter.query(session, tid, sql, params)
        except TenantDataDenied:
            # A read that cannot be tenant-bound is a denied read -> NOTHING (never global).
            return []
        except Exception:
            # DEGRADE-NEVER: any driver/shape surprise -> empty recall, never a crash.
            return []
        return _project_rows(result)

    # -- the EDIT->REFLECT source (B2) -------------------------------------- #
    def recent_products(
        self, tenant_id: str, *, limit: int = _MAX_LIMIT
    ) -> List[TenantKnowledge]:
        """Read the tenant's managed ``products`` rows (tenant_data kind='products'), the
        SAME rows the admin product-editor writes. Tenant-scoped via the SAME audited bind +
        adapter.query. DEGRADE-NEVER: any failure -> []."""
        tid = _coerce_tenant(tenant_id)
        if not tid:
            return []
        n = _clamp_limit(limit)
        try:
            session = self._factory()
            self._adapter.bind_session_tenant(session, {"tenant": tid})
            sql = (
                "SELECT id, capability, kind, payload, created_at FROM "
                + _TENANT_DATA_TABLE
                + " WHERE tenant_id = %s AND kind = %s "
                "ORDER BY created_at DESC LIMIT %s"
            )
            params: List[Any] = [tid, PRODUCTS_ENTITY_KIND, n]
            result = self._adapter.query(session, tid, sql, params)
        except TenantDataDenied:
            return []
        except Exception:
            return []
        return _project_rows(result)

    def find_product(
        self, tenant_id: str, ref: str
    ) -> Optional[Dict[str, Any]]:
        """Find ONE current product record by ``ref`` (a sku / slug / record_id), or None.

        Reads the tenant's ``products`` rows (recent_products, tenant-scoped) and matches
        ``ref`` against each row's record_id, then payload sku, then payload slug
        (case-insensitive on the value). Returns the matched product PAYLOAD (the
        product_catalog_schema-ish dict the admin saved) with its row id folded in under
        'id' / 'record_id' -- the shape a downstream ad/catalog generator consumes as
        inputs['product_record']. NEVER fabricates: no match -> None.

        DEGRADE-NEVER: any failure (no data plane / read error / empty ref) -> None. This is
        the EDIT->REFLECT bridge: the product the admin just edited IS what this returns."""
        want = (ref or "").strip()
        if not want:
            return None
        want_low = want.lower()
        rows = self.recent_products(tenant_id)
        # PASS 1: an exact record_id match wins (the most specific ref).
        for row in rows:
            if row.record_id and row.record_id == want:
                return _product_payload(row)
        # PASS 2: a sku/slug match within the saved payload (case-insensitive value compare).
        for row in rows:
            payload = row.payload if isinstance(row.payload, Mapping) else {}
            if _payload_ref_matches(payload, want, want_low):
                return _product_payload(row)
        return None

    # -- the generic managed-entity READ (the LEADS-injection source) ------- #
    def list_entity(
        self, tenant_id: str, kind: str, *, limit: int = _MAX_LIMIT
    ) -> Tuple[Dict[str, Any], ...]:
        """Read the tenant's managed-entity rows for an arbitrary ``kind`` (the tenant_data.
        kind slug -- e.g. 'contacts' for B2B leads) as a tuple of row payload dicts (each the
        saved entity fields with the row id folded in under 'id' / 'record_id'). Tenant-scoped
        via the SAME audited bind + adapter.query as recent_products / recent_knowledge (the
        ``kind`` is a BOUND param, never string-concatenated -> no injection surface).

        Powers the CRM / Sales-Assistant LIVE-leads seam (cex_run_capability._inject_leads_
        entity): the SAME tenant_data rows the managed-entity Data-tab CRUD writes, read back
        tenant-scoped + RLS-enforced. Generalizes find_product's read to any entity kind.

        DEGRADE-NEVER: an empty tenant_id / kind, an unbound or denied (cross-tenant) bind
        (TenantDataDenied), or ANY read surprise -> () (NEVER another tenant's rows, NEVER a
        crash). NEVER fabricates a row."""
        tid = _coerce_tenant(tenant_id)
        slug = (kind or "").strip()
        if not tid or not slug:
            return ()  # no tenant / no kind to scope -> nothing (fail-closed, never global).
        n = _clamp_limit(limit)
        try:
            session = self._factory()
            self._adapter.bind_session_tenant(session, {"tenant": tid})
            sql = (
                "SELECT id, capability, kind, payload, created_at FROM "
                + _TENANT_DATA_TABLE
                + " WHERE tenant_id = %s AND kind = %s "
                "ORDER BY created_at DESC LIMIT %s"
            )
            params: List[Any] = [tid, slug, n]
            result = self._adapter.query(session, tid, sql, params)
        except TenantDataDenied:
            return ()
        except Exception:
            return ()
        rows = _project_rows(result)
        return tuple(_entity_payload(row) for row in rows)


class LocalOnlyKnowledgeReader:
    """Degrade-never no-op reader. Returned by make_tenant_knowledge_reader when NO session
    factory is configured (no central creds). Every read returns []/None and NEVER raises /
    NEVER touches a session -> the brain proceeds with no recalled knowledge, never blocked
    by a missing data plane. Satisfies the SAME shape as TenantKnowledgeReader so callers
    wire it identically (mirrors cex_runtime_sync.LocalOnlyWriter)."""

    def recent_knowledge(
        self,
        tenant_id: str,
        *,
        limit: int = _DEFAULT_LIMIT,
        capability: Optional[str] = None,
    ) -> List[TenantKnowledge]:
        return []

    def recent_products(
        self, tenant_id: str, *, limit: int = _MAX_LIMIT
    ) -> List[TenantKnowledge]:
        return []

    def find_product(self, tenant_id: str, ref: str) -> Optional[Dict[str, Any]]:
        return None

    def list_entity(
        self, tenant_id: str, kind: str, *, limit: int = _MAX_LIMIT
    ) -> Tuple[Dict[str, Any], ...]:
        return ()


def make_tenant_knowledge_reader(
    session_factory: Optional[Callable[[], DbSession]],
    *,
    adapter: Optional[SupabaseDataAdapter] = None,
):
    """Construct the brain-side knowledge reader, degrading to LOCAL-ONLY when no central
    data plane is configured (degrade-never -- mirrors make_runtime_sync_writer).

    session_factory None -> LocalOnlyKnowledgeReader (no creds / no pooled connection: the
    brain reads nothing, NEVER blocked). A real zero-arg factory -> TenantKnowledgeReader
    over the audited adapter. The glue owns adapter construction so callers never import the
    package directly (single seam = single import line)."""
    if session_factory is None:
        return LocalOnlyKnowledgeReader()
    return TenantKnowledgeReader(session_factory, adapter=adapter)


# --------------------------------------------------------------------------- #
# small helpers (PURE + TOTAL).                                                #
# --------------------------------------------------------------------------- #
def _project_rows(result: Any) -> List[TenantKnowledge]:
    """Project a driver-native query result into [TenantKnowledge]. TOTAL: a non-iterable /
    shape surprise -> [] (the offline fake's (sql, params) echo is treated as no rows)."""
    out: List[TenantKnowledge] = []
    for row in _iter_rows(result):
        item = _row_to_knowledge(row)
        if item is not None:
            out.append(item)
    return out


def _iter_rows(result: Any) -> List[Any]:
    """Yield the rows from a driver-native result (cursor.fetchall / a sequence of rows).
    TOTAL: the FakeDbSession (sql, params) 2-tuple echo (leading str) -> no rows."""
    if result is None:
        return []
    fetchall = getattr(result, "fetchall", None)
    if callable(fetchall):
        try:
            rows = fetchall()
        except Exception:
            return []
        return list(rows) if rows else []
    if isinstance(result, (list, tuple)):
        # Distinguish the audited fake's (sql, params) echo (a 2-tuple, leading str) from a
        # real list of rows: a real row is a sequence/mapping, never a leading-str 2-tuple.
        if len(result) == 2 and isinstance(result[0], str):
            return []
        return list(result)
    return [result]


# The SELECT column order (so a positional / tuple row is read by index, mirroring how
# entities.py + the apps read path consume rows). id, capability, kind, payload, created_at.
_COL_ID = 0
_COL_CAPABILITY = 1
_COL_KIND = 2
_COL_PAYLOAD = 3
_COL_CREATED_AT = 4


def _row_to_knowledge(row: Any) -> Optional[TenantKnowledge]:
    """Project ONE row (a mapping with named columns OR a positional sequence in the SELECT
    order) into TenantKnowledge, or None for an unusable row. PURE + TOTAL."""
    if isinstance(row, Mapping):
        rid = _str(row.get("id"))
        capability = _str(row.get("capability"))
        kind = _str(row.get("kind"))
        payload_raw = row.get("payload")
        created = _str(row.get("created_at"))
    elif isinstance(row, (list, tuple)):
        rid = _str(_at(row, _COL_ID))
        capability = _str(_at(row, _COL_CAPABILITY))
        kind = _str(_at(row, _COL_KIND))
        payload_raw = _at(row, _COL_PAYLOAD)
        created = _str(_at(row, _COL_CREATED_AT))
    else:
        return None
    if not rid:
        return None
    payload = _coerce_payload(payload_raw)
    artifact = _str(payload.get("artifact"))
    meta_raw = payload.get("meta")
    meta = dict(meta_raw) if isinstance(meta_raw, Mapping) else {}
    structured = meta.pop("structured", None)
    if not isinstance(structured, dict):
        structured = None
    return TenantKnowledge(
        record_id=rid,
        capability=capability,
        kind=kind,
        created_at=created,
        artifact=artifact,
        structured=structured,
        meta=meta,
        payload=payload,
    )


def _coerce_payload(payload: Any) -> Dict[str, Any]:
    """Coerce a jsonb payload (dict | JSON string/bytes | None) into a plain dict. TOTAL."""
    if isinstance(payload, Mapping):
        return dict(payload)
    if isinstance(payload, (bytes, bytearray)):
        try:
            payload = payload.decode("utf-8")
        except Exception:
            return {}
    if isinstance(payload, str) and payload.strip():
        try:
            loaded = json.loads(payload)
        except (ValueError, TypeError):
            return {}
        return loaded if isinstance(loaded, dict) else {}
    return {}


def _product_payload(row: TenantKnowledge) -> Dict[str, Any]:
    """Build the inputs['product_record'] dict from a managed-product row: the saved entity
    payload (row.payload -- a managed-entity row, EntityManager.create, stores its fields at
    payload TOP level) with the row id folded in for correlation. PURE + TOTAL."""
    payload = dict(row.payload) if isinstance(row.payload, Mapping) else {}
    payload.setdefault("id", row.record_id)
    payload.setdefault("record_id", row.record_id)
    return payload


def _entity_payload(row: TenantKnowledge) -> Dict[str, Any]:
    """Build a generic managed-entity row dict (the LEADS-injection projection): the saved
    entity payload (row.payload -- the managed-entity Data-tab CRUD stores its fields at the
    payload TOP level) with the row id folded in under 'id'/'record_id' for correlation.
    IDENTICAL shape to _product_payload, kind-agnostic. PASS-THROUGH: every saved field is
    kept verbatim (never fabricates a missing key). PURE + TOTAL."""
    payload = dict(row.payload) if isinstance(row.payload, Mapping) else {}
    payload.setdefault("id", row.record_id)
    payload.setdefault("record_id", row.record_id)
    return payload


def _payload_ref_matches(payload: Mapping[str, Any], want: str, want_low: str) -> bool:
    """True if the saved product payload's sku/slug matches ``want`` (case-insensitive on the
    value). PURE + TOTAL."""
    for k in _PRODUCT_SKU_KEYS:
        v = payload.get(k)
        if v is not None and str(v).strip() and str(v).strip() == want:
            return True
    for k in _PRODUCT_SLUG_KEYS:
        v = payload.get(k)
        if v is not None and str(v).strip().lower() == want_low:
            return True
    return False


def _at(seq: Any, idx: int) -> Any:
    """Safe positional access: seq[idx] or None."""
    try:
        return seq[idx]
    except (IndexError, KeyError, TypeError):
        return None


def _str(v: Any) -> str:
    """A stripped string for a scalar; None -> ''. TOTAL."""
    if v is None:
        return ""
    return str(v).strip()
