#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_wikilink_gate.py -- mechanical wikilink grounding gate (Benchmark-2 mandated).

WHY (measured 2026-06-08, .cex/runtime/decisions/bench2/BENCHMARK2_REPORT.md):
  The producer-rail (prompt layer) fixed self-scoring but did NOT stop wikilink
  hallucination -- 3/3 rail-governed cheap producers fabricated wikilinks
  (7/7 tested = zero id-decls on disk: [[Cmd_I_ground_or_abstain]],
  [[kc_8f_mode_b]], [[prompt_package]], ...). A MECHANICAL gate between the
  cheap producer and the F8 commit is non-optional. This is that gate.

WHAT:
  Parse every [[target]] in an artifact body; a target RESOLVES iff some .md in
  the repo declares `^id: target$` in its frontmatter. Any unresolved target is
  a FABRICATED link. Exact id-decl match only: [[kc_8f_mode_b]] does NOT resolve
  against the real id `kc_8f_mode_b_decompose` -- substring/prefix matching would
  silently pass hallucinations, so the gate refuses it.

REUSE NOTE (checked before building, per handoff):
  The wikilink regex is kept byte-identical to cex_index.WIKILINK_RE. cex_index
  builds a heavyweight SQLite graph (files.id + edges.target_id) but exposes NO
  standalone "is this id declared?" resolver, and using it would require a built
  .cex/index.db. cex_doctor has no public per-artifact wikilink resolver either.
  This gate implements the lightweight, in-process-cached id-decl scan the
  handoff asked for, so the W3 swarm can call gate(path) per artifact with zero
  DB dependency.

CLI:
  python _tools/cex_wikilink_gate.py path/to/artifact.md
  python _tools/cex_wikilink_gate.py --all N03_engineering/
  python _tools/cex_wikilink_gate.py path/to/artifact.md --json
  python _tools/cex_wikilink_gate.py path/to/artifact.md --on-fail drop|escalate|reject

Programmatic (W3 swarm, per artifact):
  from cex_wikilink_gate import gate
  ok, fabricated = gate("path/to/artifact.md")   # (bool, list[str])

Exit codes:
  0 -- all wikilinks resolve (or --on-fail drop repaired the artifact)
  1 -- fabrication found, policy=reject (default)
  2 -- fabrication found, policy=escalate
  3 -- input error (no path / file not found)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Same capture as cex_index.WIKILINK_RE -- keep in sync.
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
# Frontmatter id declaration: `id: <slug>` at the start of a line.
ID_DECL_RE = re.compile(r"^id:\s*(.+?)\s*$", re.MULTILINE)

# Infra dirs that hold no typed artifacts (mirrors cex_index.SKIP_DIRS + caches).
SKIP_DIRS = {".git", ".obsidian", "__pycache__", "node_modules", ".cex",
             ".pytest_cache", ".mypy_cache", "compiled"}

EXIT_OK = 0
EXIT_REJECT = 1
EXIT_ESCALATE = 2
EXIT_INPUT = 3

# In-process cache: {root_str: frozenset(ids)}. The W3 swarm gates N artifacts
# in one process; it must not re-scan the corpus N times.
_ID_INDEX_CACHE: dict[str, frozenset[str]] = {}


# ---------------------------------------------------------------------------
# id index (the resolution authority)
# ---------------------------------------------------------------------------

def _frontmatter_block(text: str) -> str:
    """Return the frontmatter region (between the first two '---' fences), or ''."""
    t = text.lstrip()
    if not t.startswith("---"):
        return ""
    end = t.find("---", 3)
    if end < 0:
        return ""
    return t[3:end]


def extract_declared_id(text: str) -> str | None:
    """Return the frontmatter `id:` declaration of a doc, or None.

    Implements the handoff's `^id: target$` rule. Scans ONLY the frontmatter
    block, so a body line like `id: foo` inside a fenced code sample cannot mint
    a phantom id (a false-positive id would let a fabricated link pass -- the one
    failure mode a security gate must never have).
    """
    fm = _frontmatter_block(text)
    if not fm:
        return None
    m = ID_DECL_RE.search(fm)
    if not m:
        return None
    val = m.group(1).strip().strip('"').strip("'").strip()
    return val or None


def build_id_index(root: Path = ROOT, force: bool = False) -> frozenset[str]:
    """Scan every .md under root; return the frozenset of declared frontmatter ids.

    Cached per-root in-process. Pass force=True to invalidate (e.g. after the
    pipeline writes a new artifact whose own id later links are checked against).
    """
    key = str(root)
    if not force and key in _ID_INDEX_CACHE:
        return _ID_INDEX_CACHE[key]
    ids: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            fp = Path(dirpath) / fn
            try:
                text = fp.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            decl = extract_declared_id(text)
            if decl:
                ids.add(decl)
    frozen = frozenset(ids)
    _ID_INDEX_CACHE[key] = frozen
    return frozen


# ---------------------------------------------------------------------------
# wikilink extraction + check
# ---------------------------------------------------------------------------

def _normalize_target(raw: str) -> str:
    """Strip Obsidian alias/heading/block suffixes -> bare target id.

    [[target|Alias]]   -> target
    [[target#Section]] -> target
    [[target^block]]   -> target
    """
    t = raw.strip()
    for sep in ("|", "#", "^"):
        if sep in t:
            t = t.split(sep, 1)[0]
    return t.strip()


def _strip_frontmatter(text: str) -> str:
    """Return the body after the frontmatter fence (wikilinks live in the body)."""
    t = text.lstrip()
    if t.startswith("---"):
        end = t.find("---", 3)
        if end >= 0:
            return t[end + 3:]
    return text


def extract_body_wikilinks(text: str) -> list[str]:
    """All [[target]] in the body (frontmatter stripped), normalized, in order."""
    body = _strip_frontmatter(text)
    out: list[str] = []
    for raw in WIKILINK_RE.findall(body):
        tgt = _normalize_target(raw)
        if tgt:
            out.append(tgt)
    return out


def check_text(text: str, id_index: frozenset[str] | set[str]) -> tuple[bool, list[str]]:
    """(ok, fabricated) for artifact text + a resolved id index.

    `fabricated` is the sorted, de-duplicated list of targets with no `^id:`
    declaration in id_index.
    """
    targets = extract_body_wikilinks(text)
    fabricated = sorted({t for t in targets if t not in id_index})
    return (len(fabricated) == 0, fabricated)


def check_artifact(path: str | Path,
                   id_index: frozenset[str] | set[str] | None = None) -> tuple[bool, list[str]]:
    """(ok, fabricated) for an artifact file. Builds/uses the cached index if None."""
    if id_index is None:
        id_index = build_id_index()
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return check_text(text, id_index)


def gate(path: str | Path) -> tuple[bool, list[str]]:
    """Per-artifact callable for the W3 swarm. -> (ok: bool, fabricated: list[str]).

    Uses the in-process cached id index (build once, gate many). This is the
    authoritative entry point: the W3 swarm calls it with an explicit path right
    after each cheap producer emits, before any commit.
    """
    return check_artifact(path, build_id_index())


# ---------------------------------------------------------------------------
# repair (--on-fail drop)
# ---------------------------------------------------------------------------

def repair_text(text: str, fabricated: list[str] | set[str]) -> tuple[str, list[str]]:
    """Drop fabricated [[X]] -> plain display text. Returns (new_text, dropped).

    [[X]] -> X ; [[X|Alias]] -> Alias ; [[X#H]] -> X . Valid links are untouched.
    Only [[...]] tokens are rewritten, so frontmatter (bare `related:` ids) is
    never disturbed.
    """
    fab = set(fabricated)
    dropped: list[str] = []

    def _sub(m: re.Match) -> str:
        raw = m.group(1)
        tgt = _normalize_target(raw)
        if tgt in fab:
            dropped.append(tgt)
            if "|" in raw:
                return raw.split("|", 1)[1].strip()  # keep the human alias text
            return tgt
        return m.group(0)

    new_text = WIKILINK_RE.sub(_sub, text)
    return new_text, dropped


def repair_file(path: str | Path,
                fabricated: list[str] | None = None) -> list[str]:
    """Drop fabricated links in-place. Returns the list of dropped targets."""
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    if fabricated is None:
        _ok, fabricated = check_text(text, build_id_index())
    if not fabricated:
        return []
    new_text, dropped = repair_text(text, fabricated)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
    return dropped


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _under_root(p: Path) -> bool:
    try:
        Path(p).resolve().relative_to(ROOT)
        return True
    except ValueError:
        return False


def _rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p)


def _iter_targets(path: str | None, all_dir: str | None) -> list[Path]:
    paths: list[Path] = []
    if path:
        paths.append(Path(path))
    if all_dir:
        base = Path(all_dir)
        if not base.is_absolute():
            base = ROOT / base
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                if fn.endswith(".md"):
                    paths.append(Path(dirpath) / fn)
    return paths


def _print_human(results: list[dict], on_fail: str) -> None:
    total = len(results)
    clean = sum(1 for r in results if r["ok"])
    failed = total - clean
    for r in results:
        if r["ok"]:
            continue
        if r["dropped"]:
            print("[DROP] %s -- dropped %d fabricated: %s"
                  % (r["path"], len(r["dropped"]), ", ".join(r["dropped"])))
        else:
            print("[FAIL] %s -- %d fabricated: %s"
                  % (r["path"], len(r["fabricated"]), ", ".join(r["fabricated"])))
    if failed == 0:
        print("[wikilink-gate] PASS: %d/%d artifact(s) clean." % (clean, total))
    else:
        verb = {"drop": "repaired (dropped)",
                "escalate": "escalated",
                "reject": "rejected"}[on_fail]
        print("[wikilink-gate] %d/%d clean; %d %s."
              % (clean, total, failed, verb))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="CEX wikilink grounding gate (Benchmark-2 mandated)")
    ap.add_argument("path", nargs="?", help="Artifact .md to gate")
    ap.add_argument("--all", metavar="DIR", dest="all_dir",
                    help="Gate every .md under DIR")
    ap.add_argument("--on-fail", choices=["drop", "escalate", "reject"],
                    default="reject",
                    help="Policy on fabrication (default: reject)")
    ap.add_argument("--json", action="store_true", help="Emit a JSON report")
    args = ap.parse_args(argv)

    if not args.path and not args.all_dir:
        print("[wikilink-gate] FAIL: need a PATH or --all DIR", file=sys.stderr)
        return EXIT_INPUT
    if args.path and not Path(args.path).exists():
        print("[wikilink-gate] FAIL: file not found: %s" % args.path,
              file=sys.stderr)
        return EXIT_INPUT

    id_index = build_id_index()
    results: list[dict] = []
    any_fab = False
    for p in _iter_targets(args.path, args.all_dir):
        if not p.exists():
            continue
        ok, fab = check_artifact(p, id_index)
        dropped: list[str] = []
        if not ok and args.on_fail == "drop":
            dropped = repair_file(p, fab)
        results.append({
            "path": _rel(p),
            "ok": ok,
            "fabricated": fab,
            "dropped": dropped,
        })
        if not ok:
            any_fab = True

    if args.json:
        print(json.dumps({"on_fail": args.on_fail, "results": results}, indent=2))
    else:
        _print_human(results, args.on_fail)

    if not any_fab:
        return EXIT_OK
    if args.on_fail == "drop":
        return EXIT_OK  # repaired in place; artifact may proceed
    if args.on_fail == "escalate":
        return EXIT_ESCALATE
    return EXIT_REJECT


if __name__ == "__main__":
    sys.exit(main())
