"""Span attribute redaction (05_agno FR-009).

Masks sensitive substrings in span (and span-event) attribute values BEFORE a
span is exported, so an API key or PII that lands in a trace attr never reaches
the collector or the local buffer. The v1 default pattern set is an in-code
tuple -- the SOURCE OF TRUTH (Article VIII: no new hard dep, import-light) --
mirrored for documentation/override in ``cexai/security/default_redaction.yaml``,
which is loaded LAZILY (``import yaml`` inside the loader; on ImportError or a
missing file the in-code defaults stand). Matches are MASKED, not dropped: the
matched substring is replaced with ``[REDACTED]`` so the attribute keeps its
shape and surrounding context.

The patterns are plain ASCII regexes (Article: ASCII-only code). v1 set covers
the provider API-key formats CEXAI calls plus the PII the spec names:
  * Anthropic  sk-ant-...    * OpenAI  sk-...    * Google  AIza...
  * email      * US phone    * US SSN

absorbs: 05_agno/observability-otel
"""

from __future__ import annotations

import dataclasses
import re
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any

from cexai.governance._shared.types import RedactionConfig, Span, SpanEvent

__all__ = [
    "DEFAULT_REDACTION_PATTERNS",
    "REDACTION_MASK",
    "default_redaction_config",
    "load_redaction_config",
    "redact",
]

# The mask token. Masking (not dropping) keeps the attribute present so a trace
# still shows "an authorization header was here" without leaking the secret.
REDACTION_MASK = "[REDACTED]"

# v1 default pattern set -- the in-code SOURCE OF TRUTH (FR-009). Order matters:
# the Anthropic ``sk-ant-`` form is masked before the broader OpenAI ``sk-`` form
# so a single key is never half-matched twice. Each is a standalone ASCII regex.
DEFAULT_REDACTION_PATTERNS: tuple[str, ...] = (
    r"sk-ant-[A-Za-z0-9_-]{8,}",                       # Anthropic API key
    r"sk-[A-Za-z0-9]{20,}",                            # OpenAI API key
    r"AIza[A-Za-z0-9_-]{10,}",                         # Google API key
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",  # email address
    r"\b\d{3}-\d{2}-\d{4}\b",                          # US Social Security Number
    r"\+?\d{1,2}[ .-]?\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}",  # US phone number
)

# Path to the mirrored yaml (documentation / override). Packaged next to this
# code under cexai/security/. Resolved relative to the installed package so it
# works from a wheel or an editable checkout alike.
_YAML_PATH = Path(__file__).resolve().parents[2] / "security" / "default_redaction.yaml"


def default_redaction_config() -> RedactionConfig:
    """The v1 default ``RedactionConfig`` from the in-code pattern set (the
    source of truth -- no file or yaml dependency to construct it)."""
    return RedactionConfig(patterns=DEFAULT_REDACTION_PATTERNS)


def load_redaction_config(path: str | Path | None = None) -> RedactionConfig:
    """Load redaction patterns from a yaml override, falling back to the in-code
    defaults. ``yaml`` is imported LAZILY: when PyYAML is absent (offline, no new
    hard dep) or the file is missing/empty/malformed, the in-code defaults stand.
    The yaml is expected to hold a top-level ``patterns:`` list of ASCII regexes."""
    target = Path(path) if path is not None else _YAML_PATH
    try:
        import yaml  # lazy: not a hard dependency (Article VIII / XIV offline)
    except ImportError:
        return default_redaction_config()
    try:
        raw = target.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return default_redaction_config()
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return default_redaction_config()
    patterns = data.get("patterns") if isinstance(data, Mapping) else None
    if not patterns:
        return default_redaction_config()
    return RedactionConfig(patterns=tuple(str(p) for p in patterns))


def redact(span: Span, config: RedactionConfig) -> Span:
    """Return a copy of ``span`` with every attribute value (on the span and on
    each of its events) masked against ``config.patterns`` (FR-009). An empty
    pattern tuple is a no-op -- the same instance is returned unchanged. Frozen
    dataclasses are never mutated; a redacted span is a fresh ``dataclasses.
    replace`` so the caller's original is untouched."""
    patterns = config.patterns
    if not patterns:
        return span

    compiled = [re.compile(pattern) for pattern in patterns]

    new_attrs, attrs_changed = _redact_mapping(span.attrs, compiled)

    events_changed = False
    rebuilt_events: list[SpanEvent] = []
    for event in span.events:
        event_attrs, changed = _redact_mapping(event.attrs, compiled)
        if changed:
            events_changed = True
            rebuilt_events.append(dataclasses.replace(event, attrs=event_attrs))
        else:
            rebuilt_events.append(event)

    if not attrs_changed and not events_changed:
        return span

    return dataclasses.replace(
        span,
        attrs=new_attrs if attrs_changed else span.attrs,
        events=tuple(rebuilt_events) if events_changed else span.events,
    )


def _redact_mapping(
    attrs: Mapping[str, Any], compiled: list[re.Pattern[str]]
) -> tuple[Mapping[str, Any], bool]:
    """Mask every string value in ``attrs`` against the compiled patterns. Returns
    a (read-only mapping, changed?) pair; non-string values pass through. The
    returned mapping is a ``MappingProxyType`` so the projection stays immutable."""
    redacted: dict[str, Any] = {}
    changed = False
    for key, value in attrs.items():
        if isinstance(value, str):
            masked = _mask_value(value, compiled)
            if masked != value:
                changed = True
            redacted[key] = masked
        else:
            redacted[key] = value
    if not changed:
        return attrs, False
    return MappingProxyType(redacted), True


def _mask_value(value: str, compiled: list[re.Pattern[str]]) -> str:
    """Replace every match of every pattern in ``value`` with the mask token."""
    for pattern in compiled:
        value = pattern.sub(REDACTION_MASK, value)
    return value
