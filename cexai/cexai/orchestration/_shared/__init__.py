"""Shared, dependency-free primitives for the CEXAI orchestration layer.

Contains the FROZEN type contracts (``types``) shared by the topology, planning,
streaming, and sparc subsystems, and the orchestration exception hierarchy
(``errors``). Import the concrete symbols from the submodules directly, e.g.
``from cexai.orchestration._shared.types import Topology``. Kept import-light so
the hot coordination path pays no startup cost (mirrors the v0.1 foundation and
v0.2 memory ``_shared``).
"""

__all__: list = []
