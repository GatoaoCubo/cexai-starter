"""SPARC phase templates + the pure phase helpers (cexai-specs/04_claude-flow).

This module holds the methodology's DATA and PURE FUNCTIONS -- no state, no I/O, no
LLM (Article XIV). ``SparcPipeline`` (methodology.py) composes these into the
stateful engine. The split keeps the 5 phase scaffolds, the explicit advance gates
(FR-002), the prior->next pre-population (P1 #2 / V04-F6), and the Code-phase
traceability (P1 #3) each independently testable.

Founder rule (v0.5 taxonomy ADR): the 5-phase pipeline REUSES the existing
``pipeline_template`` kind -- a scenario-indexed agent sequence WITH a revision loop
(the ``refinement`` phase). ``sparc_phase`` is NOT a new kind. Every ``SparcTemplate``
points at the one ``PIPELINE_TEMPLATE_ID`` reuse anchor; the five phase ids are the
v0.3 orchestration ``SparcPhaseId`` (imported, never redefined).

absorbs: 04_claude-flow
"""

from __future__ import annotations

import re
from typing import get_args

from cexai.distribution._shared.types import SparcTemplate

# Reuse the FROZEN v0.3 orchestration phase ids -- do NOT redefine (founder rule).
from cexai.orchestration._shared.types import SparcPhaseId

__all__ = [
    "PHASE_ORDER",
    "PIPELINE_TEMPLATE_ID",
    "GATE_CRITERIA",
    "prior_phase",
    "next_phase",
    "template_for",
    "gate_check",
    "build_content",
    "extract_requirement_lines",
    "field_lines",
    "prepopulation_ratio",
]

# The five SPARC phases in S-P-A-R-C order. The frozen ``SparcPhaseId`` Literal IS
# the contract; this tuple must match it exactly or the methodology has silently
# drifted from orchestration -- fail loudly at import (mirrors topology/registry.py).
PHASE_ORDER: tuple[SparcPhaseId, ...] = (
    "specification",
    "pseudocode",
    "architecture",
    "refinement",
    "code",
)
if PHASE_ORDER != get_args(SparcPhaseId):  # drift guard -- never silent
    raise RuntimeError(
        "SPARC PHASE_ORDER drifted from orchestration SparcPhaseId "
        f"{get_args(SparcPhaseId)!r}; the founder-rule reuse is broken."
    )

# The founder-rule reuse anchor: every phase template belongs to this one
# ``pipeline_template`` instance (NOT a rejected ``sparc_phase`` kind).
PIPELINE_TEMPLATE_ID: str = "pipeline_template:sparc_5phase"

_PHASE_TITLES: dict[SparcPhaseId, str] = {
    "specification": "Specification",
    "pseudocode": "Pseudocode",
    "architecture": "Architecture",
    "refinement": "Refinement",
    "code": "Code",
}

# FR-002 -- the explicit, human-readable advance gates surfaced on each
# ``SparcTemplate.gate_criteria``. The concrete machine check lives in ``gate_check``.
GATE_CRITERIA: dict[SparcPhaseId, tuple[str, ...]] = {
    "specification": (
        "at least one numbered requirement (req-N) is declared",
        "each requirement states observable behavior",
    ),
    "pseudocode": (
        "every Specification requirement is carried forward",
        "a function/step decomposition is present",
    ),
    "architecture": (
        "components/modules are identified",
        "each carried requirement maps to a component",
    ),
    "refinement": (
        "acceptance tests are stated for the carried requirements",
        "an optimization target is declared",
    ),
    "code": (
        "each implemented unit traces_to a SPEC.req-N",
        "all carried requirements are traced",
    ),
}

# The blank scaffolds returned by ``template(phase)`` -- the user-facing starting
# point for a phase (placeholders, not gated). ``advance`` produces the FILLED
# phase via ``build_content``; these are the empty molds.
_CONTENT_TEMPLATES: dict[SparcPhaseId, str] = {
    "specification": (
        "# Specification -- <feature>\n\n"
        "## Requirements\n"
        "- req-1: <observable behavior>\n"
        "- req-2: <input contract>\n"
        "- req-3: <output contract>\n"
    ),
    "pseudocode": (
        "# Pseudocode -- <feature>\n\n"
        "## Pre-populated from specification\n"
        "- req-1: <carried from Specification>\n\n"
        "## To complete\n"
        "- function_names: <fill>\n"
        "- steps: <fill>\n"
    ),
    "architecture": (
        "# Architecture -- <feature>\n\n"
        "## Pre-populated from pseudocode\n"
        "- req-1: <carried>\n\n"
        "## To complete\n"
        "- components: <fill>\n"
        "- module_boundaries: <fill>\n"
    ),
    "refinement": (
        "# Refinement -- <feature>\n\n"
        "## Pre-populated from architecture\n"
        "- req-1: <carried>\n\n"
        "## To complete\n"
        "- acceptance_tests: <fill>\n"
        "- optimization_target: <fill>\n"
    ),
    "code": (
        "# Code -- <feature>\n\n"
        "## Pre-populated from refinement\n"
        "- req-1: <carried>\n\n"
        "## To complete\n"
        "- implementation: <fill>\n\n"
        "## Traceability\n"
        "- traces_to: SPEC.req-1\n"
    ),
}

# Default FILLED Specification content used when ``advance(feature, 'specification')``
# is called without an explicit body: the reference feature's three requirements,
# real values so the Specification gate passes and the chain can walk (SC-001).
_DEFAULT_SPECIFICATION = (
    "# Specification -- {feature}\n\n"
    "## Requirements\n"
    "- req-1: deterministic stable ordering of the input sequence\n"
    "- req-2: accept any sequence of comparable items\n"
    "- req-3: return a new sorted sequence, input left unmutated\n"
)

_REQUIREMENT_LINE = re.compile(r"^-\s+(req-\d+)\s*:", re.IGNORECASE)
_REQUIREMENT_ID = re.compile(r"req-\d+", re.IGNORECASE)
_FIELD_LINE = re.compile(r"^-\s+([^:]+):\s*(.*)$")

# R-231 -- the bare, untouched placeholder VALUE the static blank scaffolds
# (``_CONTENT_TEMPLATES``) ship with, e.g. ``- function_names: <fill>``. Deliberately
# narrower than "any '<fill' substring": ``build_content``'s own auto-generated
# default always writes a MORE DESCRIPTIVE placeholder (``<fill the ordered algorithm
# steps>``), never this bare token, so the legitimate default walk (04 SC-001 --
# "without template modification") is unaffected by the check below.
_BARE_PLACEHOLDER_VALUE = "<fill>"


def prior_phase(phase: SparcPhaseId) -> SparcPhaseId | None:
    """The phase immediately before ``phase`` (``None`` for ``specification``)."""
    idx = PHASE_ORDER.index(phase)
    return None if idx == 0 else PHASE_ORDER[idx - 1]


def next_phase(phase: SparcPhaseId) -> SparcPhaseId | None:
    """The phase immediately after ``phase`` (``None`` for ``code``)."""
    idx = PHASE_ORDER.index(phase)
    return None if idx == len(PHASE_ORDER) - 1 else PHASE_ORDER[idx + 1]


def template_for(phase: SparcPhaseId) -> SparcTemplate:
    """The typed ``SparcTemplate`` scaffold for ``phase`` (FR-001/002): the blank
    mold + explicit advance gate, anchored to the reused ``pipeline_template``."""
    return SparcTemplate(
        phase=phase,
        pipeline_template_id=PIPELINE_TEMPLATE_ID,
        gate_criteria=GATE_CRITERIA[phase],
        content_template=_CONTENT_TEMPLATES[phase],
    )


def default_specification(feature_id: str) -> str:
    """The filled Specification body used when ``advance`` is called with no content
    -- the reference feature's three requirements (passes the Specification gate)."""
    return _DEFAULT_SPECIFICATION.format(feature=feature_id)


def _has_unedited_placeholder_field(content: str) -> bool:
    """True when any ``- name: value`` field line in ``content`` still carries the
    bare, untouched ``<fill>`` placeholder value (R-231): the caller copy-pasted the
    blank scaffold (``template_for(phase).content_template``) verbatim as their
    submission instead of doing the phase's work. This is a NECESSARY companion to
    the keyword checks below -- without it, a phase's own static field NAMES (e.g.
    ``function_names``, ``steps``) already contain the exact keyword the gate looks
    for, so the unedited mold satisfies its own gate regardless of ``value``."""
    return any(
        value.strip().lower() == _BARE_PLACEHOLDER_VALUE
        for _section, _name, value in field_lines(content)
    )


def gate_check(phase: SparcPhaseId, content: str) -> tuple[bool, str]:
    """The concrete machine gate for ``phase`` against ``content`` (FR-002).

    Returns ``(passed, reason)``; ``reason`` is empty when the gate passes and a
    human-readable cause when it fails (surfaced via ``SparcGateError``). Each check
    is a deterministic, offline content inspection -- no LLM judgement.
    """
    lowered = content.lower()
    if phase == "specification":
        if _REQUIREMENT_ID.search(content):
            return True, ""
        return False, "no numbered requirement (req-N) declared"
    if phase == "pseudocode":
        if _has_unedited_placeholder_field(content):
            return False, "content is the unedited blank template (a <fill> placeholder was never replaced)"
        if "function" in lowered or "step" in lowered:
            return True, ""
        return False, "no function/step decomposition present"
    if phase == "architecture":
        if _has_unedited_placeholder_field(content):
            return False, "content is the unedited blank template (a <fill> placeholder was never replaced)"
        if "component" in lowered or "module" in lowered:
            return True, ""
        return False, "no component/module identified"
    if phase == "refinement":
        if _has_unedited_placeholder_field(content):
            return False, "content is the unedited blank template (a <fill> placeholder was never replaced)"
        if "test" in lowered and "optimi" in lowered:
            return True, ""
        return False, "missing an acceptance test or an optimization target"
    # code
    if "traces_to: spec.req-" in lowered:
        return True, ""
    return False, "no traces_to: SPEC.req-N traceability for the implementation"


def extract_requirement_lines(content: str) -> tuple[str, ...]:
    """The ``- req-N: ...`` requirement lines in ``content``, verbatim (rstripped).
    These are the fields carried forward phase-to-phase (the traceability backbone)."""
    out: list[str] = []
    for raw in content.splitlines():
        if _REQUIREMENT_LINE.match(raw.strip()):
            out.append(raw.rstrip())
    return tuple(out)


def _requirement_id(line: str) -> str | None:
    """The ``req-N`` id within a requirement line (lowercased ``req-`` form)."""
    match = _REQUIREMENT_ID.search(line)
    return match.group(0).lower() if match else None


def build_content(
    phase: SparcPhaseId,
    *,
    feature_id: str,
    prior_phase: SparcPhaseId,
    prior_content: str,
) -> str:
    """Build the FILLED body for ``phase`` by pre-populating from ``prior_content``
    (P1 #2 / V04-F6: >= 30% of fields carried from the prior phase). The carried
    requirement lines form a ``## Pre-populated from {prior}`` section; the phase's
    own work goes under ``## To complete``. The Code phase additionally emits a
    ``## Traceability`` block of ``traces_to: SPEC.req-N`` (P1 #3)."""
    carried = extract_requirement_lines(prior_content)
    lines: list[str] = [f"# {_PHASE_TITLES[phase]} -- {feature_id}", ""]
    lines.append(f"## Pre-populated from {prior_phase}")
    lines.extend(carried if carried else ("- req-0: <no prior requirement carried>",))
    lines.append("")

    if phase == "pseudocode":
        lines += [
            "## To complete",
            "- function_names: <fill from the requirement decomposition>",
            "- steps: <fill the ordered algorithm steps>",
        ]
    elif phase == "architecture":
        lines += [
            "## To complete",
            "- components: <fill the module list>",
            "- module_boundaries: <fill responsibilities per component>",
        ]
    elif phase == "refinement":
        lines += [
            "## To complete",
            "- acceptance_tests: <fill one test per carried requirement>",
            "- optimization_target: <fill the complexity/throughput goal>",
        ]
    elif phase == "code":
        lines += [
            "## To complete",
            "- implementation: <fill the working code>",
            "",
            "## Traceability",
        ]
        for line in carried:
            req_id = _requirement_id(line)
            if req_id is not None:
                lines.append(f"- traces_to: SPEC.{req_id}")
    return "\n".join(lines) + "\n"


def field_lines(content: str) -> tuple[tuple[str, str, str], ...]:
    """Parse ``- name: value`` field lines, tagged by their ``## `` section.

    Returns a tuple of ``(section, name, value)`` -- ``section`` is the lowercased
    header text the field sits under (empty before the first header). The basis for
    ``prepopulation_ratio`` and any field-level assertion."""
    out: list[tuple[str, str, str]] = []
    section = ""
    for raw in content.splitlines():
        stripped = raw.strip()
        if stripped.startswith("## "):
            section = stripped[3:].strip().lower()
            continue
        match = _FIELD_LINE.match(stripped)
        if match:
            out.append((section, match.group(1).strip(), match.group(2).strip()))
    return tuple(out)


def prepopulation_ratio(content: str) -> float:
    """The fraction of field lines pre-populated from the prior phase (P1 #2): the
    count under a ``Pre-populated from ...`` section over the total field count.
    ``0.0`` when there are no fields (e.g. the entry Specification carries nothing)."""
    fields = field_lines(content)
    if not fields:
        return 0.0
    prepopulated = sum(1 for section, _, _ in fields if section.startswith("pre-populated"))
    return prepopulated / len(fields)
