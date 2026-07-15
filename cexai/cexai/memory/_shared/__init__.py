"""Shared, dependency-free primitives for the CEXAI memory substrate.

Contains the FROZEN type contracts (``types``) shared by the vector, graph, and
episodic subsystems, and the memory exception hierarchy (``errors``). Import the
concrete symbols from the submodules directly, e.g.
``from cexai.memory._shared.types import MemoryRecord``. Kept import-light so the
hot retrieval path pays no startup cost (mirrors the v0.1 foundation _shared).
"""

__all__: list = []
