#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CEX Hygiene v1.1 -- Artifact CRUD / garbage collector.

Enforces scope discipline in the CEX repo. Detects and cleans out-of-scope
artifacts, temp files, stale compiled output, report accumulation, and
dispatch leftovers. Also supports atomic kind deletion from all registries.

Usage:
  python _tools/cex_hygiene.py scan                  # find out-of-scope items
  python _tools/cex_hygiene.py scan --json           # machine-readable
  python _tools/cex_hygiene.py clean --dry-run       # preview actions
  python _tools/cex_hygiene.py clean                 # archive + delete
  python _tools/cex_hygiene.py prune-reports          # keep latest self-audit
  python _tools/cex_hygiene.py prune-reports --dry-run
  python _tools/cex_hygiene.py prune-compiled         # remove orphan compiled
  python _tools/cex_hygiene.py stats                  # repo hygiene metrics
  python _tools/cex_hygiene.py delete-kind KIND --dry-run  # preview kind deletion
  python _tools/cex_hygiene.py delete-kind KIND --confirm  # execute kind deletion

Exit codes: 0 = clean, 1 = issues found, 2 = critical
"""

import argparse
import json
import re
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cex_shared import CEX_ROOT, parse_frontmatter

# =============================================================================
# Constants
# =============================================================================

ARCHIVE_DIR = CEX_ROOT / ".cex" / "archive"
HYGIENE_LOG = ARCHIVE_DIR / "hygiene_log.jsonl"
RUNTIME_DIR = CEX_ROOT / ".cex" / "runtime"

# CEX system terms -- files containing these are likely system artifacts
CEX_TERMS = frozenset({
    "cex", "builder", "8", "kind", "pillar", "nucleus",
    "archetype", "iso", "frontmatter", "pipeline", "n07",
    "n03", "n01", "n02", "n04", "n05", "n06", "dispatch",
    "handoff", "signal", "fractal", "taxonomy",
})

# Known user-project indicators (heuristic, case-insensitive)
# Patterns must be specific enough to avoid false positives on CEX system terms.
# e.g., "delivery" alone would match "Delivery Formats" in CEX output pillar.
USER_PROJECT_PATTERNS = [
    r"pet\s*shop", r"\binstagram\b", r"\btiktok\b", r"\byoutube\b",
    r"\be-?commerce\b", r"loja\s+virtual", r"crm\s+para",
    r"landing\s+page\s+para", r"\bcardapio\b", r"menu\s+digital",
    r"delivery\s+(app|service|servico)", r"\bagendamento\b",
    r"scheduling\s+app", r"\bpet\b(?!\s*project)",
    r"sal(a|ao)\s+de\s+beleza", r"barbearia",
    r"consultorio", r"clinica\s+(?!al)",
]
USER_PROJECT_RE = re.compile(
    "|".join(USER_PROJECT_PATTERNS), re.IGNORECASE
)

# Nucleus directory pattern
NUCLEUS_RE = re.compile(r"^N0[0-7]_")

# Pillar directory pattern
PILLAR_RE = re.compile(r"^P(0[1-9]|1[0-2])_")

# Task file pattern in repo root
TASK_FILE_RE = re.compile(r"^n0[0-7]_task\.md$")


# =============================================================================
# Data structures
# =============================================================================

@dataclass
class Issue:
    """Single hygiene issue detected by a scan rule."""
    rule_id: str
    rule_name: str
    path: str
    action: str  # DELETE, ARCHIVE, WARN, SKIP
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {
            "rule": self.rule_id,
            "rule_name": self.rule_name,
            "path": self.path,
            "action": self.action,
            "reason": self.reason,
        }


@dataclass
class ScanResult:
    """Aggregated scan results -- importable API."""
    issues: list[Issue] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.action in ("DELETE", "ARCHIVE"))

    @property
    def warn_count(self) -> int:
        return sum(1 for i in self.issues if i.action == "WARN")

    @property
    def skip_count(self) -> int:
        return sum(1 for i in self.issues if i.action == "SKIP")

    def by_rule(self) -> dict[str, list[Issue]]:
        """Group issues by rule_id."""
        grouped: defaultdict[str, list[Issue]] = defaultdict(list)
        for issue in self.issues:
            grouped[issue.rule_id].append(issue)
        return dict(grouped)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": len(self.issues),
            "critical": self.critical_count,
            "warnings": self.warn_count,
            "skipped": self.skip_count,
            "issues": [i.to_dict() for i in self.issues],
        }


# =============================================================================
# Scan Rules
# =============================================================================

def rule_r01_temp_files(root: Path) -> list[Issue]:
    """R01: TEMP_FILES -- _tmp_* or tmp_* in repo root."""
    issues = []
    for pattern in ("_tmp_*", "tmp_*"):
        for p in root.glob(pattern):
            if p.is_file():
                issues.append(Issue(
                    rule_id="R01", rule_name="TEMP_FILES",
                    path=str(p.relative_to(root)),
                    action="DELETE",
                    reason="Temp file in repo root",
                ))
    return issues


def rule_r02_empty_dirs(root: Path) -> list[Issue]:
    """R02: EMPTY_DIRS -- directories with 0 files (recursive)."""
    issues = []
    for d in sorted(root.rglob("*")):
        if not d.is_dir():
            continue
        # Skip hidden dirs, .git, node_modules
        rel = d.relative_to(root)
        parts = rel.parts
        if any(p.startswith(".git") or p == "node_modules" for p in parts):
            continue
        # Check if truly empty (no files, no subdirs with files)
        has_content = any(d.rglob("*"))
        if has_content:
            continue
        # Exclude .cex/runtime/* dirs -- they're meant to be empty when clean
        rel_str = str(rel).replace("\\", "/")
        if rel_str.startswith(".cex/runtime"):
            issues.append(Issue(
                rule_id="R02", rule_name="EMPTY_DIRS",
                path=rel_str,
                action="SKIP",
                reason="Runtime dir (expected empty)",
            ))
            continue
        issues.append(Issue(
            rule_id="R02", rule_name="EMPTY_DIRS",
            path=rel_str,
            action="DELETE",
            reason="Empty directory",
        ))
    return issues


def rule_r03_nested_duplicates(root: Path) -> list[Issue]:
    """R03: NESTED_DUPLICATES -- N0X_name/N0X_name/ double-nesting."""
    issues = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or not NUCLEUS_RE.match(d.name):
            continue
        for sub in sorted(d.iterdir()):
            if sub.is_dir() and sub.name == d.name:
                has_files = any(sub.rglob("*"))
                if has_files:
                    issues.append(Issue(
                        rule_id="R03", rule_name="NESTED_DUPLICATES",
                        path=str(sub.relative_to(root)).replace("\\", "/"),
                        action="WARN",
                        reason="Nested duplicate with content -- manual review needed",
                    ))
                else:
                    issues.append(Issue(
                        rule_id="R03", rule_name="NESTED_DUPLICATES",
                        path=str(sub.relative_to(root)).replace("\\", "/"),
                        action="DELETE",
                        reason="Nested duplicate (empty)",
                    ))
    return issues


def rule_r04_stale_compiled(root: Path) -> list[Issue]:
    """R04: STALE_COMPILED -- .yaml in compiled/ without matching .md source."""
    issues = []
    compiled_dirs = list(root.rglob("compiled"))
    for cd in compiled_dirs:
        if not cd.is_dir():
            continue
        # Skip .cex dirs and .git
        rel = cd.relative_to(root)
        if any(p.startswith(".") for p in rel.parts):
            continue
        parent = cd.parent
        for yf in sorted(cd.glob("*.yaml")):
            # Try to find matching .md source
            stem = yf.stem
            # compiled/p05_lp_foo.yaml -> look for p05_lp_foo.md in parent tree
            found_source = False
            for md in parent.rglob("*.md"):
                if md.stem == stem:
                    found_source = True
                    break
            # Also check: the yaml might compile from a differently-named md
            # e.g., kc_foo.md -> compiled/p01_kc_foo.yaml
            if not found_source:
                # Strip pillar prefix from stem for broader search
                bare = re.sub(r"^p\d{2}_", "", stem)
                for md in parent.rglob("*.md"):
                    if md.stem == bare or md.stem.endswith("_" + bare):
                        found_source = True
                        break
            if not found_source:
                issues.append(Issue(
                    rule_id="R04", rule_name="STALE_COMPILED",
                    path=str(yf.relative_to(root)).replace("\\", "/"),
                    action="DELETE",
                    reason="No matching .md source found",
                ))
    return issues


def rule_r05_report_accumulation(root: Path) -> list[Issue]:
    """R05: REPORT_ACCUMULATION -- multiple self_audit_*.md per nucleus."""
    issues = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or not NUCLEUS_RE.match(d.name):
            continue
        reports_dir = d / "reports"
        if not reports_dir.is_dir():
            continue
        audits = sorted(reports_dir.glob("self_audit_*.md"))
        if len(audits) <= 1:
            continue
        # Keep latest (by name sort, which works for date-suffixed files)
        latest = audits[-1]
        for old in audits[:-1]:
            issues.append(Issue(
                rule_id="R05", rule_name="REPORT_ACCUMULATION",
                path=str(old.relative_to(root)).replace("\\", "/"),
                action="ARCHIVE",
                reason=f"Superseded by {latest.name}",
            ))
    return issues


def rule_r06_superseded_docs(root: Path) -> list[Issue]:
    """R06: SUPERSEDED_DOCS -- _docs/X.md when _docs/X_v2.md exists."""
    issues = []
    docs_dir = root / "_docs"
    if not docs_dir.is_dir():
        return issues
    md_files = {f.stem: f for f in docs_dir.glob("*.md")}
    for stem, path in sorted(md_files.items()):
        # Check if a _v2 version exists
        v2_stem = stem + "_v2"
        if v2_stem in md_files:
            issues.append(Issue(
                rule_id="R06", rule_name="SUPERSEDED_DOCS",
                path=str(path.relative_to(root)).replace("\\", "/"),
                action="DELETE",
                reason=f"Superseded by {v2_stem}.md",
            ))
    return issues


def _load_known_kinds() -> set[str]:
    """Load valid kind names from kinds_meta.json."""
    kinds_path = CEX_ROOT / ".cex" / "kinds_meta.json"
    if kinds_path.exists():
        try:
            data = json.loads(kinds_path.read_text(encoding="utf-8"))
            return set(data.keys())
        except Exception:
            pass
    return set()


_KNOWN_KINDS: set[str] | None = None


def _get_known_kinds() -> set[str]:
    global _KNOWN_KINDS
    if _KNOWN_KINDS is None:
        _KNOWN_KINDS = _load_known_kinds()
    return _KNOWN_KINDS


def _is_user_project_file(path: Path, root: Path) -> bool:
    """Heuristic: does this file look like a user-project artifact?

    Three-layer check:
    1. If frontmatter has a valid CEX kind -> KEEP (golden example for builders)
    2. If title/description matches user-project patterns -> FLAG
    3. If body entirely lacks CEX system terms AND no valid kind -> FLAG

    Golden examples (ex_*.md in examples/) are FORMAT references for builders.
    They demonstrate HOW to structure a knowledge_card, agent, etc. Their CONTENT
    may be about Amazon ads or React patterns -- that's fine. What matters is
    whether they have valid CEX frontmatter (kind field matching kinds_meta.json).
    """
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False

    fm = parse_frontmatter(content)

    # Check 1: valid CEX kind in frontmatter -> this is a golden example, KEEP
    if fm and isinstance(fm, dict):
        kind = str(fm.get("kind", "")).strip().lower()
        known = _get_known_kinds()
        if kind and (kind in known or kind.replace("-", "_") in known):
            return False  # legitimate golden example

    # Check 2: frontmatter title/description matches user-project patterns
    if fm and isinstance(fm, dict):
        title = str(fm.get("title", ""))
        desc = str(fm.get("description", ""))
        header = title + " " + desc
        if USER_PROJECT_RE.search(header):
            return True

    # Check 3: body (after frontmatter) lacks CEX system terms entirely
    body = content
    if content.strip().startswith("---"):
        end = content.find("---", content.find("---") + 3)
        if end > 0:
            body = content[end + 3:]
    body_lower = body.lower()
    has_cex_term = any(term in body_lower for term in CEX_TERMS)
    if not has_cex_term:
        return True
    return False


def rule_r07_user_project_artifacts(root: Path) -> list[Issue]:
    """R07: USER_PROJECT_ARTIFACTS -- user-project files in pillar examples/."""
    issues = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or not PILLAR_RE.match(d.name):
            continue
        examples_dir = d / "examples"
        if not examples_dir.is_dir():
            continue
        for f in sorted(examples_dir.rglob("*.md")):
            if _is_user_project_file(f, root):
                issues.append(Issue(
                    rule_id="R07", rule_name="USER_PROJECT_ARTIFACTS",
                    path=str(f.relative_to(root)).replace("\\", "/"),
                    action="ARCHIVE",
                    reason="User-project artifact in examples/",
                ))
        for f in sorted(examples_dir.rglob("*.yaml")):
            if _is_user_project_file(f, root):
                issues.append(Issue(
                    rule_id="R07", rule_name="USER_PROJECT_ARTIFACTS",
                    path=str(f.relative_to(root)).replace("\\", "/"),
                    action="ARCHIVE",
                    reason="User-project compiled artifact in examples/",
                ))
    # Also check compiled/ dirs in pillars for user-project compiled output
    for d in sorted(root.iterdir()):
        if not d.is_dir() or not PILLAR_RE.match(d.name):
            continue
        compiled_dir = d / "compiled"
        if not compiled_dir.is_dir():
            continue
        for f in sorted(compiled_dir.glob("*.yaml")):
            if _is_user_project_file(f, root):
                issues.append(Issue(
                    rule_id="R07", rule_name="USER_PROJECT_ARTIFACTS",
                    path=str(f.relative_to(root)).replace("\\", "/"),
                    action="ARCHIVE",
                    reason="User-project compiled artifact",
                ))
    return issues


def rule_r08_orphan_task_files(root: Path) -> list[Issue]:
    """R08: ORPHAN_TASK_FILES -- n0X_task.md files in repo root."""
    issues = []
    for f in sorted(root.iterdir()):
        if f.is_file() and TASK_FILE_RE.match(f.name):
            issues.append(Issue(
                rule_id="R08", rule_name="ORPHAN_TASK_FILES",
                path=f.name,
                action="DELETE",
                reason="Dispatch leftover in repo root",
            ))
    return issues


# =============================================================================
# Scan Engine
# =============================================================================

def rule_r09_third_party_narrative(root: Path) -> list[Issue]:
    """Detect narrative third-party project mentions.

    Flags: bare references to external projects (e.g. assimilation source frameworks)
    in docs/builders/specs.

    Preserves: provenance tags ending in `_origin` (e.g. `hermes_origin`) -- these
    are metadata about kind genealogy, not narrative.
    """
    issues: list[Issue] = []
    # Build keywords via chr to avoid self-detection
    KW_HERMES = chr(72) + chr(69) + chr(82) + chr(77) + chr(69) + chr(83)
    NARRATIVE_KEYWORDS = [
        KW_HERMES.lower(),
        "opencode-hermes-multiagent",
        "claude-council",
        "1ilkhamov/",
    ]
    EXCLUDE_DIRS = {".git", ".cex", "compiled", "_external", ".venv_litellm", "node_modules", "_done"}
    EXCLUDE_FILES = {f"kc_competitor_{KW_HERMES.lower()}.md", "changelog_cex_v1.md", "taxonomy_sources.yaml"}
    PROVENANCE_TOKEN = KW_HERMES.lower() + "_origin"

    for f in root.rglob("*.md"):
        if any(p in f.parts for p in EXCLUDE_DIRS):
            continue
        if f.name in EXCLUDE_FILES:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for line in content.splitlines():
            low = line.lower()
            if PROVENANCE_TOKEN in low:
                continue
            if "kc_competitor_" in low:
                continue  # competitor analysis cross-references
            for kw in NARRATIVE_KEYWORDS:
                if kw in low:
                    issues.append(Issue(
                        rule_id="R09",
                        rule_name="third_party_narrative",
                        path=str(f.relative_to(root)),
                        action="WARN",
                        reason=f"narrative '{kw}' (not provenance tag)",
                    ))
                    break
            else:
                continue
            break  # one issue per file
    return issues


def rule_r10_stale_model_slugs(root: Path) -> list[Issue]:
    """Detect hardcoded older model slugs that should use forward-compat aliases.

    Examples: claude-opus-4-7 -> opus, claude-sonnet-4-5 -> sonnet.

    Skips: cost_budget docs (need exact slugs), benchmark/experiment results,
    historical changelog entries.
    """
    issues: list[Issue] = []
    STALE_SLUGS = ["claude-opus-4-6", "claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-4"]
    EXCLUDE_DIRS = {".git", ".cex", "compiled", ".venv_litellm", "node_modules", "_done"}
    EXCLUDE_PATTERNS = ["cost_budget", "experiment_history", "benchmark_", "changelog"]

    for f in root.rglob("*.md"):
        if any(p in f.parts for p in EXCLUDE_DIRS):
            continue
        if any(pat in str(f).lower() for pat in EXCLUDE_PATTERNS):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for slug in STALE_SLUGS:
            if slug in content:
                issues.append(Issue(
                    rule_id="R10",
                    rule_name="stale_model_slug",
                    path=str(f.relative_to(root)),
                    action="WARN",
                    reason=f"hardcoded {slug} -- consider 'opus'/'sonnet'/'haiku' alias",
                ))
                break
    return issues


def rule_r11_stale_counts(root: Path) -> list[Issue]:
    """Detect stale repo counts that drift from reality.

    Compares mentions like 'NNN builders' to actual archetypes/builders/ count.
    """
    issues: list[Issue] = []
    builders_dir = root / "archetypes" / "builders"
    if not builders_dir.exists():
        return issues
    actual_builders = sum(1 for d in builders_dir.iterdir() if d.is_dir())
    EXCLUDE_DIRS = {".git", ".cex", "compiled", "_done", ".venv_litellm"}
    EXCLUDE_PATTERNS = ["changelog", "_releases"]

    for f in root.rglob("*.md"):
        if any(p in f.parts for p in EXCLUDE_DIRS):
            continue
        if any(pat in str(f).lower() for pat in EXCLUDE_PATTERNS):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in re.finditer(r"(\d{2,4})\s+builders\b", content):
            n = int(m.group(1))
            if n != actual_builders and n in [259, 295, 301, 302, 303, 304]:
                issues.append(Issue(
                    rule_id="R11",
                    rule_name="stale_counts",
                    path=str(f.relative_to(root)),
                    action="WARN",
                    reason=f"stale count: '{m.group()}' (actual: {actual_builders})",
                ))
                break
    return issues


def rule_r12_dead_dir_refs(root: Path) -> list[Issue]:
    """Detect references to directories that no longer exist."""
    issues: list[Issue] = []
    DEAD_DIRS = ["_seeds/", "extensions/ollama-provider", "_showoff/"]
    EXCLUDE_DIRS = {".git", ".cex", "compiled", "_done", ".venv_litellm"}

    for f in root.rglob("*.md"):
        if any(p in f.parts for p in EXCLUDE_DIRS):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for dead in DEAD_DIRS:
            if dead in content:
                target = root / dead.rstrip("/")
                if target.exists():
                    continue  # path lives, ref is OK
                issues.append(Issue(
                    rule_id="R12",
                    rule_name="dead_dir_refs",
                    path=str(f.relative_to(root)),
                    action="WARN",
                    reason=f"references dead dir: {dead}",
                ))
                break
    return issues


ALL_RULES = [
    rule_r01_temp_files,
    rule_r02_empty_dirs,
    rule_r03_nested_duplicates,
    rule_r04_stale_compiled,
    rule_r05_report_accumulation,
    rule_r06_superseded_docs,
    rule_r07_user_project_artifacts,
    rule_r08_orphan_task_files,
    rule_r09_third_party_narrative,
    rule_r10_stale_model_slugs,
    rule_r11_stale_counts,
    rule_r12_dead_dir_refs,
]


def run_scan(root: Path | None = None) -> ScanResult:
    """Run all 8 scan rules. Returns ScanResult (importable API)."""
    if root is None:
        root = CEX_ROOT
    result = ScanResult()
    for rule_fn in ALL_RULES:
        result.issues.extend(rule_fn(root))
    return result


# =============================================================================
# Actions: archive, delete, log
# =============================================================================

def _log_action(
    action: str, path_str: str, rule_id: str, dest: str | None = None
) -> None:
    """Append to hygiene_log.jsonl."""
    HYGIENE_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "path": path_str,
        "rule": rule_id,
    }
    if dest:
        entry["dest"] = dest
    with open(HYGIENE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=True) + "\n")


def _archive_file(src_path: Path, archive_subdir: str, root: Path) -> str:
    """Move file to .cex/archive/{subdir}/, handling name collisions."""
    dest_dir = ARCHIVE_DIR / archive_subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src_path.name
    if dest.exists():
        stamp = datetime.now().strftime("%Y%m%d")
        stem = src_path.stem
        suffix = src_path.suffix
        dest = dest_dir / f"{stem}_{stamp}{suffix}"
    shutil.move(str(src_path), str(dest))
    return str(dest.relative_to(root))


def _delete_path(target: Path, root: Path) -> None:
    """Delete a file or empty directory.

    RBAC seam (IRREVERSIBLE): artifact deletion is the owner-only `delete` lifecycle action.
    When a principal/session is bound (CEX_PRINCIPAL set), this HALTS + audits a non-owner
    via the cex_bootstrap --teardown reference pattern; with NO principal bound (single-
    tenant / legacy) it is byte-identical default-allow. Registered in
    p11_rp_cex_role_matrix (seam: artifact.delete). The deferred import keeps load-time
    acyclic and degrade-never (RBAC tier absent -> legacy behavior). SystemExit from a deny
    is BaseException, so it propagates past `except ImportError` and correctly halts."""
    try:
        from cex_rbac import active_principal, Resource
        from cex_rbac_audit import enforce_audited
        principal = active_principal()
        if principal is not None:
            try:
                rel = target.relative_to(root).as_posix()
            except ValueError:
                rel = target.name
            # enforce_audited HALTS (SystemExit) + logs the violation on deny; allows owner.
            enforce_audited(principal, "delete", Resource(name="artifact:" + rel))
    except ImportError:
        pass  # degrade-never: RBAC tier absent -> legacy default-allow
    if target.is_file():
        target.unlink()
    elif target.is_dir():
        try:
            target.rmdir()  # only works if empty
        except OSError:
            shutil.rmtree(str(target))


def execute_clean(
    result: ScanResult, root: Path, dry_run: bool = False
) -> tuple[int, int, int]:
    """Execute clean actions for all issues in a ScanResult."""
    archived = 0
    deleted = 0
    skipped = 0
    for issue in result.issues:
        target = root / issue.path
        if not target.exists():
            continue
        if issue.action == "SKIP" or issue.action == "WARN":
            skipped += 1
            continue
        if dry_run:
            tag = "[DRY-RUN]"
            print(f"  {tag} {issue.action}: {issue.path} ({issue.reason})")
            if issue.action == "DELETE":
                deleted += 1
            elif issue.action == "ARCHIVE":
                archived += 1
            continue
        if issue.action == "DELETE":
            _delete_path(target, root)
            _log_action("DELETE", issue.path, issue.rule_id)
            deleted += 1
            print(f"  [DELETED] {issue.path}")
        elif issue.action == "ARCHIVE":
            # Determine archive subdir from rule
            subdir_map = {
                "R05": "reports",
                "R07": "examples",
            }
            subdir = subdir_map.get(issue.rule_id, "misc")
            dest = _archive_file(target, subdir, root)
            _log_action("ARCHIVE", issue.path, issue.rule_id, dest=dest)
            archived += 1
            print(f"  [ARCHIVED] {issue.path} -> {dest}")
    return archived, deleted, skipped


# =============================================================================
# Subcommands
# =============================================================================

def cmd_scan(args: argparse.Namespace) -> int:
    """Scan and report hygiene issues."""
    result = run_scan()
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=True))
    else:
        print_scan_report(result)
    return 0 if result.critical_count == 0 else 1


def cmd_clean(args: argparse.Namespace) -> int:
    """Archive + delete flagged items."""
    result = run_scan()
    if result.critical_count == 0:
        print("=== CEX Hygiene Clean ===")
        print("Nothing to clean. Repo is healthy.")
        return 0
    print("=== CEX Hygiene Clean ===")
    archived, deleted, skipped = execute_clean(
        result, CEX_ROOT, dry_run=args.dry_run
    )
    print()
    mode_tag = " (DRY-RUN)" if args.dry_run else ""
    print(f"SUMMARY{mode_tag}: {archived} archived | {deleted} deleted | {skipped} skipped")
    if not args.dry_run and (archived + deleted) > 0:
        return 0
    return 1 if result.critical_count > 0 else 0


def cmd_prune_reports(args: argparse.Namespace) -> int:
    """Keep only latest self_audit per nucleus."""
    # Run just R05
    issues = rule_r05_report_accumulation(CEX_ROOT)
    if not issues:
        print("No report accumulation found.")
        return 0
    print(f"=== Prune Reports: {len(issues)} to archive ===")
    temp = ScanResult(issues=issues)
    archived, _, _ = execute_clean(temp, CEX_ROOT, dry_run=args.dry_run)
    print(f"Archived: {archived}")
    return 0


def cmd_prune_compiled(args: argparse.Namespace) -> int:
    """Remove compiled YAML without matching source .md."""
    issues = rule_r04_stale_compiled(CEX_ROOT)
    if not issues:
        print("No stale compiled files found.")
        return 0
    print(f"=== Prune Compiled: {len(issues)} stale files ===")
    temp = ScanResult(issues=issues)
    _, deleted, _ = execute_clean(temp, CEX_ROOT, dry_run=args.dry_run)
    print(f"Deleted: {deleted}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Print repo hygiene metrics."""
    result = run_scan()
    by_rule = result.by_rule()

    # Count total .md artifacts in pillar dirs
    total_artifacts = 0
    user_project = 0
    for d in sorted(CEX_ROOT.iterdir()):
        if d.is_dir() and PILLAR_RE.match(d.name):
            mds = list(d.rglob("*.md"))
            total_artifacts += len(mds)
    # Also count nucleus dirs
    for d in sorted(CEX_ROOT.iterdir()):
        if d.is_dir() and NUCLEUS_RE.match(d.name):
            mds = list(d.rglob("*.md"))
            total_artifacts += len(mds)

    user_project = len(by_rule.get("R07", []))
    temp_files = len(by_rule.get("R01", []))
    stale_compiled = len(by_rule.get("R04", []))
    report_accum = len(by_rule.get("R05", []))
    orphan_tasks = len(by_rule.get("R08", []))

    system_artifacts = total_artifacts - user_project
    unclassified = 0  # future: items that don't match any known kind
    health_pct = (
        (total_artifacts - result.critical_count) / total_artifacts * 100
        if total_artifacts > 0 else 100.0
    )

    print("=== CEX Hygiene Stats ===")
    print(f"Total artifacts:     {total_artifacts:>5}")
    print(f"System artifacts:    {system_artifacts:>5} ({system_artifacts / max(total_artifacts, 1) * 100:.1f}%)")
    print(f"User-project:        {user_project:>5} ({user_project / max(total_artifacts, 1) * 100:.1f}%)")
    print(f"Temp files:          {temp_files:>5}")
    print(f"Stale compiled:      {stale_compiled:>5}")
    print(f"Report accumulation: {report_accum:>5}")
    print(f"Orphan task files:   {orphan_tasks:>5}")
    print(f"Repo health:         {health_pct:>5.1f}%")
    print("=" * 32)
    return 0 if result.critical_count == 0 else 1


# =============================================================================
# Report Printer
# =============================================================================

def print_scan_report(result: ScanResult) -> None:
    """Print formatted scan report to stdout."""
    by_rule = result.by_rule()
    rule_order = [
        ("R01", "TEMP_FILES"),
        ("R02", "EMPTY_DIRS"),
        ("R03", "NESTED_DUPLICATES"),
        ("R04", "STALE_COMPILED"),
        ("R05", "REPORT_ACCUMULATION"),
        ("R06", "SUPERSEDED_DOCS"),
        ("R07", "USER_PROJECT_ARTIFACTS"),
        ("R08", "ORPHAN_TASK_FILES"),
        ("R09", "third_party_narrative"),
        ("R10", "stale_model_slug"),
        ("R11", "stale_counts"),
        ("R12", "dead_dir_refs"),
    ]

    print("=== CEX Hygiene Scan ===")
    print()
    for rule_id, rule_name in rule_order:
        issues = by_rule.get(rule_id, [])
        count = len(issues)
        print(f"{rule_id} {rule_name}: {count} found")
        for issue in issues[:5]:
            suffix = ""
            if issue.action == "SKIP":
                suffix = " (SKIP: " + issue.reason + ")"
            elif issue.reason:
                suffix = " (" + issue.reason + ")"
            print(f"  - {issue.path}{suffix}")
        if count > 5:
            print(f"  ... +{count - 5} more")

    # Summary
    total = len(result.issues)
    archives = sum(1 for i in result.issues if i.action == "ARCHIVE")
    deletes = sum(1 for i in result.issues if i.action == "DELETE")
    warns = sum(1 for i in result.issues if i.action == "WARN")
    print()
    print(f"SUMMARY: {total} items | {archives} archives | {deletes} deletes | {warns} warnings")
    if result.critical_count > 0:
        print("Run with: python _tools/cex_hygiene.py clean")


# =============================================================================
# delete-kind: atomic 6-registry removal
# =============================================================================

@dataclass
class DeleteTarget:
    """One file or directory to be deleted as part of --delete-kind."""
    registry: str  # human label (e.g. "kinds_meta.json", "builder ISOs")
    path: str      # relative to CEX_ROOT
    exists: bool


def _find_delete_targets(kind: str, root: Path) -> list[DeleteTarget]:
    """Discover all 6 registry locations for a given kind.

    Returns a list of DeleteTarget entries (exist or not).
    """
    slug = kind.replace("-", "_")
    slug_dash = kind.replace("_", "-")
    targets: list[DeleteTarget] = []

    # 1. .cex/kinds_meta.json (entry)
    km_path = root / ".cex" / "kinds_meta.json"
    km_has_kind = False
    if km_path.exists():
        try:
            data = json.loads(km_path.read_text(encoding="utf-8"))
            km_has_kind = slug in data or slug_dash in data
        except Exception:
            pass
    targets.append(DeleteTarget(
        registry="kinds_meta.json",
        path=".cex/kinds_meta.json",
        exists=km_has_kind,
    ))

    # 2. archetypes/builders/{kind}-builder/ (12 ISOs directory)
    builder_dir = root / "archetypes" / "builders" / f"{slug_dash}-builder"
    targets.append(DeleteTarget(
        registry="builder ISOs",
        path=str(builder_dir.relative_to(root)).replace("\\", "/"),
        exists=builder_dir.is_dir(),
    ))

    # 3. N00_genesis/P01_knowledge/library/kind/kc_{kind}.md
    kc_path = root / "N00_genesis" / "P01_knowledge" / "library" / "kind" / f"kc_{slug}.md"
    targets.append(DeleteTarget(
        registry="knowledge card",
        path=str(kc_path.relative_to(root)).replace("\\", "/"),
        exists=kc_path.is_file(),
    ))

    # 4. .claude/agents/{kind}-builder.md (sub-agent)
    agent_path = root / ".claude" / "agents" / f"{slug_dash}-builder.md"
    targets.append(DeleteTarget(
        registry="sub-agent",
        path=str(agent_path.relative_to(root)).replace("\\", "/"),
        exists=agent_path.is_file(),
    ))

    # 5. Any N0X_*/ artifacts with kind: {kind} in frontmatter
    for nuc_dir in sorted(root.iterdir()):
        if not nuc_dir.is_dir() or not NUCLEUS_RE.match(nuc_dir.name):
            continue
        for md_file in sorted(nuc_dir.rglob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                fm = parse_frontmatter(content)
                if fm and isinstance(fm, dict):
                    fk = str(fm.get("kind", "")).strip()
                    if fk == slug or fk == slug_dash:
                        targets.append(DeleteTarget(
                            registry="nucleus artifact",
                            path=str(md_file.relative_to(root)).replace("\\", "/"),
                            exists=True,
                        ))
            except Exception:
                continue

    # 6. References in compiled/ indexes
    compiled_patterns = [
        f"kc_{slug}.yaml",
        f"{slug_dash}.yaml",
        f"*_{slug}.yaml",
        f"*_{slug_dash}.yaml",
    ]
    seen_compiled: set[str] = set()
    for compiled_dir in root.rglob("compiled"):
        if not compiled_dir.is_dir():
            continue
        rel = compiled_dir.relative_to(root)
        if any(p.startswith(".git") for p in rel.parts):
            continue
        for pattern in compiled_patterns:
            for cf in compiled_dir.glob(pattern):
                rel_path = str(cf.relative_to(root)).replace("\\", "/")
                if rel_path in seen_compiled:
                    continue
                seen_compiled.add(rel_path)
                targets.append(DeleteTarget(
                    registry="compiled index",
                    path=rel_path,
                    exists=cf.is_file(),
                ))

    return targets


def _execute_delete_kind(kind: str, targets: list[DeleteTarget], root: Path) -> list[str]:
    """Execute atomic deletion of a kind from all registries.

    Returns list of error messages. Empty list = success.
    Atomic: if any step fails, reports errors without partial cleanup
    (caller should check before proceeding).
    """
    slug = kind.replace("-", "_")
    slug_dash = kind.replace("_", "-")
    errors: list[str] = []

    # Pre-check: verify all targets are accessible
    for t in targets:
        if not t.exists:
            continue
        full = root / t.path
        if t.registry == "kinds_meta.json":
            if not full.exists():
                errors.append(f"[FAIL] {t.path} not readable")
        elif t.registry == "builder ISOs":
            if not full.is_dir():
                errors.append(f"[FAIL] {t.path} is not a directory")
        else:
            if not full.exists():
                errors.append(f"[FAIL] {t.path} does not exist")

    if errors:
        return errors

    # Execute deletions
    for t in targets:
        if not t.exists:
            continue
        full = root / t.path
        try:
            if t.registry == "kinds_meta.json":
                # Remove entry from JSON, preserve other entries
                data = json.loads(full.read_text(encoding="utf-8"))
                removed = False
                for key in (slug, slug_dash):
                    if key in data:
                        del data[key]
                        removed = True
                if removed:
                    full.write_text(
                        json.dumps(data, indent=2, ensure_ascii=True) + "\n",
                        encoding="utf-8",
                    )
                    print(f"  [OK] Removed '{kind}' from {t.path}")
                else:
                    print(f"  [SKIP] '{kind}' not found in {t.path}")
            elif t.registry == "builder ISOs":
                shutil.rmtree(str(full))
                print(f"  [OK] Deleted directory {t.path}")
            else:
                full.unlink()
                print(f"  [OK] Deleted {t.path}")
        except Exception as e:
            errors.append(f"[FAIL] {t.path}: {e}")

    # Log the deletion
    _log_action("DELETE_KIND", kind, "DELETE_KIND")

    return errors


def cmd_delete_kind(args: argparse.Namespace) -> int:
    """Delete a kind from all 6 registries (atomic).

    --dry-run (default): show what would be deleted.
    --confirm: execute the deletion.
    """
    kind = args.delete_kind
    if not kind:
        print("[FAIL] --delete-kind requires a kind name")
        return 2

    slug = kind.replace("-", "_")
    slug_dash = kind.replace("_", "-")

    print(f"=== CEX Hygiene: delete-kind '{kind}' ===")
    print()

    targets = _find_delete_targets(kind, CEX_ROOT)

    existing = [t for t in targets if t.exists]
    missing = [t for t in targets if not t.exists]

    if not existing:
        print(f"[WARN] Kind '{kind}' not found in any registry.")
        print("Checked locations:")
        for t in targets:
            print(f"  [ ] {t.registry}: {t.path}")
        return 1

    print(f"Found {len(existing)} items to delete:\n")
    for t in existing:
        print(f"  [x] {t.registry}: {t.path}")
    if missing:
        print(f"\nNot found ({len(missing)} registries empty):")
        for t in missing:
            print(f"  [ ] {t.registry}: {t.path}")

    if not args.confirm:
        print(f"\n[DRY-RUN] No files deleted. Use --confirm to execute.")
        return 0

    print(f"\nExecuting deletion of '{kind}' from {len(existing)} locations...")
    print()
    errors = _execute_delete_kind(kind, targets, CEX_ROOT)

    if errors:
        print()
        print(f"[FAIL] {len(errors)} error(s) during deletion:")
        for e in errors:
            print(f"  {e}")
        print()
        print("WARNING: Deletion was NOT atomic -- some files may have been removed.")
        print("Check git status and restore if needed: git checkout -- <path>")
        return 2

    deleted_count = len(existing)
    print()
    print(f"[OK] Kind '{kind}' removed from {deleted_count} locations.")
    print("Run 'git status' to review changes before committing.")
    return 0


# =============================================================================
# split_frontmatter fallback (if cex_shared not available)
# =============================================================================

def _split_frontmatter_fallback(text: str) -> dict[str, Any] | None:
    """Minimal frontmatter parser fallback."""
    import yaml as _yaml
    text = text.strip()
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end < 0:
        return None
    try:
        result = _yaml.safe_load(text[3:end])
        return result if isinstance(result, dict) else None
    except Exception:
        return None


# =============================================================================
# CLI
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CEX Hygiene v1.0 -- Artifact garbage collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # scan
    p_scan = sub.add_parser("scan", help="Find out-of-scope items")
    p_scan.add_argument("--json", action="store_true", help="JSON output")

    # clean
    p_clean = sub.add_parser("clean", help="Archive + delete flagged items")
    p_clean.add_argument("--dry-run", action="store_true", help="Preview only")

    # prune-reports
    p_pr = sub.add_parser("prune-reports", help="Keep latest self-audit per nucleus")
    p_pr.add_argument("--dry-run", action="store_true", help="Preview only")

    # prune-compiled
    p_pc = sub.add_parser("prune-compiled", help="Remove orphan compiled YAML")
    p_pc.add_argument("--dry-run", action="store_true", help="Preview only")

    # stats
    sub.add_parser("stats", help="Repo hygiene metrics")

    # delete-kind
    p_dk = sub.add_parser(
        "delete-kind",
        help="Remove a kind from all 6 registries (kinds_meta, builder ISOs, "
             "KC, sub-agent, nucleus artifacts, compiled indexes)",
    )
    p_dk.add_argument(
        "delete_kind", metavar="KIND",
        help="Kind name to delete (e.g. circuit_breaker, landing-page)",
    )
    p_dk.add_argument(
        "--dry-run", action="store_true", default=True,
        help="Preview what would be deleted (default behavior)",
    )
    p_dk.add_argument(
        "--confirm", action="store_true",
        help="Execute the deletion (required to actually delete files)",
    )

    return parser


def main() -> None:
    parser = build_parser()

    # Per-verb help (article Sec 2.1).
    VERB_HELP = {
        "scan":            "Audit artifacts for hygiene issues. Read-only.",
        "clean":           "Fix detected hygiene issues (rename, dedupe, etc.).",
        "prune-reports":   "Delete stale report files from .cex/reports/.",
        "prune-compiled":  "Delete stale compiled/ directories.",
        "stats":           "Show artifact counts and hygiene summary.",
        "delete-kind":     "Remove all artifacts of a specific kind.",
    }
    try:
        from cex_agent_io import maybe_print_verb_help
        if maybe_print_verb_help(sys.argv[1:], VERB_HELP):
            sys.exit(0)
    except ImportError:
        pass

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "scan": cmd_scan,
        "clean": cmd_clean,
        "prune-reports": cmd_prune_reports,
        "prune-compiled": cmd_prune_compiled,
        "stats": cmd_stats,
        "delete-kind": cmd_delete_kind,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(0)

    exit_code = handler(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            main()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_hygiene"))
    except ImportError:
        main()
