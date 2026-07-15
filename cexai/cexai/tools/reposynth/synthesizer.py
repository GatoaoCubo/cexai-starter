"""GitReverseSynthesizer -- public repo -> deterministic reverse_prompt (14_gitreverse).

The concrete ``RepoSynthesizer`` (frozen seam in ``cexai.tools._shared.types``):
extract a public repo into a read-only ``RepoExtract`` (sorted file tree + README
+ <= 10 entry files, truncated at the 5,000-path budget), substitute the 3 open
vars into a fixed template, call the LLM through the foundation facade at
temperature 0.0, and project a deterministic ``ReversePrompt`` -- byte-identical
for a given ``(tree_sha, filled_vars)`` (FR-006 / SC-002).

LLM seam (important): the spec / W0 docstrings name
``cexai.foundation.invocation.router.dispatch(...)``, but that module is the dual
INVOCATION feature registry, not an LLM router -- it has no ``dispatch``. The real
provider-agnostic dispatch is ``cexai.foundation.llm.call(LlmRequest(...,
temperature=0.0), provider=...)`` (the same seam ``features.sentiment_classifier``
and the MoA executor use). We call that, and offline tests inject a fake provider
via ``cexai.foundation.llm.register_provider`` (the autouse
``_isolate_provider_registry`` fixture restores the registry per test). No live
LLM, no live git (Article XIV).

Repo extraction is an INJECTED ``RepoSource`` callable: tests pass a deterministic
offline fake; the unconfigured default fails closed (no fabricated repo data, no
untested live-network path shipped this wave). Determinism is structural: sorted
file paths, sorted entry files, a fixed template, temperature 0.0, and frontmatter
with NO wall-clock field.

License hygiene (Article XVII, fail-closed): an incompatible upstream LICENSE
aborts BEFORE the LLM call with ``LicenseCompatibilityError`` (E2 / SC-005); a
no-LICENSE target emits the non-fatal ``LicenseUnknownWarning`` and marks the
artifact ``derived_from_unlicensed_source: true`` (E3 / SC-006).

NOTE: the ``reverse_prompt`` KIND is registered by the N04 taxonomy cell, NOT
here -- this module only produces the runtime ``ReversePrompt`` projection and
writes its ``.md`` artifact.

absorbs: 14_gitreverse
"""

from __future__ import annotations

import logging
import os
import warnings
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from cexai.foundation._shared.types import LlmRequest, Message
from cexai.foundation.llm import call as _llm_call
from cexai.tools._shared.errors import (
    LicenseCompatibilityError,
    LicenseUnknownWarning,
    ReverseSynthError,
)
from cexai.tools._shared.types import (
    RepoExtract,
    ReversePrompt,
    TriangulationBriefFragment,
)
from cexai.tools.reposynth.license_gate import (
    check_license_compatibility,
    detect_license_spdx,
    has_license_file,
)

__all__ = [
    "GitReverseSynthesizer",
    "RepoSource",
    "synthesize_for_triangulation",
]

_LOG = logging.getLogger("cexai.tools.reposynth")

# A repo-extraction source: repo_url -> RepoExtract. The git / platform-API seam,
# injected so the synthesis pipeline is offline-testable (the default fails closed).
RepoSource = Callable[[str], RepoExtract]

# The 3 declared open vars (FR-005), in canonical order (frozen tuple = stable
# ordering for the projection + frontmatter, FR-006).
_OPEN_VARS: tuple[str, ...] = ("target_audience", "target_runtime", "complexity_level")
_DEFAULT_FILLERS: Mapping[str, str] = {
    "target_audience": "general software engineer",
    "target_runtime": "claude-code",
    "complexity_level": "intermediate",
}
_VALID_RUNTIMES: frozenset[str] = frozenset(("claude-code", "codex", "gemini", "ollama"))
_VALID_COMPLEXITY: frozenset[str] = frozenset(("introductory", "intermediate", "advanced"))

# E1 / SC-007 extraction budget and the <= 10 entry-file cap (FR-002).
_FILE_TREE_BUDGET = 5000
_MAX_ENTRY_FILES = 10

# Provider-neutral model id; live runs set CEXAI_MODEL, fakes ignore it.
_DEFAULT_MODEL = "default"
_DEFAULT_ARTIFACTS_ROOT = Path(".cex") / "runtime" / "artifacts" / "reverse_prompts"
_SYNTHESIS_NUCLEUS = "N03"
# ADR 022 wire-format protocol markers (FR-013).
_PROTOCOL = "cexai-open-vars"
_PROTOCOL_VERSION = "1.0"

_KNOWN_HOSTS: frozenset[str] = frozenset(("github.com", "gitlab.com", "bitbucket.org"))

# A tight, deterministic synthesis instruction. Temperature 0.0 + this fixed
# system prompt + a sorted extract = a reproducible body (FR-006).
_SYSTEM_PROMPT = (
    "You reconstruct software projects. Given a repository's metadata, file tree, "
    "README, and entry-point files, write a single self-contained prompt that "
    "instructs a downstream LLM to recreate an equivalent project. Calibrate the "
    "prompt to the declared target audience, target runtime, and complexity level. "
    "Output only the reconstruction prompt."
)


def _default_source(repo_url: str) -> RepoExtract:
    """The unconfigured extraction source: fail closed. The synthesis pipeline is
    offline-first -- a real git / platform-API extractor (or an offline fake in
    tests) is INJECTED via the constructor; we never fabricate repo data nor ship
    an untested live-network path here."""
    raise ReverseSynthError(
        repo_url,
        "no repo source configured; inject a RepoSource (offline fake in tests, "
        "or a platform-API extractor in production)",
    )


def _normalize_repo_url(repo_url: str) -> str:
    """Validate + canonicalize a repo reference (FR-001). Accepts
    ``https://{github|gitlab|bitbucket}.com/<o>/<r>`` and ``<owner>/<repo>``
    shorthand (defaults to GitHub). Returns ``https://<host>/<owner>/<repo>`` with
    any ``.git`` suffix and trailing slash stripped. Raises ``ReverseSynthError``
    on an unparseable reference."""
    raw = repo_url.strip()
    if not raw:
        raise ReverseSynthError(repo_url, "empty repository reference")

    host = "github.com"
    path = raw
    if "://" in raw:
        scheme, _, rest = raw.partition("://")
        host, _, path = rest.partition("/")
        host = host.lower()
        if host not in _KNOWN_HOSTS:
            raise ReverseSynthError(repo_url, f"unsupported host {host!r}")

    parts = [segment for segment in path.split("/") if segment]
    if len(parts) < 2:
        raise ReverseSynthError(repo_url, "expected <owner>/<repo>")
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[: -len(".git")]
    return f"https://{host}/{owner}/{repo}"


def _quote(value: str) -> str:
    """Double-quote a scalar for the frontmatter, escaping backslash + quote.
    ASCII-only output (the ascii-code rule)."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _render_scalar(value: Any) -> str:
    """Render a scalar frontmatter value deterministically: bool -> true/false,
    int -> bare, everything else -> a quoted string."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return _quote(str(value))


def _render_frontmatter(frontmatter: Mapping[str, Any]) -> str:
    """Render the artifact frontmatter as a deterministic YAML-subset block
    (sorted keys; nested str->str maps as indented blocks; str lists inline). No
    external YAML dependency (Article VIII) and no wall-clock field, so the same
    inputs produce byte-identical bytes (FR-006 / SC-002)."""
    lines: list[str] = ["---"]
    for key in sorted(frontmatter):
        value = frontmatter[key]
        if isinstance(value, Mapping):
            lines.append(f"{key}:")
            for sub_key in sorted(value):
                lines.append(f"  {sub_key}: {_render_scalar(value[sub_key])}")
        elif isinstance(value, (list, tuple)):
            inline = ", ".join(_quote(str(item)) for item in value)
            lines.append(f"{key}: [{inline}]")
        else:
            lines.append(f"{key}: {_render_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


class GitReverseSynthesizer:
    """Synthesize a public repo into a deterministic ``reverse_prompt`` projection.

    Implements the frozen ``RepoSynthesizer`` protocol. Construct with an injected
    ``source`` (the git / platform-API extractor; offline fake in tests), and
    optionally a ``provider`` name + ``model`` for the LLM call, a
    ``downstream_license`` to arm the compatibility gate, and an ``artifacts_root``
    for where the ``.md`` artifact is written (defaults to
    ``.cex/runtime/artifacts/reverse_prompts``). All optional -- a no-arg instance
    is constructible (its default source fails closed until injected)."""

    def __init__(
        self,
        source: RepoSource | None = None,
        *,
        provider: str | None = None,
        model: str | None = None,
        downstream_license: str | None = None,
        artifacts_root: str | Path | None = None,
    ) -> None:
        self._source: RepoSource = source if source is not None else _default_source
        self._provider = provider
        self._model = model or os.environ.get("CEXAI_MODEL", _DEFAULT_MODEL)
        self._downstream_license = downstream_license
        self._artifacts_root = (
            Path(artifacts_root) if artifacts_root is not None else _DEFAULT_ARTIFACTS_ROOT
        )

    # -- extraction --------------------------------------------------------- #
    def extract(self, repo_url: str) -> RepoExtract:
        """Extract ``repo_url`` into a normalized read-only ``RepoExtract``: sort
        the file tree (FR-006), truncate it at the 5,000-path budget (E1 / SC-007,
        ``truncated=True``), and cap entry files at 10 (FR-002). The raw source is
        injected; this method owns the deterministic shaping."""
        url = _normalize_repo_url(repo_url)
        raw = self._source(url)
        return self._normalize_extract(raw)

    @staticmethod
    def _normalize_extract(raw: RepoExtract) -> RepoExtract:
        files = tuple(sorted(raw.file_tree))
        truncated = raw.truncated
        if len(files) > _FILE_TREE_BUDGET:
            files = files[:_FILE_TREE_BUDGET]
            truncated = True
        entry_files = dict(sorted(raw.entry_files.items())[:_MAX_ENTRY_FILES])
        return RepoExtract(
            source_url=raw.source_url,
            tree_sha=raw.tree_sha,
            default_branch=raw.default_branch,
            primary_language=raw.primary_language,
            description=raw.description,
            file_tree=files,
            readme=raw.readme,
            entry_files=entry_files,
            truncated=truncated,
        )

    # -- synthesis ---------------------------------------------------------- #
    def synthesize(self, repo_url: str, filled_vars: Mapping[str, str]) -> ReversePrompt:
        """Extract ``repo_url`` and project a deterministic ``ReversePrompt`` with
        the 3 open vars filled, writing the ``.md`` artifact under the artifacts
        root. Raises ``LicenseCompatibilityError`` on an incompatible declared
        downstream (fail-closed, before the LLM call); emits
        ``LicenseUnknownWarning`` for a no-LICENSE target."""
        extract = self.extract(repo_url)
        return self._project(extract, filled_vars)

    def _project(
        self, extract: RepoExtract, filled_vars: Mapping[str, str]
    ) -> ReversePrompt:
        resolved = self._resolve_vars(extract, filled_vars)

        # License hygiene gate -- BEFORE the LLM call (no spend on a blocked synth).
        derived_from_unlicensed = False
        upstream_spdx: str | None = None
        if not has_license_file(extract):
            warnings.warn(LicenseUnknownWarning(extract.source_url), stacklevel=2)
            derived_from_unlicensed = True
        else:
            upstream_spdx = detect_license_spdx(extract)
            if upstream_spdx is not None and self._downstream_license is not None:
                check_license_compatibility(upstream_spdx, self._downstream_license)

        body = self._synthesize_body(extract, resolved)
        frontmatter = self._build_frontmatter(
            extract, resolved, derived_from_unlicensed, upstream_spdx
        )
        reverse_prompt = ReversePrompt(
            source_url=extract.source_url,
            tree_sha=extract.tree_sha,
            open_vars=_OPEN_VARS,
            filled_vars=resolved,
            body=body,
            frontmatter=frontmatter,
        )
        self._write_artifact(reverse_prompt)
        return reverse_prompt

    def _resolve_vars(
        self, extract: RepoExtract, filled_vars: Mapping[str, str]
    ) -> dict[str, str]:
        """Resolve the 3 open vars: fall through to the default filler when a value
        is missing/empty (FR-005), and validate the two enum vars."""
        resolved: dict[str, str] = {}
        for name in _OPEN_VARS:
            value = filled_vars.get(name)
            resolved[name] = str(value) if value else _DEFAULT_FILLERS[name]
        if resolved["target_runtime"] not in _VALID_RUNTIMES:
            raise ReverseSynthError(
                extract.source_url,
                f"invalid target_runtime {resolved['target_runtime']!r}",
            )
        if resolved["complexity_level"] not in _VALID_COMPLEXITY:
            raise ReverseSynthError(
                extract.source_url,
                f"invalid complexity_level {resolved['complexity_level']!r}",
            )
        return resolved

    def _synthesize_body(self, extract: RepoExtract, resolved: Mapping[str, str]) -> str:
        """Build the fixed deterministic prompt and dispatch it through the
        foundation LLM facade at temperature 0.0 (FR-006/FR-012). The reply text is
        the reverse_prompt body."""
        request = LlmRequest(
            model=self._model,
            messages=(
                Message("system", _SYSTEM_PROMPT),
                Message("user", _build_user_prompt(extract, resolved)),
            ),
            temperature=0.0,
        )
        response = _llm_call(request, provider=self._provider)
        return response.text

    def _build_frontmatter(
        self,
        extract: RepoExtract,
        resolved: Mapping[str, str],
        derived_from_unlicensed: bool,
        upstream_spdx: str | None,
    ) -> dict[str, Any]:
        frontmatter: dict[str, Any] = {
            "kind": "reverse_prompt",
            "source_url": extract.source_url,
            "tree_sha": extract.tree_sha,
            "open_vars": list(_OPEN_VARS),
            "_filled_vars": dict(resolved),
            "_open_vars_frozen": True,
            "_extraction_truncated": extract.truncated,
            "synthesized_by_nucleus": _SYNTHESIS_NUCLEUS,
            "meta": {"protocol": _PROTOCOL, "protocol_version": _PROTOCOL_VERSION},
        }
        if derived_from_unlicensed:
            frontmatter["derived_from_unlicensed_source"] = True
        if upstream_spdx is not None:
            frontmatter["upstream_license"] = upstream_spdx
        return frontmatter

    def _write_artifact(self, reverse_prompt: ReversePrompt) -> Path:
        """Persist the projection to ``<artifacts_root>/<tree_sha>.md`` with frozen
        frontmatter + body. Deterministic bytes (FR-006); returns the written
        path."""
        self._artifacts_root.mkdir(parents=True, exist_ok=True)
        path = self._artifacts_root / f"{reverse_prompt.tree_sha}.md"
        content = _render_frontmatter(reverse_prompt.frontmatter) + "\n\n" + reverse_prompt.body + "\n"
        path.write_text(content, encoding="utf-8")
        return path

    # -- triangulation (US P2) ---------------------------------------------- #
    def as_triangulation_fragment(
        self, repo_url: str
    ) -> TriangulationBriefFragment | None:
        """The auto-research 4th source (US P2 / FR-007). Returns a
        ``TriangulationBriefFragment`` with a completeness-derived ``confidence``,
        or ``None`` when the source is unavailable for a truly-optional reason
        (network failure, deleted repo, unparseable url, ...) -- logged, not
        silent (US P2 acceptance #5). A ``LicenseCompatibilityError`` is NOT one
        of those reasons: it is the fail-closed legal-hygiene gate (Article XVII,
        14 E2 / SC-005), and swallowing it here would defeat the gate by letting
        an incompatible-license synthesis slip into the triangulation brief. It
        PROPAGATES to the caller instead."""
        try:
            extract = self.extract(repo_url)
            confidence = _completeness_score(extract)
            reverse_prompt = self._project(extract, {})
            return TriangulationBriefFragment(
                source="repo_synthesizer",
                confidence=confidence,
                body=reverse_prompt.body,
            )
        except LicenseCompatibilityError:
            # Fail-closed gate (Article XVII) -- must propagate, never swallow.
            raise
        except Exception as exc:
            # US P2 acceptance #5: a genuinely-optional source failure returns
            # empty instead of raising (network failure, deleted repo, ...).
            # Logged (not silent) so a swallowed failure is still observable.
            _LOG.warning(
                "reposynth triangulation source unavailable for %r: %s",
                repo_url,
                exc,
            )
            return None


def _build_user_prompt(extract: RepoExtract, resolved: Mapping[str, str]) -> str:
    """Assemble the deterministic user prompt from the sorted extract + resolved
    open vars. Stable ordering everywhere so identical inputs yield identical
    bytes (FR-006)."""
    entry_block = "\n".join(
        f"### {name}\n{content}" for name, content in sorted(extract.entry_files.items())
    )
    return "\n".join(
        (
            f"target_audience: {resolved['target_audience']}",
            f"target_runtime: {resolved['target_runtime']}",
            f"complexity_level: {resolved['complexity_level']}",
            "",
            f"source_url: {extract.source_url}",
            f"tree_sha: {extract.tree_sha}",
            f"default_branch: {extract.default_branch}",
            f"primary_language: {extract.primary_language}",
            f"description: {extract.description}",
            f"truncated: {str(extract.truncated).lower()}",
            "",
            "## File tree",
            "\n".join(extract.file_tree),
            "",
            "## README",
            extract.readme,
            "",
            "## Entry files",
            entry_block,
        )
    )


def _completeness_score(extract: RepoExtract) -> float:
    """Source-quality score in [0.0, 1.0] from extraction completeness (US P2
    acceptance #4): fraction of populated signals, penalising a truncated tree.
    Rounded for a deterministic confidence."""
    signals = (
        bool(extract.description),
        bool(extract.primary_language),
        bool(extract.readme),
        bool(extract.entry_files),
        bool(extract.file_tree),
        not extract.truncated,
    )
    return round(sum(signals) / len(signals), 3)


def synthesize_for_triangulation(
    repo_url: str,
    *,
    source: RepoSource | None = None,
    provider: str | None = None,
    model: str | None = None,
    artifacts_root: str | Path | None = None,
) -> TriangulationBriefFragment | None:
    """Module-level auto-research entrypoint (FR-007 / US P2 acceptance #1):
    ``synthesize_for_triangulation(repo_url) -> Optional[TriangulationBriefFragment]``.
    Thin wrapper over ``GitReverseSynthesizer.as_triangulation_fragment`` -- returns
    ``None`` when the source is unavailable for a truly-optional reason, but
    PROPAGATES ``LicenseCompatibilityError`` (the fail-closed gate never gets
    swallowed into a silent ``None``)."""
    synthesizer = GitReverseSynthesizer(
        source,
        provider=provider,
        model=model,
        artifacts_root=artifacts_root,
    )
    return synthesizer.as_triangulation_fragment(repo_url)
