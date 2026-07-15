"""SparcPipeline -- the concrete opt-in SPARC methodology (cexai-specs/04_claude-flow).

Implements the frozen ``SparcMethodology`` protocol from
``cexai.distribution._shared.types``: ``template(phase) -> SparcTemplate`` and
``advance(feature_id, phase) -> SparcPhase``. The engine is a small per-feature state
machine over the five ``SparcPhaseId`` phases (specification -> pseudocode ->
architecture -> refinement -> code), pure and offline (Article XIV) -- the phase
DATA and gate logic live in ``templates.py``.

Behaviour map:
  * ``scaffold(feature, algorithmic=...)`` -- P1 #1: return all 5 phase templates.
    A non-algorithmic feature emits the non-fatal ``SPARC_MISFIT`` warning suggesting
    spec-kit (the default methodology); it does NOT block (the templates still
    return). (04 edge case.)
  * ``advance(feature, phase)`` -- FR-002: evaluate the PRIOR phase's gate; a failed
    gate raises ``SparcGateError`` and the phase does NOT advance. The prior chain is
    lazy-seeded with default content so advancing straight to a later phase walks the
    intervening gates (SC-001). The Code phase carries ``traces_to: SPEC.req-N`` (P1
    #3).
  * ``advance(..., content=...)`` -- supply an explicit phase body (the seam the gate
    failure path and real authoring use); omit it to take the template default.

Founder rule (v0.5 taxonomy ADR): the pipeline REUSES the existing
``pipeline_template`` kind and the v0.3 ``SparcPhaseId``; ``sparc_phase`` is NOT
registered. ``SparcEngine`` aliases ``SparcPipeline`` for the frozen contract test's
``from cexai.distribution.sparc import SparcEngine`` import.

absorbs: 04_claude-flow
"""

from __future__ import annotations

import warnings

from cexai.distribution._shared.errors import SparcGateError
from cexai.distribution._shared.types import SparcPhase, SparcTemplate

# Import-only reuse of the frozen v0.3 phase ids (never redefined -- founder rule).
from cexai.orchestration._shared.types import SparcPhaseId

from . import templates

__all__ = ["SparcPipeline", "SparcEngine", "SparcMisfitWarning", "SPARC_MISFIT_MESSAGE"]

# Gate verdicts (types.py: "open / passed / blocked"). The engine uses two: a phase
# whose own content satisfies its gate is ``passed`` (ready to advance); otherwise it
# is ``open`` (entered, work still owed). Advancement reads the PRIOR phase's verdict.
_PASSED = "passed"
_OPEN = "open"


class SparcMisfitWarning(UserWarning):
    """Emitted (non-fatally) when SPARC is invoked for a non-algorithmic feature (04
    edge case). It is a WARNING, not a member of the frozen ``DistributionError``
    hierarchy: SPARC is opt-in and never imposed, so a misfit advises spec-kit and
    proceeds. Callers that want it fatal can ``warnings.simplefilter('error',
    SparcMisfitWarning)``."""


SPARC_MISFIT_MESSAGE = (
    "SPARC_MISFIT: this feature does not look algorithmic; prefer spec-kit, the "
    "default CEXAI methodology. SPARC stays opt-in and does not block -- the 5 phase "
    "templates were still scaffolded."
)


class SparcPipeline:
    """A per-feature SPARC state machine satisfying the frozen ``SparcMethodology``.

    Stateless across features except for the phases each feature has entered, kept in
    ``_state: {feature_id: {phase: SparcPhase}}``. Construct one engine and drive many
    features through it; nothing here touches the network, an LLM, or the filesystem.
    """

    def __init__(self) -> None:
        self._state: dict[str, dict[SparcPhaseId, SparcPhase]] = {}

    # -- SparcMethodology protocol ------------------------------------------------ #
    def template(self, phase: SparcPhaseId) -> SparcTemplate:
        """Return the typed ``SparcTemplate`` scaffold for ``phase`` (FR-001/002)."""
        self._validate(phase)
        return templates.template_for(phase)

    def advance(
        self,
        feature_id: str,
        phase: SparcPhaseId,
        *,
        content: str | None = None,
    ) -> SparcPhase:
        """Advance ``feature_id`` into ``phase`` and return its ``SparcPhase`` (FR-002).

        Entering the first phase (``specification``) has no prior gate. For any later
        phase the prior phase's gate is evaluated first: if it is not ``passed`` a
        ``SparcGateError`` is raised naming the failing prior phase and ``phase`` is
        NOT recorded. The prior chain is lazy-seeded with template defaults so a jump
        straight to a later phase still walks every intervening gate. Pass ``content``
        to supply an explicit body; omit it to take the pre-populated default.
        """
        self._validate(phase)
        feature_phases = self._state.setdefault(feature_id, {})

        # Idempotent re-entry: an already-recorded phase with no override returns as-is.
        if content is None and phase in feature_phases:
            return feature_phases[phase]

        prior = templates.prior_phase(phase)
        if prior is None:  # specification -- entry phase, no gate to clear
            body = content if content is not None else templates.default_specification(feature_id)
            return self._record(feature_id, phase, body)

        prior_obj = feature_phases.get(prior)
        if prior_obj is None:  # lazy-seed the prior chain with defaults (SC-001 walk)
            prior_obj = self.advance(feature_id, prior)

        if prior_obj.gate_status != _PASSED:
            _ok, reason = templates.gate_check(prior, prior_obj.content)
            raise SparcGateError(feature_id, prior, reason)

        body = (
            content
            if content is not None
            else templates.build_content(
                phase,
                feature_id=feature_id,
                prior_phase=prior,
                prior_content=prior_obj.content,
            )
        )
        return self._record(feature_id, phase, body)

    # -- extensions (P1 #1 + introspection) --------------------------------------- #
    def templates(self) -> tuple[SparcTemplate, ...]:
        """All 5 phase templates in S-P-A-R-C order (FR-001)."""
        return tuple(templates.template_for(phase) for phase in templates.PHASE_ORDER)

    def scaffold(self, feature_id: str, *, algorithmic: bool = True) -> tuple[SparcTemplate, ...]:
        """Scaffold the 5 SPARC phase templates for ``feature_id`` (P1 #1).

        A non-algorithmic feature (``algorithmic=False``) emits the non-fatal
        ``SPARC_MISFIT`` warning suggesting spec-kit, then STILL returns the full
        scaffold (04 edge case -- advisory, never blocking).
        """
        if not algorithmic:
            warnings.warn(SPARC_MISFIT_MESSAGE, SparcMisfitWarning, stacklevel=2)
        return self.templates()

    def recorded(self, feature_id: str) -> tuple[SparcPhase, ...]:
        """The phases ``feature_id`` has entered, in S-P-A-R-C order."""
        feature_phases = self._state.get(feature_id, {})
        return tuple(feature_phases[p] for p in templates.PHASE_ORDER if p in feature_phases)

    # -- internals ---------------------------------------------------------------- #
    def _record(self, feature_id: str, phase: SparcPhaseId, content: str) -> SparcPhase:
        """Evaluate ``phase``'s own gate against ``content``, store, and return the
        typed ``SparcPhase`` projection (``gate_status`` = passed | open)."""
        passed, _reason = templates.gate_check(phase, content)
        projection = SparcPhase(
            phase=phase,
            feature_id=feature_id,
            gate_status=_PASSED if passed else _OPEN,
            content=content,
        )
        self._state[feature_id][phase] = projection
        return projection

    @staticmethod
    def _validate(phase: SparcPhaseId) -> None:
        if phase not in templates.PHASE_ORDER:
            raise ValueError(
                f"unknown SPARC phase {phase!r}; expected one of {templates.PHASE_ORDER!r}"
            )


# The frozen contract test imports ``SparcEngine`` (the W0-frozen impl-wave seam, like
# ``CrossAgentInstaller`` / ``CrossRuntimeVerifier``). Alias it to the canonical impl
# so the W2 contract flip resolves with no edit to the shared contract file.
SparcEngine = SparcPipeline
