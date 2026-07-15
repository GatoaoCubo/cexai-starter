"""CEXAI skills subsystem -- agentskills.io packaging + cross-agent install/verify.

The v0.5-W1 impl lane for 10_skills-sh + 13_vercel-skills. Three concrete
implementations of the frozen Protocols in ``cexai.distribution._shared.types``
(plus the publish gate that composes them):

  * ``CrossAgentInstaller`` (``installer``) -- the frozen ``SkillInstaller``:
    resolve a skill_ref across ordered sources (custom_registry-first, 10 P2 #2),
    pin the tree SHA (13 FR-002), link/copy into each detected agent dir
    (13 P1 #2 / FR-005), idempotently (13 P1 #4); emits a reasoning_trace
    (13 FR-012). Backends (resolver / detector / linker) are INJECTED -- offline.
  * ``CrossRuntimeVerifier`` (``verifier``) -- the frozen ``SkillVerifier``: a typed
    cross-runtime parity report; no-claim skills are exempt (V10-F2); a divergence
    is advisory, never auto-demoted (V10-F3). The runtime runner is INJECTED.
  * ``SkillPublishGate`` (``publish_gate``) -- the N05 (Wrath) publish gate: refuses
    invalid frontmatter / unknown kind (10 SC-002 / 13 FR-013) and raises
    ``CrossRuntimeParityError`` for a claiming-yet-failing skill (10 SC-003).
  * ``lockfile`` -- ``skills.lock.v3`` byte-stable read/write (13 SC-001/002) +
    ``--frozen`` resolution (SHA-drift HARD FAIL, 13 SC-002).

Three lane-LOCAL error leaves under the frozen ``DistributionError`` root
(sanctioned by the ``_shared.errors`` docstring): ``SkillSourceUnavailableError``
(13 E1), ``FrozenLockViolationError`` (13 P2 #1), and ``LockfileParseError`` (R-230
-- a structurally corrupted ``skills.lock.v3``: an unrecognized key or a missing
required field, surfaced rather than silently dropped/defaulted).

REUSES the existing ``skill`` + ``marketplace_app_manifest`` kinds (ZERO new kinds,
per the v0.5 taxonomy ADR). Everything is offline-first (Article XIV) and
import-light (Article VIII -- stdlib only; the heavy ``@vercel/detect-agent`` / git
deps are lazy/injected, landing in a later wiring wave).

absorbs: 10_skills-sh + 13_vercel-skills
"""

from cexai.distribution.skills.installer import (
    AgentDetector,
    CrossAgentInstaller,
    ResolvedSource,
    SkillLinker,
    SkillSourceUnavailableError,
    SourceResolver,
    build_installer,
)
from cexai.distribution.skills.lockfile import (
    FrozenLockViolationError,
    LockfileParseError,
    dump_lockfile,
    load_lockfile,
    read_lockfile,
    resolve_frozen,
    write_lockfile,
)
from cexai.distribution.skills.publish_gate import SkillPublishGate
from cexai.distribution.skills.verifier import (
    CrossRuntimeVerifier,
    RuntimeRunner,
    UnverifiedCrossRuntimeWarning,
)

__all__ = [
    # installer (SkillInstaller)
    "CrossAgentInstaller",
    "build_installer",
    "ResolvedSource",
    "SourceResolver",
    "AgentDetector",
    "SkillLinker",
    "SkillSourceUnavailableError",
    # lockfile (skills.lock.v3 + --frozen)
    "dump_lockfile",
    "load_lockfile",
    "write_lockfile",
    "read_lockfile",
    "resolve_frozen",
    "FrozenLockViolationError",
    "LockfileParseError",
    # verifier (SkillVerifier)
    "CrossRuntimeVerifier",
    "RuntimeRunner",
    "UnverifiedCrossRuntimeWarning",
    # publish gate
    "SkillPublishGate",
]
