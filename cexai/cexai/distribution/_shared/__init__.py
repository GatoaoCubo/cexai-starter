"""Shared, dependency-free primitives for the CEXAI distribution layer.

Contains the FROZEN type contracts (``types``) shared by the skills and sparc
subsystems, and the distribution exception hierarchy (``errors``). Import the
concrete symbols from the submodules directly, e.g. ``from cexai.distribution.
_shared.types import SkillManifest``. Kept import-light -- plain stdlib dataclasses
(it imports only the v0.3 orchestration ``SparcPhaseId``, never redefining it), no
npm / @vercel/detect-agent / requests -- so importing the contract never drags in a
heavy dep (those land in the impl waves when actually used). Mirrors the v0.1
foundation, v0.2 memory, v0.3 orchestration + governance, and v0.4 tools
``_shared``.
"""

__all__: list = []
