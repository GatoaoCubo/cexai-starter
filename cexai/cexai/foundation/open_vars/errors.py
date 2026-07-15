"""Open-variables error vocabulary (W2 core -- schema + validators).

Rooted at ``OpenVarError`` (a ``CexaiError`` subclass) so a caller can catch the
whole open_vars subtree with one ``except``. These are the CORE errors used by
the declaration schema (spec FR-002) and the per-token validators (ADR 022
D-022-02 validator contract / spec User Story P4).

W3 adds the registry / wire / rebind governance layer and its three errors --
``UnsupportedProtocolVersionError``, ``MalformedWireFormatError``,
``RebindNotPermittedError`` -- all rooted at ``OpenVarError`` so the whole
subtree stays catchable with one ``except``.

Spec provenance: cexai-specs/_revisions/spec_open_variables_protocol.md (FR-002,
FR-015, US P4) + cexai-specs/_decisions/adr_022_open_variables_full_protocol.md
(D-022-02, D-022-04, D-022-05).

absorbs: cexai-specs/open-variables-protocol
"""

from __future__ import annotations

from cexai.foundation._shared.errors import CexaiError

__all__ = [
    "OpenVarError",
    "MalformedOpenVarError",
    "TypeMismatchError",
    "InvalidEnumValueError",
    "ConstraintViolationError",
    "InvalidStrategyError",
    "UnknownTypeTokenError",
    "MissingRequiredOpenVarError",
    "KindExistenceUnverifiedError",
    # W3 -- registry / wire / rebind governance
    "UnsupportedProtocolVersionError",
    "MalformedWireFormatError",
    "RebindNotPermittedError",
]


class OpenVarError(CexaiError):
    """Root of the open_vars subtree. Catch this to handle any open_vars failure."""


class MalformedOpenVarError(OpenVarError):
    """A declaration is structurally invalid: a missing required field, an unknown
    extra field, a non-snake_case name, an enum without ``allowed_values`` (or a
    non-enum that declares them), or a ``default_value`` set on a required var.
    Raised at the declare stage (spec FR-002)."""


class TypeMismatchError(OpenVarError):
    """A filled value does not conform to the declared type token. Raised by the
    per-token validators -- the canonical failure of the validator contract
    (ADR 022 D-022-02); also covers unparseable custom-token values (url,
    iso_date, iso_datetime, json_schema)."""


class InvalidEnumValueError(OpenVarError):
    """An ``enum`` value is not a member of ``allowed_values`` (spec FR-008)."""


class ConstraintViolationError(OpenVarError):
    """A value is type-correct but violates a declared constraint
    (min_length / max_length / pattern / minimum / maximum / min_items /
    max_items), the url length cap, the iso_datetime timezone-awareness rule, or
    a kind_ref that does not resolve against the injected kind set."""


class InvalidStrategyError(OpenVarError):
    """``default_filler_strategy: use_default_value`` was declared on a required
    variable, or without a non-null ``default_value`` (spec FR-011)."""


class UnknownTypeTokenError(OpenVarError):
    """A ``type`` token is not in the closed v1 set of 12 (ADR 022 D-022-01),
    including a ``list[T]`` whose element token is unknown or unsupported."""


class MissingRequiredOpenVarError(OpenVarError):
    """A required open_var was not filled before freeze (spec FR-006/FR-012).

    Defined here for vocabulary completeness; it is a fill-time / F6 concern that
    the W3 wire/rebind layers raise -- the W2 core declares but does not raise it.
    """


class KindExistenceUnverifiedError(OpenVarError):
    """A ``kind_ref`` value has the correct ``kind:`` format, but its target's
    EXISTENCE could not be checked -- no ``kind_resolver`` or ``known_kinds`` was
    injected into ``validate_kind_ref`` / ``validate_open_var`` (R-228). This is
    deliberately distinct from ``ConstraintViolationError`` (which means the
    target was checked AND found unknown): a format-only pass must never read to
    the caller as a verified PASS, so the un-checkable path raises instead of
    silently returning True."""


# --------------------------------------------------------------------------- #
# W3 -- registry / wire / rebind governance (ADR 022 D-022-04, D-022-05)         #
# --------------------------------------------------------------------------- #
class UnsupportedProtocolVersionError(OpenVarError):
    """A wire blob declares a ``protocol_version`` this runtime cannot accept.

    A 1.x runtime accepts ``[1.0, 1.x]`` (minor versions are additive and
    backward-compatible) and refuses ``>= 2.0`` (ADR 022 D-022-04 / spec S 5.3).
    """


class MalformedWireFormatError(OpenVarError):
    """A wire blob is structurally invalid: not parseable JSON, a missing
    top-level key (``meta`` / ``frontmatter`` / ``open_vars_declarations`` /
    ``body`` -- spec FR-015), the wrong ``meta.protocol``, an unparseable
    version string, or an artifact that is not frozen (``_open_vars_frozen``
    absent or false, spec S 5.2 step 4)."""


class RebindNotPermittedError(OpenVarError):
    """A re-bind targeted a variable whose ``rebind_allowed`` is false (the
    default) or a name that is not a declared open_var. Per-variable granular
    permission is the gate (ADR 022 D-022-05); the original artifact is never
    mutated and no audit entry is written for a refused re-bind."""
