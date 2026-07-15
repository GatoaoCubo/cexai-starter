"""Frozen type contracts for the CEXAI governance layer -- the v0.3-W3 freeze.

These names and shapes are FROZEN for the whole v0.3-W3 (agno governance)
milestone. Every W3b cell -- OTel mission-tree tracing, HITL approval gates, RBAC
authorization -- imports these symbols and MUST NOT change their names or fields.
If a shape must evolve, that is a versioned, peer-reviewed change, not an
in-flight edit. This mirrors the v0.1 foundation, v0.2 memory, and v0.3-W0
orchestration freeze discipline in ``cexai.{foundation,memory,orchestration}.
_shared.types``.

Design constraints (Article VIII -- Anti-Abstraction):
  * stdlib typing only -- NO pydantic, NO OTel, NO pyjwt in this contract. The
    heavy deps land in W3b when actually wired; the freeze stays import-light.
  * every value type is an immutable ``@dataclass(frozen=True, slots=True)``.
  * collection fields are tuples / read-only mappings so instances are safely
    shareable across threads, nuclei, and providers without defensive copying.

Three governance subsystems share one vocabulary here:
  * tracing  (observability)  -- Span, SpanEvent, RedactionConfig, SpanOperation;
                                 Tracer.
  * hitl     (approval gates) -- ApprovalRequest, ApprovalStatus, ApprovalPolicy;
                                 ApprovalGate.
  * rbac     (authorization)  -- Role, AuthToken; AuthGuard.

These compose with -- they do NOT replace -- the existing v0.1
``cexai.foundation.tracing`` substrate (OTLP exporter + ``.cexai/traces`` local
fallback). ``Span`` / ``SpanEvent`` are the typed PROJECTION of an emitted OTel
span (precedent: orchestration's ``TopologyRun`` is "tracked as an OTel span at
runtime; this is its typed projection"); W3b's mission-tree tracer wraps
``foundation.tracing.get_tracer`` and projects into these dataclasses.

TAXONOMY NOTE (founder rule, taxonomy-neutral wave): these are Python CODE types.
Per N07's locked W3 decision this wave REUSES existing kinds -- ``hitl_config``
(HITL policy), ``rbac_policy`` + ``role_assignment`` (RBAC roles), ``trace_config``
(tracing config). OTel spans and JWT auth tokens are RUNTIME DATACLASSES, NOT
kinds. The NEW kinds (``approval_request``; a lean ``audit_event``) are registered
LATER by a dedicated W3b ADR cell -- NOT here. ``AuthToken`` as a kind is DEFERRED
to v1.0 (RBAC is opt-in / dormant); it is modelled here as a frozen dataclass
only. This module registers ZERO kinds and does NOT touch ``.cex/kinds_meta.json``.

Spec provenance: cexai-specs/05_agno/spec.md
  * US P1 + FR-001/002/003/009 + Key Entities (TraceSpan) -- tracing.
  * US P2 + FR-004/005/006/010 + Key Entities (ApprovalRequest) -- hitl.
  * US P3 + FR-007/008/011 + Key Entities (AuthToken) -- rbac.

absorbs: 05_agno/governance
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal, Protocol, runtime_checkable

__all__ = [
    "SpanOperation",
    "SpanEvent",
    "Span",
    "RedactionConfig",
    "ApprovalStatus",
    "ApprovalRequest",
    "ApprovalPolicy",
    "Role",
    "AuthToken",
    "Tracer",
    "ApprovalGate",
    "AuthGuard",
]

# Immutable empty mapping -- safe shared default for the optional ``attrs`` /
# ``claims`` fields. A frozen dataclass cannot take a dict default (mutable);
# MappingProxyType is read-only, so one shared instance is correct.
_EMPTY_CONFIG: Mapping[str, Any] = MappingProxyType({})


# --------------------------------------------------------------------------- #
# Tracing subsystem (cexai-specs/05_agno US P1) -- OTel mission span tree.       #
# --------------------------------------------------------------------------- #
# The six operations every mission emits a span for (05 FR-001). ``Span.operation``
# stays ``str`` so a future operation kind can ride along without breaking the
# contract; this Literal is the canonical, benchmark-enforced set. Named for the
# ``operation`` field (FR-001 wording) rather than OTel's ``SpanKind`` -- which
# foundation.tracing already re-exports for the CLIENT/SERVER/INTERNAL role -- so
# the two never collide in the tracing namespace.
SpanOperation = Literal[
    "mission",
    "wave",
    "nucleus",
    "dispatch",
    "tool_call",
    "llm_call",
]


@dataclass(frozen=True, slots=True)
class SpanEvent:
    """A point-in-time event attached to a ``Span`` (05 US P1 acceptance #2). The
    canonical case is a crash: ``name == 'exception'`` with ``attrs`` carrying
    ``{exception_class, message, stack_trace}`` (Python traceback for in-process
    errors, or LLM-emitted error JSON for LLM errors). ``timestamp`` is ISO-8601;
    ``attrs`` is read-only and redactable per ``RedactionConfig``."""

    name: str
    timestamp: str
    attrs: Mapping[str, Any] = _EMPTY_CONFIG


@dataclass(frozen=True, slots=True)
class Span:
    """One node of a mission span tree -- the typed projection of an emitted OTel
    span (05 US P1 / FR-001/002, Key Entities: TraceSpan). ``parent_id`` is
    ``None`` only for the root mission span (no predecessor); every other span
    links to its parent, preserving the parent-child hierarchy (FR-002).
    ``operation`` is one of ``SpanOperation`` (kept ``str`` for extension
    headroom); ``start`` is ISO-8601 and ``end`` is ``None`` while the span is
    open. ``attrs`` is the read-only attribute bag (redactable, FR-009); ``events``
    is the ordered event trail (e.g. an ``exception`` event)."""

    span_id: str
    parent_id: str | None
    operation: str
    start: str
    end: str | None
    attrs: Mapping[str, Any] = _EMPTY_CONFIG
    events: tuple[SpanEvent, ...] = ()


@dataclass(frozen=True, slots=True)
class RedactionConfig:
    """Redaction policy for sensitive span attributes (05 FR-009). ``patterns`` is
    a tuple of regexes; a matching attribute value is masked before export. W3b
    ships the v1 default set (API-key regexes for Anthropic ``sk-ant-*`` / OpenAI
    ``sk-*`` / Google ``AIza*``, plus email / phone / US-SSN) loaded from
    ``cexai/security/default_redaction.yaml``; an empty tuple redacts nothing."""

    patterns: tuple[str, ...] = ()


# --------------------------------------------------------------------------- #
# HITL subsystem (cexai-specs/05_agno US P2) -- human approval gates.            #
# --------------------------------------------------------------------------- #
# The approval lifecycle states (05 US P2 acceptance #1-#4). A freshly emitted
# request is ``pending``; ``denied`` / ``timeout`` are terminal aborts (the
# mission marks the step ``denied_by_human`` / ``approval_timeout`` respectively).
ApprovalStatus = Literal[
    "pending",
    "approved",
    "denied",
    "timeout",
]


@dataclass(frozen=True, slots=True)
class ApprovalRequest:
    """A human-approval request emitted when a HITL-tagged operation is reached
    (05 US P2 acceptance #1, Key Entities: ApprovalRequest). ``operation`` is the
    gated action (e.g. ``publish_to_social_media``); ``requester`` is the nucleus
    / agent that attempted it; ``expires_at`` is the ISO-8601 timeout deadline
    (default policy 24h, US P2 #4); ``status`` is one of ``ApprovalStatus`` -- a
    freshly emitted request carries ``pending``."""

    request_id: str
    operation: str
    requester: str
    expires_at: str
    status: str


@dataclass(frozen=True, slots=True)
class ApprovalPolicy:
    """An M-of-N approval policy (05 FR-010). ``approvers_required`` is M (the
    number of distinct approvals needed before the action proceeds) and
    ``approvers_total`` is N (the size of the eligible approver set). A single
    approver is the 1-of-1 case. Validity (``1 <= required <= total``) is the
    W3b HITL layer's concern -- this is a dumb typed container (Article VIII)."""

    approvers_required: int
    approvers_total: int


# --------------------------------------------------------------------------- #
# RBAC subsystem (cexai-specs/05_agno US P3) -- opt-in JWT authorization.        #
# --------------------------------------------------------------------------- #
# The two v1 roles (05 US P3 / FR-007). ``dev`` may dispatch; ``viewer`` is
# read-only (a dispatch attempt is rejected 403, US P3 acceptance #1). Dev mode
# with no token is allowed with zero overhead (FR-008) -- that path constructs no
# ``AuthToken`` at all. ``AuthToken.role`` stays ``str`` for extension headroom.
Role = Literal[
    "viewer",
    "dev",
]


@dataclass(frozen=True, slots=True)
class AuthToken:
    """The verified claims of a JWT (05 US P3, Key Entities: AuthToken). ``subject``
    is the authenticated principal; ``role`` is one of ``Role``; ``expires_at`` is
    the ISO-8601 expiry (an expired token yields 401 + ``WWW-Authenticate`` per
    FR-011, handled in W3b); ``claims`` is the read-only remaining JWT claim set.
    This is the verified projection, NOT the wire token -- signature verification
    happens in the W3b RBAC layer before an ``AuthToken`` is constructed."""

    subject: str
    role: str
    expires_at: str
    claims: Mapping[str, Any] = _EMPTY_CONFIG


# --------------------------------------------------------------------------- #
# Protocols -- the seams W3b implements. Structural (no base class required);    #
# runtime_checkable allows isinstance smoke checks. Each maps to a contract      #
# test signature frozen in tests/governance/contract.                           #
# --------------------------------------------------------------------------- #
@runtime_checkable
class Tracer(Protocol):
    """The mission span-tree seam (05 US P1 / FR-001/002). ``start_span`` opens a
    span for ``operation``, linked to ``parent_id`` (``None`` for the root mission
    span), and returns it; ``emit`` records a completed span to the active
    exporter. W3b ships the concrete tracer over ``foundation.tracing`` (OTLP with
    graceful degrade to ``.cexai/traces/buffer/{mission_id}.jsonl``, FR-003); the
    contract test ``test_tracer_emits_span_tree`` drives it RED->GREEN."""

    def start_span(self, operation: str, parent_id: str | None = None) -> Span:
        """Open a span for ``operation`` under ``parent_id`` and return it."""
        ...

    def emit(self, span: Span) -> None:
        """Record a completed ``span`` to the active exporter."""
        ...


@runtime_checkable
class ApprovalGate(Protocol):
    """The HITL approval seam (05 US P2 / FR-005). ``request`` emits an
    ``ApprovalRequest`` (status ``pending``) for a HITL-tagged ``operation`` and
    pauses the caller; ``await_decision`` blocks until a human records a verdict
    (or the timeout fires) and returns the terminal ``ApprovalStatus`` value
    (``approved`` | ``denied`` | ``timeout``). W3b ships the v1 file-based gate
    (FR-006); the contract test ``test_approval_gate_pauses_until_decision``
    drives it."""

    def request(self, operation: str, requester: str) -> ApprovalRequest:
        """Emit a ``pending`` ``ApprovalRequest`` for a HITL-tagged operation."""
        ...

    def await_decision(self, request_id: str) -> str:
        """Block until a verdict is recorded; return the terminal status value."""
        ...


@runtime_checkable
class AuthGuard(Protocol):
    """The RBAC authorization seam (05 US P3 / FR-007/008). ``authorize`` returns
    ``True`` if ``token`` may perform ``operation`` and ``False`` otherwise (a
    ``viewer`` dispatch attempt returns ``False`` -> the caller raises
    ``RbacForbiddenError`` [403], US P3 acceptance #1). In dev mode (no token,
    FR-008) the guard is never consulted -- zero overhead. W3b ships the concrete
    JWT guard; the contract test ``test_rbac_viewer_forbidden`` drives it."""

    def authorize(self, token: AuthToken, operation: str) -> bool:
        """Return whether ``token`` is permitted to perform ``operation``."""
        ...
