#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI multi-step agent loop -- run_agent_multistep (ADR adr_agents_sdk_dashboard, Phase C).

THE multi-step plan/act/observe LOOP -- the one genuinely-new primitive Phase C adds ON TOP
of Phase B's proven single-step spine (cex_run_agent.run_agent). It is "real agents above
cards": a tool-using, stateful, budgeted loop that COMPOSES the dormant cex_sdk primitives
(Toolkit / Workflow / Session) rather than importing a new agent framework (ADR D3).

WHAT THIS ADDS over Phase B (the gap Phase C closes): run_agent runs exactly ONE chat()
(CEXAgent.build), surfaces the declared tools as CONTEXT ONLY, and never executes a tool.
run_agent_multistep drives a real loop:

  PLAN     -> one CEXAgent.build step decides the approach (the agent contract is the system
              prompt, exactly as Phase B's ASSEMBLE loader builds it -- REUSED verbatim).
  ACT      -> the model (a CEXAgent.build step) proposes the next action; a Router dispatches
              it: a tool name -> Toolkit.execute (the tool seam); otherwise -> a produce step.
  OBSERVE  -> the tool/produce result is folded back into the Session state + history; a
              Condition checks the F7 gate (the produced artifact passed) to STOP.
  (repeat ACT/OBSERVE inside a cex_sdk.workflow.Loop until the gate passes OR the budget is
   exhausted.)

COMPOSITION (ADR D3 -- compose the dormant SDK, do NOT fork):
  * cex_sdk.tools.Toolkit       -- get_tool_schemas() surfaces the agent's declared tools to
                                   the model; execute(name, **args) is the tool-dispatch seam.
                                   The toolkit is SCOPED by the agent_card / role_assignment
                                   tool list (the agent's grants). Tool IMPLEMENTATIONS are an
                                   injected resolver (default: a safe 'unbound' stub that
                                   records the call) -- real/live tools (MCP, browser) are the
                                   founder-gated seam, not faked here.
  * cex_sdk.workflow            -- Loop = the act/observe cycle; Condition = the F7 gate (stop
                                   when the artifact passes); Router = tool dispatch vs produce;
                                   Step wraps each executor. StepInput/StepOutput carry the
                                   session_state between steps.
  * cex_sdk.session.Session     -- holds the run's state + message history, RE-HOMED into the
                                   tenant agent_runs/agent_steps plane via the audited adapter
                                   (the writer persists each step; the local Session JSON is
                                   NOT the system of record -- the tenant DB is).

BUDGET (OQ4 -- enforce a team_charter-style ceiling IN the loop): max_steps / max_tokens
(from options['budget'] or a bare options['max_steps']). The loop STOPS and REFUSES (status
'budget_exceeded') the moment a ceiling is crossed -- it never silently runs past the budget.
A 0/non-positive ceiling refuses BEFORE any LLM call (the SAME _budget_guard Phase B uses).

HITL (OQ8 -- irreversible / verb=deploy tools gate through governance): before EXECUTING a
tool flagged irreversible (or when the agent's verb is 'deploy'), the loop emits a pending
approval via the governance FileApprovalGate (emit-and-defer: it RECORDS the pending request
and SKIPS the tool -- it does NOT block on await_decision). The step is persisted with the
approval id so the dashboard surfaces it in the HITL queue. NON-BLOCKING for now (the ADR's
emit-and-defer posture, mirroring the ACR P3 graduated-HITL mechanism).

DEGENERATE CASE (DO NOT regress Phase B): an agent with NO declared tools AND a budget that
allows >=1 step runs EXACTLY the Phase B path -- ONE CEXAgent.build, no act/observe loop, the
SAME AgentRunResult (steps==1). run_agent_multistep DELEGATES to run_agent for that case, so
the 1-step/0-tool run is byte-equivalent.

DEGRADE-NEVER: no DbWriter / a LocalOnlyWriter -> the loop still completes, step persistence
is skipped (the run is local-only). No governance package -> the HITL gate degrades to a
recorded-but-inert pending marker (the tool is still skipped; nothing crashes).

HARD RULES (per the task contract + .claude/rules/ascii-code-rule.md):
  * ASCII-only; fully type-hinted; FAIL-CLOSED (every deny raises CapabilityRefused).
  * NO concrete DB driver and NO LLM key imported at MODULE IMPORT. The DbWriter + Credential
    are INJECTED; cex_sdk + governance are imported LAZILY inside the loop (so a degraded env
    still imports this module). tenant_id is ALWAYS explicit.

Spec: _docs/compiled/adr_agents_sdk_dashboard.md (Phase C, Layer 2 RUNTIME).
Sibling of: _tools/cex_run_agent.py (Phase B single-step -- REUSED for the degenerate case +
the ASSEMBLE loader + the budget guard + the credential/persist spine). Persists via:
_tools/cex_runtime_sync.py (persist_agent_run + persist_agent_step -- the C4 adapter mirror).
"""

from __future__ import annotations

import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

# --------------------------------------------------------------------------- #
# REUSE the Phase B sibling VERBATIM (the #1 rule: do NOT fork the rails). Phase B already
# reuses run_capability's spine (Credential / CapabilityRefused / DbWriter + the
# credential/enabled/frozen helpers); we pull the SAME objects + the ASSEMBLE loader + the
# budget guard from it, so Phase C shares ONE spine with Phase B + the capability runtime.
# --------------------------------------------------------------------------- #
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_run_agent as _ra  # type: ignore[import]

Credential = _ra.Credential
CapabilityRefused = _ra.CapabilityRefused
DbWriter = _ra.DbWriter
AgentRunResult = _ra.AgentRunResult
MODE_BYO_API_KEY = _ra.MODE_BYO_API_KEY
MODE_NATIVE_LOCAL = _ra.MODE_NATIVE_LOCAL
MODE_PLATFORM = _ra.MODE_PLATFORM

# The repo root (this file lives in <root>/_tools).
_REPO_ROOT = Path(__file__).resolve().parents[1]

# The act/observe loop hard ceiling -- a safety cap so an absent budget can NEVER spin
# forever. The OQ4 budget (max_steps) tightens this; this is the backstop. PLAN counts as
# step 0, so the loop body runs at most (this - 1) act/observe pairs by default.
_DEFAULT_MAX_STEPS = 8


# --------------------------------------------------------------------------- #
# AgentStep -- one row of the in-memory step ledger (persisted to agent_steps).
# Mirrors the agent_steps table (ADR Phase C / agent_grounding_record seed): kind in
# {plan|act|observe|tool}, content (the step payload), tool + tool_io for tool steps.
# --------------------------------------------------------------------------- #
@dataclass
class AgentStep:
    """One plan/act/observe/tool step. Persisted 1:1 into agent_steps; surfaced in the
    AgentRunResult.steps_log + the GET /agent/run/{id}/events stream. NEVER carries a secret."""

    index: int
    kind: str                                    # plan | act | observe | tool
    content: Dict[str, Any] = field(default_factory=dict)
    tool: Optional[str] = None                   # tool name (tool steps only)
    tool_io: Dict[str, Any] = field(default_factory=dict)  # {args, result} (tool steps)
    approval_id: Optional[str] = None            # HITL pending id (gated tool steps)


# --------------------------------------------------------------------------- #
# MultiStepResult -- the AgentRunResult shape + the run_id + the step ledger. Field parity
# with AgentRunResult is intentional (so _result_to_view serializes it unchanged); it ADDS
# run_id (the async handle) + steps_log (the live trace) + a cost dict (budget accounting).
# --------------------------------------------------------------------------- #
@dataclass
class MultiStepResult:
    """Outcome of one MULTI-step agent run. The api_key is NEVER present on this object.

    Mirrors AgentRunResult field-for-field (the dashboard _result_to_view allowlist projects
    the SAME credential-free fields) and ADDS: run_id (the public async handle == the
    deterministic agent_run_id), steps_log (the plan/act/observe/tool ledger), and cost (the
    OQ4 budget accounting: steps_used / max_steps / tokens_used / max_tokens).
    """

    tenant_id: str
    agent_id: str
    capability: str                              # the agent_id, echoed as the run "capability"
    kind: str
    pillar: str
    nucleus: str
    run_id: str = ""                             # the async handle (deterministic agent_run_id)
    agent_name: str = ""
    artifact: str = ""                           # the final produced artifact
    score: float = 0.0
    passed: bool = False
    status: str = "error"                        # completed|failed|refused|budget_exceeded|produced_unpersisted
    model_used: str = ""
    record_id: Optional[str] = None              # agent_runs row id (== run_id when persisted)
    persisted: bool = False
    steps: int = 0                               # total steps executed (>=1)
    trace: str = ""
    errors: List[str] = field(default_factory=list)
    steps_log: List[Dict[str, Any]] = field(default_factory=list)
    cost: Dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Budget (OQ4) -- a team_charter-style ceiling resolved from options.
# --------------------------------------------------------------------------- #
@dataclass
class _Budget:
    """The resolved per-run ceiling (OQ4). max_steps caps the plan+act/observe steps;
    max_tokens caps the cumulative model+tool char budget (a proxy for tokens, offline-safe).
    Either may be None (unbounded -> the _DEFAULT_MAX_STEPS backstop still applies to steps)."""

    max_steps: Optional[int] = None
    max_tokens: Optional[int] = None
    steps_used: int = 0
    tokens_used: int = 0
    steps_persisted: int = 0        # R-210: _persist_step calls that ACTUALLY reached the writer
    steps_persist_total: int = 0    # R-210: _persist_step calls attempted (success or not)

    def step_ceiling(self) -> int:
        """The effective step ceiling: the declared max_steps, else the safety backstop."""
        if isinstance(self.max_steps, int) and self.max_steps > 0:
            return min(self.max_steps, _DEFAULT_MAX_STEPS * 4)  # honor a higher explicit budget, capped
        return _DEFAULT_MAX_STEPS

    def would_exceed_steps(self) -> bool:
        """True iff taking ONE more step would cross the step ceiling."""
        return self.steps_used >= self.step_ceiling()

    def would_exceed_tokens(self, add: int) -> bool:
        """True iff adding ``add`` chars would cross the token ceiling (if declared)."""
        if not isinstance(self.max_tokens, int) or self.max_tokens <= 0:
            return False
        return (self.tokens_used + max(0, add)) > self.max_tokens

    def as_dict(self) -> Dict[str, Any]:
        """The cost accounting persisted into agent_runs.cost + surfaced on the result.

        R-210: `steps_persisted` / `steps_persist_total` make step-persistence failures
        VISIBLE here -- `_persist_step` used to swallow every exception with no return
        signal at all, so a caller (and this cost dict) could never tell whether some
        `agent_steps` rows silently failed to write. `steps_persisted < steps_persist_total`
        is the honest signal that at least one step never reached the writer."""
        return {
            "steps_used": self.steps_used,
            "max_steps": self.max_steps,
            "step_ceiling": self.step_ceiling(),
            "tokens_used": self.tokens_used,
            "max_tokens": self.max_tokens,
            "steps_persisted": self.steps_persisted,
            "steps_persist_total": self.steps_persist_total,
        }


def _resolve_budget(options: Optional[Mapping[str, Any]]) -> _Budget:
    """Resolve the OQ4 budget from options (a team_charter-style mapping or a bare max_steps).

    Precedence: options['budget'] (a mapping with max_steps/steps/max_tokens/tokens) wins;
    else a bare options['max_steps']. Absent -> an unbounded budget (the step backstop still
    caps it). PURE + TOTAL. A non-positive ceiling is NOT refused here (the loop's
    _ra._budget_guard does that BEFORE any LLM call, reusing Phase B's guard verbatim)."""
    if not options:
        return _Budget()
    budget = options.get("budget")
    if isinstance(budget, Mapping):
        return _Budget(
            max_steps=_as_pos_int(budget.get("max_steps", budget.get("steps"))),
            max_tokens=_as_pos_int(budget.get("max_tokens", budget.get("tokens"))),
        )
    return _Budget(max_steps=_as_pos_int(options.get("max_steps")))


def _as_pos_int(value: Any) -> Optional[int]:
    """Coerce a value to a positive int, or None (a non-number / <=0 / bool -> None)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, float):
        return int(value) if value > 0 else None
    return None


# --------------------------------------------------------------------------- #
# The toolkit seam (cex_sdk.tools.Toolkit) -- the agent's declared tools, scoped + executable.
# The agent's tools are NAMES (grants). We build a Toolkit of Functions wrapping a resolver:
# the default resolver is a SAFE 'unbound' stub that RECORDS the call (no live side effect);
# a real tool resolver (MCP / browser / db) is the founder-gated injected seam.
# --------------------------------------------------------------------------- #

# Tests / live wiring set cex_agent_loop.tool_resolver = fn to bind real tool implementations.
# Signature: tool_resolver(tool_name, args, *, tenant_id, agent_id) -> (result_str, meta_dict).
# None (default) -> the unbound stub (records the call, returns a 'not bound' note).
tool_resolver: Any = None


def _build_toolkit(tool_names: List[str], tenant_id: str, agent_id: str) -> Any:
    """Build a cex_sdk.tools.Toolkit over the agent's DECLARED tool names, DEGRADE-NEVER.

    Each declared tool becomes a cex_sdk Function whose entrypoint dispatches through the
    module-level tool_resolver (default: the unbound stub). So Toolkit.get_tool_schemas()
    surfaces the agent's grants to the model, and Toolkit.execute(name, **args) routes to the
    resolver. Returns None if cex_sdk is not importable (the loop then degrades to no tools).
    PURE w.r.t. tenant: the resolver closes over the explicit tenant_id (never ambient)."""
    try:
        from cex_sdk.tools.toolkit import Toolkit  # type: ignore[import]
        from cex_sdk.tools.function import Function  # type: ignore[import]
    except Exception:
        return None

    functions: List[Any] = []
    for name in tool_names:
        clean = str(name).strip()
        if not clean:
            continue
        functions.append(
            Function(
                name=clean,
                description="Agent-declared tool '%s' (grant). Args are a free-form object."
                % clean,
                parameters={"type": "object", "properties": {}},
                entrypoint=_make_tool_entrypoint(clean, tenant_id, agent_id),
            )
        )
    if not functions:
        return None
    try:
        return Toolkit(name="agent_tools", tools=functions, auto_register=False)
    except Exception:
        return None


def _make_tool_entrypoint(
    tool_name: str, tenant_id: str, agent_id: str
) -> Callable[..., str]:
    """Build the entrypoint a Toolkit Function calls -- routes to the resolver (or the stub).

    The entrypoint takes **args (the model's tool call) and returns a string (the observation).
    It NEVER raises (a tool error is returned as a JSON-ish note so the observe step records it
    rather than crashing the loop)."""

    def _entry(**args: Any) -> str:
        resolver = tool_resolver
        if resolver is None:
            return _unbound_tool_note(tool_name)
        try:
            result, _meta = resolver(tool_name, args, tenant_id=tenant_id, agent_id=agent_id)
            return str(result)
        except Exception as exc:  # a tool failure is an observation, not a loop crash.
            return "tool_error: %s: %s" % (type(exc).__name__, exc)

    return _entry


def _unbound_tool_note(tool_name: str) -> str:
    """The honest default observation for a declared-but-unbound tool (no live impl wired).

    The dashboard agent runtime does NOT ship live implementations for arbitrary agent-declared
    tool names (MCP / browser / db tools are the founder-gated seam). So a tool call against an
    unbound name returns this note -- the loop records the call (provenance) and OBSERVES the
    note, but no real side effect occurs. This keeps the loop honest + offline-testable."""
    return (
        "tool_unbound: '%s' is a declared grant with no live implementation in this runtime "
        "(bind a tool_resolver to enable it). No action taken." % tool_name
    )


# --------------------------------------------------------------------------- #
# HITL (OQ8) -- the irreversible/verb=deploy tool gate (emit-and-defer, NON-BLOCKING).
# --------------------------------------------------------------------------- #

# A tool whose name implies an irreversible/deploy effect gates through HITL. The dashboard /
# agent_card may also flag a tool irreversible explicitly via options['irreversible_tools'].
_IRREVERSIBLE_TOOL_HINTS = (
    "deploy", "publish", "release", "delete", "drop", "destroy", "send", "pay",
    "charge", "transfer", "shutdown", "terminate", "wire",
)

# R-200: a tool whose name implies a pure read/lookup effect is NEVER gated (narrows the
# fail-closed default below to genuinely-unrecognized tools, so ordinary read-only grants
# like web_search/retriever keep flowing without HITL -- an earlier fail-closed-EVERYTHING
# attempt was reverted for exactly this over-breadth / DoS risk).
_READ_ONLY_TOOL_HINTS = (
    "get", "list", "read", "search", "fetch", "query", "describe", "view",
    "retriev", "inspect", "show",
)


def _tool_needs_approval(
    tool_name: str,
    verb: str,
    options: Optional[Mapping[str, Any]],
) -> bool:
    """Decide whether a tool call must gate through HITL (OQ8).

    SECURITY INVARIANT (R-200): an unrecognized tool that is not clearly read-only must NOT
    execute unguarded -- WITHOUT gating ordinary read-only tools (web_search/retriever/etc.)
    into HITL. Order (first match wins):
      1. the agent's verb is 'deploy' (the whole run is a deploy)               -> GATE
      2. the tool name is in the operator-declared options['irreversible_tools'] -> GATE
      3. the tool name matches an irreversible hint token                       -> GATE
      4. the tool name matches a read-only hint token, OR is on the operator-
         declared options['safe_tools'] allowlist                               -> ALLOW
      5. else (unknown: neither read-only nor known-irreversible)               -> GATE

    Conservative-but-bounded: a false-positive gate only adds a (skipped) pending approval --
    it never executes a dangerous (or merely unrecognized) tool unguarded (fail-closed for the
    truly-unknown), while a declared or hinted read-only tool is never blocked (no DoS on the
    common case)."""
    if (verb or "").strip().lower() == "deploy":
        return True
    declared = options.get("irreversible_tools") if isinstance(options, Mapping) else None
    if isinstance(declared, (list, tuple)) and tool_name in {str(d) for d in declared}:
        return True
    low = (tool_name or "").lower()
    if any(hint in low for hint in _IRREVERSIBLE_TOOL_HINTS):
        return True
    safe_declared = options.get("safe_tools") if isinstance(options, Mapping) else None
    if isinstance(safe_declared, (list, tuple)) and tool_name in {str(s) for s in safe_declared}:
        return False
    if any(hint in low for hint in _READ_ONLY_TOOL_HINTS):
        return False
    return True


def _ensure_vendored_cexai_first() -> None:
    """Re-assert THIS repo's vendored ``cexai/`` at ``sys.path[0]`` (R-007/R-209
    ambient-pip-shadow guard; mirrors the identical guard in `_tools/cex_ingest_router.py`:
    ``sys.path.insert(0, str(_ROOT / "cexai"))``).

    A bare ``import cexai...`` can silently resolve to an unrelated AMBIENT pip-installed
    'cexai' package elsewhere on `sys.path` instead of this repo's own vendored copy -- the
    same landmine R-007 fixed for the distill offline_import_smoke gate. For a HITL-gated
    tool, that shadow degrades silently to "governance not installed" (the except branch
    below), meaning a real approval could silently NEVER reach the on-disk queue. Called
    right before the lazy governance import (never at module import -- this module must
    still import cleanly in a degraded env). Idempotent (dedupes any prior entry before
    re-inserting at index 0) and NEVER raises -- a `sys.path` mutation failure here must not
    break the (already best-effort) HITL emit path."""
    vendored = str(_REPO_ROOT / "cexai")
    try:
        while vendored in sys.path:
            sys.path.remove(vendored)
        sys.path.insert(0, vendored)
    except Exception:
        pass


def _emit_approval(
    tenant_id: str,
    agent_id: str,
    tool_name: str,
    options: Optional[Mapping[str, Any]],
) -> Optional[str]:
    """Emit a PENDING approval for an irreversible tool via the governance FileApprovalGate
    and RETURN its request id (emit-and-defer; ADR OQ8). NON-BLOCKING: this RECORDS the
    pending request and returns -- it NEVER calls await_decision (the tool is SKIPPED for
    now; the dashboard surfaces the pending id in the HITL queue, exactly as the ACR P3
    graduated-HITL mechanism emits-and-defers).

    DEGRADE-NEVER: if the governance package is STILL not importable after re-asserting the
    vendored `cexai` at `sys.path[0]` (R-209 -- e.g. a truly absent package, or a shadow that
    was already cached in `sys.modules` before this call), return a synthetic local pending
    id ('appr-local-...') so the step still records that an approval was REQUIRED -- the tool
    is still skipped; nothing crashes. The approvals dir is tenant-scoped under the central
    runtime so a tenant's queue is isolated."""
    try:
        _ensure_vendored_cexai_first()
        from cexai.governance.hitl import FileApprovalGate  # type: ignore[import]
    except Exception:
        return "appr-local-" + uuid.uuid4().hex[:12]
    try:
        approvals_dir = _approvals_dir(tenant_id, options)
        gate = FileApprovalGate(approvals_dir=approvals_dir)
        operation = "agent_tool:%s/%s/%s" % (tenant_id, agent_id, tool_name)
        request = gate.request(operation=operation, requester="agent_runtime:%s" % agent_id)
        return getattr(request, "request_id", None) or ("appr-" + uuid.uuid4().hex[:12])
    except Exception:
        # The gate must NEVER break the loop -- a failure to emit still skips the tool and
        # records a synthetic id so provenance is preserved.
        return "appr-local-" + uuid.uuid4().hex[:12]


def _approvals_dir(tenant_id: str, options: Optional[Mapping[str, Any]]) -> str:
    """The tenant-scoped approvals directory for the HITL queue (under the central runtime).

    An operator may override the root via options['approvals_dir']; else the default is
    .cexai/approvals/<tenant_id>/ so each tenant's pending approvals are isolated on disk."""
    override = options.get("approvals_dir") if isinstance(options, Mapping) else None
    if isinstance(override, str) and override.strip():
        base = Path(override.strip())
    else:
        base = _REPO_ROOT / ".cexai" / "approvals"
    return str(base / _safe_tenant_dir(tenant_id))


def _safe_tenant_dir(tenant_id: str) -> str:
    """A filesystem-safe tenant directory name (the uuid is already safe; belt-and-braces)."""
    return "".join(c for c in str(tenant_id) if c.isalnum() or c in "-_") or "unknown"


# --------------------------------------------------------------------------- #
# Session re-homing (cex_sdk.session.Session) -- the run's working state.
# --------------------------------------------------------------------------- #
def _new_session(run_key: str) -> Any:
    """Build a cex_sdk.session.Session for this run (state + history), or a tiny in-memory
    stand-in if cex_sdk is not importable. The Session is the working state DURING the loop;
    the system-of-record is the tenant agent_runs/agent_steps plane (the writer persists each
    step). We DO NOT call Session.save() to local JSON on the dashboard path (the tenant DB is
    the record); the Session is re-homed -- its state is what the loop threads + what each step
    persists. PURE: never raises."""
    try:
        from cex_sdk.session.base import Session  # type: ignore[import]

        return Session(session_id=run_key[:12])
    except Exception:
        return _MiniSession()


class _MiniSession:
    """A degrade-never stand-in for cex_sdk.session.Session (same set/get/add_message surface)
    used only when cex_sdk is absent. Holds state + history in memory; never touches disk."""

    def __init__(self) -> None:
        self.state: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    def set(self, key: str, value: Any) -> None:
        self.state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def add_message(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})


# --------------------------------------------------------------------------- #
# Step persistence -- one agent_steps row per step, via the SAME audited adapter (C4 mirror).
# --------------------------------------------------------------------------- #
def _persist_step(
    db: Optional[DbWriter],
    tenant_id: str,
    run_key: str,
    step: AgentStep,
) -> bool:
    """Persist ONE step into agent_steps via the injected writer's persist_agent_step, the C4
    adapter mirror (tenant_id EXPLICIT, RLS-enforced). DEGRADE-NEVER + best-effort: a writer
    that lacks persist_agent_step (a plain Phase-B DbWriter, or a no-op LocalOnlyWriter) ->
    SKIP (the loop still completes; persistence skipped). A persist failure is swallowed (the
    step is already in the in-memory ledger -- the run is never discarded for a DB hiccup).

    R-210: RETURNS True iff the writer was actually invoked AND reported a persisted row
    (a truthy id) -- False for every no-writer / no-capability / no-op / raised-exception
    path. Unlike the sibling `_persist_run_header`, this used to swallow every outcome with
    NO return signal at all (implicit None for success AND failure alike), so a caller could
    never tell whether a step silently failed to reach `agent_steps`. Callers now aggregate
    this into the run's cost dict (`steps_persisted` / `steps_persist_total`, see `_Budget`)."""
    if db is None:
        return False
    persist = getattr(db, "persist_agent_step", None)
    if not callable(persist):
        return False  # a Phase-B-only writer (tenant_data) cannot persist steps -> local-only
    try:
        result = persist(
            tenant_id,
            run_key,
            step.index,
            step.kind,
            content=step.content,
            tool=step.tool,
            tool_io=step.tool_io,
        )
        return bool(result)
    except Exception:
        # Never let a step-persist failure break the loop (the ledger is in memory + the run
        # header records the final state). This mirrors run_capability's best-effort persist.
        return False


def _persist_run_header(
    db: Optional[DbWriter],
    tenant_id: str,
    run_key: str,
    agent_id: str,
    status: str,
    *,
    inputs: Optional[Mapping[str, Any]] = None,
    result: Optional[Mapping[str, Any]] = None,
    cost: Optional[Mapping[str, Any]] = None,
) -> Optional[str]:
    """Persist (UPSERT) the agent_runs header via persist_agent_run, the C4 mirror. Returns
    the run row id (== the deterministic run_id) or None when the writer cannot persist a run
    header (degrade-never). Best-effort: a failure returns None (the run still completes)."""
    if db is None:
        return None
    persist = getattr(db, "persist_agent_run", None)
    if not callable(persist):
        return None
    try:
        return persist(
            tenant_id, run_key, agent_id, status, inputs=inputs, result=result, cost=cost
        )
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# THE multi-step entry (ADR Phase C). A SIBLING of run_agent (Phase B), one layer up.
# --------------------------------------------------------------------------- #
def run_agent_multistep(
    tenant_id: str,
    agent_id: str,
    inputs: Mapping[str, Any],
    credential: Credential,
    *,
    db: Optional[DbWriter] = None,
    options: Optional[Mapping[str, Any]] = None,
    run_key: Optional[str] = None,
) -> MultiStepResult:
    """THE multi-step agent run (ADR Phase C). plan/act/observe over the agent's tools, budgeted
    + persisted + HITL-gated. See module docstring.

    Flow:
      0  SCOPE/BUDGET  reuse run_agent's deny-by-default tenant + enabled gate + the OQ4
                       non-positive-budget guard (refuse BEFORE any LLM call) -- VERBATIM.
      1  RESOLVE       agent_id -> the agent contract (overlay-gated, tenant-scoped).
      2  DEGENERATE    NO declared tools -> DELEGATE to run_agent (Phase B): ONE build, steps==1
                       -- byte-equivalent to the single-shot path (DO NOT regress B).
      3  KICKOFF       mint run_key (or reuse the caller's) -> persist the agent_runs header
                       (status='running'); run_id := the deterministic agent_run_id.
      4  PLAN          one CEXAgent.build PLAN step (the ASSEMBLE contract is the system prompt)
                       -> persist an agent_steps 'plan' row.
      5  LOOP          a cex_sdk.workflow.Loop of ACT (model proposes -> Router dispatches a
                       tool via Toolkit.execute OR a produce) + OBSERVE (fold the result into
                       the Session; persist 'act'/'tool'/'observe' rows). A Condition stops when
                       the F7 gate passes. The budget caps every iteration (stop+refuse on
                       exhaustion). Irreversible tools gate through HITL (emit-and-defer).
      6  PERSIST       UPSERT the agent_runs header with the terminal status + result + cost.
      7  RETURN        a MultiStepResult (run_id + final artifact + steps_log + cost; NO api_key).

    FAIL-CLOSED: every deny raises CapabilityRefused. PERSIST is best-effort (a DB failure never
    discards the run). The api_key is never echoed/logged/persisted.
    """
    tid = (tenant_id or "").strip()
    if not tid:
        raise CapabilityRefused("missing_tenant", capability=agent_id)
    aid = (agent_id or "").strip()
    if not aid:
        raise CapabilityRefused("unresolved_capability", tenant_id=tid, detail="empty agent_id")

    run_inputs: Mapping[str, Any] = inputs if isinstance(inputs, Mapping) else {}

    # -- STEP 0 SCOPE: the SAME enabled gate as Phase B / the capability runtime. --------
    if not _ra._rc._capability_enabled(tid, aid, options):
        raise CapabilityRefused("capability_disabled", tenant_id=tid, capability=aid)

    # -- STEP 0 BUDGET: refuse a non-positive declared budget BEFORE any LLM call (OQ4). --
    # REUSE Phase B's guard verbatim (a max_steps<=0 / budget.*==0 -> budget_exceeded).
    _ra._budget_guard(tid, aid, options)

    # -- STEP 1 RESOLVE: agent_id -> the agent contract (overlay-gated, tenant-scoped). --
    agent = _ra._resolve_agent(tid, aid)
    nucleus, kind, pillar = _ra._agent_runtime_tuple(agent)
    agent_name = str(agent.get("name") or agent.get("id") or aid)
    verb = str(agent.get("verb") or "").strip()
    tool_names = _ra._coerce_tools(agent.get("tools"))

    # -- STEP 2 DEGENERATE: no tools -> the Phase B single-step path, byte-equivalent. ---
    # A 0-tool agent run MUST equal today's capability/Phase-B run (the ADR's degenerate
    # 1-step/0-tool case). DELEGATE to run_agent (it reuses the SAME credential + persist +
    # ASSEMBLE), then LIFT its AgentRunResult into a MultiStepResult (steps==1, no loop). The
    # run header/step rows are written too (so the run is visible in the agent_runs ledger),
    # but the produced artifact + score + persistence are exactly Phase B's.
    if not tool_names:
        return _degenerate_single_step(tid, aid, run_inputs, credential, db, options, run_key)

    # -- STEP 3 KICKOFF: the run_key + the agent_runs header (status='running'). ----------
    rkey = (run_key or uuid.uuid4().hex)
    budget = _resolve_budget(options)
    safe_inputs = {k: v for k, v in run_inputs.items() if str(k).lower() != "intent"} or dict(
        run_inputs
    )
    rid_persisted = _persist_run_header(
        db, tid, rkey, aid, "running", inputs=safe_inputs, cost=budget.as_dict()
    )
    # The public run_id is the deterministic agent_run_id (stable whether or not the header
    # persisted -- the dashboard polls it; the writer UPSERTs the SAME row at completion).
    run_id = rid_persisted or _agent_run_id(tid, rkey)

    # -- STEP 4-5 the LOOP (plan + act/observe over the Toolkit, budgeted, HITL-gated). ---
    loop_out = _run_loop(
        tenant_id=tid,
        agent_id=aid,
        agent=agent,
        nucleus=nucleus,
        kind=kind,
        pillar=pillar,
        verb=verb,
        tool_names=tool_names,
        inputs=run_inputs,
        credential=credential,
        db=db,
        options=options,
        run_key=rkey,
        budget=budget,
    )

    # -- STEP 6-7 terminal header UPSERT + the MultiStepResult. ---------------------------
    result = MultiStepResult(
        tenant_id=tid,
        agent_id=aid,
        capability=aid,
        agent_name=agent_name,
        kind=loop_out["kind"],
        pillar=loop_out["pillar"],
        nucleus=nucleus.upper(),
        run_id=run_id,
        artifact=loop_out["artifact"],
        score=loop_out["score"],
        passed=loop_out["passed"],
        status=loop_out["status"],
        model_used=loop_out["model_used"],
        steps=loop_out["steps"],
        trace=loop_out["trace"],
        errors=loop_out["errors"],
        steps_log=[_step_to_view(s) for s in loop_out["steps_log"]],
        cost=budget.as_dict(),
    )

    final_result_meta = {
        "artifact_kind": result.kind,
        "score": result.score,
        "passed": result.passed,
        "steps": result.steps,
        "status": result.status,
    }
    header_id = _persist_run_header(
        db, tid, rkey, aid, result.status,
        inputs=safe_inputs, result=final_result_meta, cost=budget.as_dict(),
    )
    if header_id is not None:
        result.record_id = str(header_id)
        result.persisted = True
    return result


def _agent_run_id(tenant_id: str, run_key: str) -> str:
    """The deterministic agent_run_id (the public run_id), resolved via the writer module so
    it matches the persisted row id EXACTLY. DEGRADE-NEVER: if the writer module is absent,
    synthesize a stable uuid5 locally with the SAME namespace contract."""
    try:
        import cex_runtime_sync  # type: ignore[import]

        return cex_runtime_sync.agent_run_id(tenant_id, run_key)
    except Exception:
        ns = uuid.UUID("a4f3c2d1-0000-5000-8000-6167656e7472")
        return str(uuid.uuid5(ns, "%s|%s" % (tenant_id, run_key)))


def _step_to_view(step: AgentStep) -> Dict[str, Any]:
    """Project one AgentStep to a JSON-safe dict for the result + the events stream. No
    secret can appear (the step content is model output / tool I/O, never a credential)."""
    return {
        "index": step.index,
        "kind": step.kind,
        "content": step.content,
        "tool": step.tool,
        "tool_io": step.tool_io,
        "approval_id": step.approval_id,
    }


# --------------------------------------------------------------------------- #
# The degenerate (0-tool) path -- DELEGATE to Phase B run_agent, byte-equivalent.
# --------------------------------------------------------------------------- #
def _degenerate_single_step(
    tenant_id: str,
    agent_id: str,
    inputs: Mapping[str, Any],
    credential: Credential,
    db: Optional[DbWriter],
    options: Optional[Mapping[str, Any]],
    run_key: Optional[str],
) -> MultiStepResult:
    """A 0-tool agent run == Phase B: ONE CEXAgent.build, steps==1 (the ADR degenerate case).

    DELEGATE to run_agent (it reuses the SAME credential + ASSEMBLE loader + the tenant_data
    persist), then LIFT its AgentRunResult into a MultiStepResult so the async API returns the
    SAME shape for every run. We ALSO write an agent_runs header + a single 'plan' step row (so
    a 0-tool run is visible in the agent-run ledger), but the produced artifact + score +
    persistence are EXACTLY Phase B's (the capability path is unregressed)."""
    rkey = (run_key or uuid.uuid4().hex)
    run_id = _agent_run_id(tenant_id, rkey)
    # The header at kickoff (status='running'); best-effort.
    _persist_run_header(db, tenant_id, rkey, agent_id, "running", inputs=dict(inputs))

    # Phase B does the real work (resolve + ASSEMBLE + ONE build + tenant_data persist).
    b: AgentRunResult = _ra.run_agent(
        tenant_id, agent_id, inputs, credential, db=db, options=options
    )

    # Record the single step (a 'plan'-kind row capturing the produced artifact provenance).
    step = AgentStep(
        index=0,
        kind="plan",
        content={"summary": "single-step run (no tools declared)", "passed": b.passed},
    )
    _persist_step(db, tenant_id, rkey, step)

    status = "completed" if b.passed else "failed"
    result = MultiStepResult(
        tenant_id=b.tenant_id,
        agent_id=b.agent_id,
        capability=b.capability,
        agent_name=b.agent_name,
        kind=b.kind,
        pillar=b.pillar,
        nucleus=b.nucleus,
        run_id=run_id,
        artifact=b.artifact,
        score=b.score,
        passed=b.passed,
        status=status,
        model_used=b.model_used,
        record_id=b.record_id,            # the tenant_data row id from Phase B
        persisted=b.persisted,
        steps=1,
        trace=b.trace,
        errors=list(b.errors),
        steps_log=[_step_to_view(step)],
        cost={"steps_used": 1, "max_steps": None},
    )
    # UPSERT the run header to the terminal state (best-effort; the run_id is stable).
    _persist_run_header(
        db, tenant_id, rkey, agent_id, status,
        inputs=dict(inputs),
        result={"artifact_kind": b.kind, "score": b.score, "passed": b.passed, "steps": 1},
        cost={"steps_used": 1},
    )
    return result


# --------------------------------------------------------------------------- #
# The plan/act/observe LOOP -- composes cex_sdk.workflow (Loop/Condition/Router/Step) +
# Toolkit + Session. Each LLM step bottoms out in CEXAgent.build (one chat), exactly as the
# ADR specifies ("the single LLM step still bottoms out in CEXAgent.build()").
# --------------------------------------------------------------------------- #
def _run_loop(
    *,
    tenant_id: str,
    agent_id: str,
    agent: Mapping[str, Any],
    nucleus: str,
    kind: str,
    pillar: str,
    verb: str,
    tool_names: List[str],
    inputs: Mapping[str, Any],
    credential: Credential,
    db: Optional[DbWriter],
    options: Optional[Mapping[str, Any]],
    run_key: str,
    budget: _Budget,
) -> Dict[str, Any]:
    """Drive plan + act/observe, COMPOSING cex_sdk primitives. Returns a dict the caller lifts
    into a MultiStepResult. Honest: each model turn is ONE CEXAgent.build (the SAME seam Phase
    B uses + tests fake); the Toolkit is the dispatch surface; the Session threads state; the
    Loop/Condition/Router structure the control flow; the budget caps it; HITL gates
    irreversible tools.

    The loop is BOUNDED three ways: the budget step ceiling, the cex_sdk Loop max_iterations,
    and a passed-gate Condition (stop early on success). A budget exhaustion sets status
    'budget_exceeded' and STOPS (never runs past the ceiling -- OQ4)."""
    # CREDENTIAL select (REUSE the spine verbatim): native_local RAISES here -- BEFORE any
    # build -- exactly as Phase B / the capability runtime; byo_api_key returns (model, provider).
    # This keeps the multi-step loop's credential story IDENTICAL to the single-step path.
    model, provider = _ra._rc._select_credential(credential, tenant_id, agent_id, default_model="")

    # Lazy SDK import (degrade-never -> a procedural fallback if cex_sdk is absent).
    sdk = _import_workflow()
    session = _new_session(run_key)
    toolkit = _build_toolkit(tool_names, tenant_id, agent_id)
    tool_schemas = toolkit.get_tool_schemas() if toolkit is not None else []

    # The ASSEMBLE contract is the system prompt for EVERY model turn (REUSE Phase B's loader).
    base_system = _ra.assemble_agent_contract(agent, inputs)
    intent = _ra.derive_intent(agent, inputs)

    # The CEXAgent seam (the SAME module-level name Phase B + the capability runtime fake).
    agent_cls = _ra._rc.CEXAgent if _ra._rc.CEXAgent is not None else _ra._rc._import_cex_agent()

    steps_log: List[AgentStep] = []
    errors: List[str] = []
    step_index = 0

    # A shared mutable loop context the cex_sdk Step executors read/write through StepInput.
    ctx: Dict[str, Any] = {
        "artifact": "",
        "kind": kind,
        "pillar": pillar,
        "score": 0.0,
        "passed": False,
        "model_used": "",
        "trace_parts": [],
        "done": False,
        "status": "running",
    }

    # ---- a single MODEL turn (PLAN or ACT): ONE CEXAgent.build under the key scope. -----
    def _model_turn(turn_kind: str, extra: str) -> AgentStep:
        nonlocal step_index
        system = base_system
        if extra:
            system = base_system + "\n\n## Loop context\n" + extra
        with _ra._rc._ProviderKeyScope(credential, provider):
            sdk_agent = agent_cls(nucleus=nucleus, kind=kind, model=model)
            build = sdk_agent.build(intent, system=system)
        artifact = str(getattr(build, "artifact", "") or "")
        ctx["artifact"] = artifact
        ctx["kind"] = str(getattr(build, "kind", kind) or kind)
        ctx["pillar"] = str(getattr(build, "pillar", pillar) or pillar)
        ctx["score"] = float(getattr(build, "score", 0.0) or 0.0)
        ctx["passed"] = bool(getattr(build, "passed", False))
        ctx["model_used"] = str(getattr(sdk_agent, "model", "") or "")
        ctx["trace_parts"].append(str(getattr(build, "trace", "") or ""))
        errors.extend(list(getattr(build, "errors", []) or []))
        budget.tokens_used += len(artifact) + len(system)
        step = AgentStep(
            index=step_index,
            kind=turn_kind,
            content={
                "intent": intent,
                "passed": ctx["passed"],
                "score": ctx["score"],
                "artifact_chars": len(artifact),
            },
        )
        step_index += 1
        steps_log.append(step)
        budget.steps_used += 1
        # R-210: aggregate the honest persist signal into the run's cost dict.
        budget.steps_persist_total += 1
        if _persist_step(db, tenant_id, run_key, step):
            budget.steps_persisted += 1
        if hasattr(session, "add_message"):
            session.add_message("assistant", artifact[:2000])
        return step

    # ---- a TOOL step: HITL-gate -> Toolkit.execute (or skip) -> OBSERVE. ----------------
    def _tool_turn(tool_name: str) -> Tuple[AgentStep, AgentStep]:
        nonlocal step_index
        args = _propose_tool_args(inputs)
        approval_id: Optional[str] = None
        observation: str
        if _tool_needs_approval(tool_name, verb, options):
            # OQ8 emit-and-defer: record a pending approval + SKIP the tool (non-blocking).
            approval_id = _emit_approval(tenant_id, agent_id, tool_name, options)
            observation = (
                "hitl_pending: tool '%s' is irreversible/deploy -> a human approval was "
                "requested (id=%s). The tool was NOT executed this run (emit-and-defer)."
                % (tool_name, approval_id)
            )
        elif toolkit is not None:
            observation = toolkit.execute(tool_name, **args)
        else:
            observation = _unbound_tool_note(tool_name)

        tool_step = AgentStep(
            index=step_index,
            kind="tool",
            tool=tool_name,
            tool_io={"args": args, "result": observation[:2000]},
            approval_id=approval_id,
        )
        step_index += 1
        steps_log.append(tool_step)
        budget.steps_used += 1
        budget.tokens_used += len(observation)
        # R-210: aggregate the honest persist signal into the run's cost dict.
        budget.steps_persist_total += 1
        if _persist_step(db, tenant_id, run_key, tool_step):
            budget.steps_persisted += 1

        observe_step = AgentStep(
            index=step_index,
            kind="observe",
            content={"tool": tool_name, "observation": observation[:1000]},
        )
        step_index += 1
        steps_log.append(observe_step)
        budget.steps_persist_total += 1
        if _persist_step(db, tenant_id, run_key, observe_step):
            budget.steps_persisted += 1
        if hasattr(session, "set"):
            session.set("last_observation", observation[:2000])
        return tool_step, observe_step

    # ---- compose the cex_sdk Workflow primitives to STRUCTURE the loop. ----------------
    # PLAN (Step) -> Loop(ACT/OBSERVE, Condition=gate-passed) -- a real cex_sdk DAG. The Step
    # executors call _model_turn / _tool_turn above; the Loop's stop-condition is the F7 gate;
    # the Router selects tool-vs-produce. We BUILD the primitives (so the structure IS cex_sdk)
    # and run them; if cex_sdk is absent we fall through to the procedural driver (same logic).
    if sdk is not None:
        _run_via_workflow(sdk, ctx, budget, tool_names, _model_turn, _tool_turn, errors)
    else:
        _run_procedural(ctx, budget, tool_names, _model_turn, _tool_turn)

    status = ctx["status"]
    if status == "running":
        status = "completed" if ctx["passed"] else "failed"
    trace = " || ".join(p for p in ctx["trace_parts"] if p)
    return {
        "artifact": ctx["artifact"],
        "kind": ctx["kind"],
        "pillar": ctx["pillar"],
        "score": ctx["score"],
        "passed": ctx["passed"],
        "status": status,
        "model_used": ctx["model_used"],
        "steps": len(steps_log),
        "trace": trace,
        "errors": errors,
        "steps_log": steps_log,
    }


def _run_via_workflow(
    sdk: Dict[str, Any],
    ctx: Dict[str, Any],
    budget: _Budget,
    tool_names: List[str],
    model_turn: Callable[[str, str], AgentStep],
    tool_turn: Callable[[str], Tuple[AgentStep, AgentStep]],
    errors: List[str],
) -> None:
    """Run the loop THROUGH the cex_sdk.workflow primitives (Workflow/Step/Loop/Condition/
    Router). The Step executors wrap model_turn/tool_turn; the Loop's condition is the F7 gate;
    the budget caps iterations. This is the ADR's "Loop = act/observe, Condition = F7 gate,
    Router = tool dispatch" composed for real."""
    Step = sdk["Step"]
    Loop = sdk["Loop"]
    StepInput = sdk["StepInput"]
    StepOutput = sdk["StepOutput"]

    # PLAN as a cex_sdk Step.
    def _plan_exec(_inp: Any) -> Any:
        if budget.would_exceed_steps():
            ctx["status"] = "budget_exceeded"
            ctx["done"] = True
            return StepOutput(content="budget_exceeded")
        model_turn("plan", "Plan the approach. Tools available: %s." % ", ".join(tool_names))
        if ctx["passed"]:
            ctx["done"] = True
        return StepOutput(content=ctx["artifact"], session_state={"passed": ctx["passed"]})

    plan_step = Step(name="PLAN", executor=_plan_exec, max_retries=1)

    # ACT/OBSERVE as a cex_sdk Step that the Loop repeats. Each iteration: pick a tool (Router
    # semantics -- here a simple round-robin over the grants), run a tool turn, then a model
    # ACT turn to fold the observation into a fresh produce. The Loop's condition stops on the
    # gate OR budget exhaustion.
    tool_cursor = {"i": 0}

    def _act_exec(_inp: Any) -> Any:
        if ctx["done"]:
            return StepOutput(content="done")
        if budget.would_exceed_steps():
            ctx["status"] = "budget_exceeded"
            ctx["done"] = True
            return StepOutput(content="budget_exceeded")
        # Router: choose the next tool grant (round-robin); a real planner would choose by the
        # model's proposed action -- this bounded selection keeps the loop deterministic offline.
        tool_name = tool_names[tool_cursor["i"] % len(tool_names)]
        tool_cursor["i"] += 1
        if budget.would_exceed_tokens(0):
            ctx["status"] = "budget_exceeded"
            ctx["done"] = True
            return StepOutput(content="budget_exceeded")
        tool_turn(tool_name)
        if budget.would_exceed_steps():
            ctx["status"] = "budget_exceeded"
            ctx["done"] = True
            return StepOutput(content="budget_exceeded")
        # ACT: a model turn that produces with the observation in context.
        model_turn("act", "Incorporate the latest tool observation and produce the artifact.")
        if ctx["passed"]:
            ctx["done"] = True
        return StepOutput(content=ctx["artifact"], session_state={"passed": ctx["passed"]})

    act_step = Step(name="ACT_OBSERVE", executor=_act_exec, max_retries=1)

    # The Loop: repeat ACT/OBSERVE until the gate passes (Condition) or the budget/iteration cap.
    # max_iterations is the SDK backstop; the budget step ceiling is the authoritative OQ4 cap.
    loop = Loop(
        name="act_observe_loop",
        step=act_step,
        condition=lambda out: ctx["done"],     # stop when done (gate passed or budget hit)
        max_iterations=max(1, budget.step_ceiling()),
    )

    # Run PLAN then the LOOP through a real cex_sdk Workflow (the composition IS the SDK DAG).
    Workflow = sdk["Workflow"]
    wf = Workflow(name="agent_plan_act_observe", steps=[plan_step, loop])
    try:
        wf.run(StepInput(content="start"))
    except Exception as exc:  # the loop must surface, never crash the run.
        errors.append("loop_error: %s: %s" % (type(exc).__name__, exc))
        ctx["status"] = "failed"


def _run_procedural(
    ctx: Dict[str, Any],
    budget: _Budget,
    tool_names: List[str],
    model_turn: Callable[[str, str], AgentStep],
    tool_turn: Callable[[str], Tuple[AgentStep, AgentStep]],
) -> None:
    """The SAME plan/act/observe logic WITHOUT cex_sdk (degrade-never fallback). Mirrors
    _run_via_workflow exactly so the loop behaves identically whether or not cex_sdk imports."""
    if budget.would_exceed_steps():
        ctx["status"] = "budget_exceeded"
        return
    model_turn("plan", "Plan the approach. Tools available: %s." % ", ".join(tool_names))
    if ctx["passed"]:
        return
    i = 0
    while not ctx["passed"]:
        if budget.would_exceed_steps() or budget.would_exceed_tokens(0):
            ctx["status"] = "budget_exceeded"
            return
        tool_name = tool_names[i % len(tool_names)]
        i += 1
        tool_turn(tool_name)
        if budget.would_exceed_steps():
            ctx["status"] = "budget_exceeded"
            return
        model_turn("act", "Incorporate the latest tool observation and produce the artifact.")


def _import_workflow() -> Optional[Dict[str, Any]]:
    """Import the cex_sdk.workflow primitives, or None (degrade-never). Returned as a dict of
    classes so the loop composes them without a hard module dependency at import."""
    try:
        from cex_sdk.workflow import (  # type: ignore[import]
            Condition,
            Loop,
            Router,
            Step,
            StepInput,
            StepOutput,
            Workflow,
        )

        return {
            "Condition": Condition,
            "Loop": Loop,
            "Router": Router,
            "Step": Step,
            "StepInput": StepInput,
            "StepOutput": StepOutput,
            "Workflow": Workflow,
        }
    except Exception:
        return None


def _propose_tool_args(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    """The args a tool call carries. Offline-deterministic: the typed run inputs (minus the
    free-text 'intent') are the tool's context. A real model would emit structured tool args;
    this bounded projection keeps the loop testable without a live LLM tool-call round-trip."""
    return {k: v for k, v in inputs.items() if str(k).lower() != "intent"}


__all__ = [
    "AgentStep",
    "MultiStepResult",
    "run_agent_multistep",
    "tool_resolver",
    "Credential",
    "CapabilityRefused",
    "DbWriter",
    "AgentRunResult",
    "MODE_BYO_API_KEY",
    "MODE_NATIVE_LOCAL",
    "MODE_PLATFORM",
]
