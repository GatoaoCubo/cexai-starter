"""Resolve a blueprint's open_vars against a deployer config and FREEZE the result.

``apply`` is the executable half of the blueprint protocol: take a packaged feature
template (open slots declared per Article XIX), resolve each slot from the
deployer's ``brand_config``, validate the resolved value against its declaration,
and write a FROZEN artifact (``_open_vars_frozen: true`` + the ADR 022 FR-014
provenance fields) into ``<target>/.cexai/blueprints/<stack>/``.

Resolution is offline and deterministic (no GDP prompt, no network -- Article XIV):

  * walk the declaration's ``context_hints``; a ``brand_config.<dotted.key>`` hint is
    looked up in the config (first present, non-null hint wins);
  * else, for a NON-required var with a ``default_value``, use the default;
  * else the var is MISSING. A ``gdp_ask`` slot with no config value is simply
    missing here -- interactive filling is out of scope (handoff), so apply errors
    clearly and lists every missing var rather than prompting.

Every resolved value is validated through the foundation ``validate_open_var``
(REUSED, not reimplemented). Resolution is ALL-OR-NOTHING per stack: if any feature
has a missing-required or invalid value, ``apply_stack`` raises ``BlueprintApplyError``
and writes nothing -- a half-frozen target is never produced.

The template body is spec prose (it carries no ``{{placeholder}}`` markers), so the
freeze does not rewrite it; the parameterization is recorded in ``_filled_vars`` --
the auditable record ADR 022 FR-014 mandates.

absorbs: cexai-specs/16_company_stack + 17_saas_stack (apply) + ADR 022 (freeze)
"""

from __future__ import annotations

import datetime as _dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from cexai.foundation.open_vars import (
    PROTOCOL_VERSION,
    OpenVar,
    OpenVarError,
    validate_open_var,
)

from cexai.distribution.blueprints.loader import FeatureTemplate, load_features

__all__ = [
    "ResolvedVar",
    "MissingVar",
    "FrozenFeature",
    "ApplyResult",
    "BlueprintApplyError",
    "load_config",
    "resolve_feature",
    "freeze_feature_text",
    "apply_stack",
    "FROZEN_BY_DEFAULT",
]

FROZEN_BY_DEFAULT = "cexai-blueprint-apply"
_BRAND_CONFIG_PREFIX = "brand_config."


@dataclass(frozen=True, slots=True)
class ResolvedVar:
    """One successfully resolved open variable. ``name`` is the slot; ``value`` is
    the validated value; ``source`` records how it was filled (the winning
    ``context_hint:<key>`` or ``default_value``)."""

    name: str
    value: Any
    source: str


@dataclass(frozen=True, slots=True)
class MissingVar:
    """One open variable that could not be resolved. ``name`` + ``description`` echo
    the declaration; ``looked_for`` are the ``brand_config`` keys tried (in order);
    ``reason`` is ``unresolved`` (no hint/default) or ``invalid: <message>`` (a value
    was found but failed its declaration's validator)."""

    name: str
    description: str
    looked_for: tuple[str, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class FrozenFeature:
    """The freeze result for one feature: the ``feature_name``, the ordered tuple of
    ``ResolvedVar`` filled into it, and the frozen markdown ``text``."""

    feature_name: str
    resolved: tuple[ResolvedVar, ...]
    text: str


@dataclass(frozen=True, slots=True)
class ApplyResult:
    """The outcome of ``apply_stack``. ``written`` are the frozen artifact paths
    (sorted); ``skipped_malformed`` are feature names excluded because a declaration
    failed to parse (an upstream bug -- reported, never silently frozen);
    ``malformed_detail`` flattens those into ``(feature, var, error)`` for reporting.
    A successful apply never silently emits a broken artifact: malformed features are
    skipped + surfaced, while a deployer-side missing var aborts the whole apply."""

    stack_id: str
    written: tuple[Path, ...]
    skipped_malformed: tuple[str, ...] = ()
    malformed_detail: tuple[tuple[str, str, str], ...] = ()


class BlueprintApplyError(Exception):
    """Raised when a stack cannot be fully, validly frozen. ``missing`` aggregates
    every unresolved/invalid var across every feature so the caller can report them
    all at once; ``stack_id`` is the stack that failed."""

    def __init__(self, stack_id: str, missing: list[tuple[str, MissingVar]]) -> None:
        self.stack_id = stack_id
        self.missing = missing
        lines = [
            f"{feature}.{m.name}: {m.reason} (looked for: {', '.join(m.looked_for) or 'no brand_config hint'})"
            for feature, m in missing
        ]
        super().__init__(
            f"cannot apply {stack_id}: {len(missing)} unresolved open variable(s):\n  "
            + "\n  ".join(lines)
        )


# --------------------------------------------------------------------------- #
# Config loading                                                                #
# --------------------------------------------------------------------------- #
def load_config(path: str | Path) -> dict[str, Any]:
    """Load a deployer ``brand_config`` from ``.json`` (stdlib) or ``.yaml``/``.yml``
    (PyYAML, lazy). Returns a dict; a non-mapping document or an unknown extension is
    a ``ValueError``. JSON keeps the loader dependency-free for the common test path;
    YAML matches the spec's ``brand_config.yaml`` and is imported only when used."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    suffix = p.suffix.lower()
    if suffix == ".json":
        data = json.loads(text)
    elif suffix in (".yaml", ".yml"):
        try:
            import yaml  # lazy: not a hard dependency (Article VIII / XIV offline)
        except Exception as exc:  # pragma: no cover - yaml-less install
            raise RuntimeError(
                f"PyYAML is required to read {p.name}: {exc}. "
                "Install it with `pip install pyyaml`, or pass a .json config."
            ) from exc
        data = yaml.safe_load(text)
    else:
        raise ValueError(f"unsupported config extension {suffix!r} (use .yaml, .yml, or .json)")
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"config root must be a mapping, got {type(data).__name__}")
    return data


# --------------------------------------------------------------------------- #
# Resolution                                                                    #
# --------------------------------------------------------------------------- #
def _lookup_dotted(config: Mapping[str, Any], dotted_key: str) -> tuple[bool, Any]:
    """Resolve ``a.b.c`` against nested mappings. Returns ``(found, value)``; a value
    that resolves to ``None`` is treated as NOT found (an explicit null is no value)."""
    node: Any = config
    for part in dotted_key.split("."):
        if not isinstance(node, Mapping) or part not in node:
            return False, None
        node = node[part]
    if node is None:
        return False, None
    return True, node


def _resolve_one(decl: OpenVar, config: Mapping[str, Any]) -> tuple[ResolvedVar | None, MissingVar]:
    """Resolve a single declaration. Returns ``(ResolvedVar, _)`` on success or
    ``(None, MissingVar)`` on failure. The MissingVar is always built so the caller
    has the diagnostic even on success (it is ignored when the ResolvedVar is set)."""
    looked_for = tuple(
        h[len(_BRAND_CONFIG_PREFIX) :] for h in decl.context_hints if h.startswith(_BRAND_CONFIG_PREFIX)
    )
    candidate: Any = None
    winning_key: str | None = None
    for key in looked_for:
        found, value = _lookup_dotted(config, key)
        if found:
            candidate, winning_key = value, key
            break

    if winning_key is None:
        # No config hint resolved. A non-required var with a default fills from it.
        if not decl.required and decl.default_value is not None:
            return (
                ResolvedVar(name=decl.name, value=decl.default_value, source="default_value"),
                MissingVar(decl.name, decl.description, looked_for, "unresolved"),
            )
        return None, MissingVar(decl.name, decl.description, looked_for, "unresolved")

    try:
        validate_open_var(decl, candidate)
    except OpenVarError as exc:
        return None, MissingVar(
            decl.name, decl.description, looked_for, f"invalid: {exc}"
        )
    return (
        ResolvedVar(name=decl.name, value=candidate, source=f"context_hint:{winning_key}"),
        MissingVar(decl.name, decl.description, looked_for, "unresolved"),
    )


def resolve_feature(
    feature: FeatureTemplate, config: Mapping[str, Any]
) -> tuple[list[ResolvedVar], list[MissingVar]]:
    """Resolve every open var of ``feature`` against ``config``. Returns
    ``(resolved, missing)`` -- a feature is freezable iff ``missing`` is empty."""
    resolved: list[ResolvedVar] = []
    missing: list[MissingVar] = []
    for decl in feature.open_vars:
        rv, mv = _resolve_one(decl, config)
        if rv is None:
            missing.append(mv)
        else:
            resolved.append(rv)
    return resolved, missing


# --------------------------------------------------------------------------- #
# Freeze                                                                        #
# --------------------------------------------------------------------------- #
def _now_iso() -> str:
    """Timezone-aware ISO 8601 UTC timestamp (seconds precision)."""
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def freeze_feature_text(
    feature: FeatureTemplate,
    resolved: list[ResolvedVar],
    *,
    frozen_by: str = FROZEN_BY_DEFAULT,
    frozen_at: str | None = None,
) -> str:
    """Render the frozen markdown for ``feature``: original frontmatter (including the
    open_vars declarations, preserved per ADR 022 FR-014) + the freeze provenance
    block (``_open_vars_frozen`` / ``_frozen_at`` / ``_frozen_by`` /
    ``_protocol_version`` / ``_filled_vars``) + the unchanged body."""
    import yaml  # lazy: apply already requires yaml to have parsed the templates

    front: dict[str, Any] = dict(feature.frontmatter)
    # Preserve declarations; record the filled values + provenance (FR-014).
    front["_open_vars_frozen"] = True
    front["_frozen_at"] = frozen_at or _now_iso()
    front["_frozen_by"] = frozen_by
    front["_protocol_version"] = PROTOCOL_VERSION
    front["_filled_vars"] = {rv.name: rv.value for rv in resolved}
    dumped = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, default_flow_style=False)
    body = feature.body if feature.body.startswith("\n") else "\n" + feature.body
    return f"---\n{dumped}---{body}"


def apply_stack(
    stack_id: str,
    target: str | Path,
    config: Mapping[str, Any],
    *,
    frozen_by: str = FROZEN_BY_DEFAULT,
    frozen_at: str | None = None,
) -> ApplyResult:
    """Freeze a stack's feature templates into ``<target>/.cexai/blueprints/<stack>/``.

    Two distinct failure classes are handled differently:

      * a MALFORMED feature (an open_var declaration that does not parse -- an upstream
        template bug the deployer cannot fix) is SKIPPED and reported, never frozen;
      * a MISSING-required or INVALID var (a deployer-config problem the deployer CAN
        fix) aborts the WHOLE apply -- ``BlueprintApplyError`` is raised and nothing is
        written, so a half-frozen target is never produced.

    On success, writes one frozen ``<feature_name>.md`` per freezable feature and
    returns an ``ApplyResult`` (written paths + any skipped-malformed features).
    ``frozen_at`` is injectable for deterministic tests.
    """
    features = load_features(stack_id)
    freezable = [f for f in features if f.is_freezable]
    skipped = [f for f in features if not f.is_freezable]

    frozen: list[FrozenFeature] = []
    all_missing: list[tuple[str, MissingVar]] = []
    for feature in freezable:
        resolved, missing = resolve_feature(feature, config)
        if missing:
            all_missing.extend((feature.feature_name, m) for m in missing)
            continue
        text = freeze_feature_text(feature, resolved, frozen_by=frozen_by, frozen_at=frozen_at)
        frozen.append(FrozenFeature(feature.feature_name, tuple(resolved), text))

    if all_missing:
        raise BlueprintApplyError(stack_id, all_missing)

    out_dir = Path(target) / ".cexai" / "blueprints" / stack_id
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for ff in frozen:
        dest = out_dir / f"{ff.feature_name}.md"
        dest.write_text(ff.text, encoding="utf-8")
        written.append(dest)

    malformed_detail = tuple(
        (f.feature_name, m.name, m.error) for f in skipped for m in f.malformed
    )
    return ApplyResult(
        stack_id=stack_id,
        written=tuple(sorted(written, key=lambda p: p.name)),
        skipped_malformed=tuple(f.feature_name for f in skipped),
        malformed_detail=malformed_detail,
    )
