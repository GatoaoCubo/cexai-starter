"""``topology`` CLI sub-app -- audit a topology run's coordination + span trace.

A standalone ``typer.Typer`` named ``topology_app`` exposing
``topology audit <run_id> [--json] [--root DIR]``. It reconstructs the audit trace
for a traced run (see ``cexai.orchestration.topology.audit.reconstruct``) and prints
it: pretty JSON by default, compact machine JSON with ``--json``. Only the result
goes to stdout; errors go to stderr with a non-zero exit (Article II).

Mount status (per the W3c handoff's "mount it; else keep import-clean + note which"):
NOT mounted under the main ``cexai`` CLI in this wave. The ``cexai`` entry
(``cexai.foundation.invocation.cli``) is a SINGLE bare command -- ``add_typer`` would
turn it into a click group and break the ``cexai <feature>`` invocation -- so it
mounts sub-apps as explicit DELEGATIONS inside its ``main`` (the ``mem`` precedent).
Adding a ``topology`` delegation there is a one-line foundation-lane edit, OUT OF
SCOPE for this operations cell (foundation is frozen for N05 here). Until that lands,
this app is import-clean and independently runnable:

    python -m cexai.orchestration.topology.cli audit <run_id> [--json] [--root DIR]

The ``@topology_app.callback()`` keeps ``audit`` an explicit subcommand (the app does
not collapse to a bare command), so it is ready to mount under ``cexai topology``
verbatim once the foundation delegation is added.

absorbs: 05_agno/governance-integration + 03_swarms/audit
"""

from __future__ import annotations

import json
import re

import typer

from cexai.orchestration.topology.audit import reconstruct

__all__ = ["topology_app", "main"]

# Exit codes: 0 ok, 1 audit error (no trace / phantom input). Mirrors the
# foundation CLI's EXIT_OK / EXIT_FEATURE_ERROR; 2 stays click's usage code.
EXIT_OK = 0
EXIT_AUDIT_ERROR = 1

# R-242: ``audit.reconstruct`` joins ``run_id`` straight into a filesystem path
# (``{root}/.cexai/topology/runs/{run_id}.json``) with no shape check -- a
# ``run_id`` containing ``../`` segments (or an absolute/drive path, which a
# plain ``Path.__truediv__`` join silently accepts and lets override ``root``
# entirely) escapes the intended audit dir and can read + dump an arbitrary
# JSON file to stdout. ``run_id`` must be a bounded token: letters, digits,
# ``_``/``-``/``.`` only. This is input-shape validation on the CLI boundary,
# not a change to the audit trust model.
_RUN_ID_SHAPE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _validate_run_id_shape(run_id: str) -> str:
    """Typer Argument callback: reject any ``run_id`` that is not a bounded
    allowlisted token before it ever reaches the ``audit.reconstruct`` path
    join. Rejects path separators, drive/UNC prefixes, and ``..`` traversal
    segments (SC- / R-242)."""
    if not run_id or not _RUN_ID_SHAPE.fullmatch(run_id) or ".." in run_id:
        raise typer.BadParameter(
            "run_id must be a bounded token: letters, digits, '_', '-', '.' "
            "only -- no path separators or '..' segments",
            param_hint="RUN_ID",
        )
    return run_id


topology_app = typer.Typer(
    add_completion=False,
    help="Topology audit: reconstruct a traced run's coordination + span trace.",
)


@topology_app.callback()
def _root() -> None:
    """Topology coordination tooling. The callback keeps ``audit`` an explicit
    subcommand so this app is mount-ready under ``cexai topology`` (it would
    otherwise collapse to a bare single command)."""


@topology_app.command()
def audit(
    run_id: str = typer.Argument(
        ...,
        help="The run_id of a traced TopologyRun.",
        callback=_validate_run_id_shape,
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit compact machine-readable JSON."),
    root: str = typer.Option(".", "--root", help="Root dir holding .cexai/ (default: current dir)."),
) -> None:
    """Reconstruct + print the audit trace for RUN_ID.

    Joins the persisted TopologyRun events + span tree (and any graceful-degrade
    buffered spans) and certifies the zero-phantom-input invariant. Pretty JSON on
    stdout by default; compact JSON with ``--json``. Exits 1 with a stderr
    diagnostic when no trace exists or the trail fails the invariant."""
    try:
        trace = reconstruct(run_id, root_dir=root)
    except Exception as exc:  # noqa: BLE001 -- surface any audit failure as a clean CLI error
        typer.echo(f"{type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(code=EXIT_AUDIT_ERROR) from None
    typer.echo(json.dumps(trace, ensure_ascii=True, indent=None if json_output else 2))


def main() -> None:
    """Console entry point: run the topology sub-app standalone."""
    topology_app()


if __name__ == "__main__":
    main()
