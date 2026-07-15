"""CEXAI distribution exception hierarchy (skills install/verify + SPARC gates).

Rooted at the foundation's ``CexaiError`` so a caller can still catch the whole
package with one ``except CexaiError``. ``DistributionError`` is the v0.5
(distribution) subtree root; the leaves below map to the specific failure modes
the three distribution specs name, with the spec-named signatures encoded as
structured attributes so callers and contract tests branch on fields
(``.missing_fields``, ``.expected_sha``, ``.failures``, ``.phase``, ...) rather
than parsing messages -- mirroring ``ToolsError`` in v0.4 and ``RbacForbiddenError``
in governance.

Impl waves MAY add more leaves under ``DistributionError`` in their own lanes
(e.g. a ``SkillSourceUnavailableError`` for 13 E1, a ``SkillNameCollisionError``
for 10 FR-006 / 13 E2, or a ``FrozenLockViolationError`` for the 13 ``--frozen``
not-in-lockfile reject path); the names defined here are FROZEN for v0.5.

Spec provenance:
  * SkillValidationError     -> 10 US P1 #3 / SC-002 -- a skill is published with
                                missing required frontmatter or a malformed
                                manifest; the publish gate refuses it.
                                SkillValidationError(missing_fields). (This is the
                                spec's ``SkillManifestError(missing_fields)``.)
  * LockfileMismatchError    -> 13 US P2 #2 / SC-002 -- a ``--frozen`` install found
                                the upstream tree SHA drifted from the lockfile;
                                HARD FAIL. LockfileMismatchError(skill_ref,
                                expected_sha, actual_sha).
  * CrossRuntimeParityError  -> 10 SC-003 / 13 SC-004 -- a skill CLAIMING
                                cross-runtime support failed parity at the publish
                                gate. CrossRuntimeParityError(skill_name, failures).
  * SparcGateError           -> 04 FR-002 -- a SPARC phase gate's criteria were not
                                met, so the feature may not advance.
                                SparcGateError(feature_id, phase, reason).

absorbs: 10_skills-sh + 13_vercel-skills + 04_claude-flow
"""

from __future__ import annotations

from cexai.foundation._shared.errors import CexaiError

__all__ = [
    "DistributionError",
    "SkillValidationError",
    "LockfileMismatchError",
    "CrossRuntimeParityError",
    "SparcGateError",
]


class DistributionError(CexaiError):
    """Root of the distribution subtree -- a skills-install, skills-verify, or SPARC
    failure. Subclasses ``CexaiError`` so a single ``except CexaiError`` covers it."""


# --------------------------------------------------------------------------- #
# Skills (cexai-specs/10_skills-sh + 13_vercel-skills)                         #
# --------------------------------------------------------------------------- #
class SkillValidationError(DistributionError):
    """A skill failed publish-gate validation (10 US P1 #3 / SC-002) -- required
    agentskills.io frontmatter is missing or the manifest is malformed. This is the
    spec's ``SkillManifestError(missing_fields)``; the publish gate refuses 100% of
    invalid skills (SC-002). ``missing_fields`` is the explicit ordered tuple of the
    absent / invalid frontmatter keys, surfaced so the author can fix them."""

    def __init__(self, missing_fields: tuple[str, ...]) -> None:
        self.missing_fields = missing_fields
        super().__init__(
            f"skill manifest invalid: missing/invalid fields {list(missing_fields)!r}"
        )


class LockfileMismatchError(DistributionError):
    """A ``--frozen`` install detected a tree-SHA drift (13 US P2 #2 / SC-002) -- the
    upstream ``skillFolderHash`` no longer matches the ``skills.lock.v3`` entry. This
    is a HARD FAIL: the install aborts and the lockfile is NOT modified.
    ``skill_ref`` is the affected skill, ``expected_sha`` is the lockfile's pinned
    SHA, and ``actual_sha`` is the drifted upstream SHA, all surfaced for the diff."""

    def __init__(self, skill_ref: str, expected_sha: str, actual_sha: str) -> None:
        self.skill_ref = skill_ref
        self.expected_sha = expected_sha
        self.actual_sha = actual_sha
        super().__init__(
            f"lockfile SHA mismatch for {skill_ref!r}: expected {expected_sha!r}, "
            f"upstream {actual_sha!r}"
        )


class CrossRuntimeParityError(DistributionError):
    """A skill that CLAIMS cross-runtime support failed parity at the publish gate
    (10 SC-003 / 13 SC-004). Distinct from the advisory ``CrossRuntimeReport`` that
    ``SkillVerifier.verify`` RETURNS (a failed report flags maintainer review, not a
    raise -- V10-F3): this is RAISED by the publish gate when a skill declaring
    cross-runtime compatibility diverges across runtimes. ``skill_name`` is the
    skill and ``failures`` is the ordered tuple of runtime ids that diverged."""

    def __init__(self, skill_name: str, failures: tuple[str, ...]) -> None:
        self.skill_name = skill_name
        self.failures = failures
        super().__init__(
            f"skill {skill_name!r} claims cross-runtime but failed on "
            f"{list(failures)!r}"
        )


# --------------------------------------------------------------------------- #
# SPARC (cexai-specs/04_claude-flow)                                           #
# --------------------------------------------------------------------------- #
class SparcGateError(DistributionError):
    """A SPARC phase gate's criteria were not met (04 FR-002), so the feature may not
    advance to the next phase. ``feature_id`` is the feature, ``phase`` is the
    ``SparcPhaseId`` value whose gate failed, and ``reason`` is the human-readable
    cause, surfaced for the gate report."""

    def __init__(self, feature_id: str, phase: str, reason: str) -> None:
        self.feature_id = feature_id
        self.phase = phase
        self.reason = reason
        super().__init__(
            f"SPARC gate failed for feature {feature_id!r} at phase {phase!r}: {reason}"
        )
