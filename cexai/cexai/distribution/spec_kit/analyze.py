"""Cross-artifact consistency checker (the spec-kit Analyze step) -- the core value.

CEX has F7 GOVERN (single-artifact quality gate) but NO cross-artifact comparator
(cexai-specs/01_spec-kit/retro.md, gap #2: "No cross-artifact consistency check").
This module is that comparator: it reads a spec-kit feature dir
(``spec.md`` + ``plan.md`` + ``tasks.md``) and reports where the three artifacts
disagree -- orphan requirements, unimplemented user stories, dangling task
references, and unresolved clarification markers.

Pure + offline (Article XIV): the engine is text-in / findings-out with no network,
no LLM, no global state. ``analyze_text`` is the testable core; ``analyze_feature_dir``
is the thin filesystem wrapper.

Severity model (mirrors the existing analyze.md PASS/CONDITIONAL/FAIL verdict, e.g.
cexai-specs/05_agno/analyze.md):
  * SEV-1 (critical): the spec is unbuildable as written (unresolved clarification
    marker; a task points at a user story that does not exist).
  * SEV-2 (high): a whole user story has no tasks; a task references a requirement
    id absent from the spec; a required artifact is missing.
  * SEV-3 (advisory): an orphan requirement (declared, never referenced by a task);
    a user story not explicitly labelled in the plan.

Verdict: any SEV-1/SEV-2 -> FAIL (exit 1, CI gate trips); only SEV-3 -> CONDITIONAL
(exit 0); none -> PASS (exit 0). So a clean OR merely-advisory feature dir exits 0
and a structurally-broken one exits non-zero -- the CI contract.

Founder rule: this is CODE (a checker), NOT a new kind -- no kinds_meta edit.

absorbs: 01_spec-kit (Analyze)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "SEV_CRITICAL",
    "SEV_HIGH",
    "SEV_ADVISORY",
    "VERDICT_PASS",
    "VERDICT_CONDITIONAL",
    "VERDICT_FAIL",
    "Finding",
    "AnalyzeReport",
    "analyze_text",
    "analyze_feature_dir",
]

SEV_CRITICAL = 1
SEV_HIGH = 2
SEV_ADVISORY = 3
_SEV_LABEL: dict[int, str] = {1: "SEV-1", 2: "SEV-2", 3: "SEV-3"}

VERDICT_PASS = "PASS"
VERDICT_CONDITIONAL = "CONDITIONAL"
VERDICT_FAIL = "FAIL"

# The three artifacts the checker compares. Constitution is inherited project-wide
# (cexai-specs/_decisions/constitution.md), so it is not part of this comparison.
SPEC_FILE = "spec.md"
PLAN_FILE = "plan.md"
TASKS_FILE = "tasks.md"

# -- extraction patterns ------------------------------------------------------ #
# A user story header: "### User Story P1 -- ..." or "User Story 1". Both the
# "P<n>" (spec-kit priority) and bare "<n>" forms map to the same story number.
_USER_STORY = re.compile(r"User Story\s+P?(\d+)", re.IGNORECASE)
# A requirement id token (FR-### / SC-###), tolerant of **bold** wrapping. Digits
# are kept verbatim (no zero-strip) so "FR-001" matches "FR-001", never "FR-1".
_REQUIREMENT = re.compile(r"\b(FR|SC)-(\d+)\b", re.IGNORECASE)
# A task's user-story tag: the spec-kit "[US#]" notation in tasks.md.
_TASK_US = re.compile(r"\[US(\d+)\]", re.IGNORECASE)
# An unresolved clarification marker: "[NEEDS CLARIFICATION]" or
# "[NEEDS CLARIFICATION: <question>]". The closing bracket bounds the snippet.
_CLARIFICATION = re.compile(r"\[NEEDS CLARIFICATION[^\]]*\]", re.IGNORECASE)
# A plan's explicit user-story reference: "P1", "US1", or "User Story 1".
_PLAN_US = re.compile(r"\b(?:US|P)(\d+)\b|User Story\s+P?(\d+)", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class Finding:
    """One cross-artifact inconsistency. ``severity`` is 1/2/3 (see module docstring);
    ``code`` is the stable machine label (e.g. ``ORPHAN_REQUIREMENT``); ``message`` is
    the human explanation; ``artifact`` names the file the finding is anchored to
    (``spec.md`` / ``plan.md`` / ``tasks.md`` / ``<dir>`` for a missing file); ``ref``
    is the requirement id or user-story id the finding concerns (empty when N/A).
    Callers branch on the structured fields, never by parsing ``message``."""

    severity: int
    code: str
    message: str
    artifact: str = ""
    ref: str = ""

    @property
    def severity_label(self) -> str:
        """The ``SEV-1`` / ``SEV-2`` / ``SEV-3`` label for this finding."""
        return _SEV_LABEL.get(self.severity, f"SEV-{self.severity}")

    def to_dict(self) -> dict[str, object]:
        """A JSON-ready mapping of this finding (stable keys, ASCII-safe values)."""
        return {
            "severity": self.severity,
            "severity_label": self.severity_label,
            "code": self.code,
            "message": self.message,
            "artifact": self.artifact,
            "ref": self.ref,
        }


@dataclass(frozen=True, slots=True)
class AnalyzeReport:
    """The result of analyzing one feature dir: the ordered ``findings`` plus the
    derived ``verdict`` and exit code. Immutable so a report is safely shareable and
    serializes deterministically. ``feature_dir`` is the analyzed path (for the
    header); findings are pre-sorted (critical first) by ``analyze_feature_dir``."""

    feature_dir: str
    findings: tuple[Finding, ...]

    @property
    def verdict(self) -> str:
        """``FAIL`` if any SEV-1/SEV-2 finding, ``CONDITIONAL`` if only SEV-3,
        ``PASS`` if none -- mirroring the analyze.md verdict vocabulary."""
        sev = {f.severity for f in self.findings}
        if SEV_CRITICAL in sev or SEV_HIGH in sev:
            return VERDICT_FAIL
        if SEV_ADVISORY in sev:
            return VERDICT_CONDITIONAL
        return VERDICT_PASS

    @property
    def exit_code(self) -> int:
        """0 for PASS/CONDITIONAL, 1 for FAIL -- the CI gate (non-zero on SEV-1/2)."""
        return 1 if self.verdict == VERDICT_FAIL else 0

    def counts(self) -> dict[str, int]:
        """Finding counts by severity (``sev1`` / ``sev2`` / ``sev3`` / ``total``)."""
        out = {"sev1": 0, "sev2": 0, "sev3": 0}
        for f in self.findings:
            out[f"sev{f.severity}"] = out.get(f"sev{f.severity}", 0) + 1
        out["total"] = len(self.findings)
        return out

    def to_dict(self) -> dict[str, object]:
        """A JSON-ready mapping of the whole report (verdict + counts + findings)."""
        return {
            "feature_dir": self.feature_dir,
            "verdict": self.verdict,
            "exit_code": self.exit_code,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
        }

    def render(self) -> str:
        """A compact human-readable report (the default, non-``--json`` CLI output)."""
        c = self.counts()
        lines = [
            f"Analyze: {self.feature_dir}",
            f"Verdict: {self.verdict}  "
            f"(SEV-1={c['sev1']} SEV-2={c['sev2']} SEV-3={c['sev3']})",
        ]
        if not self.findings:
            lines.append("  no findings -- spec, plan, and tasks are consistent.")
            return "\n".join(lines)
        for f in self.findings:
            ref = f" [{f.ref}]" if f.ref else ""
            lines.append(f"  {f.severity_label} {f.code} ({f.artifact}){ref}: {f.message}")
        return "\n".join(lines)


# -- pure extraction helpers -------------------------------------------------- #
def _story_numbers(text: str) -> set[int]:
    """The set of user-story numbers declared in a spec body (P1 -> 1)."""
    return {int(m.group(1)) for m in _USER_STORY.finditer(text)}


def _requirement_ids(text: str) -> set[str]:
    """The set of requirement ids (``FR-###`` / ``SC-###``) appearing in ``text``,
    uppercased and de-duplicated."""
    return {f"{kind.upper()}-{num}" for kind, num in _REQUIREMENT.findall(text)}


def _task_story_numbers(text: str) -> set[int]:
    """The user-story numbers tasks claim to serve, from ``[US#]`` tags."""
    return {int(m.group(1)) for m in _TASK_US.finditer(text)}


def _plan_story_numbers(text: str) -> set[int]:
    """The user-story numbers the plan explicitly references (P#, US#, User Story #)."""
    out: set[int] = set()
    for a, b in _PLAN_US.findall(text):
        out.add(int(a or b))
    return out


def _clarification_markers(text: str) -> list[str]:
    """Every unresolved ``[NEEDS CLARIFICATION ...]`` marker snippet in ``text``."""
    return [m.group(0) for m in _CLARIFICATION.finditer(text)]


def analyze_text(spec: str, plan: str, tasks: str) -> tuple[Finding, ...]:
    """Compare the three artifact bodies and return ordered findings (pure core).

    This is the testable heart of the checker -- no filesystem, no I/O. The four
    cross-artifact checks (retro.md gap #2):
      1. orphan requirements: every spec FR-###/SC-### is referenced by >= 1 task;
         report spec requirements no task references (SEV-3) and task requirement
         references absent from the spec (SEV-2);
      2. plan covers every spec user story P1/P2/P3 (SEV-3 advisory when a story is
         not explicitly labelled in the plan);
      3. unresolved ``[NEEDS CLARIFICATION]`` markers in any artifact (SEV-1);
      4. tasks reference valid ``[US#]`` ids that exist in the spec (dangling ->
         SEV-1; a spec story with no task -> SEV-2).
    """
    findings: list[Finding] = []

    spec_stories = _story_numbers(spec)
    spec_reqs = _requirement_ids(spec)
    task_stories = _task_story_numbers(tasks)
    task_reqs = _requirement_ids(tasks)
    plan_stories = _plan_story_numbers(plan)

    # (3) Unresolved clarification markers -- spec is not buildable as written.
    for artifact, body in ((SPEC_FILE, spec), (PLAN_FILE, plan), (TASKS_FILE, tasks)):
        for marker in _clarification_markers(body):
            findings.append(
                Finding(
                    SEV_CRITICAL,
                    "NEEDS_CLARIFICATION",
                    f"unresolved clarification marker: {marker}",
                    artifact=artifact,
                )
            )

    # (4) Tasks -> spec user-story traceability.
    for n in sorted(task_stories - spec_stories):
        findings.append(
            Finding(
                SEV_CRITICAL,
                "DANGLING_TASK_US",
                f"a task references user story US{n}, which the spec does not declare",
                artifact=TASKS_FILE,
                ref=f"US{n}",
            )
        )
    for n in sorted(spec_stories - task_stories):
        findings.append(
            Finding(
                SEV_HIGH,
                "USER_STORY_NOT_IN_TASKS",
                f"spec user story P{n} has no task ([US{n}] appears in no task)",
                artifact=TASKS_FILE,
                ref=f"P{n}",
            )
        )

    # (1) Requirement coverage (spec FR/SC <-> tasks).
    for req in sorted(task_reqs - spec_reqs):
        findings.append(
            Finding(
                SEV_HIGH,
                "DANGLING_TASK_REQUIREMENT",
                f"a task references {req}, which the spec does not declare",
                artifact=TASKS_FILE,
                ref=req,
            )
        )
    for req in sorted(spec_reqs - task_reqs):
        findings.append(
            Finding(
                SEV_ADVISORY,
                "ORPHAN_REQUIREMENT",
                f"spec requirement {req} is not referenced by any task",
                artifact=SPEC_FILE,
                ref=req,
            )
        )

    # (2) Plan -> spec user-story coverage (advisory: plans often label by component).
    for n in sorted(spec_stories - plan_stories):
        findings.append(
            Finding(
                SEV_ADVISORY,
                "USER_STORY_NOT_IN_PLAN",
                f"plan.md does not explicitly reference user story P{n} "
                f"(coverage may still exist via components)",
                artifact=PLAN_FILE,
                ref=f"P{n}",
            )
        )

    return _ordered(findings)


def _ordered(findings: list[Finding]) -> tuple[Finding, ...]:
    """Sort findings critical-first, then by code then ref -- a stable presentation
    order that keeps ``--json`` output deterministic across runs."""
    return tuple(sorted(findings, key=lambda f: (f.severity, f.code, f.ref)))


def _read(path: Path) -> str | None:
    """Read ``path`` as text, or ``None`` if it does not exist. UTF-8 with a lenient
    fallback so a stray non-ASCII byte in a human-authored .md never crashes analyze."""
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def analyze_feature_dir(feature_dir: str | Path) -> AnalyzeReport:
    """Analyze the spec-kit feature dir at ``feature_dir`` and return its report.

    Reads ``spec.md`` / ``plan.md`` / ``tasks.md``. A missing ``spec.md`` is SEV-2
    (nothing to compare against); a missing ``plan.md`` or ``tasks.md`` is SEV-2
    (an incomplete feature). Present artifacts are compared via ``analyze_text``.
    Raises ``FileNotFoundError`` only when ``feature_dir`` itself is not a directory.
    """
    base = Path(feature_dir)
    if not base.is_dir():
        raise FileNotFoundError(f"not a feature directory: {feature_dir!r}")

    spec = _read(base / SPEC_FILE)
    plan = _read(base / PLAN_FILE)
    tasks = _read(base / TASKS_FILE)

    findings: list[Finding] = []
    for name, body in ((SPEC_FILE, spec), (PLAN_FILE, plan), (TASKS_FILE, tasks)):
        if body is None:
            findings.append(
                Finding(
                    SEV_HIGH,
                    "MISSING_ARTIFACT",
                    f"feature dir is missing {name}",
                    artifact=name,
                )
            )

    findings.extend(analyze_text(spec or "", plan or "", tasks or ""))
    return AnalyzeReport(feature_dir=str(base), findings=_ordered(findings))
