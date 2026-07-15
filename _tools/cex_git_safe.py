#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_git_safe.py -- gitignore-aware safe-commit helper for the F8 site.

The F8 COLLABORATE step of the 8F pipeline saves an artifact, then commits it.
Many artifact-landing paths are intentionally gitignored (`.cex/runtime/`,
`**/compiled/`, `_docs/`, `_reports/`, several `*/P10_memory/*` instance files).
A naive `git add <path> && git commit -m msg` against such a path has TWO
failure modes:

  (A) LOUD: interactive nuclei see the "paths are ignored" error and may react
      by force-adding (`git add -f`), which pollutes the tree with files that
      were deliberately ephemeral.
  (B) SILENT FALSE-SUCCESS: a headless runner ignores the returncode, runs
      `git commit` (which prints "nothing to commit"), and still sets
      `committed = True` -- claiming a commit that never happened.

This module is the single shared fix. It checks `.gitignore` BEFORE staging,
skips ignored paths (recording them honestly), and reports `committed` based on
the REAL commit result. It NEVER force-adds and NEVER raises (degrade-never:
git missing / not a repo / any subprocess error -> a structured result dict).

Public API:
  is_git_ignored(path, *, cwd=None) -> bool
  safe_artifact_commit(paths, message, *, cwd=None, timeout=10) -> dict

No heavy imports -- stdlib only (subprocess, pathlib, typing).
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

__all__ = ["is_git_ignored", "safe_artifact_commit"]

PathLike = Union[str, Path]

# "nothing to commit" sentinels git prints when the staged set is empty (no
# real change). Matched case-insensitively against stdout+stderr so a HONEST
# committed=False is returned instead of a false success.
_NOTHING_TO_COMMIT = (
    "nothing to commit",
    "nothing added to commit",
    "no changes added to commit",
    "working tree clean",
)


def _run(
    args: Sequence[str],
    *,
    cwd: Optional[PathLike],
    timeout: int,
) -> "subprocess.CompletedProcess[str]":
    """Run a git subprocess, capturing text output. Raises on spawn failure
    (callers wrap this) so degrade-never is centralized at the API boundary."""
    return subprocess.run(
        list(args),
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def is_git_ignored(path: PathLike, *, cwd: Optional[PathLike] = None) -> bool:
    """Return True iff `path` is gitignored.

    Uses `git check-ignore -q <path>` (returncode 0 == ignored, 1 == not
    ignored, >=2 == error). Any error (git missing, not a repo) returns False
    -- the caller then tries to stage it and the commit step honestly reports
    the outcome. Degrade-never: never raises.
    """
    try:
        proc = _run(
            ["git", "check-ignore", "-q", str(path)],
            cwd=cwd,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0


def _empty_result(reason: str) -> Dict[str, object]:
    """A committed=False result carrying an explanation (no staging happened)."""
    return {
        "committed": False,
        "staged": [],
        "skipped_ignored": [],
        "reason": reason,
    }


def safe_artifact_commit(
    paths: Union[PathLike, Sequence[PathLike]],
    message: str,
    *,
    cwd: Optional[PathLike] = None,
    timeout: int = 10,
) -> Dict[str, object]:
    """Gitignore-aware commit of one or more produced artifact paths.

    For each path:
      * `git check-ignore` -> ignored paths go to `skipped_ignored` (NEVER
        force-added; a gitignored deliverable is intentionally ephemeral and
        stays on disk for the collector / N07 to read directly).
      * a non-ignored path that exists on disk is staged via `git add`.
      * a non-ignored path that does NOT exist is recorded in `reason`.

    `git commit` runs ONLY if at least one path was staged. The returncode and
    output are inspected: a "nothing to commit" outcome yields
    committed=False (HONEST) -- it never blindly claims success.

    Returns a dict:
      {
        "committed": bool,           # True only on a REAL commit
        "staged": [str, ...],        # paths handed to `git add`
        "skipped_ignored": [str, ...],  # gitignored paths (left on disk)
        "reason": str,               # short human-readable explanation
      }

    Degrade-never: git missing / not a repo / any subprocess error returns a
    committed=False result with `reason` set -- this function never raises.
    """
    # Normalize to a list of strings (accept a single path or a sequence).
    if isinstance(paths, (str, Path)):
        path_list: List[str] = [str(paths)]
    else:
        path_list = [str(p) for p in paths]

    if not path_list:
        return _empty_result("no paths given")

    skipped_ignored: List[str] = []
    to_stage: List[str] = []
    missing: List[str] = []

    for raw in path_list:
        if is_git_ignored(raw, cwd=cwd):
            skipped_ignored.append(raw)
            continue
        if not Path(raw).exists():
            missing.append(raw)
            continue
        to_stage.append(raw)

    if not to_stage:
        if skipped_ignored and not missing:
            reason = "all paths gitignored (kept on disk, intentionally uncommitted)"
        elif missing and not skipped_ignored:
            reason = "no existing non-ignored paths to stage (missing: %s)" % (
                ", ".join(missing)
            )
        else:
            reason = "nothing stageable (ignored: %d, missing: %d)" % (
                len(skipped_ignored),
                len(missing),
            )
        return {
            "committed": False,
            "staged": [],
            "skipped_ignored": skipped_ignored,
            "reason": reason,
        }

    # Stage the non-ignored existing paths. Scope the eventual commit to EXACTLY
    # these paths via a trailing `-- <paths>` pathspec so a concurrently-staged
    # foreign file is never swept into this artifact commit.
    try:
        add_proc = _run(["git", "add", "--", *to_stage], cwd=cwd, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "committed": False,
            "staged": [],
            "skipped_ignored": skipped_ignored,
            "reason": "git add failed: %s" % str(exc)[:80],
        }
    if add_proc.returncode != 0:
        detail = (add_proc.stderr or add_proc.stdout or "").strip()
        return {
            "committed": False,
            "staged": [],
            "skipped_ignored": skipped_ignored,
            "reason": "git add returncode %d: %s" % (
                add_proc.returncode,
                detail[:120],
            ),
        }

    try:
        commit_proc = _run(
            ["git", "commit", "-m", message, "--", *to_stage],
            cwd=cwd,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "committed": False,
            "staged": to_stage,
            "skipped_ignored": skipped_ignored,
            "reason": "git commit failed: %s" % str(exc)[:80],
        }

    combined = ((commit_proc.stdout or "") + "\n" + (commit_proc.stderr or "")).lower()
    nothing = any(token in combined for token in _NOTHING_TO_COMMIT)

    if commit_proc.returncode == 0 and not nothing:
        return {
            "committed": True,
            "staged": to_stage,
            "skipped_ignored": skipped_ignored,
            "reason": "committed %d path(s)" % len(to_stage),
        }

    # returncode != 0 OR a "nothing to commit" message -> HONEST committed=False.
    reason = "nothing to commit (no change staged)" if nothing else (
        "git commit returncode %d: %s" % (
            commit_proc.returncode,
            ((commit_proc.stderr or commit_proc.stdout or "").strip())[:120],
        )
    )
    return {
        "committed": False,
        "staged": to_stage,
        "skipped_ignored": skipped_ignored,
        "reason": reason,
    }


if __name__ == "__main__":  # pragma: no cover -- tiny manual smoke entry
    import sys

    if len(sys.argv) < 3:
        print("usage: cex_git_safe.py <message> <path> [<path> ...]")
        raise SystemExit(2)
    msg = sys.argv[1]
    result = safe_artifact_commit(sys.argv[2:], msg)
    print(result)
