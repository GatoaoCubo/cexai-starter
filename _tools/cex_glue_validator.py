# -*- coding: utf-8 -*-
"""CEX Glue Validator -- G2 gate for the FT glue-brain corpus.

WHY THIS EXISTS
  The generic cex_ft_dataset.py --validate rejects EVERY glue pair with
  "output too short (6 chars)". That check does len(pair["output"]) on a
  glue OUTPUT that is a structured dict/list -- len() counts its KEYS (6 for
  a carteiro decision), not characters. Router outputs are SHORT STRUCTURED
  TOKENS by design ({kind, pillar, nucleus, verb}); a min-char-length rule is
  the wrong validator for them.

WHAT THIS DOES
  Validates a glue pair BY ROLE (carteiro/rag/preflight/injetar):
    1. Alpaca shape   -- instruction/input/output present.
    2. Role tag       -- role present and in VALID_ROLES.
    3. Structured token -- the OUTPUT is a well-formed decision FOR THAT ROLE
       (e.g. carteiro output parses to a valid {kind,pillar,nucleus,verb}
       against .cex/kinds_meta.json), NOT a length rule.

  Three verdicts, reported honestly and separately:
    pass    -- well-formed CONCRETE structured token (training-useful).
    abstain -- structurally valid but content-empty (carteiro kind=None
               escalation, rag empty ranking, preflight/injetar empty
               selection). A legitimate "I don't know / escalate" label,
               but low training value -- counted apart from pass.
    fail    -- malformed (missing field, wrong type, unknown kind, pillar
               mismatch, ranking not descending, compression out of range).

CONTRACT
  - Pure validation: never mutates the corpus. ASCII-only source.
  - Importable: validate_pair(rec) -> dict ; validate_file/validate_corpus.
  - Redaction-aware: the logger redacts any key containing 'token' (so
    *_tokens fields arrive as "[REDACTED]"); numeric sanity is skipped for
    redacted values, the pair is still structurally valid.

CLI:
  python _tools/cex_glue_validator.py                      # all corpus files
  python _tools/cex_glue_validator.py FILE [FILE ...]
  python _tools/cex_glue_validator.py --role carteiro --show-fails 20
  python _tools/cex_glue_validator.py --json
  python _tools/cex_glue_validator.py --strict             # exit 1 on any fail
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
GLUE_DIR = REPO_ROOT / "_data" / "ft" / "glue"
KINDS_META_PATH = REPO_ROOT / ".cex" / "kinds_meta.json"

VALID_ROLES = ("carteiro", "rag", "preflight", "injetar")
VALID_NUCLEI = frozenset("N0%d" % i for i in range(0, 8))  # N00..N07
VALID_PILLARS = frozenset("P%02d" % i for i in range(1, 13))  # P01..P12

# Canonical verbs -- import from the resolver (single source of truth) with a
# hardcoded fallback so the validator stands alone if the import path changes.
try:  # pragma: no cover - import shim
    sys.path.insert(0, str(REPO_ROOT / "_tools"))
    from cex_intent_resolver import VERB_TABLE as _VERB_TABLE  # type: ignore
    CANONICAL_VERBS = frozenset(_VERB_TABLE.values())
except Exception:  # pragma: no cover
    CANONICAL_VERBS = frozenset({
        "create", "improve", "analyze", "validate", "document", "test",
        "deploy", "configure", "optimize", "research", "monitor",
        "schedule", "fix", "audit",
    })

REDACTED = "[REDACTED]"

_KINDS_META_CACHE: dict[str, Any] | None = None


def load_kinds_meta() -> dict[str, Any]:
    """Load + cache kinds_meta.json. Returns {} on any error (fail-open read)."""
    global _KINDS_META_CACHE
    if _KINDS_META_CACHE is not None:
        return _KINDS_META_CACHE
    try:
        _KINDS_META_CACHE = json.loads(KINDS_META_PATH.read_text(encoding="utf-8"))
    except Exception:
        _KINDS_META_CACHE = {}
    return _KINDS_META_CACHE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _coerce(obj: Any) -> Any:
    """Return dict/list as-is; parse a JSON-looking string; else passthrough."""
    if isinstance(obj, (dict, list)):
        return obj
    if isinstance(obj, str):
        s = obj.strip()
        if s and s[0] in "{[":
            try:
                return json.loads(s)
            except Exception:
                return obj
    return obj


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _conf_ok(v: Any) -> bool:
    """A confidence is OK if absent/None, or a number in [0, 1]."""
    if v is None:
        return True
    return _is_number(v) and -0.0001 <= float(v) <= 1.0001


def _verdict(role: str, status: str, category: str, reasons: list[str]) -> dict[str, Any]:
    return {"role": role, "verdict": status, "category": category, "reasons": reasons}


# ---------------------------------------------------------------------------
# Per-role output validators -> (status, category, reasons)
# ---------------------------------------------------------------------------
def _check_carteiro(out: Any, conf: Any) -> tuple[str, str, list[str]]:
    if not isinstance(out, dict):
        return "fail", "bad_shape", ["carteiro output must be an object, got %s" % type(out).__name__]
    reasons: list[str] = []
    for k in ("kind", "pillar", "nucleus", "verb"):
        if k not in out:
            reasons.append("missing key: %s" % k)
    if reasons:
        return "fail", "missing_keys", reasons

    kind = out.get("kind")
    # kind=None is a legitimate "escalate to LLM" abstention label.
    if kind is None:
        if not _conf_ok(out.get("confidence", conf)):
            return "fail", "bad_confidence", ["confidence out of [0,1]"]
        return "abstain", "escalation", ["kind=None (low-confidence escalate)"]

    meta = load_kinds_meta()
    if kind not in meta:
        return "fail", "unknown_kind", ["kind '%s' not in kinds_meta" % kind]

    pillar = out.get("pillar")
    expected_pillar = meta[kind].get("pillar")
    if pillar not in VALID_PILLARS:
        reasons.append("pillar '%s' not in P01..P12" % pillar)
    elif expected_pillar and pillar != expected_pillar:
        reasons.append("pillar_mismatch: got %s, kinds_meta says %s" % (pillar, expected_pillar))

    nucleus = out.get("nucleus")
    if nucleus not in VALID_NUCLEI:
        reasons.append("nucleus '%s' not in N00..N07" % nucleus)

    verb = out.get("verb")
    if verb not in CANONICAL_VERBS:
        reasons.append("verb '%s' not canonical" % verb)

    if not _conf_ok(out.get("confidence", conf)):
        reasons.append("confidence out of [0,1]")

    if reasons:
        return "fail", "invalid_token", reasons
    return "pass", "concrete", []


def _check_rag(out: Any, conf: Any) -> tuple[str, str, list[str]]:
    # rag ranks over the WHOLE indexed corpus -- including rule files and
    # builder ISOs whose `kind` tag is not one of the 304 canonical kinds
    # (e.g. 'rule', 'builder_default'). A retrieval pointing at such a real
    # doc is a VALID ranking decision, so a non-canonical item kind is a
    # surfaced WARNING, not a hard fail. The hard invariants are: list shape,
    # item objects, non-empty id, numeric score, DESCENDING score order.
    if not isinstance(out, list):
        return "fail", "bad_shape", ["rag output must be a list, got %s" % type(out).__name__]
    if len(out) == 0:
        return "abstain", "empty_ranking", ["no candidates retrieved"]
    hard: list[str] = []
    warn: list[str] = []
    meta = load_kinds_meta()
    last_score: float | None = None
    for i, item in enumerate(out):
        if not isinstance(item, dict):
            hard.append("item %d not an object" % i)
            continue
        if not item.get("id"):
            hard.append("item %d missing id" % i)
        k = item.get("kind")
        if k is not None and meta and k not in meta:
            warn.append("item %d kind '%s' non-canonical" % (i, k))
        score = item.get("score")
        if not _is_number(score):
            hard.append("item %d score not numeric" % i)
        else:
            if last_score is not None and float(score) > float(last_score) + 1e-9:
                hard.append("ranking not descending at item %d (%.4f > %.4f)" % (i, score, last_score))
            last_score = score
    if hard:
        return "fail", "invalid_ranking", hard + warn
    if warn:
        return "pass", "concrete_warn", warn
    return "pass", "concrete", []


def _check_preflight(out: Any, conf: Any) -> tuple[str, str, list[str]]:
    if not isinstance(out, dict):
        return "fail", "bad_shape", ["preflight output must be an object, got %s" % type(out).__name__]
    reasons: list[str] = []
    for k in ("selected_isos", "selected_kcs", "needs_cloud"):
        if k not in out:
            reasons.append("missing key: %s" % k)
    if reasons:
        return "fail", "missing_keys", reasons
    isos = out.get("selected_isos")
    kcs = out.get("selected_kcs")
    if not isinstance(isos, list) or not isinstance(kcs, list):
        return "fail", "bad_shape", ["selected_isos and selected_kcs must be lists"]
    if not isinstance(out.get("needs_cloud"), bool):
        reasons.append("needs_cloud must be a boolean")
    ct, ot = out.get("context_tokens"), out.get("original_tokens")
    if _is_number(ct) and _is_number(ot) and ot > 0 and ct > ot:
        reasons.append("context_tokens (%s) exceeds original_tokens (%s)" % (ct, ot))
    if not _conf_ok(conf):
        reasons.append("confidence out of [0,1]")
    if reasons:
        return "fail", "invalid_token", reasons
    if len(isos) == 0 and len(kcs) == 0:
        return "abstain", "empty_selection", ["no sources selected"]
    return "pass", "concrete", []


def _check_injetar(out: Any, conf: Any) -> tuple[str, str, list[str]]:
    if not isinstance(out, dict):
        return "fail", "bad_shape", ["injetar output must be an object, got %s" % type(out).__name__]
    if "injected_sources" not in out:
        return "fail", "missing_keys", ["missing key: injected_sources"]
    sources = out.get("injected_sources")
    if not isinstance(sources, list):
        return "fail", "bad_shape", ["injected_sources must be a list"]
    reasons: list[str] = []
    comp = out.get("compression")
    if comp is not None:
        if not _is_number(comp):
            reasons.append("compression not numeric")
        elif float(comp) > 1.0001:
            reasons.append("compression > 1 (impossible): %s" % comp)
        elif float(comp) < 0:
            reasons.append("compression < 0 (context grew during assembly): %s" % comp)
    if not _conf_ok(conf):
        reasons.append("confidence out of [0,1]")
    # compression<0 is a soft warning, not a hard fail (assembly can expand).
    hard = [r for r in reasons if "context grew" not in r]
    if hard:
        return "fail", "invalid_token", reasons
    if len(sources) == 0:
        return "abstain", "empty_injection", ["no sources injected"]
    return "pass", ("concrete" if not reasons else "concrete_warn"), reasons


_ROLE_CHECK = {
    "carteiro": _check_carteiro,
    "rag": _check_rag,
    "preflight": _check_preflight,
    "injetar": _check_injetar,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def validate_pair(rec: Any) -> dict[str, Any]:
    """Validate ONE glue pair record. Returns a verdict dict:
        {role, verdict: pass|abstain|fail, category, reasons:[...]}.
    Never raises -- a structural problem becomes a 'fail' verdict.
    """
    try:
        if not isinstance(rec, dict):
            return _verdict("?", "fail", "not_an_object", ["record is not a JSON object"])

        # 1. Alpaca shape
        missing = [f for f in ("instruction", "input", "output") if f not in rec]
        if missing:
            return _verdict(str(rec.get("role", "?")), "fail", "bad_alpaca_shape",
                            ["missing Alpaca field(s): %s" % ", ".join(missing)])

        # 2. Role tag
        role = rec.get("role")
        if role not in VALID_ROLES:
            return _verdict(str(role), "fail", "bad_role",
                            ["role '%s' not in %s" % (role, list(VALID_ROLES))])

        # 3. Structured token per role
        out = _coerce(rec.get("output"))
        conf = rec.get("confidence")
        status, category, reasons = _ROLE_CHECK[role](out, conf)
        return _verdict(role, status, category, reasons)
    except Exception as exc:  # never raise from a validator
        return _verdict(str(rec.get("role", "?")) if isinstance(rec, dict) else "?",
                        "fail", "validator_error", ["unexpected: %s" % exc])


def _blank_report() -> dict[str, Any]:
    rep: dict[str, Any] = {
        "files": 0, "total": 0,
        "pass": 0, "abstain": 0, "fail": 0,
        "by_role": {}, "by_category": {}, "fails": [],
    }
    return rep


def _accumulate(rep: dict[str, Any], v: dict[str, Any], where: str) -> None:
    rep["total"] += 1
    rep[v["verdict"]] += 1
    role = v["role"]
    rr = rep["by_role"].setdefault(role, {"pass": 0, "abstain": 0, "fail": 0})
    if v["verdict"] in rr:
        rr[v["verdict"]] += 1
    cat = "%s/%s" % (role, v["category"])
    rep["by_category"][cat] = rep["by_category"].get(cat, 0) + 1
    if v["verdict"] == "fail":
        rep["fails"].append({"where": where, "role": role,
                             "category": v["category"], "reasons": v["reasons"]})


def validate_file(path: str | Path, rep: dict[str, Any] | None = None,
                  role_filter: str | None = None) -> dict[str, Any]:
    """Validate every JSONL line in one file, folding into `rep`."""
    if rep is None:
        rep = _blank_report()
    path = Path(path)
    if not path.exists():
        return rep
    rep["files"] += 1
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for i, raw in enumerate(fh, 1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    rec = json.loads(raw)
                except Exception as exc:
                    _accumulate(rep, _verdict("?", "fail", "bad_json", ["line %d: %s" % (i, exc)]),
                                "%s:%d" % (path.name, i))
                    continue
                if role_filter and rec.get("role") != role_filter:
                    continue
                v = validate_pair(rec)
                _accumulate(rep, v, "%s:%d" % (path.name, i))
    except Exception:
        pass
    return rep


def validate_corpus(paths: list[str | Path] | None = None,
                    role_filter: str | None = None) -> dict[str, Any]:
    """Validate a list of files (default: the whole glue corpus)."""
    if not paths:
        paths = sorted(GLUE_DIR.glob("glue_*.jsonl")) if GLUE_DIR.exists() else []
    rep = _blank_report()
    for p in paths:
        validate_file(p, rep, role_filter)
    return rep


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _print_report(rep: dict[str, Any], show_fails: int) -> None:
    print("=== Glue Validator ===")
    print("Files: %d   Pairs: %d" % (rep["files"], rep["total"]))
    total = max(rep["total"], 1)
    print("  PASS    %5d (%.1f%%)" % (rep["pass"], 100 * rep["pass"] / total))
    print("  ABSTAIN %5d (%.1f%%)" % (rep["abstain"], 100 * rep["abstain"] / total))
    print("  FAIL    %5d (%.1f%%)" % (rep["fail"], 100 * rep["fail"] / total))
    if rep["by_role"]:
        print("\nBy role (pass/abstain/fail):")
        for role in sorted(rep["by_role"]):
            r = rep["by_role"][role]
            print("  %-10s %4d / %4d / %4d" % (role, r["pass"], r["abstain"], r["fail"]))
    if rep["by_category"]:
        print("\nBy category:")
        for cat in sorted(rep["by_category"], key=lambda c: -rep["by_category"][c]):
            print("  %-28s %5d" % (cat, rep["by_category"][cat]))
    if rep["fails"] and show_fails:
        print("\nFirst %d failures:" % min(show_fails, len(rep["fails"])))
        for f in rep["fails"][:show_fails]:
            print("  [%s] %s/%s -- %s" % (f["where"], f["role"], f["category"],
                                          "; ".join(f["reasons"][:3])))


def main() -> int:
    ap = argparse.ArgumentParser(description="CEX Glue Validator (G2 gate for FT glue corpus)")
    ap.add_argument("paths", nargs="*", help="JSONL files (default: _data/ft/glue/glue_*.jsonl)")
    ap.add_argument("--role", choices=VALID_ROLES, help="validate only this role")
    ap.add_argument("--json", action="store_true", help="emit the report as JSON")
    ap.add_argument("--show-fails", type=int, default=10, metavar="N", help="print first N failures")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any pair FAILS (abstain is OK)")
    ap.add_argument("--leak-gate", action="store_true",
                    help="DP6 (BETTER_EVAL): assert ZERO eval2<->training-corpus "
                         "intent overlap (delegates to cex_eval2_leakgate; exit 1 "
                         "on any hit). Ignores the per-pair corpus validation.")
    ap.add_argument("--eval2", action="append", metavar="GLOB",
                    help="with --leak-gate: eval2 JSONL path/glob (repeatable)")
    ap.add_argument("--corpus", action="append", metavar="GLOB",
                    help="with --leak-gate: training corpus path/glob (repeatable)")
    args = ap.parse_args()

    # DP6 leak gate -- wired into the FT validator flow. The leak check is a
    # cross-corpus assertion (eval2 vs training), distinct from the per-pair
    # structural validation below, so it is its own exit path.
    if args.leak_gate:
        import cex_eval2_leakgate as leakgate
        rep = leakgate.run_default_gate(args.eval2, args.corpus)
        if args.json:
            print(json.dumps(rep, indent=2, ensure_ascii=True))
        else:
            leakgate._print_report(rep, args.show_fails)
        return 0 if rep["clean"] else 1

    rep = validate_corpus(args.paths or None, role_filter=args.role)
    if args.json:
        print(json.dumps(rep, indent=2, ensure_ascii=True))
    else:
        _print_report(rep, args.show_fails)

    if args.strict:
        return 1 if rep["fail"] else 0
    return 0


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_glue_validator"))
    except ImportError:
        sys.exit(main())
