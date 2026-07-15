"""Streaming subsystem -- stream-json agent-to-agent chaining.

Lets a downstream nucleus begin work on partial upstream output via monotonic,
newline-terminated ``StreamEvent`` chunks, coexisting with the existing
file-based signals (cexai-specs/02_ruflo US P3 / FR-006/007). ``LocalStdioStreamChannel``
(v0.3-W2) implements the frozen ``StreamChannel`` contract over an in-memory line
buffer (offline; networked transport is v2); the frozen ``StreamEvent`` /
``StreamChannel`` contracts live in ``cexai.orchestration._shared.types``.

Coexistence (FR-007): this is the ADDITIVE streaming alternative -- it does NOT
replace or touch the file-based signal path (``.cex/runtime/signals/``). REUSES the
existing ``event_schema`` kind (``StreamEvent`` is its extension); registers NO new kind.

Public surface:
  * ``LocalStdioStreamChannel`` -- send/receive, monotonic-seq enforcement,
    EOF/completion termination, PAUSE/RESUME backpressure.
  * ``backpressure_event`` + ``PAUSE`` / ``RESUME`` / ``BACKPRESSURE_KEY``
    -- the out-of-band control-plane helper + its protocol constants.

absorbs: 02_ruflo/stream
"""

from .channel import (
    BACKPRESSURE_KEY,
    PAUSE,
    RESUME,
    LocalStdioStreamChannel,
    backpressure_event,
)

__all__ = [
    "LocalStdioStreamChannel",
    "backpressure_event",
    "BACKPRESSURE_KEY",
    "PAUSE",
    "RESUME",
]
