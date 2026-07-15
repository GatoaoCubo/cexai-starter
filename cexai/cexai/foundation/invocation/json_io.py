"""Output rendering for the dual-invocation layer (W3).

Two renderers over a feature's return value:
  * ``to_json`` -- deterministic (sorted keys), ASCII-safe, ANSI-stripped JSON for
    ``--json`` / machine consumers and the CLI<->library parity check.
  * ``to_text`` -- a compact human-readable rendering for the default CLI mode.

ANSI escape sequences are stripped from every string the layer emits so machine
output never carries terminal control codes (spec P3: "ANSI codes stripped in
--json mode"). ``to_json`` being order-independent and stable is what makes the
parity assertion ``json.loads(cli_stdout) == library_result`` sound (SC-003).

absorbs: 08_goose/dual-invocation
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any

__all__ = ["to_json", "to_text", "strip_ansi"]

# CSI / SGR and related escape sequences (e.g. "\x1b[31m", "\x1b[0m"). Compiled once.
_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from ``text``."""
    return _ANSI_RE.sub("", text)


def _clean(obj: Any) -> Any:
    """Recursively strip ANSI from every string in a JSON-like structure,
    returning a new structure with control-code-free strings. Mapping keys are
    coerced to ``str`` so the result is always JSON-serializable with sorted keys."""
    if isinstance(obj, str):
        return strip_ansi(obj)
    if isinstance(obj, Mapping):
        return {str(key): _clean(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(value) for value in obj]
    return obj


def to_json(obj: Any) -> str:
    """Serialize ``obj`` to a stable JSON string: keys sorted, ASCII-escaped,
    ANSI stripped, compact separators.

    Equal objects always serialize to equal strings, so this is a sound basis for
    the CLI<->library parity assertion. Non-JSON-native values fall back to
    ``str`` so a feature returning, say, a dataclass still renders."""
    return json.dumps(
        _clean(obj),
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )


def to_text(obj: Any) -> str:
    """Render ``obj`` as human-readable text for the default CLI mode.

    Scalars render as their plain string; mappings render one ``key: value`` line
    per sorted key; sequences render one item per line. ANSI is stripped so the
    default output stays clean in pipes and captured logs alike."""
    cleaned = _clean(obj)
    if isinstance(cleaned, str):
        return cleaned
    if isinstance(cleaned, Mapping):
        return "\n".join(f"{key}: {_scalar(value)}" for key, value in sorted(cleaned.items()))
    if isinstance(cleaned, (list, tuple)):
        return "\n".join(_scalar(value) for value in cleaned)
    return str(cleaned)


def _scalar(value: Any) -> str:
    """Render a value inside a single text line: scalars plain, containers as
    compact JSON so one line stays parseable and unambiguous."""
    if isinstance(value, bool) or value is None:
        return str(value)
    if isinstance(value, (int, float, str)):
        return str(value)
    return to_json(value)
