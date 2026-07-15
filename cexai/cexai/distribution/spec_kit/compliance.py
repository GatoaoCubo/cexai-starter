"""Per-article constitution compliance checks (ADR 013) -- the CI gate generator.

ADR 013 maps each of the constitution's 17 articles to a CI-runnable test pattern;
this module implements the AUTOMATABLE subset against the cexai repo and registers
the rest as ``MANUAL`` / ``CI-ONLY`` with a one-line reason (it does NOT fake the
ones that need git history, OTel runtime, or human judgment).

Automatable here (the ADR 013 examples plus a cheap Article VI):
  * I    Library-First       -- every package dir has __init__.py + a console-script CLI
  * II   CLI Interface Mandate-- the spec-kit/compliance sub-apps expose --help + --json
  * VI   Versioning Discipline-- CHANGELOG.md exists with >= 1 semver entry
  * VII  Simplicity           -- the spec-kit feature footprint is a bounded module set
  * XI   Type-First Artifacts -- a non-exempt typed artifact carries a quality: field
  * XVI  Spec-Kit Native      -- each feature dir has the 5 spec-kit artifacts
  * XVII License Hygiene       -- NOTICE lists the absorbed sources

Registered but NOT run (honest, per the handoff -- do not fake): III, IV, V, VIII,
IX, X, XII, XIII, XIV, XV (git-history / coverage / OTel / mock-ratio / kinds_meta /
multi-runtime / human-judgment patterns).

``check_article`` runs ONE article and is a CI gate (non-zero exit on FAIL via the
CLI). ``check_all`` runs every automatable article + lists the rest as a single
"Article Compliance Report" (ADR 013 reporting format); it is a report, not a gate
(exit 0), so a single FAIL in the aggregate still emits a valid report -- the CI
gates on individual articles or reads the JSON ``passed`` flag.

Founder rule: this is CODE (checkers), NOT a new kind -- no kinds_meta edit.

absorbs: 01_spec-kit (Analyze) + ADR 013
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib  # stdlib, py3.11+ (this package's own requires-python floor)
except ImportError:  # pragma: no cover -- fallback for py<3.11 runners
    import tomli as tomllib  # type: ignore[no-redef]

from cexai.distribution.spec_kit.analyze import (
    SEV_HIGH,
    Finding,
)

__all__ = [
    "ArticleResult",
    "ComplianceReport",
    "ARTICLE_TITLES",
    "normalize_article",
    "check_article",
    "check_all",
]

# Status vocabulary. PASS/FAIL are graded (automatable) verdicts; MANUAL/CI-ONLY are
# "not run here" with a reason (the article needs human judgment or CI infrastructure).
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_MANUAL = "MANUAL"
STATUS_CI_ONLY = "CI-ONLY"

# The 17 ADR 013 articles in order. Roman numeral is the canonical id.
_ROMAN = (
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX",
    "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII",
)
_INT_TO_ROMAN = {i + 1: r for i, r in enumerate(_ROMAN)}
_ROMAN_SET = set(_ROMAN)

ARTICLE_TITLES: dict[str, str] = {
    "I": "Library-First",
    "II": "CLI Interface Mandate",
    "III": "Test-First (TDD)",
    "IV": "Integration-First Testing",
    "V": "Observable by Default",
    "VI": "Versioning Discipline",
    "VII": "Simplicity Over Cleverness",
    "VIII": "Anti-Abstraction",
    "IX": "Integration-First (no Mock-First)",
    "X": "Vocabulary-First",
    "XI": "Type-First Artifacts",
    "XII": "8F Pipeline Non-Negotiable",
    "XIII": "Sin-Driven Dispatch",
    "XIV": "Multi-Runtime Portable",
    "XV": "Absorption Over Reinvention",
    "XVI": "Spec-Kit Native",
    "XVII": "License Hygiene",
}

# The non-automatable articles + the honest reason they are not run here.
_NON_AUTOMATABLE: dict[str, tuple[str, str]] = {
    "III": (STATUS_CI_ONLY, "git-history check: test commit date <= impl commit date"),
    "IV": (STATUS_CI_ONLY, "coverage run required (integration coverage >= 80% of public API)"),
    "V": (STATUS_CI_ONLY, "OTel span-coverage runtime audit required (100% of ops emit a span)"),
    "VIII": (STATUS_MANUAL, "anti-abstraction is a code-review judgment (no wrapper-on-wrapper)"),
    "IX": (STATUS_CI_ONLY, "per-test-dir mock/dep ratio measurement required (< 0.3)"),
    "X": (STATUS_CI_ONLY, "needs kinds_meta.json to resolve every artifact kind (post cex-lab merge)"),
    "XII": (STATUS_CI_ONLY, "git pre-commit 8F-path declaration check on dispatch_* changes"),
    "XIII": (STATUS_CI_ONLY, "owner_nucleus scan over runtime dispatch handoffs"),
    "XIV": (STATUS_CI_ONLY, "multi-runtime parity run required (Claude + Ollama minimum)"),
    "XV": (STATUS_MANUAL, "Prior Art alternative quality is human-judged (>= 3 genuine alternatives)"),
}

# spec-kit chain + scaffold document kinds are governed by Articles XVI/XIX, not XI's
# quality contract; they are EXEMPT from the Type-First quality-field requirement.
# (constitution_override + feature_template are spec-kit scaffolds, not F6-PRODUCE
# CEX output artifacts -- exempting them keeps XI from a category error; genuine CEX
# kinds like knowledge_card / scoring_rubric remain graded.)
_XI_EXEMPT_KINDS = frozenset(
    {
        "specification",
        "plan",
        "tasks",
        "analysis",
        "analyze",
        "constitution",
        "constitution_override",
        "feature_template",
    }
)

# Article VII module bound for the spec-kit feature footprint (Simplicity).
_VII_MODULE_BOUND = 6


@dataclass(frozen=True, slots=True)
class ArticleResult:
    """The verdict for one article. ``status`` is PASS/FAIL (graded) or MANUAL/CI-ONLY
    (registered, not run). ``detail`` is the one-line human summary (the measured count
    or the not-run reason); ``findings`` carries the structured violations when graded.
    Immutable so it serializes deterministically."""

    article: str
    title: str
    status: str
    detail: str
    findings: tuple[Finding, ...] = ()

    @property
    def is_automatable(self) -> bool:
        """True when this article was graded here (PASS/FAIL), not just registered."""
        return self.status in (STATUS_PASS, STATUS_FAIL)

    @property
    def exit_code(self) -> int:
        """0 unless this article was graded FAIL -- the per-article CI gate."""
        return 1 if self.status == STATUS_FAIL else 0

    def to_dict(self) -> dict[str, object]:
        """A JSON-ready mapping (stable keys; findings expanded)."""
        return {
            "article": self.article,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "findings": [f.to_dict() for f in self.findings],
        }


@dataclass(frozen=True, slots=True)
class ComplianceReport:
    """The aggregate "Article Compliance Report" (ADR 013 reporting format). ``results``
    is the ordered per-article verdicts; ``root`` is the audited repo root. A report,
    not a gate: ``exit_code`` is always 0 (CI gates on individual articles or reads
    ``passed``)."""

    root: str
    results: tuple[ArticleResult, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        """True when NO automatable article graded FAIL (manual/ci-only do not count)."""
        return all(r.status != STATUS_FAIL for r in self.results)

    @property
    def exit_code(self) -> int:
        """Always 0 -- ``check all`` is report mode, not a gate (smoke-stable)."""
        return 0

    def counts(self) -> dict[str, int]:
        """Tallies: automatable pass/fail + the not-run manual/ci-only split."""
        pass_n = sum(1 for r in self.results if r.status == STATUS_PASS)
        fail_n = sum(1 for r in self.results if r.status == STATUS_FAIL)
        manual_n = sum(1 for r in self.results if r.status == STATUS_MANUAL)
        ci_n = sum(1 for r in self.results if r.status == STATUS_CI_ONLY)
        return {
            "automatable": pass_n + fail_n,
            "pass": pass_n,
            "fail": fail_n,
            "manual": manual_n,
            "ci_only": ci_n,
            "total": len(self.results),
        }

    def to_dict(self) -> dict[str, object]:
        """A JSON-ready mapping of the whole report."""
        return {
            "root": self.root,
            "passed": self.passed,
            "counts": self.counts(),
            "articles": [r.to_dict() for r in self.results],
        }

    def render(self) -> str:
        """The human-readable Article Compliance Report (ADR 013 format)."""
        c = self.counts()
        lines = [f"Article Compliance Report (root: {self.root})"]
        for r in self.results:
            lines.append(f"- Article {r.article:<5} {r.title:<28} {r.status:<8} {r.detail}")
        lines.append(
            f"Summary: {c['automatable']} automatable -> {c['pass']} PASS / {c['fail']} FAIL ; "
            f"{c['manual'] + c['ci_only']} not-run ({c['manual']} manual, {c['ci_only']} ci-only)"
        )
        return "\n".join(lines)


def normalize_article(article: str) -> str:
    """Map a user article token to its canonical roman id.

    Accepts ``article-vii`` / ``Article VII`` / ``vii`` / ``VII`` / ``7`` (case- and
    prefix-insensitive). Raises ``ValueError`` (listing the valid range) for anything
    that is not one of the 17 articles."""
    t = article.strip().lower()
    for prefix in ("article-", "article "):
        if t.startswith(prefix):
            t = t[len(prefix):].strip()
    if t.isdigit():
        n = int(t)
        if n in _INT_TO_ROMAN:
            return _INT_TO_ROMAN[n]
        raise ValueError(f"article {article!r} out of range; expected 1..17")
    up = t.upper()
    if up in _ROMAN_SET:
        return up
    raise ValueError(f"unknown article {article!r}; expected I..XVII, 1..17, or 'all'")


# --------------------------------------------------------------------------- #
# Path helpers -- every automatable check resolves paths under an explicit root  #
# (default cwd at the CLI), so tests point it at a fixture repo and `check all`   #
# audits the real repo from its root.                                            #
# --------------------------------------------------------------------------- #
def _pkg_dir(root: Path) -> Path:
    """The importable cexai package dir under ``root`` (``root/cexai/cexai``)."""
    return root / "cexai" / "cexai"


def _specs_dir(root: Path) -> Path:
    """The spec-kit feature-spec tree under ``root`` (``root/cexai-specs``)."""
    return root / "cexai-specs"


def _frontmatter(text: str) -> str | None:
    """The leading YAML frontmatter block (between the first two ``---`` fences), or
    ``None`` when the file does not open with one. Parsed line-wise -- no yaml dep."""
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    return None


_FM_KIND = re.compile(r"^kind\s*:\s*(\S+)", re.MULTILINE)
_FM_QUALITY = re.compile(r"^quality\s*:", re.MULTILINE)
_SEMVER = re.compile(r"\b\d+\.\d+\.\d+\b")


# --------------------------------------------------------------------------- #
# Automatable article checkers: (root) -> (passed, detail, findings).            #
# --------------------------------------------------------------------------- #
def _has_cexai_console_script(pyproject: Path) -> bool:
    """True iff ``pyproject`` is valid TOML declaring a real ``cexai`` entry under
    ``[project.scripts]`` (Article I's console-script requirement).

    A REAL parse via stdlib ``tomllib`` (R-232), not a substring scan over the raw
    file text: a substring test on ``"cexai =" in text`` false-PASSES on any
    unrelated line that happens to contain that text (a comment, a same-named key
    under a different table) and false-FAILS a validly-formatted entry that simply
    lacks the exact ``"cexai ="`` spacing (e.g. ``cexai="..."``). A missing file or
    a file that fails to parse as TOML honestly reports "no script" (``False``)
    rather than raising out of an Article I check.
    """
    if not pyproject.is_file():
        return False
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8", errors="replace"))
    except tomllib.TOMLDecodeError:
        return False
    scripts = data.get("project", {}).get("scripts", {})
    return isinstance(scripts, dict) and "cexai" in scripts


def _check_i(root: Path) -> tuple[bool, str, tuple[Finding, ...]]:
    """Article I -- every package dir has ``__init__.py`` + a console-script CLI."""
    pkg = _pkg_dir(root)
    if not pkg.is_dir():
        return False, f"cexai package not found at {pkg}", (
            Finding(SEV_HIGH, "PKG_NOT_FOUND", f"no package dir at {pkg}", artifact=str(pkg)),
        )
    findings: list[Finding] = []
    checked = 0
    for sub in sorted(pkg.iterdir()):
        if not sub.is_dir() or sub.name.startswith((".", "__")):
            continue
        has_py = any(sub.glob("*.py"))
        if has_py and not (sub / "__init__.py").is_file():
            findings.append(
                Finding(SEV_HIGH, "MISSING_INIT", f"package {sub.name} has .py but no __init__.py",
                        artifact=f"cexai/cexai/{sub.name}")
            )
        if has_py:
            checked += 1
    pyproject = root / "cexai" / "pyproject.toml"
    has_script = _has_cexai_console_script(pyproject)
    if not has_script:
        findings.append(
            Finding(SEV_HIGH, "NO_CONSOLE_SCRIPT", "no `cexai` console-script in pyproject [project.scripts]",
                    artifact="cexai/pyproject.toml")
        )
    passed = not findings
    detail = f"{checked} packages have __init__.py; console-script={'yes' if has_script else 'NO'}"
    return passed, detail, tuple(findings)


def _check_ii(root: Path) -> tuple[bool, str, tuple[Finding, ...]]:
    """Article II -- the spec-kit + compliance sub-apps expose ``--help`` (exit 0) and
    a ``--json`` mode. Introspects the live typer apps via CliRunner (root-independent;
    imported lazily to avoid a CLI<->checker import cycle)."""
    from typer.testing import CliRunner  # lazy: avoids spec_kit.cli import cycle

    from cexai.distribution.spec_kit.cli import compliance_app, spec_kit_app

    try:
        runner = CliRunner(mix_stderr=False)
    except TypeError:  # click >= 8.2 separates streams by default
        runner = CliRunner()

    findings: list[Finding] = []
    probes = (("spec-kit", spec_kit_app, "analyze"), ("compliance", compliance_app, "check"))
    for feature, app, subcmd in probes:
        res = runner.invoke(app, [subcmd, "--help"])
        if res.exit_code != 0:
            findings.append(
                Finding(SEV_HIGH, "HELP_NONZERO", f"`{feature} {subcmd} --help` exited {res.exit_code}",
                        artifact=feature)
            )
        if "--json" not in (res.stdout or ""):
            findings.append(
                Finding(SEV_HIGH, "NO_JSON_MODE", f"`{feature} {subcmd}` declares no --json option",
                        artifact=feature)
            )
    passed = not findings
    detail = "spec-kit + compliance sub-apps expose --help (exit 0) and --json"
    return passed, detail, tuple(findings)


def _check_vi(root: Path) -> tuple[bool, str, tuple[Finding, ...]]:
    """Article VI -- CHANGELOG.md exists with at least one semver entry."""
    changelog = root / "cexai" / "CHANGELOG.md"
    if not changelog.is_file():
        return False, "no cexai/CHANGELOG.md", (
            Finding(SEV_HIGH, "NO_CHANGELOG", "cexai/CHANGELOG.md is missing", artifact="cexai/CHANGELOG.md"),
        )
    text = changelog.read_text(encoding="utf-8", errors="replace")
    versions = len(set(_SEMVER.findall(text)))
    if versions < 1:
        return False, "CHANGELOG.md has no semver entry", (
            Finding(SEV_HIGH, "NO_VERSION_ENTRY", "CHANGELOG.md has no X.Y.Z entry", artifact="cexai/CHANGELOG.md"),
        )
    return True, f"CHANGELOG.md present with {versions} semver entrie(s)", ()


def _check_vii(root: Path) -> tuple[bool, str, tuple[Finding, ...]]:
    """Article VII -- the spec-kit feature footprint is a bounded module set
    (per-feature Simplicity: the impl introduces <= the module bound of concern)."""
    sk = _pkg_dir(root) / "distribution" / "spec_kit"
    if not sk.is_dir():
        return True, "spec_kit package absent (vacuous)", ()
    modules = sorted(
        p.stem for p in sk.glob("*.py") if p.name != "__init__.py"
    )
    n = len(modules)
    passed = n <= _VII_MODULE_BOUND
    detail = f"spec_kit modules={n} (<= {_VII_MODULE_BOUND}): {', '.join(modules)}"
    findings: tuple[Finding, ...] = ()
    if not passed:
        findings = (
            Finding(SEV_HIGH, "MODULE_SPRAWL", f"spec_kit has {n} modules (> {_VII_MODULE_BOUND})",
                    artifact="cexai/cexai/distribution/spec_kit"),
        )
    return passed, detail, findings


def _check_xi(root: Path) -> tuple[bool, str, tuple[Finding, ...]]:
    """Article XI -- a non-exempt typed artifact (frontmatter with a CEX ``kind``)
    MUST carry a ``quality:`` field. spec-kit doc kinds are exempt (Articles XVI/XIX)."""
    specs = _specs_dir(root)
    if not specs.is_dir():
        return True, "no cexai-specs tree (vacuous)", ()
    scanned = 0
    findings: list[Finding] = []
    for md in sorted(specs.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        fm = _frontmatter(text)
        if fm is None:
            continue
        kind_match = _FM_KIND.search(fm)
        if not kind_match:
            continue
        scanned += 1
        kind = kind_match.group(1).strip().strip("\"'").lower()
        if kind in _XI_EXEMPT_KINDS:
            continue
        if not _FM_QUALITY.search(fm):
            findings.append(
                Finding(SEV_HIGH, "MISSING_QUALITY",
                        f"typed artifact (kind={kind}) has no quality: field",
                        artifact=str(md.relative_to(root)) if md.is_relative_to(root) else md.name)
            )
    passed = not findings
    detail = f"{scanned} kinded artifacts scanned; {len(findings)} missing quality (spec-kit kinds exempt)"
    return passed, detail, tuple(findings)


def _check_xvi(root: Path, feature_dir: Path | None = None) -> tuple[bool, str, tuple[Finding, ...]]:
    """Article XVI -- each spec-kit feature dir has the 5 artifacts (constitution
    inherited from cexai-specs/_decisions/constitution.md). Single-dir when
    ``feature_dir`` is given; otherwise aggregate over every started feature dir."""
    required = ("spec.md", "plan.md", "tasks.md", "analyze.md")
    constitution = _specs_dir(root) / "_decisions" / "constitution.md"
    has_constitution = constitution.is_file()
    findings: list[Finding] = []

    def _check_one(d: Path) -> None:
        missing = [name for name in required if not (d / name).is_file()]
        if not has_constitution:
            missing.append("(inherited) constitution.md")
        if missing:
            findings.append(
                Finding(SEV_HIGH, "INCOMPLETE_FEATURE",
                        f"{d.name} missing spec-kit artifact(s): {', '.join(missing)}",
                        artifact=str(d.name))
            )

    if feature_dir is not None:
        d = Path(feature_dir)
        if not d.is_dir():
            return False, f"not a feature dir: {feature_dir}", (
                Finding(SEV_HIGH, "NO_FEATURE_DIR", f"not a directory: {feature_dir}", artifact=str(feature_dir)),
            )
        _check_one(d)
        passed = not findings
        return passed, f"{d.name}: {'complete' if passed else 'incomplete'} (5 spec-kit artifacts)", tuple(findings)

    specs = _specs_dir(root)
    if not specs.is_dir():
        return True, "no cexai-specs tree (vacuous)", ()
    started = [
        d for d in sorted(specs.iterdir())
        if d.is_dir() and re.match(r"^\d+_", d.name) and (d / "spec.md").is_file()
    ]
    for d in started:
        _check_one(d)
    passed = not findings
    detail = f"{len(started)} feature dirs; {len(findings)} incomplete (constitution inherited={'yes' if has_constitution else 'NO'})"
    return passed, detail, tuple(findings)


def _check_xvii(root: Path) -> tuple[bool, str, tuple[Finding, ...]]:
    """Article XVII -- NOTICE exists, is non-empty, and lists >= 1 absorbed source."""
    notice = root / "cexai" / "NOTICE"
    if not notice.is_file():
        return False, "no cexai/NOTICE", (
            Finding(SEV_HIGH, "NO_NOTICE", "cexai/NOTICE is missing", artifact="cexai/NOTICE"),
        )
    text = notice.read_text(encoding="utf-8", errors="replace")
    sources = len(re.findall(r"\b(MIT|Apache-2\.0|BSD-3-Clause|BSD)\b", text))
    if not text.strip() or sources < 1:
        return False, "NOTICE lists no absorbed source", (
            Finding(SEV_HIGH, "EMPTY_NOTICE", "NOTICE has no licensed source listed", artifact="cexai/NOTICE"),
        )
    return True, f"NOTICE present, lists {sources} licensed source mention(s)", ()


_AUTOMATABLE: dict[str, Callable[[Path], tuple[bool, str, tuple[Finding, ...]]]] = {
    "I": _check_i,
    "II": _check_ii,
    "VI": _check_vi,
    "VII": _check_vii,
    "XI": _check_xi,
    "XVI": _check_xvi,
    "XVII": _check_xvii,
}


def check_article(article: str, root: str | Path = ".", *, feature_dir: str | Path | None = None) -> ArticleResult:
    """Grade ONE article against ``root`` (default cwd) and return its ``ArticleResult``.

    Automatable articles are run (PASS/FAIL + structured findings); the rest return
    their registered MANUAL/CI-ONLY status + reason. ``feature_dir`` narrows Article
    XVI to a single feature dir (otherwise XVI audits every started feature dir).
    Raises ``ValueError`` for ``'all'`` (use ``check_all``) or an unknown article."""
    if article.strip().lower() == "all":
        raise ValueError("use check_all() for 'all'")
    roman = normalize_article(article)
    title = ARTICLE_TITLES[roman]
    base = Path(root)

    if roman in _AUTOMATABLE:
        if roman == "XVI":
            passed, detail, findings = _check_xvi(base, feature_dir=feature_dir)
        else:
            passed, detail, findings = _AUTOMATABLE[roman](base)
        status = STATUS_PASS if passed else STATUS_FAIL
        return ArticleResult(roman, title, status, detail, findings)

    status, reason = _NON_AUTOMATABLE[roman]
    return ArticleResult(roman, title, status, reason, ())


def check_all(root: str | Path = ".") -> ComplianceReport:
    """Run every article (automatable graded, the rest registered) and return the
    aggregate ``ComplianceReport`` in article order. Report mode (exit 0) -- the smoke
    ``cexai compliance check all --json`` always emits a valid report."""
    base = Path(root)
    results = tuple(check_article(roman, base) for roman in _ROMAN)
    return ComplianceReport(root=str(base), results=results)
