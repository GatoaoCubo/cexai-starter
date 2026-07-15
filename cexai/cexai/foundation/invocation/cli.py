"""Typer CLI -- the command-line half of dual invocation (W3).

``cexai <feature> [args...] [--json]`` resolves ``feature`` in the library
registry, calls it through ``run_feature`` (the SAME path the library API uses),
and renders the result: human text by default, machine JSON with ``--json``.
Only the result goes to stdout; diagnostics and errors go to stderr (Article II).

This module is a SINGLE typer command with NO callback, so typer exposes it as a
bare command and the console-script ``cexai`` (declared in pyproject.toml) needs
no subcommand name. Exit codes follow the table below; 2 is reserved by click for
usage errors (e.g. a missing FEATURE argument).

absorbs: 08_goose/dual-invocation
"""

from __future__ import annotations

import importlib
import logging
from typing import List, Optional

import typer

from cexai.foundation.invocation.json_io import to_json, to_text
from cexai.foundation.invocation.library import UnknownFeatureError, run_feature

__all__ = ["app", "EXIT_OK", "EXIT_FEATURE_ERROR", "EXIT_UNKNOWN_FEATURE"]

# Feature-specific exit-code table (spec P3 acceptance #3). 2 is click's usage code.
EXIT_OK = 0
EXIT_FEATURE_ERROR = 1
EXIT_UNKNOWN_FEATURE = 3

_logger = logging.getLogger("cexai.foundation.invocation.cli")

app = typer.Typer(
    add_completion=False,
    help=(
        "Invoke any CEXAI feature: cexai <feature> [args] [--json]. "
        "Reserved sub-app: cexai mem <search|forget|audit> (episodic memory, v0.2)."
    ),
)

# Reserved feature name routed to the episodic mem sub-app (see main()).
_MEM_FEATURE = "mem"

# Reserved feature names routed to standalone sub-apps that carry their OWN flags
# (e.g. spec-kit/compliance own --json + own exit codes; blueprint owns --target /
# --config). Like ``mem``, each is a DELEGATION, not an ``add_typer`` mount: add_typer
# would turn this single bare command into a click group and break the
# ``cexai <feature>`` invocation SC-003 parity depends on. The delegation forwards the
# trailing args verbatim (+ ``--json`` when set), so a sub-app's own options reach it
# unparsed -- this is why ``main`` sets ``ignore_unknown_options`` below: an unknown
# option (``--target``) is collected into ``args`` instead of erroring at the foundation
# layer, then handed to the sub-app. A non-delegated feature keeps receiving its args
# as before. value = (module path, Typer attribute name); imported lazily on first use.
_DELEGATED_SUBAPPS: dict[str, tuple[str, str]] = {
    "spec-kit": ("cexai.distribution.spec_kit.cli", "spec_kit_app"),
    "compliance": ("cexai.distribution.spec_kit.cli", "compliance_app"),
    "blueprint": ("cexai.distribution.blueprints.cli", "blueprint_app"),
    "skills": ("cexai.distribution.skills.cli", "skills_app"),
    "topology": ("cexai.orchestration.topology.cli", "topology_app"),
}


# ignore_unknown_options: unknown ``--opts`` (a delegated sub-app's own flags, e.g.
# blueprint's --target/--config) are collected into the variadic ``args`` rather than
# rejected here, so they can be forwarded to the sub-app. Declared options (--json)
# are still parsed by this command; positional handling is unchanged.
@app.command(context_settings={"ignore_unknown_options": True})
def main(
    feature: str = typer.Argument(..., help="Registered feature name (or 'mem' for the episodic sub-app)."),
    args: Optional[List[str]] = typer.Argument(None, help="Positional string args for the feature."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON on stdout."),
) -> None:
    """Run FEATURE with ARGS. Human text on stdout by default; JSON with --json.

    Errors go to stderr and set a non-zero exit code; stdout stays empty on error
    so a downstream consumer never mistakes a diagnostic for a result.

    The reserved feature name ``mem`` is delegated to the episodic ``mem_app``
    (``cexai mem search|forget|audit``). It is wired as a DELEGATION rather than a
    typer sub-app on purpose: ``add_typer`` would turn this single bare command
    into a click group and break the ``cexai <feature>`` invocation that SC-003
    parity depends on (typer has no "default command + subcommands"). Every other
    feature name flows through the unchanged ``run_feature`` path below."""
    if feature == _MEM_FEATURE:
        mem_argv = list(args or [])
        if json_output:
            mem_argv.append("--json")
        try:
            from cexai.memory.episodic import mem_app  # lazy: only when `mem` is invoked
        except Exception as exc:  # noqa: BLE001 -- surface as a clean CLI error, not a traceback
            typer.echo(f"{type(exc).__name__}: {exc}", err=True)
            raise typer.Exit(code=EXIT_FEATURE_ERROR) from None
        # standalone_mode=True (default): mem_app owns its own exit codes.
        mem_app(args=mem_argv, prog_name="cexai mem")
        return
    if feature in _DELEGATED_SUBAPPS:
        module_name, app_name = _DELEGATED_SUBAPPS[feature]
        sub_argv = list(args or [])
        if json_output:
            sub_argv.append("--json")
        try:
            sub_app = getattr(importlib.import_module(module_name), app_name)
        except Exception as exc:  # noqa: BLE001 -- surface as a clean CLI error, not a traceback
            typer.echo(f"{type(exc).__name__}: {exc}", err=True)
            raise typer.Exit(code=EXIT_FEATURE_ERROR) from None
        # standalone_mode=True (default): the sub-app owns its own exit codes.
        sub_app(args=sub_argv, prog_name=f"cexai {feature}")
        return
    # Activation keystone: import the shipped features so their register_feature
    # side effects populate the registry before we resolve `feature`. Done HERE
    # (lazy) -- not at module import -- so `mem` and the delegated sub-apps above
    # pay nothing. Best-effort: a single broken feature import must not mask the
    # clean UnknownFeatureError a real typo deserves, so we log and continue and
    # let run_feature surface the precise resolution result.
    try:
        import cexai.features  # noqa: F401 -- import side effects register features
    except Exception:  # noqa: BLE001 -- never let feature autoload crash the CLI
        _logger.warning("feature autoload failed", exc_info=True)
    call_args = list(args or [])
    _logger.info("invoking feature %r with %d arg(s), json=%s", feature, len(call_args), json_output)
    try:
        result = run_feature(feature, *call_args)
    except UnknownFeatureError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=EXIT_UNKNOWN_FEATURE) from None
    except Exception as exc:  # noqa: BLE001 -- surface ANY feature failure as a clean CLI error
        typer.echo(f"{type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(code=EXIT_FEATURE_ERROR) from None
    typer.echo(to_json(result) if json_output else to_text(result))
