"""``mem`` CLI sub-app -- search / forget / audit (07 FR-008/FR-015/FR-016).

A standalone ``typer.Typer`` named ``mem_app``. W3 mounts it under the main
``cexai`` CLI as ``cexai mem ...``; here it is import-clean and independently
runnable. Results go to stdout (``--json`` for machine output); the store reads
the default ``.cexai/memory`` root with the production embedder, degrading to a
substring scan when no embedding model is reachable.

absorbs: 07_claude-mem/episodic
"""

from __future__ import annotations

import json

import typer

from cexai.memory.episodic.store import EpisodicMemory

__all__ = ["mem_app"]

mem_app = typer.Typer(
    add_completion=False,
    help="Episodic memory: search prior sessions, forget a session, audit redaction.",
)


@mem_app.command()
def search(
    query: str = typer.Argument(..., help="Text to match against compressed sessions."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Search compressed sessions by relevance (FR-008). Best match first."""
    hits = EpisodicMemory().search(query)
    if json_output:
        typer.echo(
            json.dumps(
                [
                    {"session_id": cs.session_id, "narrative": cs.narrative}
                    for cs in hits
                ],
                ensure_ascii=True,
            )
        )
        return
    if not hits:
        typer.echo("[NO_MATCH] no compressed session matched the query.")
        return
    for cs in hits:
        typer.echo(f"{cs.session_id}: {cs.narrative}")


@mem_app.command()
def forget(
    session_id: str = typer.Argument(..., help="Session id to delete (raw + compressed)."),
) -> None:
    """Retroactively delete a session and every derivative (FR-015)."""
    EpisodicMemory().forget(session_id)
    typer.echo(f"[OK] forgot session {session_id!r} (raw log + compressed derivative).")


@mem_app.command()
def audit(
    target: str = typer.Argument("redaction", help="What to audit (currently: redaction)."),
) -> None:
    """Audit the redaction config against a test corpus (FR-016).

    v0.2-W2-stretch: full FR-009 redaction + the SC-007 1000-pattern corpus land
    in a later wave. This reports the current (empty) config honestly rather than
    half-implementing enforcement."""
    if target != "redaction":
        typer.echo(f"[ERR] unknown audit target {target!r}; supported: redaction", err=True)
        raise typer.Exit(code=2)
    typer.echo(
        "[v0.2-W2-stretch] redaction audit: 0 patterns configured. "
        "FR-009 redaction enforcement + the SC-007 long-tail PII corpus are deferred to a later wave."
    )
