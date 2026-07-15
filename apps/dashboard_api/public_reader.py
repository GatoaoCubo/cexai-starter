# -*- coding: ascii -*-
"""Unauthenticated PUBLIC read seam for the L2 public site (spec 10 W1-backend).

THE SECURITY POSTURE (this is the keystone): the public site is browsed with NO JWT.
So every read here MUST be STRUCTURALLY incapable of returning an unpublished, private,
or cross-tenant row. This module is the data half of that guarantee -- it is DELIBERATELY
SEPARATE from the tenant-scoped path (apps/dashboard_api/entities.py + the audited
SupabaseDataAdapter), which binds a verified tenant CLAIM. The public path has no claim;
it resolves a tenant by SLUG and reads published-only rows as the low-privilege `anon`
role. The two paths never share a connection or a code path.

DEFENCE-IN-DEPTH (all three layers, none sufficient alone -- the no-leak triple-guard):
  (1) RLS at the DB: the public reader connects as the `anon` Postgres role
      (SET LOCAL ROLE anon, mirrored from the proof harness's SET LOCAL ROLE
      authenticated). The migration's public_catalog_read policy (TO anon,
      USING published = true) then constrains anon SELECTs to published rows ONLY.
      anon NEVER bypasses RLS -- only the table owner / service_role do, and this path
      uses NEITHER (using service_role here would BYPASS RLS and defeat layer 1).
  (2) Backend filter: catalog SQL ALSO carries `published = true AND kind = $kind` --
      belt-and-braces on top of RLS.
  (3) slug->tenant_id gating: the public API takes a SLUG, never a raw tenant_id. The
      slug resolves to a tenant_id ONLY via tenant_slugs WHERE public_read = true; a
      private/absent slug returns nothing (the endpoint 404s WITHOUT disclosing the
      tenant exists).

THE anon SESSION CONTRACT (the factory this module needs):
    public_factory() -> Callable[[], DbSession]   # a ZERO-ARG factory minting ONE
                                                  # fresh DbSession per logical op
where the DbSession is the SAME structural seam the audited adapter uses:
    execute(sql, params) -> driver-native rows
    set_config(key, value, is_local) -> None      # is_local=True (pooled-conn safety)
plus, for the LIVE driver, a `SET LOCAL ROLE anon` issued INSIDE the op's transaction so
the public_catalog_read policy governs (the reference live driver does this; an offline
fake just records it). The reader calls `_bind_anon(session)` which issues the role
switch via set_config-style execute, then runs the published-filtered SELECT.

DEGRADE-NEVER: no public factory configured (no central creds) -> a LocalOnly reader:
slug resolve -> None (404), catalog -> [] (empty). The public site then renders an
empty/branded shell rather than 500-ing. NEVER raises on a missing data plane; a hostile
slug is rejected (returns None / [], never SQL).

ALLOWED IMPORT DIRECTION: apps may import cexai, but this module intentionally does NOT
use SupabaseDataAdapter (that is claim-bound; the public path has no claim). It is a
small, self-contained anon reader. ASCII-only per .claude/rules/ascii-code-rule.md.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Mapping, Optional, Protocol, Sequence, Tuple

__all__ = [
    "PublicReader",
    "LocalOnlyPublicReader",
    "make_public_reader",
    "TENANT_DATA_TABLE",
    "TENANT_SLUGS_TABLE",
    "ANON_ROLE",
    "is_valid_slug",
    "is_valid_kind",
]

# The tables the public path reads (MUST match the migrations:
# 20260616000002_tenant_data.sql + 20260625000001_public_catalog.sql).
TENANT_DATA_TABLE = "tenant_data"
TENANT_SLUGS_TABLE = "tenant_slugs"

# The low-privilege Postgres role the public path runs as. It is SUBJECT to RLS, so the
# public_catalog_read / public_slug_read policies (TO anon) constrain every SELECT. This
# is a FIXED literal (never caller input) -> no injection surface; SET LOCAL ROLE cannot
# take a bound parameter, so it is inlined as a constant statement (same as the proof
# harness's `SET LOCAL ROLE authenticated`).
ANON_ROLE = "anon"
_SET_ROLE_SQL = "SET LOCAL ROLE anon"

# A slug is the public URL segment AND a tenant_slugs lookup key -- pin it to a strict
# allowlist so a path can never carry SQL or a surprise. Mirrors the tenant_id slug shape
# the rest of the system uses (cex_bootstrap._safe_tenant_id: [a-z0-9][a-z0-9_-]{0,63}).
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")

# A kind is the tenant_data.kind value the catalog filters on -- same strict allowlist as
# the entity slug (entities.py) so it can never smuggle SQL or reach a surprise kind.
_KIND_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")

# The default upper bound on a catalog page (defence against an accidental large scan).
_DEFAULT_LIMIT = 50
_MAX_LIMIT = 200


class _DbSessionLike(Protocol):
    """Structural seam (mirrors the adapter's DbSession). A real impl wraps a pooled
    psycopg connection running as anon; offline tests pass a fake."""

    def execute(self, sql: str, params: Optional[Sequence[Any]] = ...) -> Any: ...

    def set_config(self, key: str, value: str, is_local: bool) -> None: ...


# --------------------------------------------------------------------------- #
# Validation helpers (pure; fail-closed -- a bad slug/kind never reaches SQL).  #
# --------------------------------------------------------------------------- #
def is_valid_slug(slug: Any) -> bool:
    """True iff ``slug`` is a well-formed public slug. A malformed slug never reaches the
    DB -- the caller treats False as 'no such public tenant' (404)."""
    return isinstance(slug, str) and bool(_SLUG_RE.match(slug.strip()))


def is_valid_kind(kind: Any) -> bool:
    """True iff ``kind`` is a well-formed tenant_data kind. A malformed kind never reaches
    the DB -- the caller treats False as 'no such catalog' (empty)."""
    return isinstance(kind, str) and bool(_KIND_RE.match(kind.strip()))


def _jsonable(value: Any) -> Any:
    """Best-effort scalar coercion for JSON (datetimes/UUIDs -> str)."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


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


def _clamp_limit(limit: Any) -> int:
    """Clamp a client limit into [1, _MAX_LIMIT] (a bad value -> the default)."""
    try:
        n = int(limit)
    except (TypeError, ValueError):
        return _DEFAULT_LIMIT
    if n < 1:
        return 1
    if n > _MAX_LIMIT:
        return _MAX_LIMIT
    return n


def _clamp_offset(offset: Any) -> int:
    """Clamp a client offset into [0, inf) (a bad/negative value -> 0)."""
    try:
        n = int(offset)
    except (TypeError, ValueError):
        return 0
    return n if n >= 0 else 0


# --------------------------------------------------------------------------- #
# The concrete anon-role public reader.                                        #
# --------------------------------------------------------------------------- #
class PublicReader:
    """Unauthenticated, anon-role, published-only reader (spec 10 W1-backend).

    Construct via ``make_public_reader`` (which returns a LocalOnlyPublicReader when no
    public session factory is configured -- degrade-never). ``session_factory`` is a
    zero-arg callable returning a DbSession running as (or switchable to) the anon role.

    Every method:
      * switches the session to the anon role (``_bind_anon``) INSIDE the op's
        transaction so the public_* RLS policies govern (defence layer 1);
      * filters published = true (+ the exact kind for catalog) in SQL (layer 2);
      * resolves a tenant only via tenant_slugs.public_read = true (layer 3).
    It NEVER accepts a raw tenant_id from the caller and NEVER uses service_role."""

    def __init__(self, session_factory: Any) -> None:
        self._factory = session_factory

    # -- the anon-role bind (defence layer 1) ------------------------------- #
    def _bind_anon(self, session: Any) -> None:
        """Switch the session's transaction to the `anon` role so the public_* RLS
        policies (TO anon) apply. Mirrors the proof harness + pg_session_factory's
        `SET LOCAL ROLE authenticated`, but to `anon` -- the public, RLS-subject role.

        The live driver issues `SET LOCAL ROLE anon` on the open transaction (so it is
        tx-scoped and never leaks to the next pooled borrower). We route it through
        ``set_config`` when the session exposes it (the live PgSession-style driver does
        the role switch itself right after a set_config bind) and ALSO issue an explicit
        role statement via execute so a plain DbSession fake records the anon posture.
        The role literal is FIXED (never caller input) -> no injection surface."""
        # Mark the request claim as anon-empty (no tenant claim on the public path) so a
        # live driver that keys its role switch off a bind still flips to anon. is_local
        # =True keeps it transaction-scoped (pooled-conn safety). Best-effort: a session
        # without set_config (a minimal fake) just skips this and relies on the execute
        # role statement below.
        set_config = getattr(session, "set_config", None)
        if callable(set_config):
            try:
                set_config("request.jwt.claims", json.dumps({"role": ANON_ROLE}), True)
            except Exception:
                # Degrade-never: a set_config hiccup must not crash the public read; the
                # explicit role statement below is the authoritative posture switch.
                pass
        # The explicit, FIXED role switch (the load-bearing line). SET LOCAL ROLE cannot
        # take a bound parameter; 'anon' is a constant, never caller input -> safe inline.
        session.execute(_SET_ROLE_SQL, None)

    # -- slug -> tenant_id (defence layer 3) -------------------------------- #
    def resolve_public_tenant(self, slug: str) -> Optional[Dict[str, Any]]:
        """Resolve a PUBLIC slug to ``{tenant_id, slug}`` via tenant_slugs WHERE
        public_read = true, or None.

        Returns None for: a malformed slug (never reaches SQL), an unknown slug, or a
        slug whose tenant has NOT opted in (public_read = false). In every None case the
        endpoint 404s WITHOUT disclosing whether the tenant exists (no-leak). The anon
        role + the public_slug_read RLS policy (USING public_read = true) is the DB-side
        guard; the explicit `AND public_read = true` predicate is belt-and-braces."""
        s = (slug or "").strip()
        if not is_valid_slug(s):
            return None
        session = self._factory()
        self._bind_anon(session)
        sql = (
            "SELECT tenant_id, slug FROM " + TENANT_SLUGS_TABLE + " "
            "WHERE slug = %s AND public_read = true LIMIT 1"
        )
        raw = session.execute(sql, [s])
        row = _first_row(raw)
        if row is None:
            return None
        tenant_id, resolved_slug = _two_cols(row)
        tid = _jsonable(tenant_id)
        if not tid or not str(tid).strip():
            return None
        return {"tenant_id": str(tid), "slug": str(_jsonable(resolved_slug) or s)}

    # -- published catalog read (layers 1 + 2 + 3) -------------------------- #
    def read_public_catalog(
        self,
        slug: str,
        kind: str,
        *,
        limit: int = _DEFAULT_LIMIT,
        offset: int = 0,
        with_html: bool = True,
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Read PUBLISHED rows of ``kind`` for the tenant behind ``slug`` -> (tenant_id,
        items). The triple-guard in one call:

          (3) resolve_public_tenant(slug) -- a non-public/unknown slug -> (None, []) so
              the endpoint 404s without disclosing the tenant;
          (1) the read runs as the anon role so public_catalog_read (USING published =
              true) constrains it;
          (2) the SQL ALSO carries `published = true AND kind = %s` (belt) so a private
              kind that is not published is NEVER returned.

        Each item is ``{id, kind, published_at, ...payload}`` (+ optional human_html when
        with_html and the payload carries one). A malformed kind -> (tenant_id, []) (no
        such catalog). DEGRADE-NEVER + no-leak: NEVER returns a row without published =
        true; NEVER another tenant's rows (the tenant_id is the slug-resolved one)."""
        resolved = self.resolve_public_tenant(slug)
        if resolved is None:
            return None, []  # layer 3: non-public/unknown slug -> 404 upstream
        tenant_id = resolved["tenant_id"]
        if not is_valid_kind(kind):
            return tenant_id, []  # a malformed kind reaches no SQL (no such catalog)
        k = kind.strip()
        lim = _clamp_limit(limit)
        off = _clamp_offset(offset)

        session = self._factory()
        self._bind_anon(session)
        # Layer 2: the explicit published + kind predicates (on TOP of the anon RLS
        # policy). The tenant_id is the SLUG-RESOLVED one (never a client value) -> a
        # public read can only ever see THIS tenant's published rows of THIS kind.
        sql = (
            "SELECT id, kind, payload, published_at FROM " + TENANT_DATA_TABLE + " "
            "WHERE tenant_id = %s AND kind = %s AND published = true "
            "ORDER BY published_at DESC NULLS LAST LIMIT %s OFFSET %s"
        )
        params: List[Any] = [tenant_id, k, lim, off]
        raw = session.execute(sql, params)
        items = [self._row_to_item(row, with_html=with_html) for row in _iter_rows(raw)]
        return tenant_id, [it for it in items if it is not None]

    def _row_to_item(
        self, row: Any, *, with_html: bool
    ) -> Optional[Dict[str, Any]]:
        """Project ONE published tenant_data row -> a public catalog item
        ``{id, kind, published_at, ...payload}`` (+ human_html when present and asked).

        Accepts a mapping or a (id, kind, payload, published_at) sequence (driver-native).
        Reserved envelope keys (tenant_id) are never surfaced; the payload supplies the
        public fields. Returns None for an unrecognized row (skipped). NOTE (media-URL
        caveat): a payload media field is whatever the tenant stored (e.g. an external
        image URL or a base64 data: URI); this projection forwards it verbatim and does
        NOT fetch/inline/validate it -- the public site renders it as-is."""
        rid: Any = None
        rkind: Any = None
        payload: Any = None
        published_at: Any = None
        if isinstance(row, Mapping):
            rid = row.get("id")
            rkind = row.get("kind")
            payload = row.get("payload")
            published_at = row.get("published_at")
        elif isinstance(row, (list, tuple)) and len(row) >= 4:
            rid, rkind, payload, published_at = row[0], row[1], row[2], row[3]
        else:
            return None
        if rid is None:
            return None
        item: Dict[str, Any] = {}
        parsed = _coerce_payload(payload)
        for key, val in parsed.items():
            sk = str(key)
            if sk in ("tenant_id", "id", "kind", "published", "published_at"):
                continue  # envelope keys are surfaced explicitly, not from payload
            if sk == "human_html" and not with_html:
                continue  # caller asked to omit the (potentially large) human face
            item[sk] = _jsonable(val)
        item["id"] = str(rid)
        item["kind"] = str(_jsonable(rkind) or "")
        item["published_at"] = _jsonable(published_at)
        return item


class LocalOnlyPublicReader:
    """Degrade-never no-op public reader. Returned by ``make_public_reader`` when NO
    public session factory is configured (no central creds).

    resolve_public_tenant -> None (the endpoint 404s); read_public_catalog -> (None, [])
    (the public site renders an empty/branded shell). NEVER raises, NEVER touches a
    session, NEVER discloses a tenant. A malformed slug/kind is still rejected the same
    way (None / []), so behaviour matches the live reader on the safety contract."""

    def resolve_public_tenant(self, slug: str) -> Optional[Dict[str, Any]]:
        return None

    def read_public_catalog(
        self,
        slug: str,
        kind: str,
        *,
        limit: int = _DEFAULT_LIMIT,
        offset: int = 0,
        with_html: bool = True,
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        return None, []


def make_public_reader(session_factory: Optional[Any]) -> Any:
    """Construct the public reader, degrading to LOCAL-ONLY when no public data plane is
    configured (degrade-never).

    ``session_factory`` None -> LocalOnlyPublicReader (no creds: resolve -> None, catalog
    -> empty, NEVER blocked, NEVER discloses). A real zero-arg factory (minting anon-role
    sessions) -> PublicReader. There is no cexai-adapter dependency here: the public path
    is claim-free, so it does not use the tenant-claim-bound SupabaseDataAdapter."""
    if session_factory is None:
        return LocalOnlyPublicReader()
    return PublicReader(session_factory)


# --------------------------------------------------------------------------- #
# Row-shape helpers (liberal driver shapes; mirror entities._iter_rows).       #
# --------------------------------------------------------------------------- #
def _iter_rows(raw: Any) -> List[Any]:
    """Normalize a driver-native query result into a list of rows. Liberal on shape
    (psycopg cursor with fetchall / list of rows / a single row). The offline fake's
    (sql, params) 2-tuple echo (first element a str) is NOT a data row -> yields nothing.
    """
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
            return []  # the (sql, params) echo of a plain fake -> no data rows
        return list(raw)
    if isinstance(raw, Mapping):
        return [raw]
    return []


def _first_row(raw: Any) -> Optional[Any]:
    """The first data row of a driver-native result, or None. Reuses _iter_rows so the
    (sql, params) echo of a plain fake yields None (no row)."""
    rows = _iter_rows(raw)
    return rows[0] if rows else None


def _two_cols(row: Any) -> Tuple[Any, Any]:
    """Pull (col0, col1) out of one row (a mapping with tenant_id/slug, or a sequence)."""
    if isinstance(row, Mapping):
        return row.get("tenant_id"), row.get("slug")
    if isinstance(row, (list, tuple)) and len(row) >= 2:
        return row[0], row[1]
    if isinstance(row, (list, tuple)) and len(row) == 1:
        return row[0], None
    return None, None
