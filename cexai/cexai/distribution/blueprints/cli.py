"""``blueprint`` CLI sub-app -- list / show / apply the four CEXAI stack blueprints.

A standalone ``typer.Typer`` mirroring the ``spec_kit_app`` / ``compliance_app``
discipline: a ``@callback`` keeps the subcommands explicit (so it is mount-ready under
``cexai blueprint`` via the foundation CLI's delegation), results go to stdout
(``--json`` for machine output), and diagnostics/errors go to stderr with a non-zero
exit (Article II). Offline (Article XIV): everything reads packaged data + a local
config; no network, no LLM.

  * ``list``  -- the four stacks + one-line summary + apply-able vs reference-only.
  * ``show``  -- 16/17: features + their open_vars + dependencies; 18: category
        counts + ATTRIBUTION pointer; 19: the provisioning lifecycle.
  * ``apply`` -- freeze 16/17 against a deployer config into
        ``<target>/.cexai/blueprints/<stack>/``; 18/19 error (reference/protocol).

absorbs: cexai-specs/16_company_stack + 17_saas_stack + 18_aitmpl_stack + 19_osb_stack
"""

from __future__ import annotations

import json
from typing import Any, Optional

import typer

from cexai.distribution.blueprints import catalog
from cexai.distribution.blueprints.freeze import BlueprintApplyError, apply_stack, load_config
from cexai.distribution.blueprints.loader import load_features

__all__ = ["blueprint_app", "EXIT_OK", "EXIT_ERROR", "EXIT_USAGE"]

# Exit codes (mirror the foundation + spec-kit CLIs: 0 ok, 1 error, 2 click usage).
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2

_MODE_TAG = {"apply": "APPLY", "reference": "REF", "protocol": "PROTO"}

blueprint_app = typer.Typer(
    add_completion=False,
    help=(
        "Stack blueprints: list / show / apply the four CEXAI verticals. "
        "company_stack + saas_stack are apply-able (open_vars frozen against a "
        "brand_config); aitmpl_stack (reference) + osb_stack (protocol) are show-only. "
        "Offline."
    ),
)


@blueprint_app.callback()
def _blueprint_root() -> None:
    """Stack-blueprint tooling. The callback keeps the subcommands explicit so this
    app is mount-ready under ``cexai blueprint`` (it would otherwise collapse to a
    single bare command)."""


# --------------------------------------------------------------------------- #
# list                                                                          #
# --------------------------------------------------------------------------- #
@blueprint_app.command(name="list")
def list_(
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """List the four stack blueprints with their apply-able vs reference-only flag.

    Dependency-free (no template parsing), so it runs with or without PyYAML."""
    rows = []
    for stack_id in catalog.STACK_IDS:
        info = catalog.get_stack(stack_id)
        row: dict[str, Any] = {
            "stack_id": info.stack_id,
            "vertical": info.vertical,
            "title": info.title,
            "mode": info.mode,
            "applyable": info.applyable,
            "summary": info.summary,
        }
        if info.applyable:
            row["feature_count"] = _safe_feature_count(stack_id)
        rows.append(row)

    if json_output:
        typer.echo(json.dumps({"stacks": rows}, ensure_ascii=True, sort_keys=True))
        return
    for row in rows:
        tag = _MODE_TAG.get(str(row["mode"]), str(row["mode"]).upper())
        count = f" ({row['feature_count']} features)" if "feature_count" in row else ""
        typer.echo(f"{row['stack_id']:<16} [{tag}]{count}")
        typer.echo(f"    {row['summary']}")


# --------------------------------------------------------------------------- #
# show                                                                          #
# --------------------------------------------------------------------------- #
@blueprint_app.command()
def show(
    stack: str = typer.Argument(..., help="Stack id (company_stack|saas_stack|aitmpl_stack|osb_stack)."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Describe STACK. Apply-able stacks list features + open_vars + dependencies;
    aitmpl_stack lists category counts + the ATTRIBUTION pointer; osb_stack lists the
    provisioning lifecycle. An unknown stack id is a usage error (stderr, exit 2)."""
    try:
        info = catalog.get_stack(stack)
    except KeyError as exc:
        typer.echo(f"[ERR] {exc}", err=True)
        raise typer.Exit(code=EXIT_USAGE) from None

    if info.applyable:
        try:
            payload = _show_applyable(info)
        except Exception as exc:  # noqa: BLE001 -- a malformed packaged template is a clean CLI error
            typer.echo(f"[ERR] {type(exc).__name__}: {exc}", err=True)
            raise typer.Exit(code=EXIT_ERROR) from None
    else:
        payload = _show_reference(info)

    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=True, sort_keys=True))
        return
    typer.echo(_render_show(info, payload))


def _show_applyable(info: catalog.StackInfo) -> dict[str, Any]:
    features = load_features(info.stack_id)
    feature_rows = [
        {
            "feature_name": f.feature_name,
            "pillars": list(f.pillars),
            "feature_dependencies": list(f.feature_dependencies),
            "open_vars": [ov.name for ov in f.open_vars],
        }
        for f in features
    ]
    payload: dict[str, Any] = {
        "stack_id": info.stack_id,
        "title": info.title,
        "mode": info.mode,
        "applyable": True,
        "feature_count": len(feature_rows),
        "features": feature_rows,
    }
    if info.stack_id == "saas_stack":
        payload["inherits_from"] = info.detail.get("inherits_from")
        payload["inherit_manifest"] = info.detail.get("inherit_manifest")
    return payload


def _show_reference(info: catalog.StackInfo) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "stack_id": info.stack_id,
        "title": info.title,
        "mode": info.mode,
        "applyable": False,
        "specs_path": info.specs_path,
    }
    if info.stack_id == "osb_stack":
        payload["lifecycle"] = [
            {"phase": phase, "description": desc} for phase, desc in info.detail["lifecycle"]
        ]
        payload["artifact"] = info.detail["artifact"]
        payload["reuses_kinds"] = list(info.detail["reuses_kinds"])
        payload["reason_not_applyable"] = info.detail["reason_not_applyable"]
    else:  # aitmpl_stack
        payload["total_unique_items"] = info.detail["total_unique_items"]
        payload["counts_are_approximate"] = info.detail["counts_are_approximate"]
        payload["categories"] = dict(info.detail["categories"])
        payload["attribution"] = info.detail["attribution"]
        payload["source_repo"] = info.detail["source_repo"]
        payload["reason_not_applyable"] = info.detail["reason_not_applyable"]
    return payload


def _render_show(info: catalog.StackInfo, payload: dict[str, Any]) -> str:
    lines = [f"{info.title} ({info.vertical}) [{_MODE_TAG.get(info.mode, info.mode)}]", info.summary, ""]
    if info.applyable:
        lines.append(f"{payload['feature_count']} feature template(s):")
        for f in payload["features"]:
            deps = f", depends_on={f['feature_dependencies']}" if f["feature_dependencies"] else ""
            lines.append(f"  - {f['feature_name']}: open_vars={f['open_vars']}{deps}")
        if info.stack_id == "saas_stack":
            lines.append("")
            lines.append(f"Inherits company_stack features via {payload['inherit_manifest']}")
        lines.append("")
        lines.append(f"Apply: cexai blueprint apply {info.stack_id} --target <dir> --config brand_config.yaml")
    elif info.stack_id == "osb_stack":
        lines.append("Provisioning lifecycle:")
        for step in payload["lifecycle"]:
            lines.append(f"  {step['phase']:<12} {step['description']}")
        lines.append("")
        lines.append(f"Artifact: {payload['artifact']} (reuses {', '.join(payload['reuses_kinds'])})")
        lines.append(f"NOT apply-able: {payload['reason_not_applyable']}")
    else:  # aitmpl_stack
        approx = "~" if payload["counts_are_approximate"] else ""
        lines.append(f"{payload['total_unique_items']} unique items ({payload['source_repo']}):")
        for category, count in payload["categories"].items():
            lines.append(f"  {category:<12} {approx}{count}")
        lines.append("")
        lines.append(f"Attribution: {payload['attribution']}")
        lines.append(f"NOT apply-able: {payload['reason_not_applyable']}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# apply                                                                         #
# --------------------------------------------------------------------------- #
@blueprint_app.command()
def apply(
    stack: str = typer.Argument(..., help="Stack id to apply (company_stack|saas_stack)."),
    target: str = typer.Option(..., "--target", help="Deployer dir; frozen artifacts land in <target>/.cexai/blueprints/<stack>/."),
    config: Optional[str] = typer.Option(None, "--config", help="brand_config .yaml/.yml/.json with open_var values."),
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
) -> None:
    """Freeze STACK's feature templates against a deployer config.

    Resolves each open_var from the config, validates it, and writes frozen artifacts
    (``_open_vars_frozen: true``) to ``<target>/.cexai/blueprints/<stack>/``. Only
    company_stack + saas_stack are apply-able; aitmpl_stack/osb_stack error clearly
    (exit 1). Unresolved required vars abort with a listing and write nothing."""
    try:
        info = catalog.get_stack(stack)
    except KeyError as exc:
        typer.echo(f"[ERR] {exc}", err=True)
        raise typer.Exit(code=EXIT_USAGE) from None

    if not info.applyable:
        typer.echo(
            f"[ERR] {stack} is not apply-able ({info.mode}-only): "
            f"{info.detail.get('reason_not_applyable', 'see cexai blueprint show ' + stack)}",
            err=True,
        )
        raise typer.Exit(code=EXIT_ERROR) from None

    try:
        cfg = load_config(config) if config else {}
    except (OSError, ValueError, RuntimeError) as exc:
        typer.echo(f"[ERR] {type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(code=EXIT_ERROR) from None

    try:
        result = apply_stack(stack, target, cfg)
    except BlueprintApplyError as exc:
        if json_output:
            typer.echo(
                json.dumps(
                    {
                        "stack_id": stack,
                        "applied": False,
                        "missing": [
                            {"feature": feat, "name": m.name, "reason": m.reason, "looked_for": list(m.looked_for)}
                            for feat, m in exc.missing
                        ],
                    },
                    ensure_ascii=True,
                    sort_keys=True,
                ),
                err=True,
            )
        else:
            typer.echo(f"[ERR] {exc}", err=True)
        raise typer.Exit(code=EXIT_ERROR) from None
    except Exception as exc:  # noqa: BLE001 -- surface any freeze failure as a clean CLI error
        typer.echo(f"[ERR] {type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(code=EXIT_ERROR) from None

    rel = [str(p) for p in result.written]
    # Malformed features (upstream template bugs) are skipped, never frozen; surface
    # them loudly on stderr so the finding is not lost, but do not fail the apply.
    if result.skipped_malformed:
        typer.echo(
            f"[WARN] skipped {len(result.skipped_malformed)} malformed feature(s) "
            f"(upstream open_var bug): {', '.join(result.skipped_malformed)}",
            err=True,
        )
        for feat, var, err in result.malformed_detail:
            typer.echo(f"[WARN]   {feat}.{var}: {err}", err=True)
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "stack_id": stack,
                    "applied": True,
                    "count": len(rel),
                    "written": rel,
                    "skipped_malformed": list(result.skipped_malformed),
                },
                ensure_ascii=True,
                sort_keys=True,
            )
        )
        return
    typer.echo(f"[OK] froze {len(rel)} artifact(s) for {stack}:")
    for path in rel:
        typer.echo(f"  {path}")


def _safe_feature_count(stack_id: str) -> int:
    """Filesystem feature count; never raises into ``list`` (returns -1 on error)."""
    try:
        from cexai.distribution.blueprints.loader import feature_count

        return feature_count(stack_id)
    except Exception:  # noqa: BLE001 -- list must stay robust + dependency-free
        return -1


if __name__ == "__main__":  # pragma: no cover -- standalone runnability (mirrors spec_kit).
    blueprint_app()
