# -*- coding: ascii -*-
"""Async agent-run plane for the dashboard API (ADR adr_agents_sdk_dashboard, Phase C).

The ASYNC contract Phase C adds over the synchronous capability path: a multi-step agent run
is no longer instantaneous (minutes, many steps), so POST /agent/run returns a ``run_id``
immediately and the run executes in the BACKGROUND; the dashboard polls status + streams steps.

This module owns the three pieces that wire that contract WITHOUT changing the security spine:
  1. RunRegistry  -- a per-PROCESS, TENANT-SCOPED, bounded store of in-flight + recent runs.
                     It is the LIVE view of a run (authoritative while it executes in this
                     process); the tenant DB (agent_runs/agent_steps) is the durable system of
                     record (written by the loop's adapter writer). Reads ALWAYS check the
                     run's tenant_id against the verified caller's tenant -- a run_id from
                     another tenant resolves to None (404), never another tenant's transcript.
  2. start_agent_run -- kicks the multi-step loop on a worker THREAD (the loop is synchronous
                     Python; a thread keeps the request non-blocking). It records each step into
                     the registry AND persists it via the injected DbWriter (the audited adapter
                     -> agent_runs/agent_steps), so the run is visible both in-process (live) and
                     in the tenant DB (durable). The run_id is the deterministic agent_run_id, so
                     the in-process handle and the DB row id are the SAME value.
  3. event streaming -- GET /agent/run/{id}/events as SSE (OQ3) over the registry's growing step
                     list, with a poll fallback shape (GET /agent/run/{id} returns the full
                     status+steps snapshot any client can poll).

THE #1 RULE IS UNCHANGED: tenant_id is ONLY the verified JWT claim. start_agent_run is handed
the verified tenant_id (the endpoint derives it); every read re-checks the run's tenant_id
against the caller's. A run_id is NOT a capability -- holding one does not grant cross-tenant
read (the tenant check is independent of the id).

DEGRADE-NEVER: with no data plane the loop still runs (persistence skipped); the registry is
always populated so status/events work local-only. The registry is bounded (LRU-evicted) so a
long-lived process cannot leak memory.

ASCII-only per .claude/rules/ascii-code-rule.md. Fully type-hinted. No DB/secret at import.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional

__all__ = [
    "RunRegistry",
    "RunRecord",
    "get_registry",
    "start_agent_run",
]

# Bound the per-process registry so a long-lived server cannot grow without limit. Oldest
# runs are evicted (their durable record remains in the tenant DB; only the live view is LRU).
_MAX_RUNS = 256

# How long an SSE stream waits between polls of the (in-memory) step list, and its overall
# wall-clock cap, so a stream never hangs forever on a stuck run. Both are conservative.
_SSE_POLL_SECONDS = 0.25
_SSE_MAX_SECONDS = 120.0


@dataclass
class RunRecord:
    """The LIVE, in-process view of one agent run. tenant_id is the OWNER -- every read checks
    it against the verified caller (a foreign run_id -> None). The api_key is NEVER here."""

    run_id: str
    tenant_id: str
    agent_id: str
    status: str = "running"                       # running|completed|failed|refused|budget_exceeded
    agent_name: str = ""
    kind: str = ""
    pillar: str = ""
    nucleus: str = ""
    artifact: str = ""
    score: float = 0.0
    passed: bool = False
    model_used: str = ""
    record_id: Optional[str] = None               # the agent_runs row id (== run_id when persisted)
    persisted: bool = False
    steps: int = 0
    trace: str = ""
    errors: List[str] = field(default_factory=list)
    steps_log: List[Dict[str, Any]] = field(default_factory=list)
    cost: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    _done: bool = False

    def snapshot(self) -> Dict[str, Any]:
        """A JSON-safe, credential-free snapshot for GET /agent/run/{id} (the poll shape).

        This is the AgentRunEvent/AgentRunDetail payload the frontend consumes. No secret can
        appear (the fields are run metadata + step content, never a credential)."""
        return {
            "run_id": self.run_id,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status,
            "kind": self.kind,
            "pillar": self.pillar,
            "nucleus": self.nucleus,
            "artifact": self.artifact,
            "score": self.score,
            "passed": self.passed,
            "model_used": self.model_used,
            "record_id": self.record_id,
            "persisted": self.persisted,
            "steps": self.steps,
            "trace": self.trace,
            "errors": list(self.errors),
            "steps_log": list(self.steps_log),
            "cost": dict(self.cost),
            "done": self._done,
        }


class RunRegistry:
    """A thread-safe, bounded, tenant-scoped registry of agent runs (the LIVE view).

    Every accessor takes the caller's VERIFIED tenant_id and refuses to return a run owned by a
    different tenant (None -> the endpoint maps to 404). This is the in-process tenant boundary
    that mirrors the DB's RLS: a run_id alone never crosses tenants. Bounded LRU so memory is
    capped; the durable record lives in the tenant DB regardless."""

    def __init__(self, max_runs: int = _MAX_RUNS) -> None:
        self._runs: "OrderedDict[str, RunRecord]" = OrderedDict()
        self._lock = threading.Lock()
        self._max = max_runs

    def create(self, run_id: str, tenant_id: str, agent_id: str) -> RunRecord:
        """Register a new run (status='running'). LRU-evicts the oldest if at capacity."""
        rec = RunRecord(run_id=run_id, tenant_id=tenant_id, agent_id=agent_id)
        with self._lock:
            self._runs[run_id] = rec
            self._runs.move_to_end(run_id)
            while len(self._runs) > self._max:
                self._runs.popitem(last=False)
        return rec

    def get(self, run_id: str, tenant_id: str) -> Optional[RunRecord]:
        """Return the run IFF it exists AND is owned by ``tenant_id`` (the verified claim).

        A run owned by another tenant -> None (the endpoint returns 404, never another tenant's
        data). This is the in-process analogue of the RLS tenant boundary."""
        with self._lock:
            rec = self._runs.get(run_id)
            if rec is None:
                return None
            if rec.tenant_id != (tenant_id or "").strip():
                return None  # cross-tenant: invisible (fail-closed)
            return rec

    def update_from_step(self, run_id: str, step_view: Mapping[str, Any]) -> None:
        """Append one persisted step's view to the run's live ledger (called by the loop)."""
        with self._lock:
            rec = self._runs.get(run_id)
            if rec is None:
                return
            rec.steps_log.append(dict(step_view))
            rec.steps = len(rec.steps_log)

    def finalize(self, run_id: str, result_snapshot: Mapping[str, Any]) -> None:
        """Stamp the terminal result onto the run (status/artifact/score/...)."""
        with self._lock:
            rec = self._runs.get(run_id)
            if rec is None:
                return
            for key in (
                "status", "agent_name", "kind", "pillar", "nucleus", "artifact", "score",
                "passed", "model_used", "record_id", "persisted", "trace", "cost",
            ):
                if key in result_snapshot:
                    setattr(rec, key, result_snapshot[key])
            if result_snapshot.get("steps_log"):
                rec.steps_log = list(result_snapshot["steps_log"])
                rec.steps = len(rec.steps_log)
            if result_snapshot.get("errors"):
                rec.errors = list(result_snapshot["errors"])
            rec._done = True

    def fail(self, run_id: str, reason: str) -> None:
        """Mark a run failed/refused (an exception escaped the loop thread)."""
        with self._lock:
            rec = self._runs.get(run_id)
            if rec is None:
                return
            rec.status = "failed"
            rec.errors.append(reason)
            rec._done = True


# A single process-wide registry. The dashboard is one ASGI app; this is its run store.
_REGISTRY: Optional[RunRegistry] = None
_REGISTRY_LOCK = threading.Lock()


def get_registry() -> RunRegistry:
    """The process-wide RunRegistry (lazily constructed, thread-safe singleton)."""
    global _REGISTRY
    if _REGISTRY is None:
        with _REGISTRY_LOCK:
            if _REGISTRY is None:
                _REGISTRY = RunRegistry()
    return _REGISTRY


def start_agent_run(
    *,
    tenant_id: str,
    agent_id: str,
    inputs: Mapping[str, Any],
    credential: Any,
    db: Any,
    options: Optional[Mapping[str, Any]],
    runtime: Any,
    run_key: str,
    background: bool = True,
) -> str:
    """Kick the multi-step loop and return its run_id IMMEDIATELY (the async contract).

    tenant_id MUST be the verified JWT claim (the endpoint derives it). ``runtime`` is the
    cex_agent_loop module (injected so the endpoint resolves it lazily + tests fake it).
    ``run_key`` is a uuid4 hex the endpoint minted; the run_id is the deterministic
    agent_run_id over (tenant_id, run_key), so the registry handle == the DB row id.

    The loop runs on a worker THREAD (background=True) so the POST returns at once; the registry
    is populated live as steps persist. background=False runs it inline (used by tests for a
    deterministic, fully-resolved run). A loop exception is captured onto the run (status=failed)
    -- it never crashes the request thread.

    The DbWriter ``db`` is wrapped so each persisted step ALSO updates the in-process registry
    (the live view), giving the SSE/poll endpoints real progress even before the DB confirms.
    """
    registry = get_registry()
    run_id = _resolve_run_id(tenant_id, run_key)
    registry.create(run_id, tenant_id, agent_id)

    wrapped_db = _RegistryTeeWriter(db, registry, run_id) if db is not None else None

    def _execute() -> None:
        try:
            result = runtime.run_agent_multistep(
                tenant_id,
                agent_id,
                inputs,
                credential,
                db=wrapped_db,
                options=options,
                run_key=run_key,
            )
            registry.finalize(run_id, _result_snapshot(result))
        except runtime.CapabilityRefused as exc:
            # A deny inside the thread (e.g. a mid-run frozen/credential issue) -> mark refused.
            registry.fail(run_id, "refused: %s" % getattr(exc, "reason", "capability_refused"))
        except Exception as exc:  # any loop failure is captured onto the run, never raised here.
            registry.fail(run_id, "loop_error: %s: %s" % (type(exc).__name__, exc))

    if background:
        thread = threading.Thread(target=_execute, name="agent-run-%s" % run_id[:8], daemon=True)
        thread.start()
    else:
        _execute()
    return run_id


def _resolve_run_id(tenant_id: str, run_key: str) -> str:
    """The deterministic run_id (== the agent_runs row id). Resolved via cex_runtime_sync so it
    EXACTLY matches the persisted row; a degraded env synthesizes the same uuid5 contract."""
    try:
        import sys
        from pathlib import Path

        tools = str(Path(__file__).resolve().parents[2] / "_tools")
        if tools not in sys.path:
            sys.path.insert(0, tools)
        import cex_runtime_sync  # type: ignore[import]

        return cex_runtime_sync.agent_run_id(tenant_id, run_key)
    except Exception:
        import uuid

        ns = uuid.UUID("a4f3c2d1-0000-5000-8000-6167656e7472")
        return str(uuid.uuid5(ns, "%s|%s" % (tenant_id, run_key)))


def _result_snapshot(result: Any) -> Dict[str, Any]:
    """Project a MultiStepResult (dataclass) to the terminal snapshot for the registry. No
    credential field exists on the result, but we read an explicit allowlist regardless."""
    import dataclasses

    if dataclasses.is_dataclass(result) and not isinstance(result, type):
        data = dataclasses.asdict(result)
    elif isinstance(result, Mapping):
        data = dict(result)
    else:
        data = dict(getattr(result, "__dict__", {}))
    keys = (
        "status", "agent_name", "kind", "pillar", "nucleus", "artifact", "score", "passed",
        "model_used", "record_id", "persisted", "trace", "errors", "steps_log", "cost",
    )
    return {k: data.get(k) for k in keys if k in data}


class _RegistryTeeWriter:
    """A DbWriter wrapper that TEES every persisted step into the in-process registry (the live
    view) AND forwards to the real audited writer (the durable tenant DB). So a step appears in
    the SSE/poll stream the moment the loop records it, even before/without the DB.

    It forwards EVERY method of the wrapped writer (persist_artifact/persist_runtime_state/
    persist_agent_run/persist_agent_step/persist_memory) verbatim; it only ADDITIONALLY mirrors
    persist_agent_step into the registry. Degrade-never: a wrapped writer missing a method is
    simply not called for it (getattr-guarded)."""

    def __init__(self, inner: Any, registry: RunRegistry, run_id: str) -> None:
        self._inner = inner
        self._registry = registry
        self._run_id = run_id

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
        # Mirror into the live registry FIRST (so the stream shows progress even if the DB is
        # local-only / slow). The view is credential-free by construction.
        self._registry.update_from_step(
            self._run_id,
            {
                "index": step_index,
                "kind": kind,
                "content": dict(content or {}),
                "tool": tool,
                "tool_io": dict(tool_io or {}),
            },
        )
        inner = getattr(self._inner, "persist_agent_step", None)
        if callable(inner):
            return inner(
                tenant_id, run_key, step_index, kind,
                content=content, tool=tool, tool_io=tool_io,
            )
        return None

    def persist_agent_run(self, *args: Any, **kwargs: Any) -> Optional[str]:
        inner = getattr(self._inner, "persist_agent_run", None)
        return inner(*args, **kwargs) if callable(inner) else None

    def persist_artifact(self, *args: Any, **kwargs: Any) -> Optional[str]:
        inner = getattr(self._inner, "persist_artifact", None)
        return inner(*args, **kwargs) if callable(inner) else None

    def persist_runtime_state(self, *args: Any, **kwargs: Any) -> Optional[str]:
        inner = getattr(self._inner, "persist_runtime_state", None)
        return inner(*args, **kwargs) if callable(inner) else None

    def persist_memory(self, *args: Any, **kwargs: Any) -> Optional[str]:
        inner = getattr(self._inner, "persist_memory", None)
        return inner(*args, **kwargs) if callable(inner) else None


def stream_run_events(
    registry: RunRegistry,
    run_id: str,
    tenant_id: str,
    *,
    poll_seconds: float = _SSE_POLL_SECONDS,
    max_seconds: float = _SSE_MAX_SECONDS,
) -> Any:
    """A generator of SSE ``data:`` frames for GET /agent/run/{id}/events (OQ3 SSE transport).

    Yields one SSE event per NEW step as the run progresses, then a terminal ``done`` event when
    the run finalizes (or a ``timeout`` event if it stalls past max_seconds). TENANT-SCOPED: it
    re-resolves the run under ``tenant_id`` each poll, so a run that is not the caller's yields a
    single ``not_found`` event and stops (never another tenant's stream).

    Each frame is ``event: <type>\\ndata: <json>\\n\\n`` -- the SSE wire format. The poll
    fallback (GET /agent/run/{id}) returns the SAME snapshot for clients that cannot hold an SSE
    connection."""
    import json

    deadline = time.time() + max_seconds
    emitted = 0
    # Resolve once for tenant ownership; if absent, emit not_found and stop.
    rec = registry.get(run_id, tenant_id)
    if rec is None:
        yield "event: not_found\ndata: %s\n\n" % json.dumps({"run_id": run_id})
        return
    while True:
        rec = registry.get(run_id, tenant_id)
        if rec is None:
            yield "event: not_found\ndata: %s\n\n" % json.dumps({"run_id": run_id})
            return
        snap = rec.snapshot()
        steps = snap.get("steps_log", [])
        # Emit any steps not yet streamed.
        while emitted < len(steps):
            yield "event: step\ndata: %s\n\n" % json.dumps(steps[emitted])
            emitted += 1
        if snap.get("done"):
            yield "event: done\ndata: %s\n\n" % json.dumps(snap)
            return
        if time.time() >= deadline:
            yield "event: timeout\ndata: %s\n\n" % json.dumps({"run_id": run_id, "steps": emitted})
            return
        time.sleep(poll_seconds)
