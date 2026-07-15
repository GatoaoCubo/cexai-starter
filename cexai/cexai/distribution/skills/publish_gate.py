"""SkillPublishGate -- the publish-time validation gate (10 SC-002, N05 Wrath).

The gate that refuses 100% of invalid skills before publish (10 US P1 #3 / SC-002).
Two stages:

  * ``validate`` -- the frontmatter / manifest gate. A manifest missing required
    fields (``name`` / ``version`` / a ``kind`` in the frontmatter) raises
    ``SkillValidationError(missing_fields)`` with the explicit absent fields; a
    ``kind`` not in the known-kinds registry is refused too (13 FR-013 -- reject an
    unknown kind). This is the frozen spec's ``SkillManifestError(missing_fields)``.
  * ``check_cross_runtime`` -- the parity gate. It runs the ``SkillVerifier`` and,
    for a skill that CLAIMS cross-runtime support yet diverges, RAISES
    ``CrossRuntimeParityError`` (10 SC-003 / 13 SC-004). This is the RAISING
    counterpart to the verifier's ADVISORY report (V10-F3): the verifier reports, the
    gate enforces.

``gate`` runs both in order (validate -> parity) and returns the parity report.

Offline + decoupled (Article XIV / VIII): the known-kinds registry is INJECTED
(``known_kinds``) so the gate never reads ``.cex/kinds_meta.json`` in this lane --
the W2 F7-GOVERN wiring supplies the full registry; tests inject their own set. The
default is the small canonical set including the spec's reuse targets (``skill`` for
10, ``marketplace_app_manifest`` for the skill_registry, plus the v0.5 reuse anchors)
so a valid skill passes out of the box. The verifier is injectable too (defaults to
``CrossRuntimeVerifier()``).

absorbs: 10_skills-sh (SC-002 / SC-003) + 13_vercel-skills (FR-013 / SC-004)
"""

from __future__ import annotations

from collections.abc import Iterable

from cexai.distribution._shared.errors import (
    CrossRuntimeParityError,
    SkillValidationError,
)
from cexai.distribution._shared.types import CrossRuntimeReport, SkillManifest
from cexai.distribution.skills.verifier import CrossRuntimeVerifier

__all__ = ["SkillPublishGate"]

# Canonical reuse targets (per the v0.5 taxonomy ADR -- ZERO new kinds): the skill
# kind itself (10), the skill_registry's marketplace_app_manifest reuse, and the
# install/methodology reuse anchors. The W2 F7 wiring injects the full kinds_meta.
_DEFAULT_KNOWN_KINDS = frozenset(
    {
        "skill",
        "marketplace_app_manifest",
        "reasoning_trace",
        "decision_record",
        "pipeline_template",
    }
)


class SkillPublishGate:
    """The publish-time gate refusing invalid skills (10 SC-002) and claiming-yet-
    failing cross-runtime skills (10 SC-003 / 13 SC-004).

    ``known_kinds`` is the injected kind registry the frontmatter ``kind`` is checked
    against (13 FR-013; defaults to the canonical reuse set). ``verifier`` is the
    injected ``SkillVerifier`` (defaults to ``CrossRuntimeVerifier()``)."""

    def __init__(
        self,
        *,
        known_kinds: Iterable[str] | None = None,
        verifier: CrossRuntimeVerifier | None = None,
    ) -> None:
        self._known_kinds = (
            frozenset(known_kinds) if known_kinds is not None else _DEFAULT_KNOWN_KINDS
        )
        self._verifier = verifier if verifier is not None else CrossRuntimeVerifier()

    def validate(self, skill: SkillManifest) -> None:
        """Refuse an invalid manifest (10 SC-002). Raises
        ``SkillValidationError(missing_fields)`` for missing ``name`` / ``version`` /
        frontmatter ``kind``, or for a ``kind`` not in the known-kinds registry (13
        FR-013). ``missing_fields`` is the explicit ordered tuple so the author can
        fix them."""
        missing: list[str] = []
        if not skill.name:
            missing.append("name")
        if not skill.version:
            missing.append("version")
        kind = skill.frontmatter.get("kind")
        if not kind:
            missing.append("kind")
        if missing:
            raise SkillValidationError(tuple(missing))
        if kind not in self._known_kinds:
            # 13 FR-013: a frontmatter kind unknown to the registry is invalid.
            raise SkillValidationError((f"kind:{kind}",))

    def check_cross_runtime(self, skill: SkillManifest) -> CrossRuntimeReport:
        """Run the verifier and ENFORCE parity for a claiming skill. Returns the
        ``CrossRuntimeReport``; raises ``CrossRuntimeParityError(skill_name,
        failures)`` when the skill CLAIMS cross-runtime support yet diverges (10
        SC-003 / 13 SC-004). A skill claiming no runtimes is exempt (V10-F2)."""
        report = self._verifier.verify(skill)
        if skill.runtime_compatibility and not report.parity:
            raise CrossRuntimeParityError(skill.name, report.failures)
        return report

    def gate(self, skill: SkillManifest) -> CrossRuntimeReport:
        """Run the full publish gate: ``validate`` (frontmatter) then
        ``check_cross_runtime`` (parity). Returns the parity report on success;
        raises ``SkillValidationError`` or ``CrossRuntimeParityError`` on refusal."""
        self.validate(skill)
        return self.check_cross_runtime(skill)
