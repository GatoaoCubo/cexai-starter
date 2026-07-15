"""Shared, dependency-free primitives for the CEXAI foundation.

Contains the FROZEN type contracts (``types``) and the exception hierarchy
(``errors``). Import the concrete symbols from the submodules directly, e.g.
``from cexai.foundation._shared.types import LlmRequest``. Kept import-light so
hot paths pay no startup cost.
"""

__all__: list = []
