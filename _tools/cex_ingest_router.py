#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CEX Ingest Router -- source inspection + dispatch (INIT_ASSIMILATION_ENGINE Stage 1).

A user hands CEX a source (a repo, a URL/site, a PDF/office doc, a brandbook, or a
raw paste). This router INSPECTS the source, ROUTES it to the right EXISTING puller,
and NORMALIZES every source to ONE contract that the Stage 2 distill orchestrator
(cex_distill_orchestrator.py, N04) consumes directly:

    {source_id, uri, title, text, sha256, mime, license, source_type, provenance}

The top-level keys are exactly what cex_distill_orchestrator.load_sources_from_manifest
reads; source_type + provenance add the audit trail the spec Stage 1 contract names.

ROUTING (v1 repo/docs/brand + v2 social/cv graduated; media wired-by-contract to N01):
  repo        -> GitReverseSynthesizer (deep, opt-in) / offline local-repo walk (default)
  url/site    -> TieredFetcher (when a backend is present) / brand_ingest stdlib fetch
  doc/pdf/off -> document_loader adapter (markitdown -> pypdf/fitz/openpyxl -> zero-dep)
  brand       -> brand_ingest (folder/url/file signal extraction)
  paste       -> raw-text fallback (for robots/auth/paywall-blocked sources)
  social      -> cex_social_adapter (IG/LinkedIn/X export archives; live path creds-gated)
  cv          -> cex_cv_adapter (document_loader text + light CV-section structure)
  media       -> N01 cex_media_adapter.extract() by contract (degrades if not yet merged)

GATES (Gating Wrath -- fail-closed BEFORE any ingest):
  robots  -- RFC-9309 (reuses cexai.tools.ingestion.robots.RobotsTxt). Malformed or
             Disallow with no override blocks the source.
  license -- SPDX compatibility (reuses cexai.tools.reposynth.license_gate). An
             incompatible upstream repo license blocks the source.

OFFLINE-NEVER-CRASH (founder D3/D6): every adapter degrades gracefully with no API key
and no network. A source that cannot be read becomes a SKIPPED record with a clear
provenance note -- the router never raises on a bad source. Ingested content is LAB-ONLY.

Usage:
  # classify + normalize one or more sources into a distill-ready manifest
  python _tools/cex_ingest_router.py --source ./my_repo --source ./brandbook.pdf --out sources.json
  python _tools/cex_ingest_router.py --source https://example.com --out sources.json
  python _tools/cex_ingest_router.py --source ./logo.pdf --as brand --out sources.json
  python _tools/cex_ingest_router.py --paste "raw notes pasted by the user" --out sources.json
  echo "blocked-site text" | python _tools/cex_ingest_router.py --source - --out sources.json

  # offline self-test (no network, deterministic) -- gates + adapters + contract shape
  python _tools/cex_ingest_router.py --self-test

The manifest feeds Stage 2 directly:
  python _tools/cex_distill_orchestrator.py --brain demo --manifest sources.json --out OUT --execute
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

# --- reuse layer (degrade-never: every import is optional) -------------------
_THIS = Path(__file__).resolve()
_TOOLS = _THIS.parent
_ROOT = _TOOLS.parent
sys.path.insert(0, str(_TOOLS))
sys.path.insert(0, str(_ROOT / "cexai"))  # so `import cexai...` resolves

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from cex_shared import slugify as _slugify  # noqa: E402
except Exception:
    def _slugify(text: str) -> str:
        s = re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")
        return s or "source"

try:
    import brand_ingest as BRAND  # noqa: E402  (stdlib fetch + HTML text extractor + signal scan)
    _HAVE_BRAND = True
except Exception:
    BRAND = None
    _HAVE_BRAND = False

try:
    from cexai.tools.ingestion.robots import RobotsTxt  # noqa: E402
    _HAVE_ROBOTS = True
except Exception:
    RobotsTxt = None
    _HAVE_ROBOTS = False

try:
    from cexai.tools.reposynth.license_gate import (  # noqa: E402
        detect_license_spdx,
        has_license_file,
        is_compatible,
    )
    from cexai.tools._shared.types import RepoExtract  # noqa: E402
    _HAVE_LICENSE = True
except Exception:
    detect_license_spdx = has_license_file = is_compatible = None
    RepoExtract = None
    _HAVE_LICENSE = False

# v2 source adapters (INIT_V2_ADAPTERS). Safe to import at top-level: each adapter
# imports the router contract LAZILY (inside its functions), so there is no import
# cycle. Degrade-never: a missing adapter -> dispatch falls back to a clear record.
try:
    from cex_social_adapter import adapt_social as _adapt_social  # noqa: E402
    _HAVE_SOCIAL = True
except Exception:
    _adapt_social = None
    _HAVE_SOCIAL = False

try:
    from cex_cv_adapter import adapt_cv as _adapt_cv  # noqa: E402
    _HAVE_CV = True
except Exception:
    _adapt_cv = None
    _HAVE_CV = False

# --- constants --------------------------------------------------------------
TEXT_EXTS = {".txt", ".md", ".markdown", ".rst", ".csv", ".json", ".yaml", ".yml",
             ".toml", ".ini", ".cfg", ".log", ".tsv"}
DOC_EXTS = {".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls", ".rtf", ".odt", ".epub"}
OOXML_EXTS = {".docx", ".pptx", ".xlsx"}
REPO_MARKERS = (".git", "pyproject.toml", "package.json", "go.mod", "Cargo.toml",
                "pom.xml", "requirements.txt", "setup.py", ".gitignore")
DEFAULT_DOWNSTREAM_LICENSE = "Apache-2.0"   # CEX itself is Apache-2.0 (the user's own brain)
USER_AGENT = "cexai"
TYPE_PREFIXES = {"repo", "url", "doc", "brand", "paste", "social", "cv", "media"}

# Private-source credential registry (activates p09_sec_private_sources). Maps a
# secret_id -> the env var that unlocks it. NO value is ever stored here -- only the
# env var NAME. A REQUESTED private source whose env var is missing/empty is BLOCKED
# fail-closed by private_source_cred() (Gating Wrath: missing == disabled, never
# degraded-open to an unauthenticated fetch). Read-only scopes per the secret_config.
PRIVATE_SOURCE_CREDS = {
    "social": "SOCIAL_API_TOKEN",            # social ingest (own posts) -- live path
    "github": "GITHUB_PAT",                  # private-repo ingest (reposynth)
    "drive": "GOOGLE_DRIVE_OAUTH_TOKEN",     # company Drive ingest (readonly)
    "sheets": "GOOGLE_SHEETS_OAUTH_TOKEN",   # company Sheets ingest (readonly)
}
MIME_BY_EXT = {
    ".pdf": "application/pdf", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword", ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".md": "text/markdown", ".txt": "text/plain", ".html": "text/html", ".rtf": "application/rtf",
}
_RE_HTTP = re.compile(r"^https?://", re.I)
_RE_GH = re.compile(r"(github|gitlab|bitbucket)\.(com|org)/", re.I)
_RE_XMLTAG = re.compile(r"<[^>]+>")
_RE_PDF_STREAM = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.S)
_RE_PDF_SHOW = re.compile(rb"\(((?:[^()\\]|\\.)*)\)\s*Tj")
_RE_PDF_ARR = re.compile(rb"\[(.*?)\]\s*TJ", re.S)
_RE_PDF_ARRSTR = re.compile(rb"\(((?:[^()\\]|\\.)*)\)")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def _read_text(path: Path, max_bytes: int = 2_000_000) -> str:
    try:
        data = path.read_bytes()[:max_bytes]
        return data.decode("utf-8", errors="replace")
    except Exception:
        return ""


def private_source_cred(secret_id: str):
    """Resolve a private-source credential by id (p09_sec_private_sources gateway).

    Returns ``(ok, env_var, status)`` where ``ok`` is True ONLY when the mapped env
    var is present + non-empty (fail-closed). The credential VALUE is NEVER returned
    or logged (never_log_secrets / mask_in_errors): ``status`` is one of "present",
    "missing", or "unknown secret_id". A private source whose cred is absent must be
    BLOCKED by the caller, never silently degraded to an unauthenticated fetch."""
    env_var = PRIVATE_SOURCE_CREDS.get(secret_id, "")
    if not env_var:
        return False, secret_id, "unknown secret_id"
    val = os.environ.get(env_var, "")
    return (bool(val), env_var, "present" if val else "missing")


# ===========================================================================
# Normalized record (the Stage 1 -> Stage 2 contract, N04-manifest compatible)
# ===========================================================================

def make_record(source_id, source_type, uri, text, *, title="", mime="text/plain",
                license="unknown", adapter="", status="ok", notes="",
                robots="n/a", license_gate="n/a", extra=None) -> dict:
    """Build one normalized source record. Top-level keys feed N04's
    load_sources_from_manifest; provenance is the Stage-1 audit trail."""
    text = text or ""
    prov = {
        "adapter": adapter,
        "source_type": source_type,
        "uri": uri,
        "sha256": _sha256(text),
        "license": license,
        "robots": robots,
        "license_gate": license_gate,
        "bytes": len(text.encode("utf-8", errors="replace")),
        "retrieved_at": _now(),
        "status": status,
        "notes": notes,
    }
    if extra:
        prov.update(extra)
    return {
        "source_id": source_id,
        "source_type": source_type,
        "uri": uri,
        "title": title,
        "text": text,
        "sha256": prov["sha256"],
        "mime": mime,
        "license": license,
        "provenance": prov,
    }


# ===========================================================================
# Classification
# ===========================================================================

def split_type_prefix(s: str) -> tuple[str, str | None]:
    """Allow per-source typing via a `type:arg` prefix (e.g. `repo:./x`, `doc:./y`).
    A URL like `https://...` is safe because `https` is not a known type prefix."""
    if ":" in s:
        head, rest = s.split(":", 1)
        if head in TYPE_PREFIXES:
            return rest, head
    return s, None


def classify_source(arg: str, as_type: str | None) -> str:
    """Resolve a source arg to a source_type. --as overrides heuristics."""
    if as_type:
        return as_type
    if arg == "-":
        return "paste"
    if _RE_HTTP.match(arg):
        return "repo" if _RE_GH.search(arg) else "url"
    p = Path(arg)
    if p.is_dir():
        if any((p / m).exists() for m in REPO_MARKERS):
            return "repo"
        return "doc"   # a folder of files -> document set
    ext = p.suffix.lower()
    if ext in DOC_EXTS or ext in TEXT_EXTS:
        return "doc"   # a document extension signals doc even if not yet on disk
    if p.is_file():
        return "doc"
    # Not a path, not a URL -> treat as pasted literal text.
    return "paste"


# ===========================================================================
# GATES (fail-closed) -- robots (RFC 9309) + license (SPDX)
# ===========================================================================

def robots_decision(robots_text: str, path: str, ua: str = USER_AGENT):
    """Pure robots verdict over robots.txt body. Returns (allowed, status, note).
    Malformed body fails closed; a Disallow match blocks. Reuses cexai RobotsTxt."""
    if not robots_text.strip():
        return True, "allowed", "no robots rules (RFC 9309: absence = allow)"
    if not _HAVE_ROBOTS:
        # Minimal fallback: a blanket 'Disallow: /' for * blocks; else allow.
        low = robots_text.lower()
        if "disallow: /" in low and "user-agent: *" in low:
            return False, "blocked", "fallback: blanket disallow (cexai robots absent)"
        return True, "allowed", "fallback allow (cexai robots absent)"
    robots = RobotsTxt.parse(robots_text)
    if robots.malformed:
        return False, "malformed", "robots.txt malformed -> fail-closed"
    dec = robots.is_allowed(path or "/", user_agent=ua)
    if not dec.allowed:
        return False, "blocked", "disallow rule: %s" % (dec.rule or path)
    return True, "allowed", "allowed by robots"


def robots_gate(url: str):
    """Fetch + evaluate robots.txt for a URL. Returns (allowed, status, note).
    Unreachable/404 robots.txt = allow (RFC 9309). Network errors degrade to allow."""
    split = urlsplit(url)
    if not split.scheme or not split.netloc:
        return True, "n/a", "not an absolute http(s) URL"
    robots_url = "%s://%s/robots.txt" % (split.scheme, split.netloc)
    body = ""
    if _HAVE_BRAND:
        body = BRAND._fetch_url(robots_url) or ""
    if not body:
        return True, "allowed", "no reachable robots.txt (RFC 9309: allow)"
    path = split.path or "/"
    if split.query:
        path = "%s?%s" % (path, split.query)
    return robots_decision(body, path)


def repo_license_gate(repo_dir: Path, downstream: str = DEFAULT_DOWNSTREAM_LICENSE):
    """SPDX compatibility gate for a local repo. Returns (ok, spdx, status, note).
    Reuses cexai license_gate. No LICENSE = proceed-with-warning (matches reposynth
    E3); an incompatible LICENSE = fail-closed."""
    if not _HAVE_LICENSE:
        return True, None, "skipped", "license gate unavailable (cexai absent) -> proceed"
    entry_files: dict[str, str] = {}
    file_tree: list[str] = []
    try:
        for dp, dn, fn in os.walk(repo_dir):
            dn[:] = [d for d in dn if d not in (".git", "__pycache__", "node_modules")]
            for f in fn:
                rel = os.path.relpath(os.path.join(dp, f), repo_dir).replace("\\", "/")
                file_tree.append(rel)
                base = f.lower()
                if base.startswith(("license", "licence", "copying", "unlicense")):
                    entry_files[f] = _read_text(Path(dp) / f, 200_000)
    except Exception as exc:
        return True, None, "skipped", "license walk error: %s -> proceed" % type(exc).__name__
    try:
        extract = RepoExtract(
            source_url=repo_dir.as_posix(), tree_sha="local", default_branch="main",
            primary_language="", description="", file_tree=tuple(sorted(file_tree)),
            readme="", entry_files=entry_files, truncated=False)
        if not has_license_file(extract):
            return True, None, "unknown", "no LICENSE file -> derived_from_unlicensed_source"
        spdx = detect_license_spdx(extract)
        if spdx is None:
            return True, None, "unknown", "LICENSE present but unrecognized -> proceed (curate)"
        if not is_compatible(spdx, downstream):
            return False, spdx, "blocked", "incompatible: %s cannot flow into %s" % (spdx, downstream)
        return True, spdx, "ok", "compatible: %s -> %s" % (spdx, downstream)
    except Exception as exc:
        return True, None, "skipped", "license gate error: %s -> proceed" % type(exc).__name__


# ===========================================================================
# DOCUMENT TEXT EXTRACTION (deliverable #2) -- markitdown -> libs -> zero-dep
# ===========================================================================

def extract_document_text(path: Path):
    """Extract text from a PDF / office doc. Returns (text, method, note).
    Order: markitdown -> format libs (fitz/pypdf/openpyxl) -> zero-dep zip/PDF
    scraper. Every step is guarded; a fully unextractable file returns ("",...)."""
    ext = path.suffix.lower()
    if ext in TEXT_EXTS:
        return _read_text(path), "text_read", "plain text"

    # 1) markitdown (MCP/CLI) -- best general extractor when installed
    md = _try_markitdown(path)
    if md:
        return md, "markitdown", "markitdown CLI/module"

    # 2) format-specific
    if ext == ".pdf":
        for fn, name in ((_pdf_fitz, "pymupdf"), (_pdf_pypdf, "pypdf"), (_pdf_builtin, "builtin_pdf")):
            txt = fn(path)
            if txt and txt.strip():
                return txt, name, "pdf via %s" % name
        return "", "none", "pdf: no extractor produced text (install pymupdf or pypdf)"
    if ext == ".xlsx":
        txt = _xlsx_openpyxl(path) or _ooxml_text(path)
        return (txt, "xlsx", "xlsx") if txt else ("", "none", "xlsx: no text")
    if ext in OOXML_EXTS:           # docx / pptx (zero-dep zip+xml)
        txt = _ooxml_text(path)
        return (txt, "ooxml_zip", "ooxml zip+xml (zero-dep)") if txt else ("", "none", "ooxml: no text")
    if ext in (".doc", ".ppt", ".xls", ".rtf", ".odt", ".epub"):
        return "", "none", "%s needs markitdown/libreoffice (not installed) -> skipped" % ext

    # unknown binary -> best-effort decode
    raw = _read_text(path)
    return (raw, "raw_decode", "best-effort decode") if raw.strip() else ("", "none", "unreadable")


def _try_markitdown(path: Path) -> str:
    try:
        if shutil.which("markitdown"):
            r = subprocess.run(["markitdown", str(path)], capture_output=True,
                               text=True, timeout=60)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout
    except Exception:
        pass
    try:
        r = subprocess.run([sys.executable, "-m", "markitdown", str(path)],
                           capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    except Exception:
        pass
    return ""


def _pdf_fitz(path: Path) -> str:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(path))
        out = []
        for page in doc:
            out.append(page.get_text())
        doc.close()
        return "\n".join(out)
    except Exception:
        return ""


def _pdf_pypdf(path: Path) -> str:
    for mod in ("pypdf", "PyPDF2"):
        try:
            m = __import__(mod)
            reader = m.PdfReader(str(path))
            return "\n".join((pg.extract_text() or "") for pg in reader.pages)
        except Exception:
            continue
    return ""


def _pdf_builtin(path: Path) -> str:
    """Zero-dependency last resort: pull text-show operators out of PDF content
    streams (handles uncompressed + FlateDecode streams). Good enough for simple
    PDFs so extraction never hard-depends on a third-party library."""
    import zlib
    try:
        raw = path.read_bytes()
    except Exception:
        return ""
    pieces: list[str] = []
    for stream in _RE_PDF_STREAM.findall(raw):
        data = stream
        try:
            data = zlib.decompress(stream)
        except Exception:
            data = stream
        for m in _RE_PDF_SHOW.findall(data):
            pieces.append(_pdf_unescape(m))
        for arr in _RE_PDF_ARR.findall(data):
            for s in _RE_PDF_ARRSTR.findall(arr):
                pieces.append(_pdf_unescape(s))
    return " ".join(p for p in pieces if p).strip()


def _pdf_unescape(b: bytes) -> str:
    s = b.decode("latin-1", errors="replace")
    s = s.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
    s = s.replace("\\n", "\n").replace("\\r", "\n").replace("\\t", "\t")
    return s


def _ooxml_text(path: Path) -> str:
    """Zero-dep OOXML extraction: read the XML parts of a docx/pptx/xlsx zip and
    strip tags. Paragraph breaks (</w:p>, </a:p>, <row>) become newlines."""
    try:
        members_text: list[str] = []
        with zipfile.ZipFile(str(path)) as z:
            names = z.namelist()
            targets = [n for n in names if (
                n == "word/document.xml"
                or n.startswith("ppt/slides/slide")
                or n == "xl/sharedStrings.xml"
                or (n.startswith("word/") and n.endswith(".xml") and "document" in n)
            ) and n.endswith(".xml")]
            if not targets:  # generic fallback: any xml under the doc body dirs
                targets = [n for n in names if n.endswith(".xml") and (
                    n.startswith("word/") or n.startswith("ppt/") or n.startswith("xl/"))]
            for n in sorted(targets):
                try:
                    xml = z.read(n).decode("utf-8", errors="replace")
                except Exception:
                    continue
                xml = re.sub(r"</(w:p|a:p|row|w:tr)>", "\n", xml)
                txt = _RE_XMLTAG.sub(" ", xml)
                txt = _unescape_xml(txt)
                if txt.strip():
                    members_text.append(re.sub(r"[ \t]+", " ", txt).strip())
        return "\n".join(members_text).strip()
    except Exception:
        return ""


def _xlsx_openpyxl(path: Path) -> str:
    try:
        import openpyxl
        wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
        out = []
        for ws in wb.worksheets:
            out.append("# sheet: %s" % ws.title)
            for row in ws.iter_rows(values_only=True):
                cells = [str(c) for c in row if c is not None]
                if cells:
                    out.append(" | ".join(cells))
        wb.close()
        return "\n".join(out)
    except Exception:
        return ""


def _unescape_xml(s: str) -> str:
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&apos;", "'").replace("&#160;", " "))


# ===========================================================================
# ADAPTERS -- one per source_type, all returning a normalized record
# ===========================================================================

def adapt_doc(arg: str, sid: str) -> dict:
    """File or folder of documents -> normalized text via document_loader adapter."""
    p = Path(arg)
    if p.is_dir():
        parts, names = [], []
        for dp, dn, fn in os.walk(p):
            dn[:] = [d for d in dn if not d.startswith(".") and d != "__pycache__"]
            for f in sorted(fn):
                fp = Path(dp) / f
                if fp.suffix.lower() in (DOC_EXTS | TEXT_EXTS):
                    txt, method, _ = extract_document_text(fp)
                    if txt.strip():
                        parts.append("## %s\n%s" % (f, txt))
                        names.append(f)
        text = "\n\n".join(parts)
        note = "folder: %d readable doc(s): %s" % (len(names), ", ".join(names[:8]) or "none")
        return make_record(sid, "doc", p.as_posix(), text, title=p.name,
                           mime="inode/directory", adapter="document_loader",
                           status="ok" if text.strip() else "empty", notes=note)
    if not p.is_file():
        return make_record(sid, "doc", arg, "", adapter="document_loader",
                           status="empty", notes="path not found")
    text, method, note = extract_document_text(p)
    mime = MIME_BY_EXT.get(p.suffix.lower(), "application/octet-stream")
    return make_record(sid, "doc", p.as_posix(), text, title=p.name, mime=mime,
                       adapter="document_loader:%s" % method,
                       status="ok" if text.strip() else "empty", notes=note,
                       extra={"extract_method": method})


def adapt_url(arg: str, sid: str) -> dict:
    """URL/site -> robots gate -> stdlib HTML text extraction (brand_ingest)."""
    allowed, rstatus, rnote = robots_gate(arg)
    if not allowed:
        return make_record(sid, "url", arg, "", adapter="web_fetch", status="blocked",
                           robots=rstatus, notes="robots gate: %s" % rnote)
    text = ""
    if _HAVE_BRAND:
        html = BRAND._fetch_url(arg) or ""
        if html:
            try:
                ex = BRAND._TextExtractor()
                ex.feed(html)
                text = ex.get_text()
            except Exception:
                text = re.sub(r"<[^>]+>", " ", html)
    note = "fetched + html-stripped" if text.strip() else "no content (JS-rendered or blocked)"
    return make_record(sid, "url", arg, text, title=arg, mime="text/html",
                       adapter="web_fetch", robots=rstatus,
                       status="ok" if text.strip() else "empty",
                       notes="robots %s; %s" % (rstatus, note))


def adapt_repo(arg: str, sid: str) -> dict:
    """Repo -> license gate -> offline local walk (default) or remote README fetch.
    Deep reposynth (GitReverseSynthesizer, LLM) is the opt-in path, noted but not
    auto-run offline."""
    if _RE_HTTP.match(arg):              # remote repo URL
        text, lic, lstatus, lnote = _repo_remote(arg)
        return make_record(sid, "repo", arg, text, title=arg, mime="text/markdown",
                           adapter="repo_remote", license=lic or "unknown",
                           license_gate=lstatus,
                           status="ok" if text.strip() else "empty",
                           notes="remote repo; license %s (%s); deep reposynth=opt-in" % (lstatus, lnote))
    p = Path(arg)
    if not p.is_dir():
        return make_record(sid, "repo", arg, "", adapter="repo_local",
                           status="empty", notes="repo path not found")
    ok, spdx, lstatus, lnote = repo_license_gate(p)
    if not ok:
        return make_record(sid, "repo", p.as_posix(), "", adapter="repo_local",
                           license=spdx or "unknown", license_gate=lstatus,
                           status="blocked", notes="license gate: %s" % lnote)
    text = _repo_local_text(p)
    return make_record(sid, "repo", p.as_posix(), text, title=p.name, mime="text/markdown",
                       adapter="repo_local", license=spdx or "unknown", license_gate=lstatus,
                       status="ok" if text.strip() else "empty",
                       notes="local repo walk; license %s (%s); deep reposynth=opt-in" % (lstatus, lnote))


def _repo_local_text(repo_dir: Path, max_files: int = 40, budget: int = 400_000) -> str:
    """Offline repo summary: README + a file-tree outline + top text/code files."""
    parts: list[str] = []
    readme = ""
    for cand in ("README.md", "README.rst", "README.txt", "readme.md"):
        fp = repo_dir / cand
        if fp.exists():
            readme = _read_text(fp, 60_000)
            break
    if readme:
        parts.append("# README\n" + readme)
    tree = []
    picked = 0
    body = []
    for dp, dn, fn in os.walk(repo_dir):
        dn[:] = [d for d in dn if d not in (".git", "__pycache__", "node_modules", ".venv")]
        for f in sorted(fn):
            rel = os.path.relpath(os.path.join(dp, f), repo_dir).replace("\\", "/")
            tree.append(rel)
            ext = Path(f).suffix.lower()
            if picked < max_files and ext in (TEXT_EXTS | {".py", ".js", ".ts", ".go", ".rs", ".java"}):
                if f.lower().startswith("readme"):
                    continue
                txt = _read_text(Path(dp) / f, 12_000)
                if txt.strip():
                    body.append("## %s\n%s" % (rel, txt))
                    picked += 1
    parts.append("# File Tree (%d files)\n%s" % (len(tree), "\n".join(tree[:300])))
    parts.extend(body)
    out = "\n\n".join(parts)
    return out[:budget]


def _repo_remote(url: str):
    """Remote repo: fetch README + LICENSE via raw host. Returns (text, spdx, status, note)."""
    if not _HAVE_BRAND:
        return "", None, "skipped", "no fetch backend"
    m = re.search(r"github\.com/([^/]+)/([^/?#\s]+)", url)
    if not m:
        return "", None, "skipped", "non-github remote (deep reposynth handles offline)"
    owner, repo = m.group(1), m.group(2).rstrip("/").removesuffix(".git")
    text_parts, lic_text = [], ""
    for branch in ("main", "master"):
        base = "https://raw.githubusercontent.com/%s/%s/%s" % (owner, repo, branch)
        readme = BRAND._fetch_url("%s/README.md" % base) or ""
        if readme:
            text_parts.append("# README\n" + readme[:60_000])
        for lf in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
            t = BRAND._fetch_url("%s/%s" % (base, lf)) or ""
            if t:
                lic_text = t
                break
        if text_parts:
            break
    spdx, lstatus, lnote = None, "unknown", "no LICENSE fetched"
    if lic_text and _HAVE_LICENSE:
        try:
            ext = RepoExtract(source_url=url, tree_sha="remote", default_branch="main",
                              primary_language="", description="", file_tree=("LICENSE",),
                              readme="", entry_files={"LICENSE": lic_text}, truncated=False)
            spdx = detect_license_spdx(ext)
            if spdx and not is_compatible(spdx, DEFAULT_DOWNSTREAM_LICENSE):
                return "", spdx, "blocked", "incompatible %s -> %s" % (spdx, DEFAULT_DOWNSTREAM_LICENSE)
            lstatus = "ok" if spdx else "unknown"
            lnote = ("compatible %s" % spdx) if spdx else "LICENSE unrecognized"
        except Exception:
            pass
    return "\n\n".join(text_parts), spdx, lstatus, lnote


def adapt_brand(arg: str, sid: str) -> dict:
    """Brand signals -> brand_ingest (folder / url / file) -> LLM-ready brief."""
    if not _HAVE_BRAND:
        return make_record(sid, "brand", arg, "", adapter="brand_ingest",
                           status="empty", notes="brand_ingest unavailable")
    try:
        if _RE_HTTP.match(arg):
            signals = BRAND.ingest_url(arg)
        elif Path(arg).is_dir():
            signals = BRAND.ingest(Path(arg))
        elif Path(arg).is_file():
            signals = BRAND.ingest_file(arg)
        else:
            return make_record(sid, "brand", arg, "", adapter="brand_ingest",
                               status="empty", notes="brand source not found")
        text = BRAND.format_for_llm(signals)
    except Exception as exc:
        return make_record(sid, "brand", arg, "", adapter="brand_ingest",
                           status="empty", notes="brand_ingest error: %s" % type(exc).__name__)
    return make_record(sid, "brand", arg, text, title="brand:%s" % arg, mime="text/markdown",
                       adapter="brand_ingest", status="ok" if text.strip() else "empty",
                       notes="brand signals extracted")


def adapt_paste(text: str, sid: str, uri: str = "paste://stdin") -> dict:
    """Raw pasted text -> normalized contract. The fallback when crawl/fetch is
    blocked by robots / auth / paywall."""
    return make_record(sid, "paste", uri, text or "", title="pasted", mime="text/plain",
                       adapter="paste", status="ok" if (text or "").strip() else "empty",
                       notes="raw paste fallback (robots/auth/paywall bypass)")


def adapt_stub(arg: str, sid: str, stype: str) -> dict:
    """Fallback stub for a not-yet-available adapter (e.g. media before N01 merges).
    Clear provenance: a stub record is `skipped`, never silently dropped."""
    return make_record(sid, stype, arg, "", adapter="stub", status="stub",
                       notes="%s adapter pending -- router stub (clear provenance)" % stype)


def dispatch_social(arg: str, sid: str) -> dict:
    """social: -> cex_social_adapter (export-first; live path creds-gated). Degrade to
    a clear record if the adapter module is unavailable or raises (never crash)."""
    if _HAVE_SOCIAL and _adapt_social is not None:
        try:
            return _adapt_social(arg, sid)
        except Exception as exc:
            return make_record(sid, "social", arg, "", adapter="social", status="empty",
                               notes="social adapter error: %s -> skipped" % type(exc).__name__,
                               extra={"untrusted": True})
    return make_record(sid, "social", arg, "", adapter="social", status="empty",
                       notes="cex_social_adapter unavailable -> skipped",
                       extra={"untrusted": True})


def dispatch_cv(arg: str, sid: str) -> dict:
    """cv: -> cex_cv_adapter (document_loader text + CV-section structure). Degrade-never."""
    if _HAVE_CV and _adapt_cv is not None:
        try:
            return _adapt_cv(arg, sid)
        except Exception as exc:
            return make_record(sid, "cv", arg, "", adapter="cv", status="empty",
                               notes="cv adapter error: %s -> skipped" % type(exc).__name__,
                               extra={"untrusted": True})
    return make_record(sid, "cv", arg, "", adapter="cv", status="empty",
                       notes="cex_cv_adapter unavailable -> skipped",
                       extra={"untrusted": True})


def dispatch_media(arg: str, sid: str) -> dict:
    """media: -> N01 cex_media_adapter.extract() BY CONTRACT.

    N01 lands cex_media_adapter this same wave; until it merges (or if the call shape
    differs) this degrades to a clear 'media adapter pending' record -- never a crash
    (Gating Wrath degrade-never). Expected N01 contract:
        cex_media_adapter.extract(arg, sid) -> a normalized p06_is_ingest_intake record.
    A str return is wrapped into a record; a signature mismatch falls back to
    extract(arg); an unrecognized shape becomes an empty record."""
    try:
        import cex_media_adapter as MEDIA  # N01 owns this module (this wave)
    except Exception:
        return adapt_stub(arg, sid, "media")  # pending until N01 merges
    extract = getattr(MEDIA, "extract", None)
    if extract is None:
        return make_record(sid, "media", arg, "", adapter="media", status="stub",
                           notes="cex_media_adapter present but exposes no extract() -> pending")
    # N01 contract: extract(path_or_uri, source_id=..., **opts) -> [record]. Try that
    # first; fall back through positional/bare signatures for any other adapter shape.
    result = None
    for call in (lambda: extract(arg, source_id=sid),
                 lambda: extract(arg, sid),
                 lambda: extract(arg)):
        try:
            result = call()
            break
        except TypeError:
            continue
        except Exception as exc:
            return make_record(sid, "media", arg, "", adapter="media", status="empty",
                               notes="media extract error: %s -> skipped" % type(exc).__name__)
    if result is None:
        return make_record(sid, "media", arg, "", adapter="media", status="empty",
                           notes="media adapter signature not callable by contract -> skipped")
    return _normalize_media_result(result, arg, sid)


def _normalize_media_result(result, arg: str, sid: str) -> dict:
    """Coerce N01's return into the manifest contract. N01's extract() returns a LIST
    of records (one per media source); take the first well-formed one. Also tolerates a
    bare record dict or raw text from any other adapter shape (degrade-never)."""
    required = {"source_id", "source_type", "uri", "text", "provenance"}
    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict) and required.issubset(set(item.keys())):
                return item
        return make_record(sid, "media", arg, "", adapter="cex_media_adapter", status="empty",
                           notes="media adapter returned an empty/unrecognized list -> skipped",
                           extra={"untrusted": True})
    if isinstance(result, dict) and required.issubset(set(result.keys())):
        return result
    if isinstance(result, str):
        return make_record(sid, "media", arg, result, adapter="cex_media_adapter",
                           status="ok" if result.strip() else "empty",
                           notes="media text via N01 cex_media_adapter",
                           extra={"untrusted": True})
    return make_record(sid, "media", arg, "", adapter="cex_media_adapter", status="empty",
                       notes="media adapter returned an unrecognized shape -> skipped",
                       extra={"untrusted": True})


# ===========================================================================
# Orchestration
# ===========================================================================

def route_one(arg: str, as_type: str | None, paste_text: str | None, seen: set) -> dict:
    stype = classify_source(arg, as_type)
    base = _slugify(Path(arg).stem if (not _RE_HTTP.match(arg) and arg != "-") else
                    re.sub(r"^https?://", "", arg)) or stype
    sid = base
    n = 1
    while sid in seen:
        n += 1
        sid = "%s_%d" % (base, n)
    seen.add(sid)

    if stype == "social":
        return dispatch_social(arg, sid)
    if stype == "cv":
        return dispatch_cv(arg, sid)
    if stype == "media":
        return dispatch_media(arg, sid)
    if stype == "paste":
        if arg == "-" and paste_text is None:
            paste_text = sys.stdin.read()
        return adapt_paste(paste_text if paste_text is not None else arg, sid,
                           uri="paste://stdin" if arg == "-" else "paste://arg")
    if stype == "repo":
        return adapt_repo(arg, sid)
    if stype == "url":
        return adapt_url(arg, sid)
    if stype == "brand":
        return adapt_brand(arg, sid)
    return adapt_doc(arg, sid)


def run(args) -> int:
    sources_in: list[tuple[str, str | None, str | None]] = []
    if args.paste is not None:
        sources_in.append(("paste://arg", "paste", args.paste))
    if args.paste_file:
        sources_in.append((args.paste_file, "paste", _read_text(Path(args.paste_file))))
    for s in (args.source or []):
        arg, ptype = split_type_prefix(s)
        sources_in.append((arg, ptype or args.as_type, None))
    if not sources_in:
        print("[FAIL] no --source / --paste / --paste-file given", file=sys.stderr)
        return 2

    seen: set = set()
    ok_records, skipped = [], []
    print("=== INGEST ROUTER (Stage 1: INGEST) ===", file=sys.stderr)
    print("F1 CONSTRAIN: %d source(s); downstream_license=%s; offline=%s" % (
        len(sources_in), DEFAULT_DOWNSTREAM_LICENSE,
        "yes" if not os.environ.get("FIRECRAWL_API_KEY") else "firecrawl-on"), file=sys.stderr)
    print("F2 BECOME:    N05 Operations -- Gating Wrath (robots=%s license=%s)" % (
        "cexai" if _HAVE_ROBOTS else "fallback", "cexai" if _HAVE_LICENSE else "off"), file=sys.stderr)

    for arg, as_type, paste_text in sources_in:
        rec = route_one(arg, as_type, paste_text, seen)
        st = rec["provenance"]["status"]
        line = "  [%-7s] %-6s %s -> %s" % (
            st, rec["source_type"], (arg[:48] + "...") if len(arg) > 48 else arg,
            rec["provenance"]["notes"][:60])
        print(line, file=sys.stderr)
        if st == "ok":
            ok_records.append(rec)
        else:
            skipped.append(rec)

    manifest = {
        "schema": "cex_ingest_manifest_v1",
        "contract": "p06_is_ingest_intake",
        "generated_by": "cex_ingest_router.py",
        "generated_at": _now(),
        "privacy": "lab_only",
        "count_ok": len(ok_records),
        "count_skipped": len(skipped),
        "sources": ok_records,
        "skipped": skipped,
    }
    print("F7 GOVERN:    ok=%d skipped=%d (gates fail-closed)" % (len(ok_records), len(skipped)),
          file=sys.stderr)

    payload = json.dumps(manifest, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print("F8 COLLAB:    manifest -> %s (feed N04: --manifest %s)" % (args.out, args.out),
              file=sys.stderr)
    else:
        print(payload)
    return 0


# ===========================================================================
# Self-test (offline, deterministic) -- gates + adapters + contract shape
# ===========================================================================

def self_test() -> int:
    import tempfile
    passed, failed = 0, 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print("  [OK]   %s" % name)
        else:
            failed += 1
            print("  [FAIL] %s" % name)

    print("=== cex_ingest_router self-test (offline) ===")
    print("-- reuse anchors --")
    check("cexai robots importable", _HAVE_ROBOTS)
    check("cexai license_gate importable", _HAVE_LICENSE)
    check("brand_ingest importable", _HAVE_BRAND)

    print("-- classification --")
    check("github URL -> repo", classify_source("https://github.com/a/b", None) == "repo")
    check("plain URL -> url", classify_source("https://example.com", None) == "url")
    check("pdf path -> doc", classify_source("x.pdf", None) == "doc")
    check("--as brand override", classify_source("anything", "brand") == "brand")
    check("--as social -> stub type", classify_source("x", "social") == "social")
    check("prefix repo:./x parsed", split_type_prefix("repo:./x") == ("./x", "repo"))
    check("prefix leaves URL intact", split_type_prefix("https://e.com") == ("https://e.com", None))

    print("-- robots gate (fail-closed) --")
    a1, s1, _ = robots_decision("User-agent: *\nDisallow: /", "/secret")
    check("blanket disallow blocks", (a1 is False and s1 == "blocked"))
    a2, s2, _ = robots_decision("<html>captcha</html>", "/x")
    check("malformed robots fails closed", (a2 is False and s2 == "malformed"))
    a3, _, _ = robots_decision("User-agent: *\nDisallow: /private", "/public")
    check("allowed path passes", a3 is True)
    a4, _, _ = robots_decision("", "/x")
    check("empty robots = allow", a4 is True)

    print("-- license gate (fail-closed) --")
    if _HAVE_LICENSE:
        check("GPL-3.0 -> MIT incompatible", is_compatible("GPL-3.0", "MIT") is False)
        check("MIT -> MIT compatible", is_compatible("MIT", "MIT") is True)
        check("Apache-2.0 -> MIT compatible", is_compatible("Apache-2.0", "MIT") is True)

    tmp = Path(tempfile.mkdtemp(prefix="ingest_selftest_"))
    try:
        print("-- document extraction --")
        f = tmp / "note.md"
        f.write_text("# Title\nbody text for distill", encoding="utf-8")
        txt, method, _ = extract_document_text(f)
        check("markdown text extracted", "body text" in txt)

        xlsx = tmp / "data.xlsx"
        _write_min_xlsx(xlsx, ["alpha", "beta", "gamma"])
        xtxt, _, _ = extract_document_text(xlsx)
        check("xlsx text extracted", ("alpha" in xtxt or "beta" in xtxt))

        pdf = tmp / "doc.pdf"
        _write_min_pdf(pdf, "CEX assimilation smoke PDF body")
        ptxt, pm, _ = extract_document_text(pdf)
        check("pdf text extracted", "assimilation" in ptxt.lower())

        print("-- local repo license gate (incompatible) --")
        repo = tmp / "gpl_repo"
        repo.mkdir()
        (repo / "README.md").write_text("# proj", encoding="utf-8")
        (repo / ".gitignore").write_text("*.pyc", encoding="utf-8")
        (repo / "LICENSE").write_text(
            "GNU GENERAL PUBLIC LICENSE\nVersion 3, 29 June 2007", encoding="utf-8")
        rec_repo = adapt_repo(str(repo), "gpl_repo")
        check("GPL local repo blocked", rec_repo["provenance"]["status"] == "blocked")

        repo2 = tmp / "mit_repo"
        repo2.mkdir()
        (repo2 / "README.md").write_text("# proj two\nhello", encoding="utf-8")
        (repo2 / "pyproject.toml").write_text("[project]\nname='x'", encoding="utf-8")
        (repo2 / "LICENSE").write_text(
            "MIT License\nPermission is hereby granted, free of charge", encoding="utf-8")
        rec_repo2 = adapt_repo(str(repo2), "mit_repo")
        check("MIT local repo ok", rec_repo2["provenance"]["status"] == "ok")
        check("repo classified as repo", classify_source(str(repo2), None) == "repo")

        print("-- paste + stub + contract shape --")
        rp = adapt_paste("pasted notes", "p1")
        check("paste record ok", rp["provenance"]["status"] == "ok" and rp["text"] == "pasted notes")
        rs = adapt_stub("clip.mp4", "s1", "media")
        check("media stub marked", rs["provenance"]["status"] == "stub")

        required = {"source_id", "uri", "title", "text", "sha256", "mime", "license", "source_type", "provenance"}
        check("record has N04-contract keys", required.issubset(set(rec_repo2.keys())))
        check("sha256 recomputed correctly", rec_repo2["sha256"] == _sha256(rec_repo2["text"]))

        print("-- v2 adapters: social/cv dispatch + private-source creds (wiring) --")
        ig_zip = tmp / "ig.zip"
        with zipfile.ZipFile(str(ig_zip), "w") as z:
            z.writestr("content/posts_1.json",
                       json.dumps({"posts": [{"media": [{"title": "router social hello"}]}]}))
        rec_soc = route_one(str(ig_zip), "social", None, set())
        check("social dispatched (ok)", rec_soc["provenance"]["status"] == "ok"
              and "router social hello" in rec_soc["text"])
        check("social tagged untrusted", rec_soc["provenance"].get("untrusted") is True)

        cvf = tmp / "cv.txt"
        cvf.write_text("Summary\nHi there\n\nSkills\nPython, RAG\n", encoding="utf-8")
        rec_cv = route_one(str(cvf), "cv", None, set())
        check("cv dispatched (ok)", rec_cv["provenance"]["status"] == "ok")
        check("cv sections found", "Skills" in rec_cv["provenance"].get("cv_sections", []))

        saved_tok = os.environ.pop("SOCIAL_API_TOKEN", None)
        ok_c, env_c, st_c = private_source_cred("social")
        check("social cred missing -> not ok (fail-closed)",
              ok_c is False and env_c == "SOCIAL_API_TOKEN" and st_c == "missing")
        check("unknown secret_id -> not ok", private_source_cred("nope")[0] is False)
        rec_live = route_one("live:instagram:@h", "social", None, set())
        check("social live w/o creds BLOCKED", rec_live["provenance"]["status"] == "blocked")
        os.environ["SOCIAL_API_TOKEN"] = "dummy-token-for-test"
        check("social cred present -> ok", private_source_cred("social")[0] is True)
        if saved_tok is not None:
            os.environ["SOCIAL_API_TOKEN"] = saved_tok
        else:
            os.environ.pop("SOCIAL_API_TOKEN", None)

        rec_media = route_one("clip.mp4", "media", None, set())
        check("media degrades (no N01 module yet, no crash)",
              rec_media["provenance"]["status"] in ("stub", "empty"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("=== self-test: %d passed, %d failed ===" % (passed, failed))
    return 0 if failed == 0 else 1


def _write_min_pdf(path: Path, body: str) -> None:
    """Write a minimal uncompressed single-page PDF with extractable text."""
    text = body.replace("(", r"\(").replace(")", r"\)")
    content = "BT /F1 24 Tf 72 700 Td (%s) Tj ET" % text
    cbytes = content.encode("latin-1", errors="replace")
    objs = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>",
        b"<</Length %d>>\nstream\n%s\nendstream" % (len(cbytes), cbytes),
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body_obj in enumerate(objs, 1):
        offsets.append(len(out))
        out += ("%d 0 obj" % i).encode() + body_obj + b"\nendobj\n"
    xref_pos = len(out)
    out += ("xref\n0 %d\n" % (len(objs) + 1)).encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += ("%010d 00000 n \n" % off).encode()
    out += ("trailer<</Size %d/Root 1 0 R>>\nstartxref\n%d\n%%%%EOF" % (len(objs) + 1, xref_pos)).encode()
    path.write_bytes(bytes(out))


def _write_min_xlsx(path: Path, values: list) -> None:
    """Write a minimal valid xlsx (OOXML zip) carrying inline string cells."""
    ct = ('<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
          '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
    rels = ('<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    wb = ('<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
          '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>')
    wb_rels = ('<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
               '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
    rows = "".join('<row r="%d"><c r="A%d" t="inlineStr"><is><t>%s</t></is></c></row>' % (i + 1, i + 1, v)
                   for i, v in enumerate(values))
    sheet = ('<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
             '<sheetData>%s</sheetData></worksheet>' % rows)
    with zipfile.ZipFile(str(path), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        z.writestr("xl/worksheets/sheet1.xml", sheet)


def main() -> int:
    p = argparse.ArgumentParser(description="CEX ingest router (Stage 1: inspect + dispatch + normalize)")
    p.add_argument("--source", action="append",
                   help="source arg (path / URL / '-' for stdin); repeatable. "
                        "Per-source typing via prefix: repo:PATH, doc:PATH, brand:PATH, url:URL")
    p.add_argument("--as", dest="as_type",
                   choices=["repo", "url", "doc", "brand", "paste", "social", "cv", "media"],
                   help="force the source_type (overrides classification)")
    p.add_argument("--paste", help="raw text to ingest as a paste source")
    p.add_argument("--paste-file", help="file whose raw text is ingested as a paste source")
    p.add_argument("--out", help="write the normalized manifest JSON here (default: stdout)")
    p.add_argument("--self-test", action="store_true", help="run the offline self-test and exit")
    args = p.parse_args()
    if args.self_test:
        return self_test()
    return run(args)


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_ingest_router"))
    except ImportError:
        sys.exit(main())
