"""LocalStdioStreamChannel -- the concrete stream-json transport (02_ruflo US P3 / FR-006/007).

Implements the frozen ``StreamChannel`` protocol from
``cexai.orchestration._shared.types``: ``send(event) -> None`` and
``receive() -> Iterator[StreamEvent]``. The transport is an in-memory, newline-
delimited line buffer standing in for local stdio (Article XIV: offline, no
network, no real file descriptors; networked transport is v2). Two channels may
share one buffer to model a real pipe across endpoints (see ``__init__``).

Wire format (FR-006 'logical chunk'): exactly one ``StreamEvent`` per newline-
terminated JSON line, serialized ASCII-only (``json.dumps`` default
``ensure_ascii=True`` -- ascii-code-rule).

Two planes:
  * data plane (``type`` in {``data``, ``EOF``}) -- carried on the wire; ``receive``
    enforces monotonic ``sequence_id`` (0-indexed in v1) and terminal semantics.
  * control plane (``type == "control"``) -- backpressure directives (PAUSE/RESUME).
    Consumed by the channel OUT-OF-BAND: never written to the wire, never yielded
    by ``receive``, never counted in the monotonic sequence. While paused, data
    emission is HELD (the spec's "upstream pauses emission"); RESUME flushes the
    held chunks to the wire in order. Backpressure deferral is the one case where a
    ``send`` does not write its line immediately -- it writes once, on resume.

Termination (02 US P3):
  * a terminal ``EOF`` event MUST carry ``completion=True`` -> ``receive`` stops cleanly.
  * an ``EOF`` with ``completion=False`` -> ``StreamAbortedError(upstream, last_seq_id)``.
  * the wire ending with NO ``EOF`` at all (upstream crash) -> same abort.
  * a sequence gap (received != expected) -> ``StreamProtocolError(expected, received)``;
    the stream is not recoverable.

Coexistence (FR-007): this is ADDITIVE. It does NOT touch, replace, or break the
existing file-based signal path (``.cex/runtime/signals/``); it is the streaming
alternative a runner selects when a task is streamable, falling back to file
signals otherwise. The two mechanisms run side by side.

This subsystem REUSES the existing ``event_schema`` kind (``StreamEvent`` is its
extension per 02 Key Entities) and registers NO new kind.

absorbs: 02_ruflo/stream
"""

from __future__ import annotations

import json
from collections.abc import Iterator

from cexai.orchestration._shared.errors import StreamAbortedError, StreamProtocolError
from cexai.orchestration._shared.types import StreamEvent

# Backpressure protocol: a ``type=="control"`` StreamEvent carries one signal under
# this payload key. Exposed so callers build control events without magic strings.
BACKPRESSURE_KEY = "signal"
PAUSE = "PAUSE"
RESUME = "RESUME"

_DATA = "data"
_CONTROL = "control"
_EOF = "EOF"

# v1 streams are 0-indexed; the first data chunk MUST be sequence_id 0. A resumable
# / offset stream is v2. ``_NO_SEQUENCE`` is the "no chunk seen yet" sentinel for
# the abort report when a stream ends before any data arrives.
_FIRST_SEQUENCE_ID = 0
_NO_SEQUENCE = -1


def backpressure_event(
    *, source: str, target: str, signal: str, sequence_id: int = 0
) -> StreamEvent:
    """Build a ``type='control'`` backpressure StreamEvent (02 US P3 edge case).

    The downstream sends this back to the upstream to throttle emission. ``signal``
    must be ``PAUSE`` or ``RESUME`` (rejected otherwise -- fail loud). ``sequence_id``
    is ignored by the out-of-band control plane and defaults to 0.
    """
    if signal not in (PAUSE, RESUME):
        raise ValueError(
            f"backpressure signal must be {PAUSE!r} or {RESUME!r}, got {signal!r}"
        )
    return StreamEvent(
        source=source,
        target=target,
        sequence_id=sequence_id,
        payload={BACKPRESSURE_KEY: signal},
        type=_CONTROL,
    )


class LocalStdioStreamChannel:
    """An offline, in-memory ``StreamChannel`` over a newline-delimited line buffer.

    ``buffer`` is the shared data wire. Pass the SAME list to two channels to model a
    stdio pipe across endpoints (one ``send``s, the other ``receive``s); omit it for a
    single self-contained channel (the default -- both ends co-located, which the
    backpressure path needs since pause state is per-channel). Networked, truly
    bidirectional transport is v2.
    """

    def __init__(self, *, buffer: list[str] | None = None) -> None:
        self._wire: list[str] = [] if buffer is None else buffer
        self._pending: list[StreamEvent] = []
        self._paused: bool = False

    # -- StreamChannel protocol -------------------------------------------------- #
    def send(self, event: StreamEvent) -> None:
        """Emit one ``StreamEvent``. A ``control`` event is consumed as a backpressure
        directive (out-of-band). A ``data`` / ``EOF`` event is written as exactly one
        newline-terminated JSON line -- unless emission is paused, in which case it is
        held and flushed (written) on RESUME."""
        if event.type == _CONTROL:
            self._apply_backpressure(event)
            return
        if self._paused:
            self._pending.append(event)
            return
        self._write(event)

    def receive(self) -> Iterator[StreamEvent]:
        """Yield data chunks in monotonic ``sequence_id`` order until a completion
        ``EOF`` terminates the stream cleanly. Raises ``StreamProtocolError`` on a
        sequence gap and ``StreamAbortedError`` if the stream ends without a
        completion marker. The terminal ``EOF`` is the stop signal and is not itself
        yielded as a data chunk."""
        expected = _FIRST_SEQUENCE_ID
        last_seq = _NO_SEQUENCE
        last_source = ""
        for line in tuple(self._wire):
            event = self._decode(line)
            if event.sequence_id != expected:
                raise StreamProtocolError(expected, event.sequence_id)
            expected += 1
            last_source = event.source
            if event.type == _EOF:
                if not event.completion:
                    raise StreamAbortedError(event.source, last_seq)
                return
            last_seq = event.sequence_id
            yield event
        # Wire exhausted with no completion EOF -> upstream aborted (e.g. crash).
        raise StreamAbortedError(last_source, last_seq)

    # -- observability (backpressure policy + transport) ------------------------- #
    @property
    def is_paused(self) -> bool:
        """Whether emission is currently held by a PAUSE (cleared by RESUME)."""
        return self._paused

    @property
    def pending(self) -> tuple[StreamEvent, ...]:
        """Data chunks held while paused, awaiting RESUME (read-only snapshot)."""
        return tuple(self._pending)

    def wire_lines(self) -> tuple[str, ...]:
        """The raw newline-terminated JSON lines currently on the data wire
        (read-only snapshot) -- the inspectable transport for the in-memory model."""
        return tuple(self._wire)

    # -- internals --------------------------------------------------------------- #
    def _apply_backpressure(self, event: StreamEvent) -> None:
        """Update pause state from a control event. PAUSE holds emission; RESUME
        clears it and flushes held chunks to the wire in arrival order. The control
        event itself is out-of-band -- never written to the wire."""
        signal = event.payload.get(BACKPRESSURE_KEY)
        if signal == PAUSE:
            self._paused = True
        elif signal == RESUME:
            self._paused = False
            held, self._pending = self._pending, []
            for chunk in held:
                self._write(chunk)
        else:
            raise ValueError(f"unknown backpressure signal: {signal!r}")

    def _write(self, event: StreamEvent) -> None:
        self._wire.append(self._encode(event))

    @staticmethod
    def _encode(event: StreamEvent) -> str:
        """Serialize one StreamEvent to a single newline-terminated JSON line.
        ``ensure_ascii`` is left at its default (True) so the wire stays ASCII even
        when payload values are not (ascii-code-rule)."""
        obj = {
            "source": event.source,
            "target": event.target,
            "sequence_id": event.sequence_id,
            "payload": dict(event.payload),
            "type": event.type,
            "completion": event.completion,
        }
        return json.dumps(obj) + "\n"

    @staticmethod
    def _decode(line: str) -> StreamEvent:
        """Parse one JSON line back into a StreamEvent (inverse of ``_encode``)."""
        obj = json.loads(line)
        return StreamEvent(
            source=obj["source"],
            target=obj["target"],
            sequence_id=obj["sequence_id"],
            payload=obj["payload"],
            type=obj["type"],
            completion=obj.get("completion", False),
        )
