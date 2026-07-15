"""Local-file span exporter -- the zero-dependency fallback (Article XIV).

When no OTLP endpoint is configured, spans are appended as JSON Lines to
``.cexai/traces/spans.jsonl`` (one span per line). This keeps every component
observable with no collector, no network, and no credentials -- the default in
local dev and offline runtimes. Serialization reuses ``ReadableSpan.to_json``
(framework-native; Article VIII) compacted to a single line.

absorbs: 05_agno/observability-otel
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

__all__ = ["LocalFileSpanExporter", "build_fallback_exporter"]

_DEFAULT_DIR = Path(".cexai") / "traces"
_FILE_NAME = "spans.jsonl"


class LocalFileSpanExporter(SpanExporter):
    """Append exported spans as JSONL to ``<directory>/spans.jsonl``.

    Paired with a ``SimpleSpanProcessor`` so each span is flushed to disk the
    moment it ends -- no buffering, so a crash loses at most the in-flight span.
    """

    def __init__(self, directory: str | Path | None = None) -> None:
        self._dir = Path(directory) if directory else _DEFAULT_DIR
        self._path = self._dir / _FILE_NAME

    @property
    def path(self) -> Path:
        """Absolute-or-relative path of the JSONL sink (for callers/tests)."""
        return self._path

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        self._dir.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            for span in spans:
                handle.write(span.to_json(indent=None))
                handle.write("\n")
        return SpanExportResult.SUCCESS

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        # Writes are synchronous; nothing is buffered.
        return True

    def shutdown(self) -> None:
        # No handle is held open between exports; nothing to release.
        return None


def build_fallback_exporter(local_dir: str | None = None) -> LocalFileSpanExporter:
    """Construct the local-file exporter, defaulting to ``.cexai/traces``."""
    return LocalFileSpanExporter(local_dir)
