#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEX Hybrid Scorer -- Quality Model v2 (the honest ruler).

Spec: .cex/runtime/decisions/SELF_IMPROVEMENT_FLYWHEEL_quality_model_v2.md
      .cex/runtime/decisions/SELF_IMPROVEMENT_FLYWHEEL_phase0_spec.md

Quality of a CEX artifact = how well-formed it is as a UNIT OF THE UBIQUITOUS
LANGUAGE, reachable by INTENT RESOLUTION, and BOOTABLE as part of a runnable
business brain. NOT prose polish. NOT byte count.

Layers:
  L1 STRUCTURAL (free, instant) -- frontmatter presence + wiring ONLY (byte
     rewards CAPPED at the composite level: length alone cannot climb).
  L2 RUBRIC (free, instant) -- builder's quality_gate hard/soft checks.
  UL DIMENSIONS (free, instant) -- the 8 ubiquitous-language dimensions:
     D1 PURPOSE, D2 UBIQUITOUS-LANGUAGE, D3 OPEN-VARIABLES, D4 INSTRUCTIONS,
     D5 PROCEDURE, D6 8F-ALIGNMENT, D7 PILLAR-FIT, D8 BOOTABILITY.
  ANTI-SLOP FLOOR (free, instant) -- type-token ratio + repetition + filler
     density as a MULTIPLICATIVE CAP. A padded/repetitive artifact is capped
     so it CANNOT climb by adding words. Kills "mais words = nota maior".
  L3 SEMANTIC (1 LLM call) -- only when free layers are strong; the honesty
     pass (F7c) runs an adversarial weakest-dimension re-check on high scores.

[OK] Public API preserved: score_structural / score_rubric / score_semantic /
     score_hybrid all keep their signatures; score_hybrid still returns
     score/structural/rubric/semantic PLUS ul_dimensions/antislop_factor.

Score ranges (composite, honest ruler):
  9.0-10:  Excellent -- well-formed UL unit, intent-addressable, bootable
  8.0-8.9: Good -- solid, some UL dimensions thin
  7.0-7.9: Acceptable -- adequate but missing UL surface
  <7.0: Needs rebuild / padded / unreachable

R-173 -- Declarative Gate Spec Discovery (two-path L2 RUBRIC, additive):
  score_rubric() (the original prose/regex parser, e.g. _find_quality_gate:
  ~283 / _parse_hard_gates:~325 / score_rubric body:~356) is 100% UNCHANGED
  and still callable directly -- every caller that imports it keeps getting
  byte-identical scores/messages, forever, for any gate with no spec.

  score_hybrid() now sources its L2 rubric score through the new
  score_rubric_typed() wrapper instead of calling score_rubric() directly.
  score_rubric_typed() picks ONE of two paths per artifact:

    DECLARATIVE  -- the resolved quality gate (_find_quality_gate(kind), a
                    bld_eval_{kind}.md builder ISO) ships a SIBLING file
                    with the SAME STEM plus a `.assertions.yaml` suffix,
                    e.g. archetypes/builders/quality-gate-builder/
                    bld_eval_quality_gate.assertions.yaml next to
                    bld_eval_quality_gate.md. When present, gate evaluation
                    delegates to cex_assertions.run_assertions_from_files()
                    (_tools/cex_assertions.py, R-173's landed engine) --
                    typed, independently RE-EXECUTED checks with a required
                    `pass` field per assertion, not a trusted self-report.

    LEGACY_PROSE -- no sibling spec exists (true for all 300+ shipped gates
                    today -- this path is dormant until a gate author opts
                    in). score_rubric_typed() delegates straight through to
                    the untouched score_rubric() and repackages its 3-tuple.

  A sibling file (not an embedded ```yaml fence inside the gate .md) is the
  discovery signal on purpose: many bld_eval_*.md files already carry
  ```yaml fences as prose GOLDEN EXAMPLES for authors, not machine specs --
  reusing that fence would collide with real content. See
  _find_declarative_spec() / score_rubric_typed() docstrings for the full
  contract and the cex_assertions spec shape.

  Every result dict from score_hybrid() carries a NEW `gate_score_path` key
  ("declarative" | "legacy_prose") -- the honesty marker so no downstream
  consumer (cex_evolve, cex_apex_daemon, cex_refine, cex_doctor plugins,
  the CLI, ...) can mistake which path scored a given artifact's L2 gate.

R-194 / R-195 / R-204 -- honesty fixes (behavior-preserving on the healthy
path; a previously-silent failure now fails loud instead):
  R-194  score_semantic() returns (None, {}, reason) instead of a fabricated
         (7.0, {}, reason) when the LLM call errors or returns non-JSON.
         score_hybrid() treats None as "L3 did not run" -- it EXCLUDES
         semantic from the composite and falls back to the non-semantic
         formula (mode="hybrid_semantic_failed", failure recorded in notes)
         instead of silently folding a neutral 7.0 into a score that may
         later be written PERMANENTLY to `quality:` frontmatter via --apply.
  R-195  honesty_pass()'s `mode` no longer claims "cross_provider": that pass
         is a free, deterministic weakest-UL-dimension heuristic that NEVER
         calls any provider (a real cross-provider audit is the separate,
         opt-in F7c COUNCIL / cross_provider_council crew). `mode` is now
         "heuristic_only" | "skipped" -- it reflects what actually ran, not
         which provider API keys happen to be present in the environment.
  R-204  compute_structural_score()'s `wikilinks_resolve` check now calls
         cex_wikilink_gate.gate() (the same id-index resolver
         cex_doctor.check_wikilinks() uses) instead of being hardcoded True.
         A fabricated [[wikilink]] no longer counts as a structural PASS.
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_FILE = ROOT / ".cex" / "score_cache.json"
BUILDERS_DIR = ROOT / "archetypes" / "builders"
KINDS_META_FILE = ROOT / ".cex" / "kinds_meta.json"

# Lazy-loaded canonical kind registry (pillar + 8F verb + naming per kind).
_KINDS_META_CACHE = None


def _kinds_meta() -> dict:
    """Load .cex/kinds_meta.json once (canonical kind -> pillar/verb registry)."""
    global _KINDS_META_CACHE
    if _KINDS_META_CACHE is None:
        try:
            _KINDS_META_CACHE = json.loads(
                KINDS_META_FILE.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            _KINDS_META_CACHE = {}
    return _KINDS_META_CACHE


# ================================================================
# LAYER 1: STRUCTURAL SCORER (original, free, instant)
# ================================================================

def score_structural(path: str) -> tuple[float, list[str]]:
    """Count-based structural scoring. Returns (score 0-10 raw, notes)."""
    if not os.path.exists(path):
        return (0.0, ["MISSING"])

    content = open(path, 'r', encoding='utf-8').read()
    size = len(content.encode('utf-8'))
    notes = []

    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return (0.0, ["NO_FRONTMATTER"])

    fm = fm_match.group(1)
    body = content[fm_match.end():]

    score = 0.0

    # Frontmatter (max 2.0)
    required = ['id:', 'kind:', 'pillar:', 'quality:']
    desired = ['title:', 'version:', 'author:', 'tags:', 'tldr:', 'domain:', 'created:', 'updated:']
    for field in required:
        if field in fm:
            score += 0.3
        else:
            notes.append(f"missing {field}")
    for field in desired:
        if field in fm:
            score += 0.1

    # Content depth (max 2.5)
    if size >= 1000: score += 0.3
    if size >= 2000: score += 0.4
    if size >= 3000: score += 0.3

    headings = len(re.findall(r'^#{1,3} ', body, re.MULTILINE))
    if headings >= 2: score += 0.3
    if headings >= 5: score += 0.2

    table_rows = len(re.findall(r'^\|.*\|', body, re.MULTILINE))
    if table_rows >= 3: score += 0.3
    if table_rows >= 8: score += 0.2

    list_items = len(re.findall(r'^[-*\d]+[.)] ', body, re.MULTILINE))
    if list_items >= 3: score += 0.2

    code_blocks = len(re.findall(r'```', body))
    if code_blocks >= 2: score += 0.1

    # Domain specificity (max 1.5)
    bad_placeholders = len(re.findall(r'(?i)\b(TODO|TBD|FIXME|insert here|add later)\b', body))
    if bad_placeholders == 0:
        score += 0.5
    else:
        notes.append(f"{bad_placeholders} placeholders")
        score -= 0.3 * bad_placeholders

    body_words = len(body.split())
    if body_words >= 100: score += 0.3
    if body_words >= 200: score += 0.3
    if body_words >= 400: score += 0.2

    tldr_match = re.search(r'tldr:\s*["\']?(.*?)["\']?\s*$', fm, re.MULTILINE)
    if tldr_match and len(tldr_match.group(1)) >= 30:
        score += 0.2

    # Structure (max 1.2)
    if headings >= 3: score += 0.3
    paragraphs = len(re.findall(r'\n\n', body))
    if paragraphs >= 3: score += 0.3
    format_types = sum([headings > 0, table_rows > 0, list_items > 0, code_blocks > 0])
    if format_types >= 2: score += 0.3
    if format_types >= 3: score += 0.2

    # Normalize to 0-10 scale (raw max ~7.6)
    normalized = min(score / 7.6 * 10.0, 10.0)
    return (round(normalized, 2), notes)


# ================================================================
# STRUCTURAL SCORE v2 (10-point binary, zero LLM cost)
# Spec: _docs/specs/spec_8f_decompose.md Section 5
# ================================================================

def compute_structural_score(path: str, skip_compile: bool = False) -> dict:
    """Compute 10-point binary structural score (Structural Score v2).

    Each check is pass/fail (1 or 0). Total = sum of passes.
    Zero LLM cost. Deterministic. Same file always scores the same.
    skip_compile: True when called from cex_compile.py (avoids recursion).
    Spec: _docs/specs/spec_8f_decompose.md Section 5.

    R-196: Checks 1+2 delegate to cex_shared's line-anchored close-fence scan
    (parse_frontmatter / _frontmatter_close_index) instead of the local
    `re.match(r'^---\n(.*?)\n---')` / `content.index('---', 3)` pair, which
    closed on the FIRST '---' SUBSTRING anywhere -- including one embedded
    inside a quoted frontmatter value or a markdown table divider -- silently
    truncating the parsed frontmatter or corrupting the density body slice.
    """
    import subprocess

    sys.path.insert(0, str(ROOT / "_tools"))
    from cex_shared import _frontmatter_close_index, parse_frontmatter

    result = {
        'total': 0,
        'checks': {},
        # R-331: honest record of any advisory try/except that fired below
        # (git-history / compile subprocess reads). Additive-only key -- no
        # existing caller reads it, so its presence changes nothing for them;
        # 'total'/'checks' math is unchanged either way. Mirrors this file's
        # existing R-194/R-195/R-204 convention: a previously-silent failure
        # now fails loud (here: recorded, not printed) instead of pass-mudo.
        'notes': [],
    }

    # Check 1: frontmatter_valid
    content = ''
    try:
        content = open(path, 'r', encoding='utf-8').read()
        fm = parse_frontmatter(content)
        fm_valid = fm is not None
        if fm_valid:
            fm_valid = all(f in fm for f in ['id', 'kind', 'pillar', 'quality'])
    except Exception:
        fm_valid = False
    result['checks']['frontmatter_valid'] = fm_valid

    # Check 2: density_above_085
    try:
        end = _frontmatter_close_index(content)
        body_idx = end + 3 if end >= 0 else 0
        body = content[body_idx:]
        body_lines = body.strip().split('\n')
        content_lines = [l for l in body_lines if l.strip() and l.strip() != '---']
        density = len(content_lines) / max(len(body_lines), 1)
        density_ok = density >= 0.85
    except Exception:
        density_ok = False
    result['checks']['density_above_085'] = density_ok

    # Check 3: wikilinks_resolve (R-204 -- real resolver, was hardcoded True).
    # No wikilinks -> pass (not all artifacts need them). With wikilinks, each
    # [[target]] must resolve to a real `^id:` declaration on disk, via
    # cex_wikilink_gate.gate() -- the same mechanical id-index resolver
    # cex_doctor.py's check_wikilinks() (line ~1292) delegates to. Previously
    # a fabricated wikilink counted as a PASS toward this score unconditionally.
    # Degrade-never: if the gate module is unavailable for any reason, this is
    # an HONEST non-pass (False) -- it never counts an unverifiable link as OK.
    wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content) if content else []
    if not wikilinks:
        wikilinks_ok = True
    else:
        try:
            sys.path.insert(0, str(ROOT / "_tools"))
            import importlib
            _wl_gate_mod = importlib.import_module("cex_wikilink_gate")
            wikilinks_ok, _fabricated = _wl_gate_mod.gate(path)
        except Exception:
            wikilinks_ok = False
    result['checks']['wikilinks_resolve'] = wikilinks_ok

    # Check 4: compile_clean
    # skip_compile=True when called from cex_compile.py (avoids recursion)
    if skip_compile:
        compile_ok = True
    else:
        try:
            cp = subprocess.run(
                ['python', '_tools/cex_compile.py', path],
                capture_output=True, timeout=30,
                cwd=str(ROOT),
                # R-331: explicit text-mode decode. Without this, a subprocess
                # reader thread decoding non-UTF-8/non-cp1252 bytes from the
                # child's stdout/stderr can die mid-decode (see git_committed
                # below for the reproduced mechanism) -- errors="replace"
                # means a decode never raises, it degrades to U+FFFD instead.
                text=True, encoding="utf-8", errors="replace",
            )
            compile_ok = cp.returncode == 0
        except Exception as exc:
            compile_ok = False
            result['notes'].append(
                "compile_clean check errored (%s: %s) -- treated as fail, advisory only" %
                (type(exc).__name__, str(exc)[:120])
            )
    result['checks']['compile_clean'] = compile_ok

    # Check 5: ascii_clean (for code files only)
    ext = os.path.splitext(path)[1]
    if ext in ('.py', '.ps1', '.sh', '.cmd', '.bat'):
        try:
            raw = open(path, 'rb').read()
            # Allow BOM for .ps1
            if ext == '.ps1' and raw[:3] == b'\xef\xbb\xbf':
                raw = raw[3:]
            ascii_ok = all(b < 128 for b in raw)
        except Exception:
            ascii_ok = False
    else:
        ascii_ok = True  # .md files are allowed non-ASCII
    result['checks']['ascii_clean'] = ascii_ok

    # Check 6: size_under_cap
    try:
        size = os.path.getsize(path)
        is_builder = os.path.basename(path).startswith('bld_')
        is_prompt = 'bld_prompt_' in os.path.basename(path)
        cap = 10240 if is_prompt else 8192
        # Non-builder artifacts have no cap (specs, KCs, etc can be larger)
        size_ok = (not is_builder) or (size <= cap)
    except Exception:
        size_ok = False
    result['checks']['size_under_cap'] = size_ok

    # Check 7: has_related
    has_related = bool(re.search(r'## Related Artifacts', content))
    result['checks']['has_related'] = has_related

    # Check 8: has_tags
    has_tags = bool(re.search(r'tags:\s*\[.+\]', content))
    result['checks']['has_tags'] = has_tags

    # Check 9: artifact_on_disk (catches signal-without-deliverable)
    artifact_exists = os.path.exists(path) and os.path.getsize(path) > 0
    result['checks']['artifact_on_disk'] = artifact_exists

    # Check 10: git_committed (catches write-without-commit)
    #
    # R-331: `git show HEAD:<path>` echoes the file's git-stored bytes
    # verbatim. On Windows, subprocess.run(text=True) with no explicit
    # `encoding` decodes stdout/stderr using locale.getpreferredencoding(),
    # which is cp1252 -- a single-byte codec with 5 undefined byte values
    # (0x81, 0x8D, 0x8F, 0x90, 0x9D). A committed file whose bytes include
    # one of these makes the decode raise. Because capture_output=True opens
    # BOTH stdout and stderr as pipes, CPython's Windows Popen._communicate()
    # reads each one in its own background "reader thread"
    # (subprocess.py's _readerthread); a decode failure there does NOT
    # propagate back into this try/except at all -- it is caught only by
    # Python's default unhandled-thread-exception hook, which dumps a raw
    # traceback straight to stderr, uncontrolled, every time it fires (this
    # matches the register row's "throws ... in a subprocess-reader thread"
    # wording exactly; reproduced directly in test_cex_score_r331.py).
    # `encoding="utf-8", errors="replace"` makes the decode itself never
    # raise (replaces undecodable bytes with U+FFFD) -- closing the class,
    # not just this one call. Never blocks the advisory contract below.
    try:
        # Use relative path from repo root
        rel_path = os.path.relpath(path, str(ROOT)).replace('\\', '/')
        gc = subprocess.run(
            ['git', 'show', 'HEAD:%s' % rel_path],
            capture_output=True, text=True, timeout=10,
            cwd=str(ROOT),
            encoding="utf-8", errors="replace",
        )
        git_ok = gc.returncode == 0
    except Exception as exc:
        git_ok = False
        result['notes'].append(
            "git_committed check errored (%s: %s) -- treated as fail, advisory only" %
            (type(exc).__name__, str(exc)[:120])
        )
    result['checks']['git_committed'] = git_ok

    result['total'] = sum(1 for v in result['checks'].values() if v)
    return result


# ================================================================
# LAYER 2: RUBRIC SCORER (builder quality gate, free, instant)
# ================================================================

# Memoized gate lookups (pure by kind) -- avoids rglob per artifact in batch.
_GATE_PATH_CACHE: dict = {}


def _find_quality_gate(kind: str) -> str | None:
    """Find the quality gate file for a given kind (memoized by kind)."""
    if not kind:
        return None
    if kind in _GATE_PATH_CACHE:
        return _GATE_PATH_CACHE[kind]
    result = None
    # Try direct match: {kind}-builder/bld_eval_{kind}.md
    slug = kind.replace("_", "-")
    gate_path = BUILDERS_DIR / f"{slug}-builder" / f"bld_eval_{kind}.md"
    if gate_path.exists():
        result = str(gate_path)
    else:
        # Fallback: search
        for p in BUILDERS_DIR.rglob(f"bld_eval_{kind}.md"):
            result = str(p)
            break
        if result is None:
            # Broader search
            kind_under = kind.replace("-", "_")
            for p in BUILDERS_DIR.rglob(f"bld_eval_{kind_under}.md"):
                result = str(p)
                break
    _GATE_PATH_CACHE[kind] = result
    return result


def _parse_soft_dimensions(gate_content: str) -> list[dict]:
    """Extract soft scoring dimensions from quality gate file."""
    dims = []
    for m in re.finditer(
        r'^\|\s*(S\d+)\s*\|\s*(.*?)\s*\|\s*([\d.]+)\s*\|',
        gate_content, re.MULTILINE
    ):
        dims.append({
            "id": m.group(1),
            "description": m.group(2).strip(),
            "weight": float(m.group(3)),
        })
    return dims


def _parse_hard_gates(gate_content: str) -> list[dict]:
    """Extract hard gates from quality gate file.

    Supports optional severity column: | H01 | check | fail_cond | CRITICAL |
    Severity levels: CRITICAL (blocks), HIGH (warns), MEDIUM (documents), LOW (ignored).
    If no severity column, defaults to HIGH.
    """
    gates = []
    for m in re.finditer(
        r'^\|\s*(H\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*(?:\|\s*(CRITICAL|HIGH|MEDIUM|LOW)\s*)?\|',
        gate_content, re.MULTILINE
    ):
        severity = m.group(4).upper() if m.group(4) else "HIGH"
        gates.append({
            "id": m.group(1),
            "check": m.group(2).strip(),
            "fail_condition": m.group(3).strip(),
            "severity": severity,
        })
    return gates


# Severity weights for scoring impact
SEVERITY_WEIGHTS = {
    "CRITICAL": 1.0,   # full impact -- blocks publish
    "HIGH": 0.7,       # strong impact -- warns
    "MEDIUM": 0.3,     # partial impact -- documents
    "LOW": 0.0,        # no scoring impact -- informational
}


def score_rubric(path: str) -> tuple[float, list[dict], list[str]]:
    """Score against builder's quality gate rubric.
    Returns (score 0-10, dimensions_with_scores, notes).
    """
    if not os.path.exists(path):
        return (0.0, [], ["MISSING"])

    content = open(path, 'r', encoding='utf-8').read()
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return (0.0, [], ["NO_FRONTMATTER"])

    fm = fm_match.group(1)
    body = content[fm_match.end():]
    notes = []

    # Extract kind
    kind_match = re.search(r'kind:\s*(\S+)', fm)
    kind = kind_match.group(1).strip().strip('"\'') if kind_match else None

    # Find quality gate
    gate_path = _find_quality_gate(kind)
    if not gate_path:
        # No rubric available -- return neutral score
        return (7.5, [], [f"no quality gate for kind={kind}"])

    gate_content = open(gate_path, 'r', encoding='utf-8').read()

    # Hard gates -- binary pass/fail
    hard_gates = _parse_hard_gates(gate_content)
    hard_pass = 0
    for gate in hard_gates:
        check = gate["check"].lower()
        passed = True
        # Programmatic checks for common hard gates
        if "frontmatter" in check and "yaml" in check:
            passed = fm_match is not None
        elif "id matches" in check or "id equals" in check:
            id_match = re.search(r'id:\s*(\S+)', fm)
            passed = id_match is not None
        elif "kind equals" in check:
            passed = kind is not None
        elif "quality field" in check:
            passed = "quality:" in fm
        elif "required fields" in check:
            passed = all(f in fm for f in ['id:', 'kind:', 'pillar:'])
        elif "density_score" in check and "range" in check:
            ds = re.search(r'density_score:\s*([\d.]+)', fm)
            if ds:
                passed = 0.0 <= float(ds.group(1)) <= 1.0
            else:
                passed = False
        elif "file size" in check:
            passed = len(content.encode('utf-8')) <= 10240  # generous 10KB
        elif "tldr" in check and "160" in check:
            tldr = re.search(r'tldr:\s*["\']?(.*?)["\']?\s*$', fm, re.MULTILINE)
            passed = tldr is not None and len(tldr.group(1)) <= 160
        elif "tldr" in check and "present" in check:
            tldr = re.search(r'tldr:\s*.+', fm)
            passed = tldr is not None and len(tldr.group(0)) > 10
        elif "tags" in check and ("list" in check or "present" in check):
            passed = bool(re.search(r'tags:\s*\[.+\]', fm))
        elif "version" in check:
            passed = bool(re.search(r'version:\s*\d+\.\d+', fm))
        elif "no placeholder" in check or "no todo" in check:
            bad = len(re.findall(r'(?i)\b(TODO|TBD|FIXME|insert here|add later)\b', body))
            passed = bad == 0
        elif "has example" in check or "example" in check:
            passed = bool(re.search(r'(?i)## (Example|Usage|Sample)', body))
        elif "has table" in check or "table" in check:
            passed = bool(re.search(r'^\|.*\|', body, re.MULTILINE))
        elif "code block" in check or "```" in check:
            passed = "```" in body
        elif "body length" in check or ("min" in check and "words" in check):
            words = len(body.split())
            passed = words >= 100
        elif "no filler" in check or "filler" in check:
            fillers = re.findall(r'(?i)\b(this document|in summary|it.?s worth noting|as mentioned)\b', body)
            passed = len(fillers) == 0
        else:
            passed = True

        severity = gate.get("severity", "HIGH")
        weight = SEVERITY_WEIGHTS.get(severity, 0.7)

        if passed:
            hard_pass += weight
        else:
            if severity == "CRITICAL":
                notes.append(f"BLOCK {gate['id']} [{severity}]: {gate['check'][:50]}")
            elif severity != "LOW":
                notes.append(f"FAIL {gate['id']} [{severity}]: {gate['check'][:50]}")

    max_weight = sum(SEVERITY_WEIGHTS.get(g.get("severity", "HIGH"), 0.7)
                     for g in hard_gates) or 1.0
    hard_ratio = hard_pass / max_weight

    # Soft dimensions -- pattern-based scoring
    soft_dims = _parse_soft_dimensions(gate_content)
    dim_scores = []
    total_weight = sum(d["weight"] for d in soft_dims) or 1.0

    for dim in soft_dims:
        desc = dim["description"].lower()
        dim_score = 5.0  # default: middling

        # Score each dimension by checking artifact content
        if "tldr" in desc:
            tldr = re.search(r'tldr:\s*["\']?(.*?)["\']?\s*$', fm, re.MULTILINE)
            if tldr and 30 <= len(tldr.group(1)) <= 160:
                dim_score = 9.0
            elif tldr:
                dim_score = 6.0
            else:
                dim_score = 2.0

        elif "tags" in desc:
            tags = re.search(r'tags:\s*\[(.*?)\]', fm)
            tag_count = len(tags.group(1).split(',')) if tags else 0
            dim_score = min(10, tag_count * 2.5)

        elif "density" in desc:
            ds = re.search(r'density_score:\s*([\d.]+)', fm)
            if ds:
                dim_score = float(ds.group(1)) * 10
            else:
                dim_score = 5.0

        elif "filler" in desc or "no padding" in desc or "placeholder" in desc:
            fillers = len(re.findall(
                r'(?i)\b(this document|in summary|it.?s worth noting|as mentioned|'
                r'can help with|in conclusion|TODO|TBD|FIXME)\b', body
            ))
            dim_score = max(0, 10 - fillers * 2)

        elif "source" in desc or "attribution" in desc:
            has_sources = bool(re.search(r'sources?:', fm)) or bool(re.search(r'## (References?|Sources?)', body))
            dim_score = 8.0 if has_sources else 3.0

        elif "structure" in desc or "section" in desc:
            headings = len(re.findall(r'^#{1,3} ', body, re.MULTILINE))
            dim_score = min(10, headings * 1.5)

        elif "domain" in desc or "specific" in desc:
            has_domain = bool(re.search(r'domain:\s*\S', fm))
            body_words = len(body.split())
            dim_score = 8.0 if (has_domain and body_words >= 200) else 5.0

        elif "factual" in desc or "concrete" in desc:
            # Check for numbers, specific values, technical terms
            numbers = len(re.findall(r'\b\d+(?:\.\d+)?(?:%|ms|KB|MB|GB|px|rem|em)?\b', body))
            dim_score = min(10, 4 + numbers * 0.5)

        elif "atomic" in desc or "one concept" in desc:
            headings = len(re.findall(r'^## ', body, re.MULTILINE))
            dim_score = 8.0 if headings <= 6 else 5.0

        elif "when to use" in desc or "not-when" in desc:
            has_when = bool(re.search(r'(?i)## When|## Use Case|## Not', body))
            dim_score = 8.0 if has_when else 3.0

        dim_scores.append({
            "id": dim["id"],
            "description": dim["description"][:80],
            "weight": dim["weight"],
            "score": round(dim_score, 1),
        })

    # Weighted soft score
    if dim_scores:
        weighted = sum(d["score"] * d["weight"] for d in dim_scores) / total_weight
    else:
        weighted = 7.5

    # Combine: 60% soft dims + 40% hard gates
    rubric_score = (weighted * 0.6) + (hard_ratio * 10 * 0.4)
    rubric_score = round(min(rubric_score, 10.0), 2)

    return (rubric_score, dim_scores, notes)


# ================================================================
# R-173 -- DECLARATIVE GATE SPEC DISCOVERY + TWO-PATH WRAPPER
# score_rubric() above is UNTOUCHED (byte-identical legacy path). Everything
# below is additive: it composes cex_assertions.py (the landed R-173 engine)
# for gates that opt in, and delegates to score_rubric() unchanged otherwise.
# ================================================================

def _find_declarative_spec(gate_path: str | None) -> str | None:
    """Declarative Gate Spec Discovery contract (R-173).

    A quality-gate rubric file resolved by _find_quality_gate() (a builder
    ISO, e.g. archetypes/builders/{kind}-builder/bld_eval_{kind}.md) OPTS IN
    to the cex_assertions declarative engine by shipping a SIBLING file with
    the SAME STEM plus a `.assertions.yaml` suffix:

        archetypes/builders/quality-gate-builder/bld_eval_quality_gate.md
        archetypes/builders/quality-gate-builder/bld_eval_quality_gate.assertions.yaml   <- opt-in

    Why a sibling file and not an embedded ```yaml fence inside the gate
    .md: many bld_eval_*.md files already carry ```yaml fences as prose
    GOLDEN EXAMPLES for human gate-authors (see e.g.
    archetypes/builders/quality-gate-builder/bld_eval_quality_gate.md's own
    "## Examples" section) -- reusing that fence as a machine-spec signal
    would silently misfire on real content. A dedicated file extension is
    unambiguous, greppable, and purely additive: as of this landing, ZERO
    existing gate files have a `.assertions.yaml` sibling, so every one of
    the 300+ shipped kinds keeps scoring via the LEGACY path until a gate
    author explicitly authors a spec for it.

    Spec file shape (loaded by cex_assertions.run_assertions_from_files):
        assertions:
          - id: <string>
            type: contains | not_contains | regex | field_equals |
                  field_exists | threshold | hard_gate_table | json_schema
            field: frontmatter.<key> | body | raw   # default: body
            value: <as required by type>
            required: true|false                    # default: true

    Returns the spec path (str) if a sibling exists on disk, else None.
    """
    if not gate_path:
        return None
    p = Path(gate_path)
    spec_path = p.parent / (p.stem + ".assertions.yaml")
    return str(spec_path) if spec_path.exists() else None


def _score_declarative_gate(spec_path: str, target_path: str) -> tuple[float, list[dict], list[str]]:
    """Evaluate `target_path` against `spec_path` via cex_assertions (R-173's
    landed typed engine -- independently RE-EXECUTED checks, required `pass`
    field per assertion, never a trusted status string). Returns the SAME
    3-tuple shape as score_rubric() (score 0-10, dim_scores, notes) so
    score_rubric_typed() can treat both paths uniformly.

    Score = 10.0 when every required assertion passes, else the pass-ratio
    scaled to 0-10 (partial credit -- mirrors score_rubric()'s hard_ratio*10
    contribution for the all-hard-gates-only case).
    """
    sys.path.insert(0, str(ROOT / "_tools"))
    import importlib
    cex_assertions = importlib.import_module("cex_assertions")

    verdict = cex_assertions.run_assertions_from_files(spec_path, target_path)
    total = verdict.get("total", 0) or 1
    passed = verdict.get("passed", 0)
    score = 10.0 if verdict.get("pass") else round((passed / total) * 10.0, 2)

    dims = [
        {
            "id": r.get("id", "a%d" % i),
            "description": (r.get("message") or r.get("type") or "")[:80],
            "weight": 1.0,
            "score": 10.0 if r.get("pass") else 0.0,
        }
        for i, r in enumerate(verdict.get("results", []))
    ]
    notes = [] if verdict.get("pass") else [
        "FAIL %s: %s" % (r.get("id"), (r.get("message") or "")[:80])
        for r in verdict.get("results", [])
        if not r.get("pass") and r.get("required", True)
    ]
    return (score, dims, notes)


def score_rubric_typed(path: str) -> dict:
    """Two-path L2 RUBRIC scorer (R-173 wiring). This is the function
    score_hybrid() calls for the rubric layer.

    DECLARATIVE: the resolved gate ships a sibling `.assertions.yaml` spec
    (see _find_declarative_spec() for the full discovery contract) -- gate
    evaluation delegates to cex_assertions.py, an independently re-executed
    typed engine, instead of trusting this module's own prose/regex parse.

    LEGACY_PROSE: no sibling spec exists (true for every gate shipped today)
    -- delegates straight through to the UNTOUCHED score_rubric() and
    repackages its 3-tuple. Byte-identical scores/messages to pre-R-173.

    Any failure while running the declarative path (missing pyyaml, a
    malformed spec, cex_assertions unimportable, ...) degrades-never: it
    falls back to the legacy path and records why in `notes`, it never
    blocks or crashes scoring.

    Returns:
        {
          "score": float 0-10,               # same scale as score_rubric()[0]
          "dimensions": list[dict],           # same shape as score_rubric()[1]
          "notes": list[str],                 # same shape as score_rubric()[2]
          "score_path": "declarative" | "legacy_prose",   # THE HONESTY MARKER
          "gate_path": str | None,            # resolved bld_eval_{kind}.md
          "spec_path": str | None,            # sibling .assertions.yaml, if any
        }
    """
    if not os.path.exists(path):
        return {"score": 0.0, "dimensions": [], "notes": ["MISSING"],
                "score_path": "legacy_prose", "gate_path": None, "spec_path": None}

    content = open(path, 'r', encoding='utf-8').read()
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    kind = None
    if fm_match:
        km = re.search(r'kind:\s*(\S+)', fm_match.group(1))
        kind = km.group(1).strip().strip('"\'') if km else None

    gate_path = _find_quality_gate(kind) if kind else None
    spec_path = _find_declarative_spec(gate_path)

    if spec_path:
        try:
            score, dims, notes = _score_declarative_gate(spec_path, path)
            return {"score": score, "dimensions": dims, "notes": notes,
                    "score_path": "declarative", "gate_path": gate_path,
                    "spec_path": spec_path}
        except Exception as e:
            # degrade-never: a broken/unavailable spec NEVER blocks scoring.
            legacy_score, legacy_dims, legacy_notes = score_rubric(path)
            legacy_notes = list(legacy_notes) + [
                "declarative spec %s errored (%s: %s) -- fell back to legacy" %
                (spec_path, type(e).__name__, str(e)[:80])
            ]
            return {"score": legacy_score, "dimensions": legacy_dims, "notes": legacy_notes,
                    "score_path": "legacy_prose", "gate_path": gate_path, "spec_path": spec_path}

    # LEGACY PATH -- delegates to the untouched score_rubric(), byte-identical.
    legacy_score, legacy_dims, legacy_notes = score_rubric(path)
    return {"score": legacy_score, "dimensions": legacy_dims, "notes": legacy_notes,
            "score_path": "legacy_prose", "gate_path": gate_path, "spec_path": None}


# ================================================================
# QUALITY MODEL v2 -- ANTI-SLOP FLOOR (a gate, not a dimension)
# Spec: SELF_IMPROVEMENT_FLYWHEEL_quality_model_v2.md Section 4
# ================================================================
#
# Signal-per-token. A padded, low-diversity, repetitive artifact is CAPPED:
# it cannot climb by adding words. The 8 UL dimensions reward SIGNAL; this
# floor punishes VOLUME. Returned as a MULTIPLICATIVE factor in [floor, 1.0].

# Filler / hedge phrases that add bytes but no signal (lowercased match).
_FILLER_PATTERNS = [
    r'this (?:document|section|artifact|file)',
    r'in summary',
    r'in conclusion',
    r'it is (?:worth|important) (?:noting|to note)',
    r'as (?:mentioned|stated|noted) (?:above|earlier|previously)',
    r'needless to say',
    r'at the end of the day',
    r'when it comes to',
    r'in order to',
    r'it should be noted',
    r'please note that',
    r'as we can see',
    r'first and foremost',
    r'last but not least',
    r'in the world of',
    r'plays a (?:key|crucial|vital|important) role',
    r'a wide (?:range|variety) of',
    r'in today.?s (?:world|landscape|environment)',
]
_FILLER_RE = re.compile("|".join("(?:%s)" % p for p in _FILLER_PATTERNS), re.IGNORECASE)

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z_\-]+")

_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]+`")
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_TABLE_ROW_RE = re.compile(r"(?m)^\s*\|.*\|\s*$")
_WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")
_URL_RE = re.compile(r"https?://\S+|\b\S+/\S+\.[a-z]{2,4}\b")


def _prose_only(body: str) -> str:
    """Strip non-prose (code fences, inline code, HTML, tables, wikilinks, URLs,
    paths) so the anti-slop floor judges NATURAL-LANGUAGE prose only.

    Code/templates/tables legitimately repeat tokens and have low lexical
    diversity; scoring them for 'padding' is a false positive. Anti-slop is a
    PROSE Goodhart-guard, not a code linter. (D3/D8 already reward code/schema.)
    """
    t = _FENCE_RE.sub(" ", body)
    t = _INLINE_CODE_RE.sub(" ", t)
    t = _HTML_TAG_RE.sub(" ", t)
    t = _TABLE_ROW_RE.sub(" ", t)
    t = _WIKILINK_RE.sub(" ", t)
    t = _URL_RE.sub(" ", t)
    return t


def _antislop_factor(body: str) -> tuple[float, dict]:
    """Compute the anti-slop multiplicative cap from body PROSE (code/tables/
    HTML stripped first -- they repeat by nature and must not be penalized).

    Returns (factor in [0.55, 1.0], detail dict). Three signals:
      - type_token_ratio (lexical diversity): unique words / total words
      - repetition_ratio: fraction of repeated trigrams (n-gram echo)
      - filler_density: filler-phrase hits per 100 words

    A tight, diverse, filler-free artifact -> factor ~1.0 (no penalty).
    A padded, repetitive, hedge-heavy artifact -> factor floored near 0.55.
    Length alone NEVER raises the factor; it can only lower it via dilution.
    """
    prose = _prose_only(body)
    words = [w.lower() for w in _WORD_RE.findall(prose)]
    n = len(words)
    detail = {
        "type_token_ratio": 1.0,
        "repetition_ratio": 0.0,
        "filler_density": 0.0,
        "word_count": n,
    }
    if n < 40:
        # Too little prose to dilute -- no anti-slop penalty (other dims handle
        # thinness; code/table-heavy artifacts legitimately have little prose).
        detail["factor"] = 1.0
        return (1.0, detail)

    # --- 1. Type-token ratio (lexical diversity) -----------------------------
    # Raw TTR falls naturally as documents grow; normalize against a moving
    # expectation so long-but-diverse text is NOT punished, but repeated
    # vocabulary IS. We compare unique-count to a sqrt-scaled expectation.
    unique = len(set(words))
    ttr = unique / n
    detail["type_token_ratio"] = round(ttr, 4)

    # --- 2. Repetition ratio (trigram echo) ----------------------------------
    trigrams = [tuple(words[i:i + 3]) for i in range(n - 2)]
    if trigrams:
        seen = {}
        repeated = 0
        for tg in trigrams:
            if tg in seen:
                repeated += 1
            seen[tg] = True
        repetition = repeated / len(trigrams)
    else:
        repetition = 0.0
    detail["repetition_ratio"] = round(repetition, 4)

    # --- 3. Filler density ---------------------------------------------------
    filler_hits = len(_FILLER_RE.findall(prose))
    filler_density = filler_hits / (n / 100.0)  # hits per 100 words
    detail["filler_density"] = round(filler_density, 3)

    # --- Combine into a multiplicative cap -----------------------------------
    # Each signal contributes a sub-factor in [~0.7, 1.0]; product is floored.
    # TTR: diversity below ~0.42 starts to bite (English prose ~0.45-0.6 for
    # mid-length; heavy repetition drops well under 0.40).
    ttr_factor = 1.0
    if ttr < 0.42:
        ttr_factor = max(0.72, 0.72 + (ttr - 0.30) / (0.42 - 0.30) * 0.28)
    # Repetition: any echoed trigram is suspicious; 10%+ is heavy padding.
    rep_factor = 1.0 - min(0.30, repetition * 2.5)
    # Filler: each ~1 hit/100w shaves; cap the shave.
    fill_factor = 1.0 - min(0.25, filler_density * 0.06)

    factor = ttr_factor * rep_factor * fill_factor
    factor = round(max(0.55, min(1.0, factor)), 4)
    detail["factor"] = factor
    detail["ttr_factor"] = round(ttr_factor, 4)
    detail["rep_factor"] = round(rep_factor, 4)
    detail["fill_factor"] = round(fill_factor, 4)
    return (factor, detail)


# ================================================================
# QUALITY MODEL v2 -- THE 8 UBIQUITOUS-LANGUAGE DIMENSIONS
# Spec: SELF_IMPROVEMENT_FLYWHEEL_quality_model_v2.md Section 3
# ================================================================
#
# Each dimension is a FREE/INSTANT heuristic (regex / frontmatter / structure)
# scored 0-10 following the "Scored signal" column. No LLM, no byte-count
# climbing -- they reward the PRESENCE of purpose / open-vars / instructions /
# steps / canonical seed-words / 8F tags / pillar-fit / bootability surface.

# Canonical 8F verbs (D6). Match BECOME..COLLABORATE in any casing.
_8F_VERBS = {
    "constrain", "become", "inject", "reason",
    "produce", "govern", "collaborate", "call",
}
# Canonical pillar tokens (D7).
_PILLARS = {f"P{i:02d}" for i in range(1, 13)}


def _split_fm_body(content: str) -> tuple[str, str]:
    """Return (frontmatter, body). Empty frontmatter string if none."""
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return ("", content)
    return (m.group(1), content[m.end():])


def _fm_get(fm: str, field: str) -> str | None:
    """Read a scalar frontmatter field value (first line). None if absent."""
    m = re.search(r'^%s:\s*(.+)$' % re.escape(field), fm, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip().strip('"\'')


def _fm_has_block(fm: str, field: str) -> bool:
    """True if a frontmatter field exists as scalar OR block (list/map)."""
    return bool(re.search(r'^%s:' % re.escape(field), fm, re.MULTILINE))


def _d1_purpose(fm: str, body: str, title: str) -> float:
    """D1 PURPOSE -- one context = one intention. Explicit purpose +
    when/how/what + intention-revealing title. Baseline 3.0: any artifact with
    a body states *some* intention; the signals below earn it toward 10."""
    score = 3.0
    # Frontmatter intent fields (the Lovable intent surface, part 1).
    if _fm_has_block(fm, "tldr") or _fm_has_block(fm, "purpose") \
            or _fm_has_block(fm, "description") or _fm_has_block(fm, "role"):
        score += 1.5
    if _fm_has_block(fm, "when_to_use") or re.search(
            r'(?im)^#{1,3}.*(when to use|use cases?|not[- ]when|when not|applicability)', body):
        score += 1.5
    # Body purpose markers: overview / purpose / what-this-is.
    if re.search(r'(?im)^#{1,4}.*(overview|purpose|what (?:this|it) (?:is|does)'
                 r'|goal|objective|why|summary|context|mission|intro)', body):
        score += 1.0
    # A leading prose paragraph right after the H1 also reveals intent.
    elif re.search(r'(?ms)^#\s+.+?\n\n[A-Za-z].{40,}', body):
        score += 0.5
    # Intention-revealing title (a real title, not a bare id/slug).
    if title and len(title) >= 12 and " " in title:
        score += 1.5
    elif re.search(r'(?m)^#\s+\S+\s+\S+', body):  # multi-word H1 acts as title
        score += 0.5
    # axioms / scope make the intention crisp.
    if _fm_has_block(fm, "axioms") or _fm_has_block(fm, "scope") \
            or re.search(r'(?im)^#{1,4}.*(scope|axioms?|boundary)', body):
        score += 0.5
    # A single-context signal: not sprawling across too many H2 topics.
    h2 = len(re.findall(r'(?m)^##\s+', body))
    if 1 <= h2 <= 10:
        score += 1.0
    return min(10.0, score)


def _d2_ubiquitous_language(fm: str, body: str, kind: str | None) -> tuple[float, list[str]]:
    """D2 UBIQUITOUS-LANGUAGE -- canonical vocab; flag invented synonyms.
    Also scores the intent-resolution surface (keywords/long_tails/triggers)."""
    notes = []
    score = 2.0  # baseline: it speaks SOME structured language
    meta = _kinds_meta()
    text = (fm + "\n" + body)

    # (a) Kind is canonical (exists in the registry).
    if kind and kind in meta:
        score += 2.0
    elif kind:
        notes.append("non-canonical kind=%s" % kind)
        score += 0.5

    # (b) Uses canonical pillar + 8F verb tokens somewhere.
    if any(p in text for p in _PILLARS):
        score += 1.0
    tl = text.lower()
    if any(v in tl for v in _8F_VERBS):
        score += 1.0

    # (c) Intent-resolution surface -- the prompt compiler must be able to
    # RESOLVE to this artifact. keywords / long_tails / when_to_use / triggers.
    surface = 0
    for f in ("keywords", "long_tails", "when_to_use", "triggers",
              "trigger", "aliases", "tags", "tldr", "domain"):
        if _fm_has_block(fm, f):
            surface += 1
    score += min(3.0, surface * 0.8)
    if surface == 0:
        notes.append("no intent-resolution surface (keywords/long_tails/triggers)")

    # (d) Anti-synonym: penalize colloquial drift terms when canonical exists.
    drift = re.findall(r'(?i)\b(research card|intel doc|info sheet|spec sheet)\b', body)
    if drift:
        notes.append("drift synonyms: %s" % ",".join(sorted(set(d.lower() for d in drift))))
        score -= min(2.0, 0.7 * len(set(drift)))

    # (e) snake_case field discipline in frontmatter (canonical taxonomy).
    if re.search(r'(?m)^[a-z][a-z0-9_]*:', fm):
        score += 1.0

    return (max(0.0, min(10.0, score)), notes)


def _d3_open_variables(fm: str, body: str, kind: str | None) -> float:
    """D3 OPEN-VARIABLES -- intentional slots ({{var}} or schema) the consuming
    LLM fills at act-time. Dependency inversion / open boundaries; not a frozen
    blob. NOT every kind needs slots (a KC is a frozen fact) -- so kinds whose
    nature is static get partial credit for being appropriately closed."""
    score = 0.0
    # Explicit template slots.
    mustache = len(re.findall(r'\{\{[^}]+\}\}', body)) + len(re.findall(r'\{\{[^}]+\}\}', fm))
    angle = len(re.findall(r'<[A-Z][A-Z0-9_]{2,}>', body))
    if mustache >= 1:
        score += 4.0
    if mustache >= 3:
        score += 1.0
    if angle >= 1:
        score += 1.0
    # Schema / input-output contract = open boundary the caller fills.
    if re.search(r'(?im)^#{1,3}\s+(schema|input|output|parameters?|arguments?|fields?|inputs?|outputs?)', body):
        score += 2.0
    if re.search(r'(?im)^(input_schema|output_schema|parameters|args|slots|variables):', fm):
        score += 2.0
    # ```yaml/json fenced contract blocks signal a fillable structure.
    if re.search(r'```(?:yaml|json|ya?ml)', body):
        score += 1.0
    # Appropriately-closed kinds (static knowledge) get a floor so we don't
    # punish a well-formed frozen fact for lacking slots.
    meta = _kinds_meta()
    static_kinds = {"knowledge_card", "glossary_entry", "citation", "changelog",
                    "faq_entry", "context_doc", "decision_record", "lineage_record",
                    "axiom", "mental_model", "diagram", "competitive_matrix",
                    "dataset_card", "faq_entry", "report", "audit_log"}
    if kind in static_kinds:
        # Appropriately-closed: a frozen fact has no act-time slots BY NATURE.
        # Give a solid base so D3 does not define a KC's fitness; bonuses above
        # still let a KC that *does* expose structure climb higher.
        score = max(score, 5.0)
    else:
        # Other kinds: a small baseline so a thin-but-typed artifact is not 0.
        score = max(score, 2.5)
    return min(10.0, score)


def _d4_instructions(fm: str, body: str) -> float:
    """D4 INSTRUCTIONS -- carries usage instructions: how to ACT with/on this
    artifact (system-prompt / role framing / usage / how-it-works). Baseline
    2.5: most artifacts carry *some* guidance; explicit usage earns toward 10."""
    score = 2.5
    if re.search(r'(?im)^#{1,4}.*(usage|how to use|how it works|instructions?|'
                 r'getting started|quick ?start|setup|how to|guide|protocol)', body):
        score += 2.5
    if re.search(r'(?im)^#{1,4}.*(role|identity|you are|system prompt|persona|behavior|responsibilit)', body):
        score += 1.5
    if re.search(r'(?im)\byou (?:are|should|must|will|can|need to)\b', body):
        score += 1.0
    # Imperative guidance verbs at line starts (do this / use that).
    imp = len(re.findall(r'(?im)^\s*(?:-\s*)?(?:use|run|call|read|write|set|apply|invoke'
                         r'|load|configure|ensure|avoid|never|always|do|don.?t|check|verify'
                         r'|create|add|remove|update|follow)\b', body))
    score += min(2.0, imp * 0.4)
    # Frontmatter usage hints.
    if _fm_has_block(fm, "usage") or _fm_has_block(fm, "how_to_use") \
            or _fm_has_block(fm, "axioms") or _fm_has_block(fm, "instructions"):
        score += 1.0
    return min(10.0, score)


def _d5_procedure(fm: str, body: str) -> float:
    """D5 PROCEDURE -- step-by-step where it is an action/workflow; ordered,
    executable. Not every kind is procedural -- declarative kinds get a floor."""
    score = 0.0
    # Ordered numbered steps.
    numbered = len(re.findall(r'(?m)^\s*\d+[.)]\s+\S', body))
    if numbered >= 2:
        score += 3.0
    if numbered >= 4:
        score += 1.5
    # Explicit Step N / Stage N / Phase N markers.
    steps = len(re.findall(r'(?im)\b(?:step|stage|phase)\s+\d+\b', body))
    score += min(2.5, steps * 0.8)
    # Procedure / workflow / pipeline sections.
    if re.search(r'(?im)^#{1,3}\s+(procedure|steps?|workflow|process|pipeline|flow|sequence|algorithm)', body):
        score += 2.0
    # Pre/step/post or arrow flow (a -> b -> c).
    if re.search(r'->.*->', body) or re.search(r'(?im)^(pre|steps?|post|on_error|fallback):', fm):
        score += 1.0
    # A plain bulleted list also conveys some ordered structure.
    if re.search(r'(?m)^\s*[-*]\s+\S', body):
        score += 0.5
    # Declarative-kind floor: a schema/config is not a procedure; most artifacts
    # still convey *some* ordering. Give a reasonable base so non-workflow kinds
    # are not crushed on a dimension that does not define their fitness.
    score = max(score, 4.0)
    return min(10.0, score)


def _d6_8f_alignment(fm: str, body: str, kind: str | None) -> float:
    """D6 8F-ALIGNMENT -- declares which of the 8 verbs (CONSTRAIN..COLLABORATE)
    it serves. Registry-backed: a kind whose canonical llm_function appears is
    aligned; an explicit 8f/primary_8f/verb field is best."""
    score = 2.0  # baseline: a typed artifact serves *some* 8F verb implicitly
    text = (fm + "\n" + body)
    tl = text.lower()
    # Explicit 8F declaration in frontmatter.
    if re.search(r'(?im)^(8f|primary_8f|llm_function|verb|function):', fm):
        score += 3.0
    # Any canonical verb token present in the artifact.
    present = [v for v in _8F_VERBS if v in tl]
    score += min(3.0, len(present) * 1.0)
    # Registry agreement: the kind's canonical verb is actually mentioned.
    meta = _kinds_meta()
    if kind and kind in meta:
        canon = str(meta[kind].get("llm_function") or "").lower()
        prim = str(meta[kind].get("primary_8f") or "").lower()
        if canon and (canon in tl):
            score += 2.0
        elif prim and any(part in tl for part in prim.split("_")):
            score += 1.5
        else:
            score += 1.0  # canonical kind, verb implicit
    # F-step references (F1..F8) are a strong 8F-literacy signal.
    if re.search(r'\bF[1-8]\b', body):
        score += 1.0
    return min(10.0, score)


def _d7_pillar_fit(fm: str, body: str, kind: str | None, pillar: str | None) -> tuple[float, list[str]]:
    """D7 PILLAR-FIT -- correctly placed in its pillar AND embodies it (no
    leakage / dependency-rule respect). Registry-checked."""
    notes = []
    score = 0.0
    if pillar and pillar in _PILLARS:
        score += 3.0
    elif pillar:
        notes.append("non-canonical pillar=%s" % pillar)
    else:
        notes.append("no pillar")

    meta = _kinds_meta()
    if kind and kind in meta:
        canon_pillar = meta[kind].get("pillar")
        if pillar and canon_pillar and pillar == canon_pillar:
            score += 4.0  # declared pillar matches the registry's pillar
        elif pillar and canon_pillar and pillar != canon_pillar:
            notes.append("pillar %s != registry %s for kind=%s" % (pillar, canon_pillar, kind))
            score += 1.0
        else:
            score += 2.0
    else:
        # Unknown kind: credit a plausible pillar prefix in the id/name.
        idv = _fm_get(fm, "id") or ""
        if pillar and idv.lower().startswith(pillar.lower()):
            score += 2.0
        else:
            score += 1.0

    # Embodiment: artifact talks about its pillar domain (light signal).
    if pillar:
        score += 1.5
    return (max(0.0, min(10.0, score)), notes)


def _d8_bootability(content: str, fm: str, body: str) -> tuple[float, list[str]]:
    """D8 BOOTABILITY -- instantiable/executable as part of a runnable brain;
    wired (wikilinks + related resolve), has frontmatter, declares id/kind."""
    notes = []
    score = 0.0
    # Frontmatter present + parses minimal contract.
    if fm:
        score += 2.0
        if all(re.search(r'(?m)^%s:' % f, fm) for f in ("id", "kind")):
            score += 2.0
    else:
        notes.append("no frontmatter -> not bootable")

    # Wiring: a Related Artifacts section OR wikilinks OR a related: block.
    wikilinks = re.findall(r'\[\[([^\]]+)\]\]', content)
    has_related_section = bool(re.search(r'(?im)^#{1,3}\s+Related Artifacts', body))
    has_related_fm = _fm_has_block(fm, "related") or _fm_has_block(fm, "linked_artifacts")
    if wikilinks:
        score += 2.0
    if has_related_section or has_related_fm:
        score += 2.0
    if not (wikilinks or has_related_section or has_related_fm):
        notes.append("no wiring (wikilinks/related)")

    # Executable surface: code fence, command, or path reference -> runnable.
    if re.search(r'```', body) or re.search(r'(?m)^\s*(?:python|bash|\$|>)\s+\S', body) \
            or re.search(r'_tools/|\.cex/|N0[0-7]_', body):
        score += 2.0
    return (max(0.0, min(10.0, score)), notes)


# Per-dimension weights (sum = 1.0). PURPOSE + UL + BOOTABILITY carry the most
# weight (they encode reachability + well-formedness); PROCEDURE/OPEN-VARS are
# nature-dependent so weigh a touch less.
UL_DIM_WEIGHTS = {
    "D1_PURPOSE": 0.16,
    "D2_UBIQUITOUS_LANGUAGE": 0.18,
    "D3_OPEN_VARIABLES": 0.10,
    "D4_INSTRUCTIONS": 0.11,
    "D5_PROCEDURE": 0.10,
    "D6_8F_ALIGNMENT": 0.12,
    "D7_PILLAR_FIT": 0.13,
    "D8_BOOTABILITY": 0.10,
}


def score_ul_dimensions(path: str) -> tuple[float, dict, list[str]]:
    """Score the 8 ubiquitous-language dimensions (free/instant).

    Returns (weighted_score 0-10, per-dimension dict, notes).
    The per-dimension dict maps D1..D8 -> {"score": float, "weight": float}.
    """
    if not os.path.exists(path):
        return (0.0, {}, ["MISSING"])
    content = open(path, 'r', encoding='utf-8').read()
    fm, body = _split_fm_body(content)
    if not fm:
        # No frontmatter: only bootability can speak, and it says "not bootable".
        d8, n8 = _d8_bootability(content, fm, body)
        dims = {"D8_BOOTABILITY": {"score": round(d8, 1), "weight": UL_DIM_WEIGHTS["D8_BOOTABILITY"]}}
        return (round(d8 * UL_DIM_WEIGHTS["D8_BOOTABILITY"], 2), dims, ["NO_FRONTMATTER"] + n8)

    kind = _fm_get(fm, "kind")
    pillar = _fm_get(fm, "pillar")
    title = _fm_get(fm, "title") or ""

    notes = []
    d1 = _d1_purpose(fm, body, title)
    d2, n2 = _d2_ubiquitous_language(fm, body, kind)
    d3 = _d3_open_variables(fm, body, kind)
    d4 = _d4_instructions(fm, body)
    d5 = _d5_procedure(fm, body)
    d6 = _d6_8f_alignment(fm, body, kind)
    d7, n7 = _d7_pillar_fit(fm, body, kind, pillar)
    d8, n8 = _d8_bootability(content, fm, body)
    notes.extend(n2 + n7 + n8)

    raw = {
        "D1_PURPOSE": d1,
        "D2_UBIQUITOUS_LANGUAGE": d2,
        "D3_OPEN_VARIABLES": d3,
        "D4_INSTRUCTIONS": d4,
        "D5_PROCEDURE": d5,
        "D6_8F_ALIGNMENT": d6,
        "D7_PILLAR_FIT": d7,
        "D8_BOOTABILITY": d8,
    }
    dims = {k: {"score": round(v, 1), "weight": UL_DIM_WEIGHTS[k]} for k, v in raw.items()}
    weighted = sum(raw[k] * UL_DIM_WEIGHTS[k] for k in raw)
    return (round(min(10.0, weighted), 2), dims, notes)


def _weakest_ul_dimension(dims: dict) -> tuple[str, float]:
    """Return (dimension_name, score) of the lowest-scoring UL dimension."""
    if not dims:
        return ("", 10.0)
    name = min(dims, key=lambda k: dims[k]["score"])
    return (name, dims[name]["score"])


# ================================================================
# LAYER 3: SEMANTIC SCORER (LLM-based, 1 call per artifact)
# ================================================================

def score_semantic(path: str, structural: float, rubric_dims: list[dict]) -> tuple[float | None, dict, str]:
    """LLM-based semantic scoring via execute_prompt().
    Returns (score 0-10 | None, dimension_scores, reason).

    R-194 (honesty): score is None -- NEVER a fabricated neutral 7.0 -- when the
    LLM call fails (import/network/provider exception) or the response is not
    parseable JSON. A silently-defaulted 7.0 could previously be folded into
    score_hybrid()'s composite and, via --apply, written PERMANENTLY to an
    artifact's `quality:` frontmatter as if it were a real judgment. Callers
    (score_hybrid()) must treat None as "semantic scoring did not run" and
    exclude it from the composite, the same way they already treat a skipped
    L3 pass -- never as a passing 7.0.
    """
    content = open(path, 'r', encoding='utf-8').read()
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    fm = fm_match.group(1) if fm_match else ""
    kind_match = re.search(r'kind:\s*(\S+)', fm)
    kind = kind_match.group(1).strip().strip('"\'') if kind_match else "unknown"

    # Build dimension list for LLM
    dim_list = ""
    if rubric_dims:
        dim_list = "\n".join(
            f"  {d['id']}: {d['description']} (heuristic={d['score']}/10)"
            for d in rubric_dims
        )
    else:
        dim_list = """  S01: Factual concreteness -- specific values, numbers, verifiable facts
  S02: Atomicity -- covers one concept without scope creep
  S03: Searchability -- tags and tldr enable retrieval
  S04: Actionability -- reader knows what to DO after reading
  S05: Density -- no filler, no padding, every sentence earns its place
  S06: Domain expertise -- shows deep knowledge, not surface-level"""

    prompt = f"""You are a quality reviewer scoring a knowledge artifact (kind: {kind}).

## Artifact
```markdown
{content[:3000]}
```

## Dimensions to score (0-10 each)
{dim_list}

## Additional dimensions (always score these)
  ACTIONABILITY: Reader can immediately act on the content
  INSIGHT_DEPTH: Contains non-obvious insights, not just definitions
  COMPLETENESS: Covers the topic adequately for its scope

## Instructions
Score each dimension 0-10. Be STRICT:
- 10 = exceptional, publishable in a technical reference
- 8 = solid, useful, minor improvements possible  
- 6 = adequate but generic, could be better
- 4 = thin, mostly filler or surface-level
- 2 = poor, largely unhelpful

Return ONLY valid JSON (no markdown, no explanation):
{{
  "dimensions": {{
    "ACTIONABILITY": 7,
    "INSIGHT_DEPTH": 6,
    "COMPLETENESS": 8,
    ...
  }},
  "overall": 7.5,
  "weakest": "INSIGHT_DEPTH",
  "suggestion": "one specific improvement that would raise the weakest dimension"
}}"""

    try:
        # Import execute_prompt from cex_intent
        sys.path.insert(0, str(ROOT / "_tools"))
        from cex_intent import execute_prompt
        response = execute_prompt(prompt)

        # Parse JSON from response
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            data = json.loads(json_match.group())
            overall = float(data.get("overall", 7.0))
            dims = data.get("dimensions", {})
            weakest = data.get("weakest", "")
            suggestion = data.get("suggestion", "")
            reason = f"weakest={weakest}: {suggestion}" if weakest else ""
            return (round(overall, 1), dims, reason)
        else:
            # R-194: honest failure signal, not a fabricated 7.0.
            return (None, {}, f"LLM response not JSON: {response[:100]}")

    except Exception as e:
        # R-194: honest failure signal, not a fabricated 7.0.
        return (None, {}, f"semantic error: {str(e)[:100]}")


# ================================================================
# F7c HONESTY PASS -- adversarial weakest-dimension re-check
# Spec: 8f-reasoning.md F7c COUNCIL + quality_model_v2 Section 6
# ================================================================
#
# Triggered when the within-model score >= 9.0 (sycophancy heuristic). PROBES
# for a 2nd LLM provider; if none is healthy (founder on Claude Max => likely
# Claude-only) it DEGRADES to within-Claude adversarial multi-sample. It NEVER
# blocks on a missing provider -- it records what it used and returns a possibly
# down-adjusted score plus a divergence figure.

def probe_providers() -> list[str]:
    """Return the list of LLM providers that look healthy/available.

    Best-effort + offline-safe: reads .cex/config/nucleus_models.yaml and the
    quota cache if present; never raises. Claude is assumed available when an
    execute_prompt path exists. Used to decide cross-provider vs within-model.
    """
    providers = []
    # Claude path: if cex_intent.execute_prompt imports, Claude is reachable.
    try:
        sys.path.insert(0, str(ROOT / "_tools"))
        import importlib
        importlib.import_module("cex_intent")
        providers.append("claude")
    except Exception:
        pass
    # Other providers: look for explicit API keys in the environment only
    # (do NOT spend tokens probing). This keeps the probe free + deterministic.
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        providers.append("gemini")
    if os.environ.get("OPENAI_API_KEY"):
        providers.append("openai")
    # Codex/Ollama: treat as available only if explicitly flagged (offline).
    if os.environ.get("CEX_OLLAMA_AVAILABLE") == "1":
        providers.append("ollama")
    return providers


def honesty_pass(path: str, within_score: float, ul_dims: dict,
                 verbose: bool = False) -> dict:
    """Adversarial weakest-dimension skeptic for high scores (>= 9.0).

    R-195 (honesty): this pass is a FREE, deterministic, weakest-UL-dimension
    heuristic. It NEVER makes a live call to any LLM provider -- not a second
    provider, not even Claude again. probe_providers() only checks which
    provider API keys are PRESENT in the environment; that presence is
    recorded in `providers` for transparency, but it does not change what this
    function actually does (the adjustment math below is identical either
    way). A real cross-provider audit is a SEPARATE, opt-in mechanism (F7c
    COUNCIL / the cross_provider_council crew_template -- see
    .claude/rules/8f-reasoning.md) -- `mode` must never claim that mechanism
    ran when it did not; it was previously mislabeled "cross_provider" purely
    from env-var presence with zero provider calls made.

    Returns dict:
        {
          "triggered": bool,
          "providers": [..],          # provider keys DETECTED in env (informational
                                        # only -- presence, not a call made)
          "mode": "heuristic_only" | "skipped",   # what ACTUALLY ran; always the
                                        # free weakest-dim heuristic when triggered
          "consensus": float,         # adjusted/consensus score
          "divergence": float,        # stddev across samples (0 if 1 sample)
          "weakest": str,             # weakest UL dimension name
          "weakest_score": float,
          "dissent": [str],           # rationales
          "degraded": bool,           # True if no non-Claude provider key was
                                        # detected (informational; this pass never
                                        # calls any provider regardless of this flag)
        }
    """
    weakest, weakest_score = _weakest_ul_dimension(ul_dims)
    out = {
        "triggered": within_score >= 9.0,
        "providers": [],
        "mode": "skipped",
        "consensus": round(within_score, 2),
        "divergence": 0.0,
        "weakest": weakest,
        "weakest_score": round(weakest_score, 1),
        "dissent": [],
        "degraded": False,
    }
    if within_score < 9.0:
        return out

    providers = probe_providers()
    out["providers"] = providers
    multi = len([p for p in providers if p != "claude"]) >= 1

    # The skeptic's job: a >=9.0 grade must survive a weakest-dimension audit.
    # Heuristic-anchored adjustment (free, deterministic): if the weakest UL
    # dimension is itself weak, the honest score cannot legitimately be 9.0+.
    # This is the within-model adversary even when zero LLM providers answer.
    adjusted = within_score
    if weakest_score < 5.0:
        adjusted = min(adjusted, 8.5)
        out["dissent"].append(
            "weakest dimension %s=%.1f cannot support a 9.0+ grade" % (weakest, weakest_score)
        )
    elif weakest_score < 6.5:
        adjusted = min(adjusted, 8.9)
        out["dissent"].append(
            "weakest dimension %s=%.1f caps the honest grade below 9.0" % (weakest, weakest_score)
        )

    # R-195: `mode` reflects what ACTUALLY ran -- the free weakest-dimension
    # heuristic above, identically, regardless of which provider keys are
    # present. It must never read "cross_provider": no second-provider call is
    # ever made here. `multi` (provider keys detected) only changes the
    # divergence-cap formula below, not whether a live call happened.
    out["mode"] = "heuristic_only"
    if multi:
        # A 2nd provider key is present; we still anchor on the free
        # heuristic adversary here (a real cross-call is opt-in via evolve/F7c
        # crew). Record a small divergence proxy from the weakest gap.
        out["divergence"] = round(min(0.3, (within_score - adjusted) / 3.0), 3)
    else:
        out["degraded"] = True
        # Within-Claude multi-sample proxy: divergence ~ the size of the
        # weakest-dimension correction (kept under the 0.3 publish gate unless
        # the correction is large, which legitimately surfaces dissent).
        out["divergence"] = round((within_score - adjusted) / 3.0, 3)

    out["consensus"] = round(adjusted, 2)
    if verbose:
        print("  [F7c] honesty mode=%s providers=%s weakest=%s(%.1f) "
              "%.2f -> %.2f div=%.3f" % (
                  out["mode"], ",".join(providers) or "none", weakest,
                  weakest_score, within_score, adjusted, out["divergence"]))
    return out


# ================================================================
# CACHE -- by content hash (GDP D03)
# ================================================================

def _content_hash(path: str) -> str:
    """SHA256 of file content."""
    content = open(path, 'rb').read()
    return hashlib.sha256(content).hexdigest()[:16]


def _load_cache() -> dict:
    """Load score cache from disk."""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(cache: dict):
    """Save score cache to disk."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding='utf-8')


# ================================================================
# HYBRID SCORER -- combines all 3 layers
# ================================================================

def score_hybrid(path: str, use_cache: bool = True, force_semantic: bool = False,
                 verbose: bool = False, allow_semantic: bool = True) -> dict:
    """
    Quality Model v2 hybrid scoring. Returns dict with full breakdown.

    allow_semantic=False forces the FREE non-LLM branch (L1+L2+UL only): the
    semantic L3 call is skipped unconditionally even when avg_free >= 8.5. This
    is the guaranteed-zero-LLM path the overnight curate sweep uses to populate
    the score_cache cheaply (a weak artifact already skips L3, but allow_semantic
    makes "no token spend" provable for the whole sweep, not just the weak tail).

    Composite = (capped structural wiring + rubric hard-gates + the 8 UL
    dimensions [+ semantic when run]) MULTIPLIED by the anti-slop floor.
    Byte count alone cannot climb: structural contributes only frontmatter +
    wiring, and the anti-slop factor caps padded/repetitive artifacts.

    Returns (existing keys PRESERVED for cex_evolve / cex_doctor compatibility,
    plus new v2 keys):
        {
            "score": 8.7,             # final composite (honesty-adjusted)
            "structural": 8.5,        # layer 1 (legacy structural, unchanged)
            "rubric": 8.2,            # layer 2
            "semantic": 9.0,          # layer 3 (None if skipped)
            "dimensions": {...},      # merged rubric+semantic+UL breakdown
            "weakest": "...",         # weakest dimension (UL-aware)
            "suggestion": "...",      # how to improve weakest
            "mode": "hybrid",         # structural_only | hybrid | full
            "cached": False,
            "notes": [...],
            # --- NEW v2 keys ---
            "ul_score": 8.4,          # weighted 8-dimension UL score (pre-cap)
            "ul_dimensions": {...},   # D1..D8 -> {score, weight}
            "antislop_factor": 0.97,  # multiplicative cap in [0.55, 1.0]
            "antislop": {...},        # ttr / repetition / filler detail
            "honesty": {...},         # F7c adversarial pass result
            # --- R-173 key ---
            "gate_score_path": "legacy_prose",  # "declarative" | "legacy_prose"
                                       # -- which path scored the L2 gate;
                                       # see score_rubric_typed() docstring.
        }
    """
    path = str(path)
    if not os.path.exists(path):
        return {"score": 0.0, "structural": 0, "rubric": 0, "semantic": None,
                "dimensions": {}, "weakest": "", "suggestion": "",
                "mode": "error", "cached": False, "notes": ["MISSING"],
                "ul_score": 0.0, "ul_dimensions": {}, "antislop_factor": 1.0,
                "antislop": {}, "honesty": {"triggered": False, "mode": "skipped"},
                "gate_score_path": "legacy_prose"}

    # Check cache
    if use_cache:
        cache = _load_cache()
        h = _content_hash(path)
        cache_key = f"{path}:{h}"
        if cache_key in cache:
            cached = cache[cache_key]
            cached["cached"] = True
            if verbose:
                print(f"  [CACHE] {Path(path).name}: {cached['score']}")
            return cached

    content = open(path, 'r', encoding='utf-8').read()
    _fm, _body = _split_fm_body(content)

    # Layer 1: Structural (legacy -- preserved for the `structural` key + the
    # cheap pre-filter that decides whether the LLM layer runs). Its byte
    # rewards do NOT enter the composite directly (capped: see below).
    struct_raw, struct_notes = score_structural(path)
    structural = round(struct_raw, 2)
    if verbose:
        print(f"  [L1] structural(legacy): {structural}")

    # Capped structural contribution: frontmatter presence + wiring ONLY.
    # (Structural Score v2 binary checks, normalized; length cannot climb it.)
    sv2 = compute_structural_score(path, skip_compile=True)
    wiring_checks = ["frontmatter_valid", "wikilinks_resolve", "has_related",
                     "has_tags", "artifact_on_disk", "ascii_clean"]
    wiring_pass = sum(1 for c in wiring_checks if sv2["checks"].get(c))
    structural_capped = round(wiring_pass / len(wiring_checks) * 10.0, 2)

    # Layer 2: Rubric (always) -- hard gates + soft dims from the builder.
    # Two-path (R-173): score_rubric_typed() picks DECLARATIVE (cex_assertions,
    # when the resolved gate ships a sibling .assertions.yaml spec) or
    # LEGACY_PROSE (score_rubric(), unmodified -- true for every gate today).
    # gate_score_path is the honesty marker carried into the result below.
    rubric_typed = score_rubric_typed(path)
    rubric_raw = rubric_typed["score"]
    rubric_dims = rubric_typed["dimensions"]
    rubric_notes = rubric_typed["notes"]
    gate_score_path = rubric_typed["score_path"]
    rubric = round(rubric_raw, 2)
    if verbose:
        print(f"  [L2] rubric: {rubric} ({len(rubric_dims)} dims, path={gate_score_path})")

    # UL DIMENSIONS (always, free) -- the 8 ubiquitous-language dimensions.
    ul_score, ul_dims, ul_notes = score_ul_dimensions(path)
    if verbose:
        uw, uws = _weakest_ul_dimension(ul_dims)
        print(f"  [UL] ul_score: {ul_score} (weakest {uw}={uws})")

    # ANTI-SLOP FLOOR (always, free) -- multiplicative cap from prose.
    antislop_factor, antislop_detail = _antislop_factor(_body)
    if verbose:
        print(f"  [AS] antislop_factor: {antislop_factor} "
              f"(ttr={antislop_detail.get('type_token_ratio')} "
              f"rep={antislop_detail.get('repetition_ratio')} "
              f"fill={antislop_detail.get('filler_density')})")

    all_notes = struct_notes + rubric_notes + ul_notes

    # Layer 3: Semantic (only if free layers are strong OR forced).
    avg_free = (structural_capped + rubric + ul_score) / 3.0
    semantic = None
    sem_dims = {}
    sem_weakest = ""
    suggestion = ""

    if allow_semantic and (force_semantic or avg_free >= 8.5):
        skip_llm = False
        if not force_semantic and use_cache:
            cache = _load_cache()
            h = _content_hash(path)
            cache_key = f"{path}:{h}"
            if cache_key in cache and cache[cache_key].get("semantic") is not None:
                semantic_raw = cache[cache_key]["semantic"]
                sem_dims = cache[cache_key].get("dimensions", {})
                reason = "exact content-hash cache hit"
                skip_llm = True
                if verbose:
                    print("  [L3] semantic: CACHED (exact hash match)")

        if not skip_llm:
            if verbose:
                print(f"  [L3] semantic: calling LLM (avg_free={avg_free:.1f})...")
            semantic_raw, sem_dims, reason = score_semantic(path, structural, rubric_dims)

        if semantic_raw is None:
            # R-194: score_semantic() failed (exception or non-JSON LLM
            # response). NEVER fabricate a neutral 7.0 that could later be
            # written to `quality:` frontmatter via --apply -- surface the
            # failure honestly in notes and fall back to the SAME non-semantic
            # composite formula used when avg_free < 8.5. The failed attempt
            # is excluded from the composite entirely, not defaulted into it.
            semantic = None
            all_notes.append(f"semantic scoring failed: {reason}")
            if verbose:
                print(f"  [L3] semantic: FAILED ({reason[:60]}) -- excluded from composite")
            base = ul_score * 0.55 + rubric * 0.30 + structural_capped * 0.15
            mode = "hybrid_semantic_failed"
        else:
            semantic = round(semantic_raw, 2)
            if verbose:
                print(f"  [L3] semantic: {semantic} ({reason[:60]})")

            if sem_dims:
                wd = min(sem_dims.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 10)
                sem_weakest = wd[0]
            if "weakest=" in reason:
                parts = reason.split("weakest=", 1)
                if len(parts) > 1:
                    wr = parts[1]
                    if ":" in wr:
                        sem_weakest = wr.split(":")[0].strip()
                        suggestion = wr.split(":", 1)[1].strip()

            # v2 composite WITH semantic: UL leads (45%), rubric (25%),
            # semantic (20%), capped structural wiring (10%).
            base = (ul_score * 0.45 + rubric * 0.25 + semantic * 0.20
                    + structural_capped * 0.10)
            mode = "full"
    else:
        # v2 composite WITHOUT semantic: UL leads (55%), rubric (30%),
        # capped structural wiring (15%).
        base = ul_score * 0.55 + rubric * 0.30 + structural_capped * 0.15
        mode = "structural_only" if not rubric_dims else "hybrid"
        if verbose:
            print(f"  [L3] semantic: SKIPPED (avg_free={avg_free:.1f} < 8.5)")

    # Apply the anti-slop multiplicative cap. Padded/repetitive => lower.
    capped = base * antislop_factor
    within = round(min(capped, 10.0), 2)

    # Weakest dimension: prefer the UL weakest (drives Phase-1 enrichment).
    ul_weak, ul_weak_score = _weakest_ul_dimension(ul_dims)
    weakest = ul_weak or sem_weakest
    if ul_weak and not suggestion:
        suggestion = "raise %s (currently %.1f/10)" % (ul_weak, ul_weak_score)

    # F7c HONESTY PASS -- adversarial weakest-dimension re-check on >= 9.0.
    honesty = honesty_pass(path, within, ul_dims, verbose=verbose)
    final = round(min(honesty["consensus"] if honesty["triggered"] else within, 10.0), 1)

    # Merge dimension info (rubric + semantic + UL) for evolve's targeting.
    dimensions = {}
    for d in rubric_dims:
        dimensions[d["id"]] = {"description": d["description"], "heuristic": d["score"]}
    for k, v in sem_dims.items():
        if k in dimensions:
            dimensions[k]["semantic"] = v
        else:
            dimensions[k] = {"description": k, "semantic": v}
    for k, v in ul_dims.items():
        dimensions[k] = {"description": k, "ul": v["score"], "weight": v["weight"]}

    result = {
        "score": final,
        "structural": structural,
        "rubric": rubric,
        "semantic": semantic,
        "dimensions": dimensions,
        "weakest": weakest,
        "suggestion": suggestion,
        "mode": mode,
        "cached": False,
        "notes": all_notes,
        # --- v2 additions ---
        "ul_score": ul_score,
        "ul_dimensions": ul_dims,
        "structural_capped": structural_capped,
        "antislop_factor": antislop_factor,
        "antislop": antislop_detail,
        "honesty": honesty,
        # R-173 honesty marker: which path scored the L2 gate for this
        # artifact -- "declarative" (cex_assertions) or "legacy_prose"
        # (score_rubric(), unmodified). See score_rubric_typed() docstring.
        "gate_score_path": gate_score_path,
    }

    # Save to cache
    if use_cache:
        cache = _load_cache()
        h = _content_hash(path)
        cache[f"{path}:{h}"] = result
        _save_cache(cache)

    return result


# ================================================================
# BACKWARD COMPAT -- score_artifact() still works everywhere
# ================================================================

def score_artifact(path, hybrid: bool = False) -> tuple[float, str]:
    """Score a single artifact. Returns (score, notes).

    If hybrid=True, uses 3-layer scoring with LLM.
    If hybrid=False (default), uses fast structural-only scoring.
    This keeps backward compatibility with all existing callers.
    """
    if hybrid:
        result = score_hybrid(str(path))
        notes = "; ".join(result["notes"]) if result["notes"] else "OK"
        if result["weakest"]:
            notes += f" | weakest={result['weakest']}"
        if result["suggestion"]:
            notes += f" | fix={result['suggestion'][:80]}"
        return (result["score"], notes)
    else:
        # Fast structural-only path (original behavior)
        raw, notes = score_structural(str(path))
        if "MISSING" in notes:
            return (0.0, "MISSING")
        if "NO_FRONTMATTER" in notes:
            return (round(raw * 0.5, 1), "no frontmatter")
        score = round(raw, 1)
        return (score, "; ".join(notes) if notes else "OK")


def update_quality(path, score):
    """Replace quality: null or quality: X.X with quality: Y.Y in file."""
    content = open(path, 'r', encoding='utf-8').read()
    # Update both null and numeric quality values
    updated = re.sub(
        r'^quality:\s*(?:null|[\d.]+)\s*$',
        f'quality: {score}',
        content, count=1, flags=re.MULTILINE
    )
    if updated != content:
        open(path, 'w', encoding='utf-8').write(updated)
        return True
    return False


def _read_quality(path: str):
    """Read the quality field from a file's frontmatter.

    Returns:
        float if quality has a numeric value,
        None  if quality is null or missing,
        raises ValueError if file has no frontmatter.
    """
    content = open(path, 'r', encoding='utf-8').read()
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        raise ValueError(f"no frontmatter in {path}")
    fm = fm_match.group(1)
    # Check for quality: null (explicit null)
    if re.search(r'^quality:\s*null\s*$', fm, re.MULTILINE):
        return None
    # Check for quality: <number>
    num_match = re.search(r'^quality:\s*([\d.]+)\s*$', fm, re.MULTILINE)
    if num_match:
        return float(num_match.group(1))
    # quality field missing entirely
    return None


def apply_null_only(path: str, hybrid: bool = False, verbose: bool = False):
    """Score a file and write the result ONLY if quality is currently null/missing.

    If quality already has a numeric value, the file is skipped -- peer-reviewed
    scores are never overwritten.

    Args:
        path:    path to the .md artifact
        hybrid:  True = 3-layer (L1+L2+L3), False = L1+L2 only (default)
        verbose: print scoring details

    Returns:
        float  -- the score that was written
        None   -- if skipped (already scored) or error
    """
    path = str(path)
    if not os.path.exists(path):
        if verbose:
            print(f"  [SKIP] {path} -- file not found")
        return None

    # Check current quality
    try:
        current = _read_quality(path)
    except ValueError:
        if verbose:
            print(f"  [SKIP] {path} -- no frontmatter")
        return None

    if current is not None:
        if verbose:
            print(f"  [SKIP] {path} -- quality already {current}")
        return None

    # Compute score (L1 + L2, optionally L3)
    if hybrid:
        result = score_hybrid(path, verbose=verbose)
        score = result["score"]
    else:
        struct_raw, _ = score_structural(path)
        rubric_raw, _, _ = score_rubric(path)
        score = round((struct_raw * 0.5 + rubric_raw * 0.5), 1)
        score = min(score, 10.0)

    # Write back
    if update_quality(path, score):
        if verbose:
            print(f"  [APPLY] {path} -- quality: null -> {score}")
        return score

    # update_quality returned False -- quality field may be absent from file
    if verbose:
        print(f"  [SKIP] {path} -- quality field not found in frontmatter")
    return None


# ================================================================
# CLI
# ================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='CEX Hybrid Scorer')
    parser.add_argument('--dry-run', action='store_true', help='Score but do not update files')
    parser.add_argument('--apply', action='store_true', help='Apply scores to files')
    parser.add_argument('--hybrid', action='store_true', help='Use 3-layer hybrid scoring (includes LLM)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show scoring details')
    parser.add_argument('--no-cache', action='store_true', help='Skip score cache')
    parser.add_argument('--nucleus', type=str, help='Score only artifacts in N0X_*/ directory (e.g. n01)')
    parser.add_argument('--null-only', action='store_true', help='Skip artifacts that already have quality != null')
    parser.add_argument('--apply-null-only', action='store_true', help='Shorthand for --apply --null-only')
    parser.add_argument('--structural', action='store_true',
                        help='Compute 10-point binary structural score v2 (deterministic, zero LLM cost)')
    parser.add_argument('files', nargs='*', help='Files to score (default: all N0* artifacts)')
    args = parser.parse_args()

    if args.apply_null_only:
        args.apply = True
        args.null_only = True

    # --structural: 10-point binary structural score v2
    if args.structural:
        if not args.files:
            print("Usage: python _tools/cex_score.py --structural <file> [file2 ...]")
            sys.exit(1)
        for f in args.files:
            f = f.strip()
            if not f:
                continue
            result = compute_structural_score(f)
            print("Structural Score v2: %d/10" % result['total'])
            print("File: %s" % f)
            for check_name, passed in result['checks'].items():
                tag = "PASS" if passed else "FAIL"
                print("  [%s] %s" % (tag, check_name))
        return

    # Restrict to specific nucleus directory if --nucleus given
    if args.nucleus and not args.files:
        nuc = args.nucleus.lower().replace('n', 'n0') if not args.nucleus.lower().startswith('n0') else args.nucleus.lower()
        nuc_num = nuc.replace('n', '').replace('0', '', 1) if len(nuc) == 3 else nuc[-1]
        nuc_dirs = [d for d in os.listdir('.') if d.lower().startswith(f'n0{nuc_num}') and os.path.isdir(d)]
        if not nuc_dirs:
            print(f"No directory found for nucleus {args.nucleus}")
            return
        args.files = []
        for nd in nuc_dirs:
            for root_dir, _dirs, fnames in os.walk(nd):
                for fn in fnames:
                    if fn.endswith('.md'):
                        fpath = os.path.join(root_dir, fn)
                        try:
                            head = open(fpath, 'r', encoding='utf-8').read(2000)
                            if 'quality:' in head:
                                args.files.append(fpath)
                        except (OSError, UnicodeDecodeError):
                            pass
        args.files.sort()

    # Find files if none specified
    if not args.files:
        import subprocess
        targets = [d for d in os.listdir('.') if d.startswith('N0') and os.path.isdir(d)]
        if not targets:
            print("No nucleus directories found.")
            return
        result = subprocess.run(
            ['grep', '-r', '-l', r'^quality:', '--include=*.md'] + targets,
            capture_output=True, text=True,
            # R-331: same fix class as compute_structural_score's
            # git_committed check -- an explicit decode that never raises.
            encoding="utf-8", errors="replace",
        )
        args.files = sorted(set(result.stdout.strip().split('\n'))) if result.stdout.strip() else []

    # Filter to null-only if requested (frontmatter only)
    if args.null_only and args.files:
        filtered = []
        for f in args.files:
            try:
                content = open(f, 'r', encoding='utf-8').read()
                fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if fm_match:
                    fm = fm_match.group(1)
                    if re.search(r'^quality:\s*null\s*$', fm, re.MULTILINE):
                        filtered.append(f)
            except (OSError, UnicodeDecodeError):
                pass
        args.files = filtered

    if not args.files:
        print("No artifacts found.")
        return

    if args.hybrid:
        # Hybrid mode -- full 3-layer scoring
        print(f"{'Score':>5} | {'Str':>4} | {'Rub':>4} | {'Sem':>4} | {'Mode':<10} | {'Weakest':<20} | Path")
        print("-" * 110)

        scores = {}
        for f in args.files:
            f = f.strip()
            if not f:
                continue
            result = score_hybrid(f, use_cache=not args.no_cache, verbose=args.verbose)
            scores[f] = result
            sem_str = f"{result['semantic']:.1f}" if result['semantic'] else "skip"
            print(f"{result['score']:5.1f} | {result['structural']:4.1f} | {result['rubric']:4.1f} | "
                  f"{sem_str:>4} | {result['mode']:<10} | {result['weakest'][:20]:<20} | {f}")

            if args.apply:
                update_quality(f, result['score'])

        print(f"\n{'='*110}")
        all_scores = [r['score'] for r in scores.values()]
        print(f"Total: {len(scores)} artifacts")
        print(f"Avg: {sum(all_scores)/len(all_scores):.2f}")
        print(f"9.0+: {sum(1 for s in all_scores if s >= 9.0)}")
        print(f"8.5-8.9: {sum(1 for s in all_scores if 8.5 <= s < 9.0)}")
        print(f"<8.5: {sum(1 for s in all_scores if s < 8.5)}")

    else:
        # Classic mode -- structural only (fast)
        print(f"{'Score':>5} | {'Size':>6} | {'Notes':<40} | Path")
        print("-" * 100)

        scores = {}
        for f in args.files:
            f = f.strip()
            if not f:
                continue
            score, notes = score_artifact(f)
            scores[f] = score
            size = os.path.getsize(f) if os.path.exists(f) else 0
            print(f"{score:5.1f} | {size:5d}B | {notes:<40} | {f}")

        if not scores:
            return

        print(f"\n{'='*100}")
        print(f"Total: {len(scores)} artifacts")
        print(f"Avg score: {sum(scores.values())/len(scores):.1f}")
        print(f"Min: {min(scores.values()):.1f} | Max: {max(scores.values()):.1f}")
        print(f"9.0+: {sum(1 for s in scores.values() if s >= 9.0)}")
        print(f"8.5-8.9: {sum(1 for s in scores.values() if 8.5 <= s < 9.0)}")

        if args.apply:
            updated = 0
            for f, score in scores.items():
                if update_quality(f, score):
                    updated += 1
            print(f"\nApplied scores to {updated}/{len(scores)} files.")


if __name__ == '__main__':
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            main()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_score"))
    except ImportError:
        main()
