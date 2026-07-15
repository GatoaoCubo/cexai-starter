"""Re-bind governance -- audited re-filling of a frozen artifact (ADR 022 D-022-05).

A re-bind produces a NEW frozen artifact version by re-filling specific open
variables; the original is never mutated (spec S 3 Stage 6). Each target
variable must opt in via per-variable ``rebind_allowed`` (default false) -- the
gate that keeps a portable Lego piece from drifting silently across deployments.
A refused re-bind raises ``RebindNotPermittedError`` and writes nothing.

Audit-first contract (D-022-05 step 4): on a permitted, validated re-bind the
operation appends one JSONL entry to ``.cex/runtime/rebind_log.jsonl`` BEFORE
returning the new artifact. The entry records full provenance -- before/after
versions, actor, rationale, and per-variable before/after values -- so the
provenance chain survives every divergence point. All permission and value
validation happen BEFORE any write, so a refused or invalid re-bind leaves the
log untouched.

This is the only file-I/O surface in the open_vars subsystem (validators stay
pure). The log path is injectable (``log_path=``) so tests target a tmp dir and
never the real ``.cex/runtime``; the default resolves the repo's ``.cex/runtime``
by walking up for the ``.cex`` directory. The clock + uuid are the only impurity,
appropriate for an audit record.

Spec provenance: cexai-specs/_decisions/adr_022_open_variables_full_protocol.md
(D-022-05 per-variable permission + audit log schema) +
cexai-specs/_revisions/spec_open_variables_protocol.md (S 3 Stage 6, US P7).

absorbs: cexai-specs/open-variables-protocol
"""

from __future__ import annotations

import copy
import datetime as _dt
import json
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from cexai.foundation.open_vars.errors import RebindNotPermittedError
from cexai.foundation.open_vars.schema import parse_open_var
from cexai.foundation.open_vars.validators import validate_open_var

__all__ = ["rebind"]

_DEFAULT_LOG_RELPATH = Path(".cex") / "runtime" / "rebind_log.jsonl"


def rebind(
    artifact: Mapping[str, Any],
    new_values: Mapping[str, Any],
    *,
    actor: str,
    rationale: str,
    log_path: str | Path | None = None,
) -> dict[str, Any]:
    """Re-bind ``new_values`` into a copy of ``artifact``, returning a NEW
    versioned frozen artifact and appending one audit entry.

    Every name in ``new_values`` MUST be a declared open_var with
    ``rebind_allowed: true`` (else ``RebindNotPermittedError``), and each new
    value MUST pass its declaration's validator (else the validator's specific
    error, e.g. ``TypeMismatchError`` / ``InvalidEnumValueError``). Both checks
    run before any state change, so a rejection writes no audit entry and does
    not touch ``artifact``. On success the artifact's ``version`` minor-bumps,
    ``_filled_vars`` is updated, ``_frozen_at`` / ``_frozen_by`` are refreshed,
    and a JSONL entry is appended to ``log_path`` BEFORE returning.
    """
    declarations = artifact.get("open_vars_declarations") or []
    decl_by_name = {
        d.get("name"): d for d in declarations if isinstance(d, Mapping) and d.get("name")
    }

    # Phase 1 -- gate + validate everything BEFORE any mutation or write.
    for name, value in new_values.items():
        declaration = decl_by_name.get(name)
        if declaration is None:
            raise RebindNotPermittedError(f"{name!r} is not a declared open_var")
        if not declaration.get("rebind_allowed", False):
            raise RebindNotPermittedError(
                f"open_var {name!r} is not rebindable (rebind_allowed is false)"
            )
        validate_open_var(parse_open_var(declaration), value)

    # Phase 2 -- build the new versioned artifact (original untouched).
    frontmatter = artifact.get("frontmatter") or {}
    filled_before = dict(frontmatter.get("_filled_vars") or {})
    version_before = str(frontmatter.get("version", "1.0.0"))
    version_after = _bump_minor(version_before)
    now_iso = _dt.datetime.now(_dt.timezone.utc).isoformat()

    new_artifact = copy.deepcopy(dict(artifact))
    new_fm = new_artifact.setdefault("frontmatter", {})
    new_filled = dict(filled_before)
    new_filled.update(new_values)
    new_fm["_filled_vars"] = new_filled
    new_fm["version"] = version_after
    new_fm["_frozen_at"] = now_iso
    new_fm["_frozen_by"] = actor

    # Phase 3 -- audit-first: append the entry BEFORE returning (D-022-05 step 4).
    entry = _audit_entry(
        frontmatter=frontmatter,
        version_before=version_before,
        version_after=version_after,
        now_iso=now_iso,
        actor=actor,
        rationale=rationale,
        new_values=new_values,
        filled_before=filled_before,
    )
    _append_audit(entry, log_path)
    return new_artifact


# --------------------------------------------------------------------------- #
# audit + versioning helpers                                                    #
# --------------------------------------------------------------------------- #
def _audit_entry(
    *,
    frontmatter: Mapping[str, Any],
    version_before: str,
    version_after: str,
    now_iso: str,
    actor: str,
    rationale: str,
    new_values: Mapping[str, Any],
    filled_before: Mapping[str, Any],
) -> dict[str, Any]:
    rebound_vars = [
        {
            "name": name,
            "value_before": filled_before.get(name),
            "value_after": value,
            "rebind_allowed_at_authoring": True,
        }
        for name, value in new_values.items()
    ]
    unchanged_vars = sorted(set(filled_before) - set(new_values))
    return {
        "event_id": str(uuid.uuid4()),
        "iso_timestamp": now_iso,
        "source_artifact": {
            "id": frontmatter.get("id"),
            "kind": frontmatter.get("kind"),
            "version_before": version_before,
            "version_after": version_after,
            "frozen_at_before": frontmatter.get("_frozen_at"),
        },
        "rebind_actor": {"actor": actor, "rationale": rationale},
        "rebound_vars": rebound_vars,
        "unchanged_vars": unchanged_vars,
    }


def _append_audit(entry: Mapping[str, Any], log_path: str | Path | None) -> None:
    path = Path(log_path) if log_path is not None else _default_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _default_log_path() -> Path:
    """Resolve ``<repo>/.cex/runtime/rebind_log.jsonl`` by walking up for the
    ``.cex`` directory; fall back to a cwd-relative path if none is found."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".cex").is_dir():
            return parent / _DEFAULT_LOG_RELPATH
    return _DEFAULT_LOG_RELPATH


def _bump_minor(version: str) -> str:
    """Minor-bump a ``MAJOR.MINOR[.PATCH]`` string, resetting patch to 0
    (spec US P7: 1.0.0 -> 1.1.0). Unparseable input falls back to 1.0.0's bump."""
    parts = str(version).split(".")
    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
    except (ValueError, IndexError):
        major, minor = 1, 0
    return f"{major}.{minor + 1}.0"
