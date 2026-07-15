"""Session compression -- session events -> structured + narrative digest (07 FR-002/012).

Two implementations of the ``Compressor`` seam plus the shared topic-text
derivation used to compute a session's topic embedding (07 US P1 "topic"):

  * ``DeterministicCompressor`` -- dependency-free, no LLM. Walks the events and
    extracts decisions / files_touched / errors into a typed digest AND renders a
    stable free-text narrative. This is the OFFLINE path (Article XIV) and the
    documented v0.2 fallback when no Ollama is reachable (FLAG, not a stall).
  * ``OllamaCompressor`` -- the production default (qwen2.5:7b per master_plan,
    FR-002). The ``ollama`` client is imported lazily so importing this module
    never requires it; any failure surfaces as ``CompressionUnavailableError``.

Compression is lossy + documented (constitution CM3): the structured digest
carries ``original_length`` + ``compression_ratio`` so a reviewer can judge what
was dropped. BOTH structured and narrative are returned and stored separately
(FR-012) -- the store assembles them into a ``CompressedSession`` and stamps the
topic embedding.

absorbs: 07_claude-mem/episodic
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable

from cexai.memory._shared.errors import MemoryError as _MemoryError
from cexai.memory._shared.types import SessionEvent

__all__ = [
    "Compressor",
    "DeterministicCompressor",
    "OllamaCompressor",
    "CompressionUnavailableError",
    "topic_text",
    "DEFAULT_COMPRESSION_MODEL",
]

# Production compression model (07 FR-002, RESOLVED to qwen2.5:7b in spec).
DEFAULT_COMPRESSION_MODEL = "qwen2.5:7b"

# Topic embedding is computed over the first 500 tokens of meaningful content
# (07 US P1 "topic" definition). A declared session_start ``topic`` is the
# highest-signal descriptor, so it takes precedence over event body text.
_TOPIC_TOKEN_LIMIT = 500


class CompressionUnavailableError(_MemoryError):
    """The configured compression LLM could not be reached or returned nothing.

    A recoverable, expected condition (parallels EmbeddingUnavailableError): per
    the v0.2 plan, callers fall back to the ``DeterministicCompressor`` rather
    than stall. Subclasses the frozen ``MemoryError`` so one ``except`` covers the
    whole memory subtree."""


@runtime_checkable
class Compressor(Protocol):
    """The compression seam: a session's events -> ``(structured, narrative)``.
    ``name`` identifies the compressor for provenance. The store wraps the result
    in a ``CompressedSession`` and adds the topic embedding (FR-012 keeps the two
    outputs separate)."""

    name: str

    def compress(
        self, session_id: str, events: Sequence[SessionEvent]
    ) -> tuple[Mapping[str, Any], str]:
        """Return ``(structured_digest, narrative_summary)`` for the session."""
        ...


def topic_text(events: Sequence[SessionEvent]) -> str:
    """Derive the session's topic text (07 US P1). Prefer a declared session_start
    ``topic`` payload; otherwise fall back to the first 500 tokens of all string
    payload values (boilerplate event TYPES carry no extra weight -- their text
    payloads still count). Empty when the session has no textual content."""
    declared = ""
    body_parts: list[str] = []
    for event in events:
        for key, value in dict(event.payload).items():
            if not isinstance(value, str):
                continue
            if key == "topic" and not declared:
                declared = value.strip()
            else:
                body_parts.append(value)
    if declared:
        return " ".join(declared.split()[:_TOPIC_TOKEN_LIMIT])
    return " ".join(" ".join(body_parts).split()[:_TOPIC_TOKEN_LIMIT])
    # v0.2-W2-stretch: FR-013 topic-drift split -- embed FIRST 500 vs LAST 500
    # tokens and flag multi_topic when cosine < 0.6. Deferred (single topic in v0.2).


def _payload_str(payload: Mapping[str, Any], *keys: str) -> str | None:
    """First string value among ``keys`` in ``payload`` (None if none present)."""
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


class DeterministicCompressor:
    """A no-LLM ``Compressor`` (offline + reproducible). ``compress`` is pure: the
    same events always yield the same structured digest + narrative, so the whole
    episodic substrate is testable without a model (Article XIV)."""

    name: str = "deterministic-v1"

    def compress(
        self, session_id: str, events: Sequence[SessionEvent]
    ) -> tuple[Mapping[str, Any], str]:
        decisions: list[str] = []
        files: list[str] = []
        errors: list[str] = []
        for event in events:
            payload = dict(event.payload)
            if event.type == "decision":
                choice = _payload_str(payload, "choice", "decision", "value")
                if choice:
                    decisions.append(choice)
            if event.type == "error":
                errors.append(_payload_str(payload, "message", "error") or "error")
            single = _payload_str(payload, "file", "path")
            if single:
                files.append(single)
            many = payload.get("files")
            if isinstance(many, (list, tuple)):
                files.extend(str(item) for item in many)

        focus = topic_text(events)
        files_sorted = sorted(set(files))
        original_length = sum(
            len(json.dumps(dict(event.payload), sort_keys=True, ensure_ascii=True))
            for event in events
        )

        parts = [f"Session {session_id}: {len(events)} events."]
        if focus:
            parts.append(f"Focus: {focus}.")
        if decisions:
            parts.append("Decisions: " + "; ".join(decisions) + ".")
        if files_sorted:
            parts.append("Files: " + ", ".join(files_sorted) + ".")
        if errors:
            parts.append(f"Errors: {len(errors)}.")
        narrative = " ".join(parts)

        structured: dict[str, Any] = {
            "decisions": decisions,
            "files_touched": files_sorted,
            "errors": errors,
            "kc_candidates": [],  # v0.2-W2-stretch: P2 session->KC distillation (FR-006)
            "event_count": len(events),
            "original_length": original_length,
            "compression_ratio": round(original_length / max(len(narrative), 1), 2),
        }
        return structured, narrative


class OllamaCompressor:
    """The production ``Compressor`` (qwen2.5:7b via Ollama, FR-002).

    Construction is connectionless -- it only records config. The ``ollama`` client
    is imported lazily inside ``_call`` so this module imports without the optional
    ``cexai[memory]`` extra. Any failure (missing client, refused connection,
    unparseable output) is wrapped as ``CompressionUnavailableError`` so the caller
    can fall back to ``DeterministicCompressor`` instead of stalling."""

    def __init__(self, model: str = DEFAULT_COMPRESSION_MODEL, host: str | None = None) -> None:
        self.model = model
        self.host = host

    @property
    def name(self) -> str:
        return f"ollama:{self.model}"

    def compress(
        self, session_id: str, events: Sequence[SessionEvent]
    ) -> tuple[Mapping[str, Any], str]:
        try:
            return self._call(session_id, events)
        except CompressionUnavailableError:
            raise
        except Exception as exc:  # ImportError, ConnectionError, JSONDecodeError, ...
            raise CompressionUnavailableError(
                f"ollama compressor {self.model!r} unavailable: {exc}"
            ) from exc

    def _call(
        self, session_id: str, events: Sequence[SessionEvent]
    ) -> tuple[Mapping[str, Any], str]:
        """Perform the live compression call. Isolated so all transport errors
        funnel through ``compress``'s wrapper."""
        import ollama  # lazy: optional dependency, not needed to import this module

        client = ollama.Client(host=self.host) if self.host else ollama
        log = "\n".join(
            f"[{event.seq}] {event.type}: "
            + json.dumps(dict(event.payload), sort_keys=True, ensure_ascii=True)
            for event in events
        )
        prompt = (
            "Compress this session log into JSON with two keys: "
            '"structured" (object with decisions, files_touched, errors, kc_candidates) '
            'and "narrative" (a short free-text summary). Session ' + session_id + ":\n" + log
        )
        response = client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            format="json",
        )
        data = json.loads(response["message"]["content"])
        structured = data.get("structured") or {}
        narrative = data.get("narrative") or ""
        if not narrative:
            raise CompressionUnavailableError("compression returned an empty narrative")
        return structured, narrative
