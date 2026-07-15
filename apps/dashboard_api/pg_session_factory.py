# -*- coding: ascii -*-
"""REFERENCE DbSession driver for the dashboard's LIVE mode -- the founder-gated seam
(roadmap #1). A psycopg v3 factory that satisfies the contract
``deps.register_session_factory_from_env`` resolves via
``CEXAI_DASHBOARD_SESSION_FACTORY='apps.dashboard_api.pg_session_factory:make_factory'``.

============================================================================
VALIDATE ON STAGING -- DO NOT POINT PROD AT THIS UNTIL YOU HAVE, ON A STAGING
SUPABASE PROJECT (using a REAL tenant #1):
  1. Applied supabase/migrations/2026061600000{1,2,3,4}_*.sql and confirmed RLS is
     ON + FORCED:  select relname, relrowsecurity, relforcerowsecurity
                   from pg_class where relname like 'tenant_%';
  2. Run the CROSS-TENANT DENIAL PROOF (the load-bearing test): log in as a REAL
     second staging tenant and confirm it sees ZERO of tenant #1's rows
     (GET /entity/{slug}, GET /results). The framework mirror (TenantDataDenied)
     AND the RLS WITH CHECK must BOTH hold -- this reproduces MULTITENANT_DATA_PLANE
     W3 on THIS driver.
  3. Confirm set_config(is_local=True) holds UNDER YOUR POOLER MODE: this driver
     wraps every bind+execute in ONE explicit transaction so SET LOCAL is scoped
     to that transaction -- correct for BOTH Supabase pooler modes (session-mode
     port 5432 AND transaction-mode pooler port 6543 / PgBouncer / Supavisor). A
     `false` here would leak tenant A's claim to the next borrower of a pooled
     connection (silent cross-tenant read). Prove it with a 2-tenant interleave.
Only after 1-3 pass: register the SAME factory on prod. See
_docs/compiled/runbook_dashboard_deploy.md (b.3)+(b.4).
============================================================================

WHY THIS SHAPE (the contract it satisfies):
  * deps' loader expects  ``factory(tenant_id, user_jwt) -> Callable[[], DbSession]``
    (a ZERO-ARG factory minting ONE FRESH DbSession per call) so the adapter's
    claim-bind and the query/write share ONE transaction.
  * DbSession (cexai.governance.data.adapter.DbSession) is:
        execute(sql, params)            -> driver-native rows / cursor
        set_config(key, value, is_local) -> None   # is_local=True MANDATORY
  * The audited adapter (SupabaseDataAdapter.bind_session_tenant) issues, per logical
    op, in this EXACT order on ONE session:
        session.set_config('request.jwt.claims', '{"tenant_id": <tid>}', is_local=True)
        session.execute(<sql>, <params>)            # the bind + the query, same tx
    This driver keeps both on ONE open transaction so the SET LOCAL applies to the
    execute -- THE pooled-connection safety invariant (spec A.5).

TRANSACTION + LIFECYCLE MODEL (the part you must get right per the runbook):
  The adapter mints a FRESH session per logical op (read OR write) and NEVER calls a
  teardown -- so the session owns its own commit/close. This driver:
    * opens psycopg with autocommit=False (an explicit transaction starts on the
      first statement),
    * runs set_config + execute(s) on that ONE transaction,
    * COMMITS + RELEASES the connection back to the pool once the op is done (see
      "WHEN the op finishes" below), or ROLLS BACK + releases on any error.
  The tenant bind therefore NEVER leaks across requests: each logical op gets a fresh
  session, its own transaction, its own SET LOCAL, and is committed-and-released as a
  unit (mirrors the adapter's bind-then-query/write order; RuntimeSyncWriter +
  the entity manager + _read_tenant_results each do `session = factory()` then one
  bind + one execute).

  WHEN the op finishes (the seam the adapter does NOT signal explicitly): the callers
  in this repo issue exactly ONE execute() after the bind per session (a SELECT, or an
  INSERT/UPDATE/DELETE [... RETURNING]). So this driver COMMITS-AND-RELEASES right
  after that execute returns its rows -- a "commit on first executed statement after a
  bind" policy that is correct for the single-statement logical ops the adapter drives.
  A context-manager API (`with make_session() as s:`) is ALSO provided for any future
  multi-statement caller that wants to control the boundary explicitly; the adapter
  path does not need it. If you extend the app to issue MULTIPLE executes per session,
  switch those call sites to the context-manager form and re-validate on staging.

POOLER CHOICE (operational): point CEXAI_TENANT_DB_URL at the TRANSACTION-mode pooler
  endpoint (`...pooler.supabase.com:6543`, `?sslmode=require`) for serverless / many
  short requests; SET LOCAL inside an explicit transaction is the correct primitive
  there. Session-mode (`:5432`) ALSO works with this driver (the transaction wrapper
  is a no-op-correct superset). The single non-negotiable: is_local=True (this driver
  passes it through truthfully and NEVER hardcodes False).

LAZY psycopg IMPORT (do not break the offline tests): psycopg is imported INSIDE the
  factory/connect path, NEVER at module top. So importing this module (and running the
  existing apps/dashboard_api offline test-suite) requires NO psycopg install. psycopg
  is an OPTIONAL extra -- install it only to go live:
      pip install "psycopg[binary]>=3.1"     # the live-mode extra (NOT a hard dep)

KEY CUSTODY: this driver reads ONLY a connection STRING from the env
  (CEXAI_TENANT_DB_URL). It NEVER logs the DSN and NEVER reads a provider/LLM key
  (that is deps.build_credential's job, server-side). The DSN is a server secret --
  set it in the host's secret store, never commit it.

ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted. No network/secret
read at import (the connection opens lazily, per zero-arg factory call).
"""

from __future__ import annotations

import os
from typing import Any, Callable, List, Optional, Sequence

__all__ = [
    "PgSession",
    "make_factory",
    "make_session_factory",
    "PgSessionConfigError",
    "DSN_ENV",
    "RECOMMENDED_POOL_SIZE",
]

# The env var holding the central tenant DB connection string (the transaction-mode
# pooler endpoint in production). Read lazily at connect time -- NEVER at import.
DSN_ENV = "CEXAI_TENANT_DB_URL"

# --------------------------------------------------------------------------- #
# CONNECTION-POOL GUARDRAIL (multi-tenant Sec 5b: pool exhaustion / noisy-neighbor).
# --------------------------------------------------------------------------- #
# This driver opens ONE fresh connection per logical op and relies on the EXTERNAL pooler
# (Supavisor / PgBouncer in transaction mode at :6543) to multiplex them onto a bounded set
# of physical backend connections. The pool ceiling therefore lives in TWO config surfaces
# OUTSIDE this driver -- documented here so an operator wires both:
#
#   1. The SHARED pool ceiling (Supabase dashboard -> Database -> Connection Pooling ->
#      "Pool Size", OR `default_pool_size` / `max_client_conn` if you self-host Supavisor/
#      PgBouncer). This is the hard cap on concurrent backend connections for the whole
#      project. RECOMMENDED_POOL_SIZE below is the suggested starting value for a single
#      uvicorn worker fronting a few tenants; raise it with worker count, keep it well under
#      Postgres `max_connections` (Supabase reserves some for itself).
#   2. The PER-TENANT in-flight cap (apps/dashboard_api/ratelimit.py:TenantConcurrencyCap,
#      env CEXAI_TENANT_MAX_INFLIGHT). This is what stops ONE tenant from grabbing the whole
#      shared pool: each in-flight request holds at most one pooled connection, so capping a
#      tenant's concurrency at K bounds its share of the pool at K. Set
#      sum(per-tenant caps you expect concurrently) <= RECOMMENDED_POOL_SIZE so no single
#      tenant -- nor a thundering herd of them -- can exhaust the shared pool and starve the
#      others (the noisy-neighbor defence).
#
# This driver does NOT open its own client-side psycopg_pool (the external pooler is the
# pool); RECOMMENDED_POOL_SIZE is advisory config, not an enforced limit in this file.
RECOMMENDED_POOL_SIZE = 10  # suggested Supavisor/PgBouncer pool size per uvicorn worker

# The PG run-time setting the adapter binds the tenant claim into. Fixed by the adapter
# + the RLS policy (request.jwt.claims ->> 'tenant_id'); the driver never needs to know
# it (it just executes the SELECT set_config it is handed), but it is documented here so
# the contract is legible at the driver layer.
_CLAIM_KEY = "request.jwt.claims"


class PgSessionConfigError(RuntimeError):
    """Raised when the driver cannot be configured (missing DSN env, or psycopg not
    installed). The factory provider is wrapped by deps so a raise here degrades the
    request to local-only rather than 500-ing -- but the message names the exact fix
    (set CEXAI_TENANT_DB_URL / pip install 'psycopg[binary]')."""


def _import_psycopg() -> Any:
    """LAZY psycopg import (Article VIII import-light + the offline-test contract).

    Imported here, INSIDE the connect path -- NEVER at module top -- so importing this
    module and running the existing offline test-suite needs NO psycopg install. A
    missing psycopg raises PgSessionConfigError with the install hint (the optional
    live-mode extra), not a bare ImportError at app boot."""
    try:
        import psycopg  # type: ignore[import]
    except Exception as exc:  # ImportError or any load failure -> actionable config error
        raise PgSessionConfigError(
            "psycopg v3 is not installed -- it is the OPTIONAL live-mode extra. "
            "Install it to enable the live DB driver: pip install 'psycopg[binary]>=3.1'"
        ) from exc
    return psycopg


def _resolve_dsn(dsn: Optional[str]) -> str:
    """Resolve the connection string: the explicit ``dsn`` arg wins (tests / callers
    that pass one), else $CEXAI_TENANT_DB_URL. A blank/missing value raises
    PgSessionConfigError (the DSN is the one thing the driver cannot synthesize). The
    DSN value is NEVER logged."""
    resolved = (dsn if dsn is not None else os.environ.get(DSN_ENV, "")).strip()
    if not resolved:
        raise PgSessionConfigError(
            "no tenant DB connection string -- set %s to your transaction-mode pooler "
            "endpoint (postgresql://user:pass@<project>.pooler.supabase.com:6543/postgres"
            "?sslmode=require) before going live" % DSN_ENV
        )
    return resolved


class PgSession:
    """Adapts ONE pooled psycopg v3 connection to the DbSession Protocol
    (cexai.governance.data.adapter.DbSession).

    Holds an OPEN, autocommit=False connection -- an explicit transaction begins on the
    first statement. ``set_config`` and ``execute`` run on that SAME transaction, so the
    adapter's bind (SET LOCAL request.jwt.claims via set_config) applies to the query/
    write that follows it (THE pooled-connection safety invariant, spec A.5).

    LIFECYCLE: the adapter mints a fresh PgSession per logical op and issues exactly ONE
    execute() after the bind, then drops the reference. So PgSession COMMITS + closes
    (returns the connection to the pool) right after that execute returns -- "commit on
    the first executed statement after a bind". On ANY error it ROLLS BACK + closes. The
    tenant bind thus never leaks across requests. For a future multi-statement caller,
    use the context-manager form (`with PgSession.open(...) as s:`), which defers the
    commit to __exit__; the adapter path does not need it.

    The connection is borrowed via ``_connect`` (a zero-arg callable returning an open,
    autocommit=False psycopg connection) so tests can inject a fake WITHOUT psycopg."""

    def __init__(
        self,
        connect: Callable[[], Any],
        *,
        autoclose: bool = True,
    ) -> None:
        """connect: a zero-arg callable returning an OPEN psycopg connection with
        autocommit=False (a transaction begins on first use). autoclose=True (the
        adapter path) makes the session commit+close after its first post-bind execute;
        autoclose=False (the context-manager path) defers commit/close to the explicit
        boundary (__exit__ / close())."""
        self._connect = connect
        self._autoclose = autoclose
        self._conn: Optional[Any] = None
        self._closed = False
        # True once a statement has run after the most recent bind; drives the
        # "commit on first executed statement" autoclose policy.
        self._dirty = False
        # True once `SET LOCAL ROLE authenticated` has run on the CURRENT transaction
        # (drives the once-per-transaction role switch -- see set_config). Reset when the
        # transaction ends (commit/rollback/release), since SET LOCAL is tx-scoped.
        self._role_set = False

    # -- connection acquisition (lazy: opens on first statement) ------------- #
    def _connection(self) -> Any:
        """Return the open connection, borrowing it on first use. A session reused after
        close is a programming error -- fail loudly rather than silently open a second
        connection (which would NOT carry the prior SET LOCAL bind)."""
        if self._closed:
            raise PgSessionConfigError(
                "PgSession used after it was committed/closed -- mint a fresh session "
                "per logical op (factory() returns a new one each call)"
            )
        if self._conn is None:
            self._conn = self._connect()
        return self._conn

    # -- DbSession Protocol: set_config ------------------------------------- #
    def set_config(self, key: str, value: str, is_local: bool) -> None:
        """Set a PG run-time setting via ``SELECT set_config(key, value, is_local)`` on
        the CURRENT transaction. The adapter calls this to bind the verified-claim tenant
        (key='request.jwt.claims', is_local=True) BEFORE the query/write.

        is_local is passed THROUGH TRUTHFULLY -- NEVER hardcoded. is_local=True scopes the
        setting to the current transaction so a pooled connection cannot leak it to the
        next borrower (spec A.5). This is the load-bearing line: do not 'simplify' it to
        a SET statement or a false third arg.

        RLS ROLE POSTURE (council wave-0.5 A3): immediately after the claim bind, switch the
        transaction's role to ``authenticated`` via ``SET LOCAL ROLE authenticated`` -- the
        PERMISSIVE ``tenant_boundary`` policy is ``TO authenticated``, so under the connection's
        OWNER role (which BYPASSEs RLS) the policy would never apply and a pooled prod
        connection would run the query WITHOUT row isolation. This mirrors the proof harness
        (cex_dashboard_persist_proof._Psycopg2AuthSession) exactly: set_config (the bind) ->
        SET LOCAL ROLE authenticated -> the query/write, ALL on the same transaction, so the
        production RLS posture matches what the cross-tenant denial proof certified. Done ONCE
        per transaction (``_role_set``); SET LOCAL is tx-scoped so it resets at commit/rollback.
        The role literal is a FIXED constant (never caller-controlled) -> no injection surface;
        SET LOCAL ROLE cannot take a bound parameter, so it is a plain statement here."""
        conn = self._connection()
        with conn.cursor() as cur:
            # Bound parameters (never string-concatenated) -> no injection surface; the
            # boolean is passed as-is so SET LOCAL vs SET SESSION is the caller's choice.
            cur.execute("SELECT set_config(%s, %s, %s)", (key, value, is_local))
            if not self._role_set:
                # Transaction-scoped role switch so the PERMISSIVE tenant_boundary policy
                # (TO authenticated) actually governs the subsequent execute. 'authenticated'
                # is a fixed literal (NOT caller input) -> safe to inline.
                cur.execute("SET LOCAL ROLE authenticated")
                self._role_set = True
        # The bind itself does not 'finish' the op -- the query/write that follows does.
        # Reset dirty so an autoclose commit triggers on the NEXT execute (the query),
        # keeping the bind + the query in the one transaction we commit together.
        self._dirty = False

    # -- DbSession Protocol: execute ---------------------------------------- #
    def execute(self, sql: str, params: Optional[Sequence[Any]] = None) -> Any:
        """Run ``sql`` with optional positional ``params`` on the SAME transaction as the
        preceding set_config bind, and return the driver-native result the adapter does
        not interpret:
          * a row-returning statement (SELECT, or INSERT/UPDATE/DELETE ... RETURNING) ->
            the fetched rows (a list of tuples), so the dashboard's id/row extraction
            (_first_id / _normalize_rows) sees real rows.
          * a non-returning statement -> the cursor (truthy; callers that need an id use
            RETURNING).
        On the autoclose (adapter) path this COMMITS + closes after returning (the op is
        one bind + one execute). On ANY error it ROLLS BACK + closes and re-raises."""
        conn = self._connection()
        try:
            cur = conn.cursor()
            try:
                cur.execute(sql, list(params) if params is not None else None)
                # description is set iff the statement produced a result set (SELECT or
                # ... RETURNING). Materialize rows BEFORE we commit/close the cursor.
                if cur.description is not None:
                    rows = cur.fetchall()
                else:
                    rows = cur  # non-returning: hand back the cursor (truthy)
            finally:
                # Close the cursor only if we already fetched (rows is a list); when we
                # hand the cursor back we must NOT close it here.
                if cur.description is not None:
                    cur.close()
        except Exception:
            self._rollback_and_close()
            raise
        self._dirty = True
        if self._autoclose:
            # The adapter path: one bind + one execute == the whole logical op. Commit
            # and release the connection NOW so the tenant bind never outlives the op.
            self._commit_and_close()
        return rows

    # -- explicit lifecycle (context-manager / multi-statement callers) ----- #
    def commit(self) -> None:
        """Commit the current transaction and release the connection. Idempotent after
        close. Used by the context-manager path; the adapter path commits via autoclose."""
        self._commit_and_close()

    def rollback(self) -> None:
        """Roll back the current transaction and release the connection. Idempotent."""
        self._rollback_and_close()

    def close(self) -> None:
        """Release the connection WITHOUT an extra commit if nothing is pending; if a
        statement ran but was not committed (context-manager path that did not commit),
        roll back to be safe (never leak an open, half-bound transaction to the pool)."""
        if self._closed:
            return
        if self._dirty:
            self._rollback_and_close()
        else:
            self._release()

    def _commit_and_close(self) -> None:
        if self._closed:
            return
        try:
            if self._conn is not None:
                self._conn.commit()
        finally:
            self._release()

    def _rollback_and_close(self) -> None:
        if self._closed:
            return
        try:
            if self._conn is not None:
                self._conn.rollback()
        except Exception:
            # A rollback failure must not mask the original error; we still release.
            pass
        finally:
            self._release()

    def _release(self) -> None:
        """Close the connection (returns it to the pool) and mark the session spent."""
        self._closed = True
        self._dirty = False
        # SET LOCAL ROLE is transaction-scoped; the transaction is now ending, so the next
        # bind on any future session must re-issue the role switch.
        self._role_set = False
        conn, self._conn = self._conn, None
        if conn is not None:
            try:
                conn.close()
            except Exception:
                # Best-effort: a close failure must never propagate out of teardown.
                pass

    # -- context-manager sugar (optional; adapter path does not use it) ------ #
    def __enter__(self) -> "PgSession":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        if exc_type is not None:
            self._rollback_and_close()
        else:
            self._commit_and_close()
        return False  # never suppress the exception

    @classmethod
    def open(
        cls,
        connect: Callable[[], Any],
    ) -> "PgSession":
        """Build a PgSession for EXPLICIT (multi-statement) transaction control: autoclose
        is OFF, so set_config + N executes run on one transaction committed at __exit__ /
        commit(). The adapter path does NOT need this (it uses the autoclose default)."""
        return cls(connect, autoclose=False)


def _make_connect(dsn: str) -> Callable[[], Any]:
    """Return a zero-arg callable that borrows ONE open, autocommit=False psycopg
    connection from the pooler at ``dsn``. psycopg is imported LAZILY here. Each call
    opens a fresh connection (the pooler -- Supavisor/PgBouncer in transaction mode --
    is what actually pools/recycles the physical connection); autocommit=False so an
    explicit transaction wraps the bind + the query (SET LOCAL safety)."""
    psycopg = _import_psycopg()

    def _connect() -> Any:
        # autocommit=False -> a transaction begins on the first statement, so SET LOCAL
        # (set_config is_local=True) is scoped to THIS transaction. sslmode is expected
        # to be in the DSN (?sslmode=require) for Supabase.
        return psycopg.connect(dsn, autocommit=False)

    return _connect


def make_session_factory(
    tenant_id: str,
    user_jwt: str,
    *,
    dsn: Optional[str] = None,
) -> Callable[[], PgSession]:
    """The ZERO-ARG DbSession factory for ONE (tenant_id, user_jwt) request.

    This is the inner half of the contract: deps calls
    ``make_factory(tenant_id, user_jwt)`` and gets back THIS zero-arg callable; the
    adapter then calls it ONCE PER LOGICAL OP to mint a fresh PgSession (so the bind +
    the query/write share one transaction, and the bind never leaks across ops).

    NOTE on (tenant_id, user_jwt): they are accepted to match the contract signature but
    are NOT used to scope the CONNECTION -- the tenant scoping is done by the adapter's
    set_config bind (request.jwt.claims) inside the transaction + the RLS policy, NOT by
    a per-tenant DSN. This is correct + intended: ONE central pooled DB, RLS-isolated per
    tenant_id (the CENTRALIZED multi-tenant model). The user_jwt is NOT replayed to PG
    here (the adapter binds the VERIFIED claim, not the raw token); it is part of the
    signature so a future driver could, e.g., choose a read-replica per request without
    changing the seam. The DSN is resolved ONCE here (fail-closed if missing) so a
    misconfig surfaces at factory-build time, not mid-request.

    Returns a zero-arg callable; each call returns a fresh PgSession on a fresh pooled
    connection. Raises PgSessionConfigError if the DSN is unset or psycopg is absent
    (deps wraps the provider so that degrades the request to local-only)."""
    resolved_dsn = _resolve_dsn(dsn)
    connect = _make_connect(resolved_dsn)

    def zero_arg() -> PgSession:
        # Fresh session per logical op: a new PgSession over a freshly-borrowed
        # connection. autoclose=True (default) so it commits + releases after the single
        # post-bind execute the adapter issues.
        return PgSession(connect)

    return zero_arg


def make_factory(
    tenant_id: str,
    user_jwt: str,
) -> Callable[[], PgSession]:
    """THE registration entry point. Name THIS in the env to go live:

        CEXAI_DASHBOARD_SESSION_FACTORY=apps.dashboard_api.pg_session_factory:make_factory

    deps.register_session_factory_from_env imports the module + binds this callable onto
    ``deps.tenant_session_factory``. Thereafter /results, /summary, /entity CRUD, and the
    /capability/run write-through ALL flow to the live tenant DB through the AUDITED
    SupabaseDataAdapter -- no other app code changes.

    Contract: ``factory(tenant_id, user_jwt) -> Callable[[], DbSession]``. Here it
    delegates to make_session_factory (which reads CEXAI_TENANT_DB_URL). Kept as a thin
    named wrapper so the registration target is stable + obvious.

    REMINDER -- VALIDATE ON STAGING FIRST (using a REAL tenant #1): run the cross-tenant
    denial proof + confirm set_config(is_local=True) holds under YOUR pooler mode BEFORE
    registering this on prod. See the module docstring + runbook (b.4)."""
    return make_session_factory(tenant_id, user_jwt)
