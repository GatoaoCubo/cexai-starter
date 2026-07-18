#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CEX Media Adapter -- audio/video -> transcript -> normalized ingest record.

INIT_V2_ADAPTERS (N01 Intelligence). The v1 ingest router (cex_ingest_router.py)
left social / CV / media as ROUTER STUBS (founder D1). This module implements the
MEDIA branch: it turns an audio or video source into transcript text and emits the
SAME normalized record the Stage-1 router produces, so N04's distill orchestrator
(cex_distill_orchestrator.load_sources_from_manifest) consumes a media transcript
exactly like any other source:

    {source_id, source_type, uri, title, text, sha256, mime, license, provenance}
    (source_type == "media")

N05 wires a `media:` branch into cex_ingest_router this wave that calls extract().
This module is the callee; it never edits the router.

DESIGN (founder D3 offline-first / D6 privacy):
  - LOCAL-FIRST: faster-whisper (preferred) for transcription; ffmpeg (system PATH,
    else the imageio_ffmpeg bundled binary) to pull the audio track out of a video.
    faster-whisper decodes audio containers (mp3/m4a/wav) itself via PyAV.
  - DEGRADE-NEVER: every heavy dependency is LAZY-IMPORTED inside a function, so
    `import cex_media_adapter` ALWAYS succeeds with zero optional deps installed.
    No backend -> a well-formed record with text="" + a clear provenance note,
    never a crash, never a hard import-time requirement.
  - LAB-ONLY: transcripts are private to the user's CEX by default (provenance.privacy).
  - PROVIDER STT is OPTIONAL (operator may add one behind an env key later); never required.

ZERO new kinds: this is a tool. An optional typed `document_loader` instance under
N01_intelligence/ documents the config; the tool is the deliverable.

Usage:
  # transcribe one or more media files into a distill-ready manifest
  python _tools/cex_media_adapter.py --source talk.mp4 --source memo.m4a --out media.json
  python _tools/cex_media_adapter.py --source clip.wav --language en

  # strict offline (never download a model; degrade if not cached)
  python _tools/cex_media_adapter.py --source clip.wav --no-download

  # offline, deterministic self-test (degrade path + contract shape + live-if-present)
  python _tools/cex_media_adapter.py --self-test

The manifest feeds Stage 2 directly:
  python _tools/cex_distill_orchestrator.py --brain demo --manifest media.json --out OUT --execute
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path
from urllib.parse import urlsplit

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

_THIS = Path(__file__).resolve()
_TOOLS = _THIS.parent
sys.path.insert(0, str(_TOOLS))

# --- slugify (reuse cex_shared; degrade to a local impl) --------------------
try:
    from cex_shared import slugify as _slugify  # noqa: E402
except Exception:
    def _slugify(text: str) -> str:
        s = re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")
        return s or "media"

# --- constants --------------------------------------------------------------
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".oga", ".aac",
              ".wma", ".opus", ".aiff", ".aif", ".amr"}
VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".wmv",
              ".flv", ".mpeg", ".mpg", ".3gp", ".ts"}
MIME_BY_EXT = {
    ".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/mp4",
    ".flac": "audio/flac", ".ogg": "audio/ogg", ".oga": "audio/ogg",
    ".aac": "audio/aac", ".opus": "audio/opus", ".wma": "audio/x-ms-wma",
    ".aiff": "audio/aiff", ".aif": "audio/aiff", ".amr": "audio/amr",
    ".mp4": "video/mp4", ".mov": "video/quicktime", ".mkv": "video/x-matroska",
    ".avi": "video/x-msvideo", ".webm": "video/webm", ".m4v": "video/x-m4v",
    ".wmv": "video/x-ms-wmv", ".flv": "video/x-flv", ".mpeg": "video/mpeg",
    ".mpg": "video/mpeg", ".3gp": "video/3gpp", ".ts": "video/mp2t",
}
DEFAULT_MODEL = os.environ.get("CEX_WHISPER_MODEL", "tiny")
DEFAULT_PRIVACY = "lab_only"
_RE_HTTP = re.compile(r"^https?://", re.I)


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8", errors="replace")).hexdigest()


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def _have(module: str) -> bool:
    """True if a module is importable, without importing it. Never raises."""
    try:
        import importlib.util as _u
        return _u.find_spec(module) is not None
    except Exception:
        return False


# ===========================================================================
# Normalized record -- byte-identical shape to cex_ingest_router.make_record
# (kept local so the adapter degrades even if the router import breaks; the
# self-test cross-checks the key set against the router to catch any drift)
# ===========================================================================

def make_record(source_id, source_type, uri, text, *, title="", mime="text/plain",
                license="unknown", adapter="", status="ok", notes="",
                robots="n/a", license_gate="n/a", extra=None) -> dict:
    """Build one normalized source record (Stage-1 contract, N04-manifest compatible)."""
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
# Media classification
# ===========================================================================

def media_kind(path) -> str:
    """audio | video | unknown (by extension)."""
    ext = Path(str(path)).suffix.lower()
    if ext in AUDIO_EXTS:
        return "audio"
    if ext in VIDEO_EXTS:
        return "video"
    return "unknown"


def mime_for(path) -> str:
    return MIME_BY_EXT.get(Path(str(path)).suffix.lower(), "application/octet-stream")


# ===========================================================================
# Backend resolution (lazy, degrade-never)
# ===========================================================================

def resolve_ffmpeg():
    """Path to an ffmpeg binary, or None. system PATH -> imageio_ffmpeg bundle. Never raises."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _extract_audio_to_wav(src: Path, ffmpeg: str, dst: Path, timeout: int = 900) -> bool:
    """Pull a 16kHz mono PCM wav out of a media file via ffmpeg. Never raises."""
    cmd = [ffmpeg, "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000",
           "-f", "wav", str(dst)]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return r.returncode == 0 and dst.exists() and dst.stat().st_size > 0
    except Exception:
        return False


def _transcribe_faster_whisper(audio_path: Path, *, model: str, language, compute_type: str,
                               device: str, beam_size: int, vad: bool, allow_download: bool):
    """Transcribe with faster-whisper. Returns (text, info). Raises on failure (caller guards)."""
    from faster_whisper import WhisperModel
    kwargs = {"device": device, "compute_type": compute_type}
    if not allow_download:
        kwargs["local_files_only"] = True
    wm = WhisperModel(model, **kwargs)
    segments, info = wm.transcribe(str(audio_path), language=language,
                                   beam_size=beam_size, vad_filter=vad)
    parts, nseg = [], 0
    for seg in segments:
        t = (seg.text or "").strip()
        if t:
            parts.append(t)
        nseg += 1
    text = " ".join(parts).strip()
    info_d = {
        "language": getattr(info, "language", None),
        "duration_seconds": round(float(getattr(info, "duration", 0.0) or 0.0), 2),
        "segments": nseg,
    }
    prob = getattr(info, "language_probability", None)
    if prob is not None:
        info_d["language_probability"] = round(float(prob), 3)
    return text, info_d


# ===========================================================================
# Core transcription (degrade-never) -- NEVER raises
# ===========================================================================

def transcribe_media(path, *, model: str = DEFAULT_MODEL, language=None, backend: str = "auto",
                     compute_type: str = "int8", device: str = "cpu", beam_size: int = 1,
                     vad: bool = False, allow_download: bool = True):
    """Local-first transcription. Returns (text, prov_extra, status, notes). NEVER raises.

    status: ok    -> transcript text produced
            empty -> no backend / no speech (text == "")
            error -> backend present but failed (e.g. model not cached offline)
    """
    src = Path(str(path))
    kind = media_kind(src)
    extra = {
        "backend": "none", "model": model, "media_kind": kind,
        "privacy": DEFAULT_PRIVACY, "language": (language or "auto"),
        "segments": 0, "duration_seconds": 0.0,
    }

    if backend == "none":
        return "", extra, "empty", "media transcription backend disabled (backend=none)"

    if not _have("faster_whisper"):
        return ("", extra, "empty",
                "media transcription backend unavailable (install faster-whisper+ffmpeg)")

    tmpwav = None
    try:
        audio_path = src
        if kind == "video":
            ff = resolve_ffmpeg()
            if ff:
                fd, tmp = tempfile.mkstemp(suffix=".wav", prefix="cex_media_")
                os.close(fd)
                tmpwav = Path(tmp)
                if _extract_audio_to_wav(src, ff, tmpwav):
                    audio_path = tmpwav
                # else: let faster-whisper/PyAV try the container directly
        text, info = _transcribe_faster_whisper(
            audio_path, model=model, language=language, compute_type=compute_type,
            device=device, beam_size=beam_size, vad=vad, allow_download=allow_download)
        extra.update({
            "backend": "faster_whisper", "model": model,
            "language": info.get("language") or (language or "auto"),
            "segments": info.get("segments", 0),
            "duration_seconds": info.get("duration_seconds", 0.0),
        })
        if "language_probability" in info:
            extra["language_probability"] = info["language_probability"]
        if text.strip():
            return (text, extra, "ok",
                    "transcribed via faster_whisper (model=%s, %d segment(s))"
                    % (model, info.get("segments", 0)))
        return ("", extra, "empty",
                "faster_whisper ran but detected no speech (model=%s)" % model)
    except Exception as exc:
        first = str(exc).splitlines()[0] if str(exc) else ""
        return ("", extra, "error",
                "transcription backend error: %s -- %s" % (type(exc).__name__, first[:120]))
    finally:
        if tmpwav is not None:
            try:
                tmpwav.unlink()
            except Exception:
                pass


# ===========================================================================
# Source resolution (local path; guarded http(s) download to temp)
# ===========================================================================

def _resolve_source(path_or_uri):
    """Return (local_path|None, uri, cleanup_path|None, note). Never raises."""
    s = str(path_or_uri)
    if _RE_HTTP.match(s):
        try:
            import urllib.request
            suffix = Path(urlsplit(s).path).suffix or ".bin"
            fd, tmp = tempfile.mkstemp(suffix=suffix, prefix="cex_media_dl_")
            os.close(fd)
            req = urllib.request.Request(s, headers={"User-Agent": "cexai"})
            with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as fh:
                shutil.copyfileobj(resp, fh)
            return Path(tmp), s, Path(tmp), "downloaded url to temp"
        except Exception as exc:
            return None, s, None, "url download failed: %s" % type(exc).__name__
    p = Path(s)
    if not p.exists():
        return None, p.as_posix(), None, "media file not found"
    if not p.is_file():
        return None, p.as_posix(), None, "media source is not a file"
    return p, p.as_posix(), None, "local file"


# ===========================================================================
# Public entrypoint -- N05's router calls this
# ===========================================================================

def extract(path_or_uri, **opts) -> list:
    """Transcribe ONE audio/video source -> [normalized ingest record] (source_type='media').

    NEVER raises. A backend-less, unreadable, or speechless source yields a single
    well-formed record with text="" and a clear provenance note. Returns a list so
    the caller can `.extend()` it into a manifest like the other adapters.

    opts: source_id, model, language, backend ('auto'|'none'), license,
          compute_type, device, beam_size, vad, allow_download (bool).
    """
    local, uri, cleanup, rnote = _resolve_source(path_or_uri)
    name = Path(uri).name or "media"
    src_id = opts.get("source_id") or _slugify(Path(name).stem) or "media"
    kind = media_kind(name)
    mime = mime_for(name)
    lic = opts.get("license", "unknown")
    try:
        if local is None:
            rec = make_record(
                src_id, "media", uri, "", title=name, mime=mime, license=lic,
                adapter="media:none", status="empty", notes=rnote,
                extra={"backend": "none", "media_kind": kind, "privacy": DEFAULT_PRIVACY})
            return [rec]
        text, extra, status, notes = transcribe_media(
            local,
            model=opts.get("model", DEFAULT_MODEL),
            language=opts.get("language"),
            backend=opts.get("backend", "auto"),
            compute_type=opts.get("compute_type", "int8"),
            device=opts.get("device", "cpu"),
            beam_size=int(opts.get("beam_size", 1)),
            vad=bool(opts.get("vad", False)),
            allow_download=bool(opts.get("allow_download", True)))
        rec = make_record(
            src_id, "media", uri, text, title=name, mime=mime, license=lic,
            adapter="media:%s" % extra.get("backend", "none"),
            status=status, notes=notes, extra=extra)
        return [rec]
    finally:
        if cleanup is not None:
            try:
                cleanup.unlink()
            except Exception:
                pass


# ===========================================================================
# CLI orchestration -> manifest (same envelope as cex_ingest_router)
# ===========================================================================

def run(args) -> int:
    sources = args.source or []
    if not sources:
        print("[FAIL] no --source given", file=sys.stderr)
        return 2

    print("=== MEDIA ADAPTER (Stage 1: INGEST, source_type=media) ===", file=sys.stderr)
    print("F1 CONSTRAIN: %d media source(s); model=%s backend=%s privacy=%s" % (
        len(sources), args.model, args.backend, DEFAULT_PRIVACY), file=sys.stderr)
    print("F2 BECOME:    N01 Intelligence -- media transcription (faster_whisper=%s ffmpeg=%s)" % (
        "on" if _have("faster_whisper") else "absent",
        "on" if resolve_ffmpeg() else "absent"), file=sys.stderr)

    seen: set = set()
    ok_records, skipped = [], []
    for s in sources:
        recs = extract(
            s, model=args.model, language=args.language, backend=args.backend,
            allow_download=not args.no_download, vad=args.vad)
        for rec in recs:
            base = rec["source_id"]
            sid = base
            n = 1
            while sid in seen:
                n += 1
                sid = "%s_%d" % (base, n)
            seen.add(sid)
            rec["source_id"] = sid
            st = rec["provenance"]["status"]
            label = (s[:46] + "...") if len(s) > 46 else s
            print("  [%-6s] media %-50s -> %s" % (
                st, label, rec["provenance"]["notes"][:56]), file=sys.stderr)
            (ok_records if st == "ok" else skipped).append(rec)

    manifest = {
        "schema": "cex_ingest_manifest_v1",
        "contract": "p06_is_ingest_intake",
        "generated_by": "cex_media_adapter.py",
        "generated_at": _now(),
        "privacy": DEFAULT_PRIVACY,
        "count_ok": len(ok_records),
        "count_skipped": len(skipped),
        "sources": ok_records,
        "skipped": skipped,
    }
    print("F7 GOVERN:    ok=%d skipped=%d (degrade-never)" % (len(ok_records), len(skipped)),
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
# Self-test (offline, deterministic) -- import-safe + degrade + contract shape
# ===========================================================================

def _write_tone_wav(path: Path, seconds: float = 0.4, freq: float = 440.0, rate: int = 16000) -> None:
    """Write a tiny mono 16-bit PCM wav (stdlib only) for the live-backend smoke."""
    n = int(seconds * rate)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = bytearray()
        for i in range(n):
            frames += struct.pack("<h", int(3000 * math.sin(2 * math.pi * freq * i / rate)))
        w.writeframes(bytes(frames))


def self_test() -> int:
    passed = failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            passed += 1
            print("  [OK]   %s" % name)
        else:
            failed += 1
            print("  [FAIL] %s" % name)

    print("=== cex_media_adapter self-test (offline, degrade-never) ===")
    print("-- backend availability (informational) --")
    print("   faster_whisper: %s" % ("present" if _have("faster_whisper") else "absent"))
    print("   imageio_ffmpeg: %s" % ("present" if _have("imageio_ffmpeg") else "absent"))
    print("   ffmpeg binary:  %s" % (resolve_ffmpeg() or "absent"))

    print("-- classification --")
    check("mp3 -> audio", media_kind("x.mp3") == "audio")
    check("m4a -> audio", media_kind("a/b/clip.m4a") == "audio")
    check("mp4 -> video", media_kind("x.mp4") == "video")
    check("mov -> video", media_kind("x.MOV") == "video")
    check("txt -> unknown", media_kind("x.txt") == "unknown")
    check("mov mime", mime_for("x.mov") == "video/quicktime")
    check("mp3 mime", mime_for("x.mp3") == "audio/mpeg")

    required = {"source_id", "uri", "title", "text", "sha256", "mime",
                "license", "source_type", "provenance"}

    tmp = Path(tempfile.mkdtemp(prefix="media_selftest_"))
    try:
        wavp = tmp / "tone.wav"
        _write_tone_wav(wavp, seconds=0.4)

        print("-- degrade path (forced no backend) --")
        recs = extract(wavp, backend="none")
        check("returns list[dict] of len 1", isinstance(recs, list) and len(recs) == 1
              and isinstance(recs[0], dict))
        rec = recs[0]
        check("record has all 9 contract keys", required.issubset(set(rec)))
        check("source_type == media", rec["source_type"] == "media")
        check("degrade text is empty", rec["text"] == "")
        check("sha256 == sha256(text)", rec["sha256"] == _sha256(rec["text"]))
        check("degrade status == empty", rec["provenance"]["status"] == "empty")
        check("degrade note mentions backend", "backend" in rec["provenance"]["notes"].lower())
        check("provenance carries media_kind", rec["provenance"].get("media_kind") == "audio")
        check("privacy == lab_only", rec["provenance"].get("privacy") == "lab_only")

        print("-- missing / non-file sources (no crash) --")
        miss = extract(tmp / "nope.mp3")
        check("missing file -> empty", miss[0]["provenance"]["status"] == "empty"
              and miss[0]["text"] == "")
        d = extract(tmp)  # a directory, not a file
        check("directory source -> empty", d[0]["provenance"]["status"] == "empty")

        print("-- contract drift detector vs cex_ingest_router --")
        try:
            import cex_ingest_router as RT
            rkeys = set(RT.make_record("s", "doc", "u", "t").keys())
            check("top-level keys match router.make_record", set(rec.keys()) == rkeys)
        except Exception as exc:
            print("   [info] router cross-check skipped (%s)" % type(exc).__name__)

        print("-- live backend smoke (if faster_whisper present) --")
        if _have("faster_whisper"):
            allow_dl = os.environ.get("CEX_SELFTEST_DOWNLOAD", "1") != "0"
            live = extract(wavp, model=DEFAULT_MODEL, allow_download=allow_dl)
            r = live[0]
            check("live record well-formed", required.issubset(set(r))
                  and r["source_type"] == "media")
            check("live status in {ok,empty,error}",
                  r["provenance"]["status"] in {"ok", "empty", "error"})
            check("live sha256 consistent", r["sha256"] == _sha256(r["text"]))
            print("   [live] status=%s backend=%s model=%s dur=%ss segs=%s note=%s" % (
                r["provenance"]["status"], r["provenance"].get("backend"),
                r["provenance"].get("model"), r["provenance"].get("duration_seconds"),
                r["provenance"].get("segments"), r["provenance"]["notes"][:54]))
        else:
            auto = extract(wavp)
            check("auto path degrades to empty w/o backend",
                  auto[0]["provenance"]["status"] == "empty")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("=== self-test: %d passed, %d failed ===" % (passed, failed))
    return 0 if failed == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(
        description="CEX media adapter (audio/video -> transcript -> normalized ingest record)")
    p.add_argument("--source", action="append",
                   help="audio/video path or http(s) URL; repeatable")
    p.add_argument("--out", help="write the normalized manifest JSON here (default: stdout)")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help="faster-whisper model size (default: %s; env CEX_WHISPER_MODEL)" % DEFAULT_MODEL)
    p.add_argument("--language", help="force language code (e.g. en, pt); default auto-detect")
    p.add_argument("--backend", choices=["auto", "none"], default="auto",
                   help="auto = local faster_whisper; none = force the degrade path")
    p.add_argument("--no-download", action="store_true",
                   help="never download a model (strict offline; degrade if not cached)")
    p.add_argument("--vad", action="store_true",
                   help="enable voice-activity-detection filter (needs onnxruntime)")
    p.add_argument("--self-test", action="store_true",
                   help="run the offline self-test and exit")
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

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_media_adapter"))
    except ImportError:
        sys.exit(main())
