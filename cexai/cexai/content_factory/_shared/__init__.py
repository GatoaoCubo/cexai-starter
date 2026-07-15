"""Shared, dependency-free primitives for the CEXAI content_factory layer.

Contains the FROZEN type contracts (``types``) for the content factory and its
exception hierarchy (``errors``). Import the concrete symbols from the submodules
directly, e.g. ``from cexai.content_factory._shared.types import BrandProfile``.
Kept import-light -- plain stdlib dataclasses, no moneyprinterturbo / chatterbox /
torch / ffmpeg -- so importing the contract never drags in a heavy engine (those
land lazily in the impl modules when actually wired). Mirrors the v0.1 foundation,
v0.2 memory, v0.3 orchestration + governance, v0.4 tools, and v0.5 distribution
``_shared``.
"""

__all__: list = []
