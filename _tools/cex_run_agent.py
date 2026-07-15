# !/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI headless agent runtime -- run_agent (ADR adr_agents_sdk_dashboard, Phase B).

THE single-step AGENT run -- a SIBLING of run_capability (NOT a fork). Implements Layer 2
Phase B of the Agents SDK ADR ("run_agent SIBLING of run_capability"; "the ASSEMBLE
loader"; "persist via make_run_writer"; "a 1-step/0-tool run == today's capability run").

WHAT THIS ADDS over run_capability (the gap Phase B closes): run_capability resolves a
CAPABILITY -> (nucleus, kind) and calls CEXAgent.build(intent) with a GENERIC system prompt
-- it IGNORES the agent artifact entirely (CEXAgent.build's F4 builds a kind-only prompt).
run_agent resolves a DEFINED AGENT (agent + agent_card + system_prompt) and ASSEMBLES the
agent's REAL contract -- persona + Input/Output Schema + the declared tools list -- into the
F2 BECOME context, feeding it as the ``system`` override of CEXAgent.build. That is the one
genuinely-missing definition-side piece: the loader that consumes the real contract so the
agent's persona + typed I/O are HONORED, not a generic builder prompt.

REUSE (the #1 rule -- do NOT fork the rails): run_agent imports run_capability's spine
VERBATIM and reuses it:
  * Credential / CapabilityRefused / DbWriter  -- the SAME dataclasses/Protocol (re-exported).
  * _select_credential + _ProviderKeyScope     -- BYO-key custody (OQ2: byo_api_key is the
                                                   wired path; native_local RAISES, not faked).
  * _capability_enabled                         -- the deny-by-default enabled gate.
  * _guard_frozen + _FROZEN_KINDS               -- the 8F-moat (an agent can never target a
                                                   frozen kind).
  * the CEXAgent seam (lazy import; module-level name for offline fakeability).
run_agent differs ONLY in: (1) it resolves an AGENT (not a capability) via agents_config; (2)
it ASSEMBLES the agent contract into the build's ``system`` override; (3) it returns an
AgentRunResult (the capability shape + agent_id/agent_name). PERSIST is byte-identical: the
SAME make_run_writer DbWriter into the SAME tenant_data (NO new tables -- agent_runs /
agent_steps are Phase C).

SINGLE STEP (the 1-step contract): exactly ONE chat() (inside CEXAgent.build's F5). NO tool
LOOP (the declared tools are surfaced to the model as CONTEXT but NEVER executed -- tool
execution + plan/act/observe is the Phase C multi-step loop). NO async / run_id (Phase C).
So a 1-step/0-tool agent run is byte-equivalent to today's capability run, only with the
agent's persona + I/O contract honored.

OQ FALLBACKS (decided, per the task contract):
  * OQ2 = BYO key for ALL agent runs -- the existing build_credential / byo_api_key path
    (native_local still RAISES native_local_headless_unresolved; not faked).
  * OQ4 = honor a team_charter-style budget IF declared -- a SOFT guard for 1 step: a
    declared ``max_steps``/``budget`` in options is recorded + a 1-step run is always within
    a >=1-step budget; a budget of 0 (or a non-positive max_steps) refuses BEFORE the build
    (budget_exceeded), so the soft ceiling is real but never blocks a normal 1-step run.

HARD RULES (per the task contract + .claude/rules/ascii-code-rule.md):
  * ASCII-only; fully type-hinted; FAIL-CLOSED (every deny raises CapabilityRefused).
  * NO concrete DB driver and NO LLM key imported/read at MODULE IMPORT (run_capability is
    import-light; agents_config is a pure file reader). The DbWriter + Credential are
    INJECTED; the api_key lives only inside the passed Credential.
  * tenant_id is ALWAYS an explicit argument; never inferred from ambient global state.

Spec: _docs/compiled/adr_agents_sdk_dashboard.md (Phase B, Layer 2 RUNTIME).
Sibling of: _tools/cex_run_capability.py (the spine -- reused, not forked).
Wraps: cex_sdk/agent/cex_agent.py (CEXAgent.build -- the assembled contract feeds in as
``system``). Resolves: apps/dashboard_api/agents_config.get_agent (the agent contract:
persona + Input/Output schema + tools, overlay-gated + tenant-scoped).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Mapping, Optional, Tuple

# --------------------------------------------------------------------------- #
# REUSE the run_capability spine VERBATIM (the #1 rule: do NOT fork the rails).
# Imported lazily-safe: cex_run_capability is import-light (no driver/key at load).
# We pull the SAME Credential / CapabilityResult / CapabilityRefused / DbWriter +
# the SAME credential/enabled/frozen helpers so the tenant/credential/persist rails
# are SHARED, never re-implemented.
# --------------------------------------------------------------------------- #
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_run_capability as _rc  # type: ignore[import]

# Re-export the SAME contract types so callers (the dashboard backend) construct ONE set of
# objects regardless of which sibling they call. These are NOT new types -- they are the
# run_capability contract, shared.
Credential = _rc.Credential
CapabilityResult = _rc.CapabilityResult
CapabilityRefused = _rc.CapabilityRefused
DbWriter = _rc.DbWriter
MODE_BYO_API_KEY = _rc.MODE_BYO_API_KEY
MODE_NATIVE_LOCAL = _rc.MODE_NATIVE_LOCAL
MODE_PLATFORM = _rc.MODE_PLATFORM
_FROZEN_KINDS = _rc._FROZEN_KINDS
_TENANT_DATA_TABLE = _rc._TENANT_DATA_TABLE

# The repo root (this file lives in <root>/_tools) -- used to read on-disk agent artifacts
# through the SAME tenant-scoped, fail-closed reader the dashboard uses (agents_config).
_REPO_ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------- #
# AgentRunResult (Phase B) -- the CapabilityResult shape + agent identity.
# Mirrors CapabilityResult field-for-field (so _result_to_view's allowlist serializes it
# unchanged) and ADDS agent_id / agent_name (and a single-step ``steps`` count == 1, so the
# Phase C multi-step ledger has a forward-compatible field that is always 1 here).
# --------------------------------------------------------------------------- #
@dataclass
class AgentRunResult:
    """Outcome of one SINGLE-STEP agent run. The api_key is NEVER present on this object.

    Field parity with CapabilityResult is intentional: the dashboard's _result_to_view
    allowlist projects the SAME credential-free fields, so an AgentRunResult serializes
    exactly like a CapabilityResult, plus the agent identity. ``steps`` is always 1 here (the
    1-step contract); Phase C grows it into the real step ledger.
    """

    tenant_id: str
    agent_id: str
    capability: str                              # the agent_id, echoed as the run "capability"
    kind: str
    pillar: str
    nucleus: str
    agent_name: str = ""
    artifact: str = ""                           # produced artifact (frontmatter+body)
    score: float = 0.0                           # F7 structural score
    passed: bool = False                         # gate result (score floor AND frontmatter)
    status: str = "error"                        # produced | persisted | produced_unpersisted | error
    model_used: str = ""                         # the F5 model string actually used
    record_id: Optional[str] = None              # row id in the tenant Supabase
    persisted: bool = False                      # True iff artifact landed in tenant DB
    steps: int = 1                               # always 1 (single-step contract; Phase C: N)
    trace: str = ""                              # the F1..F8 trace string from BuildResult
    errors: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Agent resolution -- DELEGATE to agents_config (the tested, overlay-gated, tenant-scoped,
# DEGRADE-NEVER reader the dashboard's GET /agents/{id} already uses). REUSE, never
# re-implement: the SAME visibility gate (a gated-out / frozen / unknown agent -> None) and
# the SAME on-disk detail parse (persona + Input/Output Schema + capabilities/tools).
# --------------------------------------------------------------------------- #
def _import_agents_config() -> Any:
    """Import apps.dashboard_api.agents_config lazily (pure file reader; no DB/network).

    Lazy + sys.path-guarded so a degraded environment that lacks it still imports THIS
    module; the failure surfaces only when a run is attempted. Returns the module.
    """
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from apps.dashboard_api import agents_config  # type: ignore[import]

    return agents_config


# Tests set cex_run_agent.resolve_agent = fake to run offline without the registry/overlay.
# When None (default), run_agent resolves via agents_config.get_agent lazily.
resolve_agent: Any = None


def _resolve_agent(tenant_id: str, agent_id: str) -> Mapping[str, Any]:
    """Resolve ``agent_id`` -> the agent contract (DTO + on-disk detail), TENANT-SCOPED.

    DELEGATES to agents_config.get_agent(tenant_id, agent_id) -- the SAME overlay-gated,
    tenant-scoped, fail-closed resolution GET /agents/{id} uses. Mapping of outcomes -> the
    runtime's fail-closed contract:
      * a dict (the visible agent's DTO + detail) -> returned;
      * None (gated out / frozen / unknown for this tenant) ->
        CapabilityRefused('unresolved_capability') so the dashboard maps it to a 4xx, never a
        500 and never another tenant's agent.

    DEGRADE-NEVER: if agents_config cannot be imported at all, raise
    CapabilityRefused('unresolved_capability') (a degraded environment cannot resolve an
    agent -- fail-closed, never a fabricated agent). The frozen guard runs belt-and-braces on
    the resolved kind afterwards.
    """
    resolver = resolve_agent
    if resolver is None:
        try:
            mod = _import_agents_config()
        except Exception as exc:
            raise CapabilityRefused(
                "unresolved_capability",
                tenant_id=tenant_id,
                capability=agent_id,
                detail="agent catalog unavailable: %s" % str(exc),
            )
        resolver = mod.get_agent

    agent = resolver(tenant_id, agent_id)
    if not agent or not isinstance(agent, Mapping):
        raise CapabilityRefused(
            "unresolved_capability",
            tenant_id=tenant_id,
            capability=agent_id,
            detail="agent maps to no visible definition (gated out, frozen, or unknown)",
        )
    return agent


def _agent_runtime_tuple(agent: Mapping[str, Any]) -> Tuple[str, str, str]:
    """Project the resolved agent -> (nucleus, kind, pillar) for the build, FAIL-CLOSED.

    nucleus  <- the agent's nucleus, lowercased to the SDK convention ('N03' -> 'n03'); a
                missing nucleus falls back to 'n03' (the build nucleus only routes the default
                model + signal -- the agent contract is what actually drives the output).
    kind     <- the agent's backing artifact kind (agent | agent_card). The frozen guard
                refuses it if (impossibly) frozen.
    pillar   <- the agent's pillar when present ('' otherwise -- CEXAgent.build re-resolves
                the pillar from the kind, so '' is safe).
    """
    nucleus = str(agent.get("nucleus") or "").strip().lower() or "n03"
    kind = str(agent.get("kind") or "agent").strip() or "agent"
    pillar = str(agent.get("pillar") or "").strip()
    _rc._guard_frozen(kind, str(agent.get("tenant_id") or ""), str(agent.get("id") or ""))
    return nucleus, kind, pillar


# --------------------------------------------------------------------------- #
# THE ASSEMBLE loader (the gap Phase B closes).
# Builds the agent's REAL contract -- persona + Input/Output Schema + the DECLARED tools list
# -- as an F2 BECOME ``system`` prompt that is fed into CEXAgent.build(intent, system=...).
# CEXAgent.build uses ``system or build_system_prompt(...)`` (cex_sdk/agent/cex_agent.py), so
# a non-empty assembled system REPLACES the generic kind-only prompt -- closing the gap that
# build IGNORES the agent artifact. The tools are surfaced as CONTEXT ONLY (DO NOT execute --
# single step; tool execution is the Phase C loop).
# --------------------------------------------------------------------------- #
def assemble_agent_contract(
    agent: Mapping[str, Any],
    inputs: Mapping[str, Any],
) -> str:
    """Assemble the agent's real contract into an F2 BECOME system prompt (the loader).

    Consumes the resolved agent's persona + capabilities + Input/Output Schema + declared
    tools (the SAME detail agents_config parses from the agent + agent_card on disk), plus the
    typed ``inputs`` for THIS run, and returns a single system-prompt string. This is what
    makes CEXAgent HONOR the agent: the persona becomes the identity, the Input Schema binds
    the typed inputs, the Output Schema constrains the artifact, and the tools are listed as
    available-but-not-executed (single step).

    PURE + TOTAL: every field is optional; a thin agent (only a name) yields a minimal but
    valid contract. NEVER raises. NEVER includes a secret (the agent DTO carries none).
    """
    name = str(agent.get("name") or agent.get("id") or "Agent").strip()
    nucleus = str(agent.get("nucleus") or "").strip()
    persona = str(agent.get("persona") or "").strip()
    goal = str(agent.get("goal") or agent.get("description") or "").strip()
    in_schema = str(agent.get("input_schema") or "").strip()
    out_schema = str(agent.get("output_schema") or "").strip()

    lines: List[str] = []
    lines.append("=== CEX Agent Contract (F2 BECOME) ===")
    header = "You ARE the agent '%s'" % name
    if nucleus:
        header += " (nucleus %s)" % nucleus
    header += "."
    lines.append(header)
    if persona:
        lines.append("")
        lines.append("## Persona")
        lines.append(persona)
    if goal:
        lines.append("")
        lines.append("## Goal")
        lines.append(goal)

    caps = agent.get("capabilities")
    if isinstance(caps, (list, tuple)) and caps:
        lines.append("")
        lines.append("## Capabilities")
        for cap in caps[:20]:
            if isinstance(cap, Mapping):
                label = str(cap.get("capability") or "").strip()
                desc = str(cap.get("description") or "").strip()
                if label:
                    lines.append("- %s%s" % (label, (": " + desc) if desc else ""))

    # The DECLARED tools -- surfaced as CONTEXT ONLY. The single-step contract: list them so
    # the model knows the agent's grants, but DO NOT execute them (tool execution is Phase C).
    tools = _coerce_tools(agent.get("tools"))
    if tools:
        lines.append("")
        lines.append("## Declared tools (context only -- NOT executed this step)")
        lines.append(", ".join(tools))
        lines.append(
            "This is a SINGLE-STEP run: reason as if these tools were available, but produce "
            "the artifact in one pass. Do not emit tool calls."
        )

    if in_schema:
        lines.append("")
        lines.append("## Input Schema")
        lines.append(in_schema)
    if out_schema:
        lines.append("")
        lines.append("## Output Schema")
        lines.append(out_schema)

    bound = _format_inputs(inputs)
    if bound:
        lines.append("")
        lines.append("## Bound inputs (this run)")
        lines.append(bound)

    lines.append("")
    lines.append(
        "Honor the persona and the Output Schema. Produce a complete, typed artifact with "
        "valid frontmatter. Single step: one pass, no tool calls, no follow-up turns."
    )
    return "\n".join(lines).strip()


def _coerce_tools(value: Any) -> List[str]:
    """Coerce the agent's ``tools`` (a list of strings on the DTO) to a clean list ([]
    otherwise). PURE + TOTAL."""
    if not isinstance(value, (list, tuple)):
        return []
    out: List[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def _format_inputs(inputs: Mapping[str, Any]) -> str:
    """Render the typed run inputs as a compact, readable block (key: value per line).

    Scalars are rendered verbatim; lists become comma-joined; anything else is str()'d.
    Bounded so a surprise input can never blow the prompt. PURE + TOTAL -- never raises.
    """
    if not isinstance(inputs, Mapping) or not inputs:
        return ""
    out: List[str] = []
    for key, value in list(inputs.items())[:40]:
        k = str(key).strip()
        if not k:
            continue
        if isinstance(value, (list, tuple)):
            rendered = ", ".join(str(v) for v in value)
        elif isinstance(value, (str, int, float, bool)) or value is None:
            rendered = str(value)
        else:
            rendered = str(value)
        out.append("%s: %s" % (k, rendered[:500]))
    return "\n".join(out)


def derive_intent(
    agent: Mapping[str, Any],
    inputs: Mapping[str, Any],
) -> str:
    """Derive the F5 user-turn intent string from the typed inputs (the build's ``intent``).

    Precedence (the typed-form contract): an explicit ``intent`` in the inputs wins (the
    free-text fallback for an agent with no Input Schema -- see the dashboard). Otherwise, a
    one-line intent is synthesized from the agent goal + the bound inputs, so a schema-driven
    run still has a meaningful user turn (the assembled contract carries the full detail; the
    intent is the human-readable ask). NEVER empty (CEXAgent.build needs a non-empty intent):
    falls back to the agent name. PURE + TOTAL.
    """
    explicit = inputs.get("intent") if isinstance(inputs, Mapping) else None
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()

    goal = str(agent.get("goal") or agent.get("description") or "").strip()
    bound = _format_inputs(
        {k: v for k, v in inputs.items() if str(k).strip() != "intent"}
    ) if isinstance(inputs, Mapping) else ""
    parts: List[str] = []
    if goal:
        parts.append(goal)
    if bound:
        parts.append(bound.replace("\n", "; "))
    intent = " -- ".join(parts).strip()
    if intent:
        return intent[:2000]
    return str(agent.get("name") or agent.get("id") or "run agent").strip()


# --------------------------------------------------------------------------- #
# OQ4 budget guard (soft, 1-step). A declared budget is RECORDED; a non-positive ceiling
# refuses BEFORE the build. Never blocks a normal 1-step run (a default/absent budget is
# unbounded for this 1 step). This is the SOFT charter-style guard the ADR (OQ4) calls for,
# minimal for a single step (the real per-step cost ceiling is the Phase C loop's job).
# --------------------------------------------------------------------------- #
def _budget_guard(
    tenant_id: str,
    agent_id: str,
    options: Optional[Mapping[str, Any]],
) -> None:
    """Refuse a run whose declared budget cannot afford even ONE step (OQ4 soft guard).

    Reads an optional ``budget`` (a team_charter-style mapping) OR a bare ``max_steps`` from
    options. A ``max_steps`` <= 0 (or budget.max_steps <= 0, or budget.usd == 0 /
    budget.tokens == 0) -> CapabilityRefused('budget_exceeded') BEFORE any LLM call. Anything
    else (absent, >=1, non-numeric) is permissive: a single step is always within a >=1-step
    budget. NEVER raises anything but CapabilityRefused.
    """
    if not options:
        return
    max_steps = options.get("max_steps")
    if _is_nonpositive_number(max_steps):
        raise CapabilityRefused(
            "budget_exceeded",
            tenant_id=tenant_id,
            capability=agent_id,
            detail="max_steps=%r cannot afford a single step" % (max_steps,),
        )
    budget = options.get("budget")
    if isinstance(budget, Mapping):
        for ceiling_key in ("max_steps", "steps", "usd", "tokens", "wall_clock"):
            if ceiling_key in budget and _is_nonpositive_number(budget.get(ceiling_key)):
                raise CapabilityRefused(
                    "budget_exceeded",
                    tenant_id=tenant_id,
                    capability=agent_id,
                    detail="budget.%s=%r cannot afford a single step"
                    % (ceiling_key, budget.get(ceiling_key)),
                )


def _is_nonpositive_number(value: Any) -> bool:
    """True iff ``value`` is a real number <= 0 (a non-number / None -> False, permissive)."""
    if isinstance(value, bool):
        return False  # a bool is not a budget number
    if isinstance(value, (int, float)):
        return value <= 0
    return False


# --------------------------------------------------------------------------- #
# THE entry (ADR Phase B). A SIBLING of run_capability.run_capability.
# --------------------------------------------------------------------------- #
def run_agent(
    tenant_id: str,
    agent_id: str,
    inputs: Mapping[str, Any],
    credential: Credential,
    *,
    db: Optional[DbWriter] = None,
    options: Optional[Mapping[str, Any]] = None,
) -> AgentRunResult:
    """THE single-step agent run (ADR Phase B). A SIBLING of run_capability; see module docstring.

    Flow (REUSES run_capability's spine; differs only in RESOLVE + ASSEMBLE):
      2a SCOPE      deny-by-default on the tenant (mirror the adapter rule).
      2b SCOPE      deny an agent not enabled for this tenant (the SAME enabled gate, keyed by
                    the agent_id -- an operator gates agents exactly like capabilities).
      OQ4 BUDGET    refuse a non-positive declared budget BEFORE any LLM call (soft 1-step guard).
      1 RESOLVE     agent_id -> the agent contract (overlay-gated, tenant-scoped via agents_config).
      3 CREDENTIAL  select the F5 model/provider/key (native_local -> raise; byo_api_key wired).
      ASSEMBLE      build the agent's REAL contract (persona + I/O schema + tools) as the F2
                    BECOME ``system`` override -- the gap-closing loader.
      4 BUILD       CEXAgent(nucleus, kind, model).build(intent, system=<contract>) -- ONE chat().
      5 PERSIST     the SAME make_run_writer DbWriter into the SAME tenant_data (NO new tables).
      6 RETURN      an AgentRunResult (artifact + score + agent identity; NO api_key).

    FAIL-CLOSED: every deny raises CapabilityRefused. PERSIST is best-effort-after-pass (a DB
    failure is surfaced, never discards the artifact). The api_key is never echoed/logged/persisted.
    """
    # -- STEP 2a SCOPE: deny-by-default on the tenant (mirror the adapter rule). -------
    tid = (tenant_id or "").strip()
    if not tid:
        raise CapabilityRefused("missing_tenant", capability=agent_id)

    aid = (agent_id or "").strip()
    if not aid:
        raise CapabilityRefused(
            "unresolved_capability",
            tenant_id=tid,
            detail="empty agent_id",
        )

    run_inputs: Mapping[str, Any] = inputs if isinstance(inputs, Mapping) else {}

    # -- STEP 2b SCOPE: deny an agent not enabled for this tenant (BEFORE building). ----
    # REUSE run_capability._capability_enabled VERBATIM: the operator's enabled allowlist is
    # passed via options['enabled_capabilities'] (the dashboard injects the tenant's enabled
    # AGENT ids there). None/absent -> all allowed (the same deny-by-default-when-declared rule).
    if not _rc._capability_enabled(tid, aid, options):
        raise CapabilityRefused("capability_disabled", tenant_id=tid, capability=aid)

    # -- OQ4 BUDGET: refuse a non-positive declared budget before any LLM call. ---------
    _budget_guard(tid, aid, options)

    # -- STEP 1 RESOLVE: agent_id -> the agent contract (overlay-gated, tenant-scoped). -
    agent = _resolve_agent(tid, aid)
    nucleus, kind, pillar = _agent_runtime_tuple(agent)
    agent_name = str(agent.get("name") or agent.get("id") or aid)

    # -- STEP 3 CREDENTIAL: select the F5 model/provider/key (native_local -> raise). ---
    # REUSE run_capability._select_credential VERBATIM (OQ2: byo_api_key wired; native_local
    # raises native_local_headless_unresolved -- NOT faked).
    model, provider = _rc._select_credential(credential, tid, aid, default_model="")

    # -- ASSEMBLE: the agent's REAL contract as the F2 BECOME system override. ----------
    # THIS is the gap Phase B closes -- CEXAgent.build(intent, system=<contract>) HONORS the
    # agent (persona + typed I/O + declared tools) instead of a generic kind-only prompt.
    system_prompt = assemble_agent_contract(agent, run_inputs)
    intent = derive_intent(agent, run_inputs)

    # -- STEP 4 BUILD: run the EXISTING F1->F8 pipeline with the assembled contract. -----
    # ONE chat() (single step). REUSE the CEXAgent seam + _ProviderKeyScope VERBATIM.
    agent_cls = _rc.CEXAgent if _rc.CEXAgent is not None else _rc._import_cex_agent()
    build_result: Any
    with _rc._ProviderKeyScope(credential, provider):
        sdk_agent = agent_cls(nucleus=nucleus, kind=kind, model=model)
        # The ``system`` override is what feeds the assembled contract in (the gap-closer).
        build_result = sdk_agent.build(intent, system=system_prompt)

    # Normalise BuildResult fields (the real dataclass; a fake mimics the attrs).
    artifact = str(getattr(build_result, "artifact", "") or "")
    out_kind = str(getattr(build_result, "kind", kind) or kind)
    out_pillar = str(getattr(build_result, "pillar", pillar) or pillar)
    score = float(getattr(build_result, "score", 0.0) or 0.0)
    passed = bool(getattr(build_result, "passed", False))
    trace = str(getattr(build_result, "trace", "") or "")
    build_errors = list(getattr(build_result, "errors", []) or [])
    model_used = str(getattr(sdk_agent, "model", model) or model)

    result = AgentRunResult(
        tenant_id=tid,
        agent_id=aid,
        capability=aid,                          # the run "capability" is the agent_id
        agent_name=agent_name,
        kind=out_kind,
        pillar=out_pillar,
        nucleus=nucleus.upper(),
        artifact=artifact,
        score=score,
        passed=passed,
        status="produced",
        model_used=model_used,
        steps=1,
        trace=trace,
        errors=build_errors,
    )

    # -- STEP 5 PERSIST: the SAME make_run_writer DbWriter into the SAME tenant_data. ----
    # Byte-identical to run_capability's persist: best-effort-after-pass, persist ONLY a
    # passed artifact, never discard on DB failure. NO new tables -- the run lands in
    # tenant_data exactly like a capability run (agent_runs/agent_steps is Phase C). The meta
    # records the agent identity so the run row is attributable.
    if db is not None and passed:
        meta: dict[str, Any] = {
            "table": _TENANT_DATA_TABLE,
            "pillar": out_pillar,
            "nucleus": nucleus.upper(),
            "score": score,
            "model_used": model_used,
            "agent_id": aid,
            "agent_name": agent_name,
            "run_kind": "agent",
            "steps": 1,
        }
        if options and "meta" in options and isinstance(options["meta"], Mapping):
            meta.update(dict(options["meta"]))
        try:
            # The DbWriter Protocol's ``capability`` arg carries the agent_id (the run's
            # subject), exactly as a capability run passes its capability. The persisted kind
            # is the produced artifact kind. NO new tables.
            record_id = db.persist_artifact(tid, aid, out_kind, artifact, meta)
            result.record_id = str(record_id) if record_id is not None else None
            result.persisted = result.record_id is not None
            result.status = "persisted" if result.persisted else "produced_unpersisted"
        except Exception as exc:  # DB failure: surface, never discard the artifact.
            result.persisted = False
            result.status = "produced_unpersisted"
            result.errors.append("persist_failed: %s: %s" % (type(exc).__name__, exc))
    elif db is not None and not passed:
        result.status = "produced_unpersisted"

    # -- STEP 6 RETURN: artifact + score + agent identity (no api_key). -----------------
    return result


__all__ = [
    "Credential",
    "CapabilityResult",
    "CapabilityRefused",
    "DbWriter",
    "AgentRunResult",
    "run_agent",
    "assemble_agent_contract",
    "derive_intent",
    "MODE_BYO_API_KEY",
    "MODE_NATIVE_LOCAL",
    "MODE_PLATFORM",
]
