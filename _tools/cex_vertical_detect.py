#!/usr/bin/env python3
"""cex_vertical_detect.py -- heuristic-first vertical auto-detect (offline, no API).

INIT_ASSIMILATION_ENGINE / Wave A / Gap#4 (Stage 0 PURPOSE, N06).

Given a free-form purpose statement (and/or source signals), map it to one of the
10 vertical templates in the registry, or return 'derive_from_purpose' when no
template fits with confidence. Pure stdlib + PyYAML; no network, no API key (D3).

Registry (DATA, not taxonomy): N06_commercial/P09_config/vertical_templates.yaml

Usage:
  python _tools/cex_vertical_detect.py --purpose "we are building a neobank with KYC"
  python _tools/cex_vertical_detect.py --purpose "..." --json
  python _tools/cex_vertical_detect.py --self-test
  python _tools/cex_vertical_detect.py --list

Heuristic: each vertical has a weighted signal list. A signal that appears in the
purpose (word-boundary match) scores its word-count (multi-word phrase = stronger
evidence than a bare token). The vertical with the top weighted score wins, gated
by min_evidence + a confidence margin over the runner-up; otherwise derive.
"""

import argparse
import json
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "[FAIL] PyYAML not available. Install with: pip install pyyaml\n")
    sys.exit(2)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REGISTRY = os.path.join(
    REPO_ROOT, "N06_commercial", "P09_config", "vertical_templates.yaml")

# ---- 10-sample self-test set: purpose -> expected vertical (acceptance >= 8/10)
SELF_TEST = [
    ("I run an online store on Shopify selling handmade goods and want to "
     "improve my checkout conversion rate", "ecommerce"),
    ("We are building a neobank with KYC and AML compliance for payment "
     "processing", "fintech"),
    ("A telemedicine platform connecting patients with clinical providers "
     "using FHIR records", "healthcare"),
    ("An online course platform with an LMS and adaptive learning for "
     "students", "edtech"),
    ("A legaltech tool that automates contract review and clause extraction "
     "for attorneys", "legal"),
    ("A public sector portal for citizens to request municipal permits from "
     "their government", "govtech"),
    ("I am a fractional strategy consultant delivering advisory frameworks "
     "to clients", "consultant"),
    ("We are a software agency building custom software and MVPs for client "
     "projects", "dev_shop"),
    ("A YouTuber and content creator monetizing a newsletter and membership "
     "for my audience", "creator"),
    ("A digital marketing agency running ad campaigns for clients on a "
     "monthly retainer", "agency"),
]


def load_registry(path):
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict) or "verticals" not in data:
        raise ValueError("registry missing 'verticals' block: %s" % path)
    return data


def _signal_weight(signal):
    """Multi-word phrase = stronger signal. Weight = whitespace-token count."""
    return max(1, len(signal.split()))


def _matches(signal, text_lower):
    """Word-boundary match so 'shop' does not fire inside 'workshop'."""
    pattern = r"\b" + re.escape(signal.lower()) + r"\b"
    return re.search(pattern, text_lower) is not None


def score_purpose(purpose, registry):
    """Return (scores, matched) dicts keyed by vertical id."""
    text_lower = (purpose or "").lower()
    scores = {}
    matched = {}
    for vid, entry in registry["verticals"].items():
        total = 0
        hits = []
        for signal in entry.get("signals", []):
            if _matches(signal, text_lower):
                total += _signal_weight(signal)
                hits.append(signal)
        scores[vid] = total
        matched[vid] = hits
    return scores, matched


def detect(purpose, registry):
    """Classify a purpose statement. Returns a result dict."""
    scores, matched = score_purpose(purpose, registry)
    fb = registry.get("fallback", {})
    min_evidence = fb.get("min_evidence", 2)
    conf_threshold = fb.get("confidence_threshold", 0.50)
    derive_id = fb.get("id", "derive_from_purpose")

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_id, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    if best_score + second_score > 0:
        confidence = round(best_score / float(best_score + second_score), 2)
    else:
        confidence = 0.0

    committed = best_score >= min_evidence and confidence >= conf_threshold
    if committed:
        entry = registry["verticals"][best_id]
        chosen = best_id
        status = entry.get("status")
        kind = entry.get("kind")
        palette = entry.get("kind_palette", [])
        nuclei = entry.get("nucleus_palette", [])
        monet = entry.get("monetization_default")
    else:
        chosen = derive_id
        status = "fallback"
        kind = None
        palette = []
        nuclei = []
        monet = None

    top3 = [{"vertical": v, "score": s} for v, s in ranked[:3] if s > 0]
    return {
        "purpose": purpose,
        "vertical": chosen,
        "confidence": confidence if committed else round(confidence, 2),
        "committed": committed,
        "status": status,
        "kind": kind,
        "kind_palette": palette,
        "nucleus_palette": nuclei,
        "monetization_default": monet,
        "matched_signals": matched.get(best_id, []) if committed else [],
        "top_scores": top3,
        "rationale": (
            "matched %d signal(s); confidence %.2f over runner-up"
            % (best_score, confidence)) if committed else
            ("best score %d below min_evidence %d or confidence %.2f < %.2f "
             "-> derive from purpose"
             % (best_score, min_evidence, confidence, conf_threshold)),
    }


def run_self_test(registry):
    hits = 0
    rows = []
    for purpose, expected in SELF_TEST:
        res = detect(purpose, registry)
        got = res["vertical"]
        ok = (got == expected)
        hits += 1 if ok else 0
        rows.append((ok, expected, got, res["confidence"], purpose))

    print("=== cex_vertical_detect --self-test ===")
    print("%-4s %-12s %-18s %-5s %s" % ("OK", "EXPECTED", "GOT", "CONF", "PURPOSE"))
    for ok, expected, got, conf, purpose in rows:
        tag = "[OK]" if ok else "[XX]"
        snippet = purpose[:46] + ("..." if len(purpose) > 46 else "")
        print("%-4s %-12s %-18s %-5s %s" % (tag, expected, got, conf, snippet))
    total = len(SELF_TEST)
    print("-" * 60)
    print("Hit rate: %d/%d (acceptance: >= 8/%d)" % (hits, total, total))
    return hits, total


def main(argv=None):
    ap = argparse.ArgumentParser(description="Heuristic vertical auto-detect (offline).")
    ap.add_argument("purpose", nargs="?", help="purpose statement (free text)")
    ap.add_argument("--purpose", dest="purpose_opt", help="purpose statement (flag form)")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY, help="path to vertical_templates.yaml")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--self-test", action="store_true", help="run the 10-sample acceptance test")
    ap.add_argument("--list", action="store_true", help="list registered verticals")
    args = ap.parse_args(argv)

    try:
        registry = load_registry(args.registry)
    except (OSError, ValueError) as exc:
        sys.stderr.write("[FAIL] cannot load registry: %s\n" % exc)
        return 2

    if args.self_test:
        hits, total = run_self_test(registry)
        return 0 if hits >= 8 else 1

    if args.list:
        for vid, entry in registry["verticals"].items():
            print("%-12s %-16s %s" % (
                vid, entry.get("status", "?"), entry.get("title", "")))
        return 0

    purpose = args.purpose_opt or args.purpose
    if not purpose:
        ap.error("provide a purpose (positional or --purpose), or use --self-test")

    result = detect(purpose, registry)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    else:
        print("vertical   : %s" % result["vertical"])
        print("confidence : %.2f" % result["confidence"])
        print("status     : %s" % result["status"])
        if result["committed"]:
            print("kind       : %s" % result["kind"])
            print("kinds      : %s" % ", ".join(result["kind_palette"]))
            print("nuclei     : %s" % ", ".join(result["nucleus_palette"]))
            print("monetize   : %s" % result["monetization_default"])
            print("signals    : %s" % ", ".join(result["matched_signals"]))
        print("rationale  : %s" % result["rationale"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
