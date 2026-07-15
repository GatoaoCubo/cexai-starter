"""Open-variables protocol -- typed late-binding slots + governance (W2 core + W3 rest).

Implements Article XIX: artifacts declare ``open_vars`` filled by the compiler or
calling nucleus during F1/F3/F4. A fully filled artifact is a portable Lego block
runnable across the four supported runtimes (Claude Code, Codex, Gemini CLI,
Ollama). Schema per spec_open_variables_protocol.md (12 fields, S 2.3) + ADR 022
(12 closed type tokens, per-token validators).

W2 ships the CORE -- the ``OpenVar`` declaration model, the closed ``TYPE_TOKENS``
set, and the pure per-token validators. W3 adds the governance layer that makes a
filled artifact a transferable, auditable Lego piece:

- ``registry``  -- the loadable type-token registry (ADR 022 D-022-02): the 12 v1
  tokens + ``register_token`` MINOR extension + ``resolve_validator``.
- ``discovery`` -- a read-only index over artifact frontmatters (D-022-03):
  ``build_index`` + ``lookup`` / ``for_kind`` / ``for_type`` / ``search``.
- ``wire``      -- ``serialize_artifact`` / ``deserialize_artifact`` (spec S 5,
  D-022-04): the cross-runtime JSON wire format + the SC-004 round-trip invariant.
- ``rebind``    -- ``rebind`` (D-022-05): audited, per-variable-gated re-filling.

Public surface::

    from cexai.foundation.open_vars import (
        OpenVar, parse_open_var, validate_open_var, TYPE_TOKENS,
        FillerRole, FillerStage, FillerStrategy,
        load_registry, register_token, TokenDef,
        serialize_artifact, deserialize_artifact, PROTOCOL, PROTOCOL_VERSION,
        rebind, discovery,
    )

absorbs: cexai-specs/open-variables-protocol
"""

from __future__ import annotations

from cexai.foundation.open_vars import discovery
from cexai.foundation.open_vars.errors import (
    ConstraintViolationError,
    InvalidEnumValueError,
    InvalidStrategyError,
    KindExistenceUnverifiedError,
    MalformedOpenVarError,
    MalformedWireFormatError,
    MissingRequiredOpenVarError,
    OpenVarError,
    RebindNotPermittedError,
    TypeMismatchError,
    UnknownTypeTokenError,
    UnsupportedProtocolVersionError,
)
from cexai.foundation.open_vars.rebind import rebind
from cexai.foundation.open_vars.registry import (
    TokenDef,
    get_token,
    load_registry,
    register_token,
    resolve_validator,
)
from cexai.foundation.open_vars.schema import (
    TYPE_TOKENS,
    FillerRole,
    FillerStage,
    FillerStrategy,
    OpenVar,
    TypeToken,
    parse_open_var,
    parse_type,
)
from cexai.foundation.open_vars.validators import validate_open_var
from cexai.foundation.open_vars.wire import (
    PROTOCOL,
    PROTOCOL_VERSION,
    deserialize_artifact,
    serialize_artifact,
)

__all__ = [
    # schema
    "OpenVar",
    "parse_open_var",
    "parse_type",
    "TypeToken",
    "TYPE_TOKENS",
    "FillerRole",
    "FillerStage",
    "FillerStrategy",
    # validation
    "validate_open_var",
    # registry (W3)
    "TokenDef",
    "load_registry",
    "register_token",
    "get_token",
    "resolve_validator",
    # discovery (W3) -- the submodule (discovery.lookup/for_kind/for_type/search)
    "discovery",
    # wire (W3)
    "serialize_artifact",
    "deserialize_artifact",
    "PROTOCOL",
    "PROTOCOL_VERSION",
    # rebind (W3)
    "rebind",
    # errors
    "OpenVarError",
    "MalformedOpenVarError",
    "TypeMismatchError",
    "InvalidEnumValueError",
    "ConstraintViolationError",
    "InvalidStrategyError",
    "UnknownTypeTokenError",
    "MissingRequiredOpenVarError",
    "KindExistenceUnverifiedError",
    "UnsupportedProtocolVersionError",
    "MalformedWireFormatError",
    "RebindNotPermittedError",
]
