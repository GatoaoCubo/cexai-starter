# -*- coding: ascii -*-
"""Generic tenant-scoped entity CRUD over tenant_data (mission CEXAI_DASHBOARD_V2,
roadmap C5 / debt D5 -- the dashboard-v2 management primitive).

THE GAP THIS CLOSES: the dashboard-v2 frontend (apps/dashboard_web) drives a generic
DataManager that calls GET/POST/PATCH/DELETE on ``/entity/{slug}`` for ANY entity
(``listEntity`` / ``createEntity`` / ``updateEntity`` / ``deleteEntity`` in
apps/dashboard_web/lib/api.ts). No backend served those paths -> live-mode 404. This
module is the server-side half so fixtures-mode and live-mode AGREE on the wire shape
(EntityListResponse / EntityRecord in apps/dashboard_web/lib/types.ts).

THE STORAGE MODEL (reuse the migrated schema, do NOT add tables): an entity row lives
in ``tenant_data`` (supabase/migrations/20260616000002_tenant_data.sql) keyed by
``kind`` == the entity SLUG. The flat record values live in the ``payload`` jsonb; the
row ``id`` is the tenant_data PK. So an EntityRecord ``{id, ...values}`` projects to /
from ``{id, tenant_id, kind=slug, payload=values}``. RLS (single PERMISSIVE
tenant-match + WITH CHECK) is the authoritative boundary; this module never re-declares
it.

THE TENANT_ID BINDING (EXPLICIT -- never implicit; defence-in-depth on top of RLS):
tenant_id is ALWAYS an explicit argument, resolved upstream from the VERIFIED JWT claim
(apps/dashboard_api/auth.extract_tenant_id) -- NEVER from the client body/query/slug.
Every method REUSES the audited ``cexai.governance.data.SupabaseDataAdapter``: it binds
the verified claim onto a fresh session (set_config is_local=True -> pooled-conn safe),
then ``adapter.query`` / ``adapter.write`` under the SAME explicit tenant_id inside ONE
session/transaction (the exact pattern RuntimeSyncWriter uses for the run write-path).
The adapter mirrors the cross-tenant equality check, so a bound-vs-target mismatch
raises ``TenantDataDenied('cross_tenant')`` BEFORE the DB is touched.

DEGRADE-NEVER (mirrors the existing /results read path + RuntimeSyncWriter):
  * NO session factory configured (no central creds) -> a LOCAL-ONLY manager: reads
    return ``([], note)``; writes are no-ops that NEVER raise (the UI still renders, the
    write simply does not reach the central plane). The dashboard is never blocked by a
    missing data plane.
  * A cross-tenant or unbound write FAILS CLOSED (TenantDataDenied propagates) -- the
    API layer maps it to 403.

ALLOWED IMPORT DIRECTION: ``apps`` MAY import ``cexai`` (the adapter is REUSED). The
adapter never imports back (it is extraction-bound). The cexai import is deferred to
construction time + guarded so the app boots even while the package is mid-build (same
posture as deps.load_runtime / main._read_tenant_results).

ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, List, Mapping, Optional, Protocol, Sequence, Tuple

__all__ = [
    "EntityManager",
    "LocalOnlyEntityManager",
    "make_entity_manager",
    "TenantDataDenied",
    "EntityError",
    "EntityNotFound",
    "InvalidSlug",
    "TENANT_DATA_TABLE",
]

# The table entity rows live in (MUST match the migration table name:
# supabase/migrations/20260616000002_tenant_data.sql).
TENANT_DATA_TABLE = "tenant_data"

# A slug is the api path segment AND the tenant_data ``kind`` -- pin it to a strict
# allowlist so it can never carry SQL or a surprise table reference. Slugs come from the
# overlay/schema (config-driven), never free user text; this is belt-and-braces.
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")

# Keys that must NEVER land in a row payload (the management surface refuses to persist a
# secret even if a future caller slips one in -- mirrors cex_runtime_sync._safe_meta).
_BLOCKED_PAYLOAD_KEYS = frozenset(
    {"api_key", "credential", "secret", "token", "password"}
)

# Reserved record keys that are part of the row envelope, not the payload. ``id`` is the
# PK (server-assigned on create, path-supplied on update); ``tenant_id``/``kind`` are the
# envelope columns the client must never set (defence-in-depth on top of RLS).
_RESERVED_RECORD_KEYS = frozenset({"id", "tenant_id", "kind"})


class _DbSessionLike(Protocol):
    """Structural seam (mirrors the adapter's DbSession). A real impl wraps a pooled
    psycopg/asyncpg connection; offline tests pass a fake."""

    def execute(self, sql: str, params: Optional[Sequence[Any]] = ...) -> Any: ...

    def set_config(self, key: str, value: str, is_local: bool) -> None: ...


# --------------------------------------------------------------------------- #
# Deferred + guarded cexai import (allowed direction apps -> cexai).          #
# --------------------------------------------------------------------------- #
def _load_adapter_cls() -> Optional[type]:
    """Return ``SupabaseDataAdapter`` if importable, else None (degrade-never).

    Deferred to construction so the app boots even while the cexai package is mid-build
    (same posture as main._read_tenant_results). A missing package -> None -> the caller
    falls back to the LOCAL-ONLY manager, never an ImportError at request time."""
    try:
        from cexai.governance.data.adapter import SupabaseDataAdapter  # type: ignore

        return SupabaseDataAdapter
    except Exception:
        return None


def _load_denied_cls() -> type:
    """Return the real ``TenantDataDenied`` if importable, else a structural shim.

    The API error mapping keys off this type; importing the real one keeps a single
    behavioural contract with the adapter. The shim only exists so this module imports
    even with cexai absent (it is never raised on the degraded path -- the local-only
    manager never touches the adapter)."""
    try:
        from cexai.governance.data.errors import TenantDataDenied as _Real  # type: ignore

        return _Real
    except Exception:

        class _TenantDataDeniedShim(Exception):
            """Fallback when cexai is not importable (degraded env). Never raised on the
            local-only path."""

            reason = "cross_tenant"

        return _TenantDataDeniedShim


# Bound once at import (cheap, no side effects). ``TenantDataDenied`` is re-exported so
# main.py can ``except entities.TenantDataDenied`` regardless of cexai availability.
TenantDataDenied = _load_denied_cls()


# --------------------------------------------------------------------------- #
# Errors (app-local; distinct from the security deny TenantDataDenied).       #
# --------------------------------------------------------------------------- #
class EntityError(Exception):
    """Base for client/shape errors the entity layer raises (mapped to 4xx by the API).

    Carries ``reason`` (machine code) + ``detail`` (safe human string). NEVER a secret."""

    def __init__(self, reason: str, *, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        super().__init__("%s: %s" % (reason, detail) if detail else reason)


class InvalidSlug(EntityError):
    """The entity slug is malformed (not in the strict allowlist) -> 400."""


class EntityNotFound(EntityError):
    """An update/delete targeted a row id that does not exist for this tenant -> 404."""

    def __init__(self, entity: str, record_id: str) -> None:
        super().__init__(
            "not_found",
            detail="no '%s' record with id %s for this tenant" % (entity, record_id),
        )
        self.entity = entity
        self.record_id = record_id


# --------------------------------------------------------------------------- #
# Validation + projection helpers (pure).                                     #
# --------------------------------------------------------------------------- #
def _validate_slug(entity: str) -> str:
    """Return the slug if it matches the strict allowlist, else raise InvalidSlug.

    The slug is BOTH the api path segment and the tenant_data ``kind`` value; pinning it
    means a path can never smuggle SQL or reach a different table/kind."""
    slug = (entity or "").strip()
    if not _SLUG_RE.match(slug):
        raise InvalidSlug(
            "invalid_entity",
            detail="entity slug must match %s" % _SLUG_RE.pattern,
        )
    return slug


def _safe_payload(values: Mapping[str, Any]) -> Dict[str, Any]:
    """Project client-supplied values into a JSON-safe payload dict.

    Strips (a) the reserved envelope keys (``id``/``tenant_id``/``kind`` -- the client
    must never set the row envelope) and (b) any secret-shaped key (belt-and-braces:
    the management surface refuses to persist a credential). Non-JSON-able values are
    coerced to str so the jsonb write never fails on a driver surprise."""
    out: Dict[str, Any] = {}
    if not values:
        return out
    for k, v in dict(values).items():
        key = str(k)
        if key in _RESERVED_RECORD_KEYS:
            continue
        if key.lower() in _BLOCKED_PAYLOAD_KEYS:
            continue
        out[key] = _jsonable(v)
    return out


def _jsonable(value: Any) -> Any:
    """Best-effort scalar coercion for jsonb (datetimes/UUIDs/etc -> str)."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    return str(value)


def _row_to_record(row: Any) -> Optional[Dict[str, Any]]:
    """Project ONE tenant_data row -> an EntityRecord ``{id, ...payload}``.

    Accepts a mapping ({id, payload}) or a (id, payload) sequence (driver-native). The
    payload jsonb may arrive as a dict (psycopg jsonb adaption) or a JSON string; both
    are handled. Returns None for an unrecognized row shape (skipped by the caller)."""
    rid: Any = None
    payload: Any = None
    if isinstance(row, Mapping):
        rid = row.get("id")
        payload = row.get("payload")
    elif isinstance(row, (list, tuple)) and len(row) >= 2:
        rid, payload = row[0], row[1]
    else:
        return None
    if rid is None:
        return None
    record: Dict[str, Any] = {}
    parsed = _coerce_payload(payload)
    for k, v in parsed.items():
        if str(k) in _RESERVED_RECORD_KEYS:
            continue
        record[str(k)] = _jsonable(v)
    # ``id`` last so a stray payload ``id`` can never shadow the canonical PK.
    record["id"] = str(rid)
    return record


def _coerce_payload(payload: Any) -> Dict[str, Any]:
    """Coerce a jsonb payload (dict | JSON string | None) into a plain dict."""
    if isinstance(payload, Mapping):
        return dict(payload)
    if isinstance(payload, str) and payload.strip():
        try:
            loaded = json.loads(payload)
        except (ValueError, TypeError):
            return {}
        return loaded if isinstance(loaded, dict) else {}
    return {}


# Sentinel so a row that simply does not carry the column is left UNCHANGED (distinct
# from a row that carries published=NULL/None, which IS a present column -> published=False).
_ABSENT = object()


def _attach_publish_state(rec: Dict[str, Any], row: Any) -> None:
    """Attach the TOP-LEVEL ``published`` / ``published_at`` gate columns from ``row`` onto
    ``rec`` (in place) so the listed record can render the honest published/draft chip.

    The gate columns are tenant_data TOP-LEVEL columns (SPEC 10 W1), NOT payload jsonb --
    so they are surfaced HERE, never via ``_row_to_record`` (which stays payload-only and
    must NEVER leak the gate into the payload). Reads the SAME two driver shapes the rest of
    this module tolerates:
      * a Mapping -> ``row.get("published")`` / ``row.get("published_at")``;
      * a sequence/tuple from the 4-col SELECT -> ``row[2]`` / ``row[3]`` (when len >= 4).
    When a column is PRESENT, sets ``rec["published"] = bool(value)`` and
    ``rec["published_at"] = str(value) or None``. A row that does NOT carry the columns -- a
    2-col legacy row, or the offline (sql, params) echo -- leaves ``rec`` UNCHANGED.
    DEGRADE-NEVER + TOTAL: never raises on a shape surprise (mirrors _row_to_record /
    _published_at_from_result)."""
    published = _ABSENT
    published_at = _ABSENT
    if isinstance(row, Mapping):
        if "published" in row:
            published = row.get("published")
        if "published_at" in row:
            published_at = row.get("published_at")
    elif isinstance(row, (list, tuple)) and len(row) >= 4:
        published = row[2]
        published_at = row[3]
    if published is not _ABSENT:
        rec["published"] = bool(published)
    if published_at is not _ABSENT:
        rec["published_at"] = str(published_at) if published_at is not None else None


# --------------------------------------------------------------------------- #
# The concrete tenant-scoped entity manager.                                  #
# --------------------------------------------------------------------------- #
class EntityManager:
    """Tenant-scoped CRUD over tenant_data, REUSING the audited SupabaseDataAdapter.

    Construct via ``make_entity_manager`` (which returns a LocalOnlyEntityManager when no
    session factory is configured -- degrade-never). The ``session_factory`` is a zero-arg
    callable returning a DbSession (production: a pooled tenant connection; tests: a fake).
    Every method takes tenant_id EXPLICITLY (the VERIFIED claim) and binds it onto a fresh
    session before the query/write -- the bind + the call share ONE transaction (spec A.5
    pooled-conn safety, mirrored from the dashboard read path)."""

    def __init__(
        self,
        session_factory: Any,
        *,
        adapter: Optional[Any] = None,
        adapter_cls: Optional[type] = None,
    ) -> None:
        self._factory = session_factory
        if adapter is not None:
            self._adapter = adapter
        else:
            cls = adapter_cls if adapter_cls is not None else _load_adapter_cls()
            if cls is None:  # pragma: no cover - guarded by make_entity_manager
                raise RuntimeError("SupabaseDataAdapter unavailable")
            self._adapter = cls(session_factory)

    # -- read --------------------------------------------------------------- #
    def list(
        self, tenant_id: str, entity: str, *, limit: int = 200
    ) -> Tuple[List[Dict[str, Any]], str]:
        """List the tenant's rows for ``entity`` -> (records, note).

        Reads tenant_data WHERE tenant_id = <claim> AND kind = <slug> via ``adapter.query``
        (tenant-scoped + cross-tenant-mirrored). Returns plain EntityRecord dicts. The note
        is '' on success (kept in the tuple so the local-only manager can explain a
        degraded read with the SAME signature)."""
        slug = _validate_slug(entity)
        session = self._factory()
        self._bind(session, tenant_id)
        # SELECT the gate columns (published/published_at) ALONGSIDE id/payload so the listed
        # record can render the HONEST published/draft chip at rest (the DataManager reads
        # record.published). _row_to_record stays payload-only {id, ...payload}; the top-level
        # gate columns are ATTACHED separately by _attach_publish_state (they never enter the
        # payload jsonb). ORDER/LIMIT unchanged.
        sql = (
            "SELECT id, payload, published, published_at FROM " + TENANT_DATA_TABLE + " "
            "WHERE tenant_id = %s AND kind = %s "
            "ORDER BY created_at DESC LIMIT %s"
        )
        params: List[Any] = [tenant_id, slug, int(limit)]
        raw = self._adapter.query(session, tenant_id, sql, params)
        records: List[Dict[str, Any]] = []
        for row in _iter_rows(raw):
            rec = _row_to_record(row)
            if rec is not None:
                _attach_publish_state(rec, row)
                records.append(rec)
        return records, ""

    # -- create ------------------------------------------------------------- #
    def create(
        self, tenant_id: str, entity: str, values: Mapping[str, Any]
    ) -> Dict[str, Any]:
        """Create one row for ``entity`` and return the new EntityRecord.

        INSERTs (tenant_id, kind=slug, payload) via ``adapter.write`` (the WITH CHECK
        shape: tenant_id == the bound claim). The new id is the server-default
        gen_random_uuid(); if the driver does not surface it via RETURNING, a client-side
        uuid4 mirrors what the row will read back as (the payload is authoritative either
        way). tenant_id/kind/id are NEVER taken from ``values``."""
        slug = _validate_slug(entity)
        payload = _safe_payload(values)
        session = self._factory()
        self._bind(session, tenant_id)
        sql = (
            "INSERT INTO " + TENANT_DATA_TABLE + " (tenant_id, kind, payload) "
            "VALUES (%s, %s, %s::jsonb) RETURNING id"
        )
        params: List[Any] = [tenant_id, slug, json.dumps(payload, ensure_ascii=True)]
        result = self._adapter.write(session, tenant_id, sql, params)
        new_id = _first_id(result) or str(uuid.uuid4())
        record = dict(payload)
        record["id"] = str(new_id)
        return record

    # -- update ------------------------------------------------------------- #
    def update(
        self,
        tenant_id: str,
        entity: str,
        record_id: str,
        values: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Update one row (merge ``values`` into its payload) and return the EntityRecord.

        Reads the current payload (tenant-scoped) first; raises EntityNotFound if the id
        does not exist for this tenant. Then UPDATEs the merged payload via ``adapter.write``
        WHERE id = <id> AND tenant_id = <claim> AND kind = <slug> (RLS + the explicit
        predicates both scope it). Returns the merged EntityRecord."""
        slug = _validate_slug(entity)
        rid = (record_id or "").strip()
        if not rid:
            raise EntityNotFound(slug, record_id)
        current = self._read_one_payload(tenant_id, slug, rid)
        if current is None:
            raise EntityNotFound(slug, rid)
        merged = dict(current)
        merged.update(_safe_payload(values))
        session = self._factory()
        self._bind(session, tenant_id)
        sql = (
            "UPDATE " + TENANT_DATA_TABLE + " SET payload = %s::jsonb "
            "WHERE id = %s AND tenant_id = %s AND kind = %s"
        )
        params: List[Any] = [
            json.dumps(merged, ensure_ascii=True),
            rid,
            tenant_id,
            slug,
        ]
        self._adapter.write(session, tenant_id, sql, params)
        record = dict(merged)
        record["id"] = str(rid)
        return record

    # -- publish gate (SPEC 10 W1 -- the L2 publish seam) ------------------- #
    def set_published(
        self, tenant_id: str, entity: str, record_id: str, published: bool
    ) -> Dict[str, Any]:
        """Flip the PUBLISHED gate on one tenant_data row the tenant OWNS, return its record.

        THE PUBLISH SEAM (spec 10 W1; supabase/migrations/20260625000001_public_catalog.sql):
        ``published``/``published_at`` are TOP-LEVEL COLUMNS on tenant_data (NOT payload jsonb),
        so flipping them is a COLUMN update -- NOT a payload merge (the entity ``update`` path).
        Setting ``published=true`` is what makes the row eligible for the L2 anon public read
        (RLS ``public_catalog_read USING (published = true)``); ``published=false`` retracts it.

        TENANT-BIND (the deny-before-DB keystone -- identical seam to ``update``/``delete``):
        the SAME audited adapter binds the VERIFIED claim onto a fresh session
        (``adapter.bind_session_tenant`` -> set_config is_local=True, pooled-conn safe), then
        ``adapter.write`` issues the UPDATE under the EXPLICIT tenant_id. The adapter's
        ``_guard_call`` cross-tenant mirror runs FIRST: a bound-vs-target mismatch raises
        ``TenantDataDenied('cross_tenant')`` BEFORE ``session.execute`` -- so this can NEVER
        flip another tenant's row, AND the SQL itself carries ``WHERE id=%s AND tenant_id=%s``
        (RLS + the explicit predicate are belt-and-braces on top of the framework mirror).

        published_at policy (server clock, documented): on PUBLISH, ``published_at = now()``
        (the server clock -- never a client value); on UNPUBLISH, ``published=false`` and
        ``published_at`` is set to NULL (a retracted row has no public-since time -- so a later
        re-publish stamps a fresh now(), and the public catalog never shows a stale timestamp).

        A row id that does not exist for THIS tenant -> EntityNotFound (404): the read-back is
        tenant-scoped, so a foreign/unknown id is indistinguishable from absent (no disclosure).
        Returns the record ``{id, ...payload, published, published_at}`` (the gate columns are
        surfaced so the UI can render the honest published/draft state)."""
        slug = _validate_slug(entity)
        rid = (record_id or "").strip()
        if not rid:
            raise EntityNotFound(slug, record_id)
        # Read the current payload FIRST (tenant-scoped) so a foreign/unknown id is a clean 404
        # (never a 0-row UPDATE silently reported as success) AND the returned record carries the
        # row's values. The read goes through the SAME bind+guard seam as every other method.
        current = self._read_one_payload(tenant_id, slug, rid)
        if current is None:
            raise EntityNotFound(slug, rid)
        want = bool(published)
        session = self._factory()
        self._bind(session, tenant_id)
        # published_at: now() on publish; NULL on unpublish (documented above). The literal is a
        # FIXED SQL token (NOT caller-controlled) so there is no injection surface; ``published``
        # is a bound parameter.
        published_at_sql = "now()" if want else "NULL"
        sql = (
            "UPDATE " + TENANT_DATA_TABLE + " "
            "SET published = %s, published_at = " + published_at_sql + " "
            "WHERE id = %s AND tenant_id = %s AND kind = %s "
            "RETURNING id, published, published_at"
        )
        params: List[Any] = [want, rid, tenant_id, slug]
        result = self._adapter.write(session, tenant_id, sql, params)
        published_at = _published_at_from_result(result, published=want)
        record = dict(current)
        record["id"] = str(rid)
        record["published"] = want
        record["published_at"] = published_at
        return record

    # -- delete ------------------------------------------------------------- #
    def delete(self, tenant_id: str, entity: str, record_id: str) -> None:
        """Delete one row WHERE id AND tenant_id AND kind (tenant-scoped + RLS).

        Idempotent: a missing id is a no-op (DELETE of 0 rows), so a double-delete from the
        UI never errors. The cross-tenant mirror still fires on the bound-vs-target check
        before the DB is touched, so a cross-tenant delete is denied (it can never reach
        another tenant's row anyway -- RLS + the tenant_id predicate)."""
        slug = _validate_slug(entity)
        rid = (record_id or "").strip()
        if not rid:
            return
        session = self._factory()
        self._bind(session, tenant_id)
        sql = (
            "DELETE FROM " + TENANT_DATA_TABLE + " "
            "WHERE id = %s AND tenant_id = %s AND kind = %s"
        )
        params: List[Any] = [rid, tenant_id, slug]
        self._adapter.write(session, tenant_id, sql, params)

    # -- internal ----------------------------------------------------------- #
    def _read_one_payload(
        self, tenant_id: str, slug: str, record_id: str
    ) -> Optional[Dict[str, Any]]:
        """Read ONE row's payload (tenant-scoped) for the update merge, or None if absent."""
        session = self._factory()
        self._bind(session, tenant_id)
        sql = (
            "SELECT id, payload FROM " + TENANT_DATA_TABLE + " "
            "WHERE id = %s AND tenant_id = %s AND kind = %s LIMIT 1"
        )
        params: List[Any] = [record_id, tenant_id, slug]
        raw = self._adapter.query(session, tenant_id, sql, params)
        for row in _iter_rows(raw):
            rec = _row_to_record(row)
            if rec is not None:
                rec.pop("id", None)
                return rec
        return None

    def _bind(self, session: Any, tenant_id: str) -> None:
        """Bind the verified-claim tenant onto the session so RLS applies on a pooled
        connection (spec A.5). REUSES adapter.bind_session_tenant (set_config
        is_local=True). The bound claim == the explicit tenant_id every call asserts, so
        the adapter's cross-tenant mirror passes for the legitimate tenant and denies a
        crossing one."""
        self._adapter.bind_session_tenant(session, {"tenant": tenant_id})


class LocalOnlyEntityManager:
    """Degrade-never no-op manager. Returned by ``make_entity_manager`` when NO session
    factory is configured (no central creds).

    Reads return ``([], note)`` (an empty, tenant-scoped list -- never another tenant's
    data). Writes are no-ops that NEVER raise / NEVER touch a session: create echoes the
    submitted values with a synthetic id so the UI's optimistic render still works; update
    echoes the merge; delete is a silent no-op. The central simply never receives a write
    -- the dashboard is never blocked by a missing data plane (mirrors LocalOnlyWriter)."""

    _NOTE = "tenant data plane not configured in this environment"

    def list(
        self, tenant_id: str, entity: str, *, limit: int = 200
    ) -> Tuple[List[Dict[str, Any]], str]:
        _validate_slug(entity)  # still reject a malformed slug (4xx, not a silent pass)
        return [], self._NOTE

    def create(
        self, tenant_id: str, entity: str, values: Mapping[str, Any]
    ) -> Dict[str, Any]:
        _validate_slug(entity)
        record = _safe_payload(values)
        record["id"] = "local-%s" % uuid.uuid4()
        return record

    def update(
        self,
        tenant_id: str,
        entity: str,
        record_id: str,
        values: Mapping[str, Any],
    ) -> Dict[str, Any]:
        _validate_slug(entity)
        record = _safe_payload(values)
        record["id"] = str((record_id or "").strip() or "local-%s" % uuid.uuid4())
        return record

    def set_published(
        self, tenant_id: str, entity: str, record_id: str, published: bool
    ) -> Dict[str, Any]:
        """Degrade-never publish flip (no central data plane). Mirrors ``update``'s local-only
        echo: validate the slug (still a 4xx on a malformed one), then echo a record carrying the
        requested ``published`` + a synthetic ``published_at`` (now() on publish, None on
        unpublish) so the UI's optimistic toggle still flips. NEVER raises, NEVER touches a
        session -- the publish ACTION simply never reaches the central plane (the founder's gated
        prod path is where a real publish lands). A blank id still 404s (no row to echo)."""
        slug = _validate_slug(entity)
        rid = (record_id or "").strip()
        if not rid:
            raise EntityNotFound(slug, record_id)
        want = bool(published)
        record: Dict[str, Any] = {
            "id": rid,
            "published": want,
            "published_at": _utcnow_iso() if want else None,
        }
        return record

    def delete(self, tenant_id: str, entity: str, record_id: str) -> None:
        _validate_slug(entity)
        return None


def make_entity_manager(
    session_factory: Optional[Any],
    *,
    adapter: Optional[Any] = None,
    adapter_cls: Optional[type] = None,
) -> Any:
    """Construct the entity manager, degrading to LOCAL-ONLY when no central data plane is
    configured (degrade-never).

    ``session_factory`` None -> LocalOnlyEntityManager (no creds: reads empty, writes
    no-op, NEVER blocked). A real zero-arg factory -> EntityManager over the audited
    adapter. If cexai is not importable at all (the adapter class is None and no
    adapter/adapter_cls was injected), also fall back to LOCAL-ONLY rather than raise --
    the app stays up even while the package is mid-build."""
    if session_factory is None:
        return LocalOnlyEntityManager()
    if adapter is None and adapter_cls is None and _load_adapter_cls() is None:
        return LocalOnlyEntityManager()
    return EntityManager(session_factory, adapter=adapter, adapter_cls=adapter_cls)


# --------------------------------------------------------------------------- #
# Row-shape helpers (mirror cex_runtime_sync._first_id / liberal driver shapes).
# --------------------------------------------------------------------------- #
def _iter_rows(raw: Any) -> List[Any]:
    """Normalize a driver-native query result into a list of rows.

    Liberal on shape (psycopg cursor / list of rows / a single row): accepts a cursor with
    fetchall(), a list/tuple of rows, or a single mapping/sequence. The FakeDbSession used
    by the offline tests returns the forwarded (sql, params) tuple -- a 2-tuple whose first
    element is a str -- which is NOT a data row; ``_iter_rows`` yields nothing for it (the
    real rows come from a RowReturningSession-style fake or a live driver)."""
    if raw is None:
        return []
    fetchall = getattr(raw, "fetchall", None)
    if callable(fetchall):
        try:
            rows = fetchall()
        except Exception:
            return []
        return list(rows) if rows is not None else []
    if isinstance(raw, (list, tuple)):
        if len(raw) == 2 and isinstance(raw[0], str):
            # The (sql, params) echo of the offline fake -> no data rows.
            return []
        return list(raw)
    if isinstance(raw, Mapping):
        return [raw]
    return []


def _first_id(result: Any) -> Optional[str]:
    """Best-effort extraction of a RETURNING id from a driver-native result.

    Mirrors cex_runtime_sync._first_id: accepts a cursor with fetchone(), a list/tuple of
    rows, a single row, or a mapping with 'id'. The offline fake's (sql, params) 2-tuple
    yields None (treated as 'not surfaced' -> the caller mints a client-side uuid4)."""
    if result is None:
        return None
    fetchone = getattr(result, "fetchone", None)
    if callable(fetchone):
        try:
            row = fetchone()
        except Exception:
            row = None
        return _id_from_row(row)
    if isinstance(result, (list, tuple)):
        if not result:
            return None
        if len(result) == 2 and isinstance(result[0], str):
            return None
        return _id_from_row(result[0])
    return _id_from_row(result)


def _id_from_row(row: Any) -> Optional[str]:
    """Pull an id out of one row (mapping with 'id', or a sequence's first element)."""
    if row is None:
        return None
    if isinstance(row, Mapping):
        val = row.get("id")
        return None if val is None else str(val)
    if isinstance(row, (list, tuple)):
        if not row:
            return None
        if isinstance(row[0], str) and len(row) == 2:
            return None
        return str(row[0])
    return str(row)


def _utcnow_iso() -> str:
    """A UTC ISO-8601 'now' for the LOCAL-ONLY publish echo ONLY (no central plane).

    The LIVE path stamps ``published_at = now()`` on the DB SERVER CLOCK (never this value);
    this is solely so the degrade-never echo carries a plausible timestamp for an optimistic UI
    flip. Timezone-aware UTC so it is unambiguous."""
    import datetime as _dt

    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _published_at_from_result(result: Any, *, published: bool) -> Optional[str]:
    """Best-effort extraction of the ``published_at`` the DB stamped from a RETURNING result.

    The publish UPDATE is ``RETURNING id, published, published_at``; the driver may surface that
    as a cursor / list of rows / a single (id, published, published_at) tuple or a mapping. We
    pull the THIRD column (or the ``published_at`` key) and stringify a datetime so the JSON
    response carries the server-clock timestamp. DEGRADE-NEVER + TOTAL: an offline fake that
    echoes (sql, params) -- or any shape that does not surface the column -- yields a fallback
    (``_utcnow_iso()`` on publish, None on unpublish) so the record is still well-formed. The
    fallback is NEVER the authoritative time (the DB value is); it only keeps the echo coherent
    when the driver did not return the row (e.g. the offline test fake)."""
    row = _first_row(result)
    value: Any = None
    if isinstance(row, Mapping):
        value = row.get("published_at")
    elif isinstance(row, (list, tuple)) and len(row) >= 3:
        value = row[2]
    if value is None:
        # No surfaced value: on unpublish the column IS NULL (faithful); on publish, fall back
        # to a server-side 'now' so an offline/echo path still returns a coherent timestamp.
        return _utcnow_iso() if published else None
    return str(value)


def _first_row(result: Any) -> Any:
    """Extract the FIRST row from a driver-native result (cursor.fetchone / a sequence / a single
    row), or None. Mirrors cex_runtime_sync._first_row: the offline fake's (sql, params) echo (a
    2-tuple with a str head) is treated as 'no row'. TOTAL -- never raises on a shape surprise."""
    if result is None:
        return None
    fetchone = getattr(result, "fetchone", None)
    if callable(fetchone):
        try:
            return fetchone()
        except Exception:
            return None
    if isinstance(result, (list, tuple)):
        if not result:
            return None
        if len(result) == 2 and isinstance(result[0], str):
            return None  # the FakeDbSession.execute (sql, params) echo -> no row surfaced
        return result[0]
    if isinstance(result, Mapping):
        return result
    return result
