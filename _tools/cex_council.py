#!/usr/bin/env python3
"""cex_council.py -- Cross-provider judging council wrapper.

Thin convenience layer over cex_crew.py. Reads a target artifact,
picks a scoring rubric, invokes the cross_provider_council crew,
parses output, computes divergence, prints consensus + dissent.

Usage:
    python _tools/cex_council.py --artifact path.md [--rubric path.md] \
        [--providers claude,gemini,ollama] [--auto]

--auto mode: read artifact frontmatter. If requires_council: true OR
within-model score >= 9.5, invoke council. Else exit 0 silently.
"""

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cex_judge_schema import parse_legacy_council_output  # noqa: E402

CREW_NAME = "cross_provider_council"
DEFAULT_PROVIDERS = ["claude", "gemini", "ollama"]
SYCOPHANCY_THRESHOLD = 9.5
DIVERGENCE_THRESHOLD = 0.3


def parse_frontmatter(path):
    """Extract YAML frontmatter from a markdown file (simple parser)."""
    fm = {}
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines or lines[0].strip() != "---":
        return fm
    end = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end < 0:
        return fm
    for line in lines[1:end]:
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def should_invoke(artifact_path):
    """Check auto-invoke conditions from artifact frontmatter."""
    fm = parse_frontmatter(artifact_path)
    if fm.get("requires_council", "").lower() == "true":
        return True
    quality = fm.get("quality", "null")
    if quality != "null":
        try:
            if float(quality) >= SYCOPHANCY_THRESHOLD:
                return True
        except ValueError:
            pass
    return False


# -- L2 user_input council trigger (CONSTITUTION W5b (b)) ---------------------
# The ONLY signals that may trigger a council on a user_input turn. COST GUARD: an
# ordinary turn (the overwhelming majority) must NEVER auto-fire a council -- it is
# expensive (N x token-budget). Mirrors cex_constitution_check.COUNCIL_REQUEST_MARKERS.
USER_INPUT_COUNCIL_MARKERS = ("requires_council", "convene_council", "council_required")
_UI_SELF_CONF_KEYS = ("within_model_score", "self_confidence", "model_self_score")


def should_invoke_user_input(text):
    """COST GUARD: whether a user_input turn warrants a cross-provider council.

    Returns True ONLY on an EXPLICIT high-stakes signal -- a council request marker
    (``requires_council: true`` / an ``<!-- requires_council -->`` turn marker) or a
    declared within-model self-confidence >= the sycophancy threshold (9.5). An ordinary
    turn returns False, so the L2 hook never auto-fires a council on it (the default for
    the overwhelming majority of turns). Pure-stdlib; never raises (False on any error).

    Deliberately DISTINCT from the artifact-path ``should_invoke`` (frontmatter file) so
    the existing ``--auto`` flow stays byte-identical -- this is the turn-text path only."""
    if not text:
        return False
    try:
        low = text.lower()
        for marker in USER_INPUT_COUNCIL_MARKERS:
            esc = re.escape(marker)
            if re.search(r"(?m)^\s*%s\s*:\s*true\b" % esc, low):
                return True
            if re.search(r"<!--\s*%s\s*-->" % esc, low):
                return True
        for key in _UI_SELF_CONF_KEYS:
            m = re.search(r"(?m)^\s*%s\s*:\s*([0-9]+(?:\.[0-9]+)?)\b" % re.escape(key), low)
            if m and float(m.group(1)) >= SYCOPHANCY_THRESHOLD:
                return True
    except Exception:
        return False
    return False


def self_consistency_fallback(scores):
    """Single-provider DEGRADED mode (spec_10_commandments D5).

    When only ONE provider is available a cross-provider council is impossible, so we
    approximate it with self-consistency: draw N independent samples (their numeric
    self-ratings), take the mean as the consensus and the spread (stddev) as the
    divergence proxy, and PASS/FAIL on the same DIVERGENCE_THRESHOLD as the real council.
    Returns ``(consensus, divergence, decision)``. Offline-safe: an empty / all-non-numeric
    sample set yields ``(0.0, 0.0, "SKIP")`` (flag + move on -- never raises, never blocks).
    Reuses ``compute_consensus`` so the math matches the cross-provider path exactly."""
    vals = [float(s) for s in (scores or []) if isinstance(s, (int, float))]
    if not vals:
        return 0.0, 0.0, "SKIP"
    consensus, divergence = compute_consensus(vals)
    decision = "PASS" if divergence <= DIVERGENCE_THRESHOLD else "FAIL"
    return consensus, divergence, decision


def _read_user_input_text(args):
    """Resolve the turn text for the --user-input path: --text if given, else stdin
    (raw, or a JSON envelope with a prompt/text/turn field). Never raises -> "" on error."""
    text = getattr(args, "text", None)
    if text:
        return text
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return ""
        raw = sys.stdin.read()
    except Exception:
        return ""
    if not raw or not raw.strip():
        return ""
    if raw.lstrip()[:1] in ("{", "["):
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict):
                for key in ("prompt", "text", "turn", "user_input", "content"):
                    val = obj.get(key)
                    if isinstance(val, str) and val:
                        return val
        except Exception:
            pass
    return raw


def write_charter(artifact_path, rubric_path, providers):
    """Generate a temporary team_charter for this council invocation."""
    charter = {
        "crew": CREW_NAME,
        "artifact": os.path.abspath(artifact_path),
        "rubric": os.path.abspath(rubric_path) if rubric_path else None,
        "providers": providers,
        "divergence_threshold": DIVERGENCE_THRESHOLD,
    }
    fd, path = tempfile.mkstemp(suffix=".json", prefix="council_charter_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(charter, f, indent=2)
    return path


def compute_consensus(scores):
    """Return (mean, stddev) for a list of numeric scores."""
    n = len(scores)
    if n == 0:
        return 0.0, 0.0
    mean = sum(scores) / n
    variance = sum((s - mean) ** 2 for s in scores) / n
    return round(mean, 2), round(math.sqrt(variance), 2)


def run_council(artifact_path, rubric_path, providers):
    """Invoke the cross_provider_council crew via cex_crew.py."""
    charter_path = write_charter(artifact_path, rubric_path, providers)
    crew_script = os.path.join(os.path.dirname(__file__), "cex_crew.py")

    cmd = [
        sys.executable, crew_script, "run", CREW_NAME,
        "--charter", charter_path,
        "--execute",
    ]

    print(f"[council] invoking {CREW_NAME} with {len(providers)} providers")
    print(f"[council] artifact: {artifact_path}")
    print(f"[council] rubric: {rubric_path or '(default)'}")
    print(f"[council] providers: {', '.join(providers)}")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[council] crew exited with code {result.returncode}")
        if result.stderr:
            print(f"[council] stderr: {result.stderr[:500]}")
        return None

    return result.stdout


def parse_crew_output(output):
    """Parse crew output for per-judge scores and rationales.

    Expected format per judge line:
        JUDGE:<provider>:SCORE:<float>:RATIONALE:<text>

    CHANGELOG (R-174, 2026-07-03): deliberate fail-open -> fail-closed
    behavior change. This function used to run its own free-text regex
    directly and silently DROP any line that did not match the exact
    prefix -- a judge whose output drifted (typo, different separator, a
    provider changing its own output shape) simply vanished from the
    returned list with zero signal, undercounting compute_consensus() /
    print_verdict() with no indication a judge had gone missing.

    It now delegates to cex_judge_schema.parse_legacy_council_output(),
    which reproduces the SAME regex (LEGACY_JUDGE_LINE_RE, verified
    identical to the pattern this function used) but classifies every
    non-blank line: well-formed judge lines parse as before; a line that
    looks like an attempted judge line (contains "JUDGE") but does not
    match the exact prefix is no longer dropped -- it is appended to the
    returned list as a RECORDED, COUNTED failure entry:
        {"provider": "unparseable", "score": 0.0,
         "rationale": <raw line>, "verdict": "FAIL", "pass": False,
         "reason": "unparseable"}
    The 0.0 score is deliberately included in downstream divergence math
    (compute_consensus / print_verdict): a panel with a drifted judge
    should read as less certain, never as silently smaller.

    Public return shape preserved for existing consumers (grep-verified:
    cex_mentor_swarm.py._council_review, tests/test_council.py): every
    entry still has "provider" / "score" / "rationale" keys with the same
    types as before; "verdict" and "pass" (and, for unparseable entries,
    "reason") are additive, non-breaking keys.
    """
    if not output:
        return []
    parsed = parse_legacy_council_output(output)
    judges = []
    for j in parsed["judges"]:
        judges.append({
            "provider": j["provider"],
            "score": j["score"],
            "rationale": j["rationale"],
            "verdict": "PASS" if j["pass"] else "FAIL",
            "pass": j["pass"],
        })
    for line in parsed["unparsed_lines"]:
        judges.append({
            "provider": "unparseable",
            "score": 0.0,
            "rationale": line.strip(),
            "verdict": "FAIL",
            "pass": False,
            "reason": "unparseable",
        })
    return judges


def print_verdict(judges, threshold):
    """Print consensus verdict with dissent analysis."""
    if not judges:
        print("[council] no judge output parsed -- crew may need manual review")
        return 1

    scores = [j["score"] for j in judges]
    consensus, divergence = compute_consensus(scores)

    print("=" * 60)
    print("CROSS-PROVIDER COUNCIL VERDICT")
    print("=" * 60)
    print()

    for j in judges:
        marker = " *DISSENT*" if abs(j["score"] - consensus) > threshold else ""
        print(f"  {j['provider']:>8}: {j['score']:.1f}/10{marker}")
        print(f"           {j['rationale'][:120]}")
        print()

    decision = "PASS" if divergence <= threshold else "FAIL"
    dissent_count = sum(
        1 for j in judges if abs(j["score"] - consensus) > threshold
    )

    print(f"  consensus={consensus} divergence={divergence} "
          f"dissent_count={dissent_count} -- {decision}")
    print()

    if decision == "FAIL":
        print("[council] BLOCKED: divergence exceeds threshold "
              f"({divergence} > {threshold})")
        print("[council] review dissent rationales before publication")
        return 1

    print(f"[council] PASSED: consensus {consensus}/10")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Cross-provider judging council"
    )
    parser.add_argument("--artifact", default=None, help="Path to artifact")
    parser.add_argument("--rubric", default=None, help="Path to scoring rubric")
    parser.add_argument(
        "--providers",
        default=",".join(DEFAULT_PROVIDERS),
        help="Comma-separated provider list (default: claude,gemini,ollama)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-invoke only if frontmatter requires_council or score >= 9.5",
    )
    parser.add_argument(
        "--user-input",
        dest="user_input",
        action="store_true",
        help="L2 turn path: invoke only on an explicit high-stakes signal (cost guard); "
             "an ordinary turn exits 0 with no council.",
    )
    parser.add_argument(
        "--text", default=None,
        help="Turn text for --user-input (else read from stdin).",
    )
    args = parser.parse_args()

    # L2 user_input path (CONSTITUTION W5b): COST-GUARDED. An ordinary turn never fires a
    # council; only an explicit requires_council / >=9.5 self-confidence signal does. This
    # branch returns BEFORE the artifact path, so the --auto/--artifact flow is unchanged.
    if args.user_input:
        text = _read_user_input_text(args)
        if not should_invoke_user_input(text):
            sys.exit(0)  # ordinary turn -> no council (the default + overwhelming majority)
        print("[council] user_input: explicit high-stakes signal -- council recommended")
        print("[council] convene at F7c: python _tools/cex_council.py --artifact <path> [--auto]")
        sys.exit(0)

    if not args.artifact:
        parser.error("--artifact is required (or use --user-input for the turn path)")

    if not os.path.isfile(args.artifact):
        print(f"[council] artifact not found: {args.artifact}")
        sys.exit(1)

    if args.auto and not should_invoke(args.artifact):
        sys.exit(0)

    providers = [p.strip() for p in args.providers.split(",") if p.strip()]

    output = run_council(args.artifact, args.rubric, providers)
    judges = parse_crew_output(output)
    rc = print_verdict(judges, DIVERGENCE_THRESHOLD)
    sys.exit(rc)


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            main()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_council"))
    except ImportError:
        main()
