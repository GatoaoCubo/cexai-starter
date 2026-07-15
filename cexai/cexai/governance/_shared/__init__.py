"""Shared, dependency-free primitives for the CEXAI governance layer.

Contains the FROZEN type contracts (``types``) shared by the tracing, hitl, rbac,
and audit subsystems, and the governance exception hierarchy (``errors``). Import
the concrete symbols from the submodules directly, e.g. ``from cexai.governance.
_shared.types import Span``. Kept import-light -- plain stdlib dataclasses, no
OTel / pyjwt -- so importing the contract never drags in a heavy dep (those land
in W3b when actually used). Mirrors the v0.1 foundation, v0.2 memory, and v0.3
orchestration ``_shared``.
"""

__all__: list = []
