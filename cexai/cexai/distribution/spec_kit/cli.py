"""``spec-kit`` + ``compliance`` CLI sub-apps (cexai-specs/01_spec-kit + ADR 013).

Two standalone ``typer.Typer`` apps, mirroring the ``skills_app`` / ``topology_app``
discipline: import-clean, independently runnable, results to stdout (``--json`` for
machine output), diagnostics/errors to stderr with a non-zero exit (Article II).

  * ``spec_kit_app`` -- ``analyze`` (the cross-artifact checker, the core value) +
        the thin scaffolders ``init|spec|plan|tasks`` (emit a template to stdout or a
        path).
  * ``compliance_app`` -- ``check <article|all> [root] [--json]`` (the ADR 013 gate).

Both carry a ``@callback`` so their subcommands stay explicit (they do not collapse
to a bare command) -- mount-ready under ``cexai spec-kit`` / ``cexai compliance`` via
the foundation CLI's ``mem``-style delegation (wired in
``cexai.foundation.invocation.cli``). The delegation forwards positional args +
``--json`` only, so every command here works with positionals + ``--json`` (no other
flag is required on the delegated path).

Offline (Article XIV): no network, no LLM. Analyze reads local files; the scaffolders
emit in-memory ASCII; compliance inspects the local repo.

absorbs: 01_spec-kit + ADR 013
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from cexai.distribution.spec_kit import templates
from cexai.distribution.spec_kit.analyze import analyze_feature_dir
from cexai.distribution.spec_kit.compliance import check_all, check_article, normalize_article

__all__ = ["spec_kit_app", "compliance_app"]

# Exit codes (mirror the foundation CLI: 0 ok, 1 gate/feature error; 2 is click usage).
EXIT_OK = 0
EXIT_GATE_FAIL = 1
EXIT_USAGE = 2


# =========================================================================== #
# spec-kit sub-app                                                            #
# =========================================================================== #
spec_kit_app = typer.Typer(
    add_completion=False,
    help=(
        "Spec-kit tooling: analyze (cross-artifact consistency gate) + thin "
        "scaffolders init|spec|plan|tasks (emit a spec-kit template). Offline."
    ),
)


@spec_kit_app.callback()
def _spec_kit_root() -> None:
    """Spec-kit methodology tooling. The callback keeps the subcommands explicit so
    this app is mount-ready under ``cexai spec-kit`` (it would otherwise collapse to a
    single bare command)."""


@spec_kit_app.command()
def analyze(
    feature_dir: str = typer.Argument(..., help="Spec-kit feature dir (holds spec.md/plan.md/tasks.md)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Cross-artifact consistency check over FEATURE_DIR.

    Compares spec vs plan vs tasks and reports orphan requirements, unimplemented
    user stories, dangling task references, and unresolved clarification markers.
    Verdict PASS/CONDITIONAL exits 0; FAIL (any SEV-1/SEV-2 finding) exits 1 so CI
    can gate. The report is the RESULT (stdout); a bad path is an error (stderr)."""
    try:
        report = analyze_feature_dir(feature_dir)
    except FileNotFoundError as exc:
        typer.echo(f"[ERR] {exc}", err=True)
        raise typer.Exit(code=EXIT_GATE_FAIL) from None
    typer.echo(json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True) if json_output else report.render())
    if report.exit_code:
        raise typer.Exit(code=report.exit_code)


def _emit_template(name: str, target: Optional[str]) -> None:
    """Emit spec-kit template ``name`` to ``target`` (a path) or stdout. The shared
    body of the thin scaffolders; a write reports the path, stdout emits the body."""
    body = templates.emit(name)
    if target:
        out = Path(target)
        out.write_text(body, encoding="utf-8")
        typer.echo(f"[OK] wrote {name} template -> {out}")
        return
    typer.echo(body)


@spec_kit_app.command(name="init")
def init(
    target: Optional[str] = typer.Argument(None, help="Write path (default: stdout)."),
) -> None:
    """Emit the Constitution template (the project's governing-law scaffold)."""
    _emit_template("constitution", target)


@spec_kit_app.command()
def spec(
    target: Optional[str] = typer.Argument(None, help="Write path (default: stdout)."),
) -> None:
    """Emit the Spec template (User Stories P1/P2/P3 + FR-### + SC-###)."""
    _emit_template("spec", target)


@spec_kit_app.command()
def plan(
    target: Optional[str] = typer.Argument(None, help="Write path (default: stdout)."),
) -> None:
    """Emit the Plan template (Technical Context + Constitution Check)."""
    _emit_template("plan", target)


@spec_kit_app.command()
def tasks(
    target: Optional[str] = typer.Argument(None, help="Write path (default: stdout)."),
) -> None:
    """Emit the Tasks template ([T###] [P] [US#] phased, tests-first)."""
    _emit_template("tasks", target)


# =========================================================================== #
# compliance sub-app                                                          #
# =========================================================================== #
compliance_app = typer.Typer(
    add_completion=False,
    help=(
        "Constitution compliance (ADR 013): check <article|all> [root] [--json]. "
        "Automatable articles graded; the rest reported as manual/ci-only. Offline."
    ),
)


@compliance_app.callback()
def _compliance_root() -> None:
    """Per-article constitution compliance tooling (ADR 013). The callback keeps
    ``check`` an explicit subcommand so this app is mount-ready under
    ``cexai compliance``."""


@compliance_app.command()
def check(
    article: str = typer.Argument(..., help="Article id (I..XVII, 1..17, article-vii) or 'all'."),
    root: str = typer.Argument(".", help="Repo root to audit (default: current dir)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Run the ADR 013 compliance check for ARTICLE (or 'all') against ROOT.

    'all' prints the aggregate Article Compliance Report and ALWAYS exits 0 (report
    mode -- CI gates per-article or reads the JSON ``passed`` flag). A single article
    is a gate: it exits 1 when graded FAIL, 0 when PASS / MANUAL / CI-ONLY. An unknown
    article id is a usage error (stderr, exit 2)."""
    if article.strip().lower() == "all":
        report = check_all(root)
        typer.echo(
            json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True)
            if json_output
            else report.render()
        )
        raise typer.Exit(code=report.exit_code)

    try:
        normalize_article(article)  # validate early for a clean usage error
    except ValueError as exc:
        typer.echo(f"[ERR] {exc}", err=True)
        raise typer.Exit(code=EXIT_USAGE) from None

    result = check_article(article, root)
    if json_output:
        typer.echo(json.dumps(result.to_dict(), ensure_ascii=True, sort_keys=True))
    else:
        detail = f" -- {result.detail}" if result.detail else ""
        typer.echo(f"Article {result.article} {result.title}: {result.status}{detail}")
        for f in result.findings:
            typer.echo(f"  {f.severity_label} {f.code} ({f.artifact}): {f.message}")
    if result.exit_code:
        raise typer.Exit(code=result.exit_code)


if __name__ == "__main__":  # pragma: no cover -- standalone runnability (mirrors skills_app).
    spec_kit_app()
