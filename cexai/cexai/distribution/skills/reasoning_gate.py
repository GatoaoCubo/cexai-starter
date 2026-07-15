"""Reasoning-trace gate -- the F7 GOVERN seam for compiler-initiated skill installs.

cexai-specs/13_vercel-skills SC-005 / FR-012: every skill install INITIATED BY THE
COMPILER MUST emit a non-empty reasoning_trace; its absence is a HARD FAIL at F7
GOVERN. ``CrossAgentInstaller`` already EMITS a reasoning_trace per install (13
FR-012, ``installer.reasoning_trace``); this module is the per-ARTIFACT F7
enforcement decision the CEX 8F engine consults -- given a compiler-initiated
skill-install artifact's frontmatter + body, decide whether it carries the required
reasoning_trace and must therefore HARD-FAIL the quality gate when it does not.

Design (mirrors the v0.4-W2 ``citation_gate`` discipline -- Article VIII, stdlib only):
  * Pure + deterministic. No yaml dep: the engine passes its already-parsed
    frontmatter dict; ``evaluate_text`` ships a tiny line parser for standalone use
    (demos / benches).
  * CONSERVATIVE by construction -- the gate APPLIES only when the artifact
    EXPLICITLY signals it is a COMPILER-INITIATED skill install (a truthy
    frontmatter marker, OR a ``compiler`` initiator paired with a skill-install
    context). The 301 existing CEX kinds carry none of these signals -- and an
    ordinary ``skill`` kind that is NOT a compiler-initiated install carries no
    initiator either -- so ``applies`` is ``False`` for every existing artifact and
    F7 behaves byte-identically. This is the zero-regression contract: the gate can
    only ever ADD a failure to an artifact that DECLARED it is a compiler-initiated
    skill install.

This module does NOT raise -- it returns a verdict (the HARD-FAIL semantics live in
the F7 gate that folds the verdict in, exactly as ``citation_gate`` documents).

absorbs: 13_vercel-skills/reasoning-gate
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

__all__ = [
    "COMPILER_INSTALL_MARKERS",
    "REQUIRES_REASONING_MARKERS",
    "ReasoningTraceGateResult",
    "is_compiler_initiated_install",
    "requires_reasoning_trace",
    "has_reasoning_trace",
    "evaluate",
    "evaluate_general",
    "evaluate_text",
]

# Frontmatter keys whose truthy value DECLARES the artifact is a compiler-initiated
# skill install (the zero-false-positive primary signal the compiler install path
# sets). The 301 existing kinds never carry one of these.
COMPILER_INSTALL_MARKERS = (
    "compiler_initiated_install",
    "compiler_initiated_skill_install",
    "skill_install_compiler_initiated",
)

# The structured fallback: a ``compiler`` initiator paired with a skill-install
# context. Both must hold, so an ordinary skill artifact (no initiator) never fires.
_INITIATOR_KEYS = ("install_initiator", "initiated_by", "initiator")
_COMPILER_VALUES = frozenset(("compiler", "prompt_compiler", "cex_compiler"))
_SKILL_INSTALL_FLAG_KEYS = ("skill_install", "is_skill_install")
_SKILL_INSTALL_KINDS = frozenset(("skill", "skill_install"))

_TRUTHY_STRINGS = frozenset(("true", "yes", "1", "on"))

# A reasoning_trace heading in the body (Reasoning Trace / Reasoning / Trace).
_REASONING_TRACE_HEADING_RE = re.compile(
    r"^\s{0,3}#{1,6}\s+(reasoning[ _-]?trace|reasoning|trace)\b",
    re.IGNORECASE | re.MULTILINE,
)
# A wikilink whose target names a reasoning_trace artifact ([[...reasoning_trace...]]).
_REASONING_WIKILINK_RE = re.compile(
    r"\[\[[^\]]*reasoning[ _-]?trace[^\]]*\]\]", re.IGNORECASE
)


@dataclass(frozen=True, slots=True)
class ReasoningTraceGateResult:
    """The F7 reasoning-trace-gate verdict for one artifact.

    ``applies`` is ``True`` when the compiler-initiated skill-install signal is
    present (the gate is in scope for this artifact); ``fails`` is ``True`` only when
    it ``applies`` AND no non-empty reasoning_trace is present -- the missing-trace
    HARD-FAIL (13 SC-005). ``reason`` is the human-readable cause surfaced into the
    F7 feedback. When ``applies`` is ``False`` the gate is a NO-OP (``fails`` is
    ``False``) and the engine adds no gate at all, so existing artifacts are
    unaffected."""

    applies: bool
    fails: bool
    reason: str

    @property
    def passed(self) -> bool:
        """``True`` when the gate does not fail (out of scope, or trace present)."""
        return not self.fails


def _is_truthy(value: Any) -> bool:
    """Whether a frontmatter scalar counts as a truthy marker."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in _TRUTHY_STRINGS
    return False


def _scalar_lower(frontmatter: Mapping[str, Any], keys: tuple[str, ...]) -> str:
    """The first non-empty string value among ``keys``, lowercased (else ``''``)."""
    for key in keys:
        val = frontmatter.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip().lower()
    return ""


def _is_skill_install_context(frontmatter: Mapping[str, Any]) -> bool:
    """Whether the frontmatter places the artifact in a skill-install context:
    a ``skill`` / ``skill_install`` kind, or a truthy skill-install flag."""
    kind = frontmatter.get("kind")
    if isinstance(kind, str) and kind.strip().lower() in _SKILL_INSTALL_KINDS:
        return True
    return any(_is_truthy(frontmatter.get(k)) for k in _SKILL_INSTALL_FLAG_KEYS)


def is_compiler_initiated_install(frontmatter: Mapping[str, Any], body: str) -> bool:
    """Whether the artifact signals a COMPILER-INITIATED skill install (gate in scope).

    Two independent signals (either suffices):
      1. EXPLICIT -- a truthy ``COMPILER_INSTALL_MARKERS`` frontmatter key (the
         zero-false-positive primary signal the compiler install path sets).
      2. STRUCTURED -- a ``compiler`` initiator (``install_initiator`` /
         ``initiated_by`` / ``initiator``) PAIRED with a skill-install context
         (``kind: skill`` / ``skill_install``, or a truthy ``skill_install`` flag).
    An ordinary skill artifact carries no initiator, so neither signal fires."""
    if any(_is_truthy(frontmatter.get(k)) for k in COMPILER_INSTALL_MARKERS):
        return True
    initiator = _scalar_lower(frontmatter, _INITIATOR_KEYS)
    if initiator in _COMPILER_VALUES and _is_skill_install_context(frontmatter):
        return True
    return False


def _trace_section_has_content(body: str) -> bool:
    """Whether a ``## Reasoning Trace`` heading is followed by a non-empty content
    line (an empty section under the heading does NOT satisfy the non-empty bar)."""
    match = _REASONING_TRACE_HEADING_RE.search(body)
    if not match:
        return False
    after = body[match.end():]
    newline = after.find("\n")  # drop the rest of the heading's own line first
    after = after[newline + 1:] if newline != -1 else ""
    for raw in after.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            return False  # next heading reached, section empty
        return True  # first content line under the heading
    return False


def has_reasoning_trace(frontmatter: Mapping[str, Any], body: str) -> bool:
    """Whether the artifact carries a non-empty reasoning_trace.

    Broad on purpose -- the gate only FAILS an artifact that
    ``is_compiler_initiated_install`` AND lacks ANY of these, so a generous detector
    minimizes false fails:
      * a non-empty frontmatter ``reasoning_trace`` / ``reasoning_traces`` list, or a
        non-empty ``reasoning_trace`` string; a truthy ``has_reasoning_trace`` /
        ``reasoning_trace_id`` field;
      * a wikilink to a ``reasoning_trace`` kind artifact;
      * a Reasoning Trace / Reasoning / Trace heading followed by content."""
    for key in ("reasoning_trace", "reasoning_traces", "trace"):
        val = frontmatter.get(key)
        if isinstance(val, (list, tuple)) and any(str(v).strip() for v in val):
            return True
        if isinstance(val, str) and val.strip():
            return True
    for key in ("has_reasoning_trace", "reasoning_trace_id", "trace_id"):
        if _is_truthy(frontmatter.get(key)):
            return True
    if _REASONING_WIKILINK_RE.search(body):
        return True
    if _trace_section_has_content(body):
        return True
    return False


# -- general (spec-agnostic) scope --------------------------------------------
# Generalizes the gate beyond compiler-initiated skill installs to ANY F6 PRODUCE
# that declares it must show its reasoning. These markers are the explicit opt-in;
# the 301 existing CEX kinds carry none of them, so the general path is a NO-OP for
# the whole corpus (the same zero-regression contract the compiler-install path
# keeps). Marker-based ONLY -- it deliberately does NOT fold in the compiler-install
# structured inference, so a caller (e.g. the constitution's Commandment IV) can
# consult ``requires_reasoning_trace`` for SCOPE without dragging in the
# initiator/skill-install pairing. ``evaluate_general`` unions the general markers
# with the compiler-install special case.
REQUIRES_REASONING_MARKERS = (
    "requires_reasoning_trace",
    "reasoning_trace_required",
    "requires_8f_trace",
    "requires_8f",
)
_REQUIRES_REASONING_TURN_RE = re.compile(
    r"<!--\s*(?:requires_reasoning_trace|reasoning_trace_required|requires_8f_trace)\s*-->",
    re.IGNORECASE,
)


def requires_reasoning_trace(frontmatter: Mapping[str, Any], body: str) -> bool:
    """Whether the artifact declares a general reasoning-trace requirement (in scope).

    The spec-agnostic generalization of ``is_compiler_initiated_install``: a truthy
    ``REQUIRES_REASONING_MARKERS`` frontmatter key or a
    ``<!-- requires_reasoning_trace -->`` turn marker. Marker-based only (no
    structured inference), so it is safe for an external SCOPE consumer; existing
    kinds set none of these -> always ``False``."""
    if any(_is_truthy(frontmatter.get(k)) for k in REQUIRES_REASONING_MARKERS):
        return True
    return _REQUIRES_REASONING_TURN_RE.search(body) is not None


def evaluate(frontmatter: Mapping[str, Any] | None, body: str) -> ReasoningTraceGateResult:
    """The F7 GOVERN decision for an artifact given its parsed frontmatter + body.

    Returns ``applies=False`` (a NO-OP) when there is no compiler-initiated
    skill-install signal -- the byte-identical path for the 301 existing kinds. When
    the signal IS present, ``fails`` is ``True`` iff no non-empty reasoning_trace
    accompanies it (13 SC-005 HARD FAIL)."""
    fm: Mapping[str, Any] = frontmatter or {}
    if not is_compiler_initiated_install(fm, body):
        return ReasoningTraceGateResult(False, False, "no compiler-initiated skill-install signal")
    if has_reasoning_trace(fm, body):
        return ReasoningTraceGateResult(
            True, False, "compiler-initiated install carries a non-empty reasoning_trace"
        )
    return ReasoningTraceGateResult(
        True, True, "compiler-initiated skill install emitted no reasoning_trace (13 SC-005 HARD FAIL)"
    )


def evaluate_general(frontmatter: Mapping[str, Any] | None, body: str) -> ReasoningTraceGateResult:
    """The GENERAL F7 reasoning-trace decision -- generalizes ``evaluate`` beyond
    compiler-initiated skill installs to all opted-in F6 PRODUCE.

    In scope when the artifact requires a reasoning_trace by EITHER the general
    markers (``requires_reasoning_trace``) OR the compiler-install special case, so it
    subsumes ``evaluate``. OUT OF SCOPE (a NO-OP) for any artifact that declares
    neither -- the byte-identical path for the 301 existing kinds. In scope, ``fails``
    is True iff no non-empty reasoning_trace accompanies the build."""
    fm: Mapping[str, Any] = frontmatter or {}
    if not (requires_reasoning_trace(fm, body) or is_compiler_initiated_install(fm, body)):
        return ReasoningTraceGateResult(False, False, "no reasoning-trace-required signal")
    if has_reasoning_trace(fm, body):
        return ReasoningTraceGateResult(
            True, False, "reasoning-required build carries a non-empty reasoning_trace"
        )
    return ReasoningTraceGateResult(
        True, True, "reasoning-required build emitted no reasoning_trace -- never shortcut"
    )


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Minimal stdlib frontmatter splitter for ``evaluate_text`` (no yaml dep).

    Handles the gate-relevant subset: ``key: scalar``, inline ``[a, b]`` lists, and
    ``- item`` block lists. Not a general YAML parser -- the engine passes a real
    parsed dict to ``evaluate`` directly; this exists for standalone demos/benches."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    fm: dict[str, Any] = {}
    cur_key: str | None = None
    for raw in lines[1:end]:
        if not raw.strip():
            continue
        stripped = raw.lstrip()
        if stripped.startswith("- ") and cur_key is not None:
            bucket = fm.setdefault(cur_key, [])
            if isinstance(bucket, list):
                bucket.append(stripped[2:].strip().strip("\"'"))
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", raw)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        cur_key = key
        if val == "":
            fm[key] = []
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key] = [x.strip().strip("\"'") for x in inner.split(",")] if inner else []
        elif val.lower() in ("null", "none", "~"):
            fm[key] = None
        else:
            fm[key] = val.strip().strip("\"'")
    return fm, "\n".join(lines[end + 1:])


def evaluate_text(text: str) -> ReasoningTraceGateResult:
    """Convenience wrapper: split frontmatter from ``text`` and ``evaluate``. For
    standalone callers (demos, benches); the engine uses ``evaluate`` with its own
    parsed frontmatter."""
    fm, body = _parse_frontmatter(text)
    return evaluate(fm, body)
