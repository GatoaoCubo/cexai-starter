"""CEXAI SPARC subsystem -- opt-in 5-phase methodology over pipeline_template.

The v0.5-W1 impl wave (04_claude-flow US P1 / FR-001..004, SC-001/002). ``SparcPipeline``
implements the frozen ``SparcMethodology`` protocol from
``cexai.distribution._shared.types``: the 5-phase templates (specification ->
pseudocode -> architecture -> refinement -> code) with explicit advance gates,
prior->next pre-population (>= 30%), Code-phase ``traces_to: SPEC.req-N`` traceability,
the non-fatal ``SPARC_MISFIT`` warning, and the SPARC-vs-spec-kit decision matrix.

The five phase ids are the v0.3 orchestration ``SparcPhaseId`` (reused, not
redefined); the 5-phase pipeline REUSES the existing ``pipeline_template`` kind and
the decision matrix REUSES ``decision_record`` (``decision_type: methodology_choice``)
-- the founder rule: ``sparc_phase`` is NOT a new kind (see the v0.5 taxonomy ADR).
``SparcEngine`` aliases ``SparcPipeline`` for the frozen contract test's import.

absorbs: 04_claude-flow
"""

from .decision_matrix import (
    METHODOLOGY_CHOICE_DIMENSIONS,
    methodology_decision_record,
    recommend,
)
from .methodology import (
    SPARC_MISFIT_MESSAGE,
    SparcEngine,
    SparcMisfitWarning,
    SparcPipeline,
)
from .templates import PHASE_ORDER, PIPELINE_TEMPLATE_ID, prepopulation_ratio

__all__ = [
    # methodology engine
    "SparcPipeline",
    "SparcEngine",
    "SparcMisfitWarning",
    "SPARC_MISFIT_MESSAGE",
    # phase vocabulary + helpers
    "PHASE_ORDER",
    "PIPELINE_TEMPLATE_ID",
    "prepopulation_ratio",
    # decision matrix (SPARC vs spec-kit)
    "METHODOLOGY_CHOICE_DIMENSIONS",
    "methodology_decision_record",
    "recommend",
]
