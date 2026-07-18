#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI generic pipeline_template executor -- cex_run_pipeline_template (spec 06, P1).

THE generic multi-stage executor: it reads a ``pipeline_template`` contract by id, runs each
declared stage through the EXISTING capability spine (cex_run_capability.run_capability),
threads a TYPED handoff between stages, and applies the declared revision_loop + quality_gates.
It is to N-stage scenario pipelines what cex_run_pipeline is to the flagship research->ads chain:
a thin COMPOSITION over the shipped spine -- it does NOT fork the rails (the #1 rule).

WHY THIS EXISTS (spec 06 P1, "the keystone"): Track-1 chains (cex_run_pipeline) are production
grade + live, but the GENERIC executor was missing -- ``cex_sdk/pipeline.py`` is referenced by
~14 pipeline_template instances' instantiation snippets (Pipeline.from_template(...).run(...))
and DID NOT EXIST, so every one of those snippets import-errored. This module is the real
executor; cex_sdk/pipeline.py is a thin Pipeline.from_template wrapper that delegates here.

REUSE (do NOT fork the rails): this module IMPORTS the proven handoff/gate/persist discipline
from cex_run_pipeline VERBATIM (Credential / CapabilityResult / CapabilityRefused / DbWriter +
the run_capability entry it re-exports). The StageHandoff below GENERALIZES the ResearchHandoff
shape (a typed, self-documenting bus threaded between stages); it does NOT re-implement the
tenant/credential/deny seam (that is run_capability, called verbatim per stage).

THE FLOW (per stage, in declared order):
  1. RESOLVE   role -> capability slug. A stage declares a ``role`` + ``model_tier`` (the
               SE-scenario vocabulary: finder/analyst/coder/reviewer/tester/...). run_capability
               needs a CAPABILITY slug, so the role is resolved EXPLICITLY + overridably:
                 (a) stage['capability'] when the contract declares one (future-proof);
                 (b) a caller-supplied role->capability map (inputs/options 'stage_capabilities');
                 (c) else the role IS the capability slug -- and run_capability's deny-by-default
                     fail-closed governs (an unknown/disabled capability RAISES; we NEVER
                     fabricate a stage output to paper over a missing mapping).
  2. RUN       run_capability(tenant_id, capability, intent, credential, db=None, options, inputs)
               -- the spine builds + scores the stage artifact through the EXISTING F1..F8 path.
               db=None per stage so THIS driver owns the (optional) persist seam below.
  3. THREAD    the stage result feeds the StageHandoff: the next stage's intent is composed from
               the base task + the prior stage's artifact summary (PRODUCT-FIRST: the user's task
               always leads; upstream output is ADDITIVE context, never fabricated).
  4. GATE      if the stage is a MANDATORY quality gate (quality_gates.mandatory) it must PASS
               (run_capability's own passed/score). A gate FAIL enters the REVISION LOOP:
               re-run the prior implementation stage with a ## FEEDBACK note appended, up to
               revision_loop.max_iterations. Exhausted -> ESCALATE (status=escalated; halt).
  5. PERSIST   optional, best-effort-after-pass via the injected DbWriter (tenant_id EXPLICIT).
               DEGRADE-NEVER: db=None -> the run still completes, persisted=False.

HARD RULES (task contract + .claude/rules/ascii-code-rule.md):
  * ASCII-only; fully type-hinted; FAIL-CLOSED (a deny from the spine propagates; a mandatory
    gate that never passes -> escalated, never a silent fake-pass).
  * tenant_id is ALWAYS an explicit argument; never inferred from ambient global state.
  * NO concrete DB driver / NO LLM key imported at MODULE IMPORT (run_capability is import-light;
    the DbWriter + Credential are INJECTED).
  * DEGRADE-NEVER: a missing optional stage input -> skip the OPTIONAL stage honestly; a missing
    role->capability mapping -> the spine's deny seam fires (never fabricate output); db=None ->
    the run still completes.
  * NEVER-FABRICATE: a stage output is ONLY ever a real run_capability result. A skipped/failed
    stage is recorded as skipped/failed, never back-filled with invented content.

Spec: docs/specs/06_orchestration_engine/spec.md (P1 PIPELINES). Composes:
_tools/cex_run_capability.py (the spine, verbatim) + _tools/cex_run_pipeline.py (the proven
handoff/result/credential rails, IMPORTED not forked) + cex_sdk.workflow (Step/StepInput/
StepOutput typed-bus primitives, reused for the threaded handoff shape).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

# --------------------------------------------------------------------------- #
# REUSE the proven rails (the #1 rule: do NOT fork). cex_run_pipeline re-exports the SAME
# Credential / CapabilityResult / CapabilityRefused / DbWriter from cex_run_capability and
# owns run_capability indirectly; we import run_capability directly from the spine so a stage
# call is the EXACT shipped entry. Nothing here re-implements the tenant/credential/deny seam.
# --------------------------------------------------------------------------- #
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import cex_run_capability as _rc  # type: ignore[import]

# Re-export the SAME contract types so callers construct ONE set of objects regardless of which
# entry (run_capability / run_pipeline / run_pipeline_template) they call. NOT new types.
Credential = _rc.Credential
CapabilityResult = _rc.CapabilityResult
CapabilityRefused = _rc.CapabilityRefused
DbWriter = _rc.DbWriter
run_capability = _rc.run_capability
_TENANT_DATA_TABLE = _rc._TENANT_DATA_TABLE

_REPO_ROOT = Path(_TOOLS_DIR).resolve().parent
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

# The pipeline_template kind discriminator (used when scanning for the contract).
_KIND = "pipeline_template"

# Stage status vocabulary (mirrors cex_sdk.workflow.StepStatus values, kept ascii + local so
# this module does not hard-depend on the SDK at import; the SDK shapes are reused where bound).
STAGE_OK = "completed"
STAGE_FAILED = "failed"
STAGE_SKIPPED = "skipped"

# Pipeline-level status.
STATUS_COMPLETED = "completed"   # all mandatory gates passed
STATUS_ESCALATED = "escalated"   # a mandatory gate never passed within max_iterations
STATUS_ERROR = "error"           # a stage refused / a structural error


# --------------------------------------------------------------------------- #
# The resolved contract (id + stages + revision_loop + quality_gates).
# --------------------------------------------------------------------------- #
@dataclass
class PipelineTemplate:
    """A resolved pipeline_template contract.

    Loaded from the .md frontmatter (the STRUCTURED source of truth -- the compiler mangles
    revision_loop/quality_gates into prose, so the .md frontmatter is preferred) or, as a
    degrade fallback, from the compiled .yaml. ``stages`` is the ordered stage list; each stage
    is a dict carrying at least ``role`` + ``model_tier`` (+ optional ``optional``/``capability``).
    """

    template_id: str
    source_path: str
    scenario: str = ""
    stages: List[Dict[str, Any]] = field(default_factory=list)
    revision_loop: Dict[str, Any] = field(default_factory=dict)
    quality_gates: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def max_iterations(self) -> int:
        """revision_loop.max_iterations, clamped to [0, 5] (schema range 1-5; 0 = no retries)."""
        try:
            n = int(self.revision_loop.get("max_iterations", 0))
        except (TypeError, ValueError):
            return 0
        return max(0, min(5, n))

    @property
    def escalation_target(self) -> str:
        tgt = self.revision_loop.get("escalation_target")
        return str(tgt) if isinstance(tgt, str) and tgt.strip() else "n07"

    @property
    def mandatory_gates(self) -> List[str]:
        """The roles that are MANDATORY quality gates (quality_gates.mandatory). DEGRADE-NEVER:
        a mangled/absent block -> [] (no gate enforced; the run still threads + completes)."""
        m = self.quality_gates.get("mandatory")
        if isinstance(m, (list, tuple)):
            return [str(x).strip() for x in m if str(x).strip()]
        return []

    def stage_plan(self) -> List[Dict[str, Any]]:
        """The resolved, ordered plan rows (role / model_tier / optional / is_gate). Pure --
        the YAML->plan bridge the --dry-run prints (no run)."""
        gates = set(self.mandatory_gates)
        plan: List[Dict[str, Any]] = []
        for i, st in enumerate(self.stages, start=1):
            role = str(st.get("role", "")).strip()
            plan.append({
                "order": i,
                "role": role,
                "model_tier": str(st.get("model_tier", "")).strip(),
                "optional": bool(st.get("optional", False)),
                "is_gate": role in gates,
                "capability": _stage_capability_hint(st),
            })
        return plan


# --------------------------------------------------------------------------- #
# The typed handoff threaded between stages (GENERALIZES ResearchHandoff, plan S4.1 style).
# --------------------------------------------------------------------------- #
@dataclass
class StageHandoff:
    """The typed bus threaded stage->stage. GENERALIZES cex_run_pipeline.ResearchHandoff: instead
    of the fixed open_vars shape it carries the ordered list of completed stage outputs so any
    downstream stage reads a STABLE, self-documenting contract. PRODUCT-FIRST: the user's base
    task always leads the composed intent; prior outputs are ADDITIVE context (never fabricated).
    Modeled on cex_sdk.workflow.StepInput (content + previous_output + metadata)."""

    base_task: str
    completed: List[Dict[str, Any]] = field(default_factory=list)  # [{role, capability, summary}]
    session_state: Dict[str, Any] = field(default_factory=dict)

    def record(self, role: str, capability: str, result: CapabilityResult) -> None:
        """Record one COMPLETED stage's REAL output (never a fabricated one)."""
        self.completed.append({
            "role": role,
            "capability": capability,
            "passed": bool(result.passed),
            "score": float(result.score),
            "summary": _summarize_artifact(result.artifact),
        })

    def compose_intent(self, base_task: str, role: str, feedback: Optional[str] = None) -> str:
        """Compose the next stage's intent: the base task + a compact, machine-readable digest of
        the prior stages' real outputs + (on a revision) the ## FEEDBACK. NEVER invents a field."""
        lines: List[str] = [base_task.strip(), "", "## Pipeline stage: %s" % role]
        if self.completed:
            lines.append("")
            lines.append("## Upstream stage outputs (context -- do not fabricate)")
            for c in self.completed:
                lines.append("- [%s/%s] passed=%s score=%.1f: %s" % (
                    c["role"], c["capability"], c["passed"], c["score"], c["summary"]))
        if feedback:
            lines.append("")
            lines.append("## FEEDBACK (revision -- correct against these specifics only)")
            lines.append(feedback.strip())
        return "\n".join(lines).strip()


@dataclass
class StageRun:
    """One stage's outcome (REAL run_capability result OR an honest skip/fail). NO api_key here."""

    order: int
    role: str
    capability: str
    status: str = STAGE_FAILED               # completed | failed | skipped
    is_gate: bool = False
    optional: bool = False
    iterations: int = 1                       # how many times this stage ran (revision loop)
    result: Optional[CapabilityResult] = None
    record_id: Optional[str] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class PipelineTemplateResult:
    """Outcome of one pipeline_template run. NO api_key is ever present here.

    GENERALIZES cex_run_pipeline.PipelineResult: it carries the per-stage StageRun list + the
    pipeline-level status + the revision/escalation bookkeeping so a dashboard can render a single
    coherent multi-stage view. ``status`` is escalated when a mandatory gate never passed."""

    template_id: str
    tenant_id: str
    scenario: str = ""
    status: str = STATUS_ERROR               # completed | escalated | error
    stages: List[StageRun] = field(default_factory=list)
    revisions: int = 0                        # total revision re-runs across the pipeline
    escalation_target: str = ""
    errors: List[str] = field(default_factory=list)

    def stage(self, role: str) -> Optional[StageRun]:
        for s in self.stages:
            if s.role == role:
                return s
        return None


# --------------------------------------------------------------------------- #
# THE entry.
# --------------------------------------------------------------------------- #
def run_pipeline_template(
    template_id: str,
    inputs: Optional[Mapping[str, Any]] = None,
    *,
    tenant_id: str,
    credential: Credential,
    db: Optional[DbWriter] = None,
    task: Optional[str] = None,
    options: Optional[Mapping[str, Any]] = None,
    run_capability_fn: Any = None,
    search_roots: Optional[List[Path]] = None,
    template: Optional[PipelineTemplate] = None,
) -> PipelineTemplateResult:
    """Run a pipeline_template contract by id for ONE tenant. See module docstring.

    Args:
      template_id: the contract id (``p12_pt_8f_decomposed``) or filename
        (``p12_pt_8f_decomposed.yaml`` / ``.md``). Resolved across the repo. Ignored when an
        already-resolved ``template`` is passed (the cex_sdk.Pipeline facade does the resolution
        once at from_template time and hands the resolved contract straight in).
      inputs: the optional typed payload threaded to run_capability per stage (uploads/urls/
        scalars) + the optional ``task`` / ``stage_capabilities`` keys (see below).
      tenant_id: EXPLICIT tenant scope (deny-by-default; empty -> CapabilityRefused).
      credential: the F5 auth seam (INJECTED; api_key never logged/persisted).
      db: optional DbWriter (best-effort-after-pass; db=None -> persisted=False, run still completes).
      task: the base task string (PRODUCT-FIRST intent lead). Falls back to inputs['task'] or the
        template scenario text. NEVER fabricated.
      options: passed through to run_capability per stage (e.g. enabled_capabilities). The
        ``stage_capabilities`` key (a role->capability dict) overrides role-as-capability resolution.
      run_capability_fn: INJECTABLE spine (defaults to the real run_capability). Tests pass a fake
        to prove stage-threading / the revision loop / the gate firing offline.

    FAIL-CLOSED: a deny from the spine (missing tenant / disabled capability / native_local /
    missing credential) PROPAGATES as CapabilityRefused. A mandatory gate that never passes within
    max_iterations -> status=escalated (NEVER a silent fake-pass). DEGRADE-NEVER: db=None -> the
    run still completes; an OPTIONAL stage whose capability is unresolved/refused -> skipped
    honestly. NEVER-FABRICATE: a stage output is only ever a real run_capability result.
    """
    tid = (tenant_id or "").strip()
    if not tid:
        # Mirror the spine deny seam exactly (fail-closed before any resolution).
        raise CapabilityRefused("missing_tenant", capability=_KIND)

    spine = run_capability_fn or run_capability
    opts: Dict[str, Any] = dict(options) if isinstance(options, Mapping) else {}
    in_payload: Dict[str, Any] = dict(inputs) if isinstance(inputs, Mapping) else {}

    if template is None:
        template = resolve_pipeline_template(template_id, search_roots=search_roots)
    base_task = _resolve_base_task(task, in_payload, template)

    result = PipelineTemplateResult(
        template_id=template.template_id,
        tenant_id=tid,
        scenario=template.scenario,
        escalation_target=template.escalation_target,
    )

    # The role->capability override map (caller-supplied), consulted before role-as-capability.
    stage_cap_map = _coerce_str_map(opts.get("stage_capabilities") or in_payload.get("stage_capabilities"))

    handoff = StageHandoff(base_task=base_task)
    gates = set(template.mandatory_gates)
    plan = template.stage_plan()

    # The index of the last NON-GATE implementation stage (the revision loop re-runs IT on a gate
    # fail -- a gate routes back to the prior implementation stage, per the revision_loop contract).
    last_impl_idx: Optional[int] = None

    for row in plan:
        role = row["role"]
        is_gate = row["is_gate"]
        optional = row["optional"]
        capability = _resolve_stage_capability(row, stage_cap_map)

        stage_run = StageRun(
            order=row["order"], role=role, capability=capability,
            is_gate=is_gate, optional=optional,
        )

        if not capability:
            # No resolvable capability AND no role to use as a slug -> skip if optional, else error.
            stage_run.status = STAGE_SKIPPED if optional else STAGE_FAILED
            msg = "stage_unresolved: role=%r has no capability mapping" % role
            stage_run.errors.append(msg)
            result.stages.append(stage_run)
            if optional:
                continue
            result.errors.append(msg)
            result.status = STATUS_ERROR
            return result

        intent = handoff.compose_intent(base_task, role)
        try:
            cap_result = _run_stage(spine, tid, capability, intent, credential, opts, in_payload)
        except CapabilityRefused as exc:
            # The spine refused (disabled/unresolved/native_local/...). An OPTIONAL stage degrades
            # to a clean skip; a MANDATORY stage fails-closed (the run errors -- never fabricated).
            stage_run.errors.append("refused: %s" % exc.reason)
            if optional:
                stage_run.status = STAGE_SKIPPED
                result.stages.append(stage_run)
                continue
            stage_run.status = STAGE_FAILED
            result.stages.append(stage_run)
            result.errors.append("stage_refused[%s]: %s" % (role, exc.reason))
            result.status = STATUS_ERROR
            return result

        stage_run.result = cap_result

        # -- GATE handling + revision loop ------------------------------------------------ #
        if is_gate and not cap_result.passed:
            escalated = _run_revision_loop(
                spine, tid, credential, opts, in_payload, template, handoff,
                base_task, role, capability, stage_run, last_impl_idx, result,
            )
            if escalated:
                result.status = STATUS_ESCALATED
                # Persist whatever real outputs we have so the employee sees WHY it stopped.
                _persist_stage(db, tid, stage_run, result)
                result.stages.append(stage_run)
                return result
            # The loop drove the gate to PASS -- stage_run.result now holds the passed gate result
            # (and the loop already threaded it into the handoff). Persist + fall through.
            stage_run.status = STAGE_OK
            _persist_stage(db, tid, stage_run, result)
            result.stages.append(stage_run)
            continue

        # The stage produced a real result -> record it + (best-effort) persist + thread it on.
        # (cap_result is authoritative here: a non-gate stage, or a gate that PASSED on the first
        # try -- neither went through the revision loop above.)
        stage_run.status = STAGE_OK if cap_result.passed else STAGE_FAILED
        if cap_result.passed:
            handoff.record(role, capability, cap_result)
            _persist_stage(db, tid, stage_run, result)
        else:
            # A non-gate stage that did not pass is surfaced but does NOT halt the pipeline (only
            # MANDATORY gates halt). It is recorded honestly as failed (never back-filled).
            stage_run.errors.append("stage_below_gate: score=%.2f" % cap_result.score)
            result.errors.append("stage_not_passed[%s]: score=%.2f" % (role, cap_result.score))

        result.stages.append(stage_run)
        if not is_gate:
            last_impl_idx = len(result.stages) - 1

    result.status = STATUS_COMPLETED
    return result


# --------------------------------------------------------------------------- #
# Stage execution + revision loop.
# --------------------------------------------------------------------------- #
def _run_stage(
    spine: Any,
    tenant_id: str,
    capability: str,
    intent: str,
    credential: Credential,
    options: Mapping[str, Any],
    inputs: Mapping[str, Any],
) -> CapabilityResult:
    """Run ONE stage via the spine (run_capability), db=None (this driver owns persist). The
    deny/credential/budget seam is REUSED verbatim -- a CapabilityRefused propagates."""
    return spine(
        tenant_id, capability, intent, credential,
        db=None,
        options=dict(options) if options else None,
        inputs=dict(inputs) if inputs else None,
    )


def _run_revision_loop(
    spine: Any,
    tenant_id: str,
    credential: Credential,
    options: Mapping[str, Any],
    inputs: Mapping[str, Any],
    template: PipelineTemplate,
    handoff: StageHandoff,
    base_task: str,
    gate_role: str,
    gate_capability: str,
    gate_stage: StageRun,
    last_impl_idx: Optional[int],
    result: PipelineTemplateResult,
) -> bool:
    """Run the declared revision loop after a MANDATORY gate fails.

    Re-runs the PRIOR implementation stage with a ## FEEDBACK note (the gate's failing score),
    then re-runs the gate. Up to max_iterations. Returns True iff the gate NEVER passed (the
    pipeline must escalate). DEGRADE-NEVER: max_iterations==0 -> no retries, escalate immediately.
    NEVER-FABRICATE: every re-run is a real spine call; an exhausted loop escalates honestly."""
    max_iters = template.max_iterations
    if max_iters <= 0:
        gate_stage.errors.append("gate_failed_no_retries: escalate to %s" % template.escalation_target)
        return True

    # Resolve the implementation stage to re-run (the last non-gate stage executed so far). A gate
    # routes back to the prior implementation stage (the revision_loop contract). None when the
    # gate is the first stage (no impl to re-run) -> only the gate is retried.
    impl_stage: Optional[StageRun] = result.stages[last_impl_idx] if last_impl_idx is not None else None

    for attempt in range(1, max_iters + 1):
        gate_stage.iterations = attempt + 1  # the gate has now run attempt+1 times total
        result.revisions += 1

        feedback = "gate '%s' failed (score=%.2f). Revise to satisfy the quality gate." % (
            gate_role, gate_stage.result.score if gate_stage.result else 0.0)

        # Re-run the prior implementation stage with feedback (if there is one to re-run).
        if impl_stage is not None and impl_stage.capability:
            impl_intent = handoff.compose_intent(base_task, impl_stage.role, feedback=feedback)
            try:
                impl_res = _run_stage(
                    spine, tenant_id, impl_stage.capability, impl_intent, credential, options, inputs,
                )
                impl_stage.iterations += 1
                impl_stage.result = impl_res
                impl_stage.status = STAGE_OK if impl_res.passed else STAGE_FAILED
            except CapabilityRefused as exc:
                impl_stage.errors.append("revision_refused: %s" % exc.reason)
                gate_stage.errors.append("revision_impl_refused: %s" % exc.reason)
                return True  # cannot revise -> escalate

        # Re-run the gate.
        gate_intent = handoff.compose_intent(base_task, gate_role, feedback=feedback)
        try:
            gate_res = _run_stage(
                spine, tenant_id, gate_capability, gate_intent, credential, options, inputs,
            )
        except CapabilityRefused as exc:
            gate_stage.errors.append("revision_gate_refused: %s" % exc.reason)
            return True
        gate_stage.result = gate_res

        if gate_res.passed:
            gate_stage.status = STAGE_OK
            handoff.record(gate_role, gate_capability, gate_res)
            return False  # gate passed -> no escalation

    # Loop exhausted; the gate never passed.
    gate_stage.errors.append(
        "gate_failed_after_%d_iterations: escalate to %s" % (max_iters, template.escalation_target))
    result.errors.append("gate_escalated[%s] after %d iterations" % (gate_role, max_iters))
    return True


def _persist_stage(
    db: Optional[DbWriter],
    tenant_id: str,
    stage: StageRun,
    result: PipelineTemplateResult,
) -> None:
    """Best-effort-after-pass persist of one stage's REAL artifact. DEGRADE-NEVER: db=None ->
    nothing persisted, the run proceeds. A DB failure is surfaced (error appended) but never
    discards the artifact. Only a PASSED stage is persisted (persist-after-pass, mirrors the spine)."""
    if db is None or stage.result is None or not stage.result.passed:
        return
    r = stage.result
    meta: Dict[str, Any] = {
        "table": _TENANT_DATA_TABLE,
        "capability": stage.capability,
        "pillar": r.pillar,
        "nucleus": r.nucleus,
        "score": r.score,
        "model_used": r.model_used,
        "pipeline_template": result.template_id,
        "stage_role": stage.role,
        "stage_order": stage.order,
    }
    try:
        rid = db.persist_artifact(tenant_id, stage.capability, r.kind, r.artifact, meta)
        stage.record_id = str(rid) if rid is not None else None
    except Exception as exc:  # surface, never discard
        stage.errors.append("persist_failed[%s]: %s: %s" % (stage.capability, type(exc).__name__, exc))


# --------------------------------------------------------------------------- #
# Contract resolution + parsing (the YAML/MD -> PipelineTemplate bridge).
# --------------------------------------------------------------------------- #
def resolve_pipeline_template(
    template_id: str,
    *,
    search_roots: Optional[List[Path]] = None,
) -> PipelineTemplate:
    """Resolve a pipeline_template by id (or filename) into a PipelineTemplate.

    PREFERS the .md source frontmatter (the compiler mangles revision_loop/quality_gates into
    prose strings; the .md frontmatter keeps them as proper dicts). Falls back to the compiled
    .yaml only when no .md exists. Raises FileNotFoundError when neither is found (fail-closed --
    a missing contract is NEVER silently substituted)."""
    stem = _normalize_id(template_id)
    roots = search_roots or [_REPO_ROOT]

    md_path = _find_first(roots, "%s.md" % stem)
    yaml_path = _find_first(roots, "%s.yaml" % stem)

    if md_path is None and yaml_path is None:
        raise FileNotFoundError(
            "pipeline_template not found: %r (looked for %s.md / %s.yaml under %s)"
            % (template_id, stem, stem, [str(r) for r in roots]))

    # Prefer the .md frontmatter (structured source of truth). Use the compiled .yaml only to
    # backfill ``stages`` if the .md frontmatter somehow lacks a clean stages list.
    data: Dict[str, Any] = {}
    source = ""
    if md_path is not None:
        data = _parse_frontmatter(md_path.read_text(encoding="utf-8", errors="replace"))
        source = str(md_path)
    if (not data or not _has_clean_stages(data)) and yaml_path is not None:
        ydata = _load_yaml(yaml_path.read_text(encoding="utf-8", errors="replace"))
        if not data:
            data, source = ydata, str(yaml_path)
        elif _has_clean_stages(ydata):
            data["stages"] = ydata.get("stages")  # backfill the clean stage list only

    if str(data.get("kind", _KIND)) != _KIND:
        # Be lenient: warn-shaped (the id matched a file) but keep going -- some instances omit
        # kind in frontmatter. We do NOT fabricate; we simply trust the resolved file's stages.
        pass

    return PipelineTemplate(
        template_id=str(data.get("id", stem)),
        source_path=source,
        scenario=_scenario_text(data.get("scenario")),
        stages=_coerce_stages(data.get("stages")),
        revision_loop=_coerce_dict(data.get("revision_loop")),
        quality_gates=_coerce_dict(data.get("quality_gates")),
        raw=data,
    )


def _parse_frontmatter(text: str) -> Dict[str, Any]:
    """Extract + parse the YAML frontmatter block. DEGRADE-NEVER: no frontmatter / no PyYAML /
    a parse error -> {} (the caller then falls back to the compiled yaml or errors honestly)."""
    if not isinstance(text, str) or not text:
        return {}
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    return _load_yaml(m.group(1))


def _load_yaml(text: str) -> Dict[str, Any]:
    try:
        import yaml  # type: ignore[import]
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _has_clean_stages(data: Mapping[str, Any]) -> bool:
    """True iff ``stages`` is a non-empty list of dicts each carrying a ``role`` (the clean shape,
    not a compiler-mangled prose string)."""
    stages = data.get("stages")
    if not isinstance(stages, (list, tuple)) or not stages:
        return False
    return all(isinstance(s, Mapping) and str(s.get("role", "")).strip() for s in stages)


def _coerce_stages(value: Any) -> List[Dict[str, Any]]:
    """Coerce the stages field into a clean ordered list of dicts. A mangled/absent value -> []
    (the run then has no stages -> a clean empty pipeline, never a fabricated one)."""
    if not isinstance(value, (list, tuple)):
        return []
    out: List[Dict[str, Any]] = []
    for s in value:
        if isinstance(s, Mapping) and str(s.get("role", "")).strip():
            out.append(dict(s))
    return out


def _coerce_dict(value: Any) -> Dict[str, Any]:
    """Coerce a frontmatter field into a dict. The compiler mangles revision_loop/quality_gates
    into a PROSE STRING in the compiled yaml; in that case we return {} so the property defaults
    apply (DEGRADE-NEVER) -- the .md frontmatter (preferred) keeps the real dict."""
    return dict(value) if isinstance(value, Mapping) else {}


def _coerce_str_map(value: Any) -> Dict[str, str]:
    if not isinstance(value, Mapping):
        return {}
    return {str(k).strip(): str(v).strip() for k, v in value.items() if str(v).strip()}


# --------------------------------------------------------------------------- #
# Helpers (PURE).
# --------------------------------------------------------------------------- #
def _normalize_id(template_id: str) -> str:
    """Strip a trailing .yaml/.md/.yml extension + any directory -> the bare stem to search for."""
    s = (template_id or "").strip()
    s = Path(s).name  # drop any directory component
    for ext in (".yaml", ".yml", ".md"):
        if s.lower().endswith(ext):
            return s[: -len(ext)]
    return s


def _find_first(roots: List[Path], filename: str) -> Optional[Path]:
    """Find the first file named ``filename`` under any root (rglob). Skips the gitignored
    ``compiled`` dirs for the .md search is NOT done here -- callers pass the right filename
    (.md vs .yaml) and we search everywhere; compiled .yaml live under */compiled/ by design."""
    for root in roots:
        try:
            for p in sorted(root.rglob(filename)):
                if p.is_file():
                    return p
        except OSError:
            continue
    return None


def _stage_capability_hint(stage: Mapping[str, Any]) -> str:
    """The capability a stage WOULD resolve to from its own fields (declared capability else role).
    The caller-supplied stage_capabilities map can still override at run time (see _resolve)."""
    cap = str(stage.get("capability", "")).strip()
    if cap:
        return cap
    return str(stage.get("role", "")).strip()


def _resolve_stage_capability(row: Mapping[str, Any], stage_cap_map: Mapping[str, str]) -> str:
    """Resolve a plan row's capability slug: (a) caller override map by role, else (b) the
    declared/role hint. Empty string when nothing resolves (the caller then skips/errors --
    NEVER fabricates a capability)."""
    role = str(row.get("role", "")).strip()
    if role in stage_cap_map:
        return stage_cap_map[role]
    return str(row.get("capability") or "").strip()


def _resolve_base_task(task: Optional[str], inputs: Mapping[str, Any], template: PipelineTemplate) -> str:
    """The PRODUCT-FIRST base task: explicit ``task`` arg > inputs['task'] > the template scenario
    text > the template id. NEVER fabricated -- it is always real caller/contract text."""
    for cand in (task, inputs.get("task"), template.scenario, template.template_id):
        if isinstance(cand, str) and cand.strip():
            return cand.strip()
    return template.template_id


def _scenario_text(value: Any) -> str:
    """The scenario as a short string (the enum slug in .md frontmatter, or the first line of the
    compiler-expanded prose in the compiled yaml). NEVER fabricated."""
    if not isinstance(value, str):
        return ""
    return value.strip().splitlines()[0].strip() if value.strip() else ""


def _summarize_artifact(artifact: str, limit: int = 240) -> str:
    """A compact, single-line digest of a stage artifact for the handoff (title/first prose line).
    PURE + ascii-safe; NEVER fabricates content (empty artifact -> '')."""
    if not isinstance(artifact, str) or not artifact:
        return ""
    body = artifact
    m = _FRONTMATTER_RE.match(artifact)
    if m:
        body = artifact[m.end():]
    for line in body.splitlines():
        s = line.strip().lstrip("#").strip()
        if s:
            s = s.encode("ascii", "ignore").decode("ascii")
            return s[:limit]
    return ""


# --------------------------------------------------------------------------- #
# CLI (--id <tid> [--dry-run]).
# --------------------------------------------------------------------------- #
def _format_plan(template: PipelineTemplate) -> str:
    """Render the resolved stage plan as a human-readable table (the --dry-run output)."""
    lines: List[str] = []
    lines.append("pipeline_template: %s" % template.template_id)
    lines.append("source:            %s" % template.source_path)
    lines.append("scenario:          %s" % (template.scenario or "(none)"))
    lines.append("revision_loop:     max_iterations=%d escalation_target=%s"
                 % (template.max_iterations, template.escalation_target))
    lines.append("quality_gates:     mandatory=%s" % (template.mandatory_gates or "(none)"))
    lines.append("")
    lines.append("  # | role        | tier   | gate | optional | capability")
    lines.append("  --+-------------+--------+------+----------+-----------")
    for row in template.stage_plan():
        lines.append("  %d | %-11s | %-6s | %-4s | %-8s | %s" % (
            row["order"], row["role"][:11], row["model_tier"][:6],
            "yes" if row["is_gate"] else "no",
            "yes" if row["optional"] else "no",
            row["capability"] or "(role-as-capability)"))
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cex_run_pipeline_template",
        description="Generic pipeline_template executor (spec 06 P1). "
                    "--dry-run validates + prints the resolved stage plan (no run).",
    )
    parser.add_argument("--id", required=True, help="pipeline_template id or filename (.md/.yaml).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Resolve + validate + print the stage plan WITHOUT running any stage.")
    parser.add_argument("--json", action="store_true", help="Emit the resolved plan as JSON.")
    args = parser.parse_args(argv)

    try:
        template = resolve_pipeline_template(args.id)
    except FileNotFoundError as exc:
        print("[FAIL] %s" % exc)
        return 1

    if args.json:
        payload = {
            "template_id": template.template_id,
            "source_path": template.source_path,
            "scenario": template.scenario,
            "max_iterations": template.max_iterations,
            "escalation_target": template.escalation_target,
            "mandatory_gates": template.mandatory_gates,
            "stages": template.stage_plan(),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=True))
    else:
        print(_format_plan(template))

    if not args.dry_run:
        # A real run needs an explicit tenant + an injected Credential (an api_key the CLI does
        # NOT hold). Per spec 06 (no real-LLM-spend without explicit wiring) the CLI surfaces the
        # plan; a real run is driven programmatically (run_pipeline_template) or via cex_sdk.Pipeline
        # with a Credential. This is fail-closed by design -- we NEVER fabricate a run here.
        print("")
        print("[i] Plan resolved. A real run requires an explicit tenant_id + Credential; drive it")
        print("    via run_pipeline_template(...) or cex_sdk.pipeline.Pipeline. Use --dry-run to")
        print("    validate only. (The CLI does not hold credentials -- no live spend from here.)")
    if not template.stages:
        print("[WARN] resolved 0 clean stages (the contract's stages field may be prose-mangled).")
        return 1
    return 0


__all__ = [
    "run_pipeline_template",
    "resolve_pipeline_template",
    "PipelineTemplate",
    "PipelineTemplateResult",
    "StageHandoff",
    "StageRun",
    "Credential",
    "CapabilityResult",
    "CapabilityRefused",
    "DbWriter",
    "STATUS_COMPLETED",
    "STATUS_ESCALATED",
    "STATUS_ERROR",
]


if __name__ == "__main__":
    sys.exit(main())
