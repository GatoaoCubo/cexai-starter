"""Shared, dependency-free primitives for the CEXAI tools layer.

Contains the FROZEN type contracts (``types``) shared by the ingestion, research,
reposynth, and browser subsystems, and the tools exception hierarchy (``errors``).
Import the concrete symbols from the submodules directly, e.g. ``from cexai.tools.
_shared.types import FetchResult``. Kept import-light -- plain stdlib dataclasses,
no scrapling / playwright / pyjwt / requests -- so importing the contract never
drags in a heavy dep (those land in the impl waves when actually used). Mirrors
the v0.1 foundation, v0.2 memory, v0.3 orchestration, and v0.3 governance
``_shared``.
"""

__all__: list = []
