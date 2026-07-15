# -*- coding: utf-8 -*-
"""cex_runtime_sync.py -- the runtime->central WRITE-THROUGH (mission
RUNTIME_CENTRAL_SYNC; roadmap C4 / debt D1; spec _docs/spec_runtime_central_sync.md).

THE GAP THIS CLOSES (the cross-layer gap). The W1/W2 data plane built + audited the
SupabaseDataAdapter (bind + write + the cross-tenant mirror), the RLS migrations
(tenant_data / tenant_runtime, SINGLE PERMISSIVE tenant-match + FORCE RLS + WITH
CHECK), and the _tools edge (cex_data_edge: the ONE CEX_TENANT_ID read). The runtime
(cex_run_capability.run_capability) emits a DbWriter SEAM (persist_artifact) -- but
NO concrete writer connects that seam to the adapter, so tenant brain-state never
syncs to the central tenant_* tables (run_capability is always called with db=None).
This module is that single missing connector.

WHAT IT WIRES (one concrete write path, reuse > rebuild):
  * persist_artifact(tenant_id, capability, kind, artifact, meta) -> str | None
      satisfies cex_run_capability.DbWriter; writes a run_capability artifact INTO
      the tenant's OWN Supabase tenant_data table THROUGH adapter.write (tenant_id
      EXPLICIT) and returns the new row id. This unblocks the dashboard /run's
      db=None.
  * persist_runtime_state(tenant_id, scope, key, state) -> str | None
      the runtime->central STATE sync proper: write-throughs a runtime record
      (scope in {handoff, signal, decision}) INTO tenant_runtime, idempotent on a
      deterministic uuid5 over (tenant_id, scope, key) so a re-sync of the SAME
      logical record UPSERTs rather than duplicates.

THE TENANT_ID BINDING (EXPLICIT -- never implicit; spec section 1):
  tenant_id is ALWAYS an explicit argument. The verified principal claim
  ({"tenant": tid}) drives adapter.bind_session_tenant; the SAME tid is the explicit
  write tenant_id. This module NEVER reads CEX_TENANT_ID -- the edge / caller resolves
  it (active_tenant_id()) and passes it IN. The bind + the write share ONE transaction
  (one session from the factory) so the is_local=True claim is not leaked to the next
  borrower of a pooled connection (spec A.5, mirrored from the dashboard read path).

THREE-LAYER DENY (defence in depth; the writer lets each fire):
  1. file-tier   -- deny_cross_tenant at the edge (optional pre-check; not re-done here).
  2. framework   -- adapter's _deny_cross_tenant_equality mirror -> TenantDataDenied
                    ('cross_tenant') BEFORE the DB is touched (proven offline here).
  3. DB          -- the migration's RLS WITH CHECK is the AUTHORITATIVE boundary
                    (proven by the EXISTING cexai test_rls_denial.py against real PG).

DEGRADE-NEVER / FAIL-CLOSED:
  * make_runtime_sync_writer(None) (no central creds / no session factory) returns a
    LOCAL-ONLY no-op writer: persist_* returns None, NEVER raises, NEVER touches a
    session -> the run proceeds local-only (persisted=False). The run is NEVER blocked
    by a missing data plane.
  * With a factory, a cross-tenant or unbound write FAILS CLOSED (TenantDataDenied
    propagates); run_capability surfaces the failure (best-effort-after-pass) without
    discarding the produced artifact.

ALLOWED IMPORT DIRECTION (ADR D6 / adapter THE BOUNDARY RULE): _tools MAY import
cexai (this glue depends on the package). cexai MUST NEVER import _tools (it is
extraction-bound). This writer lives in _tools precisely so the cexai import + any
env read sit on the allowed side. The adapter is REUSED, never re-implemented; the
RLS is REUSED, never re-declared.

ASCII-only per .claude/rules/ascii-code-rule.md.
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

# --------------------------------------------------------------------------- #
# cexai import resolution -- mirrors cex_data_edge._ensure_cexai_importable.   #
# _tools/ is a direct child of the repo root; the cexai import root is the     #
# <repo_root>/cexai dir (it CONTAINS the cexai/ package). Insert it on sys.path #
# so `from cexai...` resolves whether or not the package was pip-installed.     #
# This is the ALLOWED direction (_tools -> cexai); cexai never imports back.    #
# --------------------------------------------------------------------------- #
_REPO_ROOT = Path(__file__).resolve().parent.parent
_CEXAI_IMPORT_ROOT = _REPO_ROOT / "cexai"


def _ensure_cexai_importable() -> None:
    """Idempotently put <repo_root>/cexai on sys.path so the package resolves.

    No-op if cexai already imports (e.g. pip install -e .) or if the path is
    already present. Degrade-never: a missing dir is simply not inserted -- the
    subsequent import then raises a clear ModuleNotFoundError at use time, not a
    silent wrong-path success. APPEND (not insert-0) so a real installed package or
    a caller's deliberate ordering is never shadowed."""
    p = str(_CEXAI_IMPORT_ROOT)
    if _CEXAI_IMPORT_ROOT.is_dir() and p not in sys.path:
        sys.path.append(p)


_ensure_cexai_importable()

# The package side (allowed import direction). Imported after the path shim. The
# adapter + its deny leaf are REUSED as-is; this module re-implements NEITHER.
from cexai.governance.data.adapter import (  # noqa: E402
    DbSession,
    SupabaseDataAdapter,
)
from cexai.governance.data.errors import TenantDataDenied  # noqa: E402

__all__ = [
    "RuntimeSyncWriter",
    "LocalOnlyWriter",
    "make_runtime_sync_writer",
    "runtime_record_id",
    "memory_record_id",
    "agent_run_id",
    "agent_step_id",
    "VALID_RUNTIME_SCOPES",
    "VALID_STEP_KINDS",
    "MEMORY_EMBED_DIM",
    "TenantDataDenied",
    "DbSession",
    "SupabaseDataAdapter",
]

# The tenant tables the runtime syncs INTO (must match the migration table names:
# supabase/migrations/20260616000002_tenant_data.sql + ...0003_tenant_runtime.sql
# + ...0001_tenant_memory.sql + ...20260617000001_agent_runs_steps.sql).
_TENANT_DATA_TABLE = "tenant_data"
_TENANT_RUNTIME_TABLE = "tenant_runtime"
_TENANT_MEMORY_TABLE = "tenant_memory"
# The Phase C agent-run ledger (ADR adr_agents_sdk_dashboard / OQ6). Two tables,
# SAME audited adapter + SAME single-PERMISSIVE tenant-match RLS as the surfaces above.
_AGENT_RUNS_TABLE = "agent_runs"
_AGENT_STEPS_TABLE = "agent_steps"

# The agent_steps.kind enum the migration models (plan | act | observe | tool). The
# writer normalizes/validates against this so a typo can never widen what is persisted
# (mirrors VALID_RUNTIME_SCOPES). agent_grounding_record (P10) is the schema seed.
VALID_STEP_KINDS = ("plan", "act", "observe", "tool")

# The pgvector column width on tenant_memory.embedding (migration ...0001:
# `embedding vector(1536)` -- text-embedding-3-small width). THE single source of
# truth the migration mirrors: a pgvector INSERT of a vector whose length != the
# declared column dimension is a hard Postgres error, so the write path asserts the
# produced vector is EXACTLY this wide at the seam (spec 6.3 step 2). Option D
# (RATIFIED 2026-06-17): the OFFLINE embedder is FakeEmbedder(dim=MEMORY_EMBED_DIM),
# which already accepts `dim` -- a 1536-wide deterministic offline vector, ZERO new
# embedder code, prod column width unchanged. The REAL production embedder (OpenAI
# text-embedding-3-small or a 1536-wide model) is the founder-gated injected seam
# (passed in via the `embedding` arg); this module never calls a network embedder.
MEMORY_EMBED_DIM = 1536

# The runtime `scope` enum the migration models (handoff | signal | decision). The
# writer normalizes/validates against this so a typo can never widen what is synced.
VALID_RUNTIME_SCOPES = ("handoff", "signal", "decision")

# A fixed, project-local namespace for the deterministic runtime-record uuid5. It is
# NOT a secret and NOT tenant-derived; the tenant_id is folded into the NAME (not the
# namespace) so the id is stable per (tenant_id, scope, key) and idempotent re-syncs
# UPSERT. uuid5 (SHA-1 based) is deterministic + collision-resistant for this use.
_RUNTIME_NS = uuid.UUID("a4f3c2d1-0000-5000-8000-72756e74696d")  # "...runtim"

# The sibling fixed namespace for the deterministic memory-record uuid5 (spec 6.3
# step 3). Distinct from _RUNTIME_NS so a (tenant, namespace, key) memory record and
# a (tenant, scope, key) runtime record never share an id even if the strings align.
# Same rule: tenant_id is folded into the NAME, so two tenants never collide.
_MEMORY_NS = uuid.UUID("a4f3c2d1-0000-5000-8000-6d656d6f7279")  # "...memory"

# The agent-run fixed namespace for the deterministic agent_run uuid5 (ADR Phase C).
# Distinct from the runtime/memory namespaces so the SAME (tenant, run_key) never
# collides with a runtime/memory record. tenant_id is folded into the NAME (two
# tenants never collide). The dashboard supplies a run_key (a uuid4 hex it minted),
# so a re-persist of the SAME logical run UPSERTs rather than duplicating.
_AGENT_RUN_NS = uuid.UUID("a4f3c2d1-0000-5000-8000-6167656e7472")  # "...agentr"
# The agent-step fixed namespace -- a step id is stable per (tenant, run_key,
# step_index), so re-persisting the SAME step (idempotent retry) UPSERTs.
_AGENT_STEP_NS = uuid.UUID("a4f3c2d1-0000-5000-8000-6167656e7473")  # "...agents"


def _coerce_tenant(value: Any) -> str:
    """Project a raw tenant value to a stripped string (mirrors the adapter helper).
    None -> empty string; empty result means 'no usable tenant' -> fail-closed deny
    upstream (the adapter raises missing_tenant)."""
    if value is None:
        return ""
    return str(value).strip()


def runtime_record_id(tenant_id: str, scope: str, key: str) -> str:
    """The deterministic row id for a runtime record (idempotency key).

    uuid5(namespace, "<tenant_id>|<scope>|<key>") -- stable per logical record so a
    re-sync of the SAME (tenant, scope, key) targets the SAME row (ON CONFLICT ...
    DO UPDATE). tenant_id is part of the NAME, so two tenants' records with the same
    (scope, key) never collide. Returned as the canonical 8-4-4-4-12 string."""
    name = "%s|%s|%s" % (_coerce_tenant(tenant_id), scope, key)
    return str(uuid.uuid5(_RUNTIME_NS, name))


def memory_record_id(tenant_id: str, namespace: str, key: str) -> str:
    """The deterministic row id for a tenant_memory record (idempotency key; spec
    6.3 step 3). Sibling of runtime_record_id over the memory namespace.

    uuid5(_MEMORY_NS, "<tenant_id>|<namespace>|<key>") -- stable per logical record so
    a re-sync of the SAME (tenant, namespace, key) targets the SAME row (ON CONFLICT
    (id) DO UPDATE). tenant_id is part of the NAME, so two tenants' records with the
    same (namespace, key) never collide. Returned as the canonical 8-4-4-4-12 string."""
    name = "%s|%s|%s" % (_coerce_tenant(tenant_id), namespace, key)
    return str(uuid.uuid5(_MEMORY_NS, name))


def agent_run_id(tenant_id: str, run_key: str) -> str:
    """The deterministic row id for an agent_runs record (idempotency key; ADR Phase C).

    uuid5(_AGENT_RUN_NS, "<tenant_id>|<run_key>") -- stable per logical run so a
    re-persist of the SAME (tenant, run_key) targets the SAME row (ON CONFLICT (id) DO
    UPDATE -- the run header is written once at kickoff then UPDATEd at completion).
    tenant_id is part of the NAME, so two tenants' runs with the same run_key never
    collide. The run_key is a uuid4 hex the kicker mints. Returned as the canonical
    8-4-4-4-12 string -- so it doubles as the public ``run_id`` the dashboard polls."""
    name = "%s|%s" % (_coerce_tenant(tenant_id), run_key)
    return str(uuid.uuid5(_AGENT_RUN_NS, name))


def agent_step_id(tenant_id: str, run_key: str, step_index: int) -> str:
    """The deterministic row id for an agent_steps record (idempotency key; ADR Phase C).

    uuid5(_AGENT_STEP_NS, "<tenant_id>|<run_key>|<step_index>") -- stable per logical
    step so re-persisting the SAME (tenant, run_key, step_index) UPSERTs rather than
    duplicating (a retried step targets its own row). tenant_id is part of the NAME, so
    two tenants never collide. Distinct namespace from agent_run_id so a run header and
    its step 0 never share an id."""
    name = "%s|%s|%d" % (_coerce_tenant(tenant_id), run_key, int(step_index))
    return str(uuid.uuid5(_AGENT_STEP_NS, name))


def _memory_embedder():
    """Return the canonical OFFLINE embedder for tenant_memory (spec 6.3 step 2,
    Option D): FakeEmbedder(dim=MEMORY_EMBED_DIM) -- a deterministic, dependency-free,
    network-free 1536-wide L2-normalized vector. The class already accepts `dim`, so
    NO new embedder code is written; the prod column width (1536) is unchanged.

    Imported lazily (the cexai memory extra is optional) so importing this module
    never requires it. ImportError surfaces here only when a caller actually asks the
    writer to embed text itself (embedding=None) AND the package is absent -- the
    far more common path passes a real embedding IN (the founder-gated prod seam)."""
    from cexai.memory.vector import FakeEmbedder  # lazy: optional cexai[memory] extra

    return FakeEmbedder(dim=MEMORY_EMBED_DIM)


class RuntimeSyncWriter:
    """The concrete runtime->central write-through (spec section 1).

    Wraps a SupabaseDataAdapter bound to a session factory. Every public method takes
    tenant_id EXPLICITLY, binds the verified claim onto a fresh session, and writes
    THROUGH the adapter (tenant_id explicit, RLS-enforced) inside that one session/
    transaction (spec A.5). The api/credential never touches this layer; it persists
    artifacts + runtime state only.

    Construct via make_runtime_sync_writer (which returns a LocalOnlyWriter when no
    factory is configured -- degrade-never). The session_factory is a zero-arg
    callable returning a DbSession (production: a pooled Supabase connection; tests:
    a FakeDbSession). The adapter is REUSED, never re-implemented."""

    def __init__(
        self,
        session_factory: Callable[[], DbSession],
        *,
        adapter: Optional[SupabaseDataAdapter] = None,
    ) -> None:
        self._factory = session_factory
        # Reuse the audited adapter; allow injection for tests, else construct the
        # real one over the SAME factory (the adapter holds it for callers that want
        # it to mint connections; per-call methods take the session explicitly).
        self._adapter = adapter if adapter is not None else SupabaseDataAdapter(session_factory)

    # -- run_capability.DbWriter seam --------------------------------------- #
    def persist_artifact(
        self,
        tenant_id: str,
        capability: str,
        kind: str,
        artifact: str,
        meta: Mapping[str, Any],
    ) -> Optional[str]:
        """Write a run_capability artifact INTO the tenant's tenant_data (the
        DbWriter seam; spec a2). tenant_id EXPLICIT. Binds the verified claim, then
        adapter.write INSERTs a row whose tenant_id == the bound claim (the WITH
        CHECK shape). Returns the new row id (server-default gen_random_uuid()) or
        None if the driver did not surface one.

        Fail-closed: a cross-tenant tenant_id (vs the bound claim) raises
        TenantDataDenied('cross_tenant') from the adapter BEFORE the DB is touched.
        The artifact row carries (tenant_id, capability, kind, payload) -- payload is
        a jsonb object holding the artifact text + the safe meta (NEVER a secret;
        run_capability guarantees meta is credential-free)."""
        tid = _coerce_tenant(tenant_id)
        session = self._factory()
        self._bind(session, tid)
        payload = {
            "artifact": artifact,
            "meta": _safe_meta(meta),
        }
        # tenant_data shape: id default, tenant_id, kind, payload, created_at default
        # (migration 20260616000002) + capability text NOT NULL DEFAULT '' (migration
        # 20260618000001). We set tenant_id + kind + payload + capability; id/created_at
        # default. CAPABILITY_COMPLETENESS W1 fix: the capability slug was RECEIVED but never
        # written, so the dedicated column persisted EMPTY (proven live on a real tenant's prod).
        # It now
        # lands on the row as a first-class, WHERE-filterable value (the dashboard ?capability=
        # filter), not only inside payload jsonb. Appended LAST so the column order stays
        # backward-compatible with any positional reader.
        sql = (
            "INSERT INTO " + _TENANT_DATA_TABLE + " (tenant_id, kind, payload, capability) "
            "VALUES (%s, %s, %s::jsonb, %s) RETURNING id"
        )
        params = [tid, kind, json.dumps(payload, ensure_ascii=True), str(capability or "")]
        result = self._adapter.write(session, tid, sql, params)
        return _first_id(result)

    # -- the upload-persist read/update seam (dual-output media slots) ------- #
    def read_artifact(
        self, tenant_id: str, record_id: str
    ) -> Optional[Dict[str, Any]]:
        """Read ONE persisted tenant_data row's payload by id, TENANT-SCOPED (the upload-persist
        read seam). Binds the verified claim, SELECTs payload WHERE id = %s AND tenant_id = %s
        (RLS AND the explicit tenant predicate both scope it), and returns the parsed payload dict
        -- the ``{artifact, meta}`` object whose ``meta.dual_output`` carries the media ledger --
        or None when no row matches THIS tenant.

        Fail-closed: a cross-tenant / unknown id matches no row -> None (NEVER another tenant's
        row). Read-only -- it never writes."""
        tid = _coerce_tenant(tenant_id)
        rid = str(record_id or "").strip()
        if not rid:
            return None
        session = self._factory()
        self._bind(session, tid)
        sql = (
            "SELECT payload FROM " + _TENANT_DATA_TABLE
            + " WHERE id = %s AND tenant_id = %s"
        )
        result = self._adapter.query(session, tid, sql, [rid, tid])
        return _first_payload(result)

    def update_artifact_payload(
        self, tenant_id: str, record_id: str, payload: Mapping[str, Any]
    ) -> bool:
        """Replace ONE persisted tenant_data row's payload by id, TENANT-SCOPED (the upload-persist
        write seam). Binds the verified claim, then UPDATEs payload WHERE id = %s AND tenant_id =
        %s RETURNING id. Returns True iff a row was updated (the RETURNING id surfaced).

        Fail-closed: a cross-tenant / unknown id updates NO row (the WHERE tenant_id predicate AND
        RLS), so the method returns False -- NEVER another tenant's row. The whole payload is
        re-serialized (read-modify-write at the caller); the src it carries is a data URI / URL,
        never a secret (the upload-persist path writes only media srcs)."""
        tid = _coerce_tenant(tenant_id)
        rid = str(record_id or "").strip()
        if not rid:
            return False
        session = self._factory()
        self._bind(session, tid)
        sql = (
            "UPDATE " + _TENANT_DATA_TABLE
            + " SET payload = %s::jsonb WHERE id = %s AND tenant_id = %s RETURNING id"
        )
        params = [json.dumps(dict(payload), ensure_ascii=True), rid, tid]
        result = self._adapter.write(session, tid, sql, params)
        return _first_id(result) is not None

    # -- the runtime->central STATE sync proper ----------------------------- #
    def persist_runtime_state(
        self,
        tenant_id: str,
        scope: str,
        key: str,
        state: Mapping[str, Any],
    ) -> Optional[str]:
        """Write-through a runtime record (handoff | signal | decision) INTO
        tenant_runtime (the gap's core sync; spec a). tenant_id EXPLICIT. Idempotent
        on runtime_record_id(tenant_id, scope, key): a re-sync of the SAME logical
        record UPSERTs (ON CONFLICT (id) DO UPDATE) rather than duplicating.

        Fail-closed: an unknown scope -> ValueError (a typo must not silently widen
        what syncs); a cross-tenant tenant_id -> TenantDataDenied('cross_tenant')
        from the adapter before the DB is touched. Returns the (stable) row id."""
        tid = _coerce_tenant(tenant_id)
        scope_norm = (scope or "").strip().lower()
        if scope_norm not in VALID_RUNTIME_SCOPES:
            raise ValueError(
                "invalid runtime scope %r (expected one of %s)"
                % (scope, ", ".join(VALID_RUNTIME_SCOPES))
            )
        rid = runtime_record_id(tid, scope_norm, key)
        session = self._factory()
        self._bind(session, tid)
        # tenant_runtime shape (migration ...0003): id, tenant_id, scope, state,
        # updated_at. We set the deterministic id explicitly so re-sync UPSERTs.
        sql = (
            "INSERT INTO " + _TENANT_RUNTIME_TABLE + " (id, tenant_id, scope, state) "
            "VALUES (%s, %s, %s, %s::jsonb) "
            "ON CONFLICT (id) DO UPDATE SET state = EXCLUDED.state, updated_at = now() "
            "RETURNING id"
        )
        params = [rid, tid, scope_norm, json.dumps(dict(state), ensure_ascii=True)]
        result = self._adapter.write(session, tid, sql, params)
        surfaced = _first_id(result)
        # The id is deterministic; return the stable rid even if the fake/driver did
        # not echo a RETURNING row (the row IS rid by construction).
        return surfaced if surfaced is not None else rid

    # -- the tenant_memory (pgvector) write-through ------------------------- #
    def persist_memory(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        text: str,
        embedding: Optional[Sequence[float]] = None,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Optional[str]:
        """Write-through a tenant memory entry INTO tenant_memory (the next sync
        slice; spec section 6). tenant_id EXPLICIT -- the same rule as the rest of the
        writer. Mirrors persist_runtime_state exactly: same adapter, same bind
        (is_local=True), same idempotency, same degrade-never.

        The vector is the caller-supplied `embedding` (the founder-gated PROD seam:
        a 1536-wide vector from the real embedder injected from OUTSIDE this module)
        OR, when None, FakeEmbedder(dim=MEMORY_EMBED_DIM).embed(text) offline (Option
        D). Its width is asserted at the seam against MEMORY_EMBED_DIM == 1536 (the
        pgvector column width); a wrong-width vector -> ValueError BEFORE any DB call,
        because a length != the declared column dimension is a hard Postgres error.

        Idempotent on memory_record_id(tenant_id, namespace, key): a re-sync of the
        SAME logical record UPSERTs (ON CONFLICT (id) DO UPDATE) rather than
        duplicating. Fail-closed: a cross-tenant tenant_id (vs the bound claim) raises
        TenantDataDenied('cross_tenant') from the adapter before the DB is touched.
        Returns the (stable) row id."""
        tid = _coerce_tenant(tenant_id)
        # Resolve the vector: caller-supplied (prod seam) wins; else embed offline.
        if embedding is not None:
            vec = [float(v) for v in embedding]
        else:
            vec = [float(v) for v in _memory_embedder().embed(text)]
        # The width MUST match the pgvector column (vector(1536)); assert at the seam
        # so a wrong-width vector fails HERE with a clear message, never as an opaque
        # driver error mid-INSERT. This is spec test m4 + m6.
        if len(vec) != MEMORY_EMBED_DIM:
            raise ValueError(
                "embedding width %d != tenant_memory.embedding dimension %d"
                % (len(vec), MEMORY_EMBED_DIM)
            )
        rid = memory_record_id(tid, namespace, key)
        session = self._factory()
        self._bind(session, tid)
        # tenant_memory shape (migration ...0001): id, tenant_id, namespace, content,
        # embedding vector(1536), metadata jsonb, created_at default. We set the
        # deterministic id explicitly so a re-sync UPSERTs; embedding is cast ::vector
        # from the pgvector text literal; metadata reuses the secret-shaped-key guard.
        sql = (
            "INSERT INTO " + _TENANT_MEMORY_TABLE
            + " (id, tenant_id, namespace, content, embedding, metadata) "
            "VALUES (%s, %s, %s, %s, %s::vector, %s::jsonb) "
            "ON CONFLICT (id) DO UPDATE SET "
            "content = EXCLUDED.content, "
            "embedding = EXCLUDED.embedding, "
            "metadata = EXCLUDED.metadata "
            "RETURNING id"
        )
        params = [
            rid,
            tid,
            namespace,
            text,
            _vector_literal(vec),
            json.dumps(_safe_meta(metadata), ensure_ascii=True),
        ]
        result = self._adapter.write(session, tid, sql, params)
        surfaced = _first_id(result)
        # Deterministic id: return the stable rid even if the fake/driver did not echo
        # a RETURNING row (the row IS rid by construction), mirroring persist_runtime_state.
        return surfaced if surfaced is not None else rid

    # -- the agent-run ledger write-through (ADR Phase C) ------------------- #
    def persist_agent_run(
        self,
        tenant_id: str,
        run_key: str,
        agent_id: str,
        status: str,
        *,
        inputs: Optional[Mapping[str, Any]] = None,
        result: Optional[Mapping[str, Any]] = None,
        cost: Optional[Mapping[str, Any]] = None,
    ) -> Optional[str]:
        """Write-through the agent_runs HEADER row INTO agent_runs (ADR Phase C / OQ6).
        tenant_id EXPLICIT -- the SAME rule as the rest of the writer. Mirrors
        persist_runtime_state exactly: same adapter, same bind (is_local=True), same
        idempotency, same degrade-never.

        Idempotent on agent_run_id(tenant_id, run_key): the kicker writes the row at
        kickoff (status='running') and the SAME logical run UPSERTs at completion
        (ON CONFLICT (id) DO UPDATE -- status/result/cost/ended_at refreshed). A
        terminal status stamps ended_at = now(); a non-terminal one leaves it NULL.

        Fail-closed: a cross-tenant tenant_id (vs the bound claim) raises
        TenantDataDenied('cross_tenant') from the adapter before the DB is touched.
        inputs/result/cost are jsonb; _safe_meta strips any key-shaped field (the
        runtime guarantees them credential-free, belt-and-braces here). Returns the
        (stable) run id -- the public run_id the dashboard polls."""
        tid = _coerce_tenant(tenant_id)
        rid = agent_run_id(tid, run_key)
        status_norm = (status or "running").strip() or "running"
        terminal = status_norm in ("completed", "failed", "refused", "budget_exceeded")
        session = self._factory()
        self._bind(session, tid)
        # agent_runs shape (migration ...20260617000001): id, tenant_id, agent_id,
        # status, inputs, result, cost, started_at default, ended_at. We set the
        # deterministic id explicitly so a re-persist UPSERTs; ended_at is now() on a
        # terminal status, else left to its column default (NULL) on first insert and
        # untouched (kept) on a non-terminal update.
        sql = (
            "INSERT INTO " + _AGENT_RUNS_TABLE
            + " (id, tenant_id, agent_id, status, inputs, result, cost, ended_at) "
            "VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, "
            + ("now()" if terminal else "NULL")
            + ") "
            "ON CONFLICT (id) DO UPDATE SET "
            "status = EXCLUDED.status, "
            "result = EXCLUDED.result, "
            "cost = EXCLUDED.cost, "
            "ended_at = " + ("now()" if terminal else "agent_runs.ended_at") + " "
            "RETURNING id"
        )
        params = [
            rid,
            tid,
            str(agent_id),
            status_norm,
            json.dumps(_safe_meta(inputs), ensure_ascii=True),
            json.dumps(_safe_meta(result), ensure_ascii=True),
            json.dumps(_safe_meta(cost), ensure_ascii=True),
        ]
        out = self._adapter.write(session, tid, sql, params)
        surfaced = _first_id(out)
        return surfaced if surfaced is not None else rid

    def persist_agent_step(
        self,
        tenant_id: str,
        run_key: str,
        step_index: int,
        kind: str,
        *,
        content: Optional[Mapping[str, Any]] = None,
        tool: Optional[str] = None,
        tool_io: Optional[Mapping[str, Any]] = None,
    ) -> Optional[str]:
        """Write-through ONE agent_steps row INTO agent_steps (ADR Phase C / OQ6).
        tenant_id EXPLICIT. Mirrors persist_runtime_state: same adapter, same bind,
        same idempotency, same degrade-never. The step's tenant_id is DENORMALIZED
        (the migration isolates a step by its OWN tenant_id, not only via the run FK),
        so the bound claim == the step tenant_id == the run tenant_id.

        run_key is the SAME key the header used; the step's run_id FK is
        agent_run_id(tenant_id, run_key) (resolved here, NOT passed, so a caller can
        never point a step at a foreign run). Fail-closed: an unknown step kind ->
        ValueError (a typo must not silently widen what persists, mirroring the runtime
        scope guard); a cross-tenant tenant_id -> TenantDataDenied('cross_tenant')
        before the DB. Idempotent on agent_step_id(tenant_id, run_key, step_index).
        Returns the (stable) step id."""
        tid = _coerce_tenant(tenant_id)
        kind_norm = (kind or "").strip().lower()
        if kind_norm not in VALID_STEP_KINDS:
            raise ValueError(
                "invalid agent step kind %r (expected one of %s)"
                % (kind, ", ".join(VALID_STEP_KINDS))
            )
        sid = agent_step_id(tid, run_key, step_index)
        run_fk = agent_run_id(tid, run_key)
        session = self._factory()
        self._bind(session, tid)
        # agent_steps shape (migration ...20260617000001): id, run_id, tenant_id,
        # step_index, kind, content, tool, tool_io, created_at default. Deterministic
        # id set explicitly so a re-persist UPSERTs.
        sql = (
            "INSERT INTO " + _AGENT_STEPS_TABLE
            + " (id, run_id, tenant_id, step_index, kind, content, tool, tool_io) "
            "VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb) "
            "ON CONFLICT (id) DO UPDATE SET "
            "content = EXCLUDED.content, "
            "tool = EXCLUDED.tool, "
            "tool_io = EXCLUDED.tool_io "
            "RETURNING id"
        )
        params = [
            sid,
            run_fk,
            tid,
            int(step_index),
            kind_norm,
            json.dumps(_safe_meta(content), ensure_ascii=True),
            (str(tool) if tool else None),
            json.dumps(_safe_meta(tool_io), ensure_ascii=True),
        ]
        out = self._adapter.write(session, tid, sql, params)
        surfaced = _first_id(out)
        return surfaced if surfaced is not None else sid

    # -- internal ----------------------------------------------------------- #
    def _bind(self, session: DbSession, tenant_id: str) -> None:
        """Bind the verified-claim tenant onto the session so RLS applies on a
        pooled connection (spec A.5). Reuses adapter.bind_session_tenant, which emits
        set_config('request.jwt.claims', {"tenant_id": tid}, is_local=True). The
        claim value is the SAME tenant_id the subsequent write asserts, so the bind
        and the write agree (and the adapter's mirror passes)."""
        self._adapter.bind_session_tenant(session, {"tenant": tenant_id})


class LocalOnlyWriter:
    """Degrade-never no-op writer (spec c). Returned by make_runtime_sync_writer when
    NO session factory is configured (no central creds). Every persist_* is a no-op
    that returns None and NEVER raises / NEVER touches a session -- so a run proceeds
    LOCAL-ONLY (persisted=False) and is never blocked by a missing data plane.

    Satisfies the same shape as RuntimeSyncWriter (and run_capability.DbWriter), so
    callers wire it identically; the central simply never receives a write."""

    def persist_artifact(
        self,
        tenant_id: str,
        capability: str,
        kind: str,
        artifact: str,
        meta: Mapping[str, Any],
    ) -> Optional[str]:
        return None

    def read_artifact(
        self, tenant_id: str, record_id: str
    ) -> Optional[Dict[str, Any]]:
        """Degrade-never no-op: no central data plane -> no row to read -> None (the upload
        endpoint then surfaces a clean 'not found / no data plane', never a crash)."""
        return None

    def update_artifact_payload(
        self, tenant_id: str, record_id: str, payload: Mapping[str, Any]
    ) -> bool:
        """Degrade-never no-op: no central data plane -> nothing to update -> False."""
        return False

    def persist_runtime_state(
        self,
        tenant_id: str,
        scope: str,
        key: str,
        state: Mapping[str, Any],
    ) -> Optional[str]:
        return None

    def persist_memory(
        self,
        tenant_id: str,
        namespace: str,
        key: str,
        text: str,
        embedding: Optional[Sequence[float]] = None,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Optional[str]:
        """Degrade-never no-op (spec 6.3 step 6): returns None, NEVER raises, NEVER
        touches a session NOR an embedder -- so a run with no central data plane
        proceeds local-only (persisted=False), never blocked by a missing surface.
        Does NOT embed `text` (no FakeEmbedder import) so the no-op holds even when
        the optional cexai[memory] extra is absent."""
        return None

    def persist_agent_run(
        self,
        tenant_id: str,
        run_key: str,
        agent_id: str,
        status: str,
        *,
        inputs: Optional[Mapping[str, Any]] = None,
        result: Optional[Mapping[str, Any]] = None,
        cost: Optional[Mapping[str, Any]] = None,
    ) -> Optional[str]:
        """Degrade-never no-op (ADR Phase C): returns None, NEVER raises, NEVER touches
        a session -- so a multi-step agent run with no central data plane proceeds
        local-only (the run still completes; persistence skipped). NEVER validates
        status either (a no-op writer never gates)."""
        return None

    def persist_agent_step(
        self,
        tenant_id: str,
        run_key: str,
        step_index: int,
        kind: str,
        *,
        content: Optional[Mapping[str, Any]] = None,
        tool: Optional[str] = None,
        tool_io: Optional[Mapping[str, Any]] = None,
    ) -> Optional[str]:
        """Degrade-never no-op (ADR Phase C): returns None, NEVER raises, NEVER touches
        a session. A step kind typo does NOT raise here (the no-op writer never gates) --
        the validating path is the real RuntimeSyncWriter; local-only just skips the
        write so the loop is never blocked by a missing surface."""
        return None


def make_runtime_sync_writer(
    session_factory: Optional[Callable[[], DbSession]],
    *,
    adapter: Optional[SupabaseDataAdapter] = None,
):
    """Construct the runtime->central writer, degrading to LOCAL-ONLY when no central
    data plane is configured (spec c -- degrade-never).

    session_factory None -> LocalOnlyWriter (no creds / no pooled connection: the run
    proceeds local-only, persisted=False, NEVER blocked). A real zero-arg factory ->
    RuntimeSyncWriter over the audited adapter. The glue owns adapter construction so
    callers never import the package directly (single seam = single import line)."""
    if session_factory is None:
        return LocalOnlyWriter()
    return RuntimeSyncWriter(session_factory, adapter=adapter)


# --------------------------------------------------------------------------- #
# small helpers                                                               #
# --------------------------------------------------------------------------- #
def _safe_meta(meta: Mapping[str, Any]) -> dict:
    """Return a JSON-safe shallow copy of meta, dropping any key-shaped field as a
    belt-and-braces guard (run_capability already guarantees meta is credential-free,
    but the persistence layer refuses to write a secret even if a future caller slips
    one in)."""
    out: dict = {}
    blocked = {"api_key", "credential", "secret", "key", "token", "password"}
    if not meta:
        return out
    for k, v in dict(meta).items():
        if str(k).lower() in blocked:
            continue
        out[k] = v
    return out


def _vector_literal(vec: Sequence[float]) -> str:
    """Render a float vector as the pgvector TEXT literal form ``[f1,f2,...]`` (spec
    6.3 step 4). pgvector accepts a string cast ``::vector`` -- the writer binds this
    string as a normal parameter (never string-concatenated into SQL), so there is no
    injection surface. repr(float) keeps full precision deterministically; the cast
    in the INSERT (``%s::vector``) does the parse on the DB side."""
    return "[" + ",".join(repr(float(v)) for v in vec) + "]"


def _first_id(result: Any) -> Optional[str]:
    """Best-effort extraction of a RETURNING id from a driver-native result.

    The adapter does not interpret the result (it returns the cursor/rows as the
    driver hands them back), so this stays liberal: it accepts a cursor with
    fetchone(), a list/tuple of rows, a single row, or a mapping with an 'id' key, and
    returns the id as a string or None. A None result (offline fake that returns the
    forwarded (sql, params) tuple) yields None -- callers treat None as 'not surfaced'
    and either fall back to the deterministic id (runtime) or report persisted=False."""
    if result is None:
        return None
    # A cursor exposing fetchone() (psycopg/asyncpg style).
    fetchone = getattr(result, "fetchone", None)
    if callable(fetchone):
        try:
            row = fetchone()
        except Exception:
            row = None
        return _id_from_row(row)
    # A sequence of rows.
    if isinstance(result, (list, tuple)):
        if not result:
            return None
        # The adapter's FakeDbSession.execute returns (sql, params) -- NOT a row of
        # data. Distinguish: a real row is a 1-tuple/mapping with the id; the fake's
        # 2-tuple is (sql:str, params). Treat a leading str as 'no id surfaced'.
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
        # A (sql, params) fake tuple has a str first element -> not an id.
        if isinstance(row[0], str) and len(row) == 2:
            return None
        return str(row[0])
    return str(row)


def _first_row(result: Any) -> Any:
    """Extract the FIRST row from a driver-native query result (cursor.fetchone / a sequence /
    a single row), or None. Mirrors _first_id's liberal shape handling but returns the ROW. The
    offline fake's (sql, params) echo (a 2-tuple, leading str) is treated as 'no row'."""
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
    return result


def _first_payload(result: Any) -> Optional[Dict[str, Any]]:
    """Extract + parse the ``payload`` column (a dict, or a JSON string/bytes to parse) from a
    query result. Returns the dict, or None when no row / unparseable / not a dict. TOTAL."""
    row = _first_row(result)
    if row is None:
        return None
    if isinstance(row, Mapping):
        val: Any = row.get("payload")
    elif isinstance(row, (list, tuple)):
        val = row[0] if row else None
    else:
        val = row
    if isinstance(val, dict):
        return val
    if isinstance(val, (bytes, bytearray)):
        try:
            val = val.decode("utf-8")
        except Exception:
            return None
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
        except Exception:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None
