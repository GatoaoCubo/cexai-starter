#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEX Typed Judge-Output Schema + Strict Parser (R-174).

Grounds a REAL problem in a REAL schema:

  Problem (confirmed by direct Read, _tools/cex_council.py:203-223
  `parse_crew_output()`): judge output is extracted via a free-text regex
  `JUDGE:(\\w+):SCORE:([\\d.]+):RATIONALE:(.*)` with NO schema and NO
  required boolean `pass` field. A judge whose output drifts from that exact
  prefix silently DROPS from the panel -- `parse_crew_output()` just never
  appends it, so `compute_consensus()` runs on an undercounted list and
  nothing signals the loss. This is confirmed, not hypothetical: the same
  regex is reproduced verbatim below (`LEGACY_JUDGE_LINE_RE`) and exercised
  by tests/test_cex_judge_schema.py against constructed lines that DO and do
  NOT match it.

  Schema (REAL, not invented here): every one of the 6 typed `judge_config`
  artifacts CEXAI already ships at N05_operations/P07_evals/p07_jc_*.md
  (bleed, grounding, spec_fidelity, runnability, coherence, client_readiness
  -- R-163, promoted + N07-keystoned 2026-07-03) embeds the IDENTICAL
  "Verdict Schema" JSON Schema block:

      {"type":"object","additionalProperties":false,
       "required":["judge","verdict","blockers","warnings","evidence"],
       "properties":{
         "judge":{"type":"string"},
         "verdict":{"type":"string","enum":["PASS","FAIL"]},
         "blockers":{"type":"array","items":{"type":"string"}},
         "warnings":{"type":"array","items":{"type":"string"}},
         "evidence":{"type":"string"}}}

  (verified by direct Read: N05_operations/P07_evals/p07_jc_bleed.md and
  p07_jc_grounding.md, both identical). This module TYPES that schema (it is
  not a new invention) and adds the ONE field R-174 names as missing: a
  required boolean `pass`, mechanically derived from `verdict` so a caller
  never has to re-parse an enum string to know whether to trust the result.

This module composes with cex_assertions.py's `json_schema` assertion type
(dogfood) rather than re-implementing schema validation.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cex_assertions import _assert_json_schema  # noqa: E402  (intra-package reuse)


# ================================================================
# THE REAL SCHEMA (extracted verbatim from p07_jc_bleed.md / p07_jc_grounding.md)
# ================================================================

JUDGE_CONFIG_VERDICT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["judge", "verdict", "blockers", "warnings", "evidence"],
    "properties": {
        "judge": {"type": "string"},
        "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
        "blockers": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "evidence": {"type": "string"},
    },
}

# CEXAI-extension schema: the SAME real contract plus the required `pass`
# boolean R-174 asks for (mechanically derivable: verdict == "PASS"). This is
# additive -- any payload already conforming to JUDGE_CONFIG_VERDICT_SCHEMA
# can be upgraded to this one by calling `normalize_judge_config_verdict()`.
JUDGE_CONFIG_VERDICT_SCHEMA_TYPED: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["judge", "verdict", "pass", "blockers", "warnings", "evidence"],
    "properties": {
        "judge": {"type": "string"},
        "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
        "pass": {"type": "boolean"},
        "blockers": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "evidence": {"type": "string"},
    },
}


def validate_against_schema(instance: dict, schema: dict) -> dict:
    """Thin wrapper over cex_assertions.py's json_schema handler -- this
    module does not re-implement schema validation, it composes the
    registry-dispatched assertion engine (dogfood of the R-173 transplant)."""
    return _assert_json_schema({"schema": schema, "instance": instance}, {})


def normalize_judge_config_verdict(instance: dict) -> dict:
    """Take a payload conforming to the REAL p07_jc_* Verdict Schema
    (judge/verdict/blockers/warnings/evidence) and return one that also
    conforms to JUDGE_CONFIG_VERDICT_SCHEMA_TYPED (adds the required `pass`
    boolean, derived -- never guessed -- from `verdict`)."""
    out = dict(instance)
    out["pass"] = out.get("verdict") == "PASS"
    return out


# ================================================================
# LEGACY cex_council.py PARSER -- same regex, honest about what it misses.
# (Reproduced verbatim from _tools/cex_council.py:212-214, confirmed by
# direct Read -- NOT re-implemented from memory.)
# ================================================================

LEGACY_JUDGE_LINE_RE = re.compile(
    r"JUDGE:(\w+):SCORE:([\d.]+):RATIONALE:(.*)", re.IGNORECASE
)


def parse_legacy_council_output(output: str, threshold: float = 7.0) -> dict:
    """Parse the SAME free-text judge lines cex_council.py's
    `parse_crew_output()` parses -- but where that function silently drops
    any line that does not match (undercounting the panel with no signal),
    this parser returns BOTH the parsed judges (each normalized with a
    required boolean `pass = score >= threshold`, never left as a bare
    float a caller must re-interpret) AND an explicit `unparsed_lines` list,
    so a judge whose output drifted from the prefix format is a VISIBLE
    parse failure, not a silent omission.

    This does not modify cex_council.py (untouched, per working discipline)
    -- it is a standalone, stricter-honesty alternative a caller can opt
    into.
    """
    judges: List[Dict[str, Any]] = []
    unparsed_lines: List[str] = []
    if not output:
        return {"judges": judges, "unparsed_lines": unparsed_lines, "dropped_count": 0}

    for line in output.splitlines():
        if not line.strip():
            continue
        m = LEGACY_JUDGE_LINE_RE.search(line)
        if m:
            score = float(m.group(2))
            judges.append({
                "provider": m.group(1),
                "score": score,
                "pass": score >= threshold,
                "rationale": m.group(3).strip(),
            })
        elif "JUDGE" in line.upper():
            # Looks like an attempted judge line that didn't match the exact
            # prefix -- this is precisely the drift class R-174 names as
            # silently dropped by cex_council.py today. Surface it.
            unparsed_lines.append(line)

    return {
        "judges": judges,
        "unparsed_lines": unparsed_lines,
        "dropped_count": len(unparsed_lines),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="CEX typed judge-output schema validator + strict legacy parser (R-174)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_validate = sub.add_parser("validate", help="validate a JSON judge verdict against the real schema")
    p_validate.add_argument("json_path", help="path to a JSON file with a judge verdict object")
    p_validate.add_argument("--typed", action="store_true", help="require the typed (pass-field) schema")

    p_parse = sub.add_parser("parse-legacy", help="parse free-text JUDGE:... lines strictly")
    p_parse.add_argument("text_path", help="path to a text file with council output")
    p_parse.add_argument("--threshold", type=float, default=7.0)

    args = parser.parse_args(argv)

    if args.cmd == "validate":
        instance = json.loads(Path(args.json_path).read_text(encoding="utf-8"))
        schema = JUDGE_CONFIG_VERDICT_SCHEMA_TYPED if args.typed else JUDGE_CONFIG_VERDICT_SCHEMA
        result = validate_against_schema(instance, schema)
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1

    if args.cmd == "parse-legacy":
        text = Path(args.text_path).read_text(encoding="utf-8")
        result = parse_legacy_council_output(text, threshold=args.threshold)
        print(json.dumps(result, indent=2))
        return 0 if result["dropped_count"] == 0 else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
