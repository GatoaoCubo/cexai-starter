#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEX Agent IO -- shared helpers for agent-friendly CLI output.

Implements the agent-CLI principles documented in
_docs/audit_cli_principles_v1.md:
  - Sec 3.4 [exit:N | Xms] metadata wrapper
  - Sec 3.2 stderr separator on failure ('--- stderr ---')
  - Sec 3.1 truncation policy (200 lines OR 50 KiB) with file fallback
  - Sec 2.5 stdin separation (read content from stdin OR --arg)
  - Sec 3.3 ANSI escape stripping
  - Sec 2.1 Tips Thinking error formatter

This module is import-only -- it does not run as a CLI itself.
Tools opt into agent-IO behavior by importing and calling these helpers.

Examples:
    from cex_agent_io import agent_print, truncate_or_file, read_content

    # at end of main():
    agent_print(stdout=report, exit_code=rc, started_at=t0)

    # for long content:
    display, full_path = truncate_or_file(big_text, label="search-results")
    agent_print(stdout=display, exit_code=0, started_at=t0)

    # for content args (avoid escape hell):
    body = read_content(args.note, stdin_flag=args.stdin)
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import IO

ROOT = Path(__file__).resolve().parent.parent
TMP_OUT_DIR = ROOT / ".cex" / "runtime" / "tmp_output"

# Article spec (proven in production).
DEFAULT_MAX_LINES = 200
DEFAULT_MAX_BYTES = 51200  # 50 KiB

# ANSI escape sequence pattern (covers CSI + OSC + ESC sequences).
_ANSI_RE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\))")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text. Idempotent."""
    if not text or "\x1b" not in text:
        return text
    return _ANSI_RE.sub("", text)


def _format_duration(seconds: float) -> str:
    """Format elapsed seconds for the [exit:N | Xms] tail.

    Uses ms below 10s, s above. Tail 'rounded' to keep tokens small.
    """
    if seconds < 10:
        ms = int(round(seconds * 1000))
        return f"{ms}ms"
    if seconds < 600:
        return f"{seconds:.1f}s"
    minutes = seconds / 60.0
    return f"{minutes:.1f}m"


def truncate_or_file(
    content: str,
    *,
    max_lines: int = DEFAULT_MAX_LINES,
    max_bytes: int = DEFAULT_MAX_BYTES,
    label: str = "cmd-output",
) -> tuple[str, Path | None]:
    """Apply article Sec 3.1 truncation.

    Returns (display, full_path).
    - If content fits both thresholds: full_path is None, display is content.
    - If content exceeds either: write full to tmp file, display has first
      max_lines lines + truncation marker + reference + grep/tail hints.

    Truncation is rune-safe (line-based, won't split UTF-8).
    """
    content = content or ""
    content_bytes = content.encode("utf-8", errors="replace")
    lines = content.splitlines()

    if len(lines) <= max_lines and len(content_bytes) <= max_bytes:
        return content, None

    # Write full output to a temp file.
    TMP_OUT_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp_path_str = tempfile.mkstemp(prefix=f"{label}-", suffix=".txt",
                                        dir=str(TMP_OUT_DIR), text=False)
    tmp_path = Path(tmp_path_str)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content_bytes)
    except Exception:
        # Best-effort; if we can't write the file, fall back to truncation only.
        pass

    head = "\n".join(lines[:max_lines])
    total_lines = len(lines)
    total_kb = len(content_bytes) / 1024.0
    rel = tmp_path.relative_to(ROOT) if tmp_path.is_relative_to(ROOT) else tmp_path

    display = (
        f"{head}\n\n"
        f"--- output truncated ({total_lines} lines, {total_kb:.1f}KB) ---\n"
        f"Full output: {rel.as_posix() if hasattr(rel, 'as_posix') else rel}\n"
        f"Explore:     cat \"{rel}\" | grep <pattern>\n"
        f"             tail -n 100 \"{rel}\""
    )
    return display, tmp_path


def agent_print(
    stdout: str = "",
    *,
    stderr: str = "",
    exit_code: int = 0,
    started_at: float | None = None,
    duration_seconds: float | None = None,
    strip_color: bool = True,
    out: IO | None = None,
) -> int:
    """Emit agent-formatted output: stdout + (optional stderr separator) + [exit:N | Xms].

    Article Sec 3.2: ALWAYS attach stderr on failure. We always print it when
    non-empty AND exit_code != 0; on success, stderr is suppressed (matching
    the article's "stderr is what the agent needs MOST when a command fails"
    phrasing).

    Article Sec 3.3: strip ANSI by default (override with strip_color=False).
    Article Sec 3.4: [exit:N | Xms] metadata tail.

    Returns exit_code so caller can `return agent_print(..., exit_code=rc)`.
    """
    out = out or sys.stdout

    if started_at is not None and duration_seconds is None:
        duration_seconds = max(0.0, time.time() - started_at)
    if duration_seconds is None:
        duration_seconds = 0.0

    body = strip_ansi(stdout) if strip_color else (stdout or "")
    err = strip_ansi(stderr) if strip_color else (stderr or "")

    # Body
    if body:
        out.write(body)
        if not body.endswith("\n"):
            out.write("\n")

    # Stderr separator on failure
    if exit_code != 0 and err.strip():
        out.write("--- stderr ---\n")
        out.write(err.rstrip())
        out.write("\n")

    # Metadata tail
    out.write(f"[exit:{exit_code} | {_format_duration(duration_seconds)}]\n")
    out.flush()
    return exit_code


def error_with_tip(
    message: str,
    *,
    hint: str = "",
    usage: str = "",
    example: str = "",
    out: IO | None = None,
) -> None:
    """Article Sec 2.1 Tips Thinking. Print to stderr.

    Format:
      [error] {message}
        Usage: {usage}
        Example: {example}
        Hint: {hint}

    Empty fields are skipped. Caller still controls exit code.
    """
    out = out or sys.stderr
    out.write(f"[error] {message}\n")
    if usage:
        out.write(f"  Usage: {usage}\n")
    if example:
        out.write(f"  Example: {example}\n")
    if hint:
        out.write(f"  Hint: {hint}\n")
    out.flush()


def read_content(
    arg_value: str | None,
    *,
    stdin_flag: bool = False,
    stdin_path: str = "-",
) -> str:
    """Article Sec 2.5 stdin separation.

    Resolution order:
      1. If stdin_flag is True OR arg_value is the literal "-": read sys.stdin.
      2. If arg_value starts with "@": read the file at arg_value[1:].
      3. Otherwise: return arg_value (or "" if None).

    Use this for any flag that accepts user/agent-supplied content (notes,
    task descriptions, prompts, handoff bodies). Eliminates JSON+shell double
    escape hell.
    """
    if stdin_flag or arg_value == stdin_path:
        try:
            return sys.stdin.read()
        except Exception:
            return ""

    if arg_value and arg_value.startswith("@"):
        path = Path(arg_value[1:])
        if path.exists():
            try:
                return path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
        return ""

    return arg_value or ""


def add_stdin_arg(parser, dest: str = "stdin", help_text: str = "Read content from stdin instead of args (avoids JSON+shell escape hell)"):
    """Convenience: attach a --stdin flag to an argparse parser.

    Usage:
        from cex_agent_io import add_stdin_arg, read_content
        add_stdin_arg(parser)
        ...
        body = read_content(args.note, stdin_flag=args.stdin)
    """
    parser.add_argument("--stdin", dest=dest, action="store_true", help=help_text)


# ----- Wrap entry-point for tools with `def main(argv) -> int` ------

def wrap_main(main_fn, argv: list[str], *, label: str = "tool",
              max_lines: int = DEFAULT_MAX_LINES,
              max_bytes: int = DEFAULT_MAX_BYTES,
              flag: str = "--agent-io") -> int:
    """Wrap a tool's main() to apply agent-IO when --agent-io is in argv.

    Tool integration:
        if __name__ == "__main__":
            from cex_agent_io import wrap_main
            sys.exit(wrap_main(main, sys.argv[1:], label="my_tool"))

    The wrapper:
      - Activates only if `--agent-io` (or `flag`) is in argv (then strips it).
      - Captures stdout, runs main(remaining_argv), records start/end time.
      - Truncates if needed, prints with [exit:N | Xms] tail.
      - Otherwise calls main(argv) directly (zero overhead, identical behavior).
    """
    if flag not in argv:
        return main_fn(argv)

    import io as _io
    import time as _time

    # Strip the flag so downstream argparse doesn't see it.
    forwarded = [a for a in argv if a != flag]

    buf = _io.StringIO()
    saved = sys.stdout
    sys.stdout = buf
    t0 = _time.time()
    rc = 0
    try:
        result = main_fn(forwarded)
        rc = int(result) if result is not None else 0
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 0
    finally:
        sys.stdout = saved

    captured = buf.getvalue()
    display, _full = truncate_or_file(captured, max_lines=max_lines,
                                       max_bytes=max_bytes, label=label)
    return agent_print(stdout=display, exit_code=rc, started_at=t0)


# ----- Per-verb help (article Sec 2.1 Philosophy 1) -----------------

def maybe_print_verb_help(argv: list[str], verb_help: dict[str, str]) -> bool:
    """Detect `tool <verb> --help` (or `-h`) and print verb-specific help.

    Returns True if help was printed (caller should exit 0). False if not.

    `verb_help` is a dict like {"check": "Read-only diagnostic. Returns 0 if all
    checks pass, 1 if any fail. Suitable for CI."}.

    This is the lightweight alternative to argparse subparsers -- no
    refactor needed. Caller invokes BEFORE parser.parse_args().
    """
    if len(argv) < 2:
        return False
    verb = argv[0]
    if verb not in verb_help:
        return False
    if not any(a in ("--help", "-h") for a in argv[1:]):
        return False
    print(f"=== {verb} ===")
    print(verb_help[verb])
    print()
    print("For full options: tool --help")
    return True
