"""CrossRuntimeVerifier -- cross-runtime parity report for a skill (10 US P3).

The concrete implementation of the frozen ``SkillVerifier`` Protocol
(``cexai.distribution._shared.types.SkillVerifier``). ``verify(skill)`` returns a
typed ``CrossRuntimeReport`` (parity + the diverging ``failures`` set) for a skill's
claimed runtimes. Two rules from the spec are encoded here:

  * V10-F2 (the "claiming must pass" bar): a skill that claims NO runtimes (empty
    ``runtime_compatibility``) is EXEMPT -- it returns ``parity=True`` with no
    runtimes exercised and no failures. Cross-runtime verification only applies to
    skills that opt in by declaring runtimes.
  * V10-F3 (advisory, never auto-demote): a divergence is REPORTED (``parity=False``,
    ``failures`` non-empty); ``verify`` NEVER raises and never demotes the skill. The
    publish gate (sibling ``publish_gate`` module) is what RAISES
    ``CrossRuntimeParityError`` for a claiming-yet-failing skill.

Offline-first (Article XIV): the actual per-runtime execution is an INJECTED
``runner`` (``(skill, runtime) -> bool``; ``True`` = the skill behaves on that
runtime), so tests exercise the parity logic with a fake -- no live Claude / Ollama.
The unconfigured default runner reports parity (no divergence detected) -- an
offline-safe STUB for a no-arg instance (it never *invents* a failure), NOT a real
check; production is expected to inject the real Claude + Ollama runners (ADR 013
Article XIV).

HONESTY NOTE (f7-honesty / R-220): a no-arg ``CrossRuntimeVerifier`` is the ONLY
constructor used by ``SkillPublishGate`` and the ``cexai skills verify`` CLI when no
``runner`` is explicitly injected -- i.e. it is what actually runs in a default
install, not just in tests. Its ``verify()`` report cannot be loosened to a false
"UNVERIFIED" ``parity`` value without breaking the frozen ``CrossRuntimeReport``
shape (``cexai.distribution._shared.types`` -- v0.5-W0 freeze, no new field allowed
here) and the frozen SC-003 contract (``CrossRuntimeVerifier().verify(claiming)
.parity is True`` for the offline default, asserted by
``tests/distribution/bench/test_sc_distribution.py``). So instead of a silent
default-to-satisfied, constructing WITHOUT a real ``runner`` now emits an explicit
``UnverifiedCrossRuntimeWarning`` (stdlib ``warnings``) -- the un-checkable path
HONESTLY reports it cannot check (surfaced in logs / CI), rather than pretending a
live cross-runtime check happened. Callers that need a genuine parity check MUST
inject a real ``runner``.

absorbs: 10_skills-sh (US P3 / FR-003 / SC-003) + 13_vercel-skills (SC-004)
"""

from __future__ import annotations

import warnings
from collections.abc import Callable

from cexai.distribution._shared.types import CrossRuntimeReport, SkillManifest

__all__ = ["RuntimeRunner", "CrossRuntimeVerifier", "UnverifiedCrossRuntimeWarning"]

# ``(skill, runtime) -> bool``: True when the skill behaves correctly on the runtime.
RuntimeRunner = Callable[[SkillManifest, str], bool]


class UnverifiedCrossRuntimeWarning(RuntimeWarning):
    """Raised (as a ``warnings.warn``, not an exception) when a ``CrossRuntimeVerifier``
    is constructed without a real ``runner``. Its ``verify()`` reports offline-stub
    parity (``True``, no divergence detected) rather than an actually-executed
    cross-runtime check -- see the HONESTY NOTE in this module's docstring (R-220)."""


def _default_runner(skill: SkillManifest, runtime: str) -> bool:
    """The unconfigured runner: report parity (no divergence detected). Offline we
    cannot execute a live runtime, so the default never invents a failure; production
    is expected to inject the real per-runtime runners instead of relying on this
    stub. The report stays ADVISORY either way (V10-F3)."""
    return True


class CrossRuntimeVerifier:
    """Concrete ``SkillVerifier``: cross-runtime parity (10 US P3 / 13 SC-004).

    Construct with an optional injected ``runner`` (the per-runtime execution seam);
    a no-arg instance uses the offline-safe STUB default and emits
    ``UnverifiedCrossRuntimeWarning`` (R-220 -- no real runtime was exercised, so the
    caller is told, rather than silently getting a false-passing report). ``verify``
    is pure + total -- it returns a report and never raises (the advisory contract,
    V10-F3)."""

    def __init__(self, runner: RuntimeRunner | None = None) -> None:
        if runner is None:
            warnings.warn(
                "CrossRuntimeVerifier() constructed with no real runner -- verify() "
                "will report offline-stub parity (no divergence detected) without "
                "executing anything on any runtime. This is NOT a genuine "
                "cross-runtime check. Inject a real `runner` for one.",
                UnverifiedCrossRuntimeWarning,
                stacklevel=2,
            )
        self._runner: RuntimeRunner = runner if runner is not None else _default_runner

    # -- SkillVerifier protocol --------------------------------------------- #
    def verify(self, skill: SkillManifest) -> CrossRuntimeReport:
        """Execute ``skill`` across its claimed runtimes and return a typed
        ``CrossRuntimeReport``. An empty ``runtime_compatibility`` is exempt
        (``parity=True``, no runtimes, no failures -- V10-F2). Otherwise each claimed
        runtime is exercised through the injected runner; the diverging ones are the
        ``failures`` and ``parity`` is true exactly when none diverged. Never
        raises / auto-demotes (V10-F3)."""
        runtimes = tuple(skill.runtime_compatibility)
        if not runtimes:
            return CrossRuntimeReport(
                skill_name=skill.name, runtimes=(), parity=True, failures=()
            )
        failures = tuple(rt for rt in runtimes if not self._runner(skill, rt))
        return CrossRuntimeReport(
            skill_name=skill.name,
            runtimes=runtimes,
            parity=not failures,
            failures=failures,
        )
