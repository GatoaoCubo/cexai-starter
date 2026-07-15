"""Load packaged stack-blueprint feature templates (vertical 16/17) from package data.

A blueprint feature template is a markdown file with a YAML frontmatter block (the
``feature_template`` shape: ``feature_name`` + ``pillars`` + ``feature_dependencies``
+ ``open_vars`` per Article XIX) and a spec body. They are MIRRORED into this
package's ``data/{company_stack,saas_stack}/`` from ``cexai-specs/16|17/templates/``
so the wheel is self-contained -- the loader reads them through
``importlib.resources`` (works from a source tree, an editable install, or a built
wheel).

YAML is parsed with PyYAML, imported LAZILY (the ``open_vars.registry`` precedent):
it is a transitive repo dependency, NOT a hard ``cexai`` dependency, so a clean
install without it still imports this module -- only the parsing entry points raise
a clear error. ``feature_count`` and file discovery stay dependency-free (filesystem
only), so ``cexai blueprint list`` works with or without PyYAML.

The parsed ``OpenVar`` declarations are produced by the foundation
``parse_open_var`` (REUSED, not reimplemented): a malformed declaration raises the
governed open_vars error rather than being silently accepted.

absorbs: cexai-specs/16_company_stack + 17_saas_stack (templates)
"""

from __future__ import annotations

import importlib.resources as _resources
from dataclasses import dataclass
from typing import Any

from cexai.foundation.open_vars import OpenVar, OpenVarError, parse_open_var

__all__ = [
    "FeatureTemplate",
    "MalformedDecl",
    "TEMPLATE_STACKS",
    "load_features",
    "feature_count",
    "feature_names",
    "split_frontmatter",
]

# The two apply-able, template-based stacks packaged as data. 18 (reference catalog)
# and 19 (protocol) are intentionally NOT here -- 18 is never packaged, 19 ships as a
# single protocol artifact addressed directly by the catalog.
TEMPLATE_STACKS: tuple[str, ...] = ("company_stack", "saas_stack")

_DATA_PACKAGE = "cexai.distribution.blueprints"
_DATA_DIRNAME = "data"
_YAML_IMPORT_ERROR: Exception | None = None
try:  # PyYAML is a transitive repo dep; frontmatter parsing is too structured to guess.
    import yaml as _yaml
except Exception as exc:  # pragma: no cover - exercised only in a yaml-less install
    _yaml = None  # type: ignore[assignment]
    _YAML_IMPORT_ERROR = exc


@dataclass(frozen=True, slots=True)
class MalformedDecl:
    """A raw open_var declaration that failed ``parse_open_var`` (an upstream
    template bug, surfaced not swallowed). ``name`` + ``type_str`` echo the raw
    declaration; ``error`` is the governed open_vars message."""

    name: str
    type_str: str
    error: str


@dataclass(frozen=True, slots=True)
class FeatureTemplate:
    """One parsed blueprint feature template (the in-memory shape of a packaged
    ``feature_*.md``). ``feature_name`` is the template id within its stack;
    ``stack_id`` is the owning stack; ``pillars`` are the declared CEX pillars;
    ``feature_dependencies`` are the other feature names this one depends on;
    ``open_vars`` is the tuple of successfully parsed, validated ``OpenVar``
    declarations (the Article XIX slots); ``malformed`` is the tuple of declarations
    that FAILED to parse (an upstream bug -- the feature is then not freezable);
    ``raw_open_vars`` is the original declaration dicts (preserved verbatim so a
    freeze re-emits them per ADR 022 FR-014); ``frontmatter`` is the full parsed
    frontmatter; ``body`` is the markdown spec body; ``source_filename`` is the data
    file it loaded from. A feature is freezable iff ``malformed`` is empty."""

    feature_name: str
    stack_id: str
    pillars: tuple[str, ...]
    feature_dependencies: tuple[str, ...]
    open_vars: tuple[OpenVar, ...]
    malformed: tuple[MalformedDecl, ...]
    raw_open_vars: tuple[dict[str, Any], ...]
    frontmatter: dict[str, Any]
    body: str
    source_filename: str

    @property
    def is_freezable(self) -> bool:
        """True iff every declared open_var parsed cleanly (no upstream bug)."""
        return not self.malformed

    @property
    def declared_count(self) -> int:
        """Number of open_vars DECLARED (raw), valid or not -- the Article XIX min-4
        count is over declarations, independent of parse success."""
        return len(self.raw_open_vars)


def _require_yaml() -> Any:
    if _yaml is None:  # pragma: no cover - exercised only in a yaml-less install
        raise RuntimeError(
            "PyYAML is required to parse blueprint feature templates: "
            f"{_YAML_IMPORT_ERROR}. Install it with `pip install pyyaml`."
        )
    return _yaml


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a ``---``-fenced YAML frontmatter block from the markdown body.

    Returns ``(frontmatter_dict, body)``. A file with no leading ``---`` fence has
    an empty frontmatter and the whole text as body. Raises ``ValueError`` for an
    unterminated fence (a malformed template -- report it, do not guess).
    """
    if not text.startswith("---"):
        return {}, text
    # Strip a leading line that is exactly the opening fence.
    lines = text.splitlines(keepends=True)
    if lines[0].rstrip("\r\n") != "---":
        return {}, text
    closing_index: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\r\n") == "---":
            closing_index = idx
            break
    if closing_index is None:
        raise ValueError("frontmatter fence opened with '---' but never closed")
    fm_text = "".join(lines[1:closing_index])
    body = "".join(lines[closing_index + 1 :])
    loaded = _require_yaml().safe_load(fm_text) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"frontmatter must be a mapping, got {type(loaded).__name__}")
    return loaded, body


def _stack_dir(stack_id: str):
    """Return the importlib.resources Traversable for a packaged stack's data dir."""
    if stack_id not in TEMPLATE_STACKS:
        raise KeyError(f"{stack_id!r} is not a packaged template stack {TEMPLATE_STACKS}")
    return _resources.files(_DATA_PACKAGE).joinpath(_DATA_DIRNAME, stack_id)


def _iter_feature_paths(stack_id: str) -> list[Any]:
    """Sorted list of ``feature_*.md`` Traversables in a stack's data dir (no parse)."""
    root = _stack_dir(stack_id)
    paths = [
        child
        for child in root.iterdir()
        if child.name.startswith("feature_") and child.name.endswith(".md")
    ]
    return sorted(paths, key=lambda p: p.name)


def feature_count(stack_id: str) -> int:
    """Number of feature templates packaged for ``stack_id`` -- filesystem only, so
    it works without PyYAML (backs the dependency-free ``blueprint list``)."""
    return len(_iter_feature_paths(stack_id))


def _parse_feature(stack_id: str, name: str, text: str) -> FeatureTemplate:
    frontmatter, body = split_frontmatter(text)
    raw_open_vars = list(frontmatter.get("open_vars") or [])
    parsed: list[OpenVar] = []
    malformed: list[MalformedDecl] = []
    for decl in raw_open_vars:
        try:
            parsed.append(parse_open_var(decl))
        except OpenVarError as exc:
            # Surface the upstream template bug as a diagnostic; do NOT crash the
            # load and do NOT mutate the source (handoff: report, don't silently fix).
            malformed.append(
                MalformedDecl(
                    name=str(decl.get("name", "<unnamed>")),
                    type_str=str(decl.get("type", "<untyped>")),
                    error=str(exc),
                )
            )
    feature_name = str(frontmatter.get("feature_name") or name[len("feature_") : -len(".md")])
    pillars = tuple(str(p) for p in (frontmatter.get("pillars") or []))
    deps = tuple(str(d) for d in (frontmatter.get("feature_dependencies") or []))
    return FeatureTemplate(
        feature_name=feature_name,
        stack_id=stack_id,
        pillars=pillars,
        feature_dependencies=deps,
        open_vars=tuple(parsed),
        malformed=tuple(malformed),
        raw_open_vars=tuple(dict(d) for d in raw_open_vars),
        frontmatter=frontmatter,
        body=body,
        source_filename=name,
    )


def load_features(stack_id: str) -> tuple[FeatureTemplate, ...]:
    """Parse every packaged feature template for ``stack_id`` (sorted by filename).

    Does NOT raise on a malformed open_var declaration (R-229 -- this corrects an
    earlier docstring that claimed it did; ``_parse_feature`` has always collected,
    never raised). A packaged blueprint that does not satisfy Article XIX is an
    upstream template bug, surfaced not swallowed: each malformed declaration is
    reported on its ``FeatureTemplate.malformed`` tuple (``MalformedDecl`` -- name,
    type_str, the governed ``OpenVarError`` message), and the whole feature is then
    not freezable (``FeatureTemplate.is_freezable`` is ``False``). This is the
    contract ``apply_stack`` (``freeze.py``) actually relies on: it partitions
    ``load_features``'s result into freezable vs. ``skipped_malformed`` and reports
    both, rather than the whole stack aborting on one bad template. Only a
    structurally broken file (an unterminated frontmatter fence) raises
    ``ValueError`` here, via ``split_frontmatter``.
    """
    out: list[FeatureTemplate] = []
    for path in _iter_feature_paths(stack_id):
        text = path.read_text(encoding="utf-8")
        out.append(_parse_feature(stack_id, path.name, text))
    return tuple(out)


def feature_names(stack_id: str) -> tuple[str, ...]:
    """The feature_name set for a packaged stack (used to resolve dependencies)."""
    return tuple(f.feature_name for f in load_features(stack_id))
