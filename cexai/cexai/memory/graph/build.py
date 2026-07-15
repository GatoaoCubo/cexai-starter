"""Build a typed knowledge graph from a source tree (06 FR-001..003, FR-007).

``build_graph`` walks a directory and emits typed nodes/edges:
  * every text file in scope -> a ``file`` node (lang/size/sha1/lines attrs);
  * Python ``import`` / ``from ... import`` -> ``module`` nodes + ``imports``
    edges carrying ``line`` provenance; ``def`` / ``class`` -> ``function`` /
    ``class`` nodes + ``defines`` edges; an import whose module maps to an
    indexed file gets a ``resolves_to`` edge (the bridge that makes a 2-hop
    neighborhood reach the imported file -- US P2);
  * Markdown ``[[wikilinks]]`` -> ``doc`` nodes + ``references`` edges;
  * YAML top-level keys -> ``yaml_key`` nodes + ``declares`` edges.

Robustness (06 edge cases): binary files are skipped + logged ``WARN``; a Python
syntax error does NOT abort the build -- the file node is still created with
``parse_error=True`` and a ``parse_error_message`` attr.

PARSER CHOICE (FR-006 -- runs locally; ZERO heavy deps offline). Extraction is a
pure-Python ``re`` + stdlib ``compile()`` scanner. ``tree-sitter`` (the
``cexai[memory]`` extra) is the documented OPTIONAL accelerator for full-fidelity
ASTs across more languages; it is imported lazily only when present and is NOT
required for the offline path exercised by the test suite -- the regex/``compile``
extractor is the always-available fallback the spec calls for.

``reindex_graph`` is the FR-007 incremental pass: it diffs the on-disk manifest
against the recorded one and only re-processes changed/added files, removes
deleted ones, and garbage-collects orphaned shared nodes.

absorbs: 06_graphify/code-graph
"""

from __future__ import annotations

import hashlib
import logging
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path

from cexai.memory._shared.types import GraphEdge, GraphNode
from cexai.memory.graph.store import KnowledgeGraph

__all__ = ["build_graph", "reindex_graph", "scan_manifest", "ReindexReport"]

_LOG = logging.getLogger(__name__)

# Directories never worth indexing (VCS, caches, vendored deps, build output).
_SKIP_DIRS = frozenset(
    {
        ".git", "__pycache__", ".cex", "node_modules", ".venv", "venv",
        ".pytest_cache", ".mypy_cache", ".ruff_cache", ".idea", ".vscode",
        "compiled", "dist", "build", ".tox", ".eggs",
    }
)

# Extension -> language. Only these are indexed (spec scope: code + md + yaml).
_LANG_BY_SUFFIX = {
    ".py": "python",
    ".md": "markdown",
    ".markdown": "markdown",
    ".yaml": "yaml",
    ".yml": "yaml",
}

# Obvious binary extensions; a NUL-byte probe catches the rest.
_BINARY_SUFFIXES = frozenset(
    {
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".pdf",
        ".zip", ".gz", ".tar", ".7z", ".rar", ".exe", ".dll", ".so", ".dylib",
        ".pyc", ".pyo", ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".mp4",
        ".wav", ".mov", ".avi", ".class", ".jar", ".o", ".a", ".bin", ".wasm",
    }
)

_IMPORT_RE = re.compile(r"^\s*import\s+(.+)$")
_FROM_RE = re.compile(r"^\s*from\s+([\w.]+)\s+import\s+(.+)$")
_DEF_RE = re.compile(r"^(\s*)(async\s+def|def|class)\s+([A-Za-z_]\w*)")
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
_YAML_KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):")


@dataclass(frozen=True, slots=True)
class ReindexReport:
    """What an incremental ``reindex_graph`` pass did, by ``relposix`` path."""

    changed: tuple[str, ...]
    added: tuple[str, ...]
    removed: tuple[str, ...]


# --------------------------------------------------------------------------- #
# Filesystem scan                                                              #
# --------------------------------------------------------------------------- #
def _iter_files(root_path: Path) -> Iterator[Path]:
    """Yield indexable file paths under ``root_path`` (sorted, skip-dirs pruned)."""
    for path in sorted(root_path.rglob("*")):
        if path.is_dir():
            continue
        if any(part in _SKIP_DIRS for part in path.relative_to(root_path).parts):
            continue
        yield path


def _lang_of(path: Path) -> str | None:
    return _LANG_BY_SUFFIX.get(path.suffix.lower())


def _read_and_classify(path: Path) -> tuple[bool, bytes | None]:
    """Read ``path`` at most once and classify it as binary/text (R-238: the
    old ``_is_binary`` probe-read plus a separate content-read amplified into
    two full reads per file per build). Returns ``(is_binary, data)``:
    ``data`` is the full file content when a read happened, or ``None`` when
    the extension alone was enough to classify the file as binary (no I/O
    needed) or the read failed (treated as binary, matching the prior
    fallback)."""
    if path.suffix.lower() in _BINARY_SUFFIXES:
        return True, None
    try:
        data = path.read_bytes()
    except OSError:
        return True, None
    return (b"\x00" in data[:1024]), data


def _is_binary(path: Path) -> bool:
    is_binary, _data = _read_and_classify(path)
    return is_binary


def scan_manifest(root: str | Path) -> dict[str, tuple[int, str]]:
    """Map ``relposix -> (size_bytes, sha1)`` for every indexable file under
    ``root``. Used both to stamp a build and to detect staleness (FR-005) /
    diff an incremental reindex (FR-007). Binary + out-of-scope files are
    excluded so they never trigger a false 'stale'."""
    root_path = Path(root)
    manifest: dict[str, tuple[int, str]] = {}
    for path in _iter_files(root_path):
        if _lang_of(path) is None:
            continue
        is_binary, data = _read_and_classify(path)
        if is_binary:
            continue
        rel = path.relative_to(root_path).as_posix()
        manifest[rel] = (len(data), hashlib.sha1(data).hexdigest())
    return manifest


# --------------------------------------------------------------------------- #
# Per-file extraction                                                          #
# --------------------------------------------------------------------------- #
def _module_name(relposix: str) -> str:
    """Derive a dotted module name from a Python file path (``pkg/util.py`` ->
    ``pkg.util``; a package ``__init__`` collapses to the package)."""
    parts = relposix.removesuffix(".py").split("/")
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _python_parse_error(text: str, rel: str) -> str | None:
    """Return a message if ``text`` is not valid Python, else ``None``. Uses the
    stdlib compiler -- exact, dependency-free syntax-error detection."""
    try:
        compile(text, rel, "exec")
    except SyntaxError as exc:
        return f"{exc.msg} (line {exc.lineno})"
    except ValueError as exc:  # e.g. source contains NUL bytes
        return f"invalid source: {exc}"
    return None


def _extract_python(graph: KnowledgeGraph, rel: str, file_id: str, text: str) -> None:
    seen_defs: set[str] = set()
    for lineno, line in enumerate(text.splitlines(), start=1):
        from_match = _FROM_RE.match(line)
        if from_match:
            _add_import(graph, file_id, from_match.group(1), lineno, from_match.group(2).strip())
        else:
            import_match = _IMPORT_RE.match(line)
            if import_match:
                for part in import_match.group(1).split(","):
                    token = part.strip().split()  # drop "as alias"
                    if token:
                        _add_import(graph, file_id, token[0], lineno, token[0])
        def_match = _DEF_RE.match(line)
        if def_match:
            kind = "class" if def_match.group(2) == "class" else "function"
            name = def_match.group(3)
            node_id = f"{kind}:{rel}:{name}"
            if node_id not in seen_defs:
                seen_defs.add(node_id)
                graph.add_node(
                    GraphNode(id=node_id, type=kind, attrs={"name": name, "line": lineno}, source=rel)
                )
                graph.add_edge(GraphEdge(src=file_id, dst=node_id, type="defines", attrs={"line": lineno}))


def _add_import(graph: KnowledgeGraph, file_id: str, module: str, lineno: int, names: str) -> None:
    module_id = f"module:{module}"
    if graph.get_node(module_id) is None:
        graph.add_node(GraphNode(id=module_id, type="module", attrs={"name": module}, source=None))
    graph.add_edge(GraphEdge(src=file_id, dst=module_id, type="imports", attrs={"line": lineno, "names": names}))


def _extract_markdown(graph: KnowledgeGraph, rel: str, file_id: str, text: str) -> None:
    seen: set[str] = set()
    for lineno, line in enumerate(text.splitlines(), start=1):
        for match in _WIKILINK_RE.finditer(line):
            target = match.group(1).strip()
            if not target or target in seen:
                continue
            seen.add(target)
            doc_id = f"doc:{target}"
            if graph.get_node(doc_id) is None:
                graph.add_node(GraphNode(id=doc_id, type="doc", attrs={"name": target}, source=None))
            graph.add_edge(GraphEdge(src=file_id, dst=doc_id, type="references", attrs={"line": lineno}))


def _extract_yaml(graph: KnowledgeGraph, rel: str, file_id: str, text: str) -> None:
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = _YAML_KEY_RE.match(line)  # anchored: only column-0 (top-level) keys
        if not match:
            continue
        name = match.group(1)
        key_id = f"key:{rel}:{name}"
        graph.add_node(GraphNode(id=key_id, type="yaml_key", attrs={"name": name, "line": lineno}, source=rel))
        graph.add_edge(GraphEdge(src=file_id, dst=key_id, type="declares", attrs={"line": lineno}))


def _index_file(graph: KnowledgeGraph, rel: str, lang: str, data: bytes) -> None:
    """Add the file node + its extracted nodes/edges. Caller guarantees ``lang``
    is in scope and the file is not binary."""
    text = data.decode("utf-8", errors="replace")
    attrs: dict = {
        "path": rel,
        "lang": lang,
        "size": len(data),
        "sha1": hashlib.sha1(data).hexdigest(),
        "lines": text.count("\n") + 1,
    }
    parse_error = False
    if lang == "python":
        message = _python_parse_error(text, rel)
        if message is not None:
            parse_error = True
            attrs["parse_error_message"] = message
    file_id = f"file:{rel}"
    graph.add_node(GraphNode(id=file_id, type="file", attrs=attrs, source=rel, parse_error=parse_error))

    if lang == "python":
        _extract_python(graph, rel, file_id, text)
    elif lang == "markdown":
        _extract_markdown(graph, rel, file_id, text)
    elif lang == "yaml":
        _extract_yaml(graph, rel, file_id, text)


def _link_local_imports(graph: KnowledgeGraph) -> None:
    """Add ``module -> file`` ``resolves_to`` edges where an imported module maps
    to an indexed Python file. Idempotent: skips a link that already exists."""
    module_map: dict[str, str] = {}
    for node in graph.nodes():
        if node.type == "file" and node.attrs.get("lang") == "python":
            module_map[_module_name(node.attrs["path"])] = node.id
    for node in graph.nodes():
        if node.type != "module":
            continue
        target = module_map.get(node.attrs.get("name", ""))
        if target and target not in graph.neighbors(node.id, "resolves_to", "out"):
            graph.add_edge(GraphEdge(src=node.id, dst=target, type="resolves_to", attrs={}))


# --------------------------------------------------------------------------- #
# Public build + incremental reindex                                           #
# --------------------------------------------------------------------------- #
def build_graph(root: str | Path, *, store: KnowledgeGraph | None = None) -> KnowledgeGraph:
    """Index the source tree under ``root`` into a ``KnowledgeGraph`` (FR-001).

    Pass an existing ``store`` to accumulate into it; otherwise a fresh graph is
    created. Binary files are skipped with a ``WARN``; out-of-scope extensions
    are silently ignored. The build is stamped with a manifest so ``is_stale``
    and ``reindex_graph`` work afterwards."""
    root_path = Path(root)
    graph = store if store is not None else KnowledgeGraph()
    manifest: dict[str, tuple[int, str]] = {}
    for path in _iter_files(root_path):
        rel = path.relative_to(root_path).as_posix()
        is_binary, data = _read_and_classify(path)
        if is_binary:
            _LOG.warning("skipping binary file: %s", rel)
            continue
        lang = _lang_of(path)
        if lang is None:
            _LOG.debug("skipping out-of-scope file: %s", rel)
            continue
        manifest[rel] = (len(data), hashlib.sha1(data).hexdigest())
        _index_file(graph, rel, lang, data)
    _link_local_imports(graph)
    graph.record_build(root_path, manifest)
    return graph


def reindex_graph(graph: KnowledgeGraph, root: str | Path | None = None) -> ReindexReport:
    """Incrementally bring ``graph`` up to date with its source tree (FR-007).

    Only changed/added files are re-processed; removed files (and any shared
    nodes they orphan) are dropped. ``root`` defaults to the graph's recorded
    build root."""
    target_root = root if root is not None else graph.root
    if target_root is None:
        raise ValueError("graph has no recorded root; build_graph it before reindexing")
    root_path = Path(target_root)

    current = scan_manifest(root_path)
    previous = dict(graph.manifest)
    changed = sorted(rel for rel, sig in current.items() if rel in previous and previous[rel] != sig)
    added = sorted(rel for rel in current if rel not in previous)
    removed = sorted(rel for rel in previous if rel not in current)

    for rel in (*removed, *changed):
        graph.remove_source(rel)
    for rel in sorted({*changed, *added}):
        path = root_path / rel
        _index_file(graph, rel, _lang_of(path) or "python", path.read_bytes())

    _link_local_imports(graph)
    graph.gc_orphans()
    graph.record_build(root_path, current)
    return ReindexReport(changed=tuple(changed), added=tuple(added), removed=tuple(removed))
