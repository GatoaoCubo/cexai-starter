# -*- coding: utf-8 -*-
"""CEX Glue Logger -- B1 keystone of the FT glue-brain.

Logs every orchestrator GLUE decision (carteiro/rag/preflight/injetar) as a
training pair so CEXAI self-assimilates its own routing/retrieval/preflight/
inject behaviour into an FT corpus at ZERO marginal cost.

CONTRACT (non-negotiable):
  - FAIL-OPEN: log_glue() NEVER raises. Any error -> silent no-op. Logging
    must never break a live orchestration. Proven by test_glue_logger.py.
  - KILL-SWITCH: env CEX_GLUE_DISABLE=1 OR glue_trace.yaml enabled:false ->
    zero lines written, no side effects.
  - ASCII-only source (per .claude/rules/ascii-code-rule.md).

Sink:    _data/ft/glue/glue_<role>_<YYYYMMDD>.jsonl   (one JSON object per line)
Schema:  ts, role, instruction, input, output, source, confidence, meta
         (Alpaca-projectable: instruction/input/output map straight to Alpaca)

CLI:
  python _tools/cex_glue_logger.py --stats
  python _tools/cex_glue_logger.py --tail 10 [--role carteiro]
  python _tools/cex_glue_logger.py --selftest
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
GLUE_DIR = REPO_ROOT / "_data" / "ft" / "glue"
CONFIG_PATH = REPO_ROOT / ".cex" / "config" / "glue_trace.yaml"

VALID_ROLES = ("carteiro", "rag", "preflight", "injetar")

# Deterministic task description per role (the Alpaca "instruction").
ROLE_INSTRUCTION = {
    "carteiro": "Resolve the user intent to {kind, pillar, nucleus, verb}.",
    "rag": "Retrieve and rank the artifacts most relevant to the query.",
    "preflight": "Select the context sources and token budget this build needs.",
    "injetar": "Assemble the final builder context (F3 INJECT) from candidates.",
}

# Default-SAFE gate. Used when glue_trace.yaml is absent or unreadable.
_DEFAULT_CONFIG = {
    "enabled": True,
    "roles": {r: True for r in VALID_ROLES},
    "sampling": 1.0,
    "redact_keys": ["api_key", "token", "secret", "password", "email", "authorization"],
    "max_record_bytes": 65536,
    "fail_open": True,
}

_CONFIG_CACHE: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Config (fail-open: any error -> safe defaults)
# ---------------------------------------------------------------------------
def _load_config() -> dict[str, Any]:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    cfg = dict(_DEFAULT_CONFIG)
    try:
        if CONFIG_PATH.exists():
            try:
                import yaml  # optional dependency
                loaded = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
                if isinstance(loaded, dict):
                    cfg.update({k: v for k, v in loaded.items() if v is not None})
            except Exception:
                # pyyaml missing or parse error -> keep safe defaults
                pass
    except Exception:
        pass
    _CONFIG_CACHE = cfg
    return cfg


def _is_enabled(role: str, cfg: dict[str, Any]) -> bool:
    if os.environ.get("CEX_GLUE_DISABLE") == "1":
        return False
    if not cfg.get("enabled", True):
        return False
    roles = cfg.get("roles") or {}
    return bool(roles.get(role, True))


def _redact(obj: Any, redact_keys: list[str], depth: int = 0) -> Any:
    """Recursively replace values whose key matches a redact term. Fail-open."""
    if depth > 6:
        return obj
    try:
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                kl = str(k).lower()
                if any(term in kl for term in redact_keys):
                    out[k] = "[REDACTED]"
                else:
                    out[k] = _redact(v, redact_keys, depth + 1)
            return out
        if isinstance(obj, (list, tuple)):
            return [_redact(x, redact_keys, depth + 1) for x in obj]
        return obj
    except Exception:
        return obj


def _safe_serialize(obj: Any) -> Any:
    """Make obj JSON-serializable without raising (fallback to str)."""
    try:
        json.dumps(obj)
        return obj
    except Exception:
        try:
            return str(obj)
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def log_glue(
    role: str,
    inputs: Any,
    output: Any,
    meta: dict[str, Any] | None = None,
    source: str = "heuristic",
    confidence: float | None = None,
) -> None:
    """Append ONE glue training pair to the role's daily JSONL. FAIL-OPEN.

    Args:
        role: one of carteiro|rag|preflight|injetar.
        inputs: the decision input (the prompt side of the pair).
        output: the chosen decision (the label side of the pair).
        meta: optional {session, wall_ms, tokens, ...}.
        source: who produced the label -- heuristic|opus|sonnet|hybrid
                (the distillation key: teacher labels vs cheap baseline).
        confidence: optional resolver confidence or top rank score.
    """
    try:
        if role not in VALID_ROLES:
            return
        cfg = _load_config()
        if not _is_enabled(role, cfg):
            return

        sampling = cfg.get("sampling", 1.0)
        if sampling < 1.0:
            try:
                import random
                if random.random() > sampling:
                    return
            except Exception:
                pass

        redact_keys = cfg.get("redact_keys") or []
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "instruction": ROLE_INSTRUCTION.get(role, role),
            "input": _redact(_safe_serialize(inputs), redact_keys),
            "output": _redact(_safe_serialize(output), redact_keys),
            "source": source,
            "confidence": confidence,
            "meta": _redact(_safe_serialize(meta or {}), redact_keys),
        }
        line = json.dumps(record, ensure_ascii=True)

        max_bytes = cfg.get("max_record_bytes", 65536)
        if len(line) > max_bytes:
            # Truncate the heavy fields rather than drop the pair entirely.
            record["input"] = str(record["input"])[: max_bytes // 4]
            record["output"] = str(record["output"])[: max_bytes // 4]
            line = json.dumps(record, ensure_ascii=True)

        GLUE_DIR.mkdir(parents=True, exist_ok=True)
        day = datetime.now(timezone.utc).strftime("%Y%m%d")
        path = GLUE_DIR / ("glue_%s_%s.jsonl" % (role, day))
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        # FAIL-OPEN: never propagate a logging error to the orchestrator.
        return


def reset_config_cache() -> None:
    """Test hook: force re-read of the gate on next log_glue()."""
    global _CONFIG_CACHE
    _CONFIG_CACHE = None


def glue_stats() -> dict[str, Any]:
    """Count logged pairs per role + per source. Fail-open -> {} on error."""
    stats: dict[str, Any] = {"roles": {}, "total": 0, "by_source": {}}
    try:
        if not GLUE_DIR.exists():
            return stats
        for path in sorted(GLUE_DIR.glob("glue_*.jsonl")):
            role = path.name.split("_")[1] if "_" in path.name else "?"
            n = 0
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    for raw in fh:
                        raw = raw.strip()
                        if not raw:
                            continue
                        n += 1
                        try:
                            rec = json.loads(raw)
                            src = rec.get("source", "?")
                            stats["by_source"][src] = stats["by_source"].get(src, 0) + 1
                        except Exception:
                            pass
            except Exception:
                continue
            stats["roles"][role] = stats["roles"].get(role, 0) + n
            stats["total"] += n
    except Exception:
        pass
    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _cli_tail(n: int, role: str | None) -> None:
    if not GLUE_DIR.exists():
        print("(no glue corpus yet: %s)" % GLUE_DIR)
        return
    pattern = "glue_%s_*.jsonl" % role if role else "glue_*.jsonl"
    lines: list[str] = []
    for path in sorted(GLUE_DIR.glob(pattern)):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines.extend(fh.readlines())
        except Exception:
            continue
    for raw in lines[-n:]:
        print(raw.rstrip())


def _cli_selftest() -> int:
    """Smoke: write one pair per role to a temp sink, verify, clean up."""
    import tempfile
    global GLUE_DIR
    original = GLUE_DIR
    ok = True
    try:
        GLUE_DIR = Path(tempfile.mkdtemp(prefix="glue_selftest_"))
        reset_config_cache()
        for role in VALID_ROLES:
            log_glue(role, {"probe": role}, {"label": role}, source="heuristic")
        files = list(GLUE_DIR.glob("glue_*.jsonl"))
        ok = len(files) == len(VALID_ROLES)
        # Verify fail-open: a non-serializable monster must not raise.
        log_glue("carteiro", object(), {1, 2, 3}, meta={"x": object()})
        print("[selftest] wrote %d/%d role files -> %s" %
              (len(files), len(VALID_ROLES), "OK" if ok else "FAIL"))
        for f in files:
            try:
                f.unlink()
            except Exception:
                pass
        try:
            GLUE_DIR.rmdir()
        except Exception:
            pass
    finally:
        GLUE_DIR = original
        reset_config_cache()
    return 0 if ok else 1


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="CEX Glue Logger (FT glue-brain B1)")
    ap.add_argument("--stats", action="store_true", help="count logged pairs per role")
    ap.add_argument("--tail", type=int, metavar="N", help="print last N records")
    ap.add_argument("--role", choices=VALID_ROLES, help="filter --tail by role")
    ap.add_argument("--selftest", action="store_true", help="fail-open smoke test")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(_cli_selftest())
    if args.stats:
        st = glue_stats()
        print(json.dumps(st, indent=2, ensure_ascii=True))
        return
    if args.tail is not None:
        _cli_tail(args.tail, args.role)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
