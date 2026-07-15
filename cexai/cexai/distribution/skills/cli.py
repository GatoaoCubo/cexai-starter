"""``skills`` CLI sub-app -- install / list / verify / publish (10 + 13_vercel-skills).

A standalone ``typer.Typer`` named ``skills_app``, mirroring the episodic ``mem_app``
discipline: import-clean and independently runnable (via ``CliRunner`` or
``skills_app()``). Results go to stdout (``--json`` for machine output); diagnostics
and errors go to stderr with a non-zero exit (Article II).

Commands:
  * ``install <ref> [--frozen] [-g/--global] [--copy] [--source ...] [--lockfile P]``
        -- resolve a skill across the four sources into a typed ``InstallPlan`` (10
        SC-001 / 13 P1), emit the reasoning_trace (13 FR-012), and merge the
        ``skills.lock.v3`` entry (13 SC-001). ``--frozen`` reproduces from the
        lockfile with NO network resolution; a SHA drift / absent ref HARD-FAILS (13
        SC-002 / P2 #1).
  * ``list [-g/--global] [--lockfile P]`` -- enumerate locked skills, project and
        global scopes separated (13 P3 #3).
  * ``verify <name> [--runtime ...]`` -- the ADVISORY cross-runtime parity report
        (V10-F3: reports, never raises / demotes).
  * ``publish <name> --kind K [--runtime ...]`` -- the ENFORCING publish gate (10
        SC-002 invalid-frontmatter refusal + SC-003 claiming-yet-failing parity
        raise), wiring ``CrossRuntimeVerifier`` into the publish path.

Offline-first (Article XIV): every command uses the W1 injected-backend defaults
(``CrossAgentInstaller`` derives SHAs from the ref, detects no agents, links
nothing; ``CrossRuntimeVerifier`` reports parity). No command opens a socket, shells
to npm/git, drives a runtime, or calls an LLM. ``--frozen`` reads only the lockfile.

NOTE -- main-app mount: the foundation ``cexai`` entrypoint is a BARE command (no
callback) that delegates ``mem`` rather than ``add_typer`` (subcommands would break
``cexai <feature>``). ``skills`` subcommands carry their own flags (``--frozen`` /
``-g`` / ``--copy``) that the bare command rejects at parse time unless its
``ignore_unknown_options`` semantics are loosened -- a parser change to a shared v0.4
CLI deliberately NOT made in this integration wave. So W2 ships ``skills_app``
standalone + import-clean (as ``mem_app`` was pre-mount); the one-line context-settings
mount is deferred to the CLI-mount wave to keep the foundation parse byte-identical.

absorbs: 10_skills-sh/cli + 13_vercel-skills/cli
"""

from __future__ import annotations

import json
from typing import List, Optional

import typer

from cexai.distribution._shared.errors import (
    CrossRuntimeParityError,
    LockfileMismatchError,
    SkillValidationError,
)
from cexai.distribution._shared.types import Lockfile, SkillManifest
from cexai.distribution.skills.installer import (
    CrossAgentInstaller,
    SkillSourceUnavailableError,
)
from cexai.distribution.skills.lockfile import (
    FrozenLockViolationError,
    read_lockfile,
    resolve_frozen,
    write_lockfile,
)
from cexai.distribution.skills.publish_gate import SkillPublishGate
from cexai.distribution.skills.verifier import CrossRuntimeVerifier

__all__ = ["skills_app"]

# The canonical four install sources (10 FR-002 / 13 FR-001), custom_registry first
# (the installer orders it first regardless; this is just the default request set).
_DEFAULT_SOURCES = ("custom_registry", "registry", "git", "local")
_DEFAULT_LOCKFILE = "skills.lock.v3"

skills_app = typer.Typer(
    add_completion=False,
    help=(
        "Cross-agent skills: install (4-source + lockfile), list (project/global), "
        "verify (advisory cross-runtime), publish (enforcing gate). Offline-first."
    ),
)


def _scope_of(global_scope: bool) -> str:
    """``global`` for the ``-g`` flag, else the default ``project`` scope (13 FR-004)."""
    return "global" if global_scope else "project"


def _merge_entry(lockfile: Lockfile, entry) -> Lockfile:
    """Replace any entry with the same ``(skill_ref, scope)`` and add ``entry``;
    serialization re-canonicalizes the order (13 SC-001), so this stays byte-stable."""
    kept = tuple(
        e
        for e in lockfile.entries
        if not (e.skill_ref == entry.skill_ref and e.scope == entry.scope)
    )
    return Lockfile(version=lockfile.version, entries=kept + (entry,))


@skills_app.command()
def install(
    ref: Optional[str] = typer.Argument(
        None, help="Skill ref: GitHub/GitLab URL, alias, or local path. Omit with --frozen to reproduce all."
    ),
    frozen: bool = typer.Option(
        False, "--frozen", help="Reproduce from the lockfile with no network resolution (13 P2)."
    ),
    global_scope: bool = typer.Option(
        False, "--global", "-g", help="Install into the global agent dir (default: project)."
    ),
    copy: bool = typer.Option(
        False, "--copy", help="Copy instead of symlink (systems without symlink support, 13 FR-005)."
    ),
    source: Optional[List[str]] = typer.Option(
        None, "--source", help="Restrict/order install sources (default: the canonical four)."
    ),
    lockfile: Optional[str] = typer.Option(
        None, "--lockfile", help=f"Lockfile path (default: ./{_DEFAULT_LOCKFILE})."
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Install a skill (plan + reasoning_trace + lockfile), or reproduce with --frozen."""
    scope = _scope_of(global_scope)
    lock_path = lockfile or _DEFAULT_LOCKFILE

    if frozen:
        _install_frozen(ref, lock_path, scope, json_output)
        return

    if not ref:
        typer.echo("[ERR] install needs a <ref> (or use --frozen to reproduce the lockfile).", err=True)
        raise typer.Exit(code=2)

    sources = tuple(source) if source else _DEFAULT_SOURCES
    strategy = "copy" if copy else "symlink"
    installer = CrossAgentInstaller(scope=scope, link_strategy=strategy)
    try:
        plan = installer.install(ref, sources)
        entry = installer.lock_entry(ref, sources)
    except SkillSourceUnavailableError as exc:  # 13 E1 -- lockfile left untouched
        typer.echo(f"[ERR] {exc}", err=True)
        raise typer.Exit(code=1) from None

    # Merge the entry into the lockfile (load existing if present, else fresh v3).
    try:
        existing = read_lockfile(lock_path)
    except FileNotFoundError:
        existing = Lockfile(version="v3", entries=())
    write_lockfile(lock_path, _merge_entry(existing, entry))

    trace = installer.reasoning_trace
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "skill_ref": plan.skill_ref,
                    "source": plan.source,
                    "resolved_sha": plan.resolved_sha,
                    "scope": plan.scope,
                    "target_dirs": list(plan.target_dirs),
                    "link_strategy": plan.link_strategy,
                    "artifact_sha256": entry.artifact_sha256,
                    "lockfile": lock_path,
                    "reasoning_trace": list(trace),
                },
                ensure_ascii=True,
            )
        )
        return
    typer.echo(f"[OK] planned {plan.skill_ref!r} from {plan.source} (sha {plan.resolved_sha[:12]})")
    typer.echo(f"     scope={plan.scope} strategy={plan.link_strategy} agent_dirs={len(plan.target_dirs)}")
    typer.echo(f"     lockfile -> {lock_path}")
    for line in trace:
        typer.echo(f"     reasoning_trace: {line}")


def _install_frozen(ref: Optional[str], lock_path: str, scope: str, json_output: bool) -> None:
    """``--frozen`` reproduction: resolve a ref (or every entry) against the lockfile
    with no network. SHA drift / absent ref HARD-FAIL (13 SC-002 / P2 #1)."""
    try:
        locked = read_lockfile(lock_path)
    except FileNotFoundError:
        typer.echo(f"[ERR] --frozen: no lockfile at {lock_path!r}.", err=True)
        raise typer.Exit(code=1) from None

    try:
        if ref:
            entries = [resolve_frozen(locked, ref, scope=scope)]
        else:
            entries = list(locked.entries)  # reproduce the whole lockfile
    except (FrozenLockViolationError, LockfileMismatchError) as exc:
        typer.echo(f"[ERR] {exc}", err=True)
        raise typer.Exit(code=1) from None

    if json_output:
        typer.echo(
            json.dumps(
                {
                    "frozen": True,
                    "lockfile": lock_path,
                    "resolved": [
                        {"skill_ref": e.skill_ref, "source": e.source,
                         "resolved_sha": e.resolved_sha, "scope": e.scope}
                        for e in entries
                    ],
                },
                ensure_ascii=True,
            )
        )
        return
    if not entries:
        typer.echo(f"[FROZEN] {lock_path}: 0 entries.")
        return
    for e in entries:
        typer.echo(f"[FROZEN] {e.skill_ref} <- {e.source} @ {e.resolved_sha[:12]} ({e.scope})")


@skills_app.command(name="list")
def list_skills(
    global_scope: bool = typer.Option(
        False, "--global", "-g", help="List only the global scope (default: both)."
    ),
    lockfile: Optional[str] = typer.Option(
        None, "--lockfile", help=f"Lockfile path (default: ./{_DEFAULT_LOCKFILE})."
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """List installed skills, project and global scopes separated (13 P3 #3)."""
    lock_path = lockfile or _DEFAULT_LOCKFILE
    try:
        locked = read_lockfile(lock_path)
    except FileNotFoundError:
        if json_output:
            typer.echo(json.dumps({"lockfile": lock_path, "project": [], "global": []}, ensure_ascii=True))
            return
        typer.echo(f"[NO_LOCKFILE] no skills.lock.v3 at {lock_path!r}.")
        return

    wanted = ("global",) if global_scope else ("project", "global")
    by_scope = {s: [e for e in locked.entries if e.scope == s] for s in wanted}

    if json_output:
        typer.echo(
            json.dumps(
                {
                    "lockfile": lock_path,
                    **{
                        s: [
                            {"skill_ref": e.skill_ref, "source": e.source, "resolved_sha": e.resolved_sha}
                            for e in entries
                        ]
                        for s, entries in by_scope.items()
                    },
                },
                ensure_ascii=True,
            )
        )
        return
    for s in wanted:
        entries = by_scope[s]
        typer.echo(f"== {s} ({len(entries)}) ==")
        for e in entries:
            typer.echo(f"  {e.skill_ref}  <- {e.source}  @ {e.resolved_sha[:12]}")


@skills_app.command()
def verify(
    name: str = typer.Argument(..., help="Skill name to verify."),
    runtime: Optional[List[str]] = typer.Option(
        None, "--runtime", help="Claimed runtime id (repeatable). No runtimes = exempt (V10-F2)."
    ),
    version: str = typer.Option("0.0.0", "--version", help="Skill version (manifest field)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """ADVISORY cross-runtime parity report (V10-F3 -- reports, never demotes/raises)."""
    skill = SkillManifest(
        name=name, version=version, runtime_compatibility=tuple(runtime or ())
    )
    report = CrossRuntimeVerifier().verify(skill)
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "skill_name": report.skill_name,
                    "runtimes": list(report.runtimes),
                    "parity": report.parity,
                    "failures": list(report.failures),
                },
                ensure_ascii=True,
            )
        )
        return
    verdict = "[OK]" if report.parity else "[CROSS_RUNTIME_FAIL]"
    typer.echo(f"{verdict} {report.skill_name}: parity={report.parity} runtimes={list(report.runtimes)}")
    if report.failures:
        typer.echo(f"     diverged: {list(report.failures)} (maintainer review requested -- not auto-demoted)")


@skills_app.command()
def publish(
    name: str = typer.Argument(..., help="Skill name to gate for publish."),
    kind: str = typer.Option("skill", "--kind", help="Frontmatter kind (validated against the registry)."),
    version: str = typer.Option("0.0.0", "--version", help="Skill version (manifest field)."),
    runtime: Optional[List[str]] = typer.Option(
        None, "--runtime", help="Claimed runtime id (repeatable)."
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """ENFORCING publish gate: refuse invalid frontmatter (10 SC-002) and a
    claiming-yet-failing cross-runtime skill (10 SC-003 / 13 SC-004)."""
    skill = SkillManifest(
        name=name,
        version=version,
        frontmatter={"kind": kind},
        runtime_compatibility=tuple(runtime or ()),
    )
    try:
        report = SkillPublishGate().gate(skill)
    except (SkillValidationError, CrossRuntimeParityError) as exc:
        typer.echo(f"[REFUSED] {exc}", err=True)
        raise typer.Exit(code=1) from None
    if json_output:
        typer.echo(
            json.dumps(
                {"published": True, "skill_name": report.skill_name, "parity": report.parity},
                ensure_ascii=True,
            )
        )
        return
    typer.echo(f"[OK] {name!r} passes the publish gate (parity={report.parity}).")


if __name__ == "__main__":  # pragma: no cover -- standalone runnability (mirrors mem_app).
    skills_app()
